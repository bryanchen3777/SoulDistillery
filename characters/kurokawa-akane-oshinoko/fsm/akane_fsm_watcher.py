"""
akane_fsm_watcher.py — 機制一：FSM 狀態變化觸發
"""

import json, os
from datetime import datetime, timedelta
from akane_state import AkaneState

COOLDOWNS = {
    "A1_echo_spike":    timedelta(hours=4),
    "A2_pre_collapse":  timedelta(hours=6),
    "A3_recovery":       timedelta(hours=0),
}

def check_fsm_triggers(prev: AkaneState, curr: AkaneState,
                        cooldowns: dict) -> list[str]:
    results = []
    now = datetime.now()

    if prev.echo_level <= 1 and curr.echo_level >= 2:
        last = cooldowns.get("A1_echo_spike")
        if last is None or now - datetime.fromisoformat(last) > COOLDOWNS["A1_echo_spike"]:
            results.append("A1_echo_spike")

    if (0.55 <= curr.collapse_risk < 0.65
            and curr.attachment_to_user >= 0.5):
        last = cooldowns.get("A2_pre_collapse")
        if last is None or now - datetime.fromisoformat(last) > COOLDOWNS["A2_pre_collapse"]:
            results.append("A2_pre_collapse")

    if (prev.emotional_state == "SELF_SACRIFICE_MODE"
            and curr.emotional_state != "SELF_SACRIFICE_MODE"):
        results.append("A3_recovery")

    return results
