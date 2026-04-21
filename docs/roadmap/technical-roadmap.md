# Technical Roadmap

Rebased to the repository state as of April 21, 2026.

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

### Remaining work

- decompose the current monolithic UI into clearer product surfaces
- improve active-session views for positions, fills, lag, and recent decisions
- align UI state and operator workflows with runbooks and promotion rules

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
