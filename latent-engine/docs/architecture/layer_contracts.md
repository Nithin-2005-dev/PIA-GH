# Layer Contracts

## Canonical Order

```text
Software Events -> Observation -> Measurement -> Evidence -> Expertise
-> Reasoning -> Decision
```

## Measurement To Evidence

Producer: Measurement Operating System

Consumer: Evidence Intelligence Platform

Payload: immutable `Measurement` objects that passed the Measurement Layer
validation gate.

Rules:

- Measurement calculates facts.
- Evidence does not calculate measurements.
- Evidence may use confidence, uncertainty, quality, benchmark context,
  provenance, lineage, and metadata already attached to measurements.
- Failed or not-run measurements are rejected at Evidence intake.

## Evidence To Expertise

Producer: Evidence Intelligence Platform

Consumer: Expertise Layer

Payload: `EvidencePackage.for_expertise()`.

Rules:

- Expertise consumes only validated evidence.
- Expertise must not directly consume measurements.
- Evidence packages preserve tenant id, pipeline version, audit events, and
  generation timestamp.
- Evidence must include enough traceability for expert conclusions to cite the
  supporting measurements without re-reading raw measurement streams.

## Reasoning To Decision

Producer: Reasoning Layer

Consumer: Decision Layer

Payload: analyses, forecasts, scenarios, and ranked recommendations grounded in
expertise over evidence.

Rules:

- Decisions should cite reasoning outputs and evidence IDs.
- Decisions should not bypass Evidence or Expertise to reinterpret raw
  measurements.

