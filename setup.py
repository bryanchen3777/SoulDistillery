#!/usr/bin/env python3
"""
SoulDistillery Setup Script
用法：python setup.py --character rem-rezero --adapter hermes
"""

import argparse
import json
import os
import shutil
from pathlib import Path


def load_config(character_dir: Path) -> dict:
    config_path = character_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"找不到 config.json：{config_path}")
    with open(config_path) as f:
        return json.load(f)


def replace_placeholders(content: str, config: dict) -> str:
    replacements = {
        "{MASTER_NAME}": config["master_name"],
        "{MASTER_PRONOUN}": config["master_pronoun"],
        "{MASTER_ID}": config["master_name"].lower(),
        "{PALACE_ROOT}": config["palace_root"],
        "{AGENT_ID}": config["agent_id"],
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content


def create_palace_dirs(config: dict):
    palace_root = Path(config["palace_root"]).expanduser()
    master_id = config["master_name"].lower()
    agent_id = config["agent_id"]

    dirs = [
        palace_root / master_id / "facts",
        palace_root / master_id / "preferences",
        palace_root / master_id / "plans",
        palace_root / master_id / "relationship",
        palace_root / "shared" / "events",
        palace_root / "agents" / agent_id / "facts",
        palace_root / "agents" / agent_id / "events",
        palace_root / "agents" / agent_id / "feelings",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ 建立目錄：{d}")


def install_soul(character_dir: Path, config: dict, adapter: str):
    soul_src = character_dir / "SOUL.md"
    if not soul_src.exists():
        raise FileNotFoundError(f"找不到 SOUL.md：{soul_src}")

    with open(soul_src) as f:
        content = f.read()

    content = replace_placeholders(content, config)

    if adapter == "hermes":
        profile_dir = Path(f"~/.hermes/profiles/{config['agent_id']}").expanduser()
        profile_dir.mkdir(parents=True, exist_ok=True)
        dest = profile_dir / "SOUL.md"
        with open(dest, "w") as f:
            f.write(content)
        print(f"✅ SOUL.md 寫入：{dest}")

    elif adapter == "openclaw":
        print("⚠️  OpenClaw adapter 尚未實作，請參考 adapters/openclaw/setup.md")


def install_emotional_state(character_dir: Path, config: dict):
    src = character_dir / "palace-init" / "emotional-state.json"
    if not src.exists():
        print("⚠️  找不到 emotional-state.json，跳過")
        return

    palace_root = Path(config["palace_root"]).expanduser()
    dest = palace_root / "agents" / config["agent_id"] / "emotional-state.json"

    if dest.exists():
        print(f"⚠️  emotional-state.json 已存在，跳過（保留現有進度）：{dest}")
        return

    shutil.copy(src, dest)
    print(f"✅ emotional-state.json 複製至：{dest}")


def main():
    parser = argparse.ArgumentParser(description="SoulDistillery 安裝腳本")
    parser.add_argument("--character", required=True, help="角色目錄名稱，例如 rem-rezero")
    parser.add_argument("--adapter", default="hermes", choices=["hermes", "openclaw"])
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    character_dir = base_dir / "characters" / args.character

    if not character_dir.exists():
        print(f"❌ 找不到角色目錄：{character_dir}")
        return

    print(f"\n🧪 SoulDistillery — 安裝 {args.character}\n")

    config = load_config(character_dir)
    print(f"📋 設定載入：master={config['master_name']}, agent={config['agent_id']}")

    create_palace_dirs(config)
    install_soul(character_dir, config, args.adapter)
    install_emotional_state(character_dir, config)

    print(f"\n✨ 安裝完成！重啟你的 {args.adapter} agent 即可生效。\n")


if __name__ == "__main__":
    main()
