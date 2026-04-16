# Roadmap

This folder holds the product and technical planning documents for `akra-trader`.

## Planning principle

The project is intentionally split into three layers of planning:

1. Product roadmap
2. Technical roadmap
3. Execution backlog

The product roadmap answers:

- what user value we are trying to unlock
- in what order
- with what release checkpoints

The technical roadmap answers:

- which subsystems must mature
- what architectural constraints remain fixed
- which interfaces are expected to expand

The epic backlog answers:

- what concrete bodies of work should be executed next
- what each epic depends on
- what "done" means

## Current snapshot

As of the current baseline, the codebase provides:

- a FastAPI backend with hexagonal boundaries
- a native backtest and paper replay demo engine
- a strategy contract split into `feature frame -> decision context -> decision envelope`
- direct NostalgiaForInfinity reference cataloging and delegated Freqtrade backtest execution
- a lightweight React control room

The platform is not yet production-ready. The key missing capabilities are:

- persistent run storage
- real market data ingestion
- experiment versioning and comparison
- continuous real-time workers
- live-trading safety controls
- traceable LLM decision infrastructure

## Documents

- [Product Roadmap](product-roadmap.md)
- [Technical Roadmap](technical-roadmap.md)
- [Epic Backlog](epic-backlog.md)
- [ADR Index](../adr/README.md)
