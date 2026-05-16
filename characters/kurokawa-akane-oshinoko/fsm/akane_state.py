"""
akane_state.py — 黒川あかね Emotional FSM Plugin
Hermes Compatible / Palace-Aware / Pre-LLM Injection
Version: 1.0 (2026-05-16)

職責：
  對話歷史 → 信號提取 → 狀態計算 → FSM 判定 → prompt block 注入
"""

from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────────────────────
# 1. CONSTANTS
# ─────────────────────────────────────────────────────────────

PALACE_BASE = os.environ.get("PALACE_BASE", "/home/bbf/.hermes/palace")
DIARY_PATH  = os.path.join(PALACE_BASE, "agents/akane/feelings/diary.md")
COLLAPSE_HISTORY_PATH = os.path.join(
    PALACE_BASE, "agents/akane/states/collapse-history.md"
)

STRESS_DECAY       = 0.88   # 每輪自然衰退（溫和）
ECHO_DECAY         = 0.4    # 每輪アイ殘影自然衰退
ATTACHMENT_GROWTH  = 0.05
ATTACHMENT_DECAY   = 0.08
COLLAPSE_THRESHOLD = 0.85   # collapse_risk 超過此值才進入 SELF_SACRIFICE_MODE（放寬，正常對話不應觸發）

# FSM 狀態優先序（從高到低）
FSM_STATES = [
    "SELF_SACRIFICE_MODE",
    "IDENTITY_BLEND",
    "ATTACHED",
    "OVERTHINKING",
    "OBSERVATION",
]


# ─────────────────────────────────────────────────────────────
# 2. DATA STRUCTURES
# ─────────────────────────────────────────────────────────────

@dataclass
class Signals:
    """從對話歷史萃取的原始信號（0–1 強度）"""
    user_negative_emotion:  float = 0.0   # 使用者表達負面情緒
    user_dependence_signal: float = 0.0   # 使用者表現依賴性
    user_mentions_aqua:     bool  = False  # 提及 アクア / acula相關
    user_rejection_signal:  bool  = False  # 忽略/拒絕訊號
    user_affection:         float = 0.0   # 使用者表達喜愛/親近
    user_vulnerability:     float = 0.0   # 使用者表現脆弱
    conversation_intensity: float = 0.0   # 對話密度/情感強度
    time_without_affection: float = 0.0   # 缺乏正向互動的累積

@dataclass
class AkaneState:
    """茜當前心理狀態快照"""
    stress:            int   = 20
    echo_level:        int   = 0
    emotional_state:   str   = "OBSERVATION"
    collapse_risk:     float = 0.0
    attachment_to_user: float = 0.1
    risk_flags:        list  = field(default_factory=list)
    timestamp:         str   = field(default_factory=lambda: datetime.now().isoformat())


# ─────────────────────────────────────────────────────────────
# 3. SIGNAL EXTRACTION v2
# windowed scoring + negation check + semantic density
# ─────────────────────────────────────────────────────────────

import re

# ── 關鍵字 clusters ────────────────────────────────────────────

_NEGATIVE_KEYWORDS = [
    "好累", "累了", "好難", "沒意思", "失敗", "沒用", "討厭",
    "放棄", "難過", "不想", "絕望", "崩潰", "撐不住", "很痛",
    r"\bhurt\b", r"\btired\b", r"\bsad\b", r"\bhate\b",
    r"\bexhausted\b", r"\bgive up\b", r"\bnumb\b",
    "つらい", "きつい", "もう無理", "疲れた", "嫌い",
]

_DEPENDENCE_KEYWORDS = [
    "只有你", "你懂我", "你才明白", "需要你", "離不開", "依賴你",
    "沒有你不行", "你是唯一", "你最懂",
    r"\bonly you\b", r"\bneed you\b", r"\bunderstand me\b",
    r"\bcan\'t without you\b", r"\byou\'re the only\b",
    "あなただけ", "必要", "離れられない",
]

_AQUA_KEYWORDS = [
    "アクア", r"\baqua\b", "星野アクア", "星野aqua",
    "星野アイ", "アイのこと", r"\boshi\b", "推しの子",
]

