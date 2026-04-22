# Technical Roadmap

Rebased to the repository state as of April 22, 2026.

## Goal

Advance the architecture without breaking the core boundary rule:

- domain and application code stay independent from frameworks, exchanges, storage engines, and
  LLM providers

## Current Technical Baseline

Already implemented:

- explicit ports for market data, strategy catalog, run storage, guarded-live state, venue state,
  references, and decision engines
- durable run persistence through SQLAlchemy
- native runtime decomposition into data, execution, risk, cache, supervision, and mode services
- market-data sync with checkpoints, backfill status, gap visibility, and failure history
- experiment presets, rerun boundaries, richer query/filter contracts, and comparison surfaces
- sandbox worker heartbeat and restart recovery
- guarded-live kill switch, reconciliation, recovery, incidents, and venue-backed launch gates

The roadmap now focuses on technical completion and productization rather than greenfield feature
creation.

## Track A: Data Trust And Determinism

### Current baseline

- candle-backed runs already store dataset identity fingerprints
- runs can link directly to sync checkpoints and rerun boundaries
- canonical dataset-boundary contracts and claim-aware rerun validation categories now exist in run
  provenance
- market-data status already exposes checkpoints, gap windows, backfill, lag, and failure history
- normalized lineage-history and ingestion-job query surfaces now exist for symbol/timeframe
  inspection

### Remaining work

- clearer lineage mismatch reporting when rerun guarantees cannot be made
- stronger operator-facing workflows around data-boundary health, ingestion history, and mismatch
  interpretation
- retention, drill, and escalation policy for lineage-history and ingestion-job review paths

## Track B: Experiment OS And Persistence

### Current baseline

- durable run repository with rich provenance payloads
- presets with revisions and lifecycle actions
- richer run, preset, strategy, and comparison query contracts
- native and reference runs already share a comparison and provenance posture

### Remaining work

- durable custom strategy registry and promotion lifecycle
- normalized experiment summary tables for common query paths
- artifact/export registry beyond loosely structured provenance payloads
- clearer benchmark-pack and promotion review model

## Track C: Control Room Productization

### Current baseline

- one control room already covers research launch, histories, comparison, alerts, incidents, and
  guarded-live panels
- operator actions already reach sandbox stop, live stop, cancel/replace, reconciliation, recovery,
  and incident workflows
- runtime operator workflows now include focused lineage-history and ingestion-job triage for the
  currently selected market-data instrument, plus alert-linked focus routing and inline lineage
  incident history
- runtime and guarded-live alert payloads now include normalized symbol/timeframe context where the
  runtime can resolve it directly
- multi-symbol operator alerts now collapse onto one deterministic primary market-data focus using
  instrument risk, live-session relevance, payload order, and stable fallback
- backend operator payloads now expose explicit `primary_focus` metadata so consumers can use the
  selected symbol/timeframe directly instead of rebuilding that choice from raw symbol lists
- external webhook delivery and provider remediation payload builders now pass through that same
  normalized market context for downstream incident tooling
- provider workflow pull normalization now restores returned `primary_focus` market context into
  incident and provider-recovery state rather than keeping only raw target lists
- provider workflow action payloads now project `market_context` into vendor-native structured
  fields like `custom_details`, `details`, or `metadata`, while note/message text keeps the same
  block human-readable in downstream timelines
- provider workflow pull normalization now reads that vendor-native `market_context` back into the
  normalized pull snapshot instead of relying only on top-level provider recovery fields
- normalized provider recovery state now preserves provider-specific source provenance for restored
  market-context fields so downstream audit and export surfaces can distinguish vendor paths, and
  the control room now shows and exports that provenance during incident triage
- provider provenance export in the control room now includes filter/sort controls, persisted
  local export history, a shared server-side registry with audit trail, analytics plus
  cross-focus query rollups, and time-series drift / burn-up dashboards, moving it closer to a
  real operator handoff surface
- provider provenance analytics now also persists saved presets, shared dashboard views, and
  scheduled provenance reports with background due-run execution, manual controls, and audit
  history, so analytics state is durable across operators rather than pinned to one browser tab
- runtime operator visibility now also surfaces provider-provenance scheduler health plus lag and
  failure alerts, so automation regressions can share the same operational channel as worker faults
