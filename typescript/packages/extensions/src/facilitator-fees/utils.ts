import type { FacilitatorFeeQuote } from "./types.js";

// Fields that must NOT be included in the digest payload
export const EXCLUDED_QUOTE_FIELDS = new Set([
  "quoteId",
  "facilitatorAddress",
  "signature",
  "signatureScheme",
  "quoteDigest",
]);

/**
 * Prepares a quote object for signing by stripping non-digestable fields.
 */
export function stripQuoteForSigning(quote: FacilitatorFeeQuote): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(quote).filter(([key]) => !EXCLUDED_QUOTE_FIELDS.has(key))
  );
}

/**
 * Calculates the fee from BPS (basis points), with min/max bounds applied.
 */
export function calculateBpsFee(
  quote: FacilitatorFeeQuote,
  paymentAmount: string
): string {
  if (quote.bps === undefined) {
    throw new Error("Quote bps is required for BPS fee calculation.");
  }

  const amount = BigInt(paymentAmount);
  const bps = BigInt(quote.bps);
  let fee = (amount * bps) / BigInt(10000);

  if (quote.minFee !== undefined) {
    const min = BigInt(quote.minFee);
    if (fee < min) fee = min;
  }

  if (quote.maxFee !== undefined) {
    const max = BigInt(quote.maxFee);
    if (fee > max) fee = max;
  }

  return fee.toString();
}
