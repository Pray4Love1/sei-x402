import { readFileSync, writeFileSync } from "node:fs";
import { createHash, createPrivateKey, sign as signMessage } from "node:crypto";
import { argv, exit } from "node:process";

import { getCanonicalQuotePayload } from "../src/facilitator-fees";
import type { FacilitatorFeeQuote } from "../src/facilitator-fees";

const inputIndex = argv.indexOf("--input");
const outputIndex = argv.indexOf("--output");
const keyIndex = argv.indexOf("--private-key");

const inputPath = inputIndex !== -1 ? argv[inputIndex + 1] : "quote.json";
const outputPath = outputIndex !== -1 ? argv[outputIndex + 1] : "quote.signed.json";
const privateKeyPem =
  keyIndex !== -1 ? argv[keyIndex + 1] : process.env.FACILITATOR_PRIVATE_KEY;

if (!inputPath) {
  console.error("Missing value for --input");
  exit(1);
}

if (!outputPath) {
  console.error("Missing value for --output");
  exit(1);
}

if (!privateKeyPem) {
  console.error("Missing signing key. Set FACILITATOR_PRIVATE_KEY or pass --private-key.");
  exit(1);
}

const quote = JSON.parse(readFileSync(inputPath, "utf-8")) as FacilitatorFeeQuote;

const canonicalPayload = getCanonicalQuotePayload(quote);
const payloadHash = createHash("sha256").update(canonicalPayload).digest();
const signatureBytes = signMessage(null, payloadHash, createPrivateKey(privateKeyPem));

const signedQuote: FacilitatorFeeQuote = {
  ...quote,
  signature: `0x${signatureBytes.toString("hex")}`,
  signatureScheme: "ed25519",
};

writeFileSync(outputPath, `${JSON.stringify(signedQuote, null, 2)}\n`);
console.log(`Signed quote written to ${outputPath}`);
