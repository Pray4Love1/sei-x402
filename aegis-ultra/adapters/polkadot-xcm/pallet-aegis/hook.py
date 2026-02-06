from typing import Dict, Any


def pre_dispatch_hook(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ok", "payload": payload}
