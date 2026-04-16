# Data trust and lineage

- Direction id: `data-trust-and-lineage`

## Goal

Harden the data plane so every run points to a stable dataset boundary, market-data freshness and failures are operator-visible, and crypto-first ingestion can expand without weakening provenance.

## Success criteria

- Runs carry stable dataset or sync-checkpoint identity strong enough to validate rerun boundaries.
- Market-data status exposes freshness, gap, and failure history in a way the operator can act on without shell access.
- Read-side market access and write-side synchronization stay separated behind ports and adapters.

## Scope hints

- Use docs/blueprint/platform-program.md Workstream A, docs/blueprint/metrics-and-gates.md Metric Group A, and docs/blueprint/risk-register.md Risk 1 as the main guardrails.
- Prefer dataset identity, ingestion history, and data-quality visibility ahead of new venue breadth or market expansion polish.
- Keep Binance crypto as the operational baseline while preserving a clean extension path for stocks.
