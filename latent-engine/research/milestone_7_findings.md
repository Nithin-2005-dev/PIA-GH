# Milestone 7 Findings

## Observation 1

Time is an independent signal.

Expertise is not determined solely by activity volume.

Recency matters.

---

## Observation 2

Decay behavior should be policy-driven.

Introducing DecayPolicy allows future implementations such as:

* Exponential decay
* Activity-aware decay
* Ownership-aware decay
* Machine-learning-based decay

without modifying estimator orchestration.

---

## Observation 3

Expertise aging and contribution scoring are distinct concerns.

Contribution scoring answers:

How important was this activity?

Decay answers:

How relevant is this expertise now?

These signals should remain independent.

---

## Observation 4

Current implementation uses Lazy Decay.

Expertise is decayed when new evidence is processed.

Benefits:

* No scheduler required
* No background processing
* Simple implementation

Trade-offs:

* Stored expertise estimates are not continuously updated
* Decay is applied on state transition

This trade-off is acceptable at the current system maturity level.

---

## Observation 5

Time-aware expertise significantly improves future decision quality.

Future systems that depend on expertise:

* Ownership Detection
* Reviewer Recommendation
* Bus Factor Analysis
* Knowledge Risk Detection

all benefit from recency-aware estimates.

---

## Key Insight

Expertise is not a static asset.

Expertise is a dynamic state that changes as people contribute and as time passes.

PIA now models both.
