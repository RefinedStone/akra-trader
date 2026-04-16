# Technical Roadmap

Rebased to the repository state as of April 17, 2026.

## Goal

Advance the current architecture without breaking the core boundary rule:

- domain and application code stay independent from frameworks, exchanges, storage engines, and LLM providers

## Current Baseline

Already implemented:

- explicit ports for market data, strategy catalog, run storage, references, and decision engines
- native runtime services split into data, execution, risk, cache, and supervision concerns
- durable run storage through SQLAlchemy
- Binance market-data adapter with background sync support
- reference-runtime delegation for NFI backtests
- run comparison workflow through API and UI

Main weaknesses:

- run storage is durable but still payload-centric
- reproducibility metadata exists but is not yet fully pinned
- sandbox semantics are replay-oriented rather than worker-oriented
- observability and audit features are minimal
- the LLM lane is a contract, not a full research platform

## Track A: Data Platform

### Already implemented

- Binance-backed adapter behind `MarketDataPort`
- local SQL storage for candles and sync state
- resync, deduplication, gap detection, lag reporting, and backfill reporting
- background sync loop for tracked symbols

### Needs hardening

- stronger dataset identity and checkpointing per run
- explicit ingestion job history and failure retention
- clearer separation between read-side market access and write-side ingestion control

### Not started yet

- operator-facing ingestion failure history
- richer venue coverage beyond the current Binance path

## Track B: Experiment and Persistence Platform

### Already implemented

- durable run repository
- persisted run payloads including metrics, orders, fills, positions, notes, equity curve, and provenance
- run comparison queries
- strategy version and parameter snapshots in run provenance

### Needs hardening

- normalized tables for key run dimensions and metrics
- durable run tags and scenario presets
- export-friendly artifact storage model beyond the current provenance payload

### Not started yet

- full experiment query surface for tags, presets, and scenario history
- durable user strategy registration history

## Track C: Strategy Platform

### Already implemented

- explicit native and reference lanes
- decision-engine port and template strategy shape
- metadata normalization for built-in and reference strategies
- decision envelopes that can already carry trace metadata

### Needs hardening

- strategy lifecycle transitions beyond current static metadata fields
- richer trace schema for human and machine decisions
- scenario-aware context builders for multi-timeframe or multi-symbol strategies

### Not started yet

- provider-backed decision-engine research harness
- persistent promotion and archival workflow for strategy versions

## Track D: Real-Time Execution Platform

### Already implemented

- shared execution mode model across backtest and sandbox concepts
- native runtime services that can evolve toward worker-based operation
- API and UI controls for starting and stopping sandbox preview runs

### Needs hardening

- clear separation between sandbox preview and future continuous workers
- persisted worker state model that is distinct from replay results

### Not started yet

- long-running sandbox workers
- live execution adapter
- reconciliation after restart or faults
- exchange-native order state handling

## Track E: Safety, Observability, and Operations

### Already implemented

- basic market-data health surface
- reference and run provenance sufficient for research inspection

### Needs hardening

- structured operational events
- clearer failure surfacing for background sync and runtime errors
- service-level runbooks and deployment guidance

### Not started yet

- alerts for stale data, worker failure, and risk breaches
- operator event log
- live audit trail
- emergency stop workflow tied to real execution

## Technical Exit Criteria for the Next Major Milestone

The next milestone should meet these checks:

- repeated runs can point to a stable dataset identity
- strategy and run metadata can be queried without deserializing whole payloads for common cases
- sandbox semantics are backed by a real worker model instead of replay-only behavior
- operational failures are visible through platform surfaces rather than only through logs
- the LLM lane remains isolated until trace storage and replay controls exist
