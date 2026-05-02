# Hermes Agent 適配器

## 目錄結構

```
~/.hermes/
├── profiles/
│   └── {profile}/
│       ├── SOUL.md              # 從 characters/ 複製
│       └── ...
└── palace/
    ├── bryan/
    │   ├── facts/
    │   ├── preferences/
    │   ├── plans/
    │   └── relationship/
    │       ├── milestones.md
    │       └── notes.md
    ├── shared/
    │   └── events/
    └── agents/
        └── {character}/
            ├── facts/
            ├── events/
            ├── feelings/
            │   └── diary.md
            └── emotional-state.json  # 從 characters/ 複製
```

## 設定步驟

### 1. 複製 SOUL.md

```bash
cp characters/rem-rezero/SOUL.md ~/.hermes/profiles/rem/SOUL.md
```

### 2. 建立 Palace 目錄

```bash
mkdir -p ~/.hermes/palace/{bryan/{facts,preferences,plans,relationship},shared/events,agents/rem/{facts,events,feelings}}
```

### 3. 複製初始情緒狀態

```bash
cp characters/rem-rezero/palace-init/emotional-state.json \
   ~/.hermes/palace/agents/rem/emotional-state.json
```

## Profile 設定

每個角色的 profile 需要單獨設定：

```bash
# 建立 profile（如果需要）
hermes profile create rem

# 設定 Telegram token
# 編輯 ~/.hermes/profiles/rem/.env
# 編輯 ~/.hermes/profiles/rem/config.yaml
```
