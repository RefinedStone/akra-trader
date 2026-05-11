from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

from akra_trader.adapters.binance import CcxtMarketDataAdapter
from akra_trader.adapters.core_storage import InMemoryCoreRepository
from akra_trader.adapters.in_memory_catalogs import LocalStrategyCatalog
from akra_trader.adapters.in_memory_market_data import SeededMarketDataAdapter
from akra_trader.api import include_routes
from akra_trader.application import TradingApplication
from akra_trader.application import HoldDecisionEngine
from akra_trader.bootstrap import Container
from akra_trader.config import Settings
from akra_trader.domain.models import Candle
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.main import create_app
from akra_trader.strategies.llm import ExternalDecisionStrategy


def build_client(tmp_path, *, live_enabled: bool = False) -> TestClient:
  settings = Settings(
    runs_database_url=f"sqlite:///{tmp_path / 'runs.sqlite3'}",
    market_data_provider="seeded",
    guarded_live_execution_enabled=live_enabled,
  )
  return TestClient(create_app(settings))


def build_application_client(app: TradingApplication) -> TestClient:
  fastapi_app = FastAPI()
  include_routes(fastapi_app, Container(app=app), "/api")
  return TestClient(fastapi_app)


class FakeOhlcvExchange:
  def __init__(
    self,
    *,
    start_at: datetime,
    candle_count: int,
    timeframe: timedelta = timedelta(minutes=5),
  ) -> None:
    self.calls: list[dict] = []
    self.rows = []
    for index in range(candle_count):
      timestamp = start_at + (timeframe * index)
      price = 100.0 + index
      self.rows.append(
        [
          int(timestamp.timestamp() * 1000),
          price,
          price + 2,
          price - 2,
          price + 1,
          1000 + index,
        ]
      )

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    self.calls.append(
      {"symbol": symbol, "timeframe": timeframe, "since": since, "limit": limit}
    )
    rows = self.rows
    if since is not None:
      rows = [row for row in rows if row[0] >= since]
    return rows[: limit or len(rows)]


class RecordingVenueExecution:
  def __init__(self) -> None:
    self.submit_calls = 0

  def describe_capability(self):
    return True, ()

  def submit_market_order(self, request):
    self.submit_calls += 1
    raise AssertionError("live worker must not submit market orders")

  def submit_limit_order(self, request):
    self.submit_calls += 1
    raise AssertionError("live worker must not submit limit orders")


def test_health_and_strategy_surface(tmp_path):
  client = build_client(tmp_path)

  health = client.get("/api/health").json()
  assert health["status"] == "ok"
  assert health["layers"] == [
    "backtest",
    "sandbox",
    "data",
    "live",
    "logs",
    "llm_strategy",
  ]

  strategies = client.get("/api/strategies").json()
  strategy_ids = {strategy["strategy_id"] for strategy in strategies["strategies"]}
  assert {"ma_cross_v1", "external_decision_template"}.issubset(strategy_ids)
  assert strategies["llm_strategy"]["provider_adapter"] is None
  assert "paper" not in {mode.value for mode in RunMode}


def test_backtest_create_list_detail_metrics_and_logs(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "parameters": {"short_window": 4, "long_window": 8},
    },
  )

  assert response.status_code == 200
  run = response.json()
  assert run["mode"] == "backtest"
  assert run["status"] == "completed"
  assert run["metrics"]["initial_cash"] == 10000.0

  run_id = run["run_id"]
  assert client.get("/api/runs", params={"mode": "backtest"}).json()["runs"][0]["run_id"] == run_id
  assert client.get(f"/api/runs/{run_id}").json()["run_id"] == run_id
  assert "ending_equity" in client.get(f"/api/runs/{run_id}/metrics").json()["metrics"]
  assert client.get(f"/api/runs/{run_id}/logs").json()["logs"][0]["event_type"] == "backtest_completed"


