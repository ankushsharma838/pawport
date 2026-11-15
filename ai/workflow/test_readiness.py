from datetime import date

from ai.workflow.readiness import assess_document_texts


def test_complete_document_set_reaches_review_state():
    texts = [
        """Document Type: Rabies Vaccination Certificate
Microchip ID: 985141000123456
Expiry Date: 10/01/2027
Vaccination: Rabies""",
        "Document Type: Health Certificate",
    ]
    parsed, travel, result = assess_document_texts(
        "IN", "DE", "dog", texts, today=date(2026, 2, 1)
    )
    assert len(parsed) == 2
    assert travel.microchip_present
    assert travel.rabies_vaccination_present
    assert travel.health_certificate_present
    assert result.status == "READY_FOR_REVIEW"


def test_missing_health_document_is_not_assumed():
    texts = [
        """Document Type: Rabies Vaccination Certificate
Microchip ID: 985141000123456
Expiry Date: 10/01/2027
Vaccination: Rabies"""
    ]
    _, _, result = assess_document_texts(
        "IN", "DE", "dog", texts, today=date(2026, 2, 1)
    )
    assert result.status == "NOT_READY"
    assert "Health certificate" in result.missing_requirements


def test_expired_vaccination_document_is_flagged():
    texts = [
        """Document Type: Rabies Vaccination Certificate
Microchip ID: 985141000123456
Expiry Date: 10/01/2026
Vaccination: Rabies""",
        "Document Type: Health Certificate",
    ]
    _, _, result = assess_document_texts(
        "IN", "DE", "dog", texts, today=date(2026, 2, 1)
    )
    assert result.status == "NOT_READY"
    assert any("expired" in item for item in result.missing_requirements)