- provider provenance automation now also keeps durable scheduler health history and exposes
  paginated history, export, and daily-to-hourly health / lag drill-down surfaces in the control
  room, closing the gap between transient scheduler alerts and reviewable operations history
- scheduler-health export now also plugs into the shared export registry with audit trail and
  delivery-backed escalation workflow, so provenance automation review can promote directly into an
  operator handoff artifact
- per-export routing and approval policy now sits on top of that scheduler export workflow, so
  escalation targets and approval gates can be chosen and audited at the export artifact level
- runtime alert review now sits on top of backend auto-created scheduler-export workflows for
  lag/failure conditions, so automation faults open one shared handoff artifact automatically and
  can escalate it immediately when policy allows, tightening the loop between automation detection
  and operator
- resolved scheduler alert history can now reconstruct historical scheduler exports from persisted
  scheduler-health records, so post-incident review is no longer forced to export only the current
  automation snapshot after the alert has cleared
- scheduler alert history now keeps per-category lag/failure occurrence timelines instead of only
  the latest scheduler row, so resolved review can address older closed occurrences with stable
  occurrence ids and timeline context
- scheduler automation now also has a dedicated paginated alert-occurrence surface, so repeated
  lag/failure timelines can be queried without relying on the global operator alert-history panel
  handoff
- resolved scheduler exports can now switch into a mixed-status post-resolution narrative, so the
  exported artifact can carry recovery and stabilization context instead of only the original
  alert-status slice
- the same scheduler occurrence slice can now also emit stitched multi-occurrence narrative
  reports, so repeated lag/failure windows can be reviewed and shared as one export artifact
  instead of forcing per-row reconstruction only
- stitched scheduler reports now also live behind a dedicated saved-view surface, so named
  occurrence slices can be persisted with their export limits and later edited, deleted,
  revision-restored, or replayed directly into copy, download, or shared-report workflows
- those saved stitched report views now also have bulk governance plus a team audit layer, so
  shared scheduler handoff lenses can be batch-patched, retired, restored, and reviewed as team
  assets instead of only per-view lifecycle entries
- those same saved stitched report views now also run through staged governance plans with
  reusable policy templates, so saved scheduler report lenses can follow the same queue,
  approval, and rollback discipline as the rest of the scheduler governance layer
- those saved stitched report views now also have stitched-report-specific approval-queue and
  policy-catalog surfaces, so their saved-view governance can be reviewed and defaulted in place
  rather than only through the broader shared scheduler governance workspace
- that stitched-report governance layer now also has a stitched-report-only registry and
  lifecycle surface, so stitched queue slices plus default policy bundles can be saved,
  reapplied, deleted, and revision-restored as dedicated stitched governance objects instead of
  only as filters over the shared scheduler governance catalog
- those stitched-report governance registries now also have bulk-governance and shared audit
  surfaces, so the saved stitched-only queue/default bundles can be batch-patched and reviewed as
  team-owned lifecycle objects instead of one-off manual edits
- those same stitched-report governance registries now also run through staged governance plans
  with reusable policy templates and catalogs, so stitched queue/default bundles can follow the
  same preview, approval, apply, and rollback discipline as the rest of the scheduler governance
  layer
- that stitched-report governance registry workspace now also has its own registry-only approval
  queue and stitched-governance-registry policy-catalog surface, so registry bundle review and
  queue-defaulting can happen in place instead of only through the broader shared governance
  surfaces
- those stitched-governance-registry governance records now also persist through a dedicated
  stitched-registry plan/policy store and standalone route set, so future registry governance
  work can evolve without coupling record lifecycle to the generic scheduler governance layer
- scheduler occurrence review now also has a narrative facet plus dedicated templates and named
  registry boards, so shared scheduler review lenses can reopen post-resolution recovery or
  recurring-occurrence analysis without rebuilding the filters by hand
- that same scheduler occurrence surface now also has deeper server-side search over occurrence
  IDs, alert text, market context, and narrative status sequences, so future stitched-report and
  handoff tooling can query narrower scheduler narratives without client-only filtering
- that same scheduler search surface now also computes weighted retrieval ranking plus matched
  field highlights, so future narrative-review tooling can sort and explain scheduler matches
  instead of only returning an unranked filtered occurrence set
