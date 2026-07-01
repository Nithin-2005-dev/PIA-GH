# Research Findings — Milestone 37

These findings summarize the work captured from the uncommitted changes that followed Milestone 36.

## Summary

Milestone 37 focused on making the canonical intelligence pipeline more reliable and more explainable. The most important gains came from improving evidence synthesis, strengthening measurement calibration, and connecting the showcase pipeline to richer reasoning and decision outputs.

## Key Findings

- Evidence synthesis is more stable when rules are evaluated after grouping measurements by entity. This improves the quality of generated evidence and reduces spurious or fragmented facts.
- Statistical calibration adds useful normalization for measurement populations and helps downstream confidence and percentile-based reasoning behave more consistently.
- Developer and subsystem attribution become more reliable when canonical identity and boundary resolution are used together. That improves ownership analysis and reduces noise in knowledge mapping.
- The showcase pipeline now covers a more complete path from observations to executive intelligence, but live execution still depends on environment context such as repo access and credentials.

## Technical Notes

- The new measurement evaluators provide better signals for ownership concentration and developer activity.
- The reasoning and summary stages now produce more structured outputs that are easier to inspect and reason about.
- The pipeline remains dependent on a good source of observations and measurements, so repository quality and token availability remain practical bottlenecks.

## Suggested Next Steps

- Add regression tests for the new calibration and ownership logic.
- Expand the showcase fixtures so it can run without live GitHub access.
- Capture more temporal snapshots so forecasting and trend analysis can be demonstrated end to end.
