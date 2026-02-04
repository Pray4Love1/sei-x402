# facilitatorFees extension scripts (Jan 31 spec)

This directory contains helper scripts that implement the Jan 31 `facilitatorFees`
extension workflow for x402 v2. They provide the canonical JSON Schema emission
and the hashing workflow required for facilitator fee quote signatures.

## What the scripts do

### `facilitator_fees_schema.py`

Generates JSON Schemas for the three extension payloads described in the spec:

- **PaymentRequired** (`extensions.facilitatorFees.info`)
- **PaymentPayload** (`extensions.facilitatorFees.info`)
- **SettlementResponse** (`extensions.facilitatorFees.info`)

The schema output enforces required fields and model-specific rules:

- `flat` quotes require `flatFee`.
- `bps` quotes require `bps`.
- Each option must include exactly one of:
  `facilitatorFeeQuote`, `facilitatorFeeQuoteRef`, or `maxFacilitatorFee`.
- `options` must contain at least one entry.

Example usage:

```bash
python scripts/facilitator_fees_schema.py --target payment-required
python scripts/facilitator_fees_schema.py --target payment-payload
python scripts/facilitator_fees_schema.py --target settlement-response
python scripts/facilitator_fees_schema.py --target bundle
```

### `facilitator_fees_quote.py`

Canonicalizes a `facilitatorFeeQuote` for signing and computes the digest using
one of the supported signature schemes:

- **eip191** → Keccak-256 digest of the canonical JSON
- **ed25519** → SHA-256 digest of the canonical JSON

The script follows the spec guidance by stripping `signature` and
`signatureScheme` from the canonicalized payload, sorting keys lexicographically,
and emitting compact JSON (RFC 8785-compatible for typical quote payloads).

Example usage:

```bash
python scripts/facilitator_fees_quote.py --input quote.json --scheme eip191
python scripts/facilitator_fees_quote.py --input quote.json --scheme ed25519
python scripts/facilitator_fees_quote.py --input quote.json --scheme eip191 --print-canonical
python scripts/facilitator_fees_quote.py --input quote.json --scheme eip191 --output-json
```

Example output (digest only):

```
0x1234abcd...
```

Example output (`--output-json`):

```json
{
  "canonicalJson": "{\"asset\":\"0x...\",\"expiry\":1737400000,...}",
  "digest": "0x1234abcd...",
  "signatureScheme": "eip191"
}
```

## Alignment with the Jan 31 facilitatorFees spec

These scripts are aligned with the spec text you shared:

- **Schema coverage:** PaymentRequired, PaymentPayload, and SettlementResponse
  payloads are modeled with required fields and model-specific requirements.
- **Signature schemes:** `eip191` (Keccak-256) and `ed25519` (SHA-256) are the
  only accepted schemes, matching the spec table.
- **Canonicalization:** Keys are sorted with compact JSON serialization and the
  signature fields are removed before hashing, matching the RFC 8785 guidance
  for canonical quote serialization.

If you need stricter canonicalization (full RFC 8785 edge cases, such as
floating-point normalization or escape handling beyond typical payloads),
consider adding a dedicated JCS library or enforcing canonical JSON generation
at the quote creation point.

## Quick validation checklist

- Confirm `expiry` in each quote is >= the payment `validBefore`.
- For `bps` quotes, include `maxFee` if you need deterministic fee comparisons.
- Ensure the signer uses the digest emitted by `facilitator_fees_quote.py`.

## Troubleshooting

- If the hash does not verify, ensure the quote JSON **exactly** matches the
  signed payload (including numeric values and string casing).
- Do not include `signature` or `signatureScheme` in the signed payload.
