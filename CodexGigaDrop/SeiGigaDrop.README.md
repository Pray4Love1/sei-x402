{
  "name": "Sei GigaDrop",
  "description": "End-to-end workflow for sealing, verifying, and batching Sei x402 drops with optional facilitator fee extensions.",
  "version": "1.0",
  "author": "Pray4Love1",
  "steps": [
    {
      "step": 1,
      "title": "Seal Sei Drop",
      "description": "Seal your raw JSON payload (`handoff.json`) into a cryptographically signed Sei drop using your private key.",
      "command": "python3 scripts/seal_codex_drop.py exact-flow/handoff.json --private-key-file attribution.key --out exact-flow/handoff.codex.json"
    },
    {
      "step": 2,
      "title": "Verify Sei Signature and Facilitator Fees",
      "description": "Verify the Sei signature and embedded facilitator fee quote against the expected signer address.",
      "command": "python3 scripts/verify_codex_drop.py exact-flow/handoff.codex.json --expected-signer 0xC145037363FD314EF211C09d7E571286620EC034"
    },
    {
      "step": 3,
      "title": "Batch the Drop for Submission",
      "description": "Bundle one or more signed Sei files into a batch payload for submission to downstream agents, servers, or chain endpoints.",
      "command": "python3 codex/batch_submit.py exact-flow/ --out codex/batch.json"
    },
    {
      "step": 4,
      "title": "Inspect or Broadcast",
      "description": "View the generated batch.json manually or prepare to broadcast to Sei/MCP/x402 relay endpoints.",
      "command": "cat codex/batch.json"
    }
  ],
  "fileStructure": {
    "exact-flow/": [
      "handoff.json",
      "handoff.codex.json"
    ],
    "scripts/": [
      "seal_codex_drop.py",
      "verify_codex_drop.py"
    ],
    "codex/": [
      "batch.json",
      "batch_submit.py"
    ]
  },
  "output": {
    "codexMetadata": {
      "signer": "0xC145037363FD314EF211C09d7E571286620EC034",
      "sealDigest": "3e462a2ba1ccc4bc43e0db7b4b905bd799fa5df7c2bb19fdde31e8b31cfde0ef",
      "signatureScheme": "eip191",
      "facilitatorId": "https://solarakin.org/facilitators/x402"
    },
    "batchSummary": {
      "items": 4,
      "source": "SeiGigaDrop",
      "timestamp": "1769280788"
    }
  },
  "note": "This JSON README is machine-readable and can be used to power a UI, CLI helper, or MCP endpoint docs."
}
