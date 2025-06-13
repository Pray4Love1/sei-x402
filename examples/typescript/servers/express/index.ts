import { config } from "dotenv";
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { ExactSvmScheme } from "@x402/svm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";

config();

const evmAddress = process.env.EVM_ADDRESS as `0x${string}`;
const svmAddress = process.env.SVM_ADDRESS;

if (!evmAddress || !svmAddress) {
  console.error("Missing required environment variables");
  process.exit(1);
}

const facilitatorUrl = process.env.FACILITATOR_URL;
if (!facilitatorUrl) {
  console.error("❌ FACILITATOR_URL environment variable is required");
  process.exit(1);
}

const facilitatorClient = new HTTPFacilitatorClient({
  url: facilitatorUrl,
});

const app = express();

app.use(
  paymentMiddleware(
    {
      "GET /weather": {
        // Simple USD-denominated price (preferred upstream pattern)
        price: "$0.001",
        // Example testnet (can be base, sei-testnet, etc.)
        network: "eip155:84532",
        payTo: evmAddress,
      },

      "/premium/*": {
        // Atomic amount example (EIP-712 / Permit-compatible token)
        price: {
          amount: "100000",
          asset: {
            address: "0xabc",
            decimals: 18,
            eip712: {
              name: "WETH",
              version: "1",
            },
          },
        },
        network: "sei-testnet",
      },
    },
    new x402ResourceServer(facilitatorClient)
      .register("eip155:84532", new ExactEvmScheme())
      .register(
        "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1",
        new ExactSvmScheme(),
      ),
  ),
);

app.get("/weather", (req, res) => {
  res.json({
    report: {
      weather: "sunny",
      temperature: 70,
    },
  });
});

app.listen(4021, () => {
  console.log("Server listening at http://localhost:4021");
});
