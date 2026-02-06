# CodexDrop Multi-Chain Royalty Enforcement Kit

This kit provides chain-agnostic Solidity contracts and helper scripts to enforce Codex drop hashes across multiple EVM networks.

## Contents

- `contracts/CodexDropVerifier.sol` — Immutable, per-chain hash verifier.
- `contracts/CodexDropRegistry.sol` — Mapping-based registry keyed by `chainId`.
- `scripts/verify_codex_hash.py` — Deterministic JSON hash helper (keccak by default).
- `scripts/deploy_codex_drop_verifier.py` — Deploy the verifier from a compiled artifact.
- `scripts/deploy_codex_drop_registry.py` — Deploy the registry from a compiled artifact.

## Generate a Codex drop hash

```bash
python royalty_enforcement/scripts/verify_codex_hash.py codex_drop.json \
  --json-path paymentPayload \
  --algorithm keccak
```

To hash the entire drop instead of a JSON path, omit `--json-path`.

## Compile contracts

Use Foundry (example):

```bash
forge build --root royalty_enforcement
```

This should produce artifacts with `abi` and `bytecode` fields.

## Deploy CodexDropVerifier

```bash
python royalty_enforcement/scripts/deploy_codex_drop_verifier.py \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --artifact path/to/CodexDropVerifier.json \
  --drop-hash 0xabc123...
```

## Deploy CodexDropRegistry

```bash
python royalty_enforcement/scripts/deploy_codex_drop_registry.py \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --artifact path/to/CodexDropRegistry.json
```

## Tests

```bash
python -m unittest royalty_enforcement/tests/test_verify_codex_hash.py
```
