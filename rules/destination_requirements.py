"""Destination-specific checklist evaluation for configured PawPort routes.

This is a document-matching aid, not a legal eligibility decision. A matching
document is only evidence for user review; it is not validated as authentic or
accepted by an authority.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from ai.document_parser.parser import DocumentData, parse_document


PROFILE_DIR = Path(__file__).parent / "profiles"


def load_route_profile(origin: str, destination: str, pet_type: str) -> Optional[dict]:
    """Load an explicitly configured route profile, if one exists."""
    profile_path = PROFILE_DIR / f"{origin.upper()}-{destination.upper()}-{pet_type.lower()}-non-commercial.json"
    if not profile_path.exists():
        return None
    return json.loads(profile_path.read_text(encoding="utf-8"))


def _has_phrase(value: Optional[str], *phrases: str) -> bool:
    normalized = (value or "").casefold()
    return any(phrase.casefold() in normalized for phrase in phrases)


def _evidence_status(requirement: dict, documents: list[DocumentData], today: date) -> tuple[str, str]:
    evidence = requirement.get("evidence")

    if evidence == "microchip_id":
        found = any(bool((doc.microchip_id or "").strip()) for doc in documents)
        return ("FOUND", "A microchip ID was extracted." if found else "No microchip ID was found in the supplied documents.")

    if evidence == "rabies_vaccination":
        records = [
            doc for doc in documents
            if _has_phrase(doc.vaccination, "rabies")
            or _has_phrase(doc.document_type, "rabies vaccination")
        ]
        if not records:
            return "MISSING", "No rabies vaccination record was detected."
        dated = [doc for doc in records if doc.expiry_date]
        if not dated:
            return "REVIEW_REQUIRED", "A rabies record was detected, but its expiry date was not parsed."
        for doc in dated:
            try:
                if date.fromisoformat(doc.expiry_date) >= today:
                    return "FOUND", "A rabies record with a non-expired parsed expiry date was detected; verify the original document."
            except ValueError:
                continue
        return "EXPIRED", "The parsed rabies vaccination expiry date is in the past."

    if evidence == "rabies_titration":
        found = any(
            _has_phrase(doc.document_type, "rabies antibody", "rabies neutralising antibody", "rabies neutralizing antibody")
            and _has_phrase(doc.document_type, "titration", "titre", "titer")
            for doc in documents
        )
        return ("FOUND", "A titration report appears to be present; verify sample date, titre, laboratory designation and report authenticity.") if found else ("MISSING", "No rabies antibody titration report was detected.")

    if evidence == "eu_animal_health_certificate":
        found = any(_has_phrase(doc.document_type, "animal health certificate", "eu health certificate") for doc in documents)
        return ("FOUND", "An animal health certificate appears to be present; verify issue date, endorsement and validity.") if found else ("MISSING", "No EU animal health certificate was detected.")

    if evidence == "non_commercial_declaration":
        found = any(_has_phrase(doc.document_type, "non-commercial declaration", "non commercial declaration", "owner declaration") for doc in documents)
        return ("FOUND", "A non-commercial movement declaration appears to be present; verify it is the current required form.") if found else ("MISSING", "No non-commercial movement declaration was detected.")

    return "REVIEW_REQUIRED", "This evidence type is not yet supported by the prototype parser."


def build_destination_checklist(
    origin: str,
    destination: str,
    pet_type: str,
    document_texts: Iterable[str],
    today: Optional[date] = None,
) -> dict:
    """Match supplied document text against a configured route profile."""
    profile = load_route_profile(origin, destination, pet_type)
    if profile is None:
        return {
            "status": "PROFILE_NOT_CONFIGURED",
            "route": {"origin": origin.upper(), "destination": destination.upper(), "pet_type": pet_type.lower()},
            "items": [],
            "message": "No source-reviewed route profile is configured for this journey yet.",
        }

    documents = [parse_document(text) for text in document_texts]
    today = today or date.today()
    items = []

    for requirement in profile["requirements"]:
        kind = requirement["kind"]
        if kind == "document_evidence":
            status, note = _evidence_status(requirement, documents, today)
        else:
            status = "ACTION_REQUIRED"
            note = "This step needs confirmation outside the uploaded-document parser."

        items.append({
            "id": requirement["id"],
            "title": requirement["title"],
            "status": status,
            "kind": kind,
            "instructions": requirement["instructions"],
            "note": note,
        })

    blocking = [item for item in items if item["status"] in {"MISSING", "EXPIRED", "REVIEW_REQUIRED", "ACTION_REQUIRED"}]
    return {
        "status": "REVIEW_REQUIRED" if blocking else "READY_FOR_REVIEW",
        "route": {
            "origin": profile["origin_country"],
            "destination": profile["destination_country"],
            "pet_type": pet_type.lower(),
            "movement_type": profile["movement_type"],
        },
        "profile_id": profile["profile_id"],
        "profile_status": profile["profile_status"],
        "last_reviewed": profile["last_reviewed"],
        "items": items,
        "sources": profile["sources"],
        "limitations": profile["limitations"],
        "summary": {
            "total": len(items),
            "found": sum(item["status"] == "FOUND" for item in items),
            "missing": sum(item["status"] in {"MISSING", "EXPIRED"} for item in items),
            "actions": sum(item["status"] == "ACTION_REQUIRED" for item in items),
            "review": sum(item["status"] == "REVIEW_REQUIRED" for item in items),
        },
    }