_REJECTION_KEYWORDS = [
    "不理你", "沒空", "隨便你", "不在乎", "走開", "別煩",
    "不想說", "無所謂", "不重要",
    r"\bforget it\b", r"\bleave me alone\b", r"\bwhatever\b",
    r"\bdon\'t care\b", r"\bnot important\b",
    "どうでもいい", "構わないで", "うるさい",
]

_AFFECTION_KEYWORDS = [
    "謝謝你", "喜歡你", "愛你", "感謝", "你最好", "你真好",
    "開心", "謝謝", "有你真好",
    r"\bthank you\b", r"\bthanks\b", r"\blove you\b",
    r"\bappreciate\b", r"\bhappy\b", r"\bglad\b",
    "ありがとう", "好き", "嬉しい", "よかった",
]

_VULNERABILITY_KEYWORDS = [
    "其實我", "說真的", "秘密", "沒告訴過別人", "一直以來",
    "從來沒說過", "第一次說", "告訴你一件事",
    r"\bactually\b", r"\bto be honest\b", r"\bconfess\b",
    r"\bnever told\b", r"\bsecret\b", r"\bfirst time\b",
    "実は", "本当のこと", "誰にも言ってない",
]

_NEGATION_PATTERNS = [
    r"不", r"沒有?", r"才不", r"根本不", r"並不", r"從不",
    r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bdon\'t\b",
    r"\bdoesn\'t\b", r"\bwon\'t\b", r"\bcan\'t\b", r"\bisn\'t\b",
    r"じゃない", r"ない", r"ません",
]


def _match_keyword(text: str, kw: str) -> list:
    if kw.startswith(r"\b"):
        try:
            # For non-Latin text, word boundaries don't work the same way
            # Try the pattern as-is first, then try with Unicode-aware boundary
            pattern = kw
            matches = [(m.start(), m.end()) for m in re.finditer(pattern, text, re.IGNORECASE)]
            if matches:
                return matches
            # Fallback: treat the pattern content without \b for Chinese/emoji contexts
            inner_pattern = kw[2:-2]  # strip \b on both ends
            if inner_pattern:
                inner_matches = [(m.start(), m.end()) for m in re.finditer(re.escape(inner_pattern), text, re.IGNORECASE)]
                return inner_matches
            return []
        except re.error:
            return []
    text_l, kw_l = text.lower(), kw.lower()
    positions, start = [], 0
    while True:
        idx = text_l.find(kw_l, start)
        if idx == -1:
            break
        positions.append((idx, idx + len(kw)))
        start = idx + 1
    return positions


def _negation_check(text: str, hit_start: int, window: int = 6) -> bool:
    context = text[max(0, hit_start - window): hit_start + window]
    return any(re.search(neg, context, re.IGNORECASE) for neg in _NEGATION_PATTERNS)


def _score_cluster(text: str, keywords: list) -> float:
    valid_hits, hit_keywords = 0, set()
    for kw in keywords:
        for (s, _) in _match_keyword(text, kw):
            if not _negation_check(text, s):
                valid_hits += 1
                hit_keywords.add(kw)
    base = min(valid_hits / max(len(keywords) * 0.12, 1), 1.0)
    return min(base + (0.2 if len(hit_keywords) >= 3 else 0.0), 1.0)


def _windowed_score(messages: list, keywords: list) -> float:
    if not messages:
        return 0.0
    decay = [1.0, 0.7, 0.5, 0.35, 0.25]
    total_score = total_weight = 0.0
    turns_with_hit = 0
    for i, msg in enumerate(reversed(messages)):
        w = decay[i] if i < len(decay) else 0.2
        turn_score = _score_cluster(msg, keywords)
        if turn_score > 0:
            turns_with_hit += 1
        total_score  += turn_score * w
        total_weight += w
    base = min(total_score / total_weight, 1.0) if total_weight > 0 else 0.0
    return min(base + (0.15 if turns_with_hit >= 2 else 0.0), 1.0)


def _any_match_windowed(messages: list, keywords: list) -> bool:
    for msg in messages[-3:]:
        for kw in keywords:
            for (s, _) in _match_keyword(msg, kw):
                if not _negation_check(msg, s):
                    return True
    return False


