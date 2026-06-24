# Milestone 5 Findings

## Observation 1

Expertise estimation and expertise consumption are separate concerns.

Projection maintains state.

Query services consume state.

---

## Observation 2

Raw score and confidence represent different dimensions.

raw_score:
estimated expertise magnitude

confidence:
certainty of estimate

Both should remain independent.

---

## Observation 3

Contribution magnitude is distinct from confidence.

confidence:
trust in observation

strength:
importance of observation

These concepts should not be merged.

---

## Observation 4

Introducing evidence strength required changes only to:

* Extractor policies
* Estimator

No modifications were required in:

* Event model
* Projection layer
* Query layer

This validates architectural separation.

---

## Observation 5

Current strength is commit-level.

All files touched by a commit inherit the same strength value.

This is acceptable for the current milestone but may overestimate expertise in large multi-file commits.

---

## Future Directions

Potential future strength models:

* File-level diff strength
* Semantic code impact strength
* Review depth strength
* Architectural impact strength
* LLM-assisted contribution analysis

---

## Key Insight

Expertise is not derived from activity count alone.

Meaningful expertise estimation requires both:

* relationship type
* contribution magnitude

The system has now moved beyond activity tracking and into weighted expertise estimation.
