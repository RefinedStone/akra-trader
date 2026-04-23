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

## Cross-Cutting Lane: LLM Sensitivity Decomposition

Status:

- `Now`
- overall state: `Partial`
- direction: `llm-sensitivity-decomposition`

Why now:

- the remaining giant compatibility files are now a delivery risk, not just a style issue
- Batch 1 through Batch 3 all still depend on being able to change one bounded flow without
  reopening `App.tsx` or `application.py`

Active move map:

1. keep `controlRoomApi.ts` and `controlRoomDefinitions.ts` as compatibility barrels while the
   real provider/query-builder families move under bounded submodules, and keep provider-
   provenance saved workspace cards owned by dedicated route collaborators instead of re-expanding
   runtime triage or `App.tsx`; keep the Governance policy templates card split between a
   dedicated card wrapper and bounded template-registry, policy-catalog, catalog-hierarchy,
   hierarchy-step-template, and policy-catalog-audit collaborators instead of rebuilding that
   giant governance surface inline in `RuntimeProviderProvenanceWorkspaceCards.tsx`; keep the
   scheduler narrative templates surface routed through a dedicated card wrapper instead of
   rebuilding template drafting, bulk governance, registry listing, and revision history inline
   in `RuntimeProviderProvenanceWorkspaceCards.tsx`, and keep that scheduler narrative templates
   card split between dedicated bulk-governance, registry-table, and revision-history
   collaborators instead of recombining those flows inline in one card body; keep the scheduler
   narrative template bulk-governance collaborator split between governance-bar and
   bulk-edit-stage collaborators instead of recombining selection-policy preview actions and
   advanced bulk edit staging inline in one governance module; keep the scheduler narrative
   template registry-table collaborator split between table-view and row-detail collaborators
   instead of recombining table shell, row review, and row actions inline in one registry
   module, and keep the hierarchy-step-
   template section split between draft, registry, versions, and audit
   collaborators instead of rebuilding that cross-catalog governance surface inline in one module,
  and keep the registry layer split between bulk-selection-stage, bulk-step-stage, and
  registry-table collaborators instead of collapsing bulk staging and the registry table back
  together, and keep the registry-table layer split between row-detail and row-action
  collaborators instead of recombining cell review and row mutations inline; keep the versions
  layer split between a versions-table collaborator plus version-row-detail and version-row-action
  collaborators instead of rebuilding revision review and restore controls inline, and keep the
  audit layer split between audit-filter and audit-table collaborators plus audit-summary,
  audit-template, and audit-actor row cells instead of rebuilding filter controls and audit rows
  inline; keep the governance-policy-template registry split between draft, catalog-workflow,
  registry-table, versions, and audit collaborators instead of rebuilding template editing,
  catalog bundling, registry listing, revision history, and audit review inline in one module;
  keep the governance-policy-template registry-table layer split between row-detail and row-action
  collaborators instead of recombining template/scope review and row actions inline; keep the
  governance-policy-template versions layer split between a versions-table collaborator plus
  version-row-detail and version-row-action collaborators instead of rebuilding revision review
  and restore controls inline; keep the governance-policy-template audit layer split between
  audit-filter and audit-table collaborators plus audit-summary, audit-template, and audit-actor
  row cells instead of rebuilding filter controls and audit rows inline; keep the governance-
  policy-catalog layer split between bulk-edit, registry-table, and versions collaborators
  instead of rebuilding bulk selection edits, catalog registry listing, and revision history
  inline; keep the governance-policy-catalog bulk-edit layer split between bulk-selection, bulk-
  metadata-stage, and bulk-action collaborators instead of rebuilding selection summary/toggle
  controls, staged metadata/default-template edits, and bulk delete/restore/update actions inline
  in one filter-bar owner; keep the governance-policy-catalog bulk-selection layer split between
  bulk-selection-state and bulk-selection-summary collaborators instead of rebuilding the select-
  all toggle state and selected-count summary inline in one selection owner; keep the governance-
  policy-catalog bulk-action layer split between bulk-delete-action, bulk-restore-action, and
  bulk-update-action collaborators instead of rebuilding delete, restore, and update triggers
  inline in one action owner; keep the governance-policy-catalog bulk-metadata-stage layer split
  between bulk-name-stage, bulk-description-stage, and bulk-default-template-stage collaborators
  instead of rebuilding name prefix/suffix edits, description staging, and default-template
  staging inline in one metadata owner; keep the governance-catalog-hierarchy layer split between
  bulk-selection-stage, bulk-patch-stage, table, editor, and versions collaborators instead of
  rebuilding bulk governance staging, captured-step review, direct step editing, and step
  revision history inline in one governance section module; keep the governance-catalog-hierarchy
  bulk-selection-stage layer split between bulk-selection-state and bulk-selection-action
  collaborators instead of rebuilding staged selection fields and bulk action triggers inline in
  one bulk staging owner; keep the governance-catalog-hierarchy bulk-patch-stage layer split
  between bulk-query-patch-stage and bulk-layout-patch-stage collaborators instead of rebuilding
  query and layout patch ownership inline in one bulk patch owner; keep the governance-catalog-
  hierarchy table layer split between row-detail and row-action collaborators instead of
  recombining captured-step review cells and row-level edit/version actions inline in one table
  owner; keep the governance-catalog-hierarchy editor layer split between editor-metadata-form and
  editor-patch-textarea collaborators instead of rebuilding metadata form controls and patch
  textarea ownership inline in one editor module; keep the governance-catalog-hierarchy versions
  layer split between a versions-table collaborator plus version-row-detail and version-row-action
  collaborators instead of rebuilding revision review and restore controls inline; keep the
  governance-policy-catalog registry-table layer split between row-detail and row-action
  collaborators instead of recombining catalog/default review and row actions inline; keep the
  governance-policy-catalog versions layer split between a versions-table collaborator plus
  version-row-detail and version-row-action collaborators instead of rebuilding revision review
  and restore controls inline
