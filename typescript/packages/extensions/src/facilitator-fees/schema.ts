import { z } from "zod";
import type { FacilitatorFeesPaymentRequiredExtension } from "./types.js";

export const FeeModelSchema = z.enum(["flat", "bps", "tiered", "hybrid"]);
export const SignatureSchemeSchema = z.enum(["eip191", "ed25519"]);

export const FacilitatorFeeQuoteSchema = z.object({
  quoteId: z.string().optional(),
  facilitatorAddress: z.string(),
  model: FeeModelSchema,
  asset: z.string(),
  flatFee: z.string().optional(),
  bps: z.union([z.string(), z.number().int()]).optional(),
  minFee: z.string().optional(),
  maxFee: z.string().optional(),
  expiry: z.number().int(),
  signature: z.string().optional(),
  signatureScheme: SignatureSchemeSchema.optional(),
  quoteDigest: z.string().optional(),
});

export const FacilitatorOptionSchema = z.object({
  facilitatorId: z.string().url(),
  facilitatorFeeQuote: FacilitatorFeeQuoteSchema.optional(),
  facilitatorFeeQuoteRef: z.string().url().optional(),
  maxFacilitatorFee: z.string().optional(),
});

export const FacilitatorFeeBidSchema = z.object({
  maxTotalFee: z.string(),
  asset: z.string(),
  selectedQuoteId: z.string().optional(),
});

export const FacilitatorFeePaidSchema = z.object({
  facilitatorFeePaid: z.string(),
  asset: z.string(),
  quoteId: z.string().optional(),
  facilitatorId: z.string().optional(),
  model: FeeModelSchema.optional(),
});

export const FacilitatorFeesPaymentRequiredInfoSchema = z.object({
  version: z.string(),
  options: z.array(FacilitatorOptionSchema),
});

export const FacilitatorFeesPaymentPayloadInfoSchema = z.object({
  version: z.string(),
  facilitatorFeeBid: FacilitatorFeeBidSchema.optional(),
});

export const FacilitatorFeesSettlementInfoSchema = z.object({
  version: z.string(),
  facilitatorFeePaid: FacilitatorFeePaidSchema.optional(),
});

export const FACILITATOR_FEES_PAYMENT_REQUIRED_JSON_SCHEMA = {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  type: "object",
  properties: {
    version: { type: "string" },
    options: { type: "array" },
  },
  required: ["version", "options"],
};

export const FacilitatorFeesPaymentRequiredExtensionSchema = z.object({
  info: FacilitatorFeesPaymentRequiredInfoSchema,
  schema: z.record(z.unknown()).optional(),
});

export function parseFacilitatorFeesExtension(
  value: unknown,
): FacilitatorFeesPaymentRequiredExtension {
  return FacilitatorFeesPaymentRequiredExtensionSchema.parse(value);
}
