#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    name: str
    flag: str


ACCOUNTS = {
    "alice": Account(name="Alice", flag="--alice"),
    "bob": Account(name="Bob", flag="--bob"),
    "charlie": Account(name="Charlie", flag="--charlie"),
    "relayer": Account(name="Relayer", flag="--relayer"),
}


def run_command(command: list[str], dry_run: bool) -> None:
    printable = " ".join(shlex.quote(arg) for arg in command)
    print(f"$ {printable}")
    if dry_run:
        return
    subprocess.run(command, check=True)


def node_extrinsic(node_path: str, account: Account, call: str, dry_run: bool) -> None:
    run_command(
        [node_path, "--dev", account.flag, "--", "extrinsic", call],
        dry_run,
    )


def node_rpc(node_path: str, account: Account, call: str, dry_run: bool) -> None:
    run_command(
        [node_path, "--dev", account.flag, "--", "rpc", call],
        dry_run,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the GenZk-402 end-to-end flow using node-template CLI.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()

    node_path = os.environ.get("NODE_PATH", "./target/release/node-template")

    print("Step 1 — Environment variables")
    print(f"NODE_PATH={node_path}")
    print("ALICE=//Alice BOB=//Bob CHARLIE=//Charlie RELAYER=//Relayer")

    print("\nStep 2 — Register identities")
    node_extrinsic(
        node_path,
        ACCOUNTS["alice"],
        "GenZk402.register_identity(H256::from_low_u64_be(1))",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["bob"],
        "GenZk402.register_identity(H256::from_low_u64_be(2))",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["charlie"],
        "GenZk402.register_identity(H256::from_low_u64_be(3))",
        args.dry_run,
    )

    print("\nStep 3 — Create wallets")
    node_extrinsic(
        node_path,
        ACCOUNTS["alice"],
        "GenZk402.create_wallet(H256::from_low_u64_be(101), vec![Bob,Charlie], 500)",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["bob"],
        "GenZk402.create_wallet(H256::from_low_u64_be(102), vec![Alice,Charlie], 500)",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["charlie"],
        "GenZk402.create_wallet(H256::from_low_u64_be(103), vec![Alice,Bob], 500)",
        args.dry_run,
    )

    print("\nStep 4 — Deposit funds")
    node_extrinsic(node_path, ACCOUNTS["alice"], "GenZk402.deposit(1000)", args.dry_run)
    node_extrinsic(node_path, ACCOUNTS["bob"], "GenZk402.deposit(1000)", args.dry_run)
    node_extrinsic(
        node_path, ACCOUNTS["charlie"], "GenZk402.deposit(1000)", args.dry_run
    )

    print("\nStep 5 — Send payments")
    node_extrinsic(
        node_path,
        ACCOUNTS["alice"],
        "GenZk402.send_payment(Bob, 50, H256::from_low_u64_be(101))",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["bob"],
        "GenZk402.send_payment(Charlie, 30, H256::from_low_u64_be(102))",
        args.dry_run,
    )

    print("\nStep 6 — Initiate recovery")
    node_extrinsic(
        node_path,
        ACCOUNTS["charlie"],
        "GenZk402.initiate_recovery(Alice, H256::from_low_u64_be(201))",
        args.dry_run,
    )

    print("\nStep 7 — Approve recovery")
    recovery_id = "<recovery_id_from_previous_step>"
    node_extrinsic(
        node_path,
        ACCOUNTS["bob"],
        f"GenZk402.approve_recovery({recovery_id})",
        args.dry_run,
    )
    node_extrinsic(
        node_path,
        ACCOUNTS["charlie"],
        f"GenZk402.approve_recovery({recovery_id})",
        args.dry_run,
    )

    print("\nStep 8 — Withdraw funds with PIN")
    node_extrinsic(
        node_path,
        ACCOUNTS["alice"],
        "GenZk402.withdraw(100, H256::from_low_u64_be(201))",
        args.dry_run,
    )

    print("\nStep 9 — Gasless transaction relay")
    signed_payload = "<signed_payload>"
    node_extrinsic(
        node_path,
        ACCOUNTS["relayer"],
        "GenZk402.relay_transaction(Alice, Charlie, 50, Nonces::get(Alice), "
        + signed_payload
        + ")",
        args.dry_run,
    )

    print("\nStep 10 — Verify events")
    node_rpc(
        node_path,
        ACCOUNTS["alice"],
        "state_getStorage('System.Events')",
        args.dry_run,
    )


if __name__ == "__main__":
    main()
