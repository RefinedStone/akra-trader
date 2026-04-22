# Guarded live execution

- Direction id: `guarded-live-execution`

## Goal

Make live candidacy a gated safety program, not an execution shortcut, by requiring audit coverage,
operator events, risk controls, kill switch behavior, and reconciliation before any venue-backed
live path is treated as operationally ready.

## Current status on April 22, 2026

- kill switch, reconciliation, recovery, incidents, delivery history, and venue-backed launch gates
  already exist
- reconciliation and kill-switch drill baselines are now documented under `docs/operations/*`
- the remaining work is completeness of venue lifecycle, candidacy rules, drills, and deployment
  discipline

## Immediate gaps

- broader venue-native lifecycle recovery
- clearer guarded-live drill and candidacy rules
- deployment and credential discipline
- fuller order-management posture beyond the current baseline
- close remaining audit and operator-event gaps across live-affecting actions

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/next-wave-plan.md`
- `docs/blueprint/platform-program.md`

## Success criteria

- live-affecting actions are blocked unless safety configuration, audit capture, and operator event
  logging are present
- reconciliation and emergency-stop drills are first-class product flows rather than ad hoc procedures
- live candidacy is explicit and distinct from sandbox worker readiness, with promotion blocked until
  safety gates pass
