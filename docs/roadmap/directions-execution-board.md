# Directions Execution Board

This document turns `directions.toml` plus the roadmap and blueprint docs into one execution board
for unfinished work.

Use this when choosing what to build next. It is not the source of truth for implemented capability.
That remains [Current State](../status/current-state.md).

## Planning Sources

- `.codex-exec-loop/planning/directions.toml`
- `.codex-exec-loop/planning/directions/*.md`
- [Current State](../status/current-state.md)
- [Epic Backlog](epic-backlog.md)
- [Next Wave Plan](next-wave-plan.md)
- [Backlog Map](../blueprint/backlog-map.md)
- [Metrics And Gates](../blueprint/metrics-and-gates.md)

## Working Rules

- Finish `Batch 1` before opening major `Batch 2` work. The later batches depend on its data and
  experiment contracts.
- Treat `Batch 2` as the operator-readiness gate for `Batch 3`. Do not market guarded-live as ready
  if runtime operations are still confusing.
- Keep `Batch 4` isolated until trace, replay, and fallback controls are real.
- After each meaningful delivery, update `status/current-state.md` and at least one linked roadmap
  or operations document in the same change.

## Delivery Status Vocabulary

- `Partial`: real baseline exists, but the operator or product contract is still incomplete
- `Not started`: only contract, skeleton, or documentation shape exists
- `Blocked by gate`: should not expand yet because an earlier batch exit condition is not satisfied

## Batch 1: Research Core Closure

Status:

- `Now`
- overall state: `Partial`
- directions: `data-trust-and-lineage`, `experiment-os`
- note: deterministic dataset-boundary contracts, rerun validation categories, lineage mismatch
  taxonomy, and ingestion-history query surfaces are now in place; the remaining gate is operator
  guidance plus Experiment OS durability

Why first:

- every later runtime, guarded-live, and intelligence claim depends on deterministic data boundaries
  and a durable experiment model

Unfinished work:

1. deepen operator-facing lineage mismatch guidance plus retention and escalation policy
2. move custom strategy registration into a durable registry with lifecycle and promotion state
3. wire durable strategy lifecycle and promotion records into query filters
4. add normalized experiment summary, artifact registry, and export registry paths
5. make benchmark-pack and promotion-review artifacts first-class instead of loose payloads

Exit evidence:

- `Gate 1: Research OS Gate` can pass
- repeated identical runs can defend one stable dataset boundary and mismatch posture
- lineage-health review paths have explicit operator guidance plus retention/escalation rules
- strategy registrations survive restart and remain queryable in control-room filters
- common experiment queries no longer depend on payload-heavy scans for normal usage

Do not expand here yet:

- collaboration features
- new market breadth beyond the crypto-first baseline
- optimization automation that assumes the registry and artifact model already exist

## Batch 2: Runtime Operations Productization

Status:

- `Next`
- overall state: `Partial`
- directions: `runtime-ops`, `operator-trust-and-discipline`
- depends on: `Batch 1`
- note: the runbook baseline exists now; the remaining gap is productizing those workflows into the
  control room

Why second:

- the runtime substrate already exists, but the product still behaves too much like a dense admin
  panel instead of an operator workflow

Unfinished work:

1. separate preview and history views from active-session workflows in product language and UI shape
2. add active-session-first surfaces for positions, fills, lag, and recent decisions
3. simplify stop, hold, rerun, recover, acknowledge, and escalation guidance
4. keep decomposing the control room away from dense feature-local state and rendering
5. bind runtime actions and alerts back to runbook guidance instead of leaving them as raw controls

Exit evidence:

- `Gate 2: Sandbox Operations Gate` can pass
- one operator can answer what is running, what changed, and what to do next without shell access
- worker state, stale data, and failure conditions lead to explicit actions instead of raw logs

Do not expand here yet:

- ornamental UI work that does not reduce operator confusion
- multi-user workflow assumptions

## Batch 3: Guarded-Live Safety Completion

Status:

- `Later`
- overall state: `Partial`
- directions: `guarded-live-execution`, `operator-trust-and-discipline`
- depends on: `Batch 2`

Why third:

- guarded-live already has real control-plane capability, but the missing work is safety readiness,
  drill discipline, and clearer lifecycle scope

Unfinished work:

1. define supported venue lifecycle recovery scope and limits per venue
2. formalize the live candidacy checklist and blocking rules
3. broaden order-management posture beyond cancel and replace
4. validate reconciliation and kill-switch drills against product UX, then add deployment and
   credential discipline
5. close remaining audit and operator-event gaps across every live-affecting action

Exit evidence:

- `Gate 3: Live Readiness Gate` can pass
- guarded-live scope is explained by explicit readiness rules instead of inferred code behavior
- unresolved venue lifecycle and drill gaps are reduced to bounded exceptions

Do not expand here yet:

- unattended live behavior
- execution-first shortcuts that bypass audit, reconciliation, or kill-switch expectations

## Batch 4: Intelligence Research Foundation

Status:

- `Later`
- overall state: `Not started`
- directions: `intelligence-research-lane`
- depends on: `Batch 1`
- should wait for stronger operator controls from `Batch 2` before any broader promotion story

Why last:

- the repository only has the lane contract today; research infrastructure does not yet exist

Unfinished work:

1. add a prompt registry with versioned templates
2. store raw trace, normalized decision, and post-risk metadata
3. build replay and evaluation flows against deterministic baselines
4. enforce fallback or human review before any sandbox or live promotion
5. add provider-backed adapters only after trace, replay, and fallback infrastructure is in place

Exit evidence:

- `Gate 4: LLM Research Gate` can pass
- every intelligence-assisted run is replayable, reviewable, and benchmarkable
- no unattended promotion path exists without documented fallback integrity

Do not expand here yet:

- provider breadth for its own sake
- live promotion or autonomous execution stories

## Immediate Ready Queue

These are the highest-value slices that can start now without violating the gate order:

1. durable strategy registry schema and repository contract
2. strategy lifecycle and promotion records wired into query filters
3. experiment summary, artifact, and export registry model
4. benchmark-pack and promotion-review artifact model
5. lineage-health action guidance with retention and escalation rules

These should follow immediately after the queue above:

1. active-session vocabulary split across API and control-room surfaces
2. runtime health panels for positions, fills, lag, and recent decisions
3. runbook-linked action guidance for stop, recover, acknowledge, and escalate flows
4. live candidacy checklist plus drill validation
5. venue lifecycle recovery scope plus deployment and credential governance

## Cross-Cutting Discipline

- `Program 5` work is not a final cleanup pass. It must ship with each batch.
- `Current State`, roadmap, and direction docs should move together whenever capability meaning
  changes.
- If a metric or gate is not measurable yet, treat that as unfinished platform work rather than as a
  documentation omission.
