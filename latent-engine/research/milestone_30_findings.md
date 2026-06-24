# M30 Scenario Intelligence Research

## Research Objective

Determine the smallest architecture required to evolve PIA from:

```text
Current Intelligence
+
Forecast Intelligence
```

into:

```text
Scenario Intelligence
```

without duplicating existing forecasting, simulation, intervention, or executive intelligence services.

---

# Initial Hypothesis

PIA already contained:

* Health Intelligence
* Ownership Intelligence
* Forecast Intelligence
* Executive Intelligence

The assumption was that scenario intelligence could be implemented primarily as an orchestration layer.

Research focused on identifying:

```text
What intelligence already exists?
What intelligence is missing?
What should be reused?
```

---

# Audit 1 — Scenario Foundations

## Question

Does a generic scenario framework already exist?

## Findings

No reusable scenario abstraction existed.

No common future-state model existed.

No comparison engine existed.

## Gap

Missing:

```text
ScenarioOutcome
ScenarioExecutionService
StrategyComparisonService
```

## Result

M30.1 created the foundation layer.

---

# Audit 2 — Departure Scenario Intelligence

## Question

Can PIA already simulate developer departures?

## Findings

Simulation capability already existed through:

```text
SimulationService
DeveloperDeparturePolicy
SimulationAdapter
```

However:

```text
SimulationAdapter
```

was tightly coupled to the reasoning layer.

No reusable scenario service existed.

## Gap

Missing:

```text
DepartureScenarioRequest
DepartureScenarioService
```

## Architectural Decision

Reuse:

```text
OwnershipService
SuccessorService
ReadinessService
HealthService
SimulationService
```

Do not create new simulation logic.

## Result

M30.2 introduced reusable departure scenarios.

---

# Audit 3 — Intervention Scenario Intelligence

## Question

Can PIA already estimate intervention effects?

## Findings

Existing capability:

```text
InterventionImpactService
```

already computes:

```text
expected_health_gain
```

using:

```text
coverage
concentration
forecast severity
```

No scenario orchestration existed.

## Gap

Missing:

```text
InterventionScenarioService
```

## Architectural Decision

Reuse:

```text
InterventionImpactService
ScenarioExecutionService
```

and compute:

```text
predicted_health
=
baseline_health
+
expected_health_gain
```

without modifying intervention intelligence.

---

# Audit 4 — Forecast Dependency Discovery

## Problem Encountered

M30.3 failed with:

```text
No severity report for payments.py
```

## Investigation

Research revealed:

```text
FutureRiskPipelineService
```

depends on:

```text
HistoryService
↓
ForecastPipelineService
↓
ForecastSeverityService
```

and therefore requires:

```text
historical health reports
```

## Root Cause

Test bootstrapping created:

```text
expertise history
```

but not:

```text
health history
```

## Resolution

Reused the same:

```text
seed_history(...)
```

approach already used by:

```text
test_organization_risk_service.py
test_organization_dashboard.py
```

## Important Insight

Forecast intelligence is grounded in:

```text
HealthProjection
```

rather than expertise estimates.

---

# Audit 5 — Combined Strategy Scenarios

## Initial Idea

Research originally explored:

```text
Knowledge Transfer
↓
Successor Readiness Improves
↓
Departure Impact Reduced
```

## Verification

Repository-wide inspection showed interventions currently affect:

```text
Health
Future Risk
```

but do NOT affect:

```text
Readiness
Ownership
Bus Factor
Concentration
```

## Key Finding

Current intelligence model does not support:

```text
Intervention
↓
Readiness Improvement
```

Therefore:

```text
Knowledge Transfer
then
Alice Leaves
```

cannot be modeled honestly.

Doing so would invent behavior not supported by the repository.

## Architectural Decision

M30.4 would compare:

```text
Departure Strategies
```

against:

```text
Intervention Strategies
```

rather than attempting to chain them.

---

# Rejected Designs

## Rejected Design 1

```text
InterventionSimulationService
```

Reason:

Duplicates:

```text
InterventionImpactService
SimulationService
```

---

## Rejected Design 2

```text
Intervention modifies readiness
```

Reason:

No repository evidence supports this relationship.

---

## Rejected Design 3

```text
Scenario-specific forecasting engine
```

Reason:

ForecastPipelineService already exists.

---

# Final Architecture

```text
                    StrategyScenarioService
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ▼                                         ▼

DepartureScenarioService            InterventionScenarioService
          │                                         │
          ▼                                         ▼

SimulationResult                    ScenarioOutcome
          │                                         │
          └──────────────┬──────────────────────────┘
                         ▼

              StrategyComparisonService
```

---

# Research Conclusions

## What M30 Added

PIA can now evaluate:

```text
Owner Departure
```

```text
Knowledge Transfer
```

```text
Training Strategies
```

and compare them within a common framework.

---

## What M30 Explicitly Does NOT Model

```text
Intervention
↓
Readiness Change
↓
Ownership Change
↓
Bus Factor Change
```

These remain future research topics.

---

# Future Research

Potential M31 directions:

## Scenario Grounding

Replace synthetic:

```text
baseline_health + expected_gain
```

with grounded forecast recomputation.

---

## Intervention State Mutation

Allow interventions to modify:

```text
readiness
ownership
bus factor
```

before scenario execution.

---

## Multi-Step Scenarios

Support:

```text
Intervention
↓
Departure
↓
Forecast
```

as a single scenario graph.

---

# Outcome

M30 successfully transformed PIA from:

```text
Forecasting Intelligence
```

into:

```text
Scenario Intelligence
```

using orchestration and reuse of existing intelligence services rather than introducing duplicate analytical models.