2. keep runtime provider-provenance workspace ownership in dedicated workspace section modules
   instead of sliding cross-focus query, scheduler review, analytics, or shared-audit bodies back
   into `RuntimeDataIncidentTriagePanel.tsx`; keep focused provider readback plus persisted/shared
   export history owned by dedicated provider-provenance collaborators instead of rebuilding that
   export body inline in triage, and keep focused lineage history owned by a dedicated
   provider-provenance collaborator instead of rebuilding that history body inline, and keep
   focused ingestion jobs owned by a dedicated provider-provenance collaborator instead of
   rebuilding that jobs body inline, and keep focused lineage incident history owned by a
   dedicated provider-provenance collaborator instead of rebuilding that incident history body
   inline
3. keep the provider-provenance scheduler workspace split by bounded sections such as automation,
   moderation, stitched governance, and shared exports instead of rebuilding one giant scheduler
   collaborator
4. keep scheduler moderation flows split between alert review and governance queue ownership,
   and keep moderation-governance split between policy-catalog ownership and approval-queue
   ownership instead of recombining retrieval review, catalog governance, and approval queues in
   one module
5. keep the moderation policy-catalog layer split between catalog lifecycle, governance-policy
   lifecycle, and meta-policy defaults instead of rebuilding one large catalog/governance editor
   module
6. keep the moderation approval-queue layer split between moderation-governance, catalog-
   governance, and scheduler moderation execution queues instead of rebuilding one large approval
   queue module
7. keep stitched-governance split between stitched report view ownership and registry lifecycle
   ownership instead of recombining saved views, queue slices, and registry maintenance in one
   module
8. keep stitched registry-lifecycle split between review ownership and editor-history ownership
   and keep editor-history split between editing and audit-history collaborators instead of
   recombining queue/catalog review, registry drafting, bulk edits, and history/audit maintenance
   in one module; keep the audit-history revision table body split between recorded, snapshot, and
   action cell collaborators instead of rebuilding the revision row inline, and keep the audit-
   event table body split between when, action, actor, and detail cell collaborators instead of
   rebuilding the audit row inline; keep the audit-history revision-history and audit-event table
   shells split into dedicated table collaborators instead of leaving both table shells inline;
   keep the audit filter bar split between select and text-input collaborators instead of
   rebuilding all audit filters in one block; keep review split between queue-surface and
   policy-catalog-surface collaborators instead of rebuilding both review shells inline; keep the
   review approval-queue table split between queue-table and queue-row collaborators, and keep the
   registry policy-catalog table split between policy-catalog-table and policy-catalog-row
   collaborators instead of rebuilding those table shells and row bodies inline; keep the review
   filter bars split between queue-filter-state, queue-filter-policy, queue-filter-query, and
   policy-catalog-search collaborators instead of rebuilding all review filters inline; keep the
   queue and policy-catalog surfaces routed through dedicated summary and empty-state leaves; keep
   queue rows split between plan-detail, preview-detail, and action collaborators, and keep
   policy rows split between catalog-detail, defaults-detail, and action collaborators
