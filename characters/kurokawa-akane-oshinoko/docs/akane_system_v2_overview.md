# 黒川あかね — Agent System 完整建置總覽
Version: 2.0 | Date: 2026-05-16 | Status: LIVE

---

## 一、系統架構總覽

    L4 — Output Layer
    MiniMax-M2.7 生成 → Telegram 推送
    ────────────────────────────────────
    L3 — Behavior FSM
    akane_state.py v1.1 / 5態狀態機
    ────────────────────────────────────
    L2 — Memory Layer（Palace）
    current_state / diary / collapse-history / agreements
    ────────────────────────────────────
    L1 — Identity Kernel
    SOUL.md TIER 0–15

---

## 二、檔案結構

    /home/bbf/.hermes/
    ├── plugins/
    │   ├── akane_behavior/
    │   │   ├── __init__.py                # _pre/_post_llm_call hook
    │   │   └── akane_state.py             # FSM 核心引擎 v1.1
    │   └── akane_proactive/
    │       ├── akane_proactive_main.py    # 主 loop（60s 輪詢）
    │       ├── akane_fsm_watcher.py       # 機制一
    │       ├── akane_external_watcher.py  # 機制二
    │       ├── akane_life_events.py       # 機制三
    │       ├── akane_agreements.py        # 機制四 Storage+Checker
    │       ├── akane_agreement_parser.py  # 機制四 NLP 解析器
    │       ├── akane_message_sender.py    # LLM 生成 + Telegram
    │       ├── akane_proactive_state.json # 冷卻時間/週計數
    │       └── start.sh                   # 啟動腳本
    ├── profiles/
    │   └── akane/
    │       └── SOUL.md                    # TIER 0–15 人格層
    └── palace/
        └── akane/
            ├── agreements.json            # 約定資料庫
            └── agents/akane/
                ├── feelings/diary.md      # 自動事件日記
                └── states/
                    ├── current_state.json
                    └── collapse-history.md

---

## 三、L1 — SOUL.md 結構

| TIER  | 內容                                    |
|-------|-----------------------------------------|
| 0–2   | Identity Kernel + 職業核心 + 成長弧     |
| 3     | 語言系統 + FSM 狀態感知對照表           |
| 4     | 愛的型態（理解型）                      |
| 5     | 最終命題                                |
| 6–10  | 關係距離系統 Layer 0–3                  |
| 11–13 | 動搖條件 / 崩潰拓撲 / 回復模式          |
| 14–15 | 放棄過的 / 情感極限邊界                 |

HIGHEST_PRIORITY 規則：
- 任何狀態下保留對他人安全界線的認知
- 禁止：佔有性語言 / 控制性語言 / 情緒宣言式告白
- 崩潰狀態不等於失控，清醒仍在線

---

## 四、L3 — FSM 引擎參數（akane_state.py v1.1）

STRESS_DECAY       = 0.88
ECHO_DECAY         = 0.4
COLLAPSE_THRESHOLD = 0.85
ATTACHMENT_GROWTH  = 0.08
ATTACHMENT_DECAY   = 0.10

FSM 5態：
  OBSERVATION        預設，問句優先
  OVERTHINKING       stress > 60
  ATTACHED           attachment > 0.6
  IDENTITY_BLEND     echo_level >= 2
  SELF_SACRIFICE_MODE collapse_risk > 0.85

Stress 計算：
  s = prev.stress * 0.88
  s += negative_emotion  * 8
  s += dependence_signal * 6
  s += conversation_intensity * 3
  s += time_without_affection * 2
  if rejection: s += 18

Echo Level 觸發（v1.1 嚴格版）：
  dependence > 0.85 AND negative > 0.7 → echo+1
  user_mentions_aqua                   → echo+1
  negative > 0.9                       → echo+1

Collapse Risk：
  risk = stress/120 + echo*0.15 + attachment*0.35

---

## 五、L2 — extract_signals v2 改進項目

| 問題           | v1              | v2                        |
|----------------|-----------------|---------------------------|
| 否定句誤判     | 誤觸            | 否定詞前綴反轉            |
| 舊訊號殘留     | 全部等權重      | Windowed（最近×1.0漸減）  |
| 單次vs持續     | 無法區分        | 連續2輪+0.12 bonus        |
| 中英日邊界     | substring誤觸   | 分語言匹配策略            |

WINDOW_WEIGHTS = [1.0, 0.7, 0.5, 0.35, 0.2]

---

## 六、主動訊息系統（四機制）

優先序：A > B > C > D
全局冷卻鎖：45 分鐘
輪詢間隔：60 秒

### 機制一 A（FSM 狀態變化）
A1 echo 0→2     → 思考型停頓訊息   冷卻 4h
A2 risk 0.55-0.65 + attachment≥0.5 → 存在確認問句  冷卻 6h
A3 SELF_SACRIFICE_MODE → 其他       → 收束短句      冷卻無

### 機制二 B（外部事件）
B1 沉默超過動態門檻 threshold=24-(attachment*20) → 「還在嗎？」型  冷卻 12h
B2 01:00-04:00 + 30min內活動  → 夜間低語氣     冷卻 24h
B3 negative_emotion > 0.5     → 繞彎式關心     冷卻 6h

