# Next Wave Plan

Planning horizon: April 22, 2026 through the next 60-90 days.

This plan assumes the documentation reset in `status`, `roadmap`, and `blueprint` is the starting
point rather than a future task.

## Wave 0: Documentation Truth Reset

Status:

- materially complete, with architecture reset docs, runbook baseline, and directions board now in
  place

Goal:

- make `current-state` the single implementation baseline and remove document drift

Exit criteria:

- README, status, roadmap, blueprint, and directions no longer disagree on current progress
- sandbox, worker, and guarded-live terms are used consistently
- completed work is compacted instead of accumulating as an unbounded bullet log

Completed baseline now in place:

- architecture contract docs now describe executable backend/frontend split targets
- ports are split under `port_contracts/*` with compatibility re-exports
- frontend workspace routing and shell composition moved under `apps/web/src/app/*`
- incident-delivery dispatch now uses a registry layer instead of only large condition chains
- baseline runbooks and release-time documentation checklist now exist under `docs/operations/*`

## Wave 1: Deterministic Research Closure

Status:

- materially complete
- remaining work is now drill-evidence export and escalation workflow integration on top of the
  documented and TTL-enforced operator lineage retention policy

Target window:

- Weeks 1-3

Primary outcomes:

- close the operator workflow gap around already-implemented dataset boundaries
- make deterministic lineage review an explicit discipline instead of a raw data surface

Detailed work:

- integrate the documented lineage mismatch interpretation and escalation rules into product
  workflows
- preserve drill evidence for lineage-history and ingestion-job review
- keep product language tight around exact-match claims versus drift-aware replay paths

Acceptance criteria:

- identical strategy/version/params/data inputs can be validated against one stable boundary
- mismatches are categorized instead of collapsing into generic drift
- operator-visible lineage review is tied to retention and escalation rules instead of raw tables

Completed baseline now in place:

- canonical dataset-boundary contracts in run provenance
- claim-aware rerun validation categories for exact-match, checkpoint, window-only, delegated, and
  mode-translation results
- lineage mismatch taxonomy and operator-visible summaries
- ingestion-job history plus normalized lineage query surfaces
- focused runtime triage against the selected instrument's lineage history
- operator lineage guidance with retention floors, escalation rules, and drill validation evidence
- product TTL controls that clamp requested lineage-history and ingestion-job pruning to operator
  retention floors

## Wave 2: Durable Strategy Registry And Experiment OS Completion

Status:

- current primary delivery focus

Target window:

- Weeks 3-6

Primary outcomes:

- finish the move from run archive to experiment operating system

Detailed work:

- introduce a durable custom strategy registry
- define lifecycle transitions and promotion records for registered strategies
- normalize common experiment query paths
- define artifact/export posture for native and reference runs
- document benchmark-pack and promotion-review flows

Acceptance criteria:

- strategy registrations survive restart and appear in control-room filters
- lifecycle and promotion state are durable, queryable, and auditable
- common experiment queries no longer rely on payload-only access patterns

## Wave 3: Control Room Productization

Target window:

- Weeks 6-9

Primary outcomes:

- make the control room easier to operate than the backend feature set suggests

Detailed work:

- split the control room into clearer research, active runtime, and guarded-live sections
- add active-session-first views for positions, fills, lag, and recent decisions
- make stop, hold, rerun, compare, acknowledge, escalate, and recover actions easier to understand
- connect operator actions to runbook guidance and promotion discipline

Acceptance criteria:

- one operator can inspect active runtime health and decide what to do next without deep schema
  knowledge
- the UI no longer behaves like one large admin panel
- runtime actions and historical inspection are visibly distinct workflows

## Wave 4: Guarded-Live Safety Completion

Target window:

- Weeks 9-12

Primary outcomes:

- convert guarded-live from promising control plane into clearer operational readiness

Detailed work:

- define supported venue-lifecycle recovery scope per venue
- clarify cancel, replace, and future amend/order-management posture
- validate reconciliation and kill-switch drills against product UX and live candidacy gates
- define deployment and secret-governance expectations for guarded-live operation

Acceptance criteria:

- guarded-live scope is described by explicit readiness rules rather than inferred from code
- operators have documented and validated drills for reconciliation and emergency stop
- remaining live gaps are reduced to clear, bounded items instead of broad ambiguity

## Parallel Foundation: Runbooks And Operator Discipline

This work runs in parallel with Waves 1-4.

Baseline already in place:

- daily operations checklist
- data incident response checklist
- sandbox runtime incident checklist
- guarded-live reconciliation drill
- kill-switch procedure
- release-time documentation checklist

Remaining outputs:

- deployment and backup runbooks
- secret rotation and credential-governance procedure
- evidence that product UX fully covers the documented operator workflows without shell fallback

## Explicit Non-Goals For This Horizon

- multi-user RBAC
- distributed execution and multi-node schedulers
- unattended autonomous live behavior
- full LLM lane implementation beyond foundation definition
