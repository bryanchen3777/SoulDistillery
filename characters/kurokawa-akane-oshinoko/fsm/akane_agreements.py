"""
akane_agreements.py
Storage API + Agreement Checker
"""

import json, sys, os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_behavior")
from akane_state import AkaneState, extract_signals

AGREEMENT_FILE = Path(
    os.environ.get("PALACE_BASE", "/home/bbf/.hermes/palace")
) / "akane/agreements.json"

# ─────────────────────────────
# Storage API（底層）
# ─────────────────────────────

def _load_db() -> Dict[str, Any]:
    if not AGREEMENT_FILE.exists():
        return {"agreements": []}
    return json.loads(AGREEMENT_FILE.read_text(encoding="utf-8"))

def _save_db(db: Dict[str, Any]):
    AGREEMENT_FILE.write_text(
        json.dumps(db, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def list_agreements() -> List[Dict]:
    return _load_db()["agreements"]

def add_agreement(agreement: Dict):
    db = _load_db()
    db["agreements"].append(agreement)
    _save_db(db)

def update_last_triggered(agreement_id: str):
    db = _load_db()
    for a in db["agreements"]:
        if a["id"] == agreement_id:
            a["last_triggered_ts"] = datetime.now().isoformat()
    _save_db(db)

def deactivate_agreement(agreement_id: str):
    db = _load_db()
    for a in db["agreements"]:
        if a["id"] == agreement_id:
            a["active"] = False
    _save_db(db)

# ─────────────────────────────
# Cooldown Check
# ─────────────────────────────

def _cooldown_ok(agr: Dict) -> bool:
    last_t  = agr.get("last_triggered_ts")
    cool_h  = agr.get("cooldown_hours", 12)
    if cool_h == 0:
        return True
    if last_t is None:
        return True
    elapsed = (datetime.now() - datetime.fromisoformat(last_t)).total_seconds() / 3600
    return elapsed >= cool_h

# ─────────────────────────────
# Type Checkers
# ─────────────────────────────

def _check_silence_timeout(agr: Dict, last_user_msg_ts: str | None) -> tuple[bool, str]:
    if not last_user_msg_ts:
        return False, ""
    hours   = agr["params"].get("hours", 24)
    last_ts = datetime.fromisoformat(last_user_msg_ts)
    elapsed = (datetime.now() - last_ts).total_seconds() / 3600
    if elapsed >= hours:
        return True, f"沉默了 {elapsed:.0f} 小時（約定 {hours} 小時）"
    return False, ""

def _check_keyword_trigger(agr: Dict, last_history: list) -> tuple[bool, str]:
    keywords    = agr["params"].get("keywords", [])
    recent_text = " ".join(
        m["content"] for m in last_history[-6:]
        if m.get("role") == "user"
    )
    for kw in keywords:
        if kw in recent_text:
            return True, f"偵測到關鍵字：{kw}"
    return False, ""

def _check_time_of_day(agr: Dict) -> tuple[bool, str]:
    now      = datetime.now()
    target_h = agr["params"].get("hour", 9)
    target_m = agr["params"].get("minute", 0)
    if now.hour == target_h and abs(now.minute - target_m) <= 5:
        return True, f"約定時間 {target_h:02d}:{target_m:02d}"
    return False, ""

def _check_negative_streak(agr: Dict, state: AkaneState,
                            last_history: list) -> tuple[bool, str]:
    window = agr["params"].get("window_turns", 6)
    sig    = extract_signals(last_history, window=window)
    if sig.user_negative_emotion > 0.4 and state.stress > 50:
        return True, f"連續負面訊號，stress={state.stress}"
    return False, ""

def _check_fsm_state_alert(agr: Dict, state: AkaneState) -> tuple[bool, str]:
    target_states = agr["params"].get("states", [])
    if state.emotional_state in target_states:
        return True, f"茜進入 {state.emotional_state}"
    return False, ""

def _check_topic_absence(agr: Dict) -> tuple[bool, str]:
    keywords = agr["params"].get("keywords", [])
    days     = agr["params"].get("days", 7)
    diary_path = Path(
        os.environ.get("PALACE_BASE", "/home/bbf/.hermes/palace")
    ) / "agents/akane/feelings/diary.md"
    if not diary_path.exists():
        return False, ""
    content = diary_path.read_text(encoding="utf-8")
    last_mention = None
    for line in content.split("\n"):
        if any(kw in line for kw in keywords):
            try:
                date_str = line.split("|").replace("**","").strip()
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                if last_mention is None or dt > last_mention:
                    last_mention = dt
            except Exception:
                pass
    if last_mention:
        elapsed_days = (datetime.now() - last_mention).days
        if elapsed_days >= days:
            return True, f"{elapsed_days} 天沒提到相關話題"
    elif last_mention is None:
        return True, f"從未提到相關話題"
    return False, ""

# ─────────────────────────────
# Main Checker
# ─────────────────────────────

TYPE_CHECKERS = {
    "silence_timeout":  lambda agr, state, hist, ts:
                        _check_silence_timeout(agr, ts),
    "keyword_trigger":  lambda agr, state, hist, ts:
                        _check_keyword_trigger(agr, hist),
    "time_of_day":      lambda agr, state, hist, ts:
                        _check_time_of_day(agr),
    "negative_streak":  lambda agr, state, hist, ts:
                        _check_negative_streak(agr, state, hist),
    "fsm_state_alert":  lambda agr, state, hist, ts:
                        _check_fsm_state_alert(agr, state),
    "topic_absence":    lambda agr, state, hist, ts:
                        _check_topic_absence(agr),
}

def check_agreements(state: AkaneState,
                     last_user_msg_ts: str | None,
                     last_history: list) -> list[dict]:
    """
    掃描所有 active 約定，回傳成立的項目
    回傳格式：[{"agreement": agr, "context": str}]
    """
    triggered = []
    for agr in list_agreements():
        if not agr.get("active"):
            continue
        if not _cooldown_ok(agr):
            continue
        checker = TYPE_CHECKERS.get(agr["type"])
        if not checker:
            continue
        matched, context = checker(agr, state, last_history, last_user_msg_ts)
        if matched:
            triggered.append({"agreement": agr, "context": context})
            update_last_triggered(agr["id"])
    return triggered
