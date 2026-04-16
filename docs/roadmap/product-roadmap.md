# Product Roadmap

Rebased to the repository state as of April 17, 2026.

## Objective

Turn the current research platform into a reliable single-operator trading workstation for crypto research first, then real-time sandbox operation, and only then controlled live execution.

## North Star

One operator should be able to do the following without ad hoc scripts:

1. ingest and inspect market data
2. register or select a strategy version
3. run a backtest with stored parameters and durable provenance
4. compare runs and understand why results differ
5. operate a continuous sandbox strategy from one control room
6. enable guarded live trading with explicit risk controls
7. evaluate LLM-assisted strategies without weakening deterministic paths

## Stage 0: Baseline

Status:

- complete

Implemented now:

- architecture and ADR baseline
- strategy lane abstraction
- reference catalog
- native runtime core
- initial control-room UI

## Stage 1: Research Foundation

Status:

- largely complete

Implemented now:

- durable run storage with restart-safe lookup
- Binance-backed market-data ingestion and status reporting
- strategy version and parameter snapshots in run provenance
- market-data lineage stored with runs
- historical run listing in API and UI

Still missing:

- stronger dataset pinning and checkpoint identity
- explicit proof that repeated identical inputs reproduce identical outputs

Exit gap:

- a run must record enough immutable data identity to support deterministic rerun claims

## Stage 2: Research Workflow

Status:

- partially complete

Implemented now:

- native vs reference benchmark workflow
- comparison API and control-room comparison surface
- strategy version filtering in run history
- reference provenance and artifact summaries

Still missing:

- durable strategy lifecycle management beyond current metadata fields
- run tags and scenario presets
- richer export and artifact retrieval flows
- stronger experiment query model than the current payload-centric repository

Exit gap:

- backtesting still behaves more like stored runs plus comparison than a complete experiment management workflow

## Stage 3: Real-Time Sandbox Operations

Status:

- groundwork only

Implemented now:

- market-data polling loop for Binance
- sandbox launch and stop controls
- replay-based sandbox preview runs on the native engine

Still missing:

- continuous sandbox workers
- heartbeat and restart recovery
- stale-data and worker-failure alerts
- richer operational views for positions, fills, and lag over time

Exit gap:

- current sandbox semantics are useful for previewing recent behavior, not for continuous operation

## Stage 4: Controlled Live Trading

Status:

- not started in practice

Implemented now:

- domain-level `live` execution mode placeholder
- guardrail intent captured in ADRs and roadmap

Still missing:

- exchange execution adapter
- secret handling
- risk-limit enforcement
- kill switch
- reconciliation
- operator audit log

Exit gap:

- no live order path should be added before safety state, auditability, and restart-safe reconciliation exist

## Stage 5: LLM Decision Research Lane

Status:

- interface skeleton only

Implemented now:

- `DecisionEnginePort`
- template external-decision strategy shape
- shared decision-envelope contract designed to contain traces later

Still missing:

- prompt template versioning
- raw prompt/response trace storage
- replay harness for historical evaluation
- provider adapters
- deterministic fallback or operator review workflow

Exit gap:

- the LLM lane should remain isolated from live promotion until traceability and fallback behavior are real features

## Success Measures

The next meaningful product checkpoint should satisfy these conditions:

- recent backtests are durable and comparable from the control room
- one operator can see market-data health and run history without shell access
- benchmark comparison between native and reference strategies is a normal workflow
- sandbox semantics are no longer confused with continuous execution
- roadmap and docs clearly separate implemented capability from planned capability

## Explicit Deferrals

- equal-weight support for stocks and crypto
- multi-user RBAC or organization workflows
- multi-node distributed execution
- public self-service product polish before operator-grade research workflows are stable
