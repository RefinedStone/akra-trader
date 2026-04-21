# Documentation Index

This directory is organized around one rule:

- `docs/status/current-state.md` is the single source of truth for what is implemented now.

Everything else should either explain the current system, describe the remaining work, or define the
longer-horizon blueprint.

## Reading Order

1. [Status: Current State](status/current-state.md)
2. [Status: Product Position](status/product-position.md)
3. [Roadmap Overview](roadmap/README.md)
4. [Roadmap: Next Wave Plan](roadmap/next-wave-plan.md)
5. [Roadmap: Directions Execution Board](roadmap/directions-execution-board.md)
6. [Architecture](architecture.md)
7. [LLM Sensitivity](architecture-llm-sensitivity.md)
8. [Backend Architecture Target](architecture-backend-target.md)
9. [Frontend Architecture Target](architecture-frontend-target.md)
10. [Architecture Refactor Stages](architecture-refactor-stages.md)
11. [Blueprint](blueprint/README.md)
12. [Operations: Runbooks Overview](operations/runbooks-overview.md)
13. [ADR Index](adr/README.md)

## Document Roles

### Status

- `status/current-state.md`
  - canonical statement of implemented capability, partial areas, and missing work
- `status/product-position.md`
  - clarifies what product this is today and what it is not

### Roadmap

- `roadmap/*`
  - remaining work after the current-state baseline
  - near-term delivery waves, epics, and technical priorities
  - `roadmap/directions-execution-board.md` is the execution-oriented view that turns roadmap and
    internal directions into one ordered delivery board

### Architecture

- `architecture.md`
  - current boundary rules and the live refactor baseline
- `architecture-llm-sensitivity.md`
  - the practical definition of LLM sensitivity, anti-patterns, and review questions
- `architecture-backend-target.md`
  - backend target structure, boundary rules, and first-wave move map
- `architecture-frontend-target.md`
  - frontend target structure, route/shell split, and remaining pressure points
- `architecture-refactor-stages.md`
  - staged execution order and exit criteria for the architecture reset

### Blueprint

- `blueprint/*`
  - 6-9 month intent, gating logic, operating model, and risk documents
  - these documents must not be used as the source of truth for implementation status

### Operations

- `operations/*`
  - operator workflows, runbooks, checklists, and discipline documents

### Reference

- `reference*` and `reference/*`
  - reference notes, adoption notes, and detailed implementation matrices that should not bloat the
    core product docs

## Internal Planning Directions

The internal planning directions also participate in the documentation contract:

- `.codex-exec-loop/planning/directions/*.md`

Those files should stay aligned with `status`, `roadmap`, and `blueprint`. They are short direction
documents, not substitutes for the canonical status docs.

## Maintenance Rule

Whenever a meaningful feature changes, update:

1. `status/current-state.md`
2. at least one relevant roadmap or operations document
3. blueprint wording only if the long-horizon intent or gate changed
