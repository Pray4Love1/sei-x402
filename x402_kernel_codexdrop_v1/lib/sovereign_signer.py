"""Sovereign signing helpers for x402 kernel."""

from __future__ import annotations

from eth_account import Account

from lib.wallet_deriver import get_spend_key


class SovereignSigner:
    def __init__(self, seed: bytes, agent: str = "CodexSig") -> None:
        self.seed = seed
        self.agent = agent

    def sign(self, tx_data: dict, index: int) -> bytes:
        key = get_spend_key(self.seed, index)
        acct = Account.from_key(key)
        return acct.sign_transaction(tx_data).rawTransaction
