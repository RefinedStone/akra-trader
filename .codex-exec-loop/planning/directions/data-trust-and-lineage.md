# Data trust and lineage

- Direction id: `data-trust-and-lineage`

## Goal

Harden the data plane so every run points to a stable dataset boundary, market-data freshness and
failures are operator-visible, and crypto-first ingestion can expand without weakening provenance.

## Current status on April 21, 2026

- dataset fingerprints, sync-checkpoint linkage, and rerun boundaries already exist
- market-data status already exposes freshness, gaps, backfill, lag, and failure history
- the remaining work is about deterministic claims, mismatch interpretation, and normalized lineage
  surfaces rather than first-time implementation

## Immediate gaps

- stronger deterministic rerun validation
- lineage mismatch classification
- ingestion-job history and normalized lineage queries

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/technical-roadmap.md`
- `docs/blueprint/platform-program.md`

## Success criteria

- runs carry stable dataset or sync-checkpoint identity strong enough to validate rerun boundaries
- market-data status exposes freshness, gap, and failure history in a way the operator can act on
  without shell access
- read-side market access and write-side synchronization stay separated behind ports and adapters
