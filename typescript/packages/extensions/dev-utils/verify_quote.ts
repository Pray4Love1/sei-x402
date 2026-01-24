import { verifyMessage, keccak256, toUtf8Bytes, getBytes } from "ethers";
import canonicalize from "json-canonicalize";
import { stripQuoteForSigning } from "../src/facilitator-fees/index.js";

const signatureArgIndex = process.argv.indexOf("--signature");
const signature =
  signatureArgIndex !== -1 ? process.argv[signatureArgIndex + 1] : process.env.SIGNATURE;

const facilitatorArgIndex = process.argv.indexOf("--facilitator-address");
const facilitatorAddress =
  facilitatorArgIndex !== -1
    ? process.argv[facilitatorArgIndex + 1]
    : process.env.FACILITATOR_ADDRESS;

if (!signature) {
  throw new Error("Signature is required (set SIGNATURE or --signature).");
}

if (!facilitatorAddress) {
  throw new Error("Facilitator address is required (set FACILITATOR_ADDRESS or --facilitator-address)." );
}

const quote = {
  quoteId: "quote_abc123",
  facilitatorAddress,
  model: "flat",
  asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  flatFee: "1000",
  expiry: 9999999999,
};

const signingPayload = stripQuoteForSigning(quote);
const canonical = canonicalize(signingPayload);
const hash = keccak256(toUtf8Bytes(canonical));
const recovered = verifyMessage(getBytes(hash), signature);

console.log("Recovered:", recovered);
console.log("Match:", recovered.toLowerCase() === facilitatorAddress.toLowerCase());
