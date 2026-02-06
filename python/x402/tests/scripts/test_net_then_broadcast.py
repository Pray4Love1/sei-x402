from __future__ import annotations

import json
from importlib import util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "net_then_broadcast.py"


def load_module():
    spec = util.spec_from_file_location("net_then_broadcast", SCRIPT_PATH)
    module = util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_build_netting_body_extracts_fields(tmp_path: Path) -> None:
    pytest.importorskip("requests")
    module = load_module()
    handoff = {
        "paymentPayload": {
            "payload": {
                "authorization": {
                    "from": "0xabc",
                    "to": "0xdef",
                    "value": "123",
                }
            }
        },
        "paymentRequirements": {"resource": "session-1"},
    }
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(handoff), encoding="utf-8")

    raw = module.load_handoff(path)
    body = module.build_netting_body(raw)

    assert body == {
        "sessionId": "session-1",
        "payer": "0xabc",
        "merchant": "0xdef",
        "microAmount": 123,
    }


def test_build_netting_body_uses_root_resource() -> None:
    pytest.importorskip("requests")
    module = load_module()
    raw = {
        "paymentPayload": {
            "authorization": {
                "from": "0xabc",
                "to": "0xdef",
                "value": "456",
            }
        },
        "resource": "root-session",
    }

    body = module.build_netting_body(raw)

    assert body["sessionId"] == "root-session"
    assert body["microAmount"] == 456


def test_post_netting_raises_for_bad_response(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("requests")
    module = load_module()

    class FakeResponse:
        def raise_for_status(self) -> None:
            raise module.requests.HTTPError("bad")

    def fake_post(*_args, **_kwargs):
        return FakeResponse()

    monkeypatch.setattr(module.requests, "post", fake_post)

    with pytest.raises(module.requests.HTTPError):
        module.post_netting({"sessionId": "s"}, "http://example.com")
