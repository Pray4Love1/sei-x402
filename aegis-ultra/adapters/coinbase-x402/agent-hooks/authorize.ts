import { FeeQuote } from "../../../core/facilitator-fees";

export type PaymentProof = {
  memo: string;
  txHash: string;
};

export function authorizePayment(proof: PaymentProof, quote: FeeQuote): boolean {
  return proof.memo === quote.quoteId;
}
