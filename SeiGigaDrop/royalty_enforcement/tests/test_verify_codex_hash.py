from __future__ import annotations

import json
import unittest
from importlib import util
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "royalty_enforcement"
    / "scripts"
    / "verify_codex_hash.py"
)


def load_module():
    spec = util.spec_from_file_location("verify_codex_hash", SCRIPT_PATH)
    module = util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class VerifyCodexHashTests(unittest.TestCase):
    def test_sha256_hash(self) -> None:
        module = load_module()
        payload = {"paymentPayload": {"network": "base"}}
        canonical = json.dumps(
            payload["paymentPayload"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        expected = "0x" + module.hashlib.sha256(canonical).hexdigest()
        digest = module._sha256_hash(canonical)

        self.assertEqual(digest, expected)

    def test_select_path_missing(self) -> None:
        module = load_module()
        with self.assertRaises(KeyError):
            module._select_path({"paymentPayload": {}}, "paymentPayload.missing")


if __name__ == "__main__":
    unittest.main()