9. keep stitched registry editing split between draft, bulk-edit, and table collaborators, and
   keep draft split between identity-stage, default-policy-stage, action, and search
   collaborators instead of recombining registry drafting inputs, default policy staging,
   save/cancel actions, and registry search in one module; keep table split between listing,
   table-header, header-selection, row-selection, row-detail,
   row-action-cell, and revision-selection collaborators instead of recombining registry drafting,
   selection governance, bulk edit staging, registry listing, header shell, row selection, row
   details, action controls, and revision selection in one module
10. keep stitched registry bulk-edit split between selection-summary, selection-actions,
    metadata-stage, queue-stage, and policy-stage collaborators instead of recombining selection
    governance and bulk edit staging controls in one module; keep governance-policy selection in
    the policy-stage instead of duplicating it in selection-action controls; keep selection-actions
    split between toggle-action and preview-actions collaborators, keep metadata-stage split
    between name-affix and description staged-state collaborators, keep queue-stage split between
    queue-core-state and queue-query staged-state collaborators, keep policy-stage split between
    default-policy and governance-policy staged-state collaborators, and keep preview bulk-edit
    dispatch in a dedicated policy preview-action collaborator
11. keep stitched report views split between saved-view lifecycle ownership and approval-policy
   ownership instead of recombining saved view administration, stitched approval queue, and policy
   catalog review in one module
12. keep stitched report approval-policy ownership split between approval-queue and policy-catalog
    collaborators instead of recombining stitched governance queue review and policy catalog
    defaults in one module
13. keep stitched report policy-catalog ownership split between review and selection
    collaborators instead of recombining catalog review details and catalog action selection in one
    module
14. keep stitched report policy-catalog selection ownership split between action-cell and
    selection-state collaborators instead of recombining the action cell wrapper and button state
    in one module
15. keep stitched report policy-catalog selection-state ownership split between derived-state and
    selection-action collaborators instead of recombining button enablement checks and catalog-
    selection dispatch in one module
16. keep stitched report policy-catalog selection-action ownership split between action-dispatch
    and trigger-wiring collaborators instead of recombining catalog action dispatch and button
    wiring in one module
17. keep stitched report policy-catalog action-dispatch ownership split between per-action
    handlers and shared dispatch plumbing collaborators instead of recombining common catalog
    dispatch plumbing and action-specific handlers in one module
18. keep stitched report policy-catalog trigger-wiring ownership split between button-layout and
    callback-wiring collaborators instead of recombining button layout and callback binding in one
    module
19. keep stitched report policy-catalog review ownership split between default-body and
    catalog-state collaborators instead of recombining catalog state and default policy detail
    cells in one module
20. keep stitched report policy-catalog review ownership split between table-shell and row-detail
    collaborators instead of recombining table structure and row composition in one module
21. keep stitched report approval-queue ownership balanced so the section retains outer table
    shell, empty-state branching, and per-plan row-shell ownership while composing queue-state and
    action collaborators, instead of routing plan-list row structure through one nested body
    wrapper
22. keep stitched report approval-queue action ownership focused on review-state and mutation
    collaborators for a single plan row instead of recombining row-level review state and queue
    mutation controls with plan-list row mapping and `<tr>` shell ownership
23. keep stitched report approval-queue review-state ownership split between plan-cell and
    preview-cell collaborators instead of recombining both row cells in one review-state owner
24. keep stitched report approval-queue plan-cell ownership split between identity-summary,
    origin-summary, and approval-summary leaf collaborators instead of recombining plan metadata
    copy in one cell owner
25. keep stitched report approval-queue preview-cell ownership split between preview-headline,
    rollback-summary, and preview-count leaf collaborators instead of recombining preview-state
    copy in one cell owner
