import { buildFeeQuote, PaymentRequirement } from "../core/facilitator-fees";
import { authorizePayment } from "../adapters/coinbase-x402/agent-hooks/authorize";
import { getQuote } from "../adapters/coinbase-x402/agent-hooks/quote";
import { paymentRequired } from "../adapters/coinbase-x402/agent-hooks/payment_required";
import { runPreSettle } from "../adapters/coinbase-x402/agent-hooks";
import { requestFeeProof } from "../core/zk-circuits";

const requirement: PaymentRequirement = {
  resource: "x402://checkout/alpha",
  amount: "12500",
  asset: "USDC",
  network: "base",
};

const riskScore = 0.83;
const policyHash = "policy-hash";
const signature = "ai-signature";

const quote = getQuote({ requirement, riskScore, policyHash, signature });

const fallbackQuote = buildFeeQuote({
  requirement,
  riskScore,
  policyHash,
  signature,
});

const paymentResponse = paymentRequired(quote);

const authorized = authorizePayment(
  { memo: quote.quoteId, txHash: "0xabc" },
  quote,
);

runPreSettle({
  requirement,
  feeQuote: fallbackQuote,
  facilitator: {
    facilitatorId: "x402-demo",
    feeBps: 35,
    settlementNetwork: "base",
  },
});

const proof = requestFeeProof({
  paymentPayloadHash: "0xfee",
  feeBps: quote.totalFeeBps,
  facilitatorId: "x402-demo",
});

console.log(
  JSON.stringify(
    { requirement, quote, paymentResponse, authorized, proof },
    null,
    2,
  ),
);
