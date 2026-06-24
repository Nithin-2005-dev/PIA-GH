# Milestone 5 - Query Layer and Weighted Evidence

Status: Completed

## Objective

Transform expertise estimates into actionable answers while improving expertise quality through weighted evidence.

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Weighted Evidence

↓

Expertise Estimate

↓

Query Layer

↓

Answers

---

## Implemented Components

### Query Layer

Introduced a dedicated query layer for consuming expertise state.

Files:

* query/query_result.py
* query/expertise_query_service.py

Supported queries:

* top_experts(module_id)
* module_experts(module_id)
* developer_expertise(developer_id)

---

### QueryResult

Encapsulates ranked query results.

Contains:

* ExpertiseEstimate
* effective_score

---

### Expertise Ranking

Current ranking formula:

effective_score =
raw_score × confidence

Purpose:

* raw_score measures expertise magnitude
* confidence measures estimate certainty

Both dimensions are preserved separately.

---

### Evidence Strength Policies

Introduced strength derivation as a separate concern from extraction.

Files:

extractor/policies/

* evidence_strength_policy.py
* github_commit_strength_policy.py

---

### GitHubCommitStrengthPolicy

Maps commit size to contribution magnitude.

Current buckets:

<= 10 changes → 0.1

<= 100 changes → 1.0

<= 500 changes → 3.0

<= 1000 changes → 5.0

> 1000 changes → 10.0

---

### Weighted Evidence

Evidence now contains:

metadata["strength"]

Example:

332 changes

↓

strength = 3.0

---

### Strength-Aware Expertise Estimation

Updated expertise contribution formula:

contribution =
predicate_score
× strength
× confidence
× learning_rate

This allows larger contributions to have greater influence on expertise estimates.

---

## Validation

Successfully executed:

GitHub
↓
Event
↓
Evidence
↓
Weighted Evidence
↓
Expertise Estimate
↓
Query

Validated using live facebook/react commit data.

---

## Outcome

The system can now:

* Identify experts for a module
* Rank expertise estimates
* Distinguish small and large contributions
* Produce actionable organizational intelligence

---

## Next Milestone

Milestone 6 - Reviewer Recommendation Engine
