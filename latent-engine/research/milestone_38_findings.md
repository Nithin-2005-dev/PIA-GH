# Research Findings - Milestone 38

## Summary

M38 turns PIA's growing set of modules into an extensible platform runtime. The main finding is that PIA had enough subsystem breadth that hand-wired construction and independent lifecycle management would become a scaling bottleneck.

## Key Findings

- `IntelligenceContext` demonstrated the need for a shared runtime: services were manually constructed, lifecycle was implicit, and health/config/event concerns were absent.
- A dependency-free in-process runtime is the right first step because the existing codebase is still Python-service oriented and not yet deployed as distributed workers.
- Module capability registration is more useful than only package discovery because future plugins need to advertise what they provide.
- Constructor injection is sufficient for current services, while explicit provider lambdas handle services that still require custom construction.
- Event bus, scheduler, health, and observability can start in-process as stable contracts and later gain distributed backends.

## Technical Notes

- Default platform modules wrap Measurement, Evidence, Estimation, Graph, Forecasting, Simulation, Agent, and Executive without rewriting those packages.
- The platform API protocols define stable internal contracts for future adapters and plugins.
- The event bus includes correlation and trace IDs so later OpenTelemetry integration has a natural boundary.

## Suggested Next Steps

- Replace direct service construction in `IntelligenceContext` with platform DI resolution.
- Add adapters from existing measurement/evidence plugin systems into `PluginRegistry`.
- Add contract tests for layer communication through platform interfaces.
- Add persistence-backed event replay and scheduler leases when the runtime moves beyond one process.

