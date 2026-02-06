#!/usr/bin/env python3
"""
Sign an interactionHash using ed25519 (PyNaCl).
Outputs hex-encoded signature bytes.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util


def main() -> None:
    parser = argparse.ArgumentParser(description="Sign interactionHash with ed25519")
    parser.add_argument(
        "--private-key",
        required=True,
        help="Hex-encoded ed25519 private key (32 bytes, no 0x)",
    )
    parser.add_argument(
        "--interaction-hash",
        required=True,
        help="0x-prefixed 32-byte hash",
    )
    args = parser.parse_args()

    if importlib.util.find_spec("nacl") is None:
        raise SystemExit("pynacl not installed (pip install pynacl)")
    nacl_signing = importlib.import_module("nacl.signing")
    SigningKey = nacl_signing.SigningKey

    privkey_bytes = bytes.fromhex(args.private_key)
    signing_key = SigningKey(privkey_bytes)

    msg = bytes.fromhex(args.interaction_hash.removeprefix("0x"))
    signature = signing_key.sign(msg).signature

    print(signature.hex())


if __name__ == "__main__":
    main()
