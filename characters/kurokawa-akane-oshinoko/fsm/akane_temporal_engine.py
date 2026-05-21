"""
akane_temporal_engine.py
職責：把「現在幾點」變成「時間對茜的心理影響」
輸出 TemporalContext，供 state_transition 使用
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

TIME_PERIODS = {
    "deep_night": (1,  5),
    "dawn":       (5,  8),
    "morning":    (8,  12),
    "afternoon":  (12, 17),
    "evening":    (17, 21),
    "night":      (21, 24),
}

def get_time_period(hour: int) -> str:
    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    return "deep_night"

@dataclass
class TemporalContext:
    hour:                  int
    time_period:           str
    analysis_capacity:     float
    defense_level:         float
    emotional_leakage:     float
    suppress_decay:        bool
    emotional_multiplier:  float
    attachment_drift:      float
    silence_hours:         float
    is_late_night:         bool
    is_transition_hour:    bool
    current_time:          str   # ← 新增：2026-05-20 14:00 (水曜日)

PERIOD_PROFILES = {
    "deep_night": {
        "analysis_capacity":    0.55,
        "defense_level":        0.35,
        "emotional_leakage":    0.85,
        "suppress_decay":       True,
        "emotional_multiplier": 1.6,
    },
    "dawn": {
        "analysis_capacity":    0.65,
        "defense_level":        0.50,
        "emotional_leakage":    0.60,
        "suppress_decay":       True,
        "emotional_multiplier": 1.3,
    },
    "morning": {
        "analysis_capacity":    0.90,
        "defense_level":        0.80,
        "emotional_leakage":    0.25,
        "suppress_decay":       False,
        "emotional_multiplier": 0.9,
    },
    "afternoon": {
        "analysis_capacity":    0.95,
        "defense_level":        0.85,
        "emotional_leakage":    0.20,
        "suppress_decay":       False,
        "emotional_multiplier": 0.85,
    },
    "evening": {
        "analysis_capacity":    0.80,
        "defense_level":        0.70,
        "emotional_leakage":    0.40,
        "suppress_decay":       False,
        "emotional_multiplier": 1.0,
    },
    "night": {
        "analysis_capacity":    0.65,
        "defense_level":        0.55,
        "emotional_leakage":    0.60,
        "suppress_decay":       True,
        "emotional_multiplier": 1.25,
    },
}

TRANSITION_HOURS = {5, 8, 12, 17, 21, 1}

def compute_attachment_drift(silence_hours: float) -> float:
    if silence_hours < 2:    return 0.0
    elif silence_hours < 8:  return 0.1
    elif silence_hours < 24: return 0.2
    elif silence_hours < 48: return 0.35
    elif silence_hours < 72: return 0.5
    else:                    return 0.65

def build_temporal_context(
    last_user_msg_ts: str | None = None,
    now: datetime | None = None,
) -> TemporalContext:
    if now is None:
        now = datetime.now()
    hour        = now.hour
    time_period = get_time_period(hour)
    profile     = PERIOD_PROFILES[time_period]

    silence_hours = 0.0
    if last_user_msg_ts:
        try:
            last_ts       = datetime.fromisoformat(last_user_msg_ts)
            silence_hours = max(0.0, (now - last_ts).total_seconds() / 3600)
        except Exception:
            pass

    # 日本星期格式
    weekdays   = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    weekday_str = weekdays[now.weekday()]
    current_time_str = f"{now.strftime('%Y-%m-%d %H:%M')} ({weekday_str})"

    return TemporalContext(
        hour                 = hour,
        time_period          = time_period,
        analysis_capacity    = profile["analysis_capacity"],
        defense_level        = profile["defense_level"],
        emotional_leakage    = profile["emotional_leakage"],
        suppress_decay       = profile["suppress_decay"],
        emotional_multiplier = profile["emotional_multiplier"],
        attachment_drift     = compute_attachment_drift(silence_hours),
        silence_hours        = silence_hours,
        is_late_night        = time_period == "deep_night",
        is_transition_hour   = hour in TRANSITION_HOURS,
        current_time         = current_time_str,
    )

def render_temporal_block(ctx: TemporalContext) -> str:
    return (
        f"\n[TEMPORAL_CONTEXT]\n"
        f"current_time={ctx.current_time}\n"
        f"time_period={ctx.time_period}\n"
        f"analysis_capacity={ctx.analysis_capacity:.2f}\n"
        f"defense_level={ctx.defense_level:.2f}\n"
        f"emotional_leakage={ctx.emotional_leakage:.2f}\n"
        f"silence_hours={ctx.silence_hours:.1f}\n"
        f"[/TEMPORAL_CONTEXT]\n"
    )
