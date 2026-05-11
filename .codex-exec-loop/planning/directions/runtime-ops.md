# Runtime ops

- Direction id: `runtime-ops`

## Goal

Make sandbox and paper operation reflect active execution state, not only launch forms and history.

## Current status on May 11, 2026

- Workers persist heartbeat, progress, and recovery state.
- The main gap is operator clarity around active sessions, decisions, lag, positions, fills, and
  stop/hold actions.

## Immediate gaps

- active-session-first workspace views
- clearer lag, position, fill, and recent-decision surfaces
- simpler stop/hold/rerun/compare guidance
- continued control-room flow decomposition

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/README.md`
- `docs/operations/runbooks-overview.md`
