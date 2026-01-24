import { writeFileSync } from "node:fs";
import { argv, exit } from "node:process";

import { declareFacilitatorFeesExtension, FACILITATOR_FEES } from "../src/facilitator-fees";

const outputIndex = argv.indexOf("--output");
const outputPath = outputIndex !== -1 ? argv[outputIndex + 1] : "payment-required.json";

if (outputIndex !== -1 && !outputPath) {
  console.error("Missing value for --output");
  exit(1);
}

const extension = declareFacilitatorFeesExtension([
  {
    facilitatorId: "https://x402.org/facilitator",
    facilitatorFeeQuote: {
      quoteId: "quote_abc123",
      facilitatorAddress: "0x1234567890abcdef1234567890abcdef12345678",
      model: "flat",
      asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      flatFee: "1000",
      expiry: Math.floor(Date.now() / 1000) + 3600,
      signature: "0x",
      signatureScheme: "eip191",
    },
  },
]);

const paymentRequired = {
  x402Version: 2,
  accepts: [
    {
      scheme: "exact",
      network: "base-sepolia",
      asset: "USDC",
      payTo: "0x0000000000000000000000000000000000000000",
      amount: "1000000",
      resource: "/example",
      maxTimeoutSeconds: 30,
    },
  ],
  extensions: {
    [FACILITATOR_FEES]: extension,
  },
};

writeFileSync(outputPath, `${JSON.stringify(paymentRequired, null, 2)}\n`);
console.log(`PaymentRequired written to ${outputPath}`);
