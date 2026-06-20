# PIA-GH Architecture v0.1

## Overview

PIA-GH is an event-driven organizational intelligence engine that transforms GitHub activity into latent organizational knowledge.

The system follows Event Sourcing, Domain-Driven Design, Clean Architecture, and Functional Core principles.

---

## High-Level Pipeline

```
GitHub
    │
    ▼
Collector
    │
    ▼
Immutable Event
    │
    ▼
Evidence Extractor
    │
    ▼
Immutable Evidence
    │
    ▼
Latent State Estimator
    │
    ▼
Immutable Estimate Snapshot
    │
    ▼
Intelligence APIs
```

---

## Core Principles

* Events are immutable facts.
* Evidence is immutable interpretation.
* Estimates are immutable snapshots.
* Estimators create new estimates instead of mutating existing ones.
* Infrastructure depends on the domain, never the opposite.

---

## Domain Layer

Contains only business concepts.

* Event
* Evidence
* EntityRef
* ExpertiseEstimate

No database code.

No API code.

No GitHub code.

---

## Estimator Layer

Contains domain algorithms.

Responsibilities:

* Estimate latent state
* Consume Evidence
* Produce new Estimates

Independent of infrastructure.

---

## Policy Layer

Responsible for assigning evidence scores.

Current implementation:

* RuleExpertiseScoringPolicy

Future implementations:

* MLExpertiseScoringPolicy
* BayesianExpertiseScoringPolicy
* GNNExpertiseScoringPolicy

---

## Architectural Pattern

```
Event

↓

Evidence

↓

Estimator

↓

Estimate
```

This separation allows replacing algorithms without changing the domain model.