def test_sandbox_create_heartbeat_stop_and_log_filters(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "replay_bars": 80,
      "parameters": {"short_window": 3, "long_window": 6},
    },
  )

  assert response.status_code == 200
  run = response.json()
  assert run["mode"] == "sandbox"
  assert run["status"] == "running"
  assert run["runtime_session"]["worker_kind"] == "sandbox_native_worker"

  logs = client.get("/api/logs", params={"mode": "sandbox", "severity": "info"}).json()["logs"]
  assert any(log["event_type"] == "sandbox_started" for log in logs)

  stopped = client.post(f"/api/runs/{run['run_id']}/stop").json()
  assert stopped["status"] == "stopped"
  run_logs = client.get(f"/api/runs/{run['run_id']}/logs").json()["logs"]
  assert {log["event_type"] for log in run_logs}.issuperset({"sandbox_started", "run_stopped"})


def test_market_data_status_and_candles(tmp_path):
  client = build_client(tmp_path)

  status = client.get("/api/market-data/status", params={"timeframe": "5m"}).json()
  assert status["provider"] == "seeded"
  assert status["venue"] == "binance"
  assert len(status["instruments"]) == 3

  candles = client.get(
    "/api/market-data/candles",
    params={"symbol": "BTC/USDT", "timeframe": "5m", "limit": 5},
  ).json()
  assert candles["symbol"] == "BTC/USDT"
  assert len(candles["candles"]) == 5
  assert {"timestamp", "open", "high", "low", "close", "volume"}.issubset(
    candles["candles"][0]
  )


def test_seeded_market_data_sync_endpoint_is_fixture_noop(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/market-data/sync",
    json={
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "start_at": "2025-01-01T00:00:00Z",
      "end_at": "2025-01-01T00:20:00Z",
      "limit": 20,
    },
  )

  assert response.status_code == 200
  result = response.json()
  assert result["provider"] == "seeded"
  assert result["status"] == "fixture"
  assert result["symbol"] == "BTC/USDT"
  assert result["candle_count"] == 5


def test_binance_sync_endpoint_fetches_and_upserts_ohlcv(tmp_path):
  start_at = datetime(2026, 5, 1, tzinfo=UTC)
  exchange = FakeOhlcvExchange(start_at=start_at, candle_count=12)
  market_data = CcxtMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    default_candle_limit=5,
    historical_candle_limit=12,
    exchange_batch_limit=3,
    exchange=exchange,
    clock=lambda: start_at + timedelta(hours=2),
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
  )
  client = build_application_client(app)

  response = client.post(
    "/api/market-data/sync",
    json={
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "start_at": start_at.isoformat().replace("+00:00", "Z"),
      "end_at": (start_at + timedelta(minutes=20)).isoformat().replace("+00:00", "Z"),
      "limit": 2,
    },
  )

  assert response.status_code == 200
  result = response.json()
  assert result["provider"] == "binance"
  assert result["status"] == "synced"
  assert result["candle_count"] == 5
  assert len(exchange.calls) == 2
  assert len(market_data.get_candles(symbol="BTC/USDT", timeframe="5m")) == 5
  jobs = market_data.list_ingestion_jobs(symbol="BTC/USDT", timeframe="5m")
  assert jobs[0].operation == "sync_range"
  assert jobs[0].fetched_candle_count == 5


def test_backtest_backfills_requested_range_before_loading(tmp_path):
  start_at = datetime(2026, 5, 1, tzinfo=UTC)
  exchange = FakeOhlcvExchange(start_at=start_at, candle_count=30)
  market_data = CcxtMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange_batch_limit=10,
    exchange=exchange,
    clock=lambda: start_at + timedelta(hours=4),
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    parameters={"short_window": 3, "long_window": 5},
    start_at=start_at,
    end_at=start_at + timedelta(minutes=145),
  )

  assert run.status.value == "completed"
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.requested_start_at == start_at
  assert run.provenance.market_data.candle_count == 30
  assert len(exchange.calls) == 3


def test_backtest_fails_when_requested_range_remains_partial(tmp_path):
  start_at = datetime(2026, 5, 1, tzinfo=UTC)
  exchange = FakeOhlcvExchange(start_at=start_at, candle_count=25)
  market_data = CcxtMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    exchange_batch_limit=10,
    exchange=exchange,
    clock=lambda: start_at + timedelta(hours=4),
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    parameters={"short_window": 3, "long_window": 5},
    start_at=start_at,
    end_at=start_at + timedelta(minutes=145),
  )

  assert run.status.value == "failed"
  assert any("requested end" in note for note in run.notes)


