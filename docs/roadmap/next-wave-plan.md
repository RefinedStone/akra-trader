# Next Wave Plan

Planning horizon: April 21, 2026 through the next 60-90 days.

This plan assumes the documentation reset in `status`, `roadmap`, and `blueprint` is the starting
point rather than a future task.

## Wave 0: Documentation Truth Reset

Status:

- in progress now

Goal:

- make `current-state` the single implementation baseline and remove document drift

Exit criteria:

- README, status, roadmap, blueprint, and directions no longer disagree on current progress
- sandbox, worker, and guarded-live terms are used consistently

## Wave 1: Deterministic Research Baseline

Target window:

- Weeks 1-3

Primary outcomes:

- tighten dataset identity and rerun validation
- make lineage mismatch posture explicit
- expose clearer research-grade data-boundary health

Detailed work:

- define the canonical dataset-identity contract used in run provenance and rerun checks
- document and implement lineage mismatch categories
- add operator-visible lineage mismatch and determinism summaries where current provenance is too raw
- clarify which rerun paths are exact-match claims versus drift-aware replays

Acceptance criteria:

- identical strategy/version/params/data inputs can be validated against one stable boundary
- mismatches are categorized instead of collapsing into generic drift
- roadmap and current-state can claim deterministic posture without ambiguity

## Wave 2: Durable Strategy Registry And Experiment OS Completion

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
- document reconciliation drill, kill-switch drill, and live candidacy checklist
- define deployment and secret-governance expectations for guarded-live operation

Acceptance criteria:

- guarded-live scope is described by explicit readiness rules rather than inferred from code
- operators have documented drills for reconciliation and emergency stop
- remaining live gaps are reduced to clear, bounded items instead of broad ambiguity

## Parallel Foundation: Runbooks And Operator Discipline

This work runs in parallel with Waves 1-4.

Required outputs:

- daily operations checklist
- data incident response checklist
- sandbox runtime incident checklist
- guarded-live reconciliation drill
- kill-switch procedure
- release-time documentation checklist

## Explicit Non-Goals For This Horizon

- multi-user RBAC
- distributed execution and multi-node schedulers
- unattended autonomous live behavior
- full LLM lane implementation beyond foundation definition
