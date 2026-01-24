#!/usr/bin/env python3
"""Verify Codex + facilitatorFees seals."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import importlib.util

if importlib.util.find_spec("eth_account") is None:
    raise SystemExit(
        "Missing dependency: eth-account. Install with `python -m pip install eth-account`."
    )

from eth_account import Account
from eth_account.messages import encode_defunct

# ---------------------------------------------------------------------
# Canonical exclusion rules (MUST MATCH signer)
# ---------------------------------------------------------------------
CODEX_EXCLUDED = {
    "codexMetadata",
    "extensions",
    "sealDigest",
    "sealSignature",
    "signature",
    "signatureScheme",
}

FEE_QUOTE_EXCLUDED = {
    "signature",
    "signatureScheme",
    "quoteDigest",
    "facilitatorAddress",
    "quoteId",
}


def strip_fields(value: Any, excluded: set[str]) -> Any:
    if isinstance(value, dict):
        return {key: strip_fields(val, excluded) for key, val in value.items() if key not in excluded}
    if isinstance(value, list):
        return [strip_fields(item, excluded) for item in value]
    return value


def sha(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def recover(digest: str, sig: str) -> str:
    if not sig:
        raise SystemExit("Missing signature on sealed payload.")
    signature = sig if sig.startswith("0x") else f"0x{sig}"
    msg = encode_defunct(hexstr=digest)
    return Account.recover_message(msg, signature=signature)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--expected-signer")
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text())

    # --------------------------------------------------
    # Verify Codex seal
    # --------------------------------------------------
    md = payload.get("codexMetadata", {})
    stripped = strip_fields(payload, CODEX_EXCLUDED)
    computed = sha(stripped)

    assert computed == sha(stripped), "Codex canonicalization drift"

    if computed != md.get("sealDigest"):
        raise SystemExit("Codex digest mismatch")

    recovered = recover(computed, md.get("sealSignature"))
    if args.expected_signer and recovered.lower() != args.expected_signer.lower():
        raise SystemExit("Codex signer mismatch")

    print("[✓] Codex verified:", recovered)

    # --------------------------------------------------
    # Verify facilitator fee quotes
    # --------------------------------------------------
    options = (
        payload.get("extensions", {})
        .get("facilitatorFees", {})
        .get("info", {})
        .get("options", [])
    )

    for opt in options:
        quote = opt.get("facilitatorFeeQuote")
        if not isinstance(quote, dict):
            continue

        stripped_q = strip_fields(quote, FEE_QUOTE_EXCLUDED)
        computed_q = sha(stripped_q)

        assert computed_q == sha(stripped_q), "Fee quote canonicalization drift"

        if computed_q != quote.get("quoteDigest"):
            raise SystemExit("Fee quote digest mismatch")

        recovered_q = recover(computed_q, quote.get("signature"))
        facilitator_address = quote.get("facilitatorAddress")
        if not facilitator_address:
            raise SystemExit("Fee quote missing facilitatorAddress")
        if recovered_q.lower() != facilitator_address.lower():
            raise SystemExit("Fee quote signer mismatch")

        print("[✓] Fee quote verified:", recovered_q)

    print("[✓] All seals verified")


if __name__ == "__main__":
    main()
