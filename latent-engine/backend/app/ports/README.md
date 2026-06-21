# Ports Layer

The ports layer defines the boundaries of the core system.

## Philosophy

The core should never depend on:

- GitHub
- Jira
- Slack
- GitLab
- Azure DevOps

Instead, it depends only on abstract capabilities.

## Current Ports

### EventSourcePort

Provides normalized domain Events from an external source.

```text
Application

↓

EventSourcePort

↓

Domain Events