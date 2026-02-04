import express from "express";
import { signFacilitatorFeeQuote } from "../facilitator_fee_quote";

export const facilitatorQuoteRouter = express.Router();

facilitatorQuoteRouter.post("/facilitator/quote", async (req, res) => {
  const { network, scheme, asset } = req.body;

  if (!network || scheme !== "exact" || !asset?.address) {
    return res.status(400).json({ error: "Invalid request" });
  }

  const quote = await signFacilitatorFeeQuote(
    {
      network,
      scheme,
      asset,
      maxGasFee: "5000000000000000",
      expiry: Math.floor(Date.now() / 1000) + 60,
    },
    process.env.FACILITATOR_PRIVATE_KEY as `0x${string}`,
  );

  res.json(quote);
});
