"""
akane_life_events.py — 機制三：茜自己的事件生成器
"""

import random
from datetime import datetime, timedelta
from akane_state import AkaneState

WEEKLY_LIMIT = 3

AKANE_LIFE_EVENTS = {
    "work": [
        "剛演完一個情緒很重的場次，還沒完全出戲",
        "在背台詞，有一句怎麼都背不進去",
        "今天哭了一場，哭完反而輕鬆了",
        "剛和導演討論角色動機，有點卡住",
        "排練結束，比預期早收工",
        "今天試鏡了一個很不像自己的角色",
        "今天在舞台上有一個瞬間，感覺找到了",
    ],
    "observation": [
        "在咖啡廳看到一對情侶，好像在吵架",
        "回家的路上看到一隻流浪貓",
        "今天天氣很奇怪，像是會下雨又出不來",
        "在電車上看到一個女生在讀《【推しの子】》",
        "路過書店，看到雜誌封面是以前的同期演員",
    ],
    "personal": [
        "今天吃了一個很久沒吃的東西",
        "房間的燈泡壞了，換了三次才換對",
        "收到一封很久沒聯絡的人發的信",
        "今天突然想起以前的事",
        "發現自己最近好像變得比較能睡著了",
    ],
}

def sample_life_event() -> str:
    category = random.choice(list(AKANE_LIFE_EVENTS.keys()))
    return random.choice(AKANE_LIFE_EVENTS[category])

def check_life_event_cooldown(cooldowns: dict) -> bool:
    last = cooldowns.get("C_life_event")
    if last is None:
        return True
    return datetime.now() - datetime.fromisoformat(last) > timedelta(hours=18)
