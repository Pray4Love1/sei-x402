#!/usr/bin/env python3
"""
Load and validate an ERC-8004 agent registration file.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from typing import Any, Dict, List


def _fetch_json(uri: str) -> Dict[str, Any]:
    if uri.startswith("ipfs://"):
        uri = uri.replace("ipfs://", "https://ipfs.io/ipfs/")
    with urllib.request.urlopen(uri) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _resolve_valid_signers(registration: Dict[str, Any], now: int) -> List[Dict[str, Any]]:
    signers = registration.get("signers", [])
    valid = []

    for signer in signers:
        valid_from = signer.get("validFrom", 0)
        valid_until = signer.get("validUntil")
        if now < valid_from:
            continue
        if valid_until is not None and now >= valid_until:
            continue
        valid.append(signer)

    return valid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load ERC-8004 registration and resolve valid signers"
    )
    parser.add_argument(
        "--registration-uri",
        required=True,
        help="tokenURI from ERC-8004 registry",
    )
    args = parser.parse_args()

    now = int(time.time())
    registration = _fetch_json(args.registration_uri)

    if registration.get("type") != "https://eips.ethereum.org/EIPS/eip-8004#registration-v1":
        raise SystemExit("Invalid registration type")

    if "registrations" not in registration or "signers" not in registration:
        raise SystemExit("Missing required registration fields")

    valid_signers = _resolve_valid_signers(registration, now)
    if not valid_signers:
        raise SystemExit("No valid signers at current timestamp")

    output = {
        "name": registration.get("name"),
        "registrations": registration["registrations"],
        "validSigners": valid_signers,
        "timestamp": now,
    }

    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
