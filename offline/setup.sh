#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip >/dev/null || true
python -m pip install pycryptodome eth-account web3 >/dev/null || \
  echo "[SETUP] Optional dependency install skipped (offline/proxy environment)."

echo "[SETUP] offline x402 cryptography harness ready"
