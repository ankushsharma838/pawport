# AI Document Parser

A small, inspectable parsing layer for PawPort's future document workflow.

## Product problem

Pet travel requires parents to keep track of documents such as vaccination records and microchip information. Before PawPort can reason about readiness, useful fields need to be extracted into a consistent structure.

## Current approach

The first version deliberately separates **extraction** from **decision-making**:

1. OCR/LLM can provide raw document text.
2. `parse_document()` extracts known fields into `DocumentData`.
3. Dates are normalized to ISO format.
4. `is_expired()` provides a simple, testable expiry signal.
5. A future rules engine can consume this structured output.

This keeps regulatory decisions out of the parser and makes the extracted data easy to inspect and test.

## Example

```python
from ai.document_parser.parser import parse_document

text = """
Document Type: Rabies Vaccination Certificate
Pet Name: Bruno
Microchip ID: 985141000123456
Issue Date: 10/01/2026
Expiry Date: 10/01/2027
Vaccination: Rabies
"""

result = parse_document(text)
print(result.to_dict())
```

## Next iteration

- Add OCR input adapters.
- Add confidence scores for extracted fields.
- Add an LLM extraction experiment and compare it with deterministic parsing.
- Add malformed-document and multilingual test cases.
- Feed the normalized output into the travel eligibility rules engine.

> This module is an experiment, not a source of truth for veterinary, airline or regulatory requirements.
