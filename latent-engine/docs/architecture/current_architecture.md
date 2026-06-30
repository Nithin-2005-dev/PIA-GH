# Current PIA Architecture

## Canonical Flow

```text
Software Events
    |
    v
Vendor Adapter
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
Observation -> Measurement -> Evidence -> Expertise -> Reasoning -> Decision
```

## Contract Rule

Observation preserves software reality. Measurement quantifies it. Evidence
synthesizes measurement output into trustworthy conclusions.

- Observation produces immutable vendor-neutral `Observation` objects.
- Measurement consumes only canonical observations and produces validated,
  confidence-scored, unit-aware measurements.
- Evidence consumes only validated measurements.
- Expertise consumes evidence only, never raw observations or measurements.

## Current Capability Graph

```text
Activity
  -> Canonical Observation
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

Adapters authenticate, fetch, parse, translate, and preserve provenance.
Observation stores immutable canonical facts. It never calculates measurement,
confidence, risk, evidence, or business meaning.

### Measurement Operating System

Computes deterministic measurements, performs normalization, validation,
confidence estimation, uncertainty modeling, quality scoring, benchmarking,
lineage, streaming, and replay support from `Observation` input only.

### Evidence Intelligence Platform

Consumes only validated measurements. Produces immutable evidence with
confidence, uncertainty, quality, strength, provenance, lineage,
traceability, validation results, lifecycle, ontology category, benchmark
context, historical context, and explanations.

### Expertise Layer

Applies domain expertise to validated evidence. Direct measurement and
observation access is outside the layer contract.

### Reasoning Layer

Combines expert conclusions into coherent analyses, scenarios, and forecasts.

### Decision Layer

Turns reasoning into recommendations, plans, and executive actions.

## Milestone Status

M1-M9 established events, legacy evidence extraction, expertise, ownership,
and risk.

M30-M35 established the Measurement Operating System, signal intelligence,
scientific validation, and the Evidence Intelligence Platform.

M36 refactors Observation into the canonical vendor-agnostic foundation beneath
Measurement.
