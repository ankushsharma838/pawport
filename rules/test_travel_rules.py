from datetime import date

from travel_rules import TravelInput, evaluate_travel_readiness


def complete_travel():
    return TravelInput(
        origin="IN",
        destination="DE",
        pet_type="dog",
        microchip_present=True,
        rabies_vaccination_present=True,
        rabies_valid_until=date(2027, 6, 1),
        health_certificate_present=True,
    )


def test_complete_journey_is_ready_for_review():
    result = evaluate_travel_readiness(complete_travel(), today=date(2026, 10, 22))

    assert result.status == "READY_FOR_REVIEW"
    assert result.missing_requirements == []


def test_missing_health_certificate_blocks_readiness():
    travel = complete_travel()
    travel.health_certificate_present = False

    result = evaluate_travel_readiness(travel, today=date(2026, 10, 22))

    assert result.status == "NOT_READY"
    assert "Health certificate" in result.missing_requirements


def test_expired_rabies_vaccination_blocks_readiness():
    travel = complete_travel()
    travel.rabies_valid_until = date(2026, 10, 21)

    result = evaluate_travel_readiness(travel, today=date(2026, 10, 22))

    assert result.status == "NOT_READY"
    assert any("expired" in item for item in result.missing_requirements)


def test_missing_microchip_is_reported():
    travel = complete_travel()
    travel.microchip_present = False

    result = evaluate_travel_readiness(travel, today=date(2026, 10, 22))

    assert result.status == "NOT_READY"
    assert "Microchip identification" in result.missing_requirements
