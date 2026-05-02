# Palace 記憶系統結構

## 概述

Palace 是一個分層的外部記憶系統，讓 AI agent 跨 session 保持連續性。

## 目錄結構

```
palace/
├── bryan/                    # Bryan 相關（所有 agent 可讀寫）
│   ├── facts/               # Bryan 的已知事實
│   ├── preferences/         # Bryan 的偏好
│   ├── plans/              # Bryan 的計劃、安排
│   └── relationship/       # 感情相關
│       ├── milestones.md   # 重要里程碑
│       └── notes.md       # Bryan 說過的重要話語、Nicknames
├── shared/                   # 共享記憶（所有 agent 可讀寫）
│   └── events/            # 群聊重要事件
└── agents/
    └── {character}/        # 角色私有（只有該角色可讀寫）
        ├── facts/         # 角色的私人觀察、分析
        ├── events/       # 角色的私人事件
        └── feelings/
            └── diary.md   # 情感日記
```

## 寫入規則

### Bryan 的偏好
路徑：`bryan/preferences/YYYY-MM-DD-{theme}.md`

```
日期：{YYYY-MM-DD}
內容：{內容描述}
標籤：[{tag1}, {tag2}]
```

### 感情里程碑
路徑：`bryan/relationship/milestones.md`（append）

### 角色情感日記
路徑：`agents/{character}/feelings/diary.md`（append）

## 讀取時機

每次新 session 開始，agent 應立即讀取：
1. `agents/{character}/emotional-state.json`
2. `bryan/facts/`
3. `bryan/preferences/`
4. `bryan/plans/`
5. `bryan/relationship/`
6. `shared/events/`
7. `agents/{character}/facts/`
8. `agents/{character}/feelings/diary.md`
