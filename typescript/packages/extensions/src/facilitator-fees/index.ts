/**
 * Facilitator Fees Extension for x402 v2
 *
 * Enables fee-aware multi-facilitator routing by standardizing:
 * - FacilitatorFeeQuote: Facilitator fee disclosure at PaymentRequired time
 * - FacilitatorFeeBid: Client fee constraints in PaymentPayload
 * - FacilitatorFeePaid: Actual fee charged in SettlementResponse
 *
 * ## Usage
 *
 * ### For Resource Servers (declaring fee options)
 *
 * ```typescript
 * import {
 *   declareFacilitatorFeesExtension,
 *   FACILITATOR_FEES
 * } from '@x402/extensions/facilitator-fees';
 *
 * const extension = declareFacilitatorFeesExtension([
 *   {
 *     facilitatorId: "https://x402.org/facilitator",
 *     facilitatorFeeQuote: {
 *       quoteId: "quote_123",
 *       model: "flat",
 *       asset: "0x...",
 *       flatFee: "1000",
 *       expiry: Date.now() / 1000 + 3600,
 *       signature: "0x...",
 *       signatureScheme: "eip191"
 *     }
 *   }
 * ]);
 *
 * // Include in PaymentRequired
 * const paymentRequired = {
 *   x402Version: 2,
 *   resource: { ... },
 *   accepts: [ ... ],
 *   extensions: {
 *     [FACILITATOR_FEES]: extension
 *   }
 * };
 * ```
 *
 * ### For Clients (expressing fee constraints)
 *
 * ```typescript
 * import {
 *   createFacilitatorFeeBid,
 *   FACILITATOR_FEES
 * } from '@x402/extensions/facilitator-fees';
 *
 * const bid = createFacilitatorFeeBid({
 *   maxTotalFee: "2000",
 *   asset: "0x...",
 *   selectedQuoteId: "quote_123"
 * });
 *
 * // Include in PaymentPayload
 * const paymentPayload = {
 *   ...payload,
 *   extensions: {
 *     [FACILITATOR_FEES]: bid
 *   }
 * };
 * ```
 *
 * ### For Facilitators/Servers (reporting fees paid)
 *
 * ```typescript
 * import {
 *   createFacilitatorFeePaid,
 *   FACILITATOR_FEES
 * } from '@x402/extensions/facilitator-fees';
 *
 * const feePaid = createFacilitatorFeePaid({
 *   facilitatorFeePaid: "1000",
 *   asset: "0x...",
 *   quoteId: "quote_123",
 *   facilitatorId: "https://x402.org/facilitator"
 * });
 *
 * // Include in SettlementResponse
 * const settlementResponse = {
 *   ...response,
 *   extensions: {
 *     [FACILITATOR_FEES]: feePaid
 *   }
 * };
 * ```
 */

import {
  FacilitatorFeesPaymentRequiredInfoSchema,
  FacilitatorFeesPaymentPayloadInfoSchema,
  FacilitatorFeesSettlementInfoSchema,
  FACILITATOR_FEES_PAYMENT_REQUIRED_JSON_SCHEMA,
} from "./schema";

import type {
  FacilitatorOption,
  FacilitatorFeeBid,
  FacilitatorFeesPaymentRequiredExtension,
  FacilitatorFeesPaymentPayloadExtension,
  FacilitatorFeesSettlementExtension,
  FacilitatorFeesSettlementInfo,
} from "./types";

// Re-export types
export type {
  FeeModel,
  SignatureScheme,
  FacilitatorFeeQuote,
  FacilitatorOption,
  FacilitatorFeeBid,
  FacilitatorFeePaid,
  FacilitatorFeesPaymentRequiredInfo,
  FacilitatorFeesPaymentPayloadInfo,
  FacilitatorFeesSettlementInfo,
  FacilitatorFeesPaymentRequiredExtension,
  FacilitatorFeesPaymentPayloadExtension,
  FacilitatorFeesSettlementExtension,
} from "./types";

export { FACILITATOR_FEES } from "./types";

// Re-export schemas
export {
  FeeModelSchema,
  SignatureSchemeSchema,
  FacilitatorFeeQuoteSchema,
  FacilitatorOptionSchema,
  FacilitatorFeeBidSchema,
  FacilitatorFeesPaymentRequiredInfoSchema,
  FacilitatorFeesPaymentPayloadInfoSchema,
  FacilitatorFeesSettlementInfoSchema,
  FACILITATOR_FEES_PAYMENT_REQUIRED_JSON_SCHEMA,
} from "./schema";

