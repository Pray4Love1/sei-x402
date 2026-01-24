# 🌀 Sei Giga Drop — SeiSync Proof Batching System

This repo delivers a full Codex-compliant batch submission and verification suite for SeiSync Proof
drops. It supports:

- ✅ Deterministic digest sealing
- ✅ Signature + signer verification
- ✅ Proof batching + recursive relay expansion
- ✅ Fully local, MCP-broadcast-ready tooling

---

## ✅ What This Bundle Includes

### 💽 Core Scripts
- `scripts/seal_codex_drop.py` — Seal any payload with signer + digest
- `scripts/verify_codex_drop.py` — Verify payloads, signers, and digests
- `codex/batch_submit.py` — Build batch payloads from one or more drops
- `CodexDropSigner.py` — Thin wrapper around `scripts/seal_codex_drop.py`
- `CodexDropVerifier.py` — Thin wrapper around `scripts/verify_codex_drop.py`
- `SeiSyncProof.sc` — Reference contract for registering sealed digests

### 🔐 Private Key Handling
Use `attribution.key` (hex-encoded private key) or environment var `X402_PRIVATE_KEY`.

---

## 🧩 Prerequisites

- Python 3.10+
- `pip` (or `pipx`)

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## 🧪 End-to-End Flow

### 1) Seal a payload

```bash
python scripts/seal_codex_drop.py exact-flow/handoff.json \
  --private-key-file attribution.key \
  --out exact-flow/handoff.codex.json
```

This computes:

- `codexMetadata.sealDigest` + `sealSignature`
- `facilitatorFeeQuote.quoteDigest` + `signature` + `facilitatorAddress`

### 2) Verify the seal

```bash
python scripts/verify_codex_drop.py exact-flow/handoff.codex.json \
  --expected-signer 0xC145037363FD314EF211C09d7E571286620EC034
```

Expected output:

```
[✓] Codex verified: 0xC145037363FD314EF211C09d7E571286620EC034
[✓] Fee quote verified: 0xC145037363FD314EF211C09d7E571286620EC034
[✓] All seals verified
```

### 3) Optional: batch multiple drops

```bash
python codex/batch_submit.py exact-flow/ \
  --out codex/batch.json
```

---

## 🧪 Example Usage (Quick Reference)

```bash
python scripts/seal_codex_drop.py exact-flow/handoff.json \
  --private-key-file attribution.key \
  --out exact-flow/handoff.codex.json

python scripts/verify_codex_drop.py exact-flow/handoff.codex.json \
  --expected-signer 0xC145...034

python codex/batch_submit.py exact-flow/ \
  --out codex/batch.json
```

`exact-flow/handoff.codex.json` is a template; generate a sealed file with the signer tool before
verification or batching.

---

## 🛟 Troubleshooting

### Missing dependency: eth-account

If you see:

```
Missing dependency: eth-account.
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Signature mismatch

- Ensure the correct private key is used for sealing.
- Ensure `--expected-signer` matches the key that sealed the payload.

---

## 📡 Authors
SeiSync Protocol / Sei Giga Authors
- Reinforced by x402 Proof Chain, KinVault, SoulRelay, and Entropy 3.12

🔗 Attribution hash: `d710b49f...754e5`
