# ADR 0002: Reproducible Runs and Persistent Experiment State

## Status

Accepted

## Context

The current platform stores runs in memory and uses seeded data for the native demo flow. That is sufficient for proving architecture, but it is insufficient for research credibility.

Backtests, paper runs, and future live sessions must all be explainable after the fact.

## Decision

Every run will be treated as a reproducible experiment or execution record.

At run creation time, the platform must persist:

- strategy id and strategy version
- runtime lane
- parameter snapshot
- venue, symbol set, timeframe, and execution mode
- dataset lineage or candle source metadata
- fee and slippage settings
- resulting metrics and operator notes

Run storage will move behind a persistent repository adapter, with Postgres as the default implementation target.

## Consequences

Positive:

- research comparisons become credible
- regressions can be diagnosed after restart
- live actions can share the same audit-oriented storage model

Negative:

- schema design becomes more important early
- more data retention and migration work is required

## Implementation notes

- reproducibility metadata is captured on creation, not inferred later
- any future result export feature should point back to one canonical stored run record
- paper and live runs should use the same persistence model with different execution-mode flags
