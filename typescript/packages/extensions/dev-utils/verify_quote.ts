import { readFileSync } from "node:fs";
import { createPublicKey, verify as verifyMessage } from "node:crypto";
import { argv, exit } from "node:process";

import { getCanonicalQuotePayload } from "../src/facilitator-fees";
import type { FacilitatorFeeQuote } from "../src/facilitator-fees";

const inputIndex = argv.indexOf("--input");
const keyIndex = argv.indexOf("--public-key");

const inputPath = inputIndex !== -1 ? argv[inputIndex + 1] : "quote.signed.json";
const publicKeyPem = keyIndex !== -1 ? argv[keyIndex + 1] : process.env.FACILITATOR_PUBLIC_KEY;

if (!inputPath) {
  console.error("Missing value for --input");
  exit(1);
}

if (!publicKeyPem) {
  console.error("Missing public key. Set FACILITATOR_PUBLIC_KEY or pass --public-key.");
  exit(1);
}

const quote = JSON.parse(readFileSync(inputPath, "utf-8")) as FacilitatorFeeQuote;

if (quote.signatureScheme !== "ed25519") {
  console.error(`Unsupported signature scheme: ${quote.signatureScheme}`);
  exit(1);
}

const signatureHex = quote.signature.startsWith("0x") ? quote.signature.slice(2) : quote.signature;
const signature = Buffer.from(signatureHex, "hex");
const canonicalPayload = getCanonicalQuotePayload(quote);

const valid = verifyMessage(
  null,
  Buffer.from(canonicalPayload),
  createPublicKey(publicKeyPem),
  signature,
);

if (!valid) {
  console.error("Signature invalid");
  exit(1);
}

console.log("Signature valid");
