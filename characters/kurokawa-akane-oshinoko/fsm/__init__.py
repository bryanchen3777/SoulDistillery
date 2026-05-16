"""
__init__.py — akane Hermes Plugin Entry Point
放置路徑：/home/bbf/.hermes/plugins/akane_behavior/__init__.py
"""

import sys, os

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

sys.path.insert(0, "/home/bbf/.hermes/plugins/akane_proactive")

from akane_state import inject_akane_state


def _pre_llm_call(profile: str, context_parts: list, **kwargs) -> list:
    if profile != "akane":
        return context_parts

    try:
        context_parts = inject_akane_state(profile, context_parts, **kwargs)
    except Exception as e:
        print(f"[AKANE_STATE] warn: state injection failed — {e}")

    return context_parts


def _post_llm_call(profile: str, response: str, context_parts: list = None, **kwargs) -> str:
    """
    Post hook：偵測使用者訊息是否包含約定意圖。
    若偵測到，parse 並存入 agreements.json。
    """
    if profile != "akane":
        return response

    if context_parts is None:
        return response

    try:
        last_user_msg = None
        for part in reversed(context_parts):
            if isinstance(part, dict):
                if part.get("role") == "user":
                    last_user_msg = part.get("content", "")
                    break
            elif isinstance(part, str):
                last_user_msg = part
                break

        if not last_user_msg:
            return response

        from akane_agreement_parser import detect_agreement_intent, parse_agreement_with_llm, handle_user_message
        if detect_agreement_intent(last_user_msg):
            print(f"[AKANE_HOOK] Agreement intent detected: {last_user_msg[:50]}")
            handle_user_message(last_user_msg)

    except Exception as e:
        print(f"[AKANE_HOOK] agreement detection error: {e}")

    return response
