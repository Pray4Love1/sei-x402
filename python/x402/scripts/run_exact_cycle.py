#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from eth_account import Account

from x402.exact import decode_payment, prepare_payment_header, sign_payment_header
from x402.types import PaymentRequirements


def load_payment_requirements(path: Path) -> PaymentRequirements:
    if not path.exists():
        raise FileNotFoundError(f"Payment requirements not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if "paymentRequirements" in raw:
        raw = raw["paymentRequirements"]
    return PaymentRequirements.model_validate(raw)


def build_handoff_bundle(
    requirements: PaymentRequirements,
    private_key: str,
    x402_version: int,
) -> dict[str, Any]:
    account = Account.from_key(private_key)
    header = prepare_payment_header(account.address, x402_version, requirements)
    encoded = sign_payment_header(account, requirements, header)
    payload = decode_payment(encoded)

    return {
        "xPaymentHeader": encoded,
        "paymentPayload": payload,
        "paymentRequirements": requirements.model_dump(by_alias=True),
    }


def write_handoff(path: Path, bundle: dict[str, Any]) -> None:
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare an x402 EXACT payment handoff bundle and optionally net it."
    )
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--x402-version", type=int, default=1)
    parser.add_argument(
        "--skip-netting",
        action="store_true",
        help="Only generate the handoff bundle without netting.",
    )
    parser.add_argument(
        "--gateway-url",
        default=None,
        help="Override the netting gateway URL.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        requirements = load_payment_requirements(args.requirements)
        bundle = build_handoff_bundle(
            requirements, args.private_key, args.x402_version
        )
        write_handoff(args.output, bundle)
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as exc:
        print(f"[!] Failed to prepare handoff: {exc}", file=sys.stderr)
        return 1

    print(f"[i] Handoff bundle written to {args.output}")

    if args.skip_netting:
        return 0

    script_path = Path(__file__).with_name("net_then_broadcast.py")
    command = [sys.executable, str(script_path), str(args.output)]
    if args.gateway_url:
        command += ["--gateway-url", args.gateway_url]

    print("[i] Sending to Kin Netter for micro netting...")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[!] Netting step failed: {exc}", file=sys.stderr)
        return exc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
