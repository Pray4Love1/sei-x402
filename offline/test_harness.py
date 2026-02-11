"""Compact offline harness validating entropy->agent-sign->verify flow."""

from __future__ import annotations

import asyncio

from offline.config import OPERATOR_KEY_PATH
from soul_sync.agent_credential import AgentCredential
from soul_sync.agent_verifier import AgentVerifier


async def main() -> None:
    credential = AgentCredential(OPERATOR_KEY_PATH)
    signed = await credential.sign_payload(
        {
            "id": "header_12345",
            "destination": "0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF",
            "amount": 42,
        }
    )
    verified = AgentVerifier.verify(signed, fallback_key=credential.verification_key)
    print("[SIGNED TX]", signed)
    print("[VERIFIED]", verified)


if __name__ == "__main__":
    asyncio.run(main())
