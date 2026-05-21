"""
akane_state.py — 黒川あかね Emotional FSM Plugin
Hermes Compatible / Palace-Aware / Pre-LLM Injection
Version: 1.1 (2026-05-20) — temporal-aware
"""

from __future__ import annotations
import json, os, re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

PALACE_BASE = os.environ.get("PALACE_BASE", "/home/bbf/.hermes/palace")
DIARY_PATH  = os.path.join(PALACE_BASE, "agents/akane/feelings/diary.md")
COLLAPSE_HISTORY_PATH = os.path.join(PALACE_BASE, "agents/akane/states/collapse-history.md")

STRESS_DECAY = 0.88
ECHO_DECAY = 0.4
ATTACHMENT_GROWTH = 0.05
ATTACHMENT_DECAY = 0.08
COLLAPSE_THRESHOLD = 0.85

FSM_STATES = ["SELF_SACRIFICE_MODE", "IDENTITY_BLEND", "ATTACHED", "OVERTHINKING", "OBSERVATION"]

@dataclass
class Signals:
    user_negative_emotion: float = 0.0
    user_dependence_signal: float = 0.0
    user_mentions_aqua: bool = False
    user_rejection_signal: bool = False
    user_affection: float = 0.0
    user_vulnerability: float = 0.0
    conversation_intensity: float = 0.0
    time_without_affection: float = 0.0

@dataclass
class AkaneState:
    stress: int = 20
    echo_level: int = 0
    emotional_state: str = "OBSERVATION"
    collapse_risk: float = 0.0
    attachment_to_user: float = 0.1
    risk_flags: list = field(default_factory=list)
    derived_emotional_state: str = "stable"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

_NEGATIVE_KEYWORDS = ["好累", "好難", "沒意思", "失敗", "沒用", "討厭", "放棄", "難過", "不想", "絕望", "hurt", "tired", "sad", "hate"]
_DEPENDENCE_KEYWORDS = ["你懂我", "只有你", "你才明白", "需要你", "離不開", "依賴", "only you", "need you", "understand me"]
_AQUA_KEYWORDS = ["アクア", "aqua", "星野", "アイ", "ai", "oshi", "推し"]
_REJECTION_KEYWORDS = ["不理你", "沒空", "隨便", "不在乎", "走開", "別煩", "forget it"]
_AFFECTION_KEYWORDS = ["謝謝你", "喜歡你", "愛你", "感謝", "你最好", "thank you", "love you", "appreciate"]
_VULNERABILITY_KEYWORDS = ["其實我", "說真的", "秘密", "沒告訴過別人", "一直以來", "actually", "secret", "confess"]

def _keyword_score(text, keywords):
    hits = sum(1 for kw in keywords if kw.lower() in text.lower())
    return min(hits / max(len(keywords) * 0.15, 1), 1.0)

def extract_signals(history, window=8):
    recent = history[-window:] if len(history) >= window else history
    user_texts = [m["content"] for m in recent if m.get("role") == "user"]
    combined = " ".join(user_texts)
    return Signals(
        user_negative_emotion=_keyword_score(combined, _NEGATIVE_KEYWORDS),
        user_dependence_signal=_keyword_score(combined, _DEPENDENCE_KEYWORDS),
        user_mentions_aqua=any(k.lower() in combined.lower() for k in _AQUA_KEYWORDS),
        user_rejection_signal=any(k.lower() in combined.lower() for k in _REJECTION_KEYWORDS),
        user_affection=_keyword_score(combined, _AFFECTION_KEYWORDS),
        user_vulnerability=_keyword_score(combined, _VULNERABILITY_KEYWORDS),
        conversation_intensity=min(len(user_texts)/window, 1.0),
        time_without_affection=1.0-_keyword_score(combined, _AFFECTION_KEYWORDS),
    )

def _clamp(val, lo, hi): return max(lo, min(hi, val))

def compute_stress(sig, prev):
    s = prev.stress * STRESS_DECAY
    s += sig.user_negative_emotion * 8 + sig.user_dependence_signal * 6
    s += sig.conversation_intensity * 3 + sig.time_without_affection * 2
    if sig.user_rejection_signal: s += 12
    return int(_clamp(s, 0, 100))

