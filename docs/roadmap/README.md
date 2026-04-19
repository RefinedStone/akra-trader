# Roadmap

This folder holds the current-first planning documents for `akra-trader`.

Use [Current State](../status/current-state.md) first. The roadmap documents below describe the remaining work after rebasing the docs to the repository state as of April 17, 2026.

## Current Snapshot

Implemented foundations:

- durable run storage
- Binance-backed market-data ingestion and sync
- native backtests
- replay-based sandbox previews
- reference catalog and NFI backtest delegation
- run comparison API and control-room comparison UI

Primary gaps:

- reproducibility hardening and dataset pinning
- durable experiment workflow features such as tags, presets, and lifecycle promotion
- continuous sandbox workers
- alerts, auditability, and operator tooling
- live execution guardrails
- traceable LLM research infrastructure

## Priority Basis

- If `current-state`, `roadmap`, and `blueprint` drift on program names or remaining-work order, repair that documentation drift first.
- Otherwise execute remaining work in this order:
  1. Research Core: reproducibility, dataset lineage, experiment metadata, and lifecycle
  2. Operations Core: worker/runtime stability, alerts, and operator-visible control-room surfaces
  3. Safe Execution: guarded-live audit, reconciliation, and execution controls
  4. Intelligence Research: isolated LLM trace, replay, evaluation, and fallback
- Documentation and Operational Discipline runs across every wave and can temporarily take precedence when plan clarity itself is broken.

## Stage Read

- Stage 0: complete
- Stage 1: largely complete
- Stage 2: partially complete
- Stage 3: not yet delivered
- Stage 4: not started
- Stage 5: scaffold only

## Documents

- [Current State](../status/current-state.md)
- [Blueprint](../blueprint/README.md)
- [Product Roadmap](product-roadmap.md)
- [Technical Roadmap](technical-roadmap.md)
- [Epic Backlog](epic-backlog.md)
- [ADR Index](../adr/README.md)
