#!/usr/bin/env python3
"""Verify Codex + facilitatorFees seals."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from eth_account import Account
from eth_account.messages import encode_defunct


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
    "quoteId"
}


def strip_fields(v: Any, excluded: set[str]) -> Any:
    if isinstance(v, dict):
        return {k: strip_fields(val, excluded) for k, val in v.items() if k not in excluded}
    if isinstance(v, list):
        return [strip_fields(x, excluded) for x in v]
    return v


def sha(v: Any) -> str:
    return sha256(
        json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def recover(digest: str, sig: str) -> str:
    msg = encode_defunct(hexstr=digest)
    return Account.recover_message(msg, signature=sig)


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

    recovered = recover(computed, md["sealSignature"])
    if args.expected_signer and recovered.lower() != args.expected_signer.lower():
        raise SystemExit("Codex signer mismatch")

    print("[✓] Codex verified:", recovered)

    # --------------------------------------------------
    # Verify facilitator fee quotes
    # --------------------------------------------------
    if "facilitatorFeeQuote" in payload:
        raise SystemExit(
            "facilitatorFeeQuote must be nested under extensions.facilitatorFees.info.options"
        )

    options = (
        payload.get("extensions", {})
        .get("facilitatorFees", {})
        .get("info", {})
        .get("options", [])
    )
    if not isinstance(options, list):
        raise SystemExit("facilitatorFees.info.options must be a list")

    for opt in options:
        quote = opt.get("facilitatorFeeQuote")
        if not isinstance(quote, dict):
            continue

        stripped_q = strip_fields(quote, FEE_QUOTE_EXCLUDED)
        computed_q = sha(stripped_q)

        assert computed_q == sha(stripped_q), "Fee quote canonicalization drift"

        if computed_q != quote.get("quoteDigest"):
            raise SystemExit("Fee quote digest mismatch")

        recovered_q = recover(computed_q, quote["signature"])
        if recovered_q.lower() != quote["facilitatorAddress"].lower():
            raise SystemExit("Fee quote signer mismatch")

        print("[✓] Fee quote verified:", recovered_q)

    print("[✓] All seals verified")

if __name__ == "__main__":
    main()
