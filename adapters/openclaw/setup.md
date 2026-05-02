# OpenClaw 適配器

## 概述

OpenClaw 使用不同的記憶系統架構。SOUL 文件內容需要轉換為 OpenClaw 的 memory 格式。

## 設定步驟

### 1. 複製 SOUL.md

將 SOUL.md 的內容融入到 OpenClaw 的 `memory/` 目錄結構中。

### 2. OpenClaw Memory 結構

```
~/.openclaw/memory/
├── bryan/
│   ├── facts/
│   ├── preferences/
│   ├── plans/
│   └── relationship/
└── characters/
    └── rem/
        ├── identity.md
        ├── behavioral_rules.md
        └── evolution.md
```

### 3. 轉換要點

- Core Identity → `characters/{name}/identity.md`
- Memory Anchors → 融入 `bryan/relationship/` 相關檔案
- Shadow Core → 保留在 `characters/{name}/identity.md`（內部使用）
- Evolution Direction → `characters/{name}/evolution.md`

### 4. 初始化情緒狀態

在 `~/.openclaw/memory/characters/{name}/` 建立初始狀態檔案。
