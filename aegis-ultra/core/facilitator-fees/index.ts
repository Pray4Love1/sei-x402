export type FacilitatorMetadata = {
  facilitatorId: string;
  feeBps: number;
  settlementNetwork: string;
};

export type PaymentRequirement = {
  resource: string;
  amount: string;
  asset: string;
  network: string;
};

export type FeeQuote = {
  quoteId: string;
  asset: string;
  amount: string;
  riskScore: number;
  baseFeeBps: number;
  riskFeeBps: number;
  totalFeeBps: number;
  expiresAt: number;
  policyHash: string;
  signature: string;
};

export type FeeQuoteInput = {
  riskScore: number;
  requirement: PaymentRequirement;
  policyHash: string;
  signature: string;
};

export function buildFeeQuote(input: FeeQuoteInput): FeeQuote {
  const baseFeeBps = 10;
  const riskFeeBps = Math.min(90, Math.floor(input.riskScore * 50));

  return {
    quoteId: crypto.randomUUID(),
    asset: input.requirement.asset,
    amount: input.requirement.amount,
    riskScore: input.riskScore,
    baseFeeBps,
    riskFeeBps,
    totalFeeBps: baseFeeBps + riskFeeBps,
    expiresAt: Math.floor(Date.now() / 1000) + 300,
    policyHash: input.policyHash,
    signature: input.signature,
  };
}

export type FeeHookContext = {
  requirement: PaymentRequirement;
  metadata: FacilitatorMetadata;
  feeQuote: FeeQuote;
};

export function preSettleHook(context: FeeHookContext): void {
  if (Number(context.feeQuote.amount) <= 0) {
    throw new Error("invalid facilitator amount");
  }

  if (context.feeQuote.totalFeeBps <= 0) {
    throw new Error("invalid facilitator fee");
  }

  if (context.feeQuote.expiresAt < Math.floor(Date.now() / 1000)) {
    throw new Error("fee quote expired");
  }
}
