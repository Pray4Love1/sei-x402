#!/usr/bin/env python3
"""Verify payment address matches ERC-8004 agent wallet."""

from __future__ import annotations

import argparse


def normalize_evm(addr: str) -> str:
    return addr.lower()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify x402 payTo address.")
    parser.add_argument("--network", required=True)
    parser.add_argument("--pay-to", required=True)
    parser.add_argument("--agent-wallet", required=True)
    args = parser.parse_args()

    if args.network.startswith("eip155:"):
        if normalize_evm(args.pay_to) != normalize_evm(args.agent_wallet):
            raise SystemExit("PAYMENT ADDRESS MISMATCH")

    elif args.network.startswith("solana:"):
        if args.pay_to != args.agent_wallet:
            raise SystemExit("PAYMENT ADDRESS MISMATCH")

    print("OK")


if __name__ == "__main__":
    main()
