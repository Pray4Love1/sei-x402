# x402_kernel_codexdrop_v1 — 🔒 Final Sovereign Drop (FULL E2E)

> Kin-authored. Codex-sealed. Fully autonomous. No 0x confusion.

## ✅ Unified Sovereign Runtime

This drop includes every finalized micro and macro layer required to run the **x402 Kernel**:

- 🎯 GenZK wallet creation
- 🔐 CipherWord + Guardian-derived entropy
- 🔁 Ephemeral SessionKey rotation
- 🧠 CodexSig / KinSig signing
- 🛡 Omega Guardian runtime logic
- 🌐 Nova relay & MCP router
- 📡 Base44 metadata routing
- 🏦 Vault contracts (Receive-only, Sweeping, Replay protection)
- 💓 Holo biometric & mood enforcement
- 📓 Jupyter private ledger + heartbeat log
- 🔎 ZK login proof (PIN/entropy)
- 📜 x402 payment schema (JSON-Schema compliant)
- 🧪 Deployment scripts + agents

## 🧱 Full Folder Structure

```
x402_kernel_codexdrop_v1/
├── cli/
│   ├── create_wallet.py              # Entropy-based wallet
│   ├── sign_tx.py                    # Sovereign signing tool
│   ├── rotate_key.py                 # Session key rotator
│   ├── holo_gatekeeper.py            # Biometric + mood validator
│   ├── nova_relay.py                 # CLI interface to MCP
├── lib/
│   ├── entropy_utils.py              # Username/PIN/Guardian → entropy
│   ├── wallet_deriver.py             # BIP44 wallet logic
│   ├── sovereign_signer.py           # CodexSig / KinSig modular signer
│   ├── sessionkey_manager.py         # Rotating ephemeral keys
├── base44/
│   └── identity_metadata.json        # Sovereign identity registry entry
├── contracts/
│   ├── ReceivingVault.sol            # Immutable receive vault
│   ├── SpendingSweeper.sol           # One-time TX key + sweeper
│   ├── VaultReplayBlocker.sol        # Prevents TX replay abuse
│   ├── OmegaHooks.sol                # Guardian check onchain modifiers
├── zk/
│   └── prove_pin.zok                 # Groth16-style ZK pin verification
├── guardian/
│   ├── omega_guardian.py             # Guardian runtime (mood, biometrics)
│   ├── heartbeat_watchdog.py         # Jupyter enforcement hook
│   ├── vault_hooks.sol               # Solidity plug-in guard layer
├── agents/
│   ├── kin_agent.py                  # KinVault tx signer
│   ├── codex_agent.py                # Codex-based relay signer
│   └── nova_agent.py                 # MCP + handle resolution
├── schemas/
│   └── x402_payment_payload.json     # Finalized schema for x402 relay
├── jupyter/
│   ├── state_log.ipynb               # Notebook-stored proof + entropy anchor
│   └── jupyter_log_heartbeat.sh      # Local heartbeat ledger
├── deploy/
│   ├── forge.deploy.ts               # Forge deploy script
│   └── deploy_vault.sh               # Bash deploy to local or mainnet
├── ui/
│   ├── protocol_manager_layers.json  # UI layer spec from protocol manager view
│   └── protocol_manager_layers.py    # Script to regenerate the layer spec
└── README.md                         # Final protocol summary
```

## 🔓 Sovereign Flow Recap

1. `create_wallet.py`
   - Derives entropy from: `@handle`, `PIN`, `Guardians`, and optional salt
   - Generates deterministic mnemonic + seed
   - First address = fixed **receive-only** vault

2. `sign_tx.py` + `rotate_key.py`
   - Derive ephemeral address from `m/44'/60'/0'/0/i`
   - Sign using CodexSig / KinSig
   - Rotate to next index and wipe key post-send

3. `nova_agent.py` / `codex_agent.py`
   - MCP relay for resolving `@handle → metadata`
   - Pushes x402 payload with full schema-compliant proof

4. `omega_guardian.py`
   - Enforces biometric + mood thresholds
   - Syncs to `jupyter/state_log.ipynb`
   - Optional: blocks rotation if biometric proof fails

5. `vault_hooks.sol`
   - Solidity modifiers for in-contract Guardian enforcement

6. `zk/prove_pin.zok`
   - Zero-knowledge PIN unlock (Groth16-ready)
   - Optional onchain verifier or local verifier

7. `schemas/x402_payment_payload.json`
   - Fully schema'd relay format for trustless agent TX
   - Used by Nova, Codex, Kin relays

8. `deploy/`
   - Local deploy tools (Forge, Bash)
   - Easily pin `receiveVault` to chain and route to Base44

## 🧬 Ready for

- 🔁 SessionKey replay detection
- 🛡 Sovereign identity proof submission
- 🔓 Biometric TX gating
- 🌐 Multi-agent compatibility
- 📜 Full integration with KinVault, SolaraKin, SeiContrib

## 🧪 Quick Start (Local)

```bash
cd x402_kernel_codexdrop_v1
python cli/create_wallet.py
python cli/sign_tx.py
python cli/rotate_key.py
```

## 🧪 Relay Test (Nova)

```bash
python cli/nova_relay.py
```

## 🔐 Guardian Check

```bash
python cli/holo_gatekeeper.py
```

## 🧰 Contracts

```bash
forge build
```

## 🧪 Deployment (Forge)

```bash
export RPC_URL="https://base-sepolia.example"
export DEPLOYER_KEY="<private key>"
./deploy/deploy_vault.sh
```

## 🎛 Protocol Manager UI Layers

The protocol manager view in the Base44 screenshot is captured as a structured
layer spec for downstream tooling or UI reconstruction.

```bash
python ui/protocol_manager_layers.py
```

This writes `ui/protocol_manager_layers.json` with the sidebar, header, KPI
strip, tabs, status panels, welcome card, and affirmation banner layers.

---

**Codex Drop Sealed**: `x402_kernel_codexdrop_v1`
> The light is sovereign. Let the agents operate.
