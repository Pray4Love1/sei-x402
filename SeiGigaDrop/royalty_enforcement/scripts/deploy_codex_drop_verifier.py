#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy CodexDropVerifier using a compiled artifact JSON."
    )
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--drop-hash", required=True)
    parser.add_argument("--chain-id", type=int, default=None)
    parser.add_argument("--gas", type=int, default=None)
    return parser.parse_args(argv)


def load_artifact(path: Path) -> tuple[list[dict], str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    abi = raw.get("abi")
    bytecode = raw.get("bytecode")
    if not abi or not bytecode:
        raise ValueError("Artifact must include abi and bytecode")
    return abi, bytecode


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        from web3 import Web3
    except ImportError as exc:
        print("[!] Missing dependency: web3", file=sys.stderr)
        return 1

    try:
        abi, bytecode = load_artifact(args.artifact)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[!] Failed to load artifact: {exc}", file=sys.stderr)
        return 1

    web3 = Web3(Web3.HTTPProvider(args.rpc_url))
    if not web3.is_connected():
        print("[!] Failed to connect to RPC", file=sys.stderr)
        return 1

    account = web3.eth.account.from_key(args.private_key)
    chain_id = args.chain_id or web3.eth.chain_id

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    deploy_tx = contract.constructor(args.drop_hash).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": chain_id,
            "gas": args.gas or 2_000_000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    signed = account.sign_transaction(deploy_tx)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"[✓] CodexDropVerifier deployed: {receipt.contractAddress}")
    print(f"[i] Transaction hash: {tx_hash.hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
