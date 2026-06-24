# Current PIA Architecture (M1-M9)

## Flow

GitHub

↓

Events

↓

Evidence Extraction

↓

Evidence

↓

Expertise Estimation

↓

Time-Aware Expertise

↓

Query Layer

↓

Ownership Layer

↓

Risk Layer

---

## Layers

### Domain Layer

Core business concepts:

* Event
* Evidence
* ExpertiseEstimate
* OwnershipEstimate
* BusFactor

---

### Adapter Layer

External system integration:

* GitHubAdapter
* GitHubRestGateway

---

### Extractor Layer

Transforms Events into Evidence.

Policies:

* GitHubCommitStrengthPolicy

---

### Estimator Layer

Transforms Evidence into Expertise.

Policies:

* RuleExpertiseScoringPolicy
* ExponentialDecayPolicy

---

### Query Layer

Provides expertise retrieval and ranking.

Capabilities:

* Top Experts

---

### Decision Layer

Provides reviewer recommendations.

Policies:

* CoverageRecommendationPolicy

---

### Ownership Layer

Transforms expertise into ownership.

Policies:

* ExpertiseOwnershipPolicy

---

### Risk Layer

Transforms ownership into organizational risk.

Policies:

* OwnershipBusFactorPolicy

---

## Current Capability Graph

Activity

↓

Knowledge

↓

Ownership

↓

Risk

---

## Milestone Status

M1 Domain Kernel

M2 GitHub Event Collection

M3 Evidence Extraction

M4 Expertise Estimation

M5 Query Layer

M6 Reviewer Recommendation

M7 Time-Aware Expertise

M8 Ownership Detection

M9 Bus Factor Analysis
