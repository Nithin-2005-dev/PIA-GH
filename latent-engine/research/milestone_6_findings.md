# Milestone 6 Findings

## Observation 1

Decision making should be separated from expertise estimation.

Expertise answers:

Who knows what?

Decision answers:

What should we do?

These concerns should remain independent.

---

## Observation 2

Reviewer recommendation is a coverage problem.

The goal is not:

Who has the highest expertise?

The goal is:

Who understands the largest portion of the change?

Coverage therefore became the first recommendation strategy.

---

## Observation 3

Recommendation logic should be policy-driven.

The recommendation service delegates ranking to RecommendationPolicy.

This enables future implementations:

* Ownership recommendation
* Workload-aware recommendation
* Availability-aware recommendation
* Hybrid recommendation
* LLM-assisted recommendation

without modifying service orchestration.

---

## Observation 4

EntityRef remains the universal identity abstraction.

ReviewerRecommendation stores reviewer_ref rather than raw strings.

This preserves compatibility across future sources.

Examples:

* GitHub users
* GitLab users
* Jira users
* Slack users

---

## Observation 5

Current recommendations are expertise-only.

The system does not yet consider:

* recency
* reviewer workload
* ownership
* organizational structure
* availability

These signals should be introduced through additional policies.

---

## Key Insight

PIA has evolved from:

Activity
↓
Knowledge

to:

Activity
↓
Knowledge
↓
Decision

This establishes the foundation for organizational intelligence.
