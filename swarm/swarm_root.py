"""Root intent builder for autonomous settlement epochs."""

from __future__ import annotations


class SwarmRoot:
    def __init__(self, epoch_id: str, employee_list: list[str], networks: list[str]):
        self.epoch_id = epoch_id
        self.employee_list = employee_list
        self.networks = networks

    def create_master_intent(self) -> dict:
        return {
            "epoch": self.epoch_id,
            "employees": self.employee_list,
            "networks": self.networks,
            "mode": "settlement_sweep_v3.12",
        }
