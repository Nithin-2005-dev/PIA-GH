# Milestone 8 Findings

## Observation 1

Ownership and expertise are related but distinct concepts.

Expertise answers:

Who knows this module?

Ownership answers:

Who is primarily responsible for this module?

Ownership is derived from expertise rather than directly observed.

---

## Observation 2

Ownership should be policy-driven.

Introducing OwnershipPolicy allows future ownership strategies without modifying orchestration code.

Potential future policies:

* Recency-aware ownership
* Organizational ownership
* Team ownership
* LLM-assisted ownership

---

## Observation 3

Ownership distributions are more informative than single owners.

A module may have:

* one primary owner
* multiple secondary owners
* many contributors

This distribution preserves organizational context.

---

## Observation 4

Ownership levels simplify downstream reasoning.

Using:

* PRIMARY
* SECONDARY
* CONTRIBUTOR

is preferable to repeatedly evaluating ownership thresholds throughout the system.

Future services can reason using ownership semantics rather than percentages.

---

## Observation 5

Current ownership is relative rather than absolute.

Example:

Alice = 1

Bob = 0

Ownership:

Alice = 100%

This indicates ownership dominance but not ownership confidence.

Future versions may introduce:

* ownership confidence
* minimum expertise thresholds
* ownership stability metrics

---

## Key Insight

Ownership is an emergent property of expertise distributions.

PIA now infers responsibility structures directly from observed activity.
