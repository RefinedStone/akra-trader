# Kill-Switch Procedure

Purpose: define when to engage, verify, and release guarded-live emergency stop controls.

## Trigger Conditions

- reconciliation mismatch with live exposure
- unknown or unsafe venue-session state
- missing auditability for live-affecting actions
- unexplained live order behavior
- operator confidence in live continuity falls below a safe threshold

## Product Surfaces

- guarded-live kill-switch control
- guarded-live incidents and delivery history
- recovery and reconciliation panels
- live order, fill, and position views

## Engage Procedure

1. Treat the kill switch as a safety action, not a diagnostic shortcut.
2. Engage the kill switch immediately when live state is unsafe or unknown.
3. Record the operator reason as part of the product-visible action.
4. Verify that the incident and delivery surfaces reflect the stop condition.

## After Engagement

1. Do not reopen live readiness until reconciliation is run.
2. Review live orders, fills, positions, and session ownership.
3. Review whether the stop condition was caused by data, runtime, venue state, or audit gaps.
4. If remediation requires additional live-affecting actions, keep them explicitly tied to the incident record.

## Release Procedure

1. Run the guarded-live reconciliation drill.
2. Confirm the original trigger condition is resolved or explicitly bounded.
3. Confirm audit history is complete enough to explain the stop and recovery.
4. Release the kill switch only when the session is safe enough to trust again.

## Escalate If

- reconciliation cannot establish a safe state after the kill switch is engaged
- live order state cannot be matched to venue-backed facts
- the operator is relying on memory rather than durable product-visible records

## Closeout Record

Record at minimum:

- who engaged the kill switch and why
- what live exposure existed at the time
- what reconciliation outcome justified release or continued hold
- whether the session returned to ready, remained blocked, or was terminated

## Related Runbooks

- [Guarded-Live Reconciliation Drill](guarded-live-reconciliation-drill.md)
- [Daily Operations Checklist](daily-operations-checklist.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
