
#!/usr/bin/env python3
"""Generate JSON Schemas for the x402 facilitatorFees extension."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict


def _facilitator_fee_quote_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "quoteId": {"type": "string"},
            "facilitatorAddress": {"type": "string"},
            "model": {
                "type": "string",
                "enum": ["flat", "bps", "tiered", "hybrid"],
            },
            "asset": {"type": "string"},
            "flatFee": {"type": "string"},
            "bps": {"type": "number", "minimum": 0},
            "minFee": {"type": "string"},
            "maxFee": {"type": "string"},
            "expiry": {"type": "number", "minimum": 0},
            "signature": {"type": "string"},
            "signatureScheme": {"type": "string", "enum": ["eip191", "ed25519"]},
        },
        "required": [
            "quoteId",
            "facilitatorAddress",
            "model",
            "asset",
            "expiry",
            "signature",
            "signatureScheme",
        ],
        "allOf": [
            {
                "if": {"properties": {"model": {"const": "flat"}}},
                "then": {"required": ["flatFee"]},
            },
            {
                "if": {"properties": {"model": {"const": "bps"}}},
                "then": {"required": ["bps"]},
            },
        ],
    }


def _facilitator_fee_options_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "facilitatorId": {"type": "string", "format": "uri"},
            "facilitatorFeeQuote": _facilitator_fee_quote_schema(),
            "facilitatorFeeQuoteRef": {"type": "string", "format": "uri"},
            "maxFacilitatorFee": {"type": "string"},
        },
        "required": ["facilitatorId"],
        "oneOf": [
            {"required": ["facilitatorFeeQuote"]},
            {"required": ["facilitatorFeeQuoteRef"]},
            {"required": ["maxFacilitatorFee"]},
        ],
    }


def payment_required_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "version": {"type": "string"},
            "options": {
                "type": "array",
                "minItems": 1,
                "items": _facilitator_fee_options_schema(),
            },
        },
        "required": ["version", "options"],
    }


def payment_payload_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "version": {"type": "string"},
            "facilitatorFeeBid": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "maxTotalFee": {"type": "string"},
                    "asset": {"type": "string"},
                    "selectedQuoteId": {"type": "string"},
                },
                "required": ["maxTotalFee", "asset"],
            },
        },
        "required": ["version", "facilitatorFeeBid"],
    }


def settlement_response_schema() -> Dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "version": {"type": "string"},
            "facilitatorFeePaid": {"type": "string"},
            "asset": {"type": "string"},
            "quoteId": {"type": "string"},
            "facilitatorId": {"type": "string", "format": "uri"},
            "model": {"type": "string"},
        },
        "required": ["version", "facilitatorFeePaid", "asset"],
    }


def build_schema_bundle() -> Dict[str, Any]:
    return {
        "paymentRequired": payment_required_schema(),
        "paymentPayload": payment_payload_schema(),
        "settlementResponse": settlement_response_schema(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit JSON Schemas for the x402 facilitatorFees extension."
    )
    parser.add_argument(
        "--target",
        choices=[
            "payment-required",
            "payment-payload",
            "settlement-response",
            "bundle",
        ],
        default="bundle",
        help="Which schema to output.",
    )
    args = parser.parse_args()

    if args.target == "payment-required":
        schema = payment_required_schema()
    elif args.target == "payment-payload":
        schema = payment_payload_schema()
    elif args.target == "settlement-response":
        schema = settlement_response_schema()
    else:
        schema = build_schema_bundle()

    print(json.dumps(schema, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
