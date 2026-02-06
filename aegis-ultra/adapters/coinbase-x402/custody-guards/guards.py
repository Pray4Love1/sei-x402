from typing import Dict, Any


def validate_custody(requirement: Dict[str, Any]) -> None:
    if requirement.get("amount") is None:
        raise ValueError("missing amount for custody check")
