import google.generativeai as genai
import json

class ChatBot:
    def __init__(self, model):
        self.model = model

    def chat(self, message):
        response = self.model.chat(message)
        return response.text if response else "モデルからの応答がありません。"
    
    def get_api_key(self, api_key_json_path):
        try:
            with open(api_key_json_path, "r", encoding="utf-8") as f:
                api_key_data = json.load(f)
            return api_key_data.get("GeminiAPIKey", "")
        except Exception as e:
            print(f"APIキーの読み込み中にエラーが発生しました: {e}")
            return None
        
    def configure_model(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            print("APIキーが提供されていません。モデルを設定できません。")
            self.model = None
            
    def is_model_configured(self):
        return self.model is not None
    
    def get_input(self, prompt):
        try:
            return input(prompt)
        except EOFError:
            print("入力が終了しました。")
            return None
        except KeyboardInterrupt:
            print("\n入力がキャンセルされました。")
            return None
        except Exception as e:
            print(f"入力中にエラーが発生しました: {e}")
            return None