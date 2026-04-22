# Epic Backlog

This backlog starts from the repository state as of April 22, 2026.

## Epic 1: Deterministic Research Hardening

Priority:

- P0

Goal:

- make dataset identity, rerun validation, and lineage mismatch handling strong enough to defend
  reproducibility claims

Current baseline:

- dataset fingerprints, sync-checkpoint linkage, and rerun boundaries already exist
- canonical dataset-boundary contracts, claim-aware rerun validation categories, lineage mismatch
  taxonomy, and ingestion-job history surfaces are now in place

Acceptance criteria:

- repeated identical inputs can be validated against the same data boundary
- lineage mismatch reasons are explicit when deterministic claims fail
- operators can inspect data-boundary health without shell access and follow explicit escalation
  guidance

## Epic 2: Durable Strategy Registry And Promotion Workflow

Priority:

- P0

Goal:

- move strategy registration and lifecycle out of process-local behavior into a durable promotion
  model

Current baseline:

- strategy metadata, lifecycle fields, and filtering exist, but custom registration is not durable

Acceptance criteria:

- custom strategies survive restart
- lifecycle states are queryable and enforceable
- promotion and archival actions leave durable operator-visible records

## Epic 3: Experiment Storage, Artifacts, And Exports

Priority:

- P0

Goal:

- complete the Experiment OS beyond presets and comparison into normalized summaries, artifacts, and
  export posture

Current baseline:

- presets, revisions, query/filter contracts, and comparison already exist

Acceptance criteria:

- common experiment queries avoid payload-heavy scans
- native and reference runs expose consistent artifact and export behavior
- benchmark packs and promotion review artifacts are first-class entities

## Epic 4: Control Room Productization

Priority:

- P1

Goal:

- turn the current single-screen control room into a clearer operator product surface

Current baseline:

- launch, history, comparison, alerts, incidents, kill switch, reconciliation, and live controls all
  already exist in one UI

Acceptance criteria:

- active sessions, positions, fills, lag, and recent decisions are easy to inspect
- operator workflows are clearer than the underlying backend feature graph
- research and operations surfaces are separated well enough to reduce confusion

## Epic 5: Runtime Session Simplification And Ops Upgrade

Priority:

- P1

Goal:

- make sandbox worker operations easier to understand and operate day-to-day

Current baseline:

- sandbox workers already have heartbeat, restart recovery, and operator visibility hooks

Acceptance criteria:

- session health and stop conditions are explicit
- worker state and preview/research state are clearly separated in product surfaces
- lag, stale data, and worker failure are tied to concrete operator actions

## Epic 6: Guarded-Live Lifecycle Completion

Priority:

- P1

Goal:

- complete the guarded-live lane from a promising control plane into a disciplined operational lane

Current baseline:

- kill switch, reconciliation, recovery, incidents, delivery history, and venue-backed launch gates
  already exist
- reconciliation and kill-switch drill baselines are now documented

Acceptance criteria:

- venue-native lifecycle recovery is broader and clearer
- order management covers more than cancel and replace
- live candidacy criteria are backed by documented drills and operator packaging

## Epic 7: Deployment, Runbooks, And Operator Discipline

Priority:

- P1

Goal:

- make daily use, incident response, and release hygiene explicit

Current baseline:

- baseline runbooks and release/docs checklist now exist, but deployment, backup, credential, and
  full UX-validation discipline are still light

Acceptance criteria:

- deployment and backup posture are documented
- runbooks cover daily operations, data incidents, sandbox incidents, reconciliation, and kill switch
- documentation maintenance rules are part of normal release work

## Epic 8: Intelligence Research Lane Foundation

Priority:

- P2

Goal:

- turn the decision-engine contract into a traceable research lane

Current baseline:

- `DecisionEnginePort` and template strategy shapes exist, but trace/replay/fallback do not

Acceptance criteria:

- prompt versions, raw traces, normalized decisions, and review/fallback state are stored
- historical replay can benchmark intelligence decisions against deterministic baselines
- no unattended sandbox or live promotion path exists without fallback or review
