# x402 Offline Cryptographic Harness

This package provides a local, dependency-tolerant x402 harness for entropy, signing, and verification.

## Components

- `entropy.py` — deterministic anchor + ephemeral noise entropy commitments
- `signer.py` — canonical payload signing (secp256k1)
- `verify.py` — detached signature verification
- `test_entropy.py` — end-to-end entropy + digest + sign + verify flow
- `test_harness.py` — compact agent-credential verification path
- `setup.sh` — best-effort dependency bootstrap (safe in offline/proxy envs)

## Setup

```bash
./offline/setup.sh
```

## Run checks

```bash
python -m compileall offline
python -m offline.test_harness
python offline/test_entropy.py
```

## Notes

- `entropy.py` automatically falls back to `hashlib.sha3_256` if `pycryptodome` is unavailable.
- Set `OPERATOR_KEY_PATH` to override private key location.
