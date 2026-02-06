# x402 Scripts

This folder contains helper scripts for the x402 EXACT payment flow. The scripts are intended for local workflows where you generate a handoff bundle, optionally net micro-payments, and then broadcast or settle through your own gateway.

## Scripts

### `run_exact_cycle.py`

Generates a signed handoff bundle from a payment requirements JSON file and optionally calls the netting gateway.

```bash
python scripts/run_exact_cycle.py \
  --requirements ./payment_requirements.json \
  --private-key "0xyourprivatekey" \
  --output ./handoff.json
```

To skip the netting call (only create the handoff bundle):

```bash
python scripts/run_exact_cycle.py \
  --requirements ./payment_requirements.json \
  --private-key "0xyourprivatekey" \
  --output ./handoff.json \
  --skip-netting
```

To override the gateway URL:

```bash
python scripts/run_exact_cycle.py \
  --requirements ./payment_requirements.json \
  --private-key "0xyourprivatekey" \
  --output ./handoff.json \
  --gateway-url http://localhost:4020/x402/pay
```

### `net_then_broadcast.py`

Sends an existing `handoff.json` bundle to the netting gateway before broadcast.

```bash
python scripts/net_then_broadcast.py ./handoff.json
```

Override the gateway URL:

```bash
python scripts/net_then_broadcast.py ./handoff.json \
  --gateway-url http://localhost:4020/x402/pay
```

## Handoff bundle format

The `handoff.json` bundle is expected to contain the following keys:

```json
{
  "xPaymentHeader": "...",
  "paymentPayload": {
    "x402Version": 1,
    "scheme": "exact",
    "network": "base-sepolia",
    "payload": {
      "signature": "0x...",
      "authorization": {
        "from": "0x...",
        "to": "0x...",
        "value": "1000",
        "validAfter": "...",
        "validBefore": "...",
        "nonce": "0x..."
      }
    }
  },
  "paymentRequirements": {"resource": "example-session"}
}
```

Only the `paymentPayload` authorization fields and the optional `paymentRequirements.resource` are required for the netting step.