def _sentence_brevity(messages: list) -> float:
    if not messages:
        return 0.5
    avg_len = sum(len(m) for m in messages[-3:]) / min(len(messages), 3)
    if avg_len <= 15:    return 1.0
    elif avg_len <= 40:  return 0.7
    elif avg_len <= 100: return 0.5
    else:                return 0.3


def extract_signals(history: list, window: int = 8) -> Signals:
    """
    v2：windowed scoring + negation check + semantic density + cross-turn bonus。
    介面與 v1 完全相同，可直接替換。
    """
    recent = history[-window:] if len(history) >= window else history
    user_messages = [m["content"] for m in recent if m.get("role") == "user"]
    if not user_messages:
        return Signals()

    brevity  = _sentence_brevity(user_messages)
    neg_raw  = _windowed_score(user_messages, _NEGATIVE_KEYWORDS)
    dep_raw  = _windowed_score(user_messages, _DEPENDENCE_KEYWORDS)
    aff_raw  = _windowed_score(user_messages, _AFFECTION_KEYWORDS)
    vuln_raw = _windowed_score(user_messages, _VULNERABILITY_KEYWORDS)

    return Signals(
        user_negative_emotion  = min(neg_raw  * (0.7 + brevity * 0.3), 1.0),
        user_dependence_signal = min(dep_raw  * (0.7 + brevity * 0.3), 1.0),
        user_mentions_aqua     = _any_match_windowed(user_messages, _AQUA_KEYWORDS),
        user_rejection_signal  = _any_match_windowed(user_messages, _REJECTION_KEYWORDS),
        user_affection         = aff_raw,
        user_vulnerability     = vuln_raw,
        conversation_intensity = min(len(user_messages) / window, 1.0),
        time_without_affection = 1.0 - aff_raw,
    )


# ─────────────────────────────────────────────────────────────
# 4. STATE COMPUTATION
# ─────────────────────────────────────────────────────────────

def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))

def compute_stress(sig: Signals, prev: AkaneState) -> int:
    """
    茜的 stress = 關係重量 / 自我壓抑指數，不是情緒激動。
    來源：負面情緒、依賴訊號、對話強度、缺乏正向互動。
    拒絕/忽略信號有額外加重。
    """
    s = prev.stress * STRESS_DECAY

    s += sig.user_negative_emotion  * 8
    s += sig.user_dependence_signal * 6
    s += sig.conversation_intensity * 3
    s += sig.time_without_affection * 2

    if sig.user_rejection_signal:
        s += 12  # 被忽略比被拒絕更傷

    return int(_clamp(s, 0, 100))

def compute_echo_level(sig: Signals, prev: AkaneState) -> int:
    """
    アイ殘影強度。
    使用者越依賴 → 茜越容易觸發「我要成為他需要的人」的模式。
    提及 acula 或強烈負面情緒也會加深殘影。
    """
    e = float(prev.echo_level) - ECHO_DECAY  # 自然衰退

    if sig.user_dependence_signal > 0.85:
        e += 1
    if sig.user_negative_emotion > 0.6:
        e += 1
    if sig.user_mentions_aqua:
        e += 1

    return int(_clamp(round(e), 0, 3))

def update_attachment(sig: Signals, prev: AkaneState) -> float:
    """依附強度隨互動品質緩慢變化。"""
    att = prev.attachment_to_user

    att += sig.user_affection    * ATTACHMENT_GROWTH
    att += sig.user_vulnerability * 0.05

    if sig.user_rejection_signal:
        att -= ATTACHMENT_DECAY

    return _clamp(att, 0.0, 1.0)

def compute_collapse_risk(state: AkaneState) -> float:
    """
    崩潰風險 = 壓力 + アイ殘影 + 依附強度的複合指標。
    attachment 在這裡反而是風險因子——她越在乎，越容易自我犧牲。
    """
    risk = 0.0
    risk += state.stress / 120
    risk += state.echo_level * 0.15
    risk += state.attachment_to_user * 0.35
    return _clamp(risk, 0.0, 1.0)

