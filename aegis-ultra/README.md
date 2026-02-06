# Aegis Ultra (x402)

Aegis Ultra is a security and risk-control blueprint designed to plug into the x402 payment flow using facilitator fee extensions and hooks. The repository keeps executable logic in TypeScript, Go, and Python.

## Structure

- `core/`: shared risk and policy systems (never customer-specific).
- `adapters/`: chain or platform integrations.
- `e2e/`: end-to-end runnable scripts in Python, TypeScript, and Go.
- `legal/`: licensing, attribution, and exclusivity terms.

## Core modules

- **AI risk engine** (`core/ai-risk-engine`): risk scoring + fee pricing for facilitator quotes.
- **Facilitator fee extensions** (`core/facilitator-fees`): TypeScript fee quote + hook enforcement.
- **ZK circuits** (`core/zk-circuits`): TypeScript stubs for fee proof interfaces.
- **PQ crypto** (`core/pq-crypto`): Go stubs for PQ signature verification.
- **Homomorphic** (`core/homomorphic`): Python helpers for encrypted computation primitives.

## End-to-end scripts

- `e2e/e2e.py`: Python flow using custody guards, risk scoring, and fee quote generation.
- `e2e/e2e.ts`: TypeScript flow using x402 quote/authorize/Payment Required hooks.
- `e2e/e2e.go`: Go flow using PQ attestation checks and Sei execution guards.

## Legal

- `legal/LICENSE-COMMERCIAL.txt`: commercial facilitator deployment terms.
- `legal/LICENSE-OSS-ADAPTER.txt`: adapter licensing for open-source distribution.
- `legal/exclusivity.txt`: exclusivity and IP clauses.
- `legal/attribution.txt`: attribution requirements.