def test_seeded_live_launch_gate_and_order_state(tmp_path):
  disabled_client = build_client(tmp_path / "disabled", live_enabled=False)
  disabled = disabled_client.post(
    "/api/runs/live",
    json={"strategy_id": "ma_cross_v1", "symbol": "SOL/USDT", "timeframe": "5m"},
  )
  assert disabled.status_code == 403

  live_client = build_client(tmp_path / "enabled", live_enabled=True)
  response = live_client.post(
    "/api/runs/live",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "SOL/USDT",
      "timeframe": "5m",
      "replay_bars": 100,
      "parameters": {"short_window": 3, "long_window": 8},
    },
  )
  assert response.status_code == 200
  run = response.json()
  assert run["mode"] == "live"
  assert run["status"] == "running"
  assert run["runtime_session"]["worker_kind"] == "guarded_live_native_worker"
  assert live_client.get(f"/api/runs/{run['run_id']}/orders").status_code == 200


def test_sandbox_worker_processes_each_new_closed_candle_once():
  now = datetime(2025, 1, 1, 20, 15, tzinfo=UTC)
  market_data = SeededMarketDataAdapter()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
    clock=lambda: now,
  )
  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    replay_bars=25,
    parameters={"short_window": 3, "long_window": 5},
  )
  initial_tick_count = run.provenance.runtime_session.processed_tick_count
  _append_seeded_candle(market_data, "BTC/USDT")
  _append_seeded_candle(market_data, "BTC/USDT")

  first = app.maintain_sandbox_worker_sessions()
  second = app.maintain_sandbox_worker_sessions()
  refreshed = app.get_run(run.config.run_id)

  assert first["heartbeated"] == 1
  assert second["heartbeated"] == 1
  assert refreshed is not None
  assert refreshed.provenance.runtime_session.processed_tick_count == initial_tick_count + 2
  assert refreshed.provenance.runtime_session.last_processed_candle_at == datetime(
    2025, 1, 1, 20, 5, tzinfo=UTC
  )


def test_live_worker_polls_data_without_venue_order_submission():
  now = datetime(2025, 1, 1, 20, 15, tzinfo=UTC)
  market_data = SeededMarketDataAdapter()
  venue_execution = RecordingVenueExecution()
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
    venue_execution=venue_execution,
    guarded_live_execution_enabled=True,
    clock=lambda: now,
  )
  run = app.start_live_run(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    replay_bars=25,
    parameters={"short_window": 3, "long_window": 5},
  )
  _append_seeded_candle(market_data, "BTC/USDT")

  app.maintain_guarded_live_worker_sessions()
  refreshed = app.get_run(run.config.run_id)

  assert venue_execution.submit_calls == 0
  assert refreshed is not None
  assert refreshed.provenance.runtime_session.last_processed_candle_at == datetime(
    2025, 1, 1, 20, 0, tzinfo=UTC
  )
  assert any("without venue order submission" in note for note in refreshed.notes)


def test_external_decision_strategy_keeps_trace_envelope():
  strategy = ExternalDecisionStrategy(HoldDecisionEngine())
  timestamp = datetime(2026, 5, 11, tzinfo=UTC)
  context = StrategyDecisionContext(
    timestamp=timestamp,
    instrument_id="binance:BTC/USDT",
    features={"close": 100.0},
    market={"close": 100.0},
    state=StrategyExecutionState(
      timestamp=timestamp,
      instrument_id="binance:BTC/USDT",
      has_position=False,
      cash=1000.0,
      position_size=0.0,
      parameters={},
    ),
  )

  envelope = strategy.decide(context)

  assert envelope.signal.action.value == "hold"
  assert envelope.context is context
  assert envelope.trace["boundary"] == "DecisionEnginePort"


def _append_seeded_candle(market_data: SeededMarketDataAdapter, symbol: str) -> None:
  candles = market_data._candles[symbol]
  previous = candles[-1]
  next_timestamp = previous.timestamp + timedelta(minutes=5)
  next_close = previous.close + 1
  candles.append(
    Candle(
      timestamp=next_timestamp,
      open=previous.close,
      high=next_close + 1,
      low=previous.close - 1,
      close=next_close,
      volume=previous.volume + 10,
    )
  )
