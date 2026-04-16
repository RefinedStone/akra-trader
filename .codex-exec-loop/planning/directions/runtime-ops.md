# Runtime ops

- Direction id: `runtime-ops`

## Goal

Convert replay-style sandbox semantics into continuous runtime operations with worker sessions, heartbeat, restart recovery, runtime health, and a control room that reflects real active execution rather than previews.

## Success criteria

- Preview runs and active worker sessions are modeled and surfaced separately in backend and operator-facing views.
- Sandbox workers report heartbeat, recoverable state, recent decisions, lag, positions, and fills through one operator surface.
- Alerts connect stale data, worker failure, and runtime health to actionable operator state rather than raw background logs.

## Scope hints

- Use docs/blueprint/platform-program.md Workstream C, docs/blueprint/operating-model.md, and docs/blueprint/metrics-and-gates.md Gate 2 as the controlling guidance.
- Favor worker-session semantics, runtime recoverability, and operator-visible health over premature live exchange work.
- Preserve the shared runtime core; mode differences should stay in adapters, policies, and supervision layers.
