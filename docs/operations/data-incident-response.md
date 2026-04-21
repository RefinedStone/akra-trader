# Data Incident Response

Purpose: define the response path for stale sync, repeated ingestion failures, gap expansion, or
unclear dataset lineage.

## Trigger Conditions

- market-data freshness is stale relative to the active timeframe
- sync failures repeat without recovery
- gap windows expand or remain unresolved
- rerun or comparison work cannot defend its dataset boundary

## Product Surfaces

- market-data health and sync status surfaces
- normalized market-data lineage history and ingestion-job history query surfaces
- control-room triage workflow that binds the currently selected instrument to lineage and
  ingestion history review, auto-links runtime alerts into that focus, and keeps a merged lineage
  incident history in view
- operator and guarded-live alert payloads now carry normalized symbol/timeframe context when the
  runtime knows it
- run provenance and rerun-boundary views
- lineage posture summaries that collapse rerun taxonomy into exact-match, drift-aware, or unresolved
  operator guidance
- comparison and lineage-oriented research surfaces
- incident and operator-event history

## Triage

1. Identify the affected venue, symbol set, and timeframe.
2. Determine whether the issue is freshness, gap coverage, repeated failure, or lineage ambiguity.
3. Determine whether any active sandbox, paper, or guarded-live sessions depend on the affected data.
4. Separate one-off lag from a true incident. Repeated failure or unclear lineage is an incident.

## Immediate Actions

1. Pause or stop active work that depends on data you cannot defend.
2. Record the affected symbols, timeframe, and visible failure mode.
3. If the issue affects promotion or benchmark claims, block those decisions until lineage is clear.
4. If the issue affects guarded-live readiness, treat it as a safety blocker rather than a data nuisance.

## Resolution Path

1. Wait for sync recovery only if the gap is clearly bounded and no live-affecting action depends on it.
2. Rerun or compare only after the dataset boundary is explicit again.
3. If freshness recovers but lineage is still ambiguous, keep the incident open.
4. Record whether the final posture is exact-match, drift-aware, or unresolved.

## Escalate If

- the same venue or timeframe continues failing across multiple sync cycles
- gap windows grow while active execution remains exposed
- rerun validation cannot explain whether a result is matched or drifted
- the operator cannot explain which dataset identity or checkpoint a decision relied on

## Closeout Record

Record at minimum:

- affected venue, symbol set, and timeframe
- failure class
- active sessions impacted
- whether stop or hold actions were taken
- the final lineage posture used to reopen work

## Related Runbooks

- [Daily Operations Checklist](daily-operations-checklist.md)
- [Sandbox Runtime Incident](sandbox-runtime-incident.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
