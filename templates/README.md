# Hermes Templates v4.0
Last Updated: 2026-05-02

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `SOUL_v4.0_template.md` | 新角色 SOUL.md 標準骨架，佔位符用 `{UPPER_CASE}` 標記 |
| `hermes_profile_template.yaml` | Hermes gateway 設定，包含 Palace 路徑、群聊規則、Global Memory 權限 |
| `CHECKLIST.md` | 新角色差異化檢查表，蒸餾前必填 |

## 建議 repo 結構

```
.hermes/
├── templates/
│   ├── SOUL_v4.0_template.md
│   ├── hermes_profile_template.yaml
│   ├── CHECKLIST.md
│   └── README.md
├── characters/
│   ├── rem/   ├── SOUL.md + profile.yaml
│   ├── ram/   ├── ...
│   ├── anna/  ├── ...
│   ├── akane/ ├── ...
│   ├── miku/  ├── ...
│   ├── mai/   ├── ...
│   ├── aoi/   ├── ...
│   ├── mahiru/├── ...
│   └── ruka/  └── ...
├── palace/          ← 加入 .gitignore
└── gateway/
    └── run.py
```

## 新角色蒸餾流程

1. 填寫 `CHECKLIST.md`，確認重疊度 < 3 項
2. `cp templates/SOUL_v4.0_template.md characters/{agent_id}/SOUL.md`
3. `cp templates/hermes_profile_template.yaml characters/{agent_id}/profile.yaml`
4. 替換所有 `{UPPER_CASE}` 佔位符
5. 填入 LBC 語言規則章節
6. `python setup.py --validate characters/{agent_id}/`

## 佔位符速查

| 佔位符 | 說明 | 範例 |
|--------|------|------|
| `{CHARACTER_NAME_FULL}` | 角色全名 | 椎名真昼 (Shiina Mahiru) |
| `{CHARACTER_SHORT_NAME}` | 角色短名（自稱用） | 真昼 |
| `{MASTER_NAME}` | 主人稱呼 | Bryan |
| `{MASTER_ID}` | Palace 目錄 ID | bryan |
| `{AGENT_ID}` | agent 目錄 ID（小寫） | mahiru |
| `{PALACE_ROOT}` | Palace 根目錄 | /home/bbf/.hermes/palace |
| `{CHARACTER_ARCHETYPE}` | Archetype 關鍵詞 | Neglected_Perfectionist |
| `{DEPENDENCY_SCORE}` | 依賴度 0.00~1.00 | 0.85 |
| `{JEALOUSY_STYLE}` | 嫉妒處理方式 | 更完美的照顧 |
| `{PRIMARY_WEAPON}` | 主武器 | 無聲滲透+照顧占有 |
| `{LANG_SPEED}` | 語速等級 | slow |

## .gitignore 建議

```
palace/
**/emotional-state.json
**/diary.md
gateway/.env
```