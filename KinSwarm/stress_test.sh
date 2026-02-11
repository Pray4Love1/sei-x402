#!/usr/bin/env bash
set -euo pipefail

./KinSwarm/setup.sh

runs="${1:-3}"
for i in $(seq 1 "$runs"); do
  python KinSwarm/simulation/run_simulation.py >/tmp/x402-sim-${i}.log
  python -m KinSwarm.swarm_manager >/tmp/x402-manager-${i}.log

  python - <<'PY'
import csv
import os
from pathlib import Path

ledger = Path('KinSwarm/ledger/x402_settlement_log.csv')
assert ledger.exists(), 'ledger output missing'
rows = list(csv.DictReader(ledger.open()))
assert rows, 'ledger has no rows'
required = {
    'worker','epoch','amount','canonical_payload_hash','signature_scheme',
    'verification_result','timestamp','network','tx_hash'
}
missing = required.difference(rows[0].keys())
assert not missing, f'missing ledger columns: {sorted(missing)}'

expected = {
    n.strip().upper()
    for n in os.getenv('X402_NETWORKS', 'EVM,COSMOS,SOLANA,UTXO').split(',')
    if n.strip()
}
actual = {r['network'].upper() for r in rows}
assert actual == expected, f'network mismatch: expected={sorted(expected)} actual={sorted(actual)}'
assert all(r['verification_result'] == 'True' for r in rows), 'verification failures found'
PY

  echo "[STRESS] pass=${i}/${runs}"
done

echo "[STRESS] completed ${runs} passes"