- that same search surface now also parses advanced query operators and semantic scheduler
  concepts, so future narrative tooling can build on server-side filtered intent retrieval rather
  than a single free-text substring layer
- that same scheduler search surface now also materializes a dedicated full-text index and boolean
  query evaluator, so future narrative tooling can build on indexed `AND` / `OR` / `NOT`
- that same retrieval surface now also groups ranked matches into cross-occurrence
  semantic/vector clusters, so future stitched-report tooling can pivot from narrative clusters
  instead of only paginated occurrence rows
  retrieval instead of re-implementing linear scan matching in each workflow
- that same scheduler search layer now also persists those lexical/semantic projections in a
  standalone search store with tuned relevance weighting, so future narrative retrieval can build
  on dedicated durable index documents instead of recomputing every token stream on demand
- those scheduler narrative templates and boards now also support edit/delete/version workflow,
  so the saved scheduler review layer can evolve with durable revision restore instead of only
  appending new one-off entries
- that saved scheduler review layer now also has bulk governance workflow, so operators can clean
  up or reinstate multiple narrative templates and boards without repeating single-item actions
- the same governance workflow now also supports advanced batch edits, so teams can patch metadata,
  scheduler query filters, registry template links, and board layout flags across multiple saved
  scheduler review entries in one step
- scheduler narrative batch governance now also has a staged plan layer with diff preview,
  explicit approval, apply-time drift protection, and rollback to captured revisions, so shared
  review-lens changes are auditable before they mutate the saved workspace state
- that staged governance layer now also has reusable policy templates and an approval queue view,
  so lane/priority defaults can be reused across scheduler plan previews and pending work can be
  reviewed as a queue instead of only an undifferentiated plan table
- those governance policy templates now also carry revision history and a shared audit surface, so
  template edits and restores are durable and team-visible instead of being create/list only
- the next layer is now in place too: queue operators can batch approve/apply multiple plans, and
  higher-level governance policy catalogs can bundle linked templates into reusable queue/default
  presets instead of rebuilding the same selection set by hand
- those policy catalogs now also have lifecycle, audit, and bulk-governance surfaces, but catalog
  governance now also includes reusable staged-plan hierarchies that can be captured from the
  current template/registry workbench and replayed back into the approval queue as catalog-linked
  plans, and those captured hierarchies now also support step edit, step revision restore, and
  step bulk-governance workflow; hierarchy steps can now also be promoted into named templates and
  synced across multiple policy catalogs, and those reusable hierarchy-step templates now also
  support edit/delete/revision-restore, bulk governance, shared team audit, saved policy defaults,
  direct approval-queue staging, source-template queue filtering, batch queue staging, plus
  server-side queue search/sort and saved dashboard views for hierarchy-step approval review;
  deeper server-side scheduler narrative search is still not built

### Remaining work

- decompose the current monolithic UI into clearer product surfaces
- improve active-session views for positions, fills, lag, and recent decisions
- align UI state and operator workflows with runbooks and promotion rules
- add team-level dashboard collections above the current preset/view/report records

## Track D: Runtime Ops And Guarded-Live Stabilization

### Current baseline

- sandbox workers already persist heartbeat, runtime-session progress, and recovery history
- guarded-live control state already persists kill switch, reconciliation, recovery, incidents,
  delivery history, and session ownership
- venue-backed live launch, order cancel, and order replace already exist
- Binance handoff, plus supported Coinbase and Kraken continuation paths, already exist at the
  control-plane level

### Remaining work

- simplify and clarify runtime-session models for operators
- broaden venue-native lifecycle recovery and amend/order-management coverage
- make deployment, credentials, and drill workflows first-class operational concerns

## Track E: Intelligence Research Lane

### Current baseline

- `DecisionEnginePort`
- template strategy shape
- shared decision-envelope contract

### Remaining work

- prompt registry
- raw trace storage
- replay harness
- fallback or review enforcement
- provider-backed decision-engine adapters

## Technical Exit Criteria For The Next Major Milestone

The next milestone should meet these checks:

- repeated runs can defend their dataset identity and mismatch posture
- custom strategy lifecycle is durable across restart and queryable without payload-heavy scans
- the control room reflects active runtime work as clearly as historical inspection
- guarded-live safety is backed by productized operational discipline, not only backend capability
- the LLM lane remains isolated until trace and replay controls exist
