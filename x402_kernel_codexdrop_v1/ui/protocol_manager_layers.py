"""UI layer spec helpers for the x402 Protocol Manager view."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Layer:
    id: str
    name: str
    kind: str
    description: str
    components: list[dict[str, Any]] = field(default_factory=list)


LAYERS = [
    Layer(
        id="app-shell",
        name="Application Shell",
        kind="layout",
        description="Base split layout with left nav and main protocol view.",
        components=[
            {
                "id": "sidebar-nav",
                "kind": "sidebar",
                "items": [
                    "Dashboard",
                    "Protocol Dashboard",
                    "Risk Center",
                    "Liquidity Optimizer",
                    "Trust Graph",
                    "Strategy Lab",
                    "Policy Engine",
                    "x402 Documentation",
                    "Integration Examples",
                    "Financial Advisor",
                ],
            },
            {"id": "main-panel", "kind": "content", "surface": "gradient"},
        ],
    ),
    Layer(
        id="protocol-header",
        name="Protocol Header",
        kind="hero",
        description="Top banner introducing the x402 Protocol Manager.",
        components=[
            {
                "id": "title",
                "kind": "text",
                "value": "x402 Protocol Manager",
                "icon": "⚡",
            },
            {
                "id": "subtitle",
                "kind": "text",
                "value": "Sovereign payments. Royalty-enforced. LumenCard™ style.",
            },
            {"id": "meta", "kind": "text", "value": "ψ = 3.12 | KSSPL-1.0"},
        ],
    ),
    Layer(
        id="protocol-kpis",
        name="Protocol KPI Strip",
        kind="metrics",
        description="Top row of licensing and settlement KPIs.",
        components=[
            {"id": "license", "label": "Protocol License", "value": "KSSPL-1.0"},
            {"id": "royalty", "label": "Royalty Rate", "value": "15%"},
            {"id": "settled", "label": "Total Settled", "value": "$0.00"},
            {"id": "pending", "label": "Pending", "value": "$0.00"},
        ],
    ),
    Layer(
        id="protocol-tabs",
        name="Protocol Tabs",
        kind="navigation",
        description="Navigation tabs for overview, wallet, and proof views.",
        components=[
            {"id": "overview", "label": "Overview", "active": True},
            {"id": "wallet", "label": "Sovereign Wallet", "active": False},
            {"id": "payout", "label": "Auto-Payout", "active": False},
            {"id": "receipts", "label": "Receipts & Proofs", "active": False},
            {"id": "license-info", "label": "License Info", "active": False},
        ],
    ),
    Layer(
        id="status-panels",
        name="Status Panels",
        kind="cards",
        description="Protocol status and payment statistics panels.",
        components=[
            {
                "id": "protocol-status",
                "title": "Protocol Status",
                "rows": [
                    {"label": "Active Wallet", "value": "Not Connected"},
                    {"label": "x402 License", "value": "KSSPL-1.0"},
                    {"label": "Sovereign Mode", "value": "Standard"},
                    {"label": "Royalty Enforced", "value": "YES"},
                ],
            },
            {
                "id": "payment-stats",
                "title": "Payment Statistics",
                "rows": [
                    {"label": "Total Settlements", "value": "0"},
                    {"label": "Uncashed Checks", "value": "0"},
                    {"label": "Lifetime Royalties", "value": "$0.00"},
                    {"label": "Entropy Status", "value": "ψ = 3.12"},
                ],
            },
        ],
    ),
    Layer(
        id="welcome-card",
        name="Sovereign Welcome",
        kind="content",
        description="Primary welcome card emphasizing sovereignty messaging.",
        components=[
            {"id": "title", "value": "Welcome to Sovereign Territory"},
            {
                "id": "body",
                "value": (
                    "Your payments are protected by the x402 protocol. "
                    "Every transaction automatically enforces royalties to "
                    "support protocol development."
                ),
            },
            {
                "id": "affirmation",
                "value": "You don't log in. You don't ask permission. The Light is Yours.",
            },
        ],
    ),
    Layer(
        id="affirmation-banner",
        name="Affirmation Banner",
        kind="content",
        description="Bottom affirmation banner with protocol mantra.",
        components=[
            {
                "id": "banner",
                "value": "You don't log in. You don't ask permission. The Light is Yours. ψ = 3.12",
            }
        ],
    ),
]


def export_layers(path: Path) -> None:
    payload = {"layers": [asdict(layer) for layer in LAYERS]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_layers(Path(__file__).with_suffix(".json"))
