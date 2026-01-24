# RFC: Facilitator Fee Disclosure Extension (`facilitatorFees`)

## Summary

This RFC proposes an opt-in extension to standardize facilitator fee disclosure for
fee-aware multi-facilitator routing in x402 v2.

It introduces:

- **facilitatorFeeQuote**: Facilitator-signed fee disclosure surfaced at `PaymentRequired` time
- **facilitatorFeeBid** (optional): Client fee constraints surfaced in `PaymentPayload`
- **facilitatorFeePaid** (optional): Actual fee charged surfaced in `SettlementResponse`

> **Required Core Change**
>
> This extension depends on `SettlementResponse` supporting an optional `extensions` field:
>
> ```ts
> extensions?: Record<string, unknown>;
> ```
>
> This change is **additive** and backwards-compatible. Existing facilitators continue to work
> unchanged, and existing clients will safely ignore the new field.
>
> This extension SHOULD NOT be considered fully usable until the core type is updated.

---

## Motivation

x402 v2 supports multi-facilitator routing, but lacks a standard for facilitator fee
disclosure. Facilitators are beginning to charge explicit fees:

- Coinbase CDP x402 Facilitator: flat-fee model
- Thirdweb: percentage-based fees (BPS)

Without standardization:

- Clients cannot compare total cost across facilitators
- Multi-facilitator routing cannot become a real market
- Each facilitator invents bespoke fee formats

---

## Goals

- Enable fee-aware routing across facilitators
- Standardize disclosure without enforcing a single fee model
- Preserve privacy-preserving server behavior
- Enforce client agency in facilitator selection
- Maintain backwards compatibility

---

## Non-Goals

- NOT standardizing a preferred fee model
- NOT mandating facilitator discovery policy
- NOT changing settlement semantics

---

## Placement

Uses the top-level `extensions` field following the v2 extension pattern:

- `PaymentRequired.extensions.facilitatorFees`
- `PaymentPayload.extensions.facilitatorFees`
- `SettlementResponse.extensions.facilitatorFees`

---

## A) Server → Client: `facilitatorFeeQuote`

### Facilitator Options

Each option includes:

- `facilitatorId` (MUST be a valid URL)
- `facilitatorFeeQuote` (signed quote) OR
- `facilitatorFeeQuoteRef` (URL to fetch)
- `maxFacilitatorFee` (optional upper bound)

### FacilitatorFeeQuote Fields

| Field | Description |
|-----|------------|
| quoteId | Unique identifier |
| facilitatorAddress | Signing address |
| model | flat \| bps \| tiered \| hybrid |
| asset | Fee currency |
| flatFee / bps / minFee / maxFee | Model-specific values |
| expiry | Unix timestamp (MUST ≥ payment.validBefore) |
| signature | Facilitator signature |
| signatureScheme | eip191 \| ed25519 |

---

## B) Client → Server: `facilitatorFeeBid`

| Field | Description |
|-----|------------|
| maxTotalFee | Hard fee constraint |
| asset | Fee currency |
| selectedQuoteId | Optional explicit selection |

### Selection Semantics

- If `selectedQuoteId` is absent → server MAY choose any compliant facilitator
- If present → server MUST honor it or reject
- Asset mismatch → MUST reject

This enforces client agency.

---

## C) Server → Client: `facilitatorFeePaid`

Reports the actual fee charged after settlement.

| Field | Description |
|-----|------------|
| facilitatorFeePaid | Actual fee charged |
| asset | Fee currency |
| quoteId | Quote used |
| facilitatorId | Facilitator selected |
| model | Fee model applied |

---

## Signature Schemes

| Network Family | Scheme |
|---------------|--------|
| eip155:* | eip191 |
| solana:* | ed25519 |

---

## Canonical Quote Format (IMPORTANT)

### Canonicalization Rules

The signature is computed over a canonical JSON representation of the quote.

**Signed payload MUST include ONLY economic terms.**

### EXCLUDED from signing

- `quoteId`
- `facilitatorAddress`
- `signature`
- `signatureScheme`
- `quoteDigest`

### INCLUDED in signing (alphabetical order)

```
asset
bps (if present)
expiry
flatFee (if present)
maxFee (if present)
minFee (if present)
model
```

### Canonicalization Steps

1. Remove excluded fields
2. Sort remaining fields alphabetically
3. Serialize as compact JSON
4. Hash:
   - keccak256 (EIP-191)
   - SHA-256 (Ed25519)
5. Sign hash with facilitator private key

### Rationale

Identifiers and provenance MUST NOT affect fee signatures.  
This allows:

- Quote reuse
- Deterministic routing
- Fee comparison
- Signature portability

---

## Fee Model Semantics

### Flat

```
fee = flatFee
```

### BPS

```
fee = max(minFee, min(maxFee, floor(paymentAmount * bps / 10000)))
```

- Division MUST floor
- `maxFee` RECOMMENDED
- Quotes without `maxFee` MAY be excluded

### Tiered / Hybrid

- SHOULD include minFee/maxFee bounds

---

## Expiry Handling

- `expiry` MUST ≥ `validBefore`
- Expired selectedQuoteId → MUST reject
- Expired settlement → MUST reject
- Optional ~30s clock skew allowance

---

## Privacy Considerations

- Multiple indistinguishable options
- Use `maxFacilitatorFee` for concealment
- Prefer embedded quotes for privacy
- `facilitatorFeeQuoteRef` leaks IP (use proxy if needed)

---

## Backwards Compatibility

- Entirely opt-in
- Existing clients ignore extensions
- Existing facilitators unaffected
