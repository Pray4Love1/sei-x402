#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

DEFAULT_GATEWAY_URL = "http://localhost:4020/x402/pay"


class HandoffError(ValueError):
    pass


def load_handoff(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HandoffError(f"Handoff not found: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HandoffError(f"Failed to load JSON: {exc}") from exc


def extract_authorization(payload: dict[str, Any]) -> dict[str, Any]:
    if "payload" in payload and isinstance(payload["payload"], dict):
        payload = payload["payload"]

    authorization = payload.get("authorization")
    if not isinstance(authorization, dict):
        raise HandoffError("Invalid handoff format: missing authorization")
    return authorization


def build_netting_body(raw: dict[str, Any]) -> dict[str, Any]:
    payment_payload = raw.get("paymentPayload")
    if not isinstance(payment_payload, dict):
        raise HandoffError("Invalid handoff format: missing paymentPayload")

    authorization = extract_authorization(payment_payload)

    try:
        payer = authorization["from"]
        merchant = authorization["to"]
        amount = int(authorization["value"])
    except KeyError as exc:
        raise HandoffError(f"Invalid handoff format: missing {exc}") from exc
    except (TypeError, ValueError) as exc:
        raise HandoffError(f"Invalid handoff format: invalid value ({exc})") from exc

    session_id = (
        raw.get("paymentRequirements", {}).get("resource")
        or raw.get("resource")
        or "default_session"
    )

    return {
        "sessionId": session_id,
        "payer": payer,
        "merchant": merchant,
        "microAmount": amount,
    }


def post_netting(body: dict[str, Any], gateway_url: str) -> dict[str, Any]:
    response = requests.post(gateway_url, json=body, timeout=5)
    response.raise_for_status()
    return response.json()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Net an x402 handoff bundle before broadcast."
    )
    parser.add_argument("handoff", type=Path, help="Path to handoff.json")
    parser.add_argument(
        "--gateway-url", default=DEFAULT_GATEWAY_URL, help="Netting gateway URL"
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        raw = load_handoff(args.handoff)
        body = build_netting_body(raw)
        out = post_netting(body, args.gateway_url)
    except (HandoffError, requests.RequestException) as exc:
        print(f"[!] Failed to send to netting gateway: {exc}", file=sys.stderr)
        return 1

    accumulated = out.get("accumulated", "?")
    threshold = out.get("threshold", "?")
    should_settle = out.get("shouldSettle", "?")
    print(
        f"[✓] Netted: {accumulated} / {threshold}. Settle: {should_settle}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
