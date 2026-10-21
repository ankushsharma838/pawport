from datetime import date

from parser import is_expired, parse_document


def test_parse_pet_travel_document():
    text = """
    Document Type: Rabies Vaccination Certificate
    Pet Name: Bruno
    Microchip ID: 985141000123456
    Issue Date: 10/01/2026
    Expiry Date: 10/01/2027
    Vaccination: Rabies
    """

    result = parse_document(text)

    assert result.document_type == "Rabies Vaccination Certificate"
    assert result.pet_name == "Bruno"
    assert result.microchip_id == "985141000123456"
    assert result.issue_date == "2026-01-10"
    assert result.expiry_date == "2027-01-10"
    assert result.vaccination == "Rabies"


def test_expiry_status_is_deterministic():
    assert is_expired("2026-01-10", today=date(2026, 2, 1)) is True
    assert is_expired("2026-02-10", today=date(2026, 2, 1)) is False


def test_missing_expiry_is_unknown():
    assert is_expired(None, today=date(2026, 2, 1)) is None
