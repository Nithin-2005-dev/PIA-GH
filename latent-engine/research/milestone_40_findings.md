# Research Findings - Milestone 40

## Summary

M40 clarified the architectural boundary between measurement and evidence. Measurement answers "what can be quantified from this observation?" Evidence will later answer "what does it mean?"

## Key Findings

- The existing measurement layer already contained strong primitives for validation, confidence, quality, calibration, analytics, benchmarking, and lineage.
- The missing M40 shape was a clean scientific provider framework that is explicitly Observation -> Measurement and platform-resolvable.
- Stable measurement IDs should include observation ID, provider, measurement definition, and provider version to make replay deterministic.
- Provider registration through the Platform Runtime is the right extension point for future structural, semantic, complexity, temporal, ownership-metric, review, repository, documentation, testing, and deployment providers.
- Measurement must not infer expertise, ownership, risk, or business semantics. Those belong to future Evidence and Estimation layers.

## Scoring and Confidence

M40 reuses deterministic validation, confidence, and quality primitives. Confidence is derived from source reliability, coverage, agreement, freshness, historical stability, and missing data penalty. These are reliability properties, not semantic judgments.

## Aggregation and Statistics

The SME includes deterministic aggregation and statistical utilities: sum, mean, median, min, max, percentiles, sliding windows, rolling aggregates, time buckets, histograms, variance, standard deviation, entropy, quantiles, correlation, and distribution summaries.

## Remaining Questions

- Which static-analysis providers should be added first for AST nodes, functions modified, classes modified, imports changed, and dependencies changed?
- Should measurement versions be persisted in a dedicated replay manifest?
- Which benchmark/resource metrics should become production SLOs?

## Suggested Next Steps

- Add AST/static-analysis providers.
- Add persistent measurement version manifests.
- Add durable benchmark history.
- Build M41 Evidence Engine on top of M40 measurements without changing measurement outputs.

