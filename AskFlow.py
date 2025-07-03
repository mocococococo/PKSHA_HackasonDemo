#!/usr/bin/env python3
# ask_flow_complete.py
"""
住民票フロー: 質問→回答→保存 完全版
requirements : 標準ライブラリのみ
author       : ChatGPT
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union

# --------------------------------------------------
# 設定
# --------------------------------------------------
JSON_FILE          = Path("json/questions.json")        # 入力: 質問定義
OUTPUT_ANSWERS     = Path("json/answers.json")          # 出力: 回答だけ
OUTPUT_QUEST_FILLED = Path("questions_filled.json")# 出力: answer 埋込版
START_ID           = "Q1"                          # フロースタート

# --------------------------------------------------
# 質問 I/O
# --------------------------------------------------
def prompt_text(q: Dict[str, Any]) -> str:
    """自由記述を取得"""
    return input(f"\n[{q['id']}] {q['question']}\n> ").strip()

def prompt_bool(q: Dict[str, Any]) -> bool:
    """Yes/No を bool で取得 (y=Yes=True / n=No=False)"""
    while True:
        raw = input(f"\n[{q['id']}] {q['question']} (y/n) > ").strip().lower()
        if raw in ("y", "yes", "1", "true"):
            return True
        if raw in ("n", "no", "0", "false"):
            return False
        print("※ y か n で答えてください")

def prompt_user(q: Dict[str, Any]) -> Union[str, bool]:
    """type に応じて質問し、回答を返す"""
    if q["type"] == "text":
        return prompt_text(q)
    if q["type"] == "bool":
        return prompt_bool(q)
    raise ValueError(f"未知の type: {q['type']}")

# --------------------------------------------------
# 遷移ロジック
# --------------------------------------------------
def resolve_next(q: Dict[str, Any], answer: Union[str, bool]) -> Union[str, None]:
    """
    q["next"] を解析し次 ID を返す
      - next == str                     : そのまま
      - next == dict                    : キーにマッチ / default
    """
    nxt = q.get("next")
    if nxt is None:                              # 終端
        return None
    # 文字列なら直接
    if isinstance(nxt, str):
        return nxt or None
    # dict（分岐テーブル）
    if isinstance(nxt, dict):
        key: str
        if isinstance(answer, bool):             # bool → "Yes"/"No"
            key = "Yes" if answer else "No"
        else:
            key = answer
        # CSV（カンマ区切り）なら個別に確認
        if isinstance(key, str) and "," in key:
            for part in (s.strip() for s in key.split(",")):
                if part in nxt:
                    return nxt[part] or None
        # 直接マッチ or default
        return nxt.get(key) or nxt.get("default")
    return None

# --------------------------------------------------
# 入出力ヘルパ
# --------------------------------------------------
def load_questions() -> List[Dict[str, Any]]:
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    return data

def save_answers_dict(answers: Dict[str, Any]) -> None:
    OUTPUT_ANSWERS.write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n✔ 回答を {OUTPUT_ANSWERS} に保存しました。")

def save_filled_questions(questions: List[Dict[str, Any]]) -> None:
    OUTPUT_QUEST_FILLED.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✔ answer 付き質問集を {OUTPUT_QUEST_FILLED} に保存しました。")

# --------------------------------------------------
# メインフロー
# --------------------------------------------------
def main() -> None:
    questions: List[Dict[str, Any]] = load_questions()
    # id → obj 辞書
    qmap = {q["id"]: q for q in questions}
    answers: Dict[str, Any] = {}

    current = START_ID
    while current:
        q = qmap[current]

        ans = prompt_user(q)
        # 1. オブジェクトに保存
        q["answer"] = ans
        # 2. 平坦な dict にも保存
        answers[current] = ans

        # 次の ID
        current = resolve_next(q, ans)

    # 保存
    save_answers_dict(answers)
    save_filled_questions(questions)
    print("\n=== すべての入力が完了しました ===")

# --------------------------------------------------
if __name__ == "__main__":
    if not JSON_FILE.exists():
        raise SystemExit(f"質問定義 {JSON_FILE} が見つかりません")
    main()