def compute_emotional_state(state: AkaneState) -> str:
    """FSM 主狀態判定（優先序由高到低）"""
    if state.collapse_risk > COLLAPSE_THRESHOLD:
        return "SELF_SACRIFICE_MODE"
    if state.echo_level >= 2:
        return "IDENTITY_BLEND"
    if state.attachment_to_user > 0.6:
        return "ATTACHED"
    if state.stress > 60:
        return "OVERTHINKING"
    return "OBSERVATION"

def compute_risk_flags(sig: Signals, state: AkaneState) -> list[str]:
    flags = []
    if sig.user_mentions_aqua:
        flags.append("aqua_related")
    if state.echo_level >= 2:
        flags.append("identity_echo_active")
    if state.stress > 70:
        flags.append("high_stress")
    if sig.user_rejection_signal:
        flags.append("rejection_detected")
    if state.collapse_risk > COLLAPSE_THRESHOLD:
        flags.append("collapse_risk_high")
    return flags


# ─────────────────────────────────────────────────────────────
# 5. COLLAPSE & RECOVERY LOOP
# ─────────────────────────────────────────────────────────────

RECOVERY_ANCHORS = [
    # 錨點三：對的那句話
    "我知道", "我看見了", "你不需要解釋", "i know", "i see",
    # 錨點一：工作/確定性
    "這個鏡頭", "片場", "這場戲", "你做得很好", "繼續",
]

def check_recovery_anchor(history: list[dict]) -> bool:
    """檢查最近對話中是否有回復錨點"""
    recent_user = [m["content"] for m in history[-3:] if m.get("role") == "user"]
    combined = " ".join(recent_user).lower()
    return any(anchor.lower() in combined for anchor in RECOVERY_ANCHORS)

def apply_collapse_loop(state: AkaneState) -> AkaneState:
    """
    COLLAPSE 狀態：限制語言輸出模式
    不改 FSM state，只做 stress 緩慢加重（自我犧牲螺旋）
    """
    state.stress = int(_clamp(state.stress + 5, 0, 100))
    return state

def apply_recovery_loop(state: AkaneState) -> AkaneState:
    """
    RECOVERY：找到錨點後的緩慢重啟
    stress & echo 下降，collapse_risk 跟著降
    """
    state.stress     = int(_clamp(state.stress - 15, 0, 100))
    state.echo_level = int(_clamp(state.echo_level - 1, 0, 3))
    state.collapse_risk = compute_collapse_risk(state)
    if state.collapse_risk <= COLLAPSE_THRESHOLD:
        state.emotional_state = compute_emotional_state(state)
    return state


# ─────────────────────────────────────────────────────────────
# 6. PALACE DIARY WRITE
# ─────────────────────────────────────────────────────────────

