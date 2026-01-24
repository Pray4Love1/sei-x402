# CodexGigaDrop

CodexGigaDrop is a small utility suite for preparing, signing, and submitting
Codex drop payloads. It includes:

- **Signing utilities** (`CodexDropSigner.py`, `scripts/seal_codex_drop.py`)
- **Verification utilities** (`CodexDropVerifier.py`, `scripts/verify_codex_drop.py`)
- **Batch submission helper** (`codex/batch_submit.py`)
- **Example handoff payloads** (`exact-flow/`)

> **Note**: These utilities use an HMAC-based signature for local testing and
> integration flows. Replace the signing scheme with a production-grade signer
> if you need verifiable on-chain signatures.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Seal (sign) a handoff payload

```bash
python scripts/seal_codex_drop.py --input exact-flow/handoff.json --output exact-flow/handoff.codex.json
```

### Verify a sealed payload

```bash
python scripts/verify_codex_drop.py --input exact-flow/handoff.codex.json
```

### Submit a batch

```bash
python codex/batch_submit.py --input exact-flow/handoff.codex.json --endpoint https://example.com/api/codex-drops
```

## Environment variables

- `CODEX_DROP_SECRET`: shared HMAC signing secret (required)
- `CODEX_DROP_INPUT`: default input path for signing
- `CODEX_DROP_SIGNED_OUTPUT`: default output path for signed payloads
- `CODEX_GIGADROP_ENDPOINT`: default batch submission endpoint
