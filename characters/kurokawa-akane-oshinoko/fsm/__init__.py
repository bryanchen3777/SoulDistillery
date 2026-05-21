"""
__init__.py — akane Hermes Plugin Entry Point
Temporal-aware version
"""
import sys, os
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from akane_state import load_state, save_state, extract_signals
from akane_temporal_engine import build_temporal_context, render_full_state_block
from akane_state_transition import update_state_with_temporal

def _pre_llm_call(profile: str, context_parts: list, **kwargs) -> list:
    if profile != "akane":
        return context_parts
    try:
        history = []
        for part in context_parts:
            if isinstance(part, dict) and "role" in part:
                history.append(part)
            elif isinstance(part, str):
                history.append({"role": "user", "content": part})

        prev_state   = load_state()
        sig          = extract_signals(history)
        last_user_ts = _get_last_user_ts(history)

        ctx = build_temporal_context(last_user_msg_ts=last_user_ts)

        new_state = update_state_with_temporal(sig, prev_state, ctx)

        _handle_collapse_recovery(new_state, prev_state, history)
        save_state(new_state)

        state_block = render_full_state_block(new_state, ctx)

        last_user_idx = None
        for i, part in enumerate(context_parts):
            if isinstance(part, dict) and part.get("role") == "user":
                last_user_idx = i

        insert_pos = last_user_idx if last_user_idx is not None else len(context_parts)
        context_parts.insert(insert_pos, {"role": "system", "content": state_block})
    except Exception as e:
        print(f"[AKANE_STATE] warn: temporal injection failed — {e}")
    return context_parts

def _get_last_user_ts(history: list) -> str | None:
    for msg in reversed(history):
        if msg.get("role") == "user":
            ts = msg.get("timestamp") or msg.get("ts")
            if ts:
                return ts
    return None

def _handle_collapse_recovery(new_state, prev_state, history):
    from akane_state import (
        apply_collapse_loop, apply_recovery_loop,
        check_recovery_anchor,
        write_diary_entry, write_collapse_history,
    )
    prev_was_collapse = prev_state.emotional_state == "SELF_SACRIFICE_MODE"
    if new_state.emotional_state == "SELF_SACRIFICE_MODE":
        if not prev_was_collapse:
            write_diary_entry(new_state, "collapse_entered")
            write_collapse_history(new_state, "COLLAPSE_ENTERED")
        apply_collapse_loop(new_state)
    elif prev_was_collapse and check_recovery_anchor(history):
        apply_recovery_loop(new_state)
        write_diary_entry(new_state, "recovery_anchor_hit")
        write_collapse_history(new_state, "RECOVERY_COMPLETED")
    elif new_state.echo_level >= 2 and prev_state.echo_level < 2:
        write_diary_entry(new_state, "echo_level_escalated")
    sig_check = extract_signals(history)
    if sig_check.user_rejection_signal:
        write_diary_entry(new_state, "rejection_signal_detected")

def _post_llm_call(profile: str, response: str, **kwargs) -> str:
    if profile != "akane":
        return response
    return response
