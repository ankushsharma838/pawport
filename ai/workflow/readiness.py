"""Connect parsed pet documents to PawPort's deterministic readiness rules.

This adapter does not infer regulatory eligibility. It only maps explicitly
extracted document fields into the prototype rules engine's structured input.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from ai.document_parser.parser import DocumentData, parse_document
from rules.travel_rules import TravelInput, TravelResult, evaluate_travel_readiness


def _contains(value: Optional[str], *terms: str) -> bool:
    normalized = (value or "").casefold()
    return any(term in normalized for term in terms)


def build_travel_input(
    origin: str,
    destination: str,
    pet_type: str,
    documents: Iterable[DocumentData],
) -> TravelInput:
    """Build a conservative TravelInput from parsed document records."""
    docs = list(documents)

    microchip_present = any(bool((doc.microchip_id or "").strip()) for doc in docs)

    rabies_docs = [
        doc for doc in docs
        if _contains(doc.vaccination, "rabies")
        or _contains(doc.document_type, "rabies")
    ]
    rabies_doc = next(
        (doc for doc in rabies_docs if doc.expiry_date),
        rabies_docs[0] if rabies_docs else None,
    )

    rabies_valid_until: Optional[date] = None
    if rabies_doc and rabies_doc.expiry_date:
        try:
            rabies_valid_until = date.fromisoformat(rabies_doc.expiry_date)
        except ValueError:
            rabies_valid_until = None

    health_certificate_present = any(
        _contains(doc.document_type, "health certificate", "health cert")
        for doc in docs
    )

    return TravelInput(
        origin=origin,
        destination=destination,
        pet_type=pet_type,
        microchip_present=microchip_present,
        rabies_vaccination_present=bool(rabies_docs),
        rabies_valid_until=rabies_valid_until,
        health_certificate_present=health_certificate_present,
    )


def assess_document_texts(
    origin: str,
    destination: str,
    pet_type: str,
    document_texts: Iterable[str],
    today: Optional[date] = None,
) -> tuple[list[DocumentData], TravelInput, TravelResult]:
    """Parse document text, build structured travel input, and assess readiness."""
    parsed_documents = [parse_document(text) for text in document_texts]
    travel_input = build_travel_input(origin, destination, pet_type, parsed_documents)
    result = evaluate_travel_readiness(travel_input, today=today)
    return parsed_documents, travel_input, result
