# Guarded live execution

- Direction id: `guarded-live-execution`

## Goal

Make live candidacy a gated safety program, not an execution shortcut, by requiring audit coverage, operator events, risk controls, kill switch behavior, and reconciliation before any venue-backed live path is considered real.

## Success criteria

- Live-affecting actions are blocked unless safety configuration, audit capture, and operator event logging are present.
- Reconciliation and emergency-stop drills are first-class product flows rather than ad hoc procedures.
- Live candidacy is explicit and distinct from sandbox worker readiness, with promotion blocked until safety gates pass.

## Scope hints

- Use docs/blueprint/platform-program.md Workstream D, docs/blueprint/metrics-and-gates.md Gate 3, and docs/blueprint/risk-register.md Risk 5 as the governing rules.
- Do not ship execution-first shortcuts or unattended live behavior before audit and reconciliation exist.
- Treat account state, exposure state, operator events, audit views, and reconciliation results as required interfaces.
