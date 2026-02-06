from __future__ import annotations

from importlib import util
from pathlib import Path
import sys

import pytest

pytest.importorskip("pydantic")

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_PATH))

from x402.types import PaymentRequirements

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "run_exact_cycle.py"


def load_module():
    spec = util.spec_from_file_location("run_exact_cycle", SCRIPT_PATH)
    module = util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_build_handoff_bundle_includes_payload() -> None:
    eth_account = pytest.importorskip("eth_account")
    module = load_module()
    requirements = PaymentRequirements.model_validate(
        {
            "scheme": "exact",
            "network": "base-sepolia",
            "maxAmountRequired": "1000",
            "resource": "test-session",
            "description": "Test",
            "mimeType": "application/json",
            "payTo": "0x0000000000000000000000000000000000000001",
            "maxTimeoutSeconds": 300,
            "asset": "0x0000000000000000000000000000000000000000",
            "extra": {"name": "TestToken", "version": "1"},
        }
    )
    account = eth_account.Account.create()

    bundle = module.build_handoff_bundle(
        requirements=requirements,
        private_key=account.key.hex(),
        x402_version=1,
    )

    assert "xPaymentHeader" in bundle
    assert "paymentPayload" in bundle
    payload = bundle["paymentPayload"]
    assert payload["payload"]["authorization"]["from"].lower() == account.address.lower()
