"""
akane_state_transition.py
職責：temporal modifier 真正接進 FSM transition
      + derived_emotional_state 派生
"""
from __future__ import annotations
from akane_state import AkaneState, Signals, _clamp, COLLAPSE_THRESHOLD
from akane_temporal_engine import TemporalContext

# ─────────────────────────────────────────────
# 1. DERIVED EMOTIONAL STATE
# ─────────────────────────────────────────────

def derive_emotional_state(
    state:      AkaneState,
    ctx:        TemporalContext,
    prev_state: AkaneState | None = None,
) -> str:
    if (prev_state is not None
            and prev_state.emotional_state == "SELF_SACRIFICE_MODE"
            and state.emotional_state != "SELF_SACRIFICE_MODE"):
        return "post_collapse_recovery"
    if ctx.silence_hours > 48 and state.attachment_to_user > 0.6:
        return "checking_presence"
    fragile_threshold = 65 if ctx.is_late_night else 75
    if state.stress > fragile_threshold and ctx.defense_level < 0.5:
        return "fragile"
    if state.echo_level >= 2 and ctx.analysis_capacity < 0.65:
        return "identity_blur"
    if state.stress > 70 and state.emotional_state == "OBSERVATION":
        return "over_normal"
    if ctx.is_late_night and ctx.defense_level < 0.4 and state.stress > 30:
        return "night_leaking"
    if ctx.analysis_capacity > 0.85 and state.stress < 30:
        return "deep_analysis"
    if state.attachment_to_user > 0.6 and state.stress < 40:
        return "attached_stable"
    return "stable"

# ─────────────────────────────────────────────
# 2. TEMPORAL-AWARE STATE UPDATERS
# ─────────────────────────────────────────────

def compute_stress_temporal(sig: Signals, prev: AkaneState,
                             ctx: TemporalContext) -> int:
    s = prev.stress * 0.88
    base_delta = (
        sig.user_negative_emotion  * 8
      + sig.user_dependence_signal * 6
      + sig.conversation_intensity * 3
      + sig.time_without_affection * 2
    )
    if sig.user_rejection_signal:
        base_delta += 18
    s += base_delta * ctx.emotional_multiplier
    if ctx.suppress_decay:
        s = s * 1.08
    return int(_clamp(s, 0, 100))

def compute_echo_temporal(sig: Signals, prev: AkaneState,
                           ctx: TemporalContext) -> int:
    e = float(prev.echo_level) - 0.4
    if sig.user_dependence_signal > 0.85 and sig.user_negative_emotion > 0.7:
        e += 1
    if sig.user_mentions_aqua:
        e += 1
    if sig.user_negative_emotion > 0.9:
        e += 1
    if ctx.analysis_capacity < 0.65 and e > 0:
        e += 0.5
    if ctx.is_late_night and sig.user_mentions_aqua:
        e += 0.5
    return int(_clamp(round(e), 0, 3))

def update_attachment_temporal(sig: Signals, prev: AkaneState,
                                ctx: TemporalContext) -> float:
    att = prev.attachment_to_user
    att += sig.user_affection     * 0.08
    att += sig.user_vulnerability * 0.05
    if sig.user_rejection_signal:
        att -= 0.10
    if ctx.attachment_drift > 0 and sig.user_affection > 0:
        att += sig.user_affection * ctx.attachment_drift * 0.5
    if ctx.is_late_night and sig.user_rejection_signal:
        att -= 0.05
    return _clamp(att, 0.0, 1.0)

# ─────────────────────────────────────────────
# 3. FULL TEMPORAL-AWARE UPDATE
# ─────────────────────────────────────────────

def update_state_with_temporal(
    sig:   Signals,
    prev:  AkaneState,
    ctx:   TemporalContext,
) -> AkaneState:
    from akane_state import (
        compute_collapse_risk,
        compute_emotional_state,
        compute_risk_flags,
    )
    stress     = compute_stress_temporal(sig, prev, ctx)
    echo       = compute_echo_temporal(sig, prev, ctx)
    attachment = update_attachment_temporal(sig, prev, ctx)
    new_state = AkaneState(
        stress             = stress,
        echo_level         = echo,
        attachment_to_user = attachment,
        emotional_state    = "OBSERVATION",
        collapse_risk      = 0.0,
        risk_flags         = [],
    )
    new_state.collapse_risk            = compute_collapse_risk(new_state)
    new_state.emotional_state          = compute_emotional_state(new_state)
    new_state.risk_flags               = compute_risk_flags(sig, new_state)
    new_state.derived_emotional_state  = derive_emotional_state(
        new_state, ctx, prev_state=prev
    )
    return new_state

# ─────────────────────────────────────────────
# 4. RENDER (with current_time)
# ─────────────────────────────────────────────

def render_full_state_block(state: AkaneState, ctx: TemporalContext) -> str:
    flags_str = ", ".join(state.risk_flags) if state.risk_flags else "none"
    derived   = getattr(state, "derived_emotional_state", "stable")
    return (
        f"\n[AKANE_STATE]\n"
        f"current_time={ctx.current_time}\n"
        f"derived_state={derived}\n"
        f"time_period={ctx.time_period}\n"
        f"emotional_state={state.emotional_state}\n"
        f"stress={state.stress}/100\n"
        f"echo_level={state.echo_level}/3\n"
        f"defense={ctx.defense_level:.2f}\n"
        f"analysis={ctx.analysis_capacity:.2f}\n"
        f"collapse_risk={state.collapse_risk:.2f}\n"
        f"attachment={state.attachment_to_user:.2f}\n"
        f"silence_h={ctx.silence_hours:.1f}\n"
        f"risk_flags=[{flags_str}]\n"
        f"[/AKANE_STATE]\n"
    )
