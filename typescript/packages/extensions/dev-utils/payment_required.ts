import { declareFacilitatorFeesExtension } from "../src/facilitator-fees/index.js";

const quote = {
  quoteId: "quote_abc123",
  facilitatorAddress: "0xabc1230000000000000000000000000000000000",
  model: "flat",
  asset: "0xfee1230000000000000000000000000000000000",
  flatFee: "1000",
  expiry: Math.floor(Date.now() / 1000) + 600,
  signature: "0xSIG_FROM_SIGNER",
  signatureScheme: "eip191",
};

const paymentRequired = {
  x402Version: 2,
  error: "Payment required",
  resource: {
    url: "https://api.example.com/premium-data",
    description: "Premium API access",
    mimeType: "application/json",
  },
  extensions: {
    facilitatorFees: declareFacilitatorFeesExtension([
      {
        facilitatorId: "https://yourdomain.com/facilitator",
        facilitatorFeeQuote: quote,
      },
    ]),
  },
};

console.log(JSON.stringify(paymentRequired, null, 2));
