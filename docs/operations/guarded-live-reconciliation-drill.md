# Guarded-Live Reconciliation Drill

Purpose: define the minimum operator drill for verifying that local guarded-live state still matches
venue reality before trusting live continuity.

## When To Run

- before guarded-live launch
- after guarded-live recovery or resume
- when venue state, local state, or audit history looks inconsistent
- before releasing a kill switch after a live-affecting incident

## Product Surfaces

- guarded-live candidacy and blocker panels
- venue snapshot and recovery state panels
- order, fill, and position history tied to the live session
- incident, delivery-history, and audit-oriented views

## Drill

1. Confirm guarded-live is allowed by configuration and current safety gates.
2. Confirm the intended venue, symbol, strategy, and session owner.
3. Review open-order, fill, and position state in local surfaces.
4. Review venue-backed snapshot and reconciliation output.
5. Verify that mismatches are either zero or explicitly understood before continuing.
6. Verify that recent incidents, acknowledgments, escalations, and remediation state are current.
7. Verify that kill-switch posture is known before resuming trust in live continuity.

## Blocking Conditions

Do not treat the live path as ready if any of the following are true:

- reconciliation mismatch is unresolved
- session ownership is unclear
- venue snapshot and local order state disagree without explanation
- recovery state is incomplete
- audit coverage is missing for the actions that changed live state

## Allowed Actions

- stop or hold live readiness
- acknowledge, escalate, remediate, or recover through product-visible flows
- cancel or replace active orders only when reconciliation posture is clear enough to justify it

## Escalate If

- reconciliation mismatch persists after one clear operator pass
- venue-native lifecycle state cannot be reconstructed from product-visible records
- the operator cannot state whether the session is safe, unsafe, or unknown

## Closeout Record

Record at minimum:

- the session and venue checked
- whether reconciliation passed, failed, or remained unknown
- what blocking condition was cleared or left open
- what live-affecting actions were taken during the drill

## Related Runbooks

- [Kill-Switch Procedure](kill-switch-procedure.md)
- [Daily Operations Checklist](daily-operations-checklist.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
