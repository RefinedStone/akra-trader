# Roadmap

Remaining work from the May 11, 2026 implementation snapshot.

## Next Priorities

1. Durable strategy lifecycle
   - persist custom registrations across restarts
   - add lifecycle and promotion records
   - expose lifecycle state in filters and audit views

2. Experiment OS completion
   - normalize common experiment summaries
   - define artifact and export registry paths
   - reduce payload-only scans for common query surfaces

3. Runtime and control-room productization
   - make active sessions the first runtime view
   - clarify lag, positions, fills, recent decisions, stop/hold/rerun/compare actions
   - keep decomposing large control-room sections by operator flow

4. Guarded-live safety completion
   - make venue lifecycle recovery scope explicit per venue
   - validate reconciliation and kill-switch drills against product UX
   - add deployment, backup, and credential-governance discipline

5. Provider and incident ownership
   - continue splitting provider-delivery families
   - clarify which providers are operationally supported versus adapter-compatible
   - add provider-owned incident ownership semantics where needed

6. Intelligence research lane
   - add provider adapters, prompt registry, raw trace storage, replay harness, evaluation, and
     operator review controls
   - keep this lane isolated from live promotion until those controls exist
   - harden trace retention and promotion evidence beyond the first mock-backed judgement layer

## Non-Goals For This Horizon

- multi-user RBAC
- unattended autonomous live trading
- distributed/multi-node execution
- LLM-driven live decisioning

## Documentation Rule

This roadmap lists only unfinished work. Completed delivery notes belong in commit history, not in
roadmap files.
