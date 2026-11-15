# Document-to-readiness workflow

This experiment connects PawPort's existing document parser to its deterministic
travel-readiness rules.

## Flow

1. OCR or an upstream AI step supplies document text.
2. `parse_document()` extracts known fields into `DocumentData`.
3. `build_travel_input()` combines the parsed records into the structured input
   expected by the rules engine.
4. `evaluate_travel_readiness()` returns missing requirements, warnings and a
   conservative status.

The adapter currently recognizes a microchip when a parsed record contains a
microchip ID, a rabies record when the document type or vaccination field
explicitly mentions rabies, and a health certificate when the document type
explicitly identifies one. It uses the expiry date from a rabies record when
available.

## Important boundaries

- Missing or unrecognized information is not silently treated as present.
- A rabies record without a parseable expiry date remains incomplete.
- `READY_FOR_REVIEW` is not a travel clearance or regulatory approval.
- This prototype does not yet load country- or airline-specific requirements.
- Parser output should be reviewed when source documents are unclear or OCR is
  uncertain.

## Run the tests

From the repository root:

```bash
python -m pytest ai/document_parser/test_parser.py rules/test_travel_rules.py ai/workflow/test_readiness.py
```
