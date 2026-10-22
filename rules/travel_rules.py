"""Deterministic travel-readiness rules for PawPort.

The rules layer intentionally contains no LLM calls. It evaluates structured
journey data against explicit requirements so that AI can assist with messy
inputs without becoming the source of truth for eligibility decisions.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class TravelInput:
    origin: str
    destination: str
    pet_type: str
    microchip_present: bool
    rabies_vaccination_present: bool
    rabies_valid_until: Optional[date]
    health_certificate_present: bool


@dataclass
class TravelResult:
    status: str
    missing_requirements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def evaluate_travel_readiness(travel: TravelInput, today: Optional[date] = None) -> TravelResult:
    """Evaluate basic travel readiness using deterministic rules.

    This is a product prototype, not a regulatory database. It deliberately
    does not claim that these checks cover every country or airline requirement.
    """
    today = today or date.today()
    missing: List[str] = []
    warnings: List[str] = []

    if not travel.microchip_present:
        missing.append("Microchip identification")

    if not travel.rabies_vaccination_present:
        missing.append("Valid rabies vaccination")
    elif travel.rabies_valid_until is None:
        missing.append("Rabies vaccination validity date")
    elif travel.rabies_valid_until < today:
        missing.append("Valid rabies vaccination (current record is expired)")

    if not travel.health_certificate_present:
        missing.append("Health certificate")

    if missing:
        return TravelResult(status="NOT_READY", missing_requirements=missing, warnings=warnings)

    warnings.append(
        "Prototype check only: verify destination- and airline-specific requirements before travel."
    )
    return TravelResult(status="READY_FOR_REVIEW", missing_requirements=[], warnings=warnings)
