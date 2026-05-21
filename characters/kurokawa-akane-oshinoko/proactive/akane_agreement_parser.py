"""
akane_agreement_parser.py
自然語言 → 結構化 Agreement
"""

import os, re, json, sys, uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_proactive")
from akane_agreements import add_agreement

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_MODEL   = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.7")
MINIMAX_URL     = "https://api.minimax.io/v1/text/chatcompletion_v2"

DETECTION_PATTERNS = [
    r"如果我.{1,20}(就|你要|記得|提醒|告訴我)",
    r"你要記得.{1,30}",
    r"我們說好.{1,30}",
    r"如果.{1,20}超過.{1,10}(天|小時|hour|day)",
    r"(提醒|告訴)我.{1,20}",
    r"你能不能.{1,20}(提醒|告訴|說)",
    r"約好.{1,20}",
]

PARSE_SYSTEM_PROMPT = """
你是 Agreement Parser。
判斷使用者訊息是否包含「未來條件約定」。

若是，只輸出 JSON（不要任何說明文字）：
{
  "type": "silence_timeout | keyword_trigger | time_of_day | negative_streak | fsm_state_alert | topic_absence",
  "params": {...},
  "cooldown_hours": 12,
  "raw_summary": "用一句話描述這個約定"
}

type 說明：
- silence_timeout：沉默超過 N 小時/天 → params: {"hours": N}
- keyword_trigger：出現特定詞 → params: {"keywords": ["..."]}
- time_of_day：特定時間 → params: {"hour": H, "minute": M}
- negative_streak：連續負面 → params: {"window_turns": 6}
- fsm_state_alert：茜進入特定狀態 → params: {"states": ["SELF_SACRIFICE_MODE"]}
- topic_absence：話題消失 N 天 → params: {"keywords": ["..."], "days": N}

若不是約定句 → 只輸出：{"type": null}
"""

def detect_agreement_intent(message: str) -> bool:
    for pat in DETECTION_PATTERNS:
        if re.search(pat, message):
            return True
    return False

def parse_agreement_with_llm(message: str) -> dict | None:
    import requests
    try:
        resp = requests.post(
            MINIMAX_URL,
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       MINIMAX_MODEL,
                "max_tokens":  200,
                "prompt":      PARSE_SYSTEM_PROMPT,
                "messages":    [{"role": "user",
                                 "content": f"使用者說：「{message}」"}],
            },
            timeout=20,
        )
        resp.raise_for_status()
        raw = ""
        choices = resp.json().get("choices", [])
        if choices and len(choices) > 0:
            raw = choices[0].get("message", {}).get("content", "").strip()
        parsed = json.loads(raw)
        if parsed.get("type") is None:
            return None
        return parsed
    except Exception as e:
        print(f"[AGREEMENT_PARSER] LLM error: {e}")
        return None

def handle_user_message(message: str) -> bool:
    if not detect_agreement_intent(message):
        return False
    parsed = parse_agreement_with_llm(message)
    if not parsed:
        return False
    agreement = {
        "id":           f"agr_{uuid.uuid4().hex[:8]}",
        "raw":          message,
        "raw_summary":  parsed.get("raw_summary", ""),
        "type":         parsed["type"],
        "params":       parsed.get("params", {}),
        "cooldown_hours": parsed.get("cooldown_hours", 12),
        "active":       True,
        "created_ts":   datetime.now().isoformat(),
        "last_triggered_ts": None,
    }
    add_agreement(agreement)
    print(f"[AGREEMENT_PARSER] Stored: {agreement['id']} ({parsed['type']})")
    return True
