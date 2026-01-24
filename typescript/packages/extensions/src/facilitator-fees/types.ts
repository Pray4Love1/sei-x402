export const FACILITATOR_FEES = "facilitatorFees";

export type FeeModel = "flat" | "bps" | "tiered" | "hybrid";
export type SignatureScheme = "eip191" | "ed25519";

export interface FacilitatorFeeQuote {
  quoteId?: string;
  facilitatorAddress: string;
  model: FeeModel;
  asset: string;
  flatFee?: string;
  bps?: number | string;
  minFee?: string;
  maxFee?: string;
  expiry: number;
  signature?: string;
  signatureScheme?: SignatureScheme;
  quoteDigest?: string;
}

export interface FacilitatorFeeBid {
  maxTotalFee: string;
  asset: string;
  selectedQuoteId?: string;
}

export interface FacilitatorFeePaid {
  facilitatorFeePaid: string;
  asset: string;
  quoteId?: string;
  facilitatorId?: string;
  model?: FeeModel;
}

export interface FacilitatorOption {
  /** Stable facilitator identifier (MUST be a valid URL). */
  facilitatorId: string;
  facilitatorFeeQuote?: FacilitatorFeeQuote;
  facilitatorFeeQuoteRef?: string;
  maxFacilitatorFee?: string;
}

export interface FacilitatorFeeOption extends FacilitatorOption {}

export interface FacilitatorFeesPaymentRequiredInfo {
  version: string;
  options: FacilitatorOption[];
}

export interface FacilitatorFeesPaymentPayloadInfo {
  version: string;
  facilitatorFeeBid?: FacilitatorFeeBid;
}

export interface FacilitatorFeesSettlementInfo {
  version: string;
  facilitatorFeePaid?: FacilitatorFeePaid;
}

export interface FacilitatorFeesPaymentRequiredExtension {
  info: FacilitatorFeesPaymentRequiredInfo;
  schema?: Record<string, unknown>;
}

export interface FacilitatorFeesPaymentPayloadExtension {
  info: FacilitatorFeesPaymentPayloadInfo;
}

export interface FacilitatorFeesSettlementExtension {
  info: FacilitatorFeesSettlementInfo;
}
