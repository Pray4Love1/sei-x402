#!/usr/bin/env python3
"""Generate JSON Schemas for the x402 8004-reputation extension."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict


def payment_required_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "version": {
                "type": "string",
                "pattern": "^\\d+\\.\\d+\\.\\d+$",
            },
            "registrations": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "agentRegistry": {"type": "string"},
                        "agentId": {"type": "string"},
                        "reputationRegistry": {"type": "string"},
                    },
                    "required": ["agentRegistry", "agentId", "reputationRegistry"],
                },
            },
            "endpoint": {"type": "string", "format": "uri"},
            "feedbackAggregator": {"type": "string", "format": "uri"},
        },
        "required": ["version", "registrations"],
    }


def interaction_data_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "x402 8004-reputation InteractionData",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "networkId": {
                "type": "string",
                "description": "CAIP-2 network identifier",
            },
            "agentId": {
                "type": "string",
                "description": "Agent identifier on this network",
            },
            "taskRef": {
                "type": "string",
                "description": "CAIP-220 transaction reference",
            },
            "interactionHash": {
                "type": "string",
                "pattern": "^0x[0-9a-fA-F]{64}$",
                "description": "keccak256(taskRef || requestBody || responseBody)",
            },
            "agentSignature": {
                "type": "string",
                "description": "Signature over interactionHash",
            },
            "timestamp": {
                "type": "number",
                "minimum": 0,
                "description": "Unix timestamp (NOT signed)",
            },
        },
        "required": [
            "networkId",
            "agentId",
            "taskRef",
            "interactionHash",
            "agentSignature",
            "timestamp",
        ],
    }


def bundle() -> Dict[str, Any]:
    return {
        "paymentRequired": payment_required_schema(),
        "interactionData": interaction_data_schema(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit JSON Schemas for the x402 8004-reputation extension."
    )
    parser.add_argument(
        "--target",
        choices=["payment-required", "interaction", "bundle"],
        default="bundle",
    )
    args = parser.parse_args()

    if args.target == "payment-required":
        schema = payment_required_schema()
    elif args.target == "interaction":
        schema = interaction_data_schema()
    else:
        schema = bundle()

    print(json.dumps(schema, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
