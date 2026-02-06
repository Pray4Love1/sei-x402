import { buildFeeQuote, PaymentRequirement } from "../../../core/facilitator-fees";

export type QuoteInput = {
  requirement: PaymentRequirement;
  riskScore: number;
  policyHash: string;
  signature: string;
};

export function getQuote(input: QuoteInput) {
  return buildFeeQuote({
    riskScore: input.riskScore,
    requirement: input.requirement,
    policyHash: input.policyHash,
    signature: input.signature,
  });
}
