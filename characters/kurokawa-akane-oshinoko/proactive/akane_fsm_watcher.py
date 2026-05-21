"""
akane_fsm_watcher.py — 機制一：FSM 狀態變化觸發
含 derived_emotional_state 觸發（A4/A5/A6）
"""
from datetime import datetime, timedelta
from akane_state import AkaneState

COOLDOWNS = {
    "A1_echo_spike":        timedelta(hours=4),
    "A2_pre_collapse":      timedelta(hours=6),
    "A3_recovery":          timedelta(hours=2),
    "A4_checking_presence": timedelta(hours=8),
    "A5_night_leaking":     timedelta(hours=6),
    "A6_fragile":           timedelta(hours=4),
}

def check_fsm_triggers(prev: AkaneState, curr: AkaneState,
                        cooldowns: dict) -> list[str]:
    results = []
    now     = datetime.now()

    def cool_ok(key):
        last = cooldowns.get(key)
        if last is None:
            return True
        cd = COOLDOWNS.get(key)
        if cd is None or cd.total_seconds() == 0:
            return True
        return now - datetime.fromisoformat(last) > cd

    if prev.echo_level <= 1 and curr.echo_level >= 2:
        if cool_ok("A1_echo_spike"):
            results.append("A1_echo_spike")

    if (0.55 <= curr.collapse_risk < 0.65
            and curr.attachment_to_user >= 0.5):
        if cool_ok("A2_pre_collapse"):
            results.append("A2_pre_collapse")

    if (prev.emotional_state == "SELF_SACRIFICE_MODE"
            and curr.emotional_state != "SELF_SACRIFICE_MODE"):
        results.append("A3_recovery")

    derived = getattr(curr, "derived_emotional_state", "stable")

    if derived == "checking_presence":
        if cool_ok("A4_checking_presence"):
            results.append("A4_checking_presence")

    if derived == "night_leaking":
        if cool_ok("A5_night_leaking"):
            results.append("A5_night_leaking")

    if derived == "fragile":
        if cool_ok("A6_fragile"):
            results.append("A6_fragile")

    return results
