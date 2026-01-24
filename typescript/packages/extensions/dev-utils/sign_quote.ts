import { Wallet, keccak256, toUtf8Bytes, getBytes } from "ethers";
import canonicalize from "json-canonicalize";
import { stripQuoteForSigning } from "../src/facilitator-fees/index.js";

const PRIVATE_KEY = process.env.SIGNER_KEY;

if (!PRIVATE_KEY) {
  throw new Error("SIGNER_KEY is required (hex-encoded private key).");
}

const wallet = new Wallet(PRIVATE_KEY);

const quote = {
  quoteId: "quote_abc123",
  facilitatorAddress: wallet.address,
  model: "flat",
  asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  flatFee: "1000",
  expiry: Math.floor(Date.now() / 1000) + 3600,
};

const signingPayload = stripQuoteForSigning(quote);
const canonical = canonicalize(signingPayload);
const hash = keccak256(toUtf8Bytes(canonical));
const signature = await wallet.signMessage(getBytes(hash));

const signedQuote = {
  ...quote,
  signature,
  signatureScheme: "eip191",
};

console.log("Quote:", signedQuote);
console.log("Canonical:", canonical);
console.log("Signature:", signature);