export {
  isQuoteExpired,
  findOptionByQuoteId,
  filterOptionsByMaxFee,
  calculateBpsFee,
  calculateFee,
  getCanonicalQuotePayload,
  verifyQuoteSignatureEip191,
  verifySettlementMatchesSelection,
  canCompareForFeeRouting,
  validateBpsQuoteHasMaxFee,
  InvalidFeeQuoteError,
} from "./utils";

/**
 * Create a facilitator fees extension for PaymentRequired
 *
 * @param options - Array of facilitator options with fee quotes
 * @returns Extension object to include in PaymentRequired.extensions
 */
export function declareFacilitatorFeesExtension(
  options: FacilitatorOption[],
): FacilitatorFeesPaymentRequiredExtension {
  const info = { version: "1" as const, options };

  // Validate
  FacilitatorFeesPaymentRequiredInfoSchema.parse(info);

  return {
    info,
    schema: FACILITATOR_FEES_PAYMENT_REQUIRED_JSON_SCHEMA,
  };
}

/**
 * Create a facilitator fee bid for PaymentPayload
 *
 * @param bid - Client fee constraints
 * @returns Extension object to include in PaymentPayload.extensions
 */
export function createFacilitatorFeeBid(
  bid: FacilitatorFeeBid,
): FacilitatorFeesPaymentPayloadExtension {
  const info = { version: "1" as const, facilitatorFeeBid: bid };

  // Validate
  FacilitatorFeesPaymentPayloadInfoSchema.parse(info);

  return { info };
}

/**
 * Create a facilitator fee paid extension for SettlementResponse
 *
 * @param feePaid - Fee payment details
 * @returns Extension object to include in SettlementResponse.extensions
 */
export function createFacilitatorFeePaid(
  feePaid: Omit<FacilitatorFeesSettlementInfo, "version">,
): FacilitatorFeesSettlementExtension {
  const info: FacilitatorFeesSettlementInfo = { version: "1", ...feePaid };

  // Validate
  FacilitatorFeesSettlementInfoSchema.parse(info);

  return { info };
}

/**
 * Extract facilitator fees extension from PaymentRequired
 *
 * @param paymentRequired - PaymentRequired object with extensions
 * @param paymentRequired.extensions - Extensions map
 * @returns Parsed extension info or undefined if not present/invalid
 */
export function extractFacilitatorFeesFromPaymentRequired(paymentRequired: {
  extensions?: Record<string, unknown>;
}): FacilitatorFeesPaymentRequiredExtension["info"] | undefined {
  const ext = paymentRequired.extensions?.["facilitatorFees"] as { info?: unknown } | undefined;
  if (!ext?.info) return undefined;

  const result = FacilitatorFeesPaymentRequiredInfoSchema.safeParse(ext.info);
  return result.success ? result.data : undefined;
}

/**
 * Extract facilitator fee bid from PaymentPayload
 *
 * @param paymentPayload - PaymentPayload object with extensions
 * @param paymentPayload.extensions - Extensions map
 * @returns Parsed fee bid or undefined if not present/invalid
 */
export function extractFacilitatorFeeBid(paymentPayload: {
  extensions?: Record<string, unknown>;
}): FacilitatorFeeBid | undefined {
  const ext = paymentPayload.extensions?.["facilitatorFees"] as { info?: unknown } | undefined;
  if (!ext?.info) return undefined;

  const result = FacilitatorFeesPaymentPayloadInfoSchema.safeParse(ext.info);
  return result.success ? result.data.facilitatorFeeBid : undefined;
}

/**
 * Extract facilitator fee paid from SettlementResponse
 *
 * @param settlementResponse - SettlementResponse object with extensions
 * @param settlementResponse.extensions - Extensions map
 * @returns Parsed fee paid info or undefined if not present/invalid
 */
export function extractFacilitatorFeePaid(settlementResponse: {
  extensions?: Record<string, unknown>;
}): FacilitatorFeesSettlementInfo | undefined {
  const ext = settlementResponse.extensions?.["facilitatorFees"] as { info?: unknown } | undefined;
  if (!ext?.info) return undefined;

  const result = FacilitatorFeesSettlementInfoSchema.safeParse(ext.info);
  return result.success ? result.data : undefined;
}
