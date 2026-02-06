import { FeeQuote } from "../../../core/facilitator-fees";

export type PaymentRequiredResponse = {
  code: number;
  message: string;
  facilitatorFeeQuote: FeeQuote;
  paymentInstructions: {
    chain: string;
    recipient: string;
    denom: string;
    memo: string;
  };
};

export function paymentRequired(quote: FeeQuote): PaymentRequiredResponse {
  return {
    code: 402,
    message: "Payment Required",
    facilitatorFeeQuote: quote,
    paymentInstructions: {
      chain: "sei",
      recipient: process.env.FACILITATOR_ADDR ?? "sei1facilitator",
      denom: "usei",
      memo: quote.quoteId,
    },
  };
}
