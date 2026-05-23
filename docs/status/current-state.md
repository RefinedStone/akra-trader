# Current State

Canonical implementation snapshot as of May 11, 2026.

## Product Position

`akra-trader` is a crypto-first, single-operator research and runtime control workstation. It is
useful for deterministic research, sandbox supervision, and guarded-live readiness work. It is not
yet a finished live-trading product, a multi-user platform, or an LLM-native strategy system.

## Stage Read

- Research foundation: strong.
- Experiment OS: partially complete.
- Runtime operations: real but still needs clearer active-session UX.
- Guarded live: early but meaningful.
- Intelligence research: provider-neutral judgement contract, mock client, OpenAI structured-output
  adapter, and veto-only wrapper exist; replay/evaluation controls are still incomplete.

## Implemented

Research and experiment:

- FastAPI backend with domain, application, adapter, runtime, and port-contract boundaries.
- Native strategy catalog and registration endpoint.
- Durable native backtests with persisted config, metrics, orders, fills, positions, notes, equity,
  provenance, and benchmark comparison.
- Presets, revision/restore flows, run filters, run-surface contracts, rerun boundaries, and
  claim-aware rerun validation.
- Replay-link alias governance, audit browsing, export jobs, and query-builder support surfaces.

Data trust:

- ccxt-backed market-data sync for Binance, Coinbase, and Kraken paths.
- Gap detection, lag reporting, checkpoints, backfill status, ingestion history, lineage history,
  mismatch summaries, TTL floors, and drill evidence exports.

Runtime operations:

- Sandbox workers continue after the priming window and persist heartbeat, processed-candle
  progress, and recovery history.
- Paper sessions are separate from sandbox history.
- Operator visibility covers stale workers, failures, runtime audit events, incidents, delivery
  attempts, acknowledgments, escalations, and remediation state.

Guarded live:

- Guarded-live launch gates, kill switch, reconciliation, recovery, resume, and venue-backed live
  order submission.
- Local order/fill/position sync, live-session ownership, open-order snapshots, cancel/replace
  actions, and venue-session continuation baselines.
- Incident delivery uses explicit provider registries plus workflow callback/pull-sync support.

Frontend:

- `App.tsx` is now a tiny compatibility entrypoint to `control-room/ControlRoomApp`.
- Workspace routing and shell code live under `apps/web/src/app` and `apps/web/src/routes`.
- Control-room API helpers and type families are split under `controlRoomApi/*` and
  `controlRoomDefinitions/*`.
- Query-builder and run-history features have dedicated modules and tests.

Architecture:

- `application.py`, `ports.py`, `domain/models.py`, `controlRoomApi.ts`, and
  `controlRoomDefinitions.ts` are compatibility barrels/facades rather than primary logic owners.
- Backend use-case work is increasingly under `application_flows/*`, `application_support/*`,
  mixins, and bounded domain model modules.

## Incomplete Or Fragile

- Custom strategy registration exists, but durable lifecycle, promotion state, and registry
  workflows are still incomplete.
- Experiment storage still has payload-centric paths where normalized artifact/export/query storage
  is needed.
- Runtime and guarded-live surfaces are broad, but active-session views are still harder to operate
  than the backend capabilities.
- Guarded-live recovery does not yet cover a complete venue-native lifecycle for every supported
  venue.
- Provider delivery coverage is broad, but provider-owned incident ownership and policy management
  remain incomplete.
- Deployment, backup, and credential governance are not product-grade.
- LLM work includes provider-neutral judgement request/response contracts, `LlmJudgementPort`, a
  deterministic mock client, an OpenAI Responses structured-output adapter, and a veto-only wrapper
  for existing rule-based candidate signals. The active prompt profile is a general
  `elite_market_auditor_v1` market-audit prompt with recent feature history, sanitized strategy
  trace context, and dimension-level reviews. It still has no prompt registry, durable raw trace
  store, replay harness, or live-promotion path.
- Some extracted backend/frontend modules remain large and need continued flow-level decomposition.

## Immediate Priorities

1. Finish durable strategy lifecycle, promotion records, and normalized experiment artifact/export
   paths.
2. Make active runtime and guarded-live operation easier to inspect from the control room.
3. Tighten venue lifecycle recovery, drill evidence, deployment, backup, and secret-governance
   discipline.
4. Continue decomposing large provider-provenance, operator-delivery, and control-room modules by
   bounded operator flow.
5. Keep the LLM lane isolated from live promotion until provider adapters, prompt registry, raw
   trace storage, replay, evaluation, and operator review controls exist.

## Source Documents

- [Architecture](../architecture.md)
- [Roadmap](../roadmap/README.md)
- [Operations](../operations/runbooks-overview.md)
- [Blueprint](../blueprint/README.md)
