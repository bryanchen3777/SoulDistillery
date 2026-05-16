# Akane System Build Log

## v2.0 — 2026-05-16

### Phase 1：FSM + SOUL + Palace + Proactive 三機制
- SOUL.md v1.0 完成（TIER 0–15 + HIGHEST_PRIORITY + Palace 規則）
- akane_state.py v1.1（FSM 5態 + extract_signals v2）
- _pre_llm_call 注入 AKANE_STATE block
- 主動訊息系統上線（機制一A/二B/三C）
- 推送端：Telegram Bot + MiniMax-M2.7
- 驗證通過：TEST 1-5 全部 ✓

### Phase 2：User Agreement Layer
- akane_agreements.py（Storage API + 6種 Checker）
- akane_agreement_parser.py（NLP 解析 + LLM call）
- _post_llm_call hook（對話偵測→自動存入 agreements.json）
- 機制四 D 整合進 proactive main loop
- 驗證通過：silence_timeout / keyword_trigger / dry-run ✓

### 參數總覽
- STRESS_DECAY = 0.88
- ECHO_DECAY = 0.4
- COLLAPSE_THRESHOLD = 0.85
- FSM 狀態：OBSERVATION / OVERTHINKING / ATTACHED / IDENTITY_BLEND / SELF_SACRIFICE_MODE
- 全局冷卻鎖：45分鐘
- 週生活事件上限：3次
