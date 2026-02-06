from typing import Dict, Any


def map_fee_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    return {"policy": policy, "status": "mapped"}
