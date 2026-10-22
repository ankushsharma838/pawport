# PawPort travel rules engine

## Why a deterministic layer?

PawPort may eventually use AI to extract information from messy documents and to explain travel preparation in natural language. The eligibility decision itself should remain traceable.

The rules engine therefore consumes **structured inputs** and returns explicit requirements, missing items and warnings.

```text
Documents / user input
        |
        v
  Structured fields
        |
        v
  Deterministic rules
        |
        +--> READY_FOR_REVIEW
        |
        +--> NOT_READY + missing requirements
```

## Current prototype

The first version checks three basic readiness areas:

- Microchip identification
- Rabies vaccination and validity date
- Health certificate

The engine returns `NOT_READY` when a required item is missing or expired. A complete input returns `READY_FOR_REVIEW` rather than claiming final eligibility.

## Product decision

The engine is deliberately conservative about what it claims. It is a prototype and **not a regulatory database**. Country- and airline-specific requirements still need to be modeled and verified before a production launch.

## Next iteration

The next version should introduce structured requirement data for destination/airline combinations instead of hard-coding checks, then connect the document parser output to this rules layer.
