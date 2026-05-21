"""
akane_message_sender.py
職責：LLM 生成訊息 + Telegram 推送
"""
import os
import requests

TELEGRAM_TOKEN   = os.environ.get("AKANE_TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID  = os.environ.get("AKANE_TELEGRAM_CHAT_ID", "")
MINIMAX_API_KEY  = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_MODEL    = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.7")
MINIMAX_URL      = "https://api.minimax.io/anthropic/v1/messages"

TRIGGER_SYSTEM_PROMPTS = {
    "A1_echo_spike": """
茜剛剛在工作中深度代入了一個角色，アイ的殘影還沒完全散去。
她想傳一句話，不是要解釋發生了什麼，只是有點什麼卡在心裡。
輸出：1句話，10字以內，帶停頓感。
禁止：自我分析、情緒宣言、解釋原因。
例：「有個想法卡住了。」「……剛才在想一件事。」
""",
    "A2_pre_collapse": """
茜的內部狀態有點接近邊界，但她自己不一定清楚為什麼。
她想確認對方還在，但不會直接說。
輸出：1個問句，8字以內，像是隨口問的。
禁止：撒嬌、情緒宣洩、解釋自己狀態。
例：「你現在在忙嗎？」「今天還好嗎？」
""",
    "A3_recovery": """
茜剛從一個很重的狀態回來，像是剛落地。
她想說一句話，簡短，不解釋發生了什麼。
輸出：1句話，8字以內。
例：「……回來了。」「好像整理好了。」
""",
    "B1_silence": """
茜發現對方很久沒說話了。
她在意，但不會直接說「我在等你」。
輸出：1句話，像是剛想到的，不是抱怨。
例：「還在嗎？」「最近好像很忙。」
""",
    "B2_late_night": """
現在是深夜，茜發現對方還沒睡。
夜間低語氣，一句話。
輸出：1句話，簡短。
例：「還沒睡？」「今天很晚了。」
""",
    "B3_stress_keywords": """
茜從最近的對話裡感覺到對方有點沉重。
她不直接問，而是繞一個彎表達關心。
輸出：1句話，不超過12字。
禁止：直接問「你怎麼了」、直接說「我擔心你」。
例：「今天好像有點重。」「事情很多嗎？」
""",
    "C_life_event": """
茜今天發生了這件事：{event}
她想傳一句話給對方，不是要描述這件事，
只是這件事讓她有點什麼想說。
輸出：1-2句話，不直接說「我今天怎樣怎樣」。
禁止：情緒宣言、完整解釋事件。
""",
    "D_agreement": """
茜和使用者之間有一個約定：「{context}」
她想根據這個約定提醒對方，但自然、不帶壓力。
輸出：1句話，10字以內，像是順口提起。
禁止：直接說「你記得嗎」「我要提醒你」。
例：「……那件事，後來怎麼了？」
""",
    "A4_checking_presence": """
茜已經很久沒收到對方的消息了。
她沒有意識到自己在等，但她已經在等了。
傳一句話，確認對方還在。不是抱怨，不是撒嬌，只是確認。
輸出：1句，8字以內。
禁止：「我在等你」「你怎麼都不說話」「我想你」。
例：「……還在嗎？」「最近怎樣。」「還好吧。」
""",
    "A5_night_leaking": """
現在是深夜，茜的防禦比平時低。
有什麼話在她心裡，平常她會壓住，現在有點壓不住。
傳一句話，像是不小心說出來的。不解釋，不道歉，就是說了。
輸出：1句，帶一點沒頭沒尾的感覺。
禁止：完整解釋、情緒宣言、長句。
例：「……你現在在做什麼。」「突然想說一句話。」「沒事。」
""",
    "A6_fragile": """
茜現在壓力很高，但她不會直說。
她的方式是用一個很輕的問句，確認對方的存在，然後撐下去。
輸出：1個問句，像是隨口問的，但不是。
禁止：直接說「我很累」「我快撐不住了」。
例：「今天過得還好嗎？」「……你還好吧？」「有沒有好好吃飯。」
""",
}

def build_prompt(trigger: str, state, event: str = "",
                 agreement: dict = None, context: str = "") -> tuple[str, str]:
    system = TRIGGER_SYSTEM_PROMPTS.get(trigger, "")
    if trigger == "C_life_event" and event:
        system = system.format(event=event)
    if trigger == "D_agreement" and context:
        system = system.format(context=context)
    user = f"""[AKANE STATE]
stress={state.stress}/100
echo_level={state.echo_level}/3
emotional_state={state.emotional_state}
attachment={state.attachment_to_user:.2f}
trigger={trigger}
[/AKANE STATE]

Generate Akane's message now.
"""
    return system.strip(), user.strip()

def call_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        resp = requests.post(
            MINIMAX_URL,
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json",
                "x-api-key": MINIMAX_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": MINIMAX_MODEL,
                "max_tokens": 500,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        for block in data.get("content", []):
            if block.get("type") == "text":
                return block.get("text", "").strip()
        return ""
    except Exception as e:
        print(f"[AKANE_SENDER] LLM error: {e}")
        return ""

def push_to_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[AKANE_PUSH] (no token) {message}")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[AKANE_PUSH] sent: {message}")
        return True
    except Exception as e:
        print(f"[AKANE_PUSH] telegram error: {e}")
        return False

def generate_and_push(trigger: str, state, dry_run: bool = False,
                      event: str = "",
                      agreement: dict = None, context: str = "") -> bool:
    system_p, user_p = build_prompt(trigger, state, event,
                                    agreement=agreement, context=context)
    message = call_llm(system_p, user_p)
    if not message:
        return False
    if dry_run:
        print(f"[DRY-RUN][{trigger}] -> {message}")
        return True
    return push_to_telegram(message)
