# Data trust and lineage

- Direction id: `data-trust-and-lineage`

## Goal

Harden the data plane so every run points to a stable dataset boundary, market-data freshness and
failures are operator-visible, and crypto-first ingestion can expand without weakening provenance.

## Current status on April 22, 2026

- deterministic dataset-boundary contracts, claim-aware rerun validation categories, lineage
  mismatch taxonomy, and operator-visible summaries are already implemented
- ingestion-job history plus normalized lineage query surfaces already exist for operator review
- market-data status already exposes freshness, gaps, backfill, lag, and failure history
- the remaining work is operator guidance, retention, escalation, and drill discipline on top of
  that baseline rather than first-time implementation

## Immediate gaps

- operator-facing lineage action guidance and escalation rules
- retention policy for lineage-history and ingestion-job review
- drill and runbook validation for data-boundary incidents

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/technical-roadmap.md`
- `docs/blueprint/platform-program.md`

## Success criteria

- runs carry stable dataset or sync-checkpoint identity strong enough to validate rerun boundaries
- market-data status exposes freshness, gap, and failure history in a way the operator can act on
  without shell access
- read-side market access and write-side synchronization stay separated behind ports and adapters
