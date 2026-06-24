# Milestone 3 Research Findings

## Observation 1

Events and Evidence are fundamentally different.

Event:

"Developer committed code."

Evidence:

"Developer modified file."

Events represent facts.

Evidence represents interpreted relationships.

---

## Observation 2

One Event may generate multiple Evidence objects.

Example:

One commit touching four files produces four MODIFIED relationships.

This confirms that Evidence is a graph expansion layer rather than a one-to-one transformation.

---

## Observation 3

Traceability is critical.

Every Evidence object retains:

source_event_id

This allows future expertise estimates to be explained and audited.

---

## Observation 4

File-level relationships appear to be the natural foundation of expertise estimation.

Observed pattern:

Developer

↓

MODIFIED

↓

File

Repeated interactions naturally accumulate into expertise signals.

---

## Observation 5

The current system produces relationship knowledge but does not yet estimate expertise.

Current pipeline:

GitHub

↓

Event

↓

Evidence

Future pipeline:

GitHub

↓

Event

↓

Evidence

↓

Expertise Estimate

---

## Key Insight

Expertise is not extracted directly from Events.

Expertise emerges from the aggregation of Evidence over time.
