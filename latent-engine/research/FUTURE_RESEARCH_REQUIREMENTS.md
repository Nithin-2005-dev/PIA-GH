# PIA – Future Research Requirements

This document records limitations discovered from the first complete execution of the PIA pipeline.

---

# Priority 1 — Historical Repository Replay

Current Issue

Only recent commits are analysed.

Observed Effect

Knowledge graph represents a snapshot.

Required Improvement

Replay repository history chronologically to build knowledge evolution.

Expected Result

Expertise becomes time-aware.

---

# Priority 2 — Repository Scale

Current Issue

Twenty commits produced

145 modules

This demonstrates that current sampling is too small.

Required Improvement

Incrementally analyse the complete repository history.

Expected Result

Stable ownership estimates.

---

# Priority 3 — Better Expertise Estimation

Current Issue

Expertise depends primarily on commit size.

Problems

Formatting commits

Large refactors

Generated files

Documentation

can dominate expertise.

Required Improvement

Introduce semantic evidence.

Possible Signals

Code complexity

API ownership

Bug fixes

Review participation

Architectural changes

---

# Priority 4 — Knowledge Evolution

Current Issue

Knowledge exists only as the current projection.

Missing

growth

decay

knowledge transfer

Expected Improvement

Continuous expertise evolution over time.

---

# Priority 5 — Repository Semantics

Current Issue

Every modified file contributes equally.

Reality

Different files have different importance.

Future Work

Critical module detection

Dependency graph analysis

Architectural importance

Public API weighting

---

# Priority 6 — Organization Intelligence

Current Issue

Developers are independent nodes.

Missing

Developer collaboration

Review graph

Mentorship

Communication

Future Goal

Build an organization graph.

---

# Priority 7 — Forecast Validation

Current Issue

Forecasts are heuristic.

Missing

Real historical validation.

Future Goal

Predict future repository health and compare against actual future history.

---

# Priority 8 — Stateful Simulation

Current Issue

Scenarios modify output metrics only.

Future Goal

Interventions should permanently modify

Expertise

Ownership

Coverage

Health

Knowledge Graph

before future simulations.

---

# Priority 9 — Repository Performance

Observation

GitHub API dominates execution time.

Future Improvements

Caching

Incremental synchronization

Parallel collection

Graph persistence

---

# Priority 10 — External Signals

Current Intelligence Uses

Commits

Future Evidence Sources

Pull Requests

Reviews

Issues

Discussions

CI/CD

Releases

CODEOWNERS

Team Membership

---

# Long-Term Vision

Transform PIA from

Repository Analytics

into

Organizational Intelligence

that continuously learns,

predicts,

and recommends organizational decisions based on evolving software development activity.
