# Akra Trader API

FastAPI backend for strategy research, run execution, sandbox workers, guarded-live controls, and
operator visibility.

## Scope

Implemented:

- native strategy catalog and registration endpoint
- durable backtests, run history, presets, comparisons, rerun boundaries, and run subresources
- market-data sync status, lineage history, ingestion jobs, gap/failure visibility, and drill
  evidence exports
- sandbox, paper, and guarded-live run paths
- guarded-live gates, kill switch, reconciliation, recovery, resume, order cancel/replace, incidents,
  delivery attempts, acknowledgments, escalation, and remediation state
- broad operator-delivery adapters behind registry-based target/provider normalization

Still incomplete:

- durable custom strategy lifecycle and promotion workflow
- fully normalized experiment artifact/export storage
- full venue-native live lifecycle recovery
- provider-owned incident ownership and policy management
- LLM prompt registry, replay, evaluation, and live-promotion controls

## Run

```bash
python3 -m pip install -e ".[dev]"
uvicorn akra_trader.main:app --reload
```

Defaults:

- market-data provider: `binance`
- run database: repo-local SQLite if not overridden
- market-data database: repo-local SQLite if not overridden
- LLM judgement provider: `disabled`; set `AKRA_TRADER_LLM_JUDGEMENT_PROVIDER=openai` and
  `AKRA_TRADER_OPENAI_API_KEY` or `OPENAI_API_KEY` for backtest/sandbox judgement

LLM judgement remains a veto-only overlay for an existing rule-strategy BUY/SELL candidate. It
does not upgrade HOLD candidates. The OpenAI prompt profile is `elite_market_auditor_v1`: it asks a
general market-audit trader to review trend, momentum, price structure, volatility/liquidity,
risk/reward, position context, and data quality using the latest snapshot, prioritized core
features, recent feature history, and sanitized strategy trace. The default judgement threshold is
`llm_judgement_min_confidence=0.60`; override it per run only when you want stricter or looser veto
behavior.

For the exact settings surface, read `apps/api/src/akra_trader/config.py`. For delivery targets and
workflow providers, read `apps/api/src/akra_trader/adapters/operator_delivery_registry.py`.

## Main Endpoint Groups

Health and catalogs:

- `GET /api/health`
- `GET /api/strategies`
- `POST /api/strategies/register`

Experiment runs:

- `GET /api/runs`
- `GET /api/runs/compare`
- `POST /api/runs/backtests`
- `POST /api/runs/sandbox`
- `POST /api/runs/paper`
- `POST /api/runs/live`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/backtests`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/paper`

Run subresources and actions:

- `GET /api/runs/{run_id}/orders`
- `GET /api/runs/{run_id}/positions`
- `GET /api/runs/{run_id}/metrics`
- `POST /api/runs/sandbox/{run_id}/stop`
- `POST /api/runs/paper/{run_id}/stop`
- `POST /api/runs/live/{run_id}/stop`
- `POST /api/runs/live/{run_id}/orders/{order_id}/cancel`
- `POST /api/runs/live/{run_id}/orders/{order_id}/replace`

Market, operator, and guarded live:

- `GET /api/market-data/status`
- `GET /api/operator/visibility`
- `POST /api/operator/incidents/external-sync`
- `GET /api/guarded-live`
- `POST /api/guarded-live/kill-switch/engage`
- `POST /api/guarded-live/kill-switch/release`
- `POST /api/guarded-live/reconciliation`
- `POST /api/guarded-live/recovery`
- `POST /api/guarded-live/resume`
- `POST /api/guarded-live/incidents/{event_id}/acknowledge`
- `POST /api/guarded-live/incidents/{event_id}/remediate`
- `POST /api/guarded-live/incidents/{event_id}/escalate`

## Test

```bash
pytest
```
