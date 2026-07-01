# Research Findings - Milestone 42

## Summary

M42 adds the first durable persistence boundary for PIA. The goal is not to choose the final production database, but to stop relying exclusively on in-memory runtime state.

## Findings

- JSONL is sufficient for deterministic local replay and smoke tests.
- Append-only records match the Observation and Measurement architecture.
- Full object rehydration should be designed after stable schemas are finalized.

## Remaining Work

- Add repository interfaces above JSONL.
- Add indexing and query filters.
- Add transactional writes for multi-record pipeline commits.
- Add production backends such as SQLite, DuckDB, Postgres, or object storage.

