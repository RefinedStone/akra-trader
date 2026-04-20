# Runtime ops

- Direction id: `runtime-ops`

## Goal

Convert the existing sandbox worker substrate into clear continuous runtime operations with one
control room that reflects real active execution rather than only previews and history.

## Current status on April 21, 2026

- sandbox workers, heartbeat, restart recovery, and stale-runtime visibility already exist
- the remaining work is productization of active-session workflows, not first-time worker creation

## Immediate gaps

- active-session-first UX
- clearer lag, positions, fills, and recent-decision surfaces
- simpler operator guidance around runtime actions and stop rules

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/product-roadmap.md`
- `docs/blueprint/platform-program.md`

## Success criteria

- preview/history runs and active worker sessions are modeled and surfaced separately in backend and
  operator-facing views
- sandbox workers report heartbeat, recoverable state, recent decisions, lag, positions, and fills
  through one operator surface
- alerts connect stale data, worker failure, and runtime health to actionable operator state rather
  than raw background logs
