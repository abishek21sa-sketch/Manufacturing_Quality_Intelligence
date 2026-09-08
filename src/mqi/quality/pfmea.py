from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class FailureMode:
    name: str
    severity: int
    occurrence: int
    detection: int

    @property
    def rpn(self) -> int:
        for v in (self.severity, self.occurrence, self.detection):
            if not 1 <= v <= 10:
                raise ValueError("PFMEA ratings must be in [1, 10]")
        return self.severity * self.occurrence * self.detection


def rank_failure_modes(modes: list[FailureMode]) -> list[FailureMode]:
    return sorted(modes, key=lambda m: m.rpn, reverse=True)
