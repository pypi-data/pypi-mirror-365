from openai import OpenAI
from dotenv import load_dotenv
import pickle

import  os, re
import requests #画像downloadで使用
import threading
import time
import queue
import base64
import json
from pydantic import BaseModel, Field
from typing import List

import anthropic
from jsonschema import validate, ValidationError
import google.generativeai as gemini
from google.generativeai import GenerationConfig

#whisper用
from io import BytesIO
import wave
import pyaudio
import mimetypes


# model_gemini_default = "gemini-2.5-flash-preview-04-17"
model_gemini_default = "gemini-2.5-pro-preview-06-05"

class myopenai :


    client = None 
    default_model = None

    def __init__(self, model:str=None, model_gemini:str=model_gemini_default) :
        self.client = OpenAI()
        self.use_gemini(model_gemini)
        self.model_name_gemini = model_gemini
        self.client_claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.queue_response_text = queue.Queue()
        self.f_running = True
        self.messages = []
        self.messages_claude = []
        self.messages_gemini = []
        self.l_cost = []
        if model :
            self.default_model = model
        else :
            self.default_model = "gpt-4.1-mini"

        # api_key=os.getenv("GEMINI_API_KEY")
        # print(f"gemini api key: {api_key}")
        gemini.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # pricedata.jsonを読み込む
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'pricedata.json'), 'r') as f:
            self.d_pricedata = json.load(f)

    def use_claude(self, api_key:str=None) :
        if not api_key :
            api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client_claude = anthropic.Anthropic(api_key=api_key)
    def use_gemini(self, model_gemini, api_key:str=None) :
        if not api_key :
            api_key = os.getenv("GEMINI_API_KEY")
        gemini.configure(api_key=os.environ['GEMINI_API_KEY'])
        self.client_gemini = gemini.GenerativeModel(model_name=model_gemini)
        
    def is_running(self) :
        return self.f_running
    def is_running_or_queue(self) :
        time.sleep(0.05) #直後に動かされた時にfalseになるのを防ぐ
        return self.f_running or not self.is_queue_empty()
    
    def is_queue_empty(self) :
        return self.queue_response_text.empty()

    def get_messages(self, f_replace_imagedata:bool=False) :
        messages = self.messages
        if f_replace_imagedata :
            #イメージデータがバカほど文字列食うので、置換
            def replace_image_url(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == "image_url":
                            data[key] = "（画像データ）"
                        else:
                            # 辞書の値も再帰的に処理する
                            replace_image_url(value)
                elif isinstance(data, list):
                    for item in data:
                        replace_image_url(item)

            replace_image_url(messages) 
        return messages
    
    def get_messages_claude(self) :
        return self.messages_claude
    def get_messages_gemini(self) :
        return self.messages_gemini

    def delete_last_message(self) :
        if len(self.messages) == 0 :
            return None
        last_message = self.messages[-1]
        self.messages        = self.messages[:-1]
        self.messages_claude = self.messages_claude[:-1]
        self.messages_gemini = self.messages_gemini[:-1]
        return last_message

    def delete_all_messages(self) :
        self.messages = []
        self.messages_claude = []
        self.messages_gemini = []

    def get_text_from_message(self, msg:dict=None) :
        if not msg :
            msg = self.messages[-1]
        for c in msg["content"] :
            if c["type"] == "text" :
                return c["text"]
    def get_audio_from_message(self, msg:dict=None) :
        if not msg :
            msg = self.messages[-1]
        for c in msg["content"] :
            if c["type"] == "input_audio" :
                data_wav = base64.b64decode(c["input_audio"]["data"])
                return data_wav
    
    def add_message(self, msg:str, role:str="user", type:str="text") :
        if type == "text" :
            data = {"role": role, "content": [{"type": "text", "text": msg }]}
        elif type == "audio" :
            data = {"role": role, "audio":{"id": msg}}

        self.messages.append(data)
        self.messages_claude.append(data)

        # Google Geminiの場合、systemは別で指定することになっている
        if role == "system" :
            self.client_gemini = gemini.GenerativeModel(
                model_name          = self.model_name_gemini,
                system_instruction  = msg
            )
        elif role == "assistant" :
            data = {"role": "model", "parts": [{"text": msg}]}
            self.messages_gemini.append(data)
        else :
            parts = [{"text": msg}]
            self.messages_gemini.append({"role": role, "parts": parts})





    def add_message_with_image(self, prompt:str, file_path:str, role:str="user") :
        img_bytes = open(file_path, "rb").read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        content = [{"type": "text", "text": prompt}]
        content.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
            # "myopenai_image_path": file_path #これ付けたらエラーになる
        })
        self.messages.append({"role": role, "content": content})

        # Anthropicでは、image_urlではなく、imageで指定する
        content = [{"type": "text", "text": prompt}]
        content.append({
            "type": "image", 
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}
        })
        self.messages_claude.append({"role": role, "content": content})

        # Google Geminiの場合
        parts = [{"text": prompt}]
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}})

        self.messages_gemini.append({"role": role, "parts": parts})


    def add_audiodata(self, audiodata, format, text:str=None, role:str="user") :
        #claudeは未実装

        #--- OpenAIの場合
        data_b64 = base64.b64encode(audiodata).decode('utf-8')
        content = [{
                "type": "input_audio",
                "input_audio": {
                    "data": data_b64,
                    "format": format
                }
        }]
        if text :
            content.append({"type": "text", "text": text})

        j = {"role": role, "content": content}
        self.messages.append(j)

        #--- Geminiの場合
        mime_type, _ = mimetypes.guess_type(f"aaa.{format}")
        audio_part = {'inline_data': {'mime_type': mime_type, 'data': audiodata}}
        cont_gemini = {'role': 'user', 'parts': [audio_part]} 
        self.messages_gemini.append(cont_gemini)

    def add_audio_fromfile(self, file_path, role:str="user") :
        audio_data = open(file_path, "rb").read()
        ext = os.path.splitext(file_path)[1].replace(".","")
        self.add_audiodata(audio_data, ext, role)

    def add_message_with_audio(self, prompt:str, file_path:str) : #roleはuser固定
        # geminiのための関数（openai/claudeは未実装）
        myfile = gemini.upload_file(path=file_path)
        audio_part = {
            "file_data": {
                "mime_type": myfile.mime_type,
                "file_uri": myfile.uri
            }
        }
        # プロンプト＋音声ファイルを履歴に追加
        self.messages_gemini.append({
            "role": "user",
            "parts": [
                {"text": prompt},
                audio_part
            ]
        })

    def get_queue(self) -> str :
        token = ""
        while not self.queue_response_text.empty() :
            token += self.queue_response_text.get(timeout=0.1)
        return token
    

    def run(self, model:str=None) -> str :
        self.f_running = True
        if not model :
            model = self.default_model

        completion = self.client.chat.completions.create(
            model       = model,
            messages    = self.messages,
        )
        self.l_cost.append({
            "model"               : completion.model,
            "tokens_input"        : completion.usage.prompt_tokens,
            "tokens_input_cached" : completion.usage.prompt_tokens_details.cached_tokens,
            "tokens_input_audio"  : completion.usage.prompt_tokens_details.audio_tokens,
            "tokens_output"       : completion.usage.completion_tokens,
            "tokens_output_audio" : completion.usage.completion_tokens_details.audio_tokens
        })

        response = completion.choices[0].message.content
        self.add_message(response, "assistant")
        self.f_running = False
        return response


    def run_claude(self, model:str="claude-3-5-sonnet-20241022") :
        self.f_running = True

        #Claude/geminiは「system」がエラーになるので、その対処
        for msg in self.messages_claude :
            if msg["role"] == "system" :
                msg["role"] = "user"

        # Claudeへのリクエストを作成
        try:
            response = self.client_claude.messages.create(
                model=model,
                messages=self.messages_claude,
                max_tokens=1024,
            )
        except Exception as e:
            print(e) #リトライすることがあるが、勝手にリトライするので、スルー（これがないとClientにエラー信号が行く）

        # レスポンスの処理
        res = response.content[0].text
        self.add_message(json.dumps(res, ensure_ascii=False, indent=4), "assistant")
        self.f_running = False

        self.l_cost.append({
            "model"               : response.model,
            "tokens_input"        : response.usage.input_tokens,
            "tokens_input_cached" : 0,
            "tokens_input_audio"  : 0,
            "tokens_output"       : response.usage.output_tokens,
            "tokens_output_audio" : 0
        })
        self.f_running = False
        return res
    

    def run_gemini(self) :
        # モデルを上書きできなくなった(なのでイニシャライズで指定してる)
        self.f_running = True

        response = self.client_gemini.generate_content(
            contents=self.messages_gemini,
        )

        total_tokens            = response.usage_metadata.total_token_count
        token_input_text        = response.usage_metadata.prompt_token_count
        token_input_text_cached = response.usage_metadata.cached_content_token_count
        token_output_text       = response.usage_metadata.candidates_token_count
        token_input_txt_incpic  = total_tokens - token_input_text_cached - token_output_text
        if token_input_text < token_input_txt_incpic :
            token_input_text = token_input_txt_incpic
        token_input_audio       = 0
        self.add_message(response.text, "assistant")
        self.f_running = False

        # #コスト計算：audioが含まれていたら、ざっくり6倍にする（本当は按分だが、今のレスポンスではtext/audioの区分がないので）
        # token_text = response.usage_metadata.prompt_token_count
        # token_audio = 0
        # for x in self.messages_gemini :
        #     for y in x['parts'] :
        #         if "inline_data" in y.keys() and 'audio' in y['inline_data']['mime_type'] :
        #             token_audio = token_text
        #             token_text = 0
        #             break
        #     if token_audio > 0 :
        #         break
        
        self.l_cost.append({
            "model"               : response.model_version,
            "tokens_input"        : token_input_text,
            "tokens_input_cached" : token_input_text_cached ,
            "tokens_input_audio"  : token_input_audio,
            "tokens_output"       : token_output_text,
            "tokens_output_audio" : 0
        })
        self.f_running = False

        return response.text


    def run_so(self, ResponseStep, model:str=None) :
        self.f_running = True
        if not model :
            model = self.default_model
    
        try :
            response = self.client.beta.chat.completions.parse(
                model           = model,
                # temperature     = 0,
                messages        = self.messages,
                response_format = ResponseStep,
            )
        except Exception as e:
            print(e)
            pass #リトライすることがあるが、勝手にリトライするので、スルー（これがないとClientにエラー信号が行く）

        self.add_message(response.choices[0].message.content, "assistant")
        self.f_running = False

        self.l_cost.append({
            "model"               : response.model,
            "tokens_input"        : response.usage.prompt_tokens,
            "tokens_input_cached" : response.usage.prompt_tokens_details.cached_tokens,
            "tokens_input_audio"  : response.usage.prompt_tokens_details.audio_tokens,
            "tokens_output"       : response.usage.completion_tokens,
            "tokens_output_audio" : response.usage.completion_tokens_details.audio_tokens
        })
        self.f_running = False
        return response.choices[0].message.parsed

    def run_so_claude(self, ResponseStep, model:str="claude-3-5-sonnet-20241022") :
        self.f_running = True

        def resolve_refs(schema, defs=None):
            # JSON Schema内の$refを手動で解決し、純粋な辞書を返します。
            if defs is None:
                defs = schema.get('$defs', {})
            
            if isinstance(schema, dict):
                if '$ref' in schema:
                    ref = schema['$ref']
                    if ref.startswith('#/$defs/'):
                        def_name = ref.replace('#/$defs/', '')
                        if def_name in defs:
                            return resolve_refs(defs[def_name], defs)
                        else:
                            raise ValueError(f"Reference {ref} not found in $defs.")
                    else:
                        raise ValueError(f"Unsupported reference format: {ref}")
                else:
                    return {k: resolve_refs(v, defs) for k, v in schema.items()}
            elif isinstance(schema, list):
                return [resolve_refs(item, defs) for item in schema]
            else:
                return schema

        json_schema_full = ResponseStep.model_json_schema()
        json_schema_dereferenced = resolve_refs(json_schema_full)
        json_schema = {
            "type": json_schema_dereferenced.get("type"),
            "properties": json_schema_dereferenced.get("properties"),
            "required": json_schema_dereferenced.get("required"),
        }

        # ツールの定義
        json_output_tool = {
            "name": "json-output",
            "input_schema": json_schema,
            "description": "出力をJSON形式のオブジェクトで返します。"
        }

        # Claudeへのリクエストを作成
        try:
            response = self.client_claude.messages.create(
                model=model,
                max_tokens=1024,
                messages=self.messages_claude,
                temperature=0,  # 一貫した応答を得るために0に設定
                tools=[json_output_tool],  # ツールを指定
                tool_choice={
                    "type": "tool",
                    "name": "json-output",
                },
            )
        except Exception as e:
            pass #リトライすることがあるが、勝手にリトライするので、スルー（これがないとClientにエラー信号が行く）


        # レスポンスの処理
        content_blocks = response.content
        for block in content_blocks:
            if hasattr(block, 'type') and block.type == "tool_use":
                # JSON Schemaに従ってバリデーション
                json_data = block.input
                validate(instance=json_data, schema=json_schema)
                # print(f"構造化データ:\n{json.dumps(json_data, ensure_ascii=False, indent=2)}")
            else:
                print(block.text)

        self.add_message(json.dumps(json_data, ensure_ascii=False, indent=4), "assistant")
        self.f_running = False

        self.l_cost.append({
            "model"               : response.model,
            "tokens_input"        : response.usage.input_tokens,
            "tokens_input_cached" : 0,
            "tokens_input_audio"  : 0,
            "tokens_output"       : response.usage.output_tokens,
            "tokens_output_audio" : 0
        })
        self.f_running = False
        return json_data


    def run_so_gemini(self, ResponseStep) :
        self.f_running = True

        response = self.client_gemini.generate_content(
            contents=self.messages_gemini,
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=ResponseStep,
            )
        )

        # model = gemini.GenerativeModel(model_name=model)
        # try :
        #     response = model.generate_content(
        #         self.messages_gemini,
        #         generation_config=gemini.GenerationConfig(
        #             response_mime_type="application/json", response_schema=ResponseStep
        #         ),
        #     )
        # except Exception as e:
        #     pass #リトライすることがあるが、勝手にリトライするので、スルー（これがないとClientにエラー信号が行く）


        total_tokens            = response.usage_metadata.total_token_count
        token_input_text        = response.usage_metadata.prompt_token_count
        token_input_text_cached = response.usage_metadata.cached_content_token_count
        token_output_text       = response.usage_metadata.candidates_token_count
        token_input_txt_incpic  = total_tokens - token_input_text_cached - token_output_text
        if token_input_text < token_input_txt_incpic :
            token_input_text = token_input_txt_incpic
        token_input_audio       = 0
        self.add_message(response.text, "assistant")
        self.f_running = False

        # token_text = response.usage_metadata.prompt_token_count
        # token_audio = 0
        # for x in self.messages_gemini :
        #     for y in x['parts'] :
        #         if "inline_data" in y.keys() and 'audio' in y['inline_data']['mime_type'] :
        #             token_audio = token_text
        #             token_text = 0
        #             break
        #     if token_audio > 0 :
        #         break
        
        self.l_cost.append({
            "model"               : response.model_version,
            "tokens_input"        : token_input_text,
            "tokens_input_cached" : token_input_text_cached ,
            "tokens_input_audio"  : token_input_audio,
            "tokens_output"       : token_output_text,
            "tokens_output_audio" : 0
        })
        self.f_running = False


        # try:
        #     res = json.loads(response.text)
        # except json.JSONDecodeError as e:
        #     print(f"JSONデコードエラー: {e}")
        #     open("json_conversion_error.txt", "w", encoding="utf-8").write(response.text)
        #     print(response.text)
        #     res = None  # エラー時のデフォルト値を設定
        # if response.parsed :
        #     res = response.parsed
        #     res = res.model_dump()
        # else :
        #     pattern = r'```json\s*([\s\S]+)\s*```'
        #     match = re.search(pattern, response.text, re.DOTALL)
        #     if match :
        #         txt_json = match.group(1).strip()
        #         res = json.loads(txt_json)
        #     else :
        #         res = None
        try :
            res = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSONデコードエラー: {e}")
            open("json_conversion_error.txt", "w", encoding="utf-8").write(response.text)
            print(response.text)
            res = None
        return res

    def run_search(self, model:str="gpt-4o-search-preview") :
        completion = self.client.chat.completions.create(
            model=model,
            web_search_options={
                "search_context_size": "low",
            },
            messages=self.messages,
        )
        response = completion.choices[0].message.content
        self.add_message(response, "assistant")
        self.f_running = False
        self.l_cost.append({
            "model"               : response.model,
            "tokens_input"        : response.usage.prompt_tokens,
            "tokens_input_cached" : response.usage.prompt_tokens_details.cached_tokens,
            "tokens_input_audio"  : response.usage.prompt_tokens_details.audio_tokens,
            "tokens_output"       : response.usage.completion_tokens,
            "tokens_output_audio" : response.usage.completion_tokens_details.audio_tokens
        })
        return response

    def run_so_search(self, ResponseStep, model:str="gpt-4o-search-preview") :
        self.f_running = True
        response = self.client.beta.chat.completions.parse(
            model           = model,
            # temperature     = 0,
            messages        = self.messages,
            response_format = ResponseStep,
        )
        self.add_message(response.choices[0].message.content, "assistant")
        self.f_running = False

        self.l_cost.append({
            "model"               : response.model,
            "tokens_input"        : response.usage.prompt_tokens,
            "tokens_input_cached" : response.usage.prompt_tokens_details.cached_tokens,
            "tokens_input_audio"  : response.usage.prompt_tokens_details.audio_tokens,
            "tokens_output"       : response.usage.completion_tokens,
            "tokens_output_audio" : response.usage.completion_tokens_details.audio_tokens
        })
        self.f_running = False
        return response.choices[0].message.parsed

    def run_to_audio(self, model:str=None) :
        self.f_running = True
        if not model :
            model = self.default_model

        completion = self.client.chat.completions.create(
            model       = model,
            modalities  = ["text", "audio"],
            audio       = {"voice": "alloy", "format": "wav"},
            messages    = self.messages
        )
        audio_id = completion.choices[0].message.audio.id
        data_txt = completion.choices[0].message.audio.transcript
        self.add_message(data_txt, role="assistant") #assistantに音声を登録すると、そのあとrunでエラーになる
        # self.add_message(audio_id, "assistant", "audio") #こうやって登録することも可能
        data_b64 = completion.choices[0].message.audio.data
        data_wav = base64.b64decode(data_b64)


        self.l_cost.append({
            "model"               : completion.model,
            "tokens_input"        : completion.usage.prompt_tokens,
            "tokens_input_cached" : completion.usage.prompt_tokens_details.cached_tokens,
            "tokens_input_audio"  : completion.usage.prompt_tokens_details.audio_tokens,
            "tokens_output"       : completion.usage.completion_tokens,
            "tokens_output_audio" : completion.usage.completion_tokens_details.audio_tokens
        })

        self.f_running = False

        return data_wav

    def run_stream(self, model:str=None) -> str :
        self.f_running = True
        if not model :
            model = self.default_model

        stream = self.client.chat.completions.create(
            model          = model,
            messages       = self.messages,
            stream         = True,
            stream_options = {"include_usage": True},
        )
        response = ""
        d_cost = {}
        for chunk in stream:
            if chunk.choices:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    response += token
                    self.queue_response_text.put(token)
                    # print(chunk.choices[0].delta.content, end="")
            if chunk.usage:
                self.l_cost.append({
                    "model"               : chunk.model,
                    "tokens_input"        : chunk.usage.prompt_tokens,
                    "tokens_input_cached" : chunk.usage.prompt_tokens_details.cached_tokens,
                    "tokens_input_audio"  : chunk.usage.prompt_tokens_details.audio_tokens,
                    "tokens_output"       : chunk.usage.completion_tokens,
                    "tokens_output_audio" : chunk.usage.completion_tokens_details.audio_tokens
                })

        self.add_message(response, "assistant")
        self.f_running = False
        return response

    def image_generate(self, pmt:str, file_path:str, model:str='dall-e-3', quality:str='standard', size:str='1024x1024', n:int=1) -> str :
        # size(dalle3): 1024x1024, 1024x1792 or 1792x1024 
        # size(dalle2): 256x256, 512x512, 1024x1024 e2とe3で指定できるサイズが違うので注意！
        # model: dall-e-3, dall-e-2
        # quality: standard, hd

        image_url = None
        try:
            response = self.client.images.generate(
                model  = model,
                prompt = pmt,
                size   = size,
                quality=quality,
                n      = n, #dalle2のみ指定できるみたい
            )
            image_url = response.data[0].url
            url_response = requests.get(image_url)
            if url_response.status_code == 200:
                open(file_path, 'wb').write(url_response.content)
            else:
                print("画像のダウンロードに失敗しました。")

            # 料金は、1枚当たりになるそう( https://platform.openai.com/docs/pricing )
            self.l_cost.append({
                "model" : model + "-" + quality,
                "size"  : size
            })
            self.f_running = False

        except Exception as e:
            error_detail = e.response.json()
            print(f"error in image_generate: {e.response.status_code} - {error_detail['error']['message']}")

        return image_url

    def speech_to_text(self, audio_data, model:str="whisper-1", lang:str='ja', prompt:str=None):
        transcription = self.client.audio.transcriptions.create(
            model                   = model,
            language                = lang,
            file                    = audio_data,
            response_format         = "verbose_json",
            timestamp_granularities = ["segment"],
            prompt                  = prompt
        )

        d_whisper_result = {}
        d_whisper_result["text"] = transcription.text
        d_whisper_result["duration"] = transcription.duration
        d_whisper_result["segments"] = []
        for segment in transcription.segments:
            res_text = {
                "text"  : segment.text, 
                "start" : segment.start, 
                "end"   : segment.end
            }
            d_whisper_result["segments"].append(res_text)

        # 料金は、時間当たりになるそう( https://platform.openai.com/docs/pricing )
        self.l_cost.append({
            "model"     : model,
            "duration"  : transcription.duration
        })
        self.f_running = False
        return d_whisper_result
    
    def speech_to_text_from_file(self, file_path, model:str="whisper-1", lang:str='ja'):
        audio_data = open(file_path, "rb")
        return self.speech_to_text(audio_data, model, lang)
    
    def speech_to_text_pcm(self, audio_data, model:str="whisper-1", lang:str='ja', prompt:str=None):
        audio_buffer = BytesIO()
        p = pyaudio.PyAudio()
        try:
            with wave.open(audio_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(24000)
                wf.writeframes(audio_data)
        finally:
            p.terminate()

        audio_buffer.seek(0)

        d_whisper_result = self.speech_to_text( 
            ("audio.wav", audio_buffer, "audio/wav"), 
            model=model,
            lang=lang,
            prompt=prompt
        )

        return d_whisper_result






    def text_to_speech(self, text:str, file_path:str, voice:str="alloy", model:str='tts-1') -> str :
        """
        alloy : アナウンサー的な男性
        echo : 渋い声のアナウンサー的な男性
        fable : 高い声のアナウンサー的な男性
        onyx : かなり低い俳優的な男性
        nova : アナウンサー的な女性
        shimmer : 低めの声の女性
        """
        response = self.client.audio.speech.create(
            model   = model,
            voice   = f"{voice}",
            input   = text,
        )
        if os.path.exists(file_path) :
            os.remove(file_path) #ファイル削除
        with open(file_path, "wb") as file:
            file.write(response.content)

        # 料金は、1M文字で15ドルとのこと（ https://openai.com/ja-JP/api/pricing/ https://platform.openai.com/docs/pricing )
        # 日本語のような全角文字の扱いはイマイチ不明。日本語でも1文字1カウントという記事が多い。
        self.l_cost.append({
            "model"             : model,
            "text_length_input" : len(text)
        })
        self.f_running = False

    def get_cost_all(self) :
        total_cost = 0
        for item in self.l_cost :
            cost = self.get_cost(item)
            item["cost"] = cost
            total_cost += cost
        return {"totalcost": total_cost, "l_cost": self.l_cost}

    def get_cost(self, item:dict=None) :
        d_pricedata = self.d_pricedata
        if not item :
            item = self.l_cost[-1]

        k = item["model"]
        v = item
        if "whisper" in k :
            unitcost = d_pricedata[k]["transcription"]["cost_per_minute"] / 60
            cost = v["duration"] * unitcost
        elif "tts-" in k :
            unitcost = d_pricedata[k]["speech_generation"]["cost_per_1m_characters"]  / 1000000
            cost = v["text_length_input"] * unitcost
        elif "dall-e" in k :
            cost = d_pricedata[k]["image_generation"][f"price_{v['size']}"]
        else :
            pricedata = d_pricedata[k]
            #テキストトークン（入力）
            tokens_input_text_cached  = v["tokens_input_cached"] if "tokens_input_cached" in v and v["tokens_input_cached"] is not None else 0
            tokens_input_text         = v["tokens_input"] if "tokens_input" in v and v["tokens_input"] is not None else 0   - tokens_input_text_cached
            #音声トークン（入力）
            tokens_input_audio_cached = v["tokens_input_audio_cached"] if "tokens_input_audio_cached" in v and v["tokens_input_audio_cached"] is not None else 0
            tokens_input_audio        = v["tokens_input_audio"] if "tokens_input_audio" in v and v["tokens_input_audio"] is not None else 0  - tokens_input_audio_cached
            #テキストトークン（出力）
            tokens_output_text_cached = v["tokens_output_cached"] if "tokens_output_cached" in v and v["tokens_output_cached"] is not None else 0
            tokens_output_text        = v["tokens_output"       ] if "tokens_output"        in v and v["tokens_output"       ] is not None else 0  - tokens_output_text_cached
            #音声トークン（出力）
            tokens_output_audio       = v["tokens_output_audio" ] if "tokens_output_audio"  in v and v["tokens_output_audio" ] is not None else 0

            #ユニットコスト
            unitcost_input_text   = (pricedata["text_tokens" ]["input_tokens" ] if "text_tokens"  in pricedata and "input_tokens"  in pricedata["text_tokens" ] else 0) / 1000000
            unitcost_input_cached = (
                pricedata["text_tokens"]["cached_input_tokens"]
                if "text_tokens" in pricedata and "cached_input_tokens" in pricedata["text_tokens"] and pricedata["text_tokens"]["cached_input_tokens"] is not None
                else 0
            ) / 1000000
            
            unitcost_input_audio  = (pricedata["audio_tokens"]["input_tokens" ] if "audio_tokens" in pricedata and "input_tokens"  in pricedata["audio_tokens"] else 0) / 1000000
            unitcost_input_audio_cached = (
                pricedata["audio_tokens"]["cached_input_tokens"] 
                if "audio_tokens" in pricedata and "cached_input_tokens" in pricedata["audio_tokens"] and pricedata["audio_tokens"]["cached_input_tokens"] is not None 
                else 0
            ) / 1000000

            unitcost_output_text  = (pricedata["text_tokens" ]["output_tokens"] if "text_tokens"  in pricedata and "output_tokens" in pricedata["text_tokens" ] else 0) / 1000000
            unitcost_output_cached = (
                pricedata["text_tokens" ]["cached_output_tokens"] 
                if "text_tokens"  in pricedata and "cached_output_tokens" in pricedata["text_tokens" ] and pricedata["text_tokens" ]["cached_output_tokens"] is not None 
                else 0
            ) / 1000000
            unitcost_output_audio = (pricedata["audio_tokens"]["output_tokens"] if "audio_tokens" in pricedata and "output_tokens" in pricedata["audio_tokens"] else 0) / 1000000

            cost_input = sum([
                unitcost_input_text         * tokens_input_text,
                unitcost_input_cached       * tokens_input_text_cached,
                unitcost_input_audio        * tokens_input_audio,
                unitcost_input_audio_cached * tokens_input_audio_cached
             ])
            cost_output = sum([
                unitcost_output_text   * tokens_output_text,
                unitcost_output_cached * tokens_output_text_cached,
                unitcost_output_audio  * tokens_output_audio
            ])
            cost = cost_input + cost_output

        return cost


    def save_messages(self, file_path:str=None) :
        if not file_path :
            file_path = f"messages_data"
        messages = self.messages_gemini
        for msg in messages:
            if 'parts' in msg:
                for part in msg['parts']:
                    if 'inline_data' in part and 'data' in part['inline_data']:
                        data = part['inline_data']['data']
                        if isinstance(data, bytes):
                            # bytes型ならbase64でエンコードしてstrに
                            part['inline_data']['data'] = base64.b64encode(data).decode('utf-8')
        json.dump(messages            , open(f"{file_path}_gemini.json", "w", encoding="utf-8-sig"), ensure_ascii=False, indent=4)
        json.dump(self.messages       , open(f"{file_path}_openai.json", "w", encoding="utf-8-sig"), ensure_ascii=False, indent=4)
        json.dump(self.messages_claude, open(f"{file_path}_claude.json", "w", encoding="utf-8-sig"), ensure_ascii=False, indent=4)

        # messages = {"openai": self.messages, "claude": self.messages_claude, "gemini": self.messages_gemini}
        # # with open(file_path, "w", encoding="utf-8") as f:
        # #     json.dump(messages, f, ensure_ascii=False, indent=4)
        # with open(f"{file_path}.pkl", "wb") as f:
        #     pickle.dump(messages, f)        

    def load_messages(self, file_path:str=None) :
        if not file_path :
            file_path = f"messages_data"
        messages = json.load(open(f"{file_path}_gemini.json", "r", encoding="utf-8-sig"))
        for msg in messages:
            if 'parts' in msg:
                for part in msg['parts']:
                    if 'inline_data' in part and 'data' in part['inline_data']:
                        data = part['inline_data']['data']
                        if isinstance(data, str):
                            # base64文字列ならbytesにデコード
                            part['inline_data']['data'] = base64.b64decode(data)
        self.messages_gemini = messages
        self.messages        = json.load(open(f"{file_path}_openai.json", "r", encoding="utf-8-sig"))
        self.messages_claude = json.load(open(f"{file_path}_claude.json", "r", encoding="utf-8-sig"))

        # with open(f"{file_path}.pkl", "rb") as f:
        #     messages = pickle.load(f)
        # # with open(file_path, "r", encoding="utf-8") as f:
        # #     messages = json.load(f)

        # self.messages = messages["openai"]
        # self.messages_claude = messages["claude"]
        # self.messages_gemini = messages["gemini"]

    #---------------------------------------------------------
    # プロンプトを整形する（改行ごとに、前後の空白を除去）
    #---------------------------------------------------------
    def format_prompt(self, pmt: str):
        return "\n".join([x.strip() for x in pmt.split("\n")])



def sample_text_to_speech() :
    mo = myopenai("gpt-4.1", model_gemini="gemini-2.5-pro-exp-03-25")
    # mo.text_to_speech("私の名前は、おおむら です。私の声を覚えてください", "speech_sample1_oomura.mp3", voice="alloy")
    # mo.text_to_speech("私の名前は、いちのへ です。私の声を覚えてください", "speech_sample2_ichinohe.mp3", voice="onyx")
    # mo.text_to_speech("私の名前は、かすや です。私の声を覚えてください", "speech_sample3_kasuya.mp3", voice="shimmer")
    # mo.text_to_speech("私の名前は、つがわ です。私の声を覚えてください", "speech_sample4_tsugawa.mp3", voice="nova")
    # mo.text_to_speech("では、チームミーティングを始めたいと思います。今日のファシリはだれだっけ？", "speech_sample_talk1.mp3", voice="alloy")
    # mo.text_to_speech("アサナに書いてますよ。ちょっと待って。今開きますから。", "speech_sample_talk2.mp3", voice="onyx")
    # mo.text_to_speech("今日はかすやさんですね。かすやさん、回してもらっていいですか。", "speech_sample_talk3.mp3", voice="onyx")
    # mo.text_to_speech("了解です。では１つ目の議題から行きましょう。まずは、えーっと、ちょっと待ってくださいね。あー、１つ目はビジョンの確認ですね。", "speech_sample_talk4.mp3", voice="shimmer")

    d_dictionary = [
        {
            "発音": "あさな",
            "単語": "Asana",
            "意味": "タスク管理ツール"
        }
    ]
    mo.add_message("今から名前を読み上げた音声データを渡します。声質からその人の名前を覚えてください")
    mo.add_message_with_audio("大村の声です", "speech_sample1_oomura.mp3")
    mo.add_message_with_audio("一戸の声です", "speech_sample2_ichinohe.mp3")
    mo.add_message_with_audio("粕谷の声です", "speech_sample3_kasuya.mp3")
    mo.add_message_with_audio("津川の声です", "speech_sample4_tsugawa.mp3")

    mo.add_message(f"それでは、次に会議を録音した音声データを渡します。文章の文字起こしに加えて、誰がしゃべっているかも特定してください。\n会議で使われている専門的な単語の辞書を参考に文字起こししてください。\n\n#専門的な単語辞書: ```\n{d_dictionary}\n```")
    mo.add_message_with_audio("", "speech_sample_talk1.mp3")
    res = mo.run_gemini()
    print(res)

    mo.add_message_with_audio("", "speech_sample_talk2.mp3")
    res = mo.run_gemini()
    print(res)

    mo.add_message_with_audio("", "speech_sample_talk3.mp3")
    res = mo.run_gemini()
    print(res)

    mo.add_message_with_audio("", "speech_sample_talk4.mp3")
    res = mo.run_gemini()
    print(res)

    print(res)

    

if __name__ == "__main__" :
    # sample_text_to_speech()
    load_dotenv()
    mo = myopenai("gpt-4.1", model_gemini="gemini-2.5-pro-exp-03-25")

    # # 準備(音声ファイル準備)
    # mo.text_to_speech("出身地についても教えて", "speech_sample1.mp3")
    # mo.text_to_speech("奥さんの名前は？", "speech_sample2.mp3")

    # # -----------------------------------------
    # # 使い方あれこれ
    # # -----------------------------------------
    # # OpenAIの場合
    # #単純照会
    # mo.add_message("あなたはアメリカメジャーリーグのスペシャリストです。", role="system")
    # mo.add_message("大谷翔平の誕生日は？")
    # res = mo.run()
    # print(res)
    # print(mo.get_cost_all())

    # #ストリーミング表示
    # mo.add_message("結婚してる？")
    # run_thread = threading.Thread(target=mo.run_stream, kwargs={})
    # run_thread.start()
    # while mo.is_running_or_queue():
    #     print(mo.get_queue(), end="", flush=True)
    #     time.sleep(0.1)
    # print("\n")
    # run_thread.join()

    # # 音声で質問 --> 文章で回答
    # mo.add_audio_fromfile("speech_sample1.mp3")
    # res = mo.run(model="gpt-4o-mini-audio-preview") #音声が入っている場合は、このモデルがマスト
    # print(res)
    # print(mo.get_cost_all())

    # mo.save_messages()
    # mo.load_messages()

    #-----------------------------------
    #--- Gemini ------------------------
    mo.add_message("あなたはアメリカメジャーリーグのスペシャリストです。", role="system")
    mo.add_message("大谷翔平の誕生日は？")
    res = mo.run_gemini()
    print(res)
    print(mo.get_cost_all())

    #ストリーミング表示は未実装

    # 音声で質問 --> 文章で回答
    mo.add_audio_fromfile("speech_sample1.mp3")
    res = mo.run_gemini()
    print(res)
    print(mo.get_cost_all())


    # #--- 音声で回答させるサンプル --------
    # # 文章で質問->音声で回答
    # mo.delete_all_messages()
    # mo.add_message("大谷翔平の性別は？")
    # wav = mo.run_to_audio(model="gpt-4o-mini-audio-preview") #音声が入っている場合は、このモデルがマスト
    # open("回答.wav", "wb").write(wav)

    # #--- 音声で質問->音声で回答 ------------
    # mo.add_audio_fromfile("speech_sample1.mp3")
    # wav = mo.run_to_audio(model="gpt-4o-mini-audio-preview") #音声が入っている場合は、このモデルがマスト
    # open("回答.wav", "wb").write(wav)

    #-----------------------------------------
    # 構造化データで回答を得る
    #-----------------------------------------
    mo.delete_all_messages()
    mo.add_message("あなたはアメリカメジャーリーグのスペシャリストです。", role="system")
    mo.add_message("大谷翔平と山本由伸の誕生日と出身地を教えて")

    class personal_info(BaseModel) :
        name        : str = Field(...,description="名前")
        birthday    : str = Field(...,description="誕生日")
        syussinchi  : str = Field(...,description="出身地（市まで）") #descは結構重要
    class responsemodel(BaseModel):
        personal_infos : List[personal_info]

    # response_data = mo.run_so(responsemodel)
    # l_personal_infos = [x.model_dump() for x in response_data.personal_infos]
    l_personal_infos = mo.run_so_gemini(responsemodel)
    print(l_personal_infos)

    #-----------------------------------------
    # その他
    #-----------------------------------------
    # 画像生成
    mo.image_generate("もふもふのわんこ","もふもふわんこ.png")

    # Whisper(Speech to Text)
    text = mo.speech_to_text_from_file("speech_sample1.mp3")
    print(text)

    # geminiで文字起こし
    mo.delete_all_messages()
    mo.add_message_with_audio("文字起こしして", "speech_sample1.mp3")
    res = mo.run_gemini()
    print(res)

    #-----------------------------------------
    # 料金計算
    #-----------------------------------------
    print(mo.get_cost_all())
