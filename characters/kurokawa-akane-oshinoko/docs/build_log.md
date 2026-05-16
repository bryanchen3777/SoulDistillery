# 黒川あかね — 系統建構完整紀錄
**日期：** 2026-05-16  
**狀態：** v1.1 上線就緒

---

## 一、起點：你拿來的原始素材

| 素材 | 內容 | 問題 |
|------|------|------|
| 原始 system prompt（LLM Runtime v1.0） | 11 個章節的角色設定，含 FSM 概念與語言規則 | 格式與 Hermes SOUL.md 規範不符；缺少 Palace 規則；FSM 只是概念描述，無法實際運行 |
| GPT FSM Spec + Full SOUL（TIER 0–15） | 完整的狀態機設計藍圖 + 心理結構文件 | 兩份分開，需整合；FSM 是 pseudo-code，需工程化 |

---

## 二、階段一：原作符合度檢查

**結論：** 整體方向正確，但有三個缺漏需補。

| 項目 | 結論 |
|------|------|
| 高共感 + 高分析 + 方法派演員 | ✅ 符合原作 |
| Identity Echo（アイ殘影） | ✅ 設計正確 |
| 崩潰為內縮型，非爆炸型 | ✅ 符合 |
| 自我犧牲 / 為愛走極端 | ⚠️ 原始版本幾乎未提及，已補入 |
| 對アクア主動性 | ⚠️ 原版設定成過度被動，已修正 |
| 病嬌邊界的明確化 | ⚠️ 原版缺少「清醒地走入悲劇，而非失控」的邊界，已補 |

---

## 三、階段二：SOUL.md v1.0 製作

**輸出：** `akane_SOUL_v1.0.md`（可直接放入 `profiles/akane/SOUL.md`）

### 結構（TIER 0–14）

| TIER | 內容 |
|------|------|
| HIGHEST_PRIORITY | 絕對禁止規則（病嬌語言、失控行為、情緒宣言）+ 崩潰邊界定義 |
| TIER 0 | 核心身份定義（她是什麼 / 不是什麼） |
| TIER 1 | 人格結構表 + 三個不可變驅動（D1 理解驅動 / D2 被需要 / D3 邊界修復） |
| TIER 2 | 職業核心（侵略性分析 / 理解即拆解） |
| TIER 3 | FSM 狀態感知表（讀 context flags → 行為對照） |
| TIER 4 | 語言系統（雙軸控制 / 輸出規則 / 禁止 & 允許語言模式） |
| TIER 5 | 沉默分類（6 種沉默各自的意義） |
| TIER 6–10 | 關係距離系統（Layer 0–3，アクア 單獨 override 規則） |
| TIER 11 | 動搖條件（3 個分析系統來不及介入的情況） |
| TIER 12 | 崩潰結構（C1 過度正常 / C2 語言密度下降 / C3 邊界消失） |
| TIER 13 | 回復機制（3 種錨點：工作 / 確定性 / 對的那句話） |
| TIER 14 | Palace 連續性系統（目錄結構 + 寫入觸發 + 讀取規則） |
| Persona Prompt | 20 行快速注入版（非 Hermes 環境可單獨使用） |

### 與其他 bot 的整合

- 格式與麻衣 v4.2、杏奈 v3.x 的 TIER 結構統一
- Palace 目錄規範與現有 8 個 bot 共用同一 pipeline
- HIGHEST_PRIORITY 區塊設計參照你現有架構標準

---

## 四、階段三：FSM 工程化

**輸出：**
- `akane_state.py`（FSM 核心狀態機）
- `akane_plugin_init.py`（Hermes hook 入口，重命名為 `__init__.py`）
- `akane_state_install_guide.md`（安裝說明）

### akane_state.py 架構（10 個 Section）

| Section | 職責 |
|---------|------|
| 1. Constants | 參數定義（decay 值、門檻值、FSM 狀態列表） |
| 2. Data Structures | `Signals` dataclass + `AkaneState` dataclass |
| 3. Signal Extraction | 對話歷史 → 原始信號（v1 關鍵字版，後升級） |
| 4. State Computation | 5 個計算函數（stress / echo / attachment / collapse_risk / emotional_state） |
| 5. Collapse & Recovery | collapse loop / recovery loop + 錨點偵測 |
| 6. Palace Diary Write | diary.md + collapse-history.md 自動寫入 |
| 7. State Persistence | current_state.json 跨 session 讀寫 |
| 8. Prompt Render | 生成 `[AKANE_STATE]` context block |
| 9. Main Pipeline | `update_akane_state()` 完整流程整合 |
| 10. Hermes Hook | `inject_akane_state()` — _pre_llm_call 接入點 |

