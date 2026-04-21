# Sandbox Runtime Incident

Purpose: define what to do when a sandbox or paper runtime stops behaving like a trustworthy active
session.

## Trigger Conditions

- worker heartbeat loss
- worker crash or restart failure
- unexplained drift or order behavior
- lag, fills, or positions no longer match operator expectations

## Product Surfaces

- runtime workspace active-session views
- sandbox and paper history surfaces
- worker health, heartbeat, and audit-oriented panels
- comparison and rerun controls

## Triage

1. Identify the affected session, strategy version, symbol, and mode.
2. Check heartbeat, recent progress, and any visible recovery history.
3. Check whether the issue is worker liveness, stale market data, strategy drift, or order-state confusion.
4. Decide whether the safest immediate action is hold, stop, rerun, or compare.

## Immediate Actions

1. Stop the session if heartbeat is missing and recovery state is unclear.
2. Hold promotion decisions if recent decisions or order behavior cannot be explained.
3. Use rerun or compare only after confirming the data boundary is defensible.
4. Keep paper incidents separate from sandbox incidents in the operator record even if the UI feels similar.

## Recovery Path

1. If the session recovered automatically, verify that the recovered state is still safe to trust.
2. If the session did not recover, stop it and record the failure mode before relaunching.
3. If drift is the concern, compare against the expected benchmark or prior run before resuming confidence.
4. If the incident exposed a missing stop rule, promotion rule, or UI clue, record it for release follow-up.

## Escalate If

- heartbeat continues to drop after restart attempts
- recent decisions or fills cannot be reconciled with visible state
- active-session health cannot be distinguished from archived history
- the operator must rely on shell access to understand what the session is doing

## Closeout Record

Record at minimum:

- affected run or session
- mode and strategy version
- stop, hold, rerun, compare, or recover action taken
- whether the incident was due to data, runtime, strategy logic, or operator clarity

## Related Runbooks

- [Daily Operations Checklist](daily-operations-checklist.md)
- [Data Incident Response](data-incident-response.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
