# Runbooks Overview

Updated for the repository state as of April 21, 2026.

This folder is the entry point for day-2 operator discipline. The current repository has many
runtime and guarded-live features, but its runbook coverage is still incomplete. This document
defines the minimum set that should exist as the platform matures.

## Required Runbook Set

| Runbook | Purpose | Current status |
| --- | --- | --- |
| Daily operations checklist | What to inspect before and after normal use | missing |
| Data incident response | Stale sync, repeated failures, gap escalation | missing |
| Sandbox runtime incident | Worker failure, heartbeat loss, unexplained drift | missing |
| Guarded-live reconciliation drill | How to verify venue state and respond to mismatches | missing |
| Kill-switch procedure | When and how to engage, verify, and release emergency stop | missing |
| Release and docs checklist | How to keep docs aligned with feature changes | missing |

## Minimum Daily Checklist

1. Review market-data freshness, recent failures, and active gap windows.
2. Review active sandbox and guarded-live sessions.
3. Review recent incidents, delivery failures, and unresolved acknowledgments.
4. Confirm whether any strategy or runtime state requires stop, hold, rerun, or compare actions.
5. Record notable operator decisions in durable product surfaces where possible.

## Runbook Design Rules

- prefer operator-visible product actions over shell-only instructions
- record what to inspect, what actions are allowed, and what must be escalated
- link each runbook to the relevant product surface and blocking condition
- keep guarded-live procedures stricter than sandbox procedures

## Related Docs

- [Current State](../status/current-state.md)
- [Product Position](../status/product-position.md)
- [Next Wave Plan](../roadmap/next-wave-plan.md)
- [Operating Model](../blueprint/operating-model.md)
