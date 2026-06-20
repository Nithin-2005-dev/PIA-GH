"""
Estimator Layer

Responsibilities:
- Convert Evidence into Latent State Estimates.
- Contain domain algorithms.
- Remain independent of infrastructure.

Rules:
- Never access database directly.
- Never call GitHub API.
- Never mutate state.
- Always return new immutable estimates.
"""