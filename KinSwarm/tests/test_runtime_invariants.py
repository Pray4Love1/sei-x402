from __future__ import annotations

import asyncio
import os
import unittest

from KinSwarm.swarm_manager import SwarmManager, build_demo_workers


class TestRuntimeInvariants(unittest.TestCase):
    def test_swarm_receipts_have_required_fields(self) -> None:
        workers = build_demo_workers(10)
        os.environ["X402_NETWORKS"] = "EVM,COSMOS,SOLANA,UTXO"
        # Re-import config-driven constant path by constructing explicit networks on manager run context.
        from importlib import reload

        import KinSwarm.config as config
        import KinSwarm.swarm_manager as swarm_manager

        reload(config)
        reload(swarm_manager)

        results = asyncio.run(swarm_manager.SwarmManager(workers).run())
        self.assertTrue(results)
        expected_networks = {"EVM", "COSMOS", "SOLANA", "UTXO"}
        actual_networks = set()

        for row in results:
            self.assertIn("worker", row)
            self.assertIn("epoch", row)
            self.assertIn("amount", row)
            self.assertIn("canonical_payload_hash", row)
            self.assertIn("signature_scheme", row)
            self.assertIn("verification_result", row)
            self.assertIn("timestamp", row)
            self.assertIn("network", row)
            actual_networks.add(row["network"])
            self.assertTrue(row["verification_result"])

        self.assertEqual(actual_networks, expected_networks)


if __name__ == "__main__":
    unittest.main()
