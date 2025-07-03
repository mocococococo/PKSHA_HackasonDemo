import google.generativeai as genai
import json
import logging
from CreateTask2Data import TaskDataSession

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

api_key_json_path = "apikey.json"
api_key_data = ""
with open(api_key_json_path, "r", encoding="utf-8") as f:
    api_key_data = json.load(f)
api_key = api_key_data.get("GeminiAPIKey", "")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

DEFAULT_TASK_INFO = {"task": ""}
    
def get_task_from_utterance(utterance: str) -> dict:
    if not model:
        logging.error("Geminiモデルが初期化されていません。デフォルト値を返します。")
        return DEFAULT_TASK_INFO.copy()

    prompt = open("prompt.txt", "r", encoding="utf-8").read()
    prompt = prompt.replace("{utterance}", utterance)
    task_json = None
    with open("json/task.json", "r", encoding="utf-8") as f:
        task_json = json.load(f)
    task_json = json.dumps(task_json, ensure_ascii=False)
    prompt = prompt.replace("{task_json}", task_json)

    logging.info(f"Geminiに送信するプロンプト:\n---\n{prompt}\n---")

    try:
        response = model.generate_content(prompt)

        if not response.parts:
             logging.warning(f"Geminiからの応答が空またはブロックされました。 Safety feedback: {response.prompt_feedback}")
             return DEFAULT_TASK_INFO.copy()

        response_text = response.text.strip()
        logging.info(f"Geminiからの生レスポンス: {response_text}")

        # Markdownのコードブロック形式 (```json ... ```) を除去
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip() # 再度トリム

        # JSON文字列をPython辞書に変換
        extracted_data = json.loads(response_text)
        
        logging.info(f"抽出されたデータ: {extracted_data}")
        # タスク情報を抽出
        task = extracted_data.get("task", "")

        result = {"task": task}
        logging.info(f"抽出・整形後の結果: {result}")
        return result

    except json.JSONDecodeError as e:
        logging.error(f"Geminiからの応答のJSON解析に失敗しました: {e}")
        logging.error(f"解析対象のテキスト: {response_text}")
        return DEFAULT_TASK_INFO.copy()
    except Exception as e:
        # API呼び出し中のエラーやその他の予期せぬエラー
        logging.error(f"タスクの抽出中に予期せぬエラーが発生しました: {e}")
        # エラーによっては response オブジェクトが存在しない可能性もある
        try:
            logging.error(f"Gemini Safety Feedback (if available): {response.prompt_feedback}")
        except AttributeError:
            pass # response オブジェクトがない場合は無視
        return DEFAULT_TASK_INFO.copy()


# --- 実行例 ---
if __name__ == "__main__":
    if model: # モデルが正常に初期化された場合のみ実行
        #utt = input("発話を入力してください> ")
        utt = "最近引っ越しをしたんですけど..."
        info = get_task_from_utterance(utt)
        print(f"発話: 「{utt}」 -> 抽出結果: {info}")
        task_name = info.get("task")
        try:
            session = TaskDataSession(task_name)
        except ValueError as e:
            logging.error(f"タスクセッションの初期化に失敗しました: {e}")
            print(f"タスクセッションの初期化に失敗しました: {e}")
            exit(1)
        while session.has_next():
            response = input(session.next_prompt())
            session.process_response(response)
        collected_data = session.get_collected()
        print(f"収集されたデータ: {collected_data}")

    else:
        print("Geminiモデルが利用できないため、テストを実行できません。")
        print("apikey.json内の 'GeminiAPIKey' を設定して、再度実行してください。")
