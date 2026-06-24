# PIA Architecture Snapshot (M28)

## Overview

PIA is an organizational intelligence platform that derives expertise, ownership, health, forecasting, succession, transfer planning, simulation, and organization-level insights from repository activity.

---

# Data Flow

```text
GitHub
    │
    ▼
Events
    │
    ▼
Evidence Extraction
    │
    ▼
Evidence
    │
    ▼
Expertise Projection
    │
    ▼
Expertise Estimates
```

---

# Expertise Intelligence

```text
Expertise Estimates
        │
        ▼
Expertise Query Service
        │
        ▼
Module Experts
```

Outputs:

* Top Experts
* Expert Rankings
* Knowledge Distribution

---

# Ownership Intelligence

```text
Expertise Estimates
        │
        ▼
Ownership Service
        │
        ▼
Ownership Estimates
```

Outputs:

* Primary Owners
* Contributors
* Ownership Rankings

---

# Coverage Intelligence

```text
Expertise Estimates
        │
        ▼
Coverage Service
        │
        ▼
Coverage Reports
```

Measures:

* Expert Count
* Coverage Score
* Coverage Level

---

# Concentration Intelligence

```text
Expertise Estimates
        │
        ▼
Concentration Service
        │
        ▼
Concentration Reports
```

Measures:

* Knowledge Concentration
* Concentration Risk

---

# Bus Factor Intelligence

```text
Ownership Estimates
        │
        ▼
Bus Factor Service
        │
        ▼
Bus Factor Reports
```

Measures:

* Failure Sensitivity
* Single Point Dependency

---

# Health Intelligence

```text
Coverage
Concentration
Bus Factor
        │
        ▼
Health Service
        │
        ▼
Health Reports
```

Produces:

* Health Score
* Health Level

---

# Historical Intelligence

```text
Health Reports
        │
        ▼
Health Projection
        │
        ▼
Health History
```

Maintains:

* Historical Health Snapshots
* Module Health Timelines

---

# Trend Intelligence

```text
Health History
        │
        ▼
Trend Analyzer
        │
        ▼
Health Trend
```

Produces:

* Delta
* Slope
* Direction

---

# Forecast Intelligence

```text
Health Trend
        │
        ▼
Forecast Service
        │
        ▼
Forecast
```

Produces:

* Current Health
* Predicted Health
* Forecast Risk Level

---

# Future Risk Intelligence

```text
Forecast
        │
        ▼
Future Risk Service
        │
        ▼
Future Risk
```

Measures:

* Predicted Deterioration

---

# Severity Intelligence

```text
Forecast
        │
        ▼
Forecast Severity Service
        │
        ▼
Forecast Severity
```

Produces:

* LOW
* MODERATE
* HIGH
* EXTREME

---

# Successor Intelligence

```text
Ownership
Expertise
        │
        ▼
Successor Service
        │
        ▼
Successor Candidates
```

Produces:

* Replacement Candidates
* Succession Options

---

# Readiness Intelligence

```text
Successor Candidates
Expertise
        │
        ▼
Readiness Service
        │
        ▼
Successor Readiness
```

Measures:

* Takeover Readiness
* Succession Strength

---

# Transfer Intelligence

```text
Ownership
Successors
Concentration
        │
        ▼
Transfer Service
        │
        ▼
Transfer Plans
```

Produces:

* Mentor
* Learner
* Priority
* Transfer Recommendation

---

# Simulation Intelligence

```text
Health
Ownership
Readiness
        │
        ▼
Simulation Service
        │
        ▼
Simulation Result
```

Answers:

* What happens if Alice leaves?
* What happens if Bob leaves?
* What is the impact of losing a key expert?

---

# Organization Intelligence Layer (M28)

## Organization Risk

```text
Future Risks
        │
        ▼
Organization Risk Service
```

Outputs:

* Top Organizational Risks
* Risk Rankings

---

## Organization Health

```text
Health Reports
        │
        ▼
Organization Health Service
```

Outputs:

* Average Health
* Best Health
* Worst Health
* Healthy Module Count
* Warning Module Count
* Critical Module Count

---

## Organization Readiness

```text
Readiness Scores
        │
        ▼
Organization Readiness Service
```

Outputs:

* Weakest Successor Benches
* Succession Risk Rankings

---

## Organization Transfer

```text
Transfer Plans
        │
        ▼
Organization Transfer Service
```

Outputs:

* Highest ROI Knowledge Transfers
* Organizational Training Priorities

---

## Executive Dashboard

```text
Organization Health
Organization Risk
Organization Readiness
Organization Transfer
            │
            ▼
Organization Dashboard
```

Answers:

* What is our biggest risk?
* Which modules need attention?
* Where should we invest training?
* What should leadership focus on?

---

# Agent Layer

```text
Question
    │
    ▼
Intent Classifier
    │
    ▼
Context Extractor
    │
    ▼
Tool Router
    │
    ▼
Grounded Adapters
```

Adapters:

* Risk Adapter
* Forecast Adapter
* Successor Adapter
* Transfer Adapter
* Intervention Adapter
* Simulation Adapter

All major adapters are grounded through `IntelligenceContext`.

---

# Milestone Evolution

```text
M1–M18
    Expertise & Ownership Intelligence

M19–M22
    Forecasting & Simulation

M23–M27
    Grounded Agent Intelligence

M28
    Organization Intelligence Layer
```

---

# Current Capability

PIA can now model:

* Expertise
* Ownership
* Coverage
* Concentration
* Bus Factor
* Health
* Historical Trends
* Forecasting
* Future Risk
* Severity
* Successor Planning
* Readiness
* Knowledge Transfer
* Departure Simulation
* Organization-wide Risk Prioritization
* Executive Dashboards

This represents the end-state architecture at Milestone 28 before moving into recommendation and decision-support capabilities.
