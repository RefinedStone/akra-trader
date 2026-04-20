# Operator trust and discipline

- Direction id: `operator-trust-and-discipline`

## Goal

Make the control room, alerts, operator events, runbooks, and documentation strong enough for
single-operator daily use, incident response, and promotion decisions without depending on shell
knowledge or drifting docs.

## Current status on April 21, 2026

- the product already exposes meaningful alerts, incidents, reconciliation, and audit-oriented
  control surfaces
- the remaining gap is clarity, runbook discipline, and documentation alignment rather than absence
  of any operator substrate

## Immediate gaps

- active-session-first control-room clarity
- runbook coverage for daily work and incidents
- release-time documentation discipline

## Linked docs

- `docs/status/current-state.md`
- `docs/operations/runbooks-overview.md`
- `docs/blueprint/operating-model.md`

## Success criteria

- the control room can answer what is running, what changed, why it changed, whether it is safe, and
  what the operator should do next
- daily, weekly, and incident workflows from the operating model are supported by product surfaces and
  durable operator-visible records
- current-state, roadmap, blueprint, and operational docs stay aligned as implementation changes over
  time
