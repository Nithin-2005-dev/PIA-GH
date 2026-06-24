# Milestone 4 - Evidence to Expertise Estimation

Status: Completed

## Objective

Transform Evidence into continuously evolving Expertise Estimates.

## Architecture

GitHub

↓

Event

↓

Evidence

↓

Expertise Estimator

↓

Expertise Estimate

## Implemented Components

### EvidenceScoringPolicy

Strategy abstraction for evaluating Evidence contributions.

Supported future implementations:

- Rule Based
- Bayesian
- Machine Learning
- Graph Neural Networks
- LLM Reasoning

### RuleExpertiseScoringPolicy

Initial scoring implementation.

Examples:

- MODIFIED = 1.0
- REVIEWED = 2.0
- FIXED = 5.0

### ExpertiseEstimator

Implements latent state transitions.

Inputs:

- Current Estimate
- Evidence
- Estimation Context

Output:

- Updated Estimate

### ExpertiseProjection

Maintains expertise state for all observed:

Developer ↔ Module

relationships.

### ExpertiseEstimateFactory

Creates initial expertise states.

## Estimation Formula

base_score =
    current_score × decay_factor

contribution =
    policy_score × evidence_confidence × learning_rate

new_score =
    base_score + contribution

## Validation

Successfully executed:

GitHub
↓
Event
↓
Evidence
↓
Expertise Estimate

using live facebook/react commits.

## Outcome

The system now maintains continuously evolving expertise state derived from observed developer activity.

## Next Milestone

Milestone 5 - Expertise Graph and Query Engine