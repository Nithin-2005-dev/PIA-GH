# PIA Validation Framework

This document is auto-generated from evaluator metadata and docstrings.

## Developer Activity

**Purpose**
Quantify developer behavioral patterns and knowledge acquisition. Mathematical Basis: Sums absolute churn (additions + deletions). Uses ratio scaling for subsystem focus.

**Assumptions**
Author email/login maps reliably to a single identity.

**Inputs**
Observation (Commits)

**Outputs**
Measurements (developer_knowledge_spread, developer_subsystem_focus, etc.)

**Limitations**
Does not account for non-code contributions (issues/reviews). Expected Accuracy: High (95%+), barring severe identity fragmentation.

## File Ownership

**Purpose**
Identify knowledge silos and key-person dependencies at the file level. Mathematical Basis: Emits 1.0 per touch. Aggregated via sum/mean to yield ownership concentration ratio [0.0, 1.0].

**Assumptions**
Author identity maps correctly. Touches imply knowledge retention.

**Inputs**
Observation (Commits)

**Outputs**
Measurements (file_ownership_score)

**Limitations**
Does not account for reading or code review, only authoring. Expected Accuracy: High (90%+), though may misclassify trivial refactors as ownership.

## Subsystem Activity

**Purpose**
Assess structural risk, knowledge distribution, and volatility at the subsystem level. Mathematical Basis: Gini coefficient for file concentration. Simple sums and ratios for coupling/churn.

**Assumptions**
SubsystemResolver accurately groups files into logical architecture domains.

**Inputs**
Observation (Commits)

**Outputs**
Measurements (subsystem_churn_rate, subsystem_file_concentration, etc.)

**Limitations**
Coupling score is currently bound to single-commit co-changes. Expected Accuracy: High for churn and contributors; moderate for coupling due to single-commit constraint.

