# Documentation

`docs/status/current-state.md` is the source of truth for what exists now. Other docs should stay
short and should not repeat implementation logs.

## Read These

1. [Current State](status/current-state.md)
2. [Architecture](architecture.md)
3. [Roadmap](roadmap/README.md)
4. [Operations](operations/runbooks-overview.md)
5. [Blueprint](blueprint/README.md)
6. [ADR Index](adr/README.md)

## Document Roles

- `status/current-state.md`: implemented capability, known gaps, and next priorities.
- `architecture.md`: current module boundaries, decomposition rules, and active pressure points.
- `roadmap/README.md`: remaining work only. Completed delivery logs do not belong here.
- `operations/runbooks-overview.md`: one-page operator checklist and escalation rules.
- `blueprint/README.md`: durable product principles and non-goals. It is not an execution board.
- `adr/*`: historical decisions. ADR bodies may describe old context; read `current-state` first.

## Maintenance Rule

When a meaningful feature changes:

1. Update `status/current-state.md`.
2. Update `roadmap/README.md` or `operations/runbooks-overview.md` only if the remaining work or
   operator workflow changed.
3. Update `architecture.md` only if ownership boundaries changed.
4. Update `blueprint/README.md` only if a durable principle or non-goal changed.

Delete or merge documents that become historical policy, execution logs, or duplicate status.
