"""
akane_external_watcher.py — 機制二：外部事件觸發
"""

import os, sys
from datetime import datetime, timedelta

sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_behavior")
from akane_state import AkaneState, extract_signals

COOLDOWNS = {
    "B1_silence":         timedelta(hours=12),
    "B2_late_night":     timedelta(hours=24),
    "B3_stress_keywords": timedelta(hours=6),
}

def silence_threshold_hours(attachment: float) -> float:
    return max(4.0, 24.0 - (attachment * 20.0))

def check_external_triggers(state: AkaneState, proactive_state: dict,
                             last_user_msg_ts: str | None,
                             last_history: list) -> list[str]:
    results = []
    now     = datetime.now()
    cooldowns = proactive_state.get("cooldowns", {})

    if last_user_msg_ts and state.attachment_to_user >= 0.5:
        last_ts    = datetime.fromisoformat(last_user_msg_ts)
        elapsed_h  = (now - last_ts).total_seconds() / 3600
        threshold  = silence_threshold_hours(state.attachment_to_user)
        last_cool  = cooldowns.get("B1_silence")
        cool_ok    = (last_cool is None or
                      now - datetime.fromisoformat(last_cool) > COOLDOWNS["B1_silence"])
        if elapsed_h > threshold and cool_ok:
            results.append("B1_silence")

    hour = now.hour
    if hour >= 1 and hour <= 4:
        if last_user_msg_ts:
            last_ts = datetime.fromisoformat(last_user_msg_ts)
            if (now - last_ts).total_seconds() < 1800:
                last_cool = cooldowns.get("B2_late_night")
                cool_ok   = (last_cool is None or
                             now - datetime.fromisoformat(last_cool) > COOLDOWNS["B2_late_night"])
                if cool_ok:
                    results.append("B2_late_night")

    if last_history:
        sig = extract_signals(last_history, window=4)
        if sig.user_negative_emotion > 0.5:
            last_cool = cooldowns.get("B3_stress_keywords")
            cool_ok   = (last_cool is None or
                         now - datetime.fromisoformat(last_cool) > COOLDOWNS["B3_stress_keywords"])
            if cool_ok:
                results.append("B3_stress_keywords")

    return results
