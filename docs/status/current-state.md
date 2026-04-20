# Current State

Canonical status snapshot for the repository as of April 21, 2026.

Use this document as the source of truth for what is actually implemented. Forward-looking planning
lives under [Roadmap](../roadmap/README.md) and [Blueprint](../blueprint/README.md).

## Product Position

`akra-trader` is currently best described as a single-operator research and runtime control
workstation for crypto-first strategy development.

It is no longer only a backtest demo:

- durable research runs, comparison, presets, and reruns are already present
- sandbox worker sessions exist with heartbeat and restart recovery semantics
- guarded-live control surfaces exist with kill switch, reconciliation, recovery, and venue-backed
  launch gates
- operator visibility includes incidents, delivery history, and audit-oriented surfaces

It is not yet a finished live trading product:

- custom strategy registration is still process-local
- experiment storage remains payload-centric in key paths
- control-room UX is still monolithic and operator workflows are not fully productized
- guarded-live venue lifecycle handling is real but not complete
- LLM research infrastructure remains an interface skeleton

## Stage Read

- Stage 0: complete
- Stage 1 Research Foundation: largely complete
- Stage 2 Experiment OS: materially underway
- Stage 3 Runtime Ops: partially complete with real worker semantics
- Stage 4 Guarded Live: early but real control-plane coverage
- Stage 5 Intelligence Research: contract only

## Implemented Now

### Research core

- FastAPI backend with explicit domain, application, adapter, and runtime boundaries
- durable run storage through `SqlAlchemyRunRepository`
- repo-local SQLite defaults with configurable Postgres support
- native backtest execution with persisted config, metrics, orders, fills, positions, notes, equity,
  and provenance
- native market-data lineage with dataset identity fingerprints, sync-checkpoint links, and rerun
  boundaries
- reference-runtime delegation for NostalgiaForInfinity backtests with stored benchmark provenance

### Experiment OS baseline

- run history listing and filtering by mode, strategy, version, and rerun-boundary identity
- native vs reference comparison API and control-room comparison workflow
- experiment presets with lifecycle actions, revisions, and restore flows
- typed query/filter contracts for strategies, presets, runs, and comparison surfaces
- shared query-discovery and run-surface capability contracts for typed query builders and run
  subresource actions
- strategy semantic metadata and parameter-contract hints propagated from catalog records into run
  snapshot and provenance views
- replay-link alias governance, audit browsing, and export-job utilities for query-builder surfaces
- native, sandbox, and paper reruns from stored rerun boundaries with match-or-drift tracking

### Runtime ops baseline

- sandbox worker sessions that continue processing newly arrived candles after a priming window
- persisted sandbox heartbeat cadence, processed-candle progress, and recovery history
- separate paper-session mode instead of collapsing paper into sandbox history
- market-data sync for ccxt-backed Binance, Coinbase, and Kraken with gap detection, lag reporting,
  sync checkpoints, backfill status, and failure history
- operator visibility for stale sandbox workers, worker failures, and recent runtime audit events

### Guarded-live baseline

- guarded-live kill switch, reconciliation, recovery, and resume control surfaces
- gated live launch behind configuration, reconciliation, and recovery checks
- venue-backed live order submission plus persisted live run history
- tracked live order lifecycle sync back into local orders, fills, positions, and audit notes
- operator cancel and replace actions for active live orders
- persisted live-session ownership and durable open-order snapshots
- venue-session handoff and continuation baseline for Binance, with supported continuation paths for
  Coinbase Advanced Trade and Kraken public market transport
- guarded-live incidents, delivery attempts, acknowledgment, escalation, remediation state, and
  provider workflow sync

### Control room baseline

- single-screen React control room with strategy catalog, reference catalog, run launch, run history,
  comparison, market-data status, alerts, incidents, delivery history, kill switch, and
  reconciliation surfaces
- separate histories for backtest, sandbox, paper, and live modes
- guarded-live panels for candidacy blockers, venue snapshots, recovery state, and audit history
- operator surfaces for replay-link alias governance and audit export administration

## Partial Or Fragile Areas

- custom strategy registration exists, but registration metadata is still process-local rather than a
  durable strategy registry
- run storage is durable, but experiment querying and artifact retrieval still lean too heavily on
  payload-centric persistence
- the control room exposes a large amount of capability, but it is still effectively a monolithic
  single-screen application rather than a clearly productized operations UI
- sandbox workers exist, but recent decisions, lag interpretation, and active-session-first operator
  workflows are still weaker than the underlying backend capabilities
- guarded-live recovery restores meaningful control-plane and order-lifecycle state, but it does not
  yet resume a full venue-native session lifecycle in all cases
- incident delivery and provider sync are broad, but provider-owned policy management and external
  incident ownership remain incomplete
- deployment guidance, backups, secret governance, and runbooks are not yet product-grade
- the LLM lane still stops at `DecisionEnginePort`, template strategy shapes, and trace-capable
  envelopes

## Not Implemented Yet

- durable custom strategy registration lifecycle and promotion workflow
- normalized experiment storage for common query, artifact, and export paths
- full venue-native amend flows and broader live order lifecycle management
- complete restart recovery for venue-native live session lifecycles
- operator-grade deployment/runbook package
- prompt versioning, raw trace persistence, replay harness, and fallback/review controls for LLM
  decision research
- multi-user workflows, RBAC, and organization features

## Immediate Next Priorities

1. Harden deterministic research claims around dataset identity, rerun validation, and lineage gaps.
2. Finish the Experiment OS around durable strategy lifecycle, normalized experiment queries, and
   artifact/export posture.
3. Productize the control room around active-session operations, clearer operator workflows, and
   decomposed UI surfaces.
4. Complete guarded-live safety around fuller venue lifecycle handling, runbooks, and deployment
   discipline.
5. Keep the LLM lane isolated until trace, replay, and fallback infrastructure are real features.

## Supporting Docs

- [Product Position](product-position.md)
- [Roadmap Overview](../roadmap/README.md)
- [Next Wave Plan](../roadmap/next-wave-plan.md)
- [Architecture](../architecture.md)
- [Blueprint](../blueprint/README.md)
