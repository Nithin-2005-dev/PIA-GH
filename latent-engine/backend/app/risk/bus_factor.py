from dataclasses import dataclass

from app.domain.entity_ref import EntityRef

from .risk_level import RiskLevel


@dataclass(frozen=True)
class BusFactor:

    module_ref: EntityRef

    value: int

    coverage: float

    risk_level: RiskLevel