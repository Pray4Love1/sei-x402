import axios from "axios";
import { buildTransferWithAuthorization } from "@x402/evm";

export async function buildExactPayment({
  facilitatorUrl,
  token,
  payTo,
  amount,
  from,
}) {
  const quote = await axios
    .post(`${facilitatorUrl}/facilitator/quote`, {
      network: "eip155:84532",
      scheme: "exact",
      asset: {
        address: token,
        decimals: 6,
      },
    })
    .then((r) => r.data);

  return buildTransferWithAuthorization({
    token,
    from,
    to: payTo,
    value: amount,
    validAfter: Math.floor(Date.now() / 1000),
    validBefore: quote.expiry,
    feeQuote: quote,
  });
}
