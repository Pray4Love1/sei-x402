from typing import Dict, Any


def enforce_fee_policy(message: Dict[str, Any]) -> bool:
    return "fee" in message
