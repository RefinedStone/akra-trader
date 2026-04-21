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
- multi-symbol alerts resolve to one explicit primary triage focus using instrument risk,
  live-session relevance, payload symbol order, and stable fallback, and the control room shows why
- backend operator alert and incident payloads now carry explicit `primary_focus` metadata for that
  selected symbol/timeframe and candidate set
- operator and guarded-live alert payloads now carry normalized symbol/timeframe context when the
  runtime knows it
- external webhook and provider remediation payloads now carry the same normalized market context
  so downstream incident systems do not need to reconstruct the lead symbol from free-form text
- when a provider returns that market context during workflow pull or remediation sync, Akra now
  restores it into normalized incident fields instead of dropping the selected focus on re-entry
- provider workflow actions now also project that `market_context` into provider-native structured
  fields such as `custom_details`, `details`, or `metadata`, and render it as an explicit
  note/message section so provider timelines preserve the selected symbol/timeframe
- provider pull normalization now reads those same vendor-native structured fields back so
  recovered incidents keep the same selected symbol/timeframe and `primary_focus` after external
  round-trips
- the normalized provider recovery state now keeps provider-specific source provenance for restored
  market-context fields so operators can see which vendor payload path last supplied that focus,
  and the control-room incident drill-down plus triage export now carry that provenance forward
- provider provenance export in the triage panel now supports provider/vendor-field filtering,
  sort controls, persisted local export history, a team-shared registry and audit trail, plus
  provider/vendor/focus/requester rollups, cross-focus query results, and daily provider-drift /
  export burn-up dashboards so repeated incident handoff does not start from an empty clipboard
  or an untraceable copy action
- provider provenance analytics now also has server-side saved presets, shared dashboard views,
  scheduled provenance reports, report audit trails, background due-run execution, and manual
  controls so teams can reuse the same triage and analytics framing across shifts instead of
  rebuilding filters locally
- operator visibility now also emits provider-provenance scheduler lag and failure alerts plus a
  scheduler-health snapshot, so automation drift shows up in the same operator review loop as
  runtime incidents
- the provenance analytics workspace now also shows paginated scheduler-cycle history, scheduler
  health export, and daily-to-hourly health / lag drill-down tables, so operators can distinguish
  one-off lag from sustained automation regression before escalating
- scheduler health export can now be shared into the team registry, leaves delivery/download /
  escalation audit records, and can be escalated directly to configured operator delivery targets
  when automation drift needs a cross-shift handoff
- each shared scheduler export now also carries its own routing and approval policy, so operators
  can hold a snapshot in chatops review, switch it to paging delivery, and require explicit
  approval before sending higher-noise escalation routes
- active scheduler lag/failure alerts now also auto-start one shared export workflow per active
  alert condition in backend automation, and that workflow auto-escalates when its saved routing
  and approval policy already permit delivery; the alert surface still exposes direct controls to
  inspect, approve, or re-escalate that same handoff artifact without leaving alert review
- when that scheduler alert has already resolved, the alert-history row can now reconstruct a
  historical scheduler export from the persisted health-cycle records for the same detected /
  resolved window instead of exporting the current scheduler snapshot
- repeated lag/failure cycles now stay visible as separate scheduler alert occurrences with
  per-category timeline position in alert history, so resolved review can pick the exact closed
  window instead of losing older occurrences behind the latest row
- the scheduler automation workspace now has its own paginated alert-occurrence table with
  category/status filters, so teams can review or reconstruct scheduler incidents without paging
  through unrelated operator alerts
- resolved scheduler exports now also support a mixed-status post-resolution narrative mode, so
  operator handoff can include the recovery path and stabilization history after the alert closed
- run provenance and rerun-boundary views
- lineage posture summaries that collapse rerun taxonomy into exact-match, drift-aware, or unresolved
  operator guidance
- comparison and lineage-oriented research surfaces
- incident and operator-event history

## Triage

1. Identify the affected venue, symbol set, and timeframe.
   If one alert covers multiple symbols, use the control-room primary-focus note as the initial
   review anchor rather than guessing the lead symbol.
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
