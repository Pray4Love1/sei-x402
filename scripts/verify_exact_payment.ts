import { verifyFacilitatorFeeQuote } from "./facilitator_fee_quote";

export function verifyExactPaymentWithFees({
  payment,
  feeQuote,
  facilitatorAddress,
}) {
  verifyFacilitatorFeeQuote(feeQuote, facilitatorAddress);

  if (payment.accepted.network !== feeQuote.network) {
    throw new Error("Network mismatch");
  }

  if (payment.accepted.scheme !== "exact") {
    throw new Error("Invalid scheme");
  }

  if (BigInt(feeQuote.maxGasFee) <= 0n) {
    throw new Error("Invalid maxGasFee");
  }
}
