# Akra Trader API

FastAPI backend for strategy cataloging, experiment execution, sandbox worker supervision,
guarded-live control, and operator visibility.

Updated for the repository state as of April 21, 2026.

## Current Scope

### Research and experiment surfaces

- strategy catalog for native strategies
- strategy semantic metadata and parameter-contract hints carried into run-facing surfaces
- durable run storage through SQLAlchemy
- native backtests
- presets, rerun boundaries, comparison, richer query/filter contracts, and typed query-discovery
  metadata
- run-surface capability contracts and shared run-subresource envelopes for action gating
- replay-link alias governance and audit export surfaces

### Runtime ops surfaces

- sandbox worker sessions with persisted heartbeat and recovery state
- separate paper sessions
- market-data status with checkpoints, backfill, gap visibility, lag, and failure history
- operator visibility for stale runtime, worker failure, and recent audit history

### Guarded-live surfaces

- kill switch, reconciliation, recovery, resume, and venue-backed live launch gates
- live order cancel and replace controls
- guarded-live incidents, delivery history, acknowledgment, escalation, and remediation state
- venue-session handoff baseline plus supported continuation paths for Binance, Coinbase Advanced
  Trade, and Kraken at the control-plane level

### Current limits

- durable custom strategy registration lifecycle is still missing
- experiment storage is still too payload-centric for some common paths
- guarded-live order management is broader than before, but not yet a full venue-native lifecycle
- incident provider coverage is broad, but provider-owned ownership and policy management are still
  incomplete
- concrete LLM provider adapters do not exist yet

## Run

```bash
python3 -m pip install -e ".[dev]"
uvicorn akra_trader.main:app --reload
```

Defaults:

- market-data provider: `binance`
- run database: repo-local SQLite if not overridden
- market-data database: repo-local SQLite if not overridden

## Key Configuration Areas

Representative environment variables:

- `AKRA_TRADER_CORS_ORIGIN`
- `AKRA_TRADER_MARKET_DATA_PROVIDER`
- `AKRA_TRADER_RUNS_DATABASE_URL`
- `AKRA_TRADER_MARKET_DATA_DATABASE_URL`
- `AKRA_TRADER_MARKET_DATA_SYMBOLS`
- `AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_INTERVAL_SECONDS`
- `AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
- `AKRA_TRADER_GUARDED_LIVE_EXECUTION_ENABLED`
- `AKRA_TRADER_GUARDED_LIVE_VENUE`
- `AKRA_TRADER_GUARDED_LIVE_API_KEY`
- `AKRA_TRADER_GUARDED_LIVE_API_SECRET`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_WEBHOOK_URL`
- `AKRA_TRADER_OPERATOR_ALERT_SLACK_WEBHOOK_URL`
- `AKRA_TRADER_OPERATOR_ALERT_EXTERNAL_SYNC_TOKEN`

The exhaustive provider and recovery-engine matrix is intentionally documented outside this README:

- [Operator Delivery Matrix](../../docs/operations/operator-delivery-matrix.md)

For the exact settings surface, see `apps/api/src/akra_trader/config.py`.

## Main Endpoint Groups

### Health and catalogs

- `GET /api/health`
- `GET /api/strategies`
- `POST /api/strategies/register`

### Experiment runs

- `GET /api/runs`
- `GET /api/runs/compare`
- `POST /api/runs/backtests`
- `POST /api/runs/sandbox`
- `POST /api/runs/paper`
- `POST /api/runs/live`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/backtests`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/paper`

### Run subresources and control actions

- `POST /api/runs/sandbox/{run_id}/stop`
- `POST /api/runs/paper/{run_id}/stop`
- `POST /api/runs/live/{run_id}/stop`
- `POST /api/runs/live/{run_id}/orders/{order_id}/cancel`
- `POST /api/runs/live/{run_id}/orders/{order_id}/replace`
- `GET /api/runs/{run_id}/orders`
- `GET /api/runs/{run_id}/positions`
- `GET /api/runs/{run_id}/metrics`

### Market, operator, and guarded-live

- `GET /api/market-data/status`
- `GET /api/operator/visibility`
- `POST /api/operator/incidents/external-sync`
- `GET /api/guarded-live`
- `POST /api/guarded-live/kill-switch/engage`
- `POST /api/guarded-live/kill-switch/release`
- `POST /api/guarded-live/reconciliation`
- `POST /api/guarded-live/recovery`
- `POST /api/guarded-live/incidents/{event_id}/acknowledge`
- `POST /api/guarded-live/incidents/{event_id}/remediate`
- `POST /api/guarded-live/incidents/{event_id}/escalate`
- `POST /api/guarded-live/resume`

## Runtime Notes

- backtests run to completion and persist immediately
- sandbox workers persist runtime-session progress, heartbeat, and recovery history
- paper runs use their own mode and history bucket
- guarded-live uses a separate control plane for kill switch, reconciliation, recovery, incidents,
  and live-session ownership
- operator delivery supports fanout plus workflow sync, but this remains a safety aid rather than a
  complete external incident-management replacement

## Test

```bash
pytest
```
