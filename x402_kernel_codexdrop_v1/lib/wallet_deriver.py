"""Wallet derivation helpers for the x402 kernel drop."""

from __future__ import annotations

from bip44 import Wallet
from eth_account import Account


def get_receive_address(seed: bytes) -> str:
    wallet = Wallet(seed)
    acct = Account.from_key(wallet.derive_account("eth", 0).private_key)
    return acct.address


def get_spend_key(seed: bytes, index: int) -> bytes:
    return Wallet(seed).derive_account("eth", index).private_key
