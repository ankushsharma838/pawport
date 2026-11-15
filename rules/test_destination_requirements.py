from datetime import date

from rules.destination_requirements import build_destination_checklist


def test_india_to_germany_profile_returns_route_specific_items():
    texts = [
        """Document Type: Rabies Vaccination Certificate
Microchip ID: 985141000123456
Expiry Date: 10/01/2027
Vaccination: Rabies""",
        "Document Type: Rabies Antibody Titration Test Report",
        "Document Type: EU Animal Health Certificate",
        "Document Type: Non-Commercial Declaration",
    ]

    result = build_destination_checklist(
        "IN", "DE", "dog", texts, today=date(2026, 2, 1)
    )

    statuses = {item["id"]: item["status"] for item in result["items"]}
    assert result["profile_id"] == "IN-DE-dog-non-commercial"
    assert statuses["microchip"] == "FOUND"
    assert statuses["rabies_vaccination"] == "FOUND"
    assert statuses["rabies_titration"] == "FOUND"
    assert statuses["eu_animal_health_certificate"] == "FOUND"
    assert statuses["non_commercial_declaration"] == "FOUND"
    assert statuses["travellers_point_of_entry"] == "ACTION_REQUIRED"
    assert result["status"] == "REVIEW_REQUIRED"


def test_missing_titration_report_is_called_out():
    result = build_destination_checklist(
        "IN",
        "DE",
        "dog",
        ["Document Type: Rabies Vaccination Certificate\nMicrochip ID: 123\nExpiry Date: 10/01/2027\nVaccination: Rabies"],
        today=date(2026, 2, 1),
    )
    statuses = {item["id"]: item["status"] for item in result["items"]}
    assert statuses["rabies_titration"] == "MISSING"
    assert result["summary"]["missing"] >= 1


def test_expired_rabies_record_is_not_marked_found():
    result = build_destination_checklist(
        "IN",
        "DE",
        "dog",
        ["Document Type: Rabies Vaccination Certificate\nMicrochip ID: 123\nExpiry Date: 10/01/2025\nVaccination: Rabies"],
        today=date(2026, 2, 1),
    )
    statuses = {item["id"]: item["status"] for item in result["items"]}
    assert statuses["rabies_vaccination"] == "EXPIRED"


def test_unknown_route_does_not_fall_back_to_generic_rules():
    result = build_destination_checklist("IN", "JP", "dog", [])
    assert result["status"] == "PROFILE_NOT_CONFIGURED"
    assert result["items"] == []
