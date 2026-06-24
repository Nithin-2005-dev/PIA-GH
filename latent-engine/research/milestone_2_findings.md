# Milestone 2 Research Findings

## Observation 1

GitHub events alone are insufficient for expertise estimation.

The initial commit endpoint does not provide file-level information.

A second enrichment step is required.

---

## Observation 2

File-level targets are the fundamental unit of organizational expertise.

Expertise is not attached to repositories.

Expertise is attached to code assets.

Examples:

* files
* modules
* packages
* services

---

## Observation 3

A commit naturally induces relationships.

Example:

Developer

↓

Modified

↓

File

This suggests expertise can emerge from repeated interactions between actors and assets.

---

## Observation 4

Events contain facts, not interpretations.

A commit states:

"Developer modified file."

It does not state:

"Developer is an expert."

Expertise therefore requires an intermediate interpretation layer.

---

## Observation 5

Event → Estimate is an invalid shortcut.

A dedicated Evidence layer is required.

Correct pipeline:

Event

↓

Evidence

↓

Estimate

↓

Intelligence

---

## Key Insight

The first meaningful expertise signal discovered during Milestone 2 is:

Developer

↓

Modified

↓

File

This relationship becomes the foundation of future expertise estimation.
