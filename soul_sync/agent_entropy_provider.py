"""Agent/Biometric-inspired ephemeral seed provider for offline simulation."""

from __future__ import annotations

import os
import time
from hashlib import sha512


class AgentEntropyProvider:
    """Generates short-lived entropy commitments from simulated agent biometrics."""

    async def generate_ephemeral_seed(self) -> str:
        biometric_sample = os.getenv("AGENT_BIOMETRIC_SAMPLE", "fp-62a3d9")
        agent_state = os.getenv("AGENT_STATE", "focused")
        timestamp_ms = int(time.time() * 1000)
        raw_seed = f"{biometric_sample}:{agent_state}:{timestamp_ms}"
        return sha512(raw_seed.encode("utf-8")).hexdigest()[:32]
