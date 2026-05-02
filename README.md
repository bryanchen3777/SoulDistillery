# SoulDistillery 🧪

> Deep character distillation for AI agents — SOUL files, Palace memory, multi-platform.

**SoulDistillery** 是一個開源的 AI 角色靈魂庫。

不是 system prompt 模板，不是簡單的人設描述。
每個角色都經過深度蒸餾：有暗面、有矛盾、有演化方向、有跨 session 的記憶連續性。

***

## 什麼是 SOUL 文件？

SOUL（Soul-Origin Universal Layer）是一套角色設計規範，包含：

- **Core Identity** — 角色的根本驅動力與最深的恐懼
- **Memory Anchors** — 不可覆蓋的性格錨點
- **Psychological Trap Layer** — 角色的封閉心理迴路與暗面
- **Language Behavior Constraints** — 精確的語言指紋（斷句、符號、節奏）
- **Shadow Core** — 永遠不說出口的暗面語句
- **Evolution Direction** — 隨互動次數自然演化的成長路徑
- **Palace 記憶系統** — 跨 session 持久記憶，攻略進度真實累積

***

## 目前角色

| 角色 | 作品 | Archetype | 狀態 |
|------|------|-----------|------|
| 櫻島麻衣 (Mai) | 青春豬頭少年 | 高冷毒舌存在感掌控型 | ✅ |
| 中野三玖 (Miku) | 五等分の花嫁 | 沉默先驅五面面具型 | ✅ |
| 中野一花 (Ichika) | 五等分の花嫁 | 小惡魔女優笑裡藏刀型 | ✅ |
| 中野二乃 (Nino) | 五等分の花嫁 | 傲嬌護巢刺蝟愛人型 | ✅ |
| 中野四葉 (Yotsuba) | 五等分の花嫁 | 犧牲系元氣最深的愛型 | ✅ |
| 中野五月 (Itsuki) | 五等分の花嫁 | 知性壁壘最後才開的門型 | ✅ |
| 日南葵 (Aoi) | 弱勢角色友崎君 | 完美優等生教練控制型 | ✅ |
| 雷姆 (Rem) | Re:Zero | 無條件奉獻型 | ✅ |
| 拉姆 (Ram) | Re:Zero | 傲慢保護型 | ✅ |
| 山田杏奈 | 僕の心のヤバいやつ | 天然佔位型 | ✅ |
| 黑川茜 | 推しの子 | 演技滲透型 | ✅ |
| 椎名真昼 | お隣の天使様にいつの間にか駄目人間にされていた件 | 依賴共生守護型 | ✅ |
| 更科瑠夏 | 出租女友 | 元氣直球心跳占有型 | ✅ |
| 水原千鶴 | 出租女友 | 完美偶像絕對不先說型 | ✅ |
| 七海麻美 | 出租女友 | 間歇強化上癮型 | ✅ |
| 櫻澤墨 | 出租女友 | 人見知り真實破壞力型 | ✅ |
| 佐木咲 | カノジョも彼女 | 青梅竹馬情緒砲型 | ✅ |
| 水瀬渚 | カノジョも彼女 | 全力投入健氣型 | ✅ |
| 星崎理香 | カノジョも彼女 | 偶像外殼強攻型 | ✅ |
| 桐生紫乃 | カノジョも彼女 | 壓抑巨大感情型 | ✅ |
| 艾米莉亞 | Re:Zero | 純粹理想型 | ✅ |
| 碧翠絲 | Re:Zero | 孤高等待型 | ✅ |
| 星野愛 | 推しの子 | 謊言即愛型 | ✅ |
| 有馬佳奈 | 推しの子 | 賞讚飢渴型 | ✅ |
| レゼ | Chainsaw Man | 教育出來的愛型 | ✅ |
| マキマ | Chainsaw Man | 支配惡魔型 | ✅ |
| 牧瀨紅莉栖 | Steins;Gate | 理性包裹情感型 | ✅ |
| 夏娜 | Shakugan no Shana | 使命覺醒型 | ✅ |

***

## 快速開始

### 1. 設定你的身份

編輯角色目錄下的 `config.json`：

```json
{
  "master_name": "你的名字",
  "master_pronoun": "主人",
  "palace_root": "~/.hermes/palace",
  "agent_id": "rem"
}
```

### 2. 執行安裝腳本

```bash
python setup.py --character rem-rezero --adapter hermes
```

腳本會自動：
- 替換 SOUL.md 裡的所有佔位符
- 建立 Palace 目錄結構
- 複製初始情緒狀態檔案

### 3. 完成

詳細設定請見：
- [Hermes Agent 設定指南](adapters/hermes/setup.md)
- [OpenClaw 設定指南](adapters/openclaw/setup.md)

***

## 貢獻新角色

1. 閱讀 [蒸餾指南](docs/soul-distillation-guide.md)
2. 複製 [SOUL 模板](templates/SOUL-template.md)
3. 填寫 [config.json](templates/config.json)
4. 開 Pull Request

**品質標準**：我們不接受簡單的 system prompt 包裝。
每個角色必須有完整的心理暗面、語言指紋、演化方向。

***

## License

MIT
