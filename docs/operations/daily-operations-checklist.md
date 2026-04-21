# Daily Operations Checklist

Purpose: define the minimum before-use and after-use routine for one operator running research,
sandbox, paper, or guarded-live flows.

## When To Run

- at the start of each working session
- before launching or resuming sandbox or guarded-live activity
- at the end of the session if any runtime or live-affecting work occurred

## Product Surfaces

- control-room runtime workspace
- control-room guarded-live workspace
- run history and comparison surfaces
- incident, delivery-history, and audit-oriented panels

## Start-Of-Session Checklist

1. Review market-data freshness, sync failures, and active gap windows.
2. Review active sandbox, paper, and guarded-live sessions.
3. Review stale heartbeat, worker-failure, and incident signals.
4. Review the most recent benchmark comparison or rerun evidence for any strategy you plan to act on.
5. Confirm whether any session should remain running, be held, be rerun, or be stopped before new work begins.

## Before Launching A New Run

1. Confirm the strategy version, dataset boundary, preset, and benchmark family you intend to use.
2. Confirm whether the launch is research, sandbox, paper, or guarded-live. Do not blur those lanes.
3. Confirm stop conditions are understood for the strategy and mode you are about to run.
4. For guarded-live, confirm reconciliation readiness and kill-switch posture before launch.

## During Active Operation

1. Keep active-session views separate from historical review. Do not infer runtime health only from archived runs.
2. Treat stale data, heartbeat loss, unexplained drift, and reconciliation mismatch as interrupt conditions.
3. Prefer product-visible stop, hold, rerun, compare, acknowledge, escalate, and recover actions over shell-only handling.

## End-Of-Session Checklist

1. Record notable operator decisions in durable product surfaces where possible.
2. Review whether any incidents remain unresolved or unacknowledged.
3. Review whether any active sessions were intentionally left running and why.
4. Capture missing runbook or UX gaps discovered during the session for the release/docs checklist.

## Escalate Immediately If

- market data is stale and active execution depends on it
- sandbox or guarded-live heartbeat is missing without a clear recovery path
- benchmark drift is unexplained for a strategy under promotion consideration
- reconciliation or audit posture is unclear for a live-affecting flow

## Related Runbooks

- [Data Incident Response](data-incident-response.md)
- [Sandbox Runtime Incident](sandbox-runtime-incident.md)
- [Guarded-Live Reconciliation Drill](guarded-live-reconciliation-drill.md)
- [Kill-Switch Procedure](kill-switch-procedure.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