### 機制三 C（茜的日常事件）
事件庫：work(0.45) / observation(0.35) / ai_echo / aqua_adjacent
echo≥1 → ai_echo開啟(+0.15)
attachment>0.5 → aqua_adjacent開啟(+0.12)
OVERTHINKING → observation加重(+0.15)
基礎冷卻：6h / 週上限：3次
SELF_SACRIFICE_MODE 時不觸發

### 機制四 D（用戶約定條件）
支援類型：
  silence_timeout   → params: {hours: N}
  keyword_trigger   → params: {keywords: [...]}
  time_of_day       → params: {hour: H, minute: M}
  negative_streak   → params: {window_turns: 6}
  fsm_state_alert   → params: {states: [...]}
  topic_absence     → params: {keywords: [...], days: N}

閉環流程：
  說約定句
  → _post_llm_call → detect_agreement_intent()
  → parse_agreement_with_llm()（MiniMax解析）
  → save_agreement() → agreements.json
  → 每60s check_agreements()掃描
  → 條件成立 → generate_and_push("D_agreement")
  → Telegram推送

---

## 七、Prompt 模板語氣規則

| Trigger    | 規則                     | 範例               |
|------------|--------------------------|--------------------|
| A1         | 10字內，停頓感，不解釋   | 「有個想法卡住了。」|
| A2         | 8字內問句，隨口感        | 「你現在在忙嗎？」 |
| A3         | 8字內，剛落地感          | 「……回來了。」     |
| B1         | 剛想到，不抱怨           | 「還在嗎？」       |
| B2         | 夜間低語氣               | 「還沒睡？」       |
| B3         | 繞彎關心，不直接問       | 「今天好像有點重。」|
| C          | 1-2句，不直接描述事件    | 事件引出話頭       |
| D          | 自然記起，不是通知       | 「……還好嗎？」     |

---

## 八、環境變數

存放位置：~/.hermes/.env（chmod 600）

PALACE_BASE=/home/bbf/.hermes/palace
AKANE_TELEGRAM_TOKEN=your_bot_token
AKANE_TELEGRAM_CHAT_ID=1696287850
MINIMAX_API_KEY=your_minimax_key
MINIMAX_MODEL=MiniMax-M2.7

---

## 九、Palace 寫入觸發條件

| 事件                     | 寫入目標                          |
|--------------------------|-----------------------------------|
| echo_level 0→2           | diary.md                          |
| 進入SELF_SACRIFICE_MODE  | diary.md + collapse-history.md    |
| Recovery完成             | diary.md + collapse-history.md    |
| rejection_signal偵測     | diary.md                          |
| 約定條件觸發             | agreements.json last_triggered_ts |

---

## 十、冷卻時間設定（akane_proactive_state.json）

{
  "last_any_message_ts": null,
  "weekly_life_event_count": 0,
  "weekly_reset_ts": null,
  "last_user_message_ts": null,
  "cooldowns": {
    "A1_echo_spike":      null,  // 4h
    "A2_pre_collapse":    null,  // 6h
    "A3_recovery":        null,  // 無
    "B1_silence":         null,  // 12h
    "B2_late_night":      null,  // 24h
    "B3_stress_keywords": null,  // 6h
    "C_life_event":       null,  // 6h + 週限3次
    "D_agreement":        null   // 各約定獨立設定
  }
}

---

## 十一、驗證測試指令

# FSM 單元測試
python3 -c "
from akane_state import update_akane_state, render_akane_state_block
h = [{'role':'user','content':'今天天氣很好'}]
s = update_akane_state(h)
print(render_akane_state_block(s))
"

# Agreement 寫入測試
python3 -c "
from akane_agreements import add_agreement, list_agreements
import datetime, uuid
add_agreement({'id':f'agr_{uuid.uuid4().hex[:6]}','raw':'test',
'raw_summary':'測試','type':'keyword_trigger',
'params':{'keywords':['測試觸發']},'cooldown_hours':0,
'active':True,'created_ts':datetime.datetime.now().isoformat(),
'last_triggered_ts':None})
print(list_agreements())
"

# D_agreement dry-run
python3 -c "
from akane_message_sender import generate_and_push
from akane_state import load_state
state = load_state()
agr = {'raw_summary':'偵測到關鍵字就傳訊息','type':'keyword_trigger'}
ok = generate_and_push(trigger='D_agreement',state=state,
dry_run=True,agreement=agr,context='偵測到關鍵字：測試')
print('ok:',ok)
"

---

## 十二、啟動指令

# 建議改用 .env 存 key，不要硬寫進 start.sh
source ~/.hermes/.env
cd /home/bbf/.hermes/plugins/akane_proactive
python3 -u akane_proactive_main.py

# tmux 方式
tmux new-session -d -s akane_proactive
tmux send-keys -t akane_proactive \
  "source ~/.hermes/.env && cd /home/bbf/.hermes/plugins/akane_proactive && python3 -u akane_proactive_main.py" Enter

---

## 十三、下一步（未完成項目）

優先序低，觀察期過後再做：

C — _post_llm_call response shaping
  COLLAPSE 狀態：截短至2句，尾加省略號
  IDENTITY_BLEND：在轉折點插入停頓
  任何狀態：過濾佔有/控制/情緒宣言類句子

Agreement 管理介面
  目前只能手動改 agreements.json
  未來可加 CLI 工具：list / deactivate / delete

extract_signals v3
  升級為更細的 NLP 判斷
  目前 v2 已足夠穩定，不急

Per-session state
  目前 current_state.json 是全域單體
  若未來多平台/多對象需要分桶

