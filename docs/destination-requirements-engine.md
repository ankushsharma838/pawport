# Destination-specific requirements: India to Germany

## Why this profile exists

A generic readiness check cannot represent every origin/destination combination. This first route profile demonstrates a data-driven approach for a private, non-commercial dog journey from India to Germany.

The profile lives in `rules/profiles/IN-DE-dog-non-commercial.json`; route requirements are data, while the evaluator stays reusable.

## What the profile checks

- Microchip identification
- Rabies vaccination and parsed expiry
- Rabies antibody titration report
- EU animal health certificate
- Non-commercial movement declaration
- Manual confirmation of a designated travellers' point of entry
- Veterinary fitness-to-travel confirmation

The European Commission currently lists the countries and territories exempt from rabies antibody titration. India does not appear in that list, so the prototype profile includes the titration report as a required evidence item. The profile also records the EU certificate, declaration and entry-check workflow.

## How the engine works

1. The document parser extracts fields and document labels from supplied text.
2. `load_route_profile()` selects a configured route profile.
3. `build_destination_checklist()` matches parsed records to the profile's evidence types.
4. Each item is marked `FOUND`, `MISSING`, `EXPIRED`, `REVIEW_REQUIRED` or `ACTION_REQUIRED`.
5. The result includes instructions, source links, profile review date and limitations.

## Example

```python
from rules.destination_requirements import build_destination_checklist

result = build_destination_checklist(
    origin="IN",
    destination="DE",
    pet_type="dog",
    document_texts=[
        "Document Type: Rabies Vaccination Certificate\n"
        "Microchip ID: 985141000123456\n"
        "Expiry Date: 10/01/2027\n"
        "Vaccination: Rabies"
    ],
)

print(result["status"])
for item in result["items"]:
    print(item["status"], item["title"], item["note"])
```

## Important product and safety decisions

- A document match means only that the parser found a relevant label or field. It does not prove authenticity, correctness, endorsement or acceptance.
- The engine deliberately keeps manual actions visible instead of pretending that document parsing can complete them.
- `READY_FOR_REVIEW` is not a travel clearance.
- The profile is limited to private, non-commercial dog travel and does not cover commercial movement, ownership transfer, more than five pets, unusual transit routes or airline-specific policies.
- Verify requirements with the competent authority, veterinarian and airline before travel.

## Official sources

- [European Commission: Bringing a pet into the EU from a non-EU country](https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/bringing-pet-eu-non-eu-country_en)
- [European Commission: Listing of territories and non-EU countries](https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/listing-territories-and-non-eu-countries_en)

Profile last reviewed: 15 November 2026.
