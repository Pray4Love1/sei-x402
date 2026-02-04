import { config } from "dotenv";
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";

config();

const app = express();
app.use(express.json());

const facilitator = new HTTPFacilitatorClient({
  url: process.env.FACILITATOR_URL!,
});

app.use(
  paymentMiddleware(
    {
      "GET /weather": {
        scheme: "exact",
        network: "eip155:84532",
        price: "$0.001",
        payTo: process.env.EVM_ADDRESS!,
        facilitatorFees: {
          required: true,
        },
      },
    },
    new x402ResourceServer(facilitator).register(
      "eip155:84532",
      new ExactEvmScheme(),
    ),
  ),
);

app.get("/weather", (_, res) => {
  res.json({ weather: "sunny", temperature: 70 });
});

app.listen(4021, () =>
  console.log("Server running on http://localhost:4021"),
);
