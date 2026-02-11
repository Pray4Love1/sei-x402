"""Worker profile model for local x402 payroll settlement simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorkerProfile:
    """Payroll attributes used to compute x402 settlement amounts."""

    name: str
    wage_per_hour: int
    hours_worked: int
    pto_allocated: float
    pto_used: float = 0.0

    def apply_pto(self, hours: float) -> None:
        hours_to_use = min(max(hours, 0.0), self.pto_allocated)
        self.pto_allocated -= hours_to_use
        self.pto_used += hours_to_use

    def calculate_pay(self) -> int:
        payable_hours = max(self.hours_worked - self.pto_used, 0)
        if self.hours_worked <= 0:
            return 0
        return int(self.wage_per_hour * payable_hours / self.hours_worked)

    @property
    def pto_remaining(self) -> float:
        return round(max(self.pto_allocated, 0.0), 2)
