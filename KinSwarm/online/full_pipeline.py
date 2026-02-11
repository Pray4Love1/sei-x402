"""Pipeline dispatcher for multi-network signed payload submission."""

from __future__ import annotations

from KinSwarm.online.broadcaster import Broadcaster


def dispatch(signed_payloads: list[dict], networks: list[str]) -> list[dict]:
    broadcaster = Broadcaster()
    results: list[dict] = []
    for signed_tx in signed_payloads:
        for network in networks:
            results.append(broadcaster.broadcast(signed_tx, network))
    return results
