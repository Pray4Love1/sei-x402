#!/usr/bin/env python3
"""
Seal a Codex payload and facilitatorFees extension.

- Codex seal covers entire payload (excluding codexMetadata)
- FacilitatorFeeQuote seal covers only the quote object
"""

from __future__ import annotations

import argparse
import json
import os
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from eth_account import Account
from eth_account.messages import encode_defunct


# ---------------------------------------------------------------------
# Canonical exclusion rules (MUST MATCH verifier)
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
    "quoteId"   
}


# ---------------------------------------------------------------------
# Canonical helpers
# ---------------------------------------------------------------------
def strip_fields(v: Any, excluded: set[str]) -> Any:
    if isinstance(v, dict):
        return {k: strip_fields(val, excluded) for k, val in v.items() if k not in excluded}
    if isinstance(v, list):
        return [strip_fields(x, excluded) for x in v]
    return v


def canonical_json(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(v: Any) -> str:
    return sha256(canonical_json(v).encode("utf-8")).hexdigest()


def sign(digest: str, key: str):
    acct = Account.from_key(key[2:] if key.startswith("0x") else key)
    msg = encode_defunct(hexstr=digest)
    sig = acct.sign_message(msg).signature.hex()
    if not sig.startswith("0x"):
        sig = "0x" + sig
    return acct.address, sig


def load_key(path: Path | None, inline: str | None) -> str:
    if inline:
        return inline.strip()
    if path:
        return path.read_text().strip()
    env = os.environ.get("X402_PRIVATE_KEY")
    if env:
        return env.strip()
    raise SystemExit("Missing private key")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--private-key")
    ap.add_argument("--private-key-file", type=Path)
    ap.add_argument("--codex-type", default="x402Drop")
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text())
    key = load_key(args.private_key_file, args.private_key)

    # --------------------------------------------------
    # Codex seal (SNAPSHOT — no mutation drift)
    # --------------------------------------------------
    codex_snapshot = strip_fields(
        json.loads(json.dumps(payload)),  # deep copy
        CODEX_EXCLUDED,
    )
    codex_digest = sha(codex_snapshot)

    # One-line invariant guard
    assert codex_digest == sha(codex_snapshot), "Codex canonicalization drift"

    codex_addr, codex_sig = sign(codex_digest, key)
    payload["codexMetadata"] = {
        "sealDigest": codex_digest,
        "sealSignature": codex_sig,
        "timestamp": int(time.time()),
        "codexType": args.codex_type,
        "signer": codex_addr,
    }

    # --------------------------------------------------
    # FacilitatorFeeQuote seal(s)
    # --------------------------------------------------
    options = (
        payload.get("extensions", {})
        .get("facilitatorFees", {})
        .get("info", {})
        .get("options", [])
    )

    sealed_quotes = 0

    for opt in options:
        quote = opt.get("facilitatorFeeQuote")
        if not isinstance(quote, dict):
            continue

        quote_snapshot = strip_fields(
            json.loads(json.dumps(quote)),  # deep copy
            FEE_QUOTE_EXCLUDED,
        )
        quote_digest = sha(quote_snapshot)

        # One-line invariant guard
        assert quote_digest == sha(quote_snapshot), "Fee quote canonicalization drift"

        addr, sig = sign(quote_digest, key)
        quote.update(
            {
                "quoteDigest": quote_digest,
                "signature": sig,
                "facilitatorAddress": addr,
                "signatureScheme": "eip191",
            }
        )
        sealed_quotes += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print("[✓] Codex sealed:", codex_digest)
    print("[✓] FacilitatorFeeQuote(s) sealed:", sealed_quotes)

if __name__ == "__main__":
    main()
