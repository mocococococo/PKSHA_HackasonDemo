import json
import logging

class TaskDataSession:
    """
    タスク名と task.json を使って、
    必要なフィールドを１つずつユーザーに問いかけるセッション管理クラス。
    """
    def __init__(self, task_name: str, task_json_path: str = "task.json"):
        # task.json の読み込み
        with open(task_json_path, "r", encoding="utf-8") as f:
            all_tasks = json.load(f).get("tasks", [])
        #print(f"task.json から読み込んだタスク: {all_tasks}")
        # 該当タスク情報の取得
        info = next((t for t in all_tasks if t.get("name") == task_name), None)
        if not info or not info.get("data"):
            raise ValueError(f"task.json に task '{task_name}' の data 定義がありません。")
        # data は {キー: 表示ラベル} の想定
        self.fields = list(info["data"].items())
        self.collected = {}
        self.idx = 0

    def has_next(self) -> bool:
        return self.idx < len(self.fields)

    def next_prompt(self) -> str:
        key, label = self.fields[self.idx]
        # 日本語ラベルがあればそれを、なければキー名を
        return f"{label} を入力してください: " if isinstance(label, str) else f"{key} を入力してください: "

    def process_response(self, response: str):
        key, _ = self.fields[self.idx]
        self.collected[key] = response.strip()
        self.idx += 1

    def get_collected(self) -> dict:
        return self.collected