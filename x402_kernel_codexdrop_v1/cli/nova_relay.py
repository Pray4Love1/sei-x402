"""Submit an x402 payload to a Nova relay endpoint."""

from __future__ import annotations

import json

import requests


def main() -> None:
    with open("schemas/x402_payment_payload.json", encoding="utf-8") as handle:
        schema = json.load(handle)

    with open("wallet_state.json", encoding="utf-8") as handle:
        wallet = json.load(handle)

    payload = {
        "type": "x402PaymentRequired",
        "from": wallet["handle"],
        "to": "@receiver",
        "amount": "3.21",
        "vault": wallet["receiveAddress"],
        "zkCommit": "0xabc123...",
        "relay": "https://relay.base44.app",
        "sig": "0xsigned...",
    }

    res = requests.post(payload["relay"] + "/mcp/proofSubmit", json=payload, timeout=10)
    print(res.status_code, res.text)


if __name__ == "__main__":
    main()
