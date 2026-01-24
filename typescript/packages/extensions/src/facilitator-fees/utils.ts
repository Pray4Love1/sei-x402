import type { FacilitatorFeeQuote } from "./types.js";

export const EXCLUDED_QUOTE_FIELDS = new Set([
  "quoteId",
  "facilitatorAddress",
  "signature",
  "signatureScheme",
  "quoteDigest",
]);

export function stripQuoteForSigning(quote: FacilitatorFeeQuote): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(quote).filter(([key]) => !EXCLUDED_QUOTE_FIELDS.has(key)),
  );
}

export function calculateBpsFee(quote: FacilitatorFeeQuote, paymentAmount: string): string {
  if (!quote.bps) {
    throw new Error("Quote bps is required for BPS fee calculation.");
  }

  const amount = BigInt(paymentAmount);
  const bps = BigInt(quote.bps);

  // Calculate raw BPS fee with floor rounding (BigInt division truncates toward zero).
  let fee = (amount * bps) / BigInt(10000);

  if (quote.minFee) {
    const minFee = BigInt(quote.minFee);
    if (fee < minFee) {
      fee = minFee;
    }
  }

  if (quote.maxFee) {
    const maxFee = BigInt(quote.maxFee);
    if (fee > maxFee) {
      fee = maxFee;
    }
  }

  return fee.toString();
}
