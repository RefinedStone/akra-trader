# ADR 0002: Reproducible Runs and Persistent Experiment State

## Status

Accepted

## Historical note

This ADR captured the adoption-time baseline.

As of April 17, 2026, the repository already has durable run storage and a Binance-backed market-data adapter, but the reproducibility guarantees described here are still only partially complete.

## Context

The current platform still relies on in-memory run storage and seeded market data for the native demo
flow. That is sufficient for proving architecture, but it is insufficient for research credibility.

Backtests, sandbox runs, reference-runtime runs, and future live sessions must all be explainable after
the fact.

## Decision

Every run will be treated as a reproducible experiment or execution record.

At run creation time, the platform must persist:

- strategy id and strategy version
- runtime lane
- parameter snapshot
- venue, symbol set, timeframe, and execution mode
- dataset lineage or candle source metadata
- fee and slippage settings
- execution provenance such as reference id, external command, and artifact paths when applicable
- resulting metrics and operator notes

Run storage will move behind a persistent repository adapter, with Postgres as the default implementation target.

## Consequences

Positive:

- research comparisons become credible
- regressions can be diagnosed after restart
- live actions can share the same audit-oriented storage model
- external runtime delegation remains auditable instead of being a hidden subprocess detail

Negative:

- schema design becomes more important early
- more data retention and migration work is required

## Implementation notes

- reproducibility metadata is captured on creation, not inferred later
- any future result export feature should point back to one canonical stored run record
- sandbox and live runs should use the same persistence model with different execution-mode flags
- native and reference lanes should share one run record model with provenance extensions instead of
  separate storage shapes
