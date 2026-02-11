from __future__ import annotations

import base64
import json
import unittest

from KinSwarm.offline.x402_reader import (
    decode_x_payment_header,
    encode_x_payment_response,
    map_internal_settlement_to_payment_response,
    map_payment_payload_to_internal_settlement,
)


class TestX402Conformance(unittest.TestCase):
    def setUp(self) -> None:
        payload = {
            "x402Version": 1,
            "scheme": "exact",
            "network": "base-sepolia",
            "payload": {"amount": "1250", "asset": "USDC", "resource": "/x402/payroll"},
        }
        self.header = base64.b64encode(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).decode("utf-8")

    def test_decode_header_golden_vector(self) -> None:
        decoded = decode_x_payment_header(self.header)
        self.assertEqual(decoded["x402Version"], 1)
        self.assertEqual(decoded["scheme"], "exact")
        self.assertEqual(decoded["payload"]["amount"], "1250")

    def test_internal_mapping_golden_vector(self) -> None:
        settlement = map_payment_payload_to_internal_settlement(
            self.header,
            intent="x402.payroll.settle",
            epoch="epoch-1",
            worker="did:x402:worker-1",
        )
        self.assertEqual(settlement.amount, 1250)
        self.assertEqual(settlement.network, "BASE-SEPOLIA")

    def test_payment_response_roundtrip(self) -> None:
        settlement = map_payment_payload_to_internal_settlement(
            self.header,
            intent="x402.payroll.settle",
            epoch="epoch-1",
            worker="did:x402:worker-1",
        )
        response = map_internal_settlement_to_payment_response(
            settlement,
            tx_hash="abc123",
            verification_result=True,
        )
        encoded = encode_x_payment_response(response)
        decoded = json.loads(base64.b64decode(encoded.encode("utf-8")).decode("utf-8"))
        self.assertEqual(decoded["txHash"], "abc123")
        self.assertTrue(decoded["success"])


if __name__ == "__main__":
    unittest.main()
