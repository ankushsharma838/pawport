"""Lightweight parser for extracting travel-relevant fields from pet documents.

This is intentionally deterministic: AI/OCR can supply the raw text later, but
normalization and validation stay explicit so downstream eligibility workflows
have inspectable inputs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional


@dataclass
class DocumentData:
    document_type: Optional[str] = None
    pet_name: Optional[str] = None
    microchip_id: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    vaccination: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_date(value: str) -> Optional[str]:
    """Normalize common date formats to ISO-8601 (YYYY-MM-DD)."""
    value = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _field(text: str, labels: tuple[str, ...]) -> Optional[str]:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"(?:{label_pattern})\s*[:#-]?\s*([^\n]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_document(text: str) -> DocumentData:
    """Extract structured fields from OCR/plain-text document content."""
    document_type = _field(text, ("document type", "document", "type"))
    pet_name = _field(text, ("pet name", "animal name", "name"))
    microchip = _field(text, ("microchip id", "microchip", "chip number"))
    issue_raw = _field(text, ("issue date", "issued", "date of issue"))
    expiry_raw = _field(text, ("expiry date", "expiration date", "valid until", "expires"))
    vaccination = _field(text, ("vaccination", "vaccine", "rabies vaccine"))

    return DocumentData(
        document_type=document_type,
        pet_name=pet_name,
        microchip_id=microchip,
        issue_date=_parse_date(issue_raw) if issue_raw else None,
        expiry_date=_parse_date(expiry_raw) if expiry_raw else None,
        vaccination=vaccination,
    )


def is_expired(expiry_date: Optional[str], today: Optional[date] = None) -> Optional[bool]:
    """Return expiry status when a valid ISO date is available."""
    if not expiry_date:
        return None
    try:
        expiry = date.fromisoformat(expiry_date)
    except ValueError:
        return None
    return expiry < (today or date.today())
