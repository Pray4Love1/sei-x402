"""Global policy and controls for X402Swarm simulation."""

from __future__ import annotations

import os

OPERATOR_KEY_PATH = "KinSwarm/offline/operator.key"
PAYROLL_EPOCH = "2026-02-epoch-01"

MAX_SHARD_SIZE = 5000
MAX_CONCURRENT_SHARDS = 50
DEFAULT_NETWORKS = [n.strip().upper() for n in os.getenv("X402_NETWORKS", "EVM,COSMOS,SOLANA,UTXO").split(",") if n.strip()]

PAY_FREQUENCY = "biweekly"
