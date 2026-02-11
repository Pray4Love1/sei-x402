"""Broadcast signed transactions through NodeClient."""

from __future__ import annotations

from KinSwarm.online.node_client import NodeClient


class Broadcaster:
    def __init__(self):
        self.client = NodeClient()

    def broadcast(self, signed_tx: dict, network: str) -> dict:
        return self.client.submit(signed_tx, network)
