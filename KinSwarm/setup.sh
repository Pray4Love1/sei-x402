#!/usr/bin/env bash
set -euo pipefail

# Local-only setup for x402-native simulation.
if [ ! -f KinSwarm/offline/operator.key ]; then
  mkdir -p KinSwarm/offline
  echo "bootstrap-local-signer-key" > KinSwarm/offline/operator.key
fi

python -m compileall KinSwarm offline simulation soul_sync swarm adapters >/dev/null
python -m unittest discover -s KinSwarm/tests -p 'test_*.py' >/dev/null

echo "[SETUP] x402 runtime workspace ready"