26. keep stitched report approval-queue mutation ownership focused on the action-cell shell while
    directly composing queue-action and commit-control collaborators instead of routing those row
    actions through extra mutation leaf wrappers
27. keep stitched report approval-queue queue-action leaf ownership split between dispatch and
    status-view collaborators instead of recombining shared-queue dispatch and selected-state copy
    in one leaf owner
28. keep stitched report approval-queue commit-control ownership directly composing per-mutation
    plan-gate collaborators, and keep plan-gate directly mounting commit-action once
    eligibility-state and label-policy resolve, instead of routing subtree entrypoints through
    extra passthrough leaf wrappers
29. keep stitched report approval-queue commit-action ownership split between dispatch-flow and
    mutation-trigger collaborators instead of recombining mutation dispatch branching and button
    rendering in one module
30. keep stitched report approval-queue plan-gate ownership split between eligibility-state and
    label-policy collaborators instead of recombining mutation eligibility checks and button-label
    policy in one module
31. keep stitched report approval queue-state ownership balanced between summary, filter-state, and
    async-state collaborators instead of pushing queue async readout down into the filter ownership
    layer
32. keep stitched report approval queue filter-state ownership directly above query-input and
    toggle-reset collaborators instead of routing queue filters through a separate filter-bar
    wrapper while mixing in async queue state
33. keep stitched report approval queue toggle-reset ownership directly above filter-select,
    reset-selection, and reset-action collaborators instead of routing template/catalog/sort
    controls through a separate reset-apply wrapper
34. keep stitched report approval queue filter-select ownership split between queue-state, lane,
    and priority selector collaborators, and keep reset-selection ownership split between policy-
    template and policy-catalog selector collaborators instead of recombining multiple selector
    bodies in each leaf owner
35. keep stitched report approval queue query-input ownership split between search-input binding and
    search-input field collaborators instead of recombining search filter update wiring and input
    layout in one leaf owner
36. keep stitched report saved-view lifecycle split between bulk-edit, revision-review, and audit
    collaborators instead of recombining selection governance, revision restore, and audit review
    in one module
37. keep stitched report bulk-edit ownership split between selection-governance, filter-stage,
    and limit-policy-stage collaborators instead of recombining bulk selection, staged filter
    edits, and staged approval controls in one module
38. keep stitched report bulk limit/policy stage ownership split between approval and policy
    collaborators instead of recombining numeric approval staging and policy template selection in
    one module
39. keep stitched report bulk approval stage ownership split between limit-controls and preview
    collaborators instead of recombining numeric limit inputs and staged bulk preview controls in
    one module
40. keep stitched report bulk preview ownership split between preview-state and approval-trigger
    collaborators instead of recombining button label state and the approval trigger in one module
41. keep stitched report bulk limit-controls ownership split between slice-limit and
    history-limit collaborators instead of recombining slice sizing and history sizing inputs in
    one module
42. keep stitched report bulk slice-limit ownership split between window, result, and occurrence
    collaborators instead of recombining the three slice sizing inputs in one module
43. keep stitched report bulk history-limit ownership split between history and drill-down
    collaborators instead of recombining the two history sizing inputs in one module
44. keep query-builder replay intent, replay review, replay promotion approval, expression
    authoring, coordination-simulation orchestration, and replay provenance/runtime-review flows in
    feature-owned hooks and section collaborators instead of re-expanding the main component body;
    the next pressure points are the remaining large workspace modules plus backend compatibility
   files such as standalone surface catalogs and `application.py`
6. keep `domain/models.py` import-compatible while model families move under `domain/model_types/*`
7. keep shrinking `application.py` by moving pure comparison and serializer flows into
   `application_support/*`
8. use route smoke tests as a floor before further `App.tsx` extraction

Exit evidence:

- new frontend/backend work no longer lands by default in the giant compatibility entrypoints
- one flow usually resolves from one entry module plus a few direct collaborators
- route and serializer regressions are caught without reopening the full control room

## Cross-Cutting Discipline

- `Program 5` work is not a final cleanup pass. It must ship with each batch.
- `Current State`, roadmap, and direction docs should move together whenever capability meaning
  changes.
- If a metric or gate is not measurable yet, treat that as unfinished platform work rather than as a
  documentation omission.
