# x402 Native Runtime Kit

`KinSwarm/` is a Python-first x402 runtime designed for deterministic offline settlement simulation.

## What is included

- **Protocol-conformance adapter** for canonical `X-PAYMENT` and `X-PAYMENT-RESPONSE` mappings.
- **Strict signature verification** (no permissive fallback validation).
- **Universal multi-network rails** with first-class adapters for `EVM`, `COSMOS`, `SOLANA`, and `UTXO`.
- **Audit ledger schema** with worker, epoch, amount, canonical payload hash, signature scheme, verification result, and timestamp.
- **Assertion-based stress tests** that fail on invariants.
- **x402 conformance test suite** with golden vectors.

## Quickstart

```bash
./KinSwarm/setup.sh
./KinSwarm/startup.sh
```

## Standalone simulation

```bash
python KinSwarm/simulation/run_simulation.py
```

## Stress test

```bash
./KinSwarm/stress_test.sh 3
```

## Configuration

- `X402_NETWORKS` controls active rails. Default: `EVM,COSMOS,SOLANA,UTXO`.
- `KinSwarm/config.py` holds shard/concurrency policy.

## Output

- Ledger file: `KinSwarm/ledger/x402_settlement_log.csv`

## License

MIT (see `KinSwarm/LICENSE`).