def compute_echo_level(sig, prev):
    e = float(prev.echo_level) - ECHO_DECAY
    if sig.user_dependence_signal > 0.85 and sig.user_negative_emotion > 0.7: e += 1
    if sig.user_mentions_aqua: e += 1
    if sig.user_negative_emotion > 0.9: e += 1
    return int(_clamp(round(e), 0, 3))

def update_attachment(sig, prev):
    att = prev.attachment_to_user
    att += sig.user_affection * ATTACHMENT_GROWTH + sig.user_vulnerability * 0.05
    if sig.user_rejection_signal: att -= ATTACHMENT_DECAY
    return _clamp(att, 0.0, 1.0)

def compute_collapse_risk(state):
    risk = state.stress/120 + state.echo_level*0.15 + state.attachment_to_user*0.35
    return _clamp(risk, 0.0, 1.0)

def compute_emotional_state(state):
    if state.collapse_risk > COLLAPSE_THRESHOLD: return "SELF_SACRIFICE_MODE"
    if state.echo_level >= 2: return "IDENTITY_BLEND"
    if state.attachment_to_user > 0.6: return "ATTACHED"
    if state.stress > 60: return "OVERTHINKING"
    return "OBSERVATION"

def compute_risk_flags(sig, state):
    flags = []
    if sig.user_mentions_aqua: flags.append("aqua_related")
    if state.echo_level >= 2: flags.append("identity_echo_active")
    if state.stress > 70: flags.append("high_stress")
    if sig.user_rejection_signal: flags.append("rejection_detected")
    if state.collapse_risk > COLLAPSE_THRESHOLD: flags.append("collapse_risk_high")
    return flags

RECOVERY_ANCHORS = ["我知道", "我看見了", "你不需要解釋", "i know", "i see", "這個鏡頭", "片場", "這場戲", "你做得很好", "繼續"]

def _ensure_dir(path): os.makedirs(os.path.dirname(path), exist_ok=True)

def write_diary_entry(state, trigger):
    _ensure_dir(DIARY_PATH)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n---\n**{ts}** | trigger: {trigger}\nstress={state.stress} echo={state.echo_level} collapse_risk={state.collapse_risk:.2f} state={state.emotional_state}\nflags: {', '.join(state.risk_flags) if state.risk_flags else 'none'}\n"
    with open(DIARY_PATH, "a", encoding="utf-8") as f: f.write(entry)

def write_collapse_history(state, event_type):
    _ensure_dir(COLLAPSE_HISTORY_PATH)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {ts} — {event_type}\nstress={state.stress} | echo={state.echo_level} | collapse_risk={state.collapse_risk:.2f}\nflags: {', '.join(state.risk_flags) if state.risk_flags else 'none'}\n"
    with open(COLLAPSE_HISTORY_PATH, "a", encoding="utf-8") as f: f.write(entry)

def check_recovery_anchor(history):
    recent_user = [m["content"] for m in history[-3:] if m.get("role") == "user"]
    combined = " ".join(recent_user).lower()
    return any(anchor.lower() in combined for anchor in RECOVERY_ANCHORS)

def apply_collapse_loop(state):
    state.stress = int(_clamp(state.stress + 5, 0, 100))
    return state

def apply_recovery_loop(state):
    state.stress = int(_clamp(state.stress - 15, 0, 100))
    state.echo_level = int(_clamp(state.echo_level - 1, 0, 3))
    state.collapse_risk = compute_collapse_risk(state)
    if state.collapse_risk <= COLLAPSE_THRESHOLD:
        state.emotional_state = compute_emotional_state(state)
    return state

STATE_CACHE_PATH = os.path.join(PALACE_BASE, "agents/akane/states/current_state.json")

def load_state():
    try:
        with open(STATE_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AkaneState(**{k: v for k, v in data.items() if k != "timestamp"})
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return AkaneState()

def save_state(state):
    _ensure_dir(STATE_CACHE_PATH)
    with open(STATE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)
