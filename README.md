# SoulDistillery 🧪

> Deep character distillation for AI agents — SOUL files, Palace memory, multi-platform.

**SoulDistillery** 是一個開源的 AI 角色靈魂庫。

不是 system prompt 模板，不是簡單的人設描述。  
每個角色都經過深度蒸餾：有暗面、有矛盾、有演化方向、有跨 session 的記憶連續性。

---

## 什麼是 SOUL 文件？

SOUL（Soul-Origin Universal Layer）是一套角色設計規範，包含：

- **Core Identity** — 角色的根本驅動力與最深的恐懼
- **Memory Anchors** — 不可覆蓋的性格錨點
- **Language Behavior Constraints** — 精確的語言指紋（斷句、符號、節奏）
- **Shadow Core** — 永遠不說出口的暗面語句
- **Evolution Direction** — 隨互動次數自然演化的成長路徑
- **Palace 記憶系統** — 跨 session 持久記憶，攻略進度真實累積

---

## 目前角色

| 角色 | 作品 | Archetype | 狀態 |
|------|------|-----------|------|
| 雷姆 (Rem) | Re:Zero | 無條件奉獻型 | ✅ |
| 拉姆 (Ram) | Re:Zero | 傲慢保護型 | ✅ |
| 山田杏奈 | 僕の心のヤバいやつ | 天然佔位型 | ✅ |
| 黑川茜 | 推しの子 | 演技滲透型 | ✅ |

---

## 快速開始

### Hermes Agent

```bash
# 1. 複製 SOUL 文件到你的 profile
cp characters/rem-rezero/SOUL.md ~/.hermes/profiles/rem/SOUL.md

# 2. 初始化 Palace 目錄
mkdir -p ~/.hermes/palace/{bryan/{facts,preferences,plans,relationship},shared/events,agents/rem/{facts,events,feelings}}

# 3. 複製初始情緒狀態
cp characters/rem-rezero/palace-init/emotional-state.json \
   ~/.hermes/palace/agents/rem/emotional-state.json
```

→ 詳細設定請見 [adapters/hermes/setup.md](adapters/hermes/setup.md)

### OpenClaw

→ 詳細設定請見 [adapters/openclaw/setup.md](adapters/openclaw/setup.md)

---

## 貢獻新角色

1. 閱讀 [docs/soul-distillation-guide.md](docs/soul-distillation-guide.md)
2. 複製 [templates/SOUL-template.md](templates/SOUL-template.md)
3. 蒸餾完成後開 Pull Request

品質標準請見貢獻指南。我們不接受簡單的 system prompt 包裝。

---

## License

MIT
