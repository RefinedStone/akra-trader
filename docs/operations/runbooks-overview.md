# Runbooks Overview

Updated for the repository state as of April 24, 2026.

This folder is the entry point for day-2 operator discipline. The current repository has many
runtime and guarded-live features, but its runbook coverage is still incomplete. This document
defines the minimum set that should exist as the platform matures.

## Required Runbook Set

| Runbook | Purpose | Current status |
| --- | --- | --- |
| [Daily operations checklist](daily-operations-checklist.md) | What to inspect before and after normal use | baseline implemented |
| [Data incident response](data-incident-response.md) | Stale sync, repeated failures, gap escalation | baseline implemented |
| [Operator lineage guidance](operator-lineage-guidance.md) | Dataset-boundary action guidance, retention policy, and drill validation evidence | baseline implemented |
| [Sandbox runtime incident](sandbox-runtime-incident.md) | Worker failure, heartbeat loss, unexplained drift | baseline implemented |
| [Guarded-live reconciliation drill](guarded-live-reconciliation-drill.md) | How to verify venue state and respond to mismatches | baseline implemented |
| [Kill-switch procedure](kill-switch-procedure.md) | When and how to engage, verify, and release emergency stop | baseline implemented |
| [Release and docs checklist](release-and-docs-checklist.md) | How to keep docs aligned with feature changes | baseline implemented |

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

## Current Baseline

The required runbook set now exists as a baseline package under `docs/operations/*`.

What this baseline is good enough for:

- single-operator daily inspection
- first-pass incident triage
- guarded-live reconciliation and stop discipline
- lineage posture interpretation, evidence retention, and drill validation
- release-time documentation alignment

What is still not complete:

- deployment and backup runbooks
- secret rotation and credential-governance procedures
- venue-specific live drills beyond the current guarded-live baseline
- evidence that every runbook step is fully represented by product UX without fallback shell work
- escalation workflow linkages for lineage drill evidence packs

## Related Docs

- [Current State](../status/current-state.md)
- [Product Position](../status/product-position.md)
- [Next Wave Plan](../roadmap/next-wave-plan.md)
- [Operating Model](../blueprint/operating-model.md)
