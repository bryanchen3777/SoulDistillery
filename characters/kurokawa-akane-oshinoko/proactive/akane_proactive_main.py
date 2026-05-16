"""
akane_proactive_main.py — 主程式：整合三機制的 Scheduler
放置：/home/bbf/.hermes/plugins/akane_proactive/akane_proactive_main.py

env:
  PALACE_BASE
  AKANE_TELEGRAM_TOKEN
  AKANE_TELEGRAM_CHAT_ID
  AKANE_LLM_BASE_URL   (default: http://localhost:11434)
  AKANE_LLM_MODEL      (default: gemma3:12b)

執行方式：
  python3 akane_proactive_main.py
"""

import os, sys, json, time
from datetime import datetime, timedelta

_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(_DIR, "akane_proactive_state.json")

sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_behavior")
sys.path.insert(0, "/home/bbf/.local/bin/hermes")
sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_proactive")

from akane_state import load_state as load_akane_state, AkaneState
from akane_fsm_watcher import check_fsm_triggers
from akane_external_watcher import check_external_triggers
from akane_life_events import sample_life_event, check_life_event_cooldown, WEEKLY_LIMIT
from akane_message_sender import generate_and_push
from akane_agreements import check_agreements


def load_proactive_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_any_message_ts": None,
            "weekly_life_event_count": 0,
            "weekly_reset_ts": None,
            "last_user_message_ts": None,
            "cooldowns": {
                "A1_echo_spike": None,
                "A2_pre_collapse": None,
                "A3_recovery": None,
                "B1_silence": None,
                "B2_late_night": None,
                "B3_stress_keywords": None,
                "C_life_event": None,
                "D_agreement": None,
            }
        }


def save_proactive_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def touch_message():
    state = load_proactive_state()
    state["last_any_message_ts"] = datetime.now().isoformat()
    save_proactive_state(state)


def update_user_message_ts():
    state = load_proactive_state()
    state["last_user_message_ts"] = datetime.now().isoformat()
    save_proactive_state(state)


def update_cooldown(trigger: str):
    state = load_proactive_state()
    state["cooldowns"][trigger] = datetime.now().isoformat()
    save_proactive_state(state)


def weekly_reset_check():
    state = load_proactive_state()
    now = datetime.now()
    reset_ts = state.get("weekly_reset_ts")
    if reset_ts is None:
        state["weekly_reset_ts"] = now.isoformat()
        save_proactive_state(state)
        return
    last_reset = datetime.fromisoformat(reset_ts)
    if (now - last_reset).days >= 7:
        state["weekly_life_event_count"] = 0
        state["weekly_reset_ts"] = now.isoformat()
        save_proactive_state(state)


def run_cycle():
    weekly_reset_check()
    proactive = load_proactive_state()
    akane_state = load_akane_state()

    triggered = []

    # ── 機制一：FSM 變化 ──
    prev_state_path = "/home/bbf/.hermes/palace/agents/akane/states/current_state.json"
    try:
        with open(prev_state_path, "r") as f:
            prev_data = json.load(f)
            prev_state = AkaneState(
                stress=prev_data.get("stress", 20),
                echo_level=prev_data.get("echo_level", 0),
                attachment_to_user=prev_data.get("attachment_to_user", 0.1),
                emotional_state=prev_data.get("emotional_state", "OBSERVATION"),
                collapse_risk=prev_data.get("collapse_risk", 0.0),
            )
    except Exception:
        prev_state = akane_state

    fsm_triggers = check_fsm_triggers(prev_state, akane_state, proactive["cooldowns"])
    triggered.extend(fsm_triggers)

    # ── 機制二：外部事件 ──
    last_history = []
    ext_triggers = check_external_triggers(
        akane_state, proactive,
        proactive.get("last_user_message_ts"),
        last_history
    )
    triggered.extend(ext_triggers)

    # ── 機制三：Life Events ──
    if (check_life_event_cooldown(proactive["cooldowns"])
            and proactive["weekly_life_event_count"] < WEEKLY_LIMIT):
        import random
        if random.random() < 0.2:
            event = sample_life_event()
            triggered.append(("C_life_event", event))

    # ── 機制四：Agreements ──
    agr_triggers = check_agreements(
        akane_state,
        proactive.get("last_user_message_ts"),
        last_history
    )
    for item in agr_triggers:
        triggered.append(("D_agreement", item["agreement"], item["context"]))

    # ── 執行所有觸發 ──
    for item in triggered:
        if isinstance(item, tuple) and len(item) == 3:
            trigger, agreement, context = item
            event = ""
        elif isinstance(item, tuple):
            trigger, event = item
            agreement, context = None, ""
        else:
            trigger, event = item, ""
            agreement, context = None, ""

        ok = generate_and_push(trigger, akane_state, event=event,
                               agreement=agreement, context=context)
        if ok:
            update_cooldown(trigger)
            if trigger == "C_life_event":
                proactive = load_proactive_state()
                proactive["weekly_life_event_count"] += 1
                save_proactive_state(proactive)
            touch_message()

    return len(triggered) > 0


if __name__ == "__main__":
    print(f"[AKANE_PROACTIVE] Starting scheduler (60s cycle)")
    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"[AKANE_PROACTIVE] cycle error: {e}")
        time.sleep(60)
