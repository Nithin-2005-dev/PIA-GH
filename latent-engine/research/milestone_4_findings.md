# Milestone 4 Research Findings

## Observation 1

Expertise is a latent state.

It cannot be observed directly.

It must be estimated from evidence.

---

## Observation 2

Expertise estimation naturally follows a state transition model.

Current Estimate

+

Evidence

↓

Updated Estimate

---

## Observation 3

Separating scoring policies from estimators was a valuable architectural decision.

This allows future replacement of rule-based scoring with:

- Bayesian methods
- ML models
- GNNs
- LLM reasoning

without modifying estimator logic.

---

## Observation 4

Current expertise estimates are file-level.

Developer

↓

Expertise

↓

File

The system currently treats:

FILE == MODULE

This simplification should be revisited later.

---

## Observation 5

Evidence magnitude is not yet incorporated.

Current system treats:

1 line change

and

300 line change

equally.

Future versions should incorporate change magnitude into evidence strength.

---

## Observation 6

Expertise estimates are continuously maintained rather than batch-computed.

This enables real-time organizational intelligence.

---

## Key Insight

Expertise emerges from accumulated evidence.

It is not a property of an event.

It is not a property of a developer.

It is an evolving relationship between an actor and an asset.