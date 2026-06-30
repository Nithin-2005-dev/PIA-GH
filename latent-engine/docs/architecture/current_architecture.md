# Current PIA Architecture

## Canonical Flow

```text
Software Events
    |
    v
Observation Layer
    |
    v
Measurement Operating System
    |
    v
Evidence Intelligence Platform
    |
    v
Expertise Layer
    |
    v
Reasoning Layer
    |
    v
Decision Layer
```

Short form:

```text
Event -> Measurement -> Evidence -> Expertise -> Reasoning -> Decision
```

## Contract Rule

Evidence is the exclusive bridge from Measurement to Expertise.

- Measurement produces validated, confidence-scored, unit-aware facts.
- Evidence synthesizes validated measurements into explainable conclusions.
- Expertise consumes evidence only, never raw measurements.

## Current Capability Graph

```text
Activity
  -> Observation
  -> Measurement
  -> Evidence
  -> Expertise
  -> Ownership
  -> Risk
  -> Forecast
  -> Decision
```

## Layers

### Observation Layer

Captures source-system activity as immutable events and software signals.

### Measurement Operating System

Computes deterministic measurements, performs normalization, validation,
confidence estimation, uncertainty modeling, quality scoring, benchmarking,
lineage, streaming, and replay support.

### Evidence Intelligence Platform

Consumes only validated measurements. Produces immutable evidence with
confidence, uncertainty, quality, strength, provenance, lineage,
traceability, validation results, lifecycle, ontology category, benchmark
context, historical context, and explanations.

### Expertise Layer

Applies domain expertise to validated evidence. Direct measurement access is
outside the layer contract.

### Reasoning Layer

Combines expert conclusions into coherent analyses, scenarios, and forecasts.

### Decision Layer

Turns reasoning into recommendations, plans, and executive actions.

## Milestone Status

M1-M9 established events, legacy evidence extraction, expertise, ownership,
and risk.

M30-M34 established the Measurement Operating System, signal intelligence, and
scientific validation.

M35 establishes the Evidence Intelligence Platform as the production bridge
between Measurement and Expertise.
