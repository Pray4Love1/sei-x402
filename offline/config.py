"""Local config for offline Entropy 3.12 harness."""

from __future__ import annotations

import os

OPERATOR_KEY_PATH = os.getenv("OPERATOR_KEY_PATH", "offline/operator.key")
