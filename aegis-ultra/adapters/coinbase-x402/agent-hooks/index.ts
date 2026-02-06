import { preSettleHook } from "../../../core/facilitator-fees";
import type { FeeQuote, PaymentRequirement } from "../../../core/facilitator-fees";

export type HookInput = {
  requirement: PaymentRequirement;
  feeQuote: FeeQuote;
  facilitator: {
    facilitatorId: string;
    feeBps: number;
    settlementNetwork: string;
  };
};

export function runPreSettle(input: HookInput): void {
  preSettleHook({
    requirement: input.requirement,
    metadata: input.facilitator,
    feeQuote: input.feeQuote,
  });
}
