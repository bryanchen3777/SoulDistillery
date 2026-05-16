# Akane FSM Layer

黒川あかね 的情緒狀態機引擎，Hermes 相容。

## 部署路徑
- akane_state.py → /home/bbf/.hermes/plugins/akane_behavior/
- 其餘檔案 → /home/bbf/.hermes/plugins/akane_proactive/

## 環境變數（存放於 ~/.hermes/.env）
PALACE_BASE=/home/bbf/.hermes/palace
MINIMAX_API_KEY=your_key
MINIMAX_MODEL=MiniMax-M2.7
AKANE_TELEGRAM_TOKEN=your_token
AKANE_TELEGRAM_CHAT_ID=your_chat_id

## FSM 5態
| 狀態 | 觸發條件 |
|------|---------|
| OBSERVATION | 預設 |
| OVERTHINKING | stress > 60 |
| ATTACHED | attachment > 0.6 |
| IDENTITY_BLEND | echo_level >= 2 |
| SELF_SACRIFICE_MODE | collapse_risk > 0.85 |

## 主動訊息四機制
- A：FSM 狀態變化觸發
- B：外部事件觸發（沉默/深夜/壓力）
- C：茜的日常事件生成（週限3次）
- D：用戶約定條件觸發

詳細說明見 docs/akane_system_v2_overview.md