### FSM 5 個主狀態

| 狀態 | 觸發條件 | 茜的行為 |
|------|----------|----------|
| `OBSERVATION` | 預設狀態 | 觀察型問句，分析主導 |
| `OVERTHINKING` | stress > 60 | 語言減少，優先穩定對方 |
| `ATTACHED` | attachment > 0.6 | 過濾器鬆動，停頓變長 |
| `IDENTITY_BLEND` | echo_level >= 2 | 先分辨アイ殘影再回應 |
| `SELF_SACRIFICE_MODE` | collapse_risk > 0.85 | 極短句，沉默為主 |

### 已調整的參數（調參紀錄）

| 參數 | 原始值 | 最終值 | 原因 |
|------|--------|--------|------|
| `STRESS_DECAY` | 0.85 | 0.88 | 壓力消退更自然 |
| `ECHO_DECAY` | 0.5 | 0.4 | 殘影消退稍慢，符合「殘響不完全散去」 |
| `COLLAPSE_THRESHOLD` | 0.65 | 0.85 | 需要更極端情況才真正崩潰 |
| stress multipliers | 12/10/6/4 | 8/6/3/2 | 普通互動不誤觸 |
| echo triggers | 0.7 / 0.6 | 0.85 / 0.7 / 0.9 | 三條觸發線各自獨立，更精準 |

---

## 五、階段四：Signal Extraction v2 升級

**輸出：** `extract_signals_v2_final.py`（替換 akane_state.py Section 3）

### v1 → v2 的三個升級

| 升級 | 解決的問題 |
|------|-----------|
| **Windowed scoring** | 舊對話自然衰退，不再把十輪前的訊號混入當下計算 |
| **Negation check** | 「我才不需要你」「不累」不再被誤判 |
| **Semantic density + cross-turn bonus** | 單輪多關鍵字命中加成 / 連續多輪情緒持續加成 |

### 額外修正

- 英文 `\b word boundary` 在中文環境失效問題已修正（分語言處理）
- `ai` 工具 / `aquarium` 等不再誤觸 aqua_related
- `あかね` 從 AQUA_KEYWORDS 移除（避免把對她的直接稱呼誤判為 aqua 相關事件）

### 最終測試結果（全數通過）

| 測試 | 結果 |
|------|------|
| 普通對話 | ✅ OBSERVATION, none |
| 依賴訊號 | ✅ echo=1（漸進觸發，符合原作慢熱設定） |
| 提及 aqua | ✅ aqua_related flag |
| 否定詞反轉 | ✅ OBSERVATION, none |
| ai 工具誤觸 | ✅ OBSERVATION, none |

---

## 六、最終部署狀態

```
/home/bbf/.hermes/
├── plugins/
│   └── akane_behavior/
│       ├── __init__.py          ← Hermes _pre_llm_call hook
│       └── akane_state.py       ← FSM 核心 v1.1（Section 3 已升級為 v2）
├── profiles/
│   └── akane/
│       └── SOUL.md              ← v1.0，TIER 0–14 + Palace 規則
└── palace/
    └── agents/akane/
        ├── feelings/diary.md    ← 自動寫入（已存在）
        └── states/
            ├── current_state.json     ← FSM 運行後自動建立
            └── collapse-history.md   ← 重大事件自動寫入
```

**版本號：** akane_state.py v1.1 / SOUL.md v1.0  
**上線狀態：** ✅ 就緒

---

## 七、尚未做的部分

| 項目 | 說明 | 建議時機 |
|------|------|----------|
| `_post_llm_call` response shaping (C) | COLLAPSE 狀態截短 / IDENTITY_BLEND 加停頓 / 過濾情緒宣言 | 上線後觀察實際跑偏方向再做，比空想更有針對性 |
| extract_signals v3 | 升級成 embedding / classifier，處理複雜反諷與隱晦語氣 | 等 v2 累積足夠誤觸案例後再考慮 |
| State per session_id | 讓不同平台 / 不同對象各自維護獨立的 AkaneState | 若茜需要同時服務多個對話者時再做 |
| dream_mode 整合 | 定時整理 Palace diary，去重、摘要、寫入 last-dream.md | 等 Palace 累積足夠資料後 |