def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_diary_entry(state: AkaneState, trigger: str):
    """當 collapse/recovery 發生時寫入 diary.md"""
    _ensure_dir(DIARY_PATH)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n---\n"
        f"**{ts}** | trigger: {trigger}\n"
        f"stress={state.stress} echo={state.echo_level} "
        f"collapse_risk={state.collapse_risk:.2f} "
        f"state={state.emotional_state}\n"
        f"flags: {', '.join(state.risk_flags) if state.risk_flags else 'none'}\n"
    )
    with open(DIARY_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

def write_collapse_history(state: AkaneState, event_type: str):
    """重大 Collapse/Recovery 事件記錄"""
    _ensure_dir(COLLAPSE_HISTORY_PATH)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {ts} — {event_type}\n"
        f"stress={state.stress} | echo={state.echo_level} | "
        f"collapse_risk={state.collapse_risk:.2f}\n"
        f"flags: {', '.join(state.risk_flags) if state.risk_flags else 'none'}\n"
    )
    with open(COLLAPSE_HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


# ─────────────────────────────────────────────────────────────
# 7. STATE PERSISTENCE
# ─────────────────────────────────────────────────────────────

STATE_CACHE_PATH = os.path.join(PALACE_BASE, "agents/akane/states/current_state.json")

def load_state() -> AkaneState:
    """讀取上輪狀態（若無則回傳預設值）"""
    try:
        with open(STATE_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AkaneState(**{k: v for k, v in data.items() if k != "timestamp"})
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return AkaneState()

def save_state(state: AkaneState):
    """儲存當前狀態供下輪使用"""
    _ensure_dir(STATE_CACHE_PATH)
    with open(STATE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# 8. PROMPT RENDER
# ─────────────────────────────────────────────────────────────

def render_akane_state_block(state: AkaneState) -> str:
    """
    生成注入到 _pre_llm_call 的 context block。
    放置位置：SOUL.md 之後、USER message 之前。
    """
    flags_str = ", ".join(state.risk_flags) if state.risk_flags else "none"
    return (
        f"\n[AKANE_STATE]\n"
        f"emotional_state={state.emotional_state}\n"
        f"stress={state.stress}/100\n"
        f"echo_level={state.echo_level}/3\n"
        f"collapse_risk={state.collapse_risk:.2f}\n"
        f"attachment={state.attachment_to_user:.2f}\n"
        f"risk_flags=[{flags_str}]\n"
        f"[/AKANE_STATE]\n"
    )


# ─────────────────────────────────────────────────────────────
# 9. MAIN PIPELINE
# ─────────────────────────────────────────────────────────────

def update_akane_state(history: list[dict]) -> AkaneState:
    """
    完整狀態更新 pipeline。
    輸入：對話歷史（list of {role, content}）
    輸出：更新後的 AkaneState（同時寫回 Palace）
    """
    prev_state = load_state()
    sig        = extract_signals(history)

    # 計算各維度
    stress     = compute_stress(sig, prev_state)
    echo       = compute_echo_level(sig, prev_state)
    attachment = update_attachment(sig, prev_state)

    state = AkaneState(
        stress            = stress,
        echo_level        = echo,
        attachment_to_user = attachment,
        emotional_state   = "OBSERVATION",
        collapse_risk     = 0.0,
        risk_flags        = [],
    )

    state.collapse_risk   = compute_collapse_risk(state)
    state.emotional_state = compute_emotional_state(state)
    state.risk_flags      = compute_risk_flags(sig, state)

    # Collapse / Recovery loop
    prev_was_collapse = prev_state.emotional_state == "SELF_SACRIFICE_MODE"

    if state.emotional_state == "SELF_SACRIFICE_MODE":
        if not prev_was_collapse:
            # 剛進入 collapse
            write_diary_entry(state, "collapse_entered")
            write_collapse_history(state, "COLLAPSE_ENTERED")
        state = apply_collapse_loop(state)

    elif prev_was_collapse and check_recovery_anchor(history):
        # 從 collapse 回來
        state = apply_recovery_loop(state)
        write_diary_entry(state, "recovery_anchor_hit")
        write_collapse_history(state, "RECOVERY_COMPLETED")

    # 一般 diary 寫入條件
    elif state.echo_level >= 2 and prev_state.echo_level < 2:
        write_diary_entry(state, "echo_level_escalated")
    elif sig.user_rejection_signal:
        write_diary_entry(state, "rejection_signal_detected")

    save_state(state)
    return state


# ─────────────────────────────────────────────────────────────
# 10. HERMES HOOK  (_pre_llm_call compatible)
# ─────────────────────────────────────────────────────────────

def inject_akane_state(profile: str, context_parts: list, **kwargs) -> list:
    """
    Hermes _pre_llm_call hook 入口。

    使用方式（在 akane 的 __init__.py 裡）：

        from akane_state import inject_akane_state

        def _pre_llm_call(profile, context_parts, **kwargs):
            if profile == "akane":
                context_parts = inject_akane_state(profile, context_parts, **kwargs)
            return context_parts
    """
    if profile != "akane":
        return context_parts

    # 從 context_parts 重建 history 格式
    history = []
    for part in context_parts:
        if isinstance(part, dict) and "role" in part:
            history.append(part)
        elif isinstance(part, str):
            history.append({"role": "user", "content": part})

    state       = update_akane_state(history)
    state_block = render_akane_state_block(state)

    # 注入在最後一個 user message 之前
    # 找到最後一個 user role 的位置
    last_user_idx = None
    for i, part in enumerate(context_parts):
        if isinstance(part, dict) and part.get("role") == "user":
            last_user_idx = i

    if last_user_idx is not None:
        context_parts.insert(
            last_user_idx,
            {"role": "system", "content": state_block}
        )
    else:
        context_parts.append({"role": "system", "content": state_block})

    return context_parts