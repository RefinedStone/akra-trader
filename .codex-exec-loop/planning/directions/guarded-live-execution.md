# Guarded live execution

- Direction id: `guarded-live-execution`

## Goal

Keep live readiness gated by configuration, audit, operator events, kill switch, reconciliation,
recovery, and venue lifecycle evidence.

## Current status on May 11, 2026

- Guarded-live control-plane coverage is real.
- Full venue-native lifecycle recovery, deployment discipline, and validated drills remain open.

## Immediate gaps

- explicit recovery scope per venue
- reconciliation and kill-switch drills validated through product UX
- deployment, backup, and credential-governance discipline
- clearer order-management posture beyond cancel/replace

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/README.md`
- `docs/operations/runbooks-overview.md`
