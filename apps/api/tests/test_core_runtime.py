from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pandas as pd
import pytest
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
from akra_trader.domain.models import ExecutionPlan
from akra_trader.domain.models import LlmFunctionLayer
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.services import apply_signal
from akra_trader.main import create_app
from akra_trader.runtime import StateCache
from akra_trader.strategies.composable import RsiFeature
from akra_trader.strategies.llm import ExternalDecisionStrategy
from akra_trader.strategies.quant_examples import Rsi14OversoldReversalStrategy
from akra_trader.strategies.quant_examples import RsiAtrOversoldPeakTurnStrategy


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
  assert {
    "ma_cross_v1",
    "rsi14_oversold_reversal_v1",
    "rsi_atr_oversold_peak_turn_v1",
    "external_decision_template",
  }.issubset(strategy_ids)
  reversal_strategy = next(
    strategy
    for strategy in strategies["strategies"]
    if strategy["strategy_id"] == "rsi14_oversold_reversal_v1"
  )
  assert reversal_strategy["runtime"] == "native_composable"
  assert reversal_strategy["name"] == "RSI14 과매도 탈출 반등 매수"
  assert reversal_strategy["parameter_schema"]["ma20_window"]["default"] == 20
  assert reversal_strategy["parameter_schema"]["ma60_window"]["default"] == 60
  assert reversal_strategy["parameter_schema"]["rsi_window"]["default"] == 14
  assert reversal_strategy["parameter_schema"]["rsi_oversold_level"]["default"] == 30
  assert reversal_strategy["parameter_schema"]["entry_lookback_bars"]["default"] == 80
  assert reversal_strategy["parameter_schema"]["entry_breakout_grace_bars"]["default"] == 20
  assert reversal_strategy["parameter_schema"]["entry_enable_early_reversal"]["default"] is False
  assert reversal_strategy["parameter_schema"]["entry_trigger_mode"]["default"] == "rsi_turn"
  assert reversal_strategy["parameter_schema"]["entry_enable_capitulation_rebound"]["default"] is True
  assert reversal_strategy["parameter_schema"]["entry_max_rsi_rebound"]["default"] == 10.0
  assert reversal_strategy["parameter_schema"]["entry_min_close_position"]["default"] == 0.75
  assert reversal_strategy["parameter_schema"]["entry_trend_filter_mode"]["default"] == "above60"
  assert reversal_strategy["parameter_schema"]["swing_lookback_bars"]["default"] == 80
  assert reversal_strategy["parameter_schema"]["exit_rsi_profit_level"]["default"] == 50
  assert reversal_strategy["parameter_schema"]["exit_enable_rsi_profit"]["default"] is False
  assert reversal_strategy["parameter_schema"]["exit_enable_ma_resistance"]["default"] is False
  assert reversal_strategy["parameter_schema"]["exit_enable_swing_low_stop"]["default"] is False
  assert reversal_strategy["parameter_schema"]["exit_profit_r_multiple"]["default"] == 1.5
  assert reversal_strategy["parameter_schema"]["exit_hold_profit_with_trailing"]["default"] is False
  assert reversal_strategy["parameter_schema"]["exit_trailing_activation_r"]["default"] == 5.0
  assert reversal_strategy["parameter_schema"]["exit_trailing_distance_atr"]["default"] == 1.2
  assert reversal_strategy["parameter_schema"]["exit_time_stop_bars"]["default"] == 288
  assert reversal_strategy["parameter_schema"]["cooldown_after_stop_bars"]["default"] == 20
  assert reversal_strategy["parameter_schema"]["max_position_fraction"]["default"] == 1.0
  assert reversal_strategy["parameter_schema"]["atr_stop_multiple"]["default"] == 4.0
  assert (
    "RSI14 과매도 탈출"
    in reversal_strategy["parameter_schema"]["rsi_window"]["description_ko"]
  )
  quant_strategy = next(
    strategy
    for strategy in strategies["strategies"]
    if strategy["strategy_id"] == "rsi_atr_oversold_peak_turn_v1"
  )
  assert quant_strategy["runtime"] == "native_composable"
  assert quant_strategy["name"] == "RSI ATR Oversold Peak Turn"
  assert quant_strategy["catalog_semantics"]["strategy_kind"] == "composable_quant"
  assert quant_strategy["parameter_schema"]["rsi_timeframe"]["enum"] == [
    "base",
    "5m",
    "15m",
    "1h",
    "4h",
    "1d",
  ]
  assert "rsi_oversold_level" in quant_strategy["parameter_schema"]
  assert "과매도 기준선" in quant_strategy["parameter_schema"]["rsi_oversold_level"]["description_ko"]
  assert "risk_fraction" in quant_strategy["parameter_schema"]
  assert "포트폴리오 위험 비율" in quant_strategy["parameter_schema"]["risk_fraction"]["description_ko"]
  assert quant_strategy["parameter_schema"]["entry_min_trend_spread_atr"]["default"] == 0.5
  assert (
    "매수 추세 강도"
    in quant_strategy["parameter_schema"]["entry_min_trend_spread_atr"]["description_ko"]
  )
  assert quant_strategy["parameter_schema"]["entry_enable_rsi_recovery"]["default"] is True
  assert quant_strategy["parameter_schema"]["entry_require_price_above_slow_ema"]["default"] is False
  assert quant_strategy["parameter_schema"]["entry_enable_range_oversold_recovery"]["default"] is False
  assert quant_strategy["parameter_schema"]["entry_recovery_max_rsi"]["default"] == 38
  assert quant_strategy["parameter_schema"]["entry_recovery_max_low_proximity_atr"]["default"] == 1.5
  assert quant_strategy["parameter_schema"]["entry_recovery_min_trend_spread_atr"]["default"] == -2.0
  assert quant_strategy["parameter_schema"]["entry_recovery_min_rsi_delta"]["default"] == 5.0
  assert quant_strategy["parameter_schema"]["entry_recovery_min_close_position"]["default"] == 0.7
  assert quant_strategy["parameter_schema"]["exit_score_threshold"]["default"] == 0.75
  assert (
    "SELL 점수 임계값"
    in quant_strategy["parameter_schema"]["exit_score_threshold"]["description_ko"]
  )
  assert quant_strategy["parameter_schema"]["exit_trailing_activation_atr"]["default"] == 1.5
  assert quant_strategy["parameter_schema"]["exit_trailing_distance_atr"]["default"] == 2.0
  assert (
    "트레일링 활성화"
    in quant_strategy["parameter_schema"]["exit_trailing_activation_atr"]["description_ko"]
  )
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
  logs = client.get(f"/api/runs/{run_id}/logs").json()["logs"]
  assert logs[0]["event_type"] == "backtest_completed"
  assert logs[0]["payload"]["market_data"]["candle_count"] == run["market_data"]["candle_count"]
  window_log = next(log for log in logs if log["event_type"] == "backtest_window_validated")
  assert window_log["payload"]["validation_status"] == "valid"
  assert window_log["payload"]["candle_count"] == run["market_data"]["candle_count"]
  assert window_log["payload"]["first_strategy_evaluation_at"] is not None


def test_composable_quant_strategy_runs_as_builtin_sample(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "rsi_atr_oversold_peak_turn_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "parameters": {
        "fast_ema_window": 8,
        "slow_ema_window": 21,
        "rsi_window": 8,
        "atr_window": 8,
        "use_llm_regime_hint": False,
      },
    },
  )

  assert response.status_code == 200
  run = response.json()
  assert run["strategy"]["strategy_id"] == "rsi_atr_oversold_peak_turn_v1"
  assert run["strategy"]["parameter_snapshot"]["resolved"]["fast_ema_window"] == 8
  assert run["status"] == "completed"


def test_rsi14_oversold_reversal_runs_as_builtin_strategy(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "rsi14_oversold_reversal_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "parameters": {
        "ma20_window": 5,
        "ma60_window": 10,
        "rsi_window": 3,
        "atr_window": 3,
      },
    },
  )

  assert response.status_code == 200
  run = response.json()
  assert run["strategy"]["strategy_id"] == "rsi14_oversold_reversal_v1"
  assert run["strategy"]["parameter_snapshot"]["resolved"]["rsi_window"] == 3
  assert run["status"] == "completed"


def test_run_request_datetimes_align_to_timeframe(tmp_path):
  client = build_client(tmp_path)

  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "start_at": "2025-01-01T00:19:00Z",
      "end_at": "2025-01-01T02:19:00Z",
      "parameters": {"short_window": 3, "long_window": 5},
    },
  )

  assert response.status_code == 200
  run = response.json()
  assert run["config"]["start_at"] == "2025-01-01T00:20:00Z"
  assert run["config"]["end_at"] == "2025-01-01T02:15:00Z"
  assert run["status"] == "completed"
  logs = client.get(f"/api/runs/{run['run_id']}/logs").json()["logs"]
  window_log = next(log for log in logs if log["event_type"] == "backtest_window_validated")
  assert window_log["payload"]["expected_candle_count"] == 24
  assert window_log["payload"]["candle_count_matches_expected"] is True


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


def test_market_data_candles_explicit_start_can_return_full_range_without_limit(tmp_path):
  start_at = datetime(2025, 5, 1, tzinfo=UTC)
  candle_count = 6_000
  end_at = start_at + timedelta(minutes=15 * (candle_count - 1))
  exchange = FakeOhlcvExchange(
    start_at=start_at,
    candle_count=candle_count,
    timeframe=timedelta(minutes=15),
  )
  market_data = CcxtMarketDataAdapter(
    database_url=f"sqlite:///{tmp_path / 'market.sqlite3'}",
    tracked_symbols=("BTC/USDT",),
    default_candle_limit=500,
    historical_candle_limit=500,
    exchange_batch_limit=1_000,
    exchange=exchange,
    clock=lambda: end_at + timedelta(hours=1),
  )
  app = TradingApplication(
    market_data=market_data,
    strategies=LocalStrategyCatalog(),
    runs=InMemoryCoreRepository(),
  )
  client = build_application_client(app)

  sync_response = client.post(
    "/api/market-data/sync",
    json={
      "symbol": "BTC/USDT",
      "timeframe": "15m",
      "start_at": start_at.isoformat().replace("+00:00", "Z"),
      "end_at": end_at.isoformat().replace("+00:00", "Z"),
    },
  )
  candle_response = client.get(
    "/api/market-data/candles",
    params={
      "symbol": "BTC/USDT",
      "timeframe": "15m",
      "start_at": start_at.isoformat().replace("+00:00", "Z"),
      "end_at": end_at.isoformat().replace("+00:00", "Z"),
    },
  )

  assert sync_response.status_code == 200
  assert sync_response.json()["candle_count"] == candle_count
  assert candle_response.status_code == 200
  candles = candle_response.json()["candles"]
  assert candle_response.json()["limit"] is None
  assert len(candles) == candle_count
  assert candles[0]["timestamp"] == start_at.isoformat().replace("+00:00", "Z")
  assert candles[-1]["timestamp"] == end_at.isoformat().replace("+00:00", "Z")


def test_binance_sync_accepts_weekly_and_monthly_ohlcv(tmp_path):
  for timeframe, start_at, candle_times in (
    (
      "1w",
      datetime(2026, 1, 5, tzinfo=UTC),
      (
        datetime(2026, 1, 5, tzinfo=UTC),
        datetime(2026, 1, 12, tzinfo=UTC),
        datetime(2026, 1, 19, tzinfo=UTC),
      ),
    ),
    (
      "1M",
      datetime(2026, 1, 1, tzinfo=UTC),
      (
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 2, 1, tzinfo=UTC),
        datetime(2026, 3, 1, tzinfo=UTC),
      ),
    ),
  ):
    exchange = FakeOhlcvExchange(start_at=start_at, candle_count=3)
    for index, candle_at in enumerate(candle_times):
      exchange.rows[index][0] = int(candle_at.timestamp() * 1000)
    market_data = CcxtMarketDataAdapter(
      database_url=f"sqlite:///{tmp_path / f'market_{timeframe}.sqlite3'}",
      tracked_symbols=("BTC/USDT",),
      exchange_batch_limit=2,
      exchange=exchange,
      clock=lambda: candle_times[-1] + timedelta(days=1),
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
        "timeframe": timeframe,
        "start_at": start_at.isoformat().replace("+00:00", "Z"),
        "end_at": candle_times[-1].isoformat().replace("+00:00", "Z"),
        "limit": 5,
      },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "synced"
    assert exchange.calls[0]["timeframe"] == timeframe
    assert len(market_data.get_candles(symbol="BTC/USDT", timeframe=timeframe)) == 3


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


def test_composable_strategy_exposes_trace_layers_and_llm_function():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  timestamp = datetime(2026, 5, 11, tzinfo=UTC)
  rows = []
  for index in range(80):
    close = 100 + index * 0.5
    rows.append(
      {
        "timestamp": timestamp + timedelta(minutes=5 * index),
        "open": close - 0.2,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000 + index,
      }
    )
  parameters = {
    "fast_ema_window": 8,
    "slow_ema_window": 21,
    "rsi_window": 8,
    "atr_window": 8,
  }
  enriched = strategy.build_feature_frame(pd.DataFrame(rows), parameters)
  state = StrategyExecutionState(
    timestamp=rows[-1]["timestamp"],
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters=parameters,
  )

  context = strategy.build_decision_context(enriched, parameters, state)
  fallback_result = context.llm.function(
    "arbitrary_research_call",
    {"close": context.market["close"]},
    fallback={"allow": True},
  )
  envelope = strategy.evaluate(enriched, parameters, state)

  assert isinstance(context.llm, LlmFunctionLayer)
  assert fallback_result.output == {"allow": True}
  assert fallback_result.used_fallback is True
  assert "feature_pipeline" in envelope.trace["architecture"]["layers"]
  assert "llm_function_layer" in envelope.trace["architecture"]["layers"]
  assert envelope.trace["regime"]["trace"]["regimes"][1]["provider"] == "disabled"


def test_rsi_feature_uses_wilder_smoothing():
  frame = pd.DataFrame(
    {
      "timestamp": pd.date_range("2026-05-11T00:00:00Z", periods=5, freq="5min"),
      "close": [100.0, 102.0, 101.0, 103.0, 102.0],
    }
  )
  feature = RsiFeature("close", "rsi", "rsi_window", 2)

  enriched = feature.apply(frame, {"rsi_window": 2})

  assert enriched.iloc[2]["rsi"] == pytest.approx(66.6667, abs=0.0001)
  assert enriched.iloc[3]["rsi"] == pytest.approx(85.7143, abs=0.0001)
  assert enriched.iloc[4]["rsi"] == pytest.approx(54.5455, abs=0.0001)
  assert enriched.iloc[4]["rsi_previous"] == pytest.approx(85.7143, abs=0.0001)
  assert enriched.iloc[4]["rsi_previous2"] == pytest.approx(66.6667, abs=0.0001)


def test_rsi_feature_can_align_higher_timeframe_values_to_base_candles():
  frame = pd.DataFrame(
    {
      "timestamp": pd.date_range("2026-05-11T00:00:00Z", periods=9, freq="5min"),
      "close": [100.0, 100.5, 100.0, 100.0, 101.0, 102.0, 102.0, 101.5, 101.0],
    }
  )
  feature = RsiFeature(
    "close",
    "rsi",
    "rsi_window",
    2,
    timeframe_parameter="rsi_timeframe",
    default_timeframe="base",
  )

  enriched = feature.apply(frame, {"rsi_window": 2, "rsi_timeframe": "15m"})

  assert enriched.iloc[7]["rsi"] == 50.0
  assert enriched.iloc[8]["rsi"] == pytest.approx(66.6667, abs=0.0001)
  assert enriched.iloc[8]["rsi_previous"] == 50.0


def test_buy_execution_stores_fixed_stop_loss_and_take_profit_prices():
  timestamp = datetime(2026, 5, 11, tzinfo=UTC)

  _, position, _, _, _ = apply_signal(
    run_id="run-1",
    instrument_id="binance:BTC/USDT",
    signal=SignalDecision(timestamp=timestamp, action=SignalAction.BUY),
    execution=ExecutionPlan(size_fraction=0.5, stop_loss_pct=0.10, take_profit_pct=0.25),
    market_price=100.0,
    position=None,
    cash=10_000.0,
    fee_rate=0.0,
    slippage_bps=0.0,
  )

  assert position is not None
  assert position.average_price == pytest.approx(100.0)
  assert position.stop_loss_price == pytest.approx(90.0)
  assert position.take_profit_price == pytest.approx(125.0)
  assert position.high_watermark_price == pytest.approx(100.0)
  cache = StateCache(instrument_id="binance:BTC/USDT", cash=5_000.0)
  cache.apply(cash=5_000.0, position=position)
  cache.mark_price(101.0, market_high=108.0)
  snapshot = cache.snapshot(timestamp=timestamp, parameters={})
  assert snapshot.position_average_price == pytest.approx(100.0)
  assert snapshot.position_stop_loss_price == pytest.approx(90.0)
  assert snapshot.position_take_profit_price == pytest.approx(125.0)
  assert snapshot.position_high_watermark_price == pytest.approx(108.0)
  assert snapshot.position_trailing_stop_price is None


def test_rsi14_oversold_reversal_buys_escape_breakout():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (36.0, 25.0, 31.0),
    closes=(100.0, 98.0, 99.2),
    ma20=(98.8, 98.9, 99.0),
    ma60=(98.0, 98.1, 98.2),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={"entry_trigger_mode": "escape_breakout", "entry_min_close_position": 0.5},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.signal.reason == "entry_conditions_met:rsi14_oversold_escape_rebound"
  assert envelope.trace["entry"]["filters"]["recent_oversold"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["rsi_crossed_oversold_recent"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["close_above_previous_high"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["trend_filter"]["passed"] is True


def test_rsi14_oversold_reversal_buys_breakout_after_reclaim_grace():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (25.0, 31.0, 35.0),
    closes=(98.0, 98.2, 99.5),
    ma20=(98.0, 98.2, 98.4),
    ma60=(97.0, 97.2, 97.4),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "escape_breakout",
      "entry_breakout_grace_bars": 2,
      "entry_min_close_position": 0.5,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["entry"]["filters"]["rsi_crossed_oversold"]["passed"] is False
  assert envelope.trace["entry"]["filters"]["rsi_crossed_oversold_recent"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["rsi_crossed_oversold_recent"]["bars_since_cross"] == 1
  assert envelope.trace["entry"]["filters"]["close_above_previous_high"]["passed"] is True


def test_rsi14_oversold_reversal_buys_early_oversold_rebound_near_low():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (34.0, 25.0, 27.0),
    closes=(100.0, 98.0, 98.6),
    ma20=(98.0, 98.1, 98.2),
    ma60=(97.0, 97.1, 97.2),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_early_reversal": True,
      "entry_trigger_mode": "early_reversal",
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 2.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.signal.reason == "entry_conditions_met:rsi14_oversold_early_reversal"
  assert envelope.trace["entry"]["early_reversal_matched"] is True
  assert envelope.trace["entry"]["filters"]["early_reversal"]["early_rsi_rebound"] is True


def test_rsi14_oversold_reversal_buys_rsi_turn_after_recent_oversold():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (24.0, 32.0, 34.0),
    closes=(100.0, 100.2, 100.8),
    ma20=(101.0, 101.0, 101.0),
    ma60=(102.0, 102.0, 102.0),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "rsi_turn",
      "entry_trend_filter_mode": "any",
      "rsi_oversold_level": 35,
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 3.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.signal.reason == "entry_conditions_met:rsi14_oversold_rsi_turn"
  assert envelope.trace["entry"]["rsi_turn_matched"] is True


def test_rsi14_oversold_reversal_rejects_overextended_rsi_rebound():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (29.0, 39.0, 53.5),
    closes=(100.0, 100.2, 101.2),
    ma20=(99.0, 99.1, 99.2),
    ma60=(98.0, 98.1, 98.2),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "rsi_turn",
      "entry_max_rsi_rebound": 10.0,
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 3.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["rsi_turn_matched"] is False
  assert envelope.trace["entry"]["filters"]["rsi_rebound_limit"]["passed"] is False
  assert envelope.trace["entry"]["filters"]["rsi_rebound_limit"]["rsi_rebound_delta"] == pytest.approx(14.5)


def test_rsi14_oversold_reversal_rejects_late_rebound_without_ma20_reclaim():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (24.0, 32.0, 34.0),
    closes=(100.0, 100.2, 101.6),
    ma20=(102.0, 102.0, 102.0),
    ma60=(99.0, 99.0, 99.0),
    recent_lower_lows=False,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "rsi_turn",
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 3.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["rsi_turn_matched"] is True
  quality = envelope.trace["entry"]["filters"]["extended_standard_rebound_quality"]
  assert quality["standard_passed"] is False
  assert quality["low_proximity_atr"] == pytest.approx(2.6)
  assert "extended_standard_rebound_quality" in envelope.trace["entry"]["reason"]


def test_rsi14_oversold_reversal_allows_deep_late_washout_rebound():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (17.0, 35.0, 40.0),
    closes=(100.5, 99.8, 100.0),
    ma20=(101.5, 101.0, 100.5),
    ma60=(99.0, 99.2, 99.4),
    ma20_slope=-30.0,
    recent_lower_lows=False,
    atr=0.35,
  )
  frame["recent_price_swing_low"] = 99.0
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "rsi_turn",
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 3.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  quality = envelope.trace["entry"]["filters"]["extended_standard_rebound_quality"]
  assert quality["deep_standard_washout_quality"] is True
  assert quality["standard_passed"] is True


def test_rsi14_oversold_reversal_buys_capitulation_rebound_below_ma60():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (17.0, 34.0, 40.0),
    closes=(100.0, 99.8, 100.0),
    ma20=(101.0, 101.5, 100.5),
    ma60=(151.0, 150.9, 100.9),
    ma20_slope=-100.0,
    recent_lower_lows=True,
    atr=0.35,
  )
  frame.loc[frame.index[-1], "open"] = 99.6
  frame.loc[frame.index[-1], "high"] = 100.2
  frame.loc[frame.index[-1], "low"] = 99.0
  frame["recent_price_swing_low"] = frame["low"].rolling(window=5, min_periods=1).min()
  frame["previous_price_swing_low"] = frame["low"].shift(1).rolling(window=5, min_periods=1).min()
  frame["ma60_slope"] = -50.0
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.signal.reason == "entry_conditions_met:rsi14_capitulation_rebound"
  assert envelope.trace["entry"]["capitulation_rebound_matched"] is True
  assert envelope.trace["entry"]["filters"]["trend_filter"]["standard_trend_filter"] is False
  assert envelope.trace["entry"]["filters"]["trend_filter"]["capitulation_rebound_override"] is True
  assert envelope.trace["entry"]["filters"]["structural_downtrend_block"]["raw_blocked"] is True
  assert envelope.trace["entry"]["filters"]["structural_downtrend_block"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["extended_standard_rebound_quality"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["extended_standard_rebound_quality"]["capitulation_rebound_override"] is True


def test_rsi14_oversold_reversal_rejects_without_previous_high_breakout():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 29.0, 31.0),
    closes=(100.0, 98.0, 98.8),
    ma20=(98.0, 98.1, 98.2),
    ma60=(97.0, 97.1, 97.2),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_trigger_mode": "escape_breakout",
      "entry_breakout_grace_bars": 2,
      "entry_min_close_position": 0.5,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["filters"]["rsi_crossed_oversold_recent"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["close_above_previous_high"]["passed"] is False
  assert "close_above_previous_high" in envelope.trace["entry"]["reason"]


def test_rsi14_oversold_reversal_allows_ma20_slope_trend_filter():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 29.0, 31.0),
    closes=(96.0, 94.0, 95.2),
    ma20=(98.0, 98.1, 98.2),
    ma60=(99.0, 99.1, 99.2),
    ma20_slope=0.1,
    atr=2.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_trigger_mode": "escape_breakout",
      "entry_trend_filter_mode": "loose",
      "entry_min_close_position": 0.5,
      "entry_max_low_proximity_atr": 3.0,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["entry"]["filters"]["trend_filter"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["trend_filter"]["ma20_slope_non_negative"] is True


def test_rsi14_oversold_reversal_blocks_structural_downtrend():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 29.0, 31.0),
    closes=(96.0, 94.0, 95.2),
    ma20=(98.0, 97.0, 96.0),
    ma60=(102.0, 101.0, 100.0),
    ma20_slope=-2.0,
    recent_lower_lows=True,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["structural_downtrend_block"] is True
  assert envelope.trace["entry"]["filters"]["structural_downtrend_block"]["passed"] is False
  assert "structural_downtrend_block" in envelope.trace["entry"]["reason"]


def test_rsi14_oversold_reversal_sells_on_swing_low_stop():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 34.0, 33.0),
    closes=(101.0, 100.0, 97.9),
    ma20=(99.0, 99.0, 99.0),
    ma60=(98.0, 98.0, 98.0),
    previous_price_swing_low=98.0,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=frame.iloc[1]["timestamp"].to_pydatetime(),
    position_stop_loss_price=98.5,
    parameters={"exit_enable_swing_low_stop": True, "cooldown_after_stop_bars": 5},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.signal.reason == "swing_low_stop"
  assert envelope.trace["exit"]["is_stop_exit"] is True


def test_rsi14_oversold_reversal_sells_on_profit_r_target():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 40.0, 45.0),
    closes=(100.5, 101.0, 102.3),
    ma20=(98.0, 98.0, 98.0),
    ma60=(97.0, 97.0, 97.0),
    previous_price_swing_low=95.0,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=frame.iloc[1]["timestamp"].to_pydatetime(),
    position_stop_loss_price=98.5,
    parameters={
      "exit_profit_r_multiple": 1.5,
      "exit_hold_profit_with_trailing": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.signal.reason == "profit_r_target"
  assert envelope.trace["exit"]["profit_r"] == pytest.approx(1.5333, abs=0.0001)


def test_rsi14_oversold_reversal_holds_profit_target_with_trailing():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 40.0, 45.0),
    closes=(100.5, 101.0, 102.3),
    ma20=(98.0, 98.0, 98.0),
    ma60=(97.0, 97.0, 97.0),
    previous_price_swing_low=95.0,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=frame.iloc[1]["timestamp"].to_pydatetime(),
    position_stop_loss_price=98.5,
    parameters={
      "exit_profit_r_multiple": 1.5,
      "exit_hold_profit_with_trailing": True,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["exit"]["reason"] == (
    "profit_trailing_active_holding_until_stop:profit_r_target"
  )
  assert envelope.trace["exit"]["trailing_active"] is True
  assert envelope.trace["exit"]["trailing_stop_price"] == pytest.approx(102.1)
  assert "trailing_stop=102.10" in envelope.rationale


def test_rsi14_oversold_reversal_sells_on_trailing_stop_after_profit():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 45.0, 43.0),
    closes=(100.5, 103.0, 101.8),
    ma20=(98.0, 98.0, 98.0),
    ma60=(97.0, 97.0, 97.0),
    previous_price_swing_low=95.0,
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=frame.iloc[1]["timestamp"].to_pydatetime(),
    position_stop_loss_price=98.5,
    position_high_watermark_price=104.0,
    position_trailing_stop_price=102.0,
    parameters={
      "entry_trigger_mode": "escape_breakout",
      "entry_min_close_position": 0.5,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.signal.reason == "trailing_stop"
  assert envelope.trace["exit"]["trailing_stop_price"] == pytest.approx(102.8)
  assert envelope.trace["exit"]["components"]["trailing_stop"]["active"] is True


def test_rsi14_oversold_reversal_sells_on_time_stop_without_profit():
  strategy = Rsi14OversoldReversalStrategy()
  frame = _rsi14_escape_frame(
    (35.0, 40.0, 42.0),
    closes=(100.0, 99.9, 99.8),
    ma20=(98.0, 98.0, 98.0),
    ma60=(97.0, 97.0, 97.0),
    previous_price_swing_low=95.0,
    atr=1.0,
  )
  opened_at = frame.iloc[-1]["timestamp"].to_pydatetime() - timedelta(minutes=35)
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=opened_at,
    position_stop_loss_price=98.5,
    parameters={"exit_time_stop_bars": 7},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.signal.reason == "time_no_profit"
  assert envelope.trace["exit"]["bars_since_entry"] == 7


def test_rsi14_oversold_reversal_blocks_reentry_during_stop_cooldown():
  strategy = Rsi14OversoldReversalStrategy()
  stop_frame = _rsi14_escape_frame(
    (35.0, 34.0, 33.0),
    closes=(101.0, 100.0, 97.9),
    ma20=(99.0, 99.0, 99.0),
    ma60=(98.0, 98.0, 98.0),
    bar_index=20,
    previous_price_swing_low=98.0,
    atr=1.0,
  )
  stop_state = StrategyExecutionState(
    timestamp=stop_frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=5_000.0,
    position_size=1.0,
    position_average_price=100.0,
    position_opened_at=stop_frame.iloc[1]["timestamp"].to_pydatetime(),
    position_stop_loss_price=98.5,
    parameters={"exit_enable_swing_low_stop": True, "cooldown_after_stop_bars": 5},
  )
  stop_envelope = strategy.evaluate(stop_frame, stop_state.parameters, stop_state)
  assert stop_envelope.signal.reason == "swing_low_stop"

  entry_frame = _rsi14_escape_frame(
    (36.0, 25.0, 31.0),
    closes=(100.0, 98.0, 99.2),
    ma20=(98.8, 98.9, 99.0),
    ma60=(98.0, 98.1, 98.2),
    bar_index=21,
    atr=1.0,
  )
  entry_state = StrategyExecutionState(
    timestamp=entry_frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "entry_trigger_mode": "escape_breakout",
      "entry_min_close_position": 0.5,
    },
  )

  entry_envelope = strategy.evaluate(entry_frame, entry_state.parameters, entry_state)

  assert entry_envelope.signal.action == SignalAction.HOLD
  assert entry_envelope.trace["entry"]["filters"]["cooldown"]["active"] is True
  assert "cooldown" in entry_envelope.trace["entry"]["reason"]


def test_rsi_atr_oversold_peak_turn_buys_when_oversold_rsi_peak_rolls_over():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame((24.0, 28.0, 26.0))
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_range_oversold_recovery": True,
      "entry_recovery_min_close_position": 0.5,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["entry"]["matched"] is True
  assert envelope.trace["entry"]["filters"]["trend_spread_strength"]["passed"] is True
  assert envelope.trace["entry"]["filters"]["price_above_slow_ema"]["passed"] is True
  assert envelope.context.features["previous2_rsi"] == 24.0
  assert envelope.context.features["previous_rsi"] == 28.0


def test_rsi_atr_oversold_peak_turn_buys_when_oversold_rsi_recovers():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame((24.0, 26.0, 31.0))
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_range_oversold_recovery": True,
      "entry_recovery_min_close_position": 0.5,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["entry"]["patterns"]["rsi_recovery"]["matched"] is True
  assert envelope.trace["entry"]["reason"] == "entry_conditions_met:rsi_recovery"


def test_rsi_atr_oversold_peak_turn_buys_range_recovery_near_local_low():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame(
    (32.0, 25.0, 31.0),
    closes=(100.0, 99.6, 99.8),
    ema_fast=(99.8, 99.7, 99.6),
    ema_slow=(101.0, 100.9, 100.8),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_range_oversold_recovery": True,
      "entry_recovery_min_close_position": 0.5,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["regime"]["allowed"] is False
  assert envelope.trace["entry"]["range_entry_matched"] is True
  assert envelope.trace["entry"]["patterns"]["range_oversold_recovery"]["matched"] is True
  assert envelope.trace["entry"]["filters"]["range_low_proximity"]["value"] == pytest.approx(1.2)
  assert envelope.trace["entry"]["reason"] == "entry_conditions_met:range_oversold_recovery"


def test_rsi_atr_oversold_peak_turn_rejects_range_recovery_far_from_local_low():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame(
    (32.0, 25.0, 31.0),
    closes=(100.0, 99.0, 103.0),
    ema_fast=(99.8, 99.7, 99.6),
    ema_slow=(101.0, 100.9, 100.8),
    atr=1.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_range_oversold_recovery": True,
      "entry_recovery_min_close_position": 0.5,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["patterns"]["range_oversold_recovery"]["matched"] is False
  assert envelope.trace["entry"]["filters"]["range_low_proximity"]["passed"] is False
  assert "range_low_proximity" in envelope.trace["entry"]["reason"]


def test_rsi_atr_oversold_peak_turn_holds_without_oversold_peak():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame((24.0, 32.0, 28.0))
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_enable_rsi_recovery": False,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["matched"] is False


def test_rsi_atr_oversold_peak_turn_rejects_buy_when_price_is_below_slow_ema():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame(
    (24.0, 28.0, 26.0),
    closes=(100.0, 101.0, 98.0),
    ema_fast=(101.0, 101.25, 101.5),
    ema_slow=(99.0, 99.25, 99.5),
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={
      "rsi_oversold_level": 30,
      "entry_require_price_above_slow_ema": True,
      "use_llm_regime_hint": False,
    },
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["reason"] == "entry_filters_failed:price_above_slow_ema"
  assert envelope.trace["entry"]["filters"]["price_above_slow_ema"]["passed"] is False


def test_rsi_atr_oversold_peak_turn_rejects_buy_when_trend_spread_is_too_weak():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_peak_turn_frame(
    (24.0, 28.0, 26.0),
    closes=(100.0, 101.0, 101.0),
    ema_fast=(100.1, 100.1, 100.1),
    ema_slow=(100.0, 100.0, 100.0),
    atr=2.0,
  )
  state = StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=False,
    cash=10_000.0,
    position_size=0.0,
    parameters={"rsi_oversold_level": 30, "use_llm_regime_hint": False},
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["entry"]["reason"] == "entry_filters_failed:trend_spread_strength"
  assert envelope.trace["entry"]["filters"]["trend_spread_strength"]["value"] == pytest.approx(0.05)


def test_rsi_atr_oversold_peak_turn_sells_immediately_on_hard_stop():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_exit_frame(
    closes=(100.0, 99.0, 94.0),
    ema_fast=(102.0, 101.0, 100.0),
    ema_slow=(100.0, 100.5, 99.0),
    rsi=(60.0, 58.0, 57.0),
  )
  state = _open_rsi_position_state(
    frame,
    position_average_price=100.0,
    stop_loss_price=95.0,
    take_profit_price=110.0,
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.trace["exit"]["reason"] == "hard_stop"
  assert envelope.trace["exit"]["score"] == 1.0


def test_rsi_atr_oversold_peak_turn_holds_on_ema_cross_alone():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_exit_frame(
    closes=(100.0, 101.0, 102.0),
    ema_fast=(102.0, 101.0, 99.9),
    ema_slow=(100.0, 100.0, 100.0),
    rsi=(58.0, 60.0, 62.0),
  )
  state = _open_rsi_position_state(
    frame,
    position_average_price=100.0,
    stop_loss_price=90.0,
    take_profit_price=112.0,
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["exit"]["score"] == pytest.approx(0.50)
  assert envelope.trace["exit"]["components"]["trend_break"]["active"] is True
  assert envelope.trace["exit"]["reason"] == "exit_score_below_threshold"


def test_rsi_atr_oversold_peak_turn_sells_when_exit_score_reaches_threshold():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_exit_frame(
    closes=(100.0, 99.0, 96.0),
    ema_fast=(102.0, 101.0, 98.0),
    ema_slow=(100.0, 100.0, 100.0),
    rsi=(55.0, 50.0, 40.0),
    atr=2.0,
  )
  state = _open_rsi_position_state(
    frame,
    position_average_price=100.0,
    stop_loss_price=90.0,
    take_profit_price=112.0,
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.trace["exit"]["score"] == pytest.approx(0.95)
  assert envelope.trace["exit"]["components"]["rsi_failure"]["active"] is True
  assert envelope.trace["exit"]["components"]["adverse_price"]["active"] is True
  assert "exit_score=0.95/0.75" in envelope.rationale


def test_rsi_atr_oversold_peak_turn_sells_on_trailing_stop_after_profit():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_exit_frame(
    closes=(110.0, 111.0, 108.0),
    ema_fast=(104.0, 104.5, 105.0),
    ema_slow=(100.0, 100.5, 101.0),
    rsi=(58.0, 60.0, 59.0),
    atr=2.0,
  )
  state = _open_rsi_position_state(
    frame,
    position_average_price=100.0,
    stop_loss_price=90.0,
    take_profit_price=112.0,
    high_watermark_price=112.0,
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.SELL
  assert envelope.trace["exit"]["reason"] == "trailing_stop"
  assert envelope.trace["exit"]["score"] == 1.0
  assert envelope.trace["exit"]["trailing_stop_price"] == pytest.approx(108.0)
  assert envelope.trace["exit"]["components"]["trailing_stop"]["active"] is True
  assert "trailing_stop=108.00" in envelope.rationale


def test_rsi_atr_oversold_peak_turn_holds_profitable_position_until_trailing_stop():
  strategy = RsiAtrOversoldPeakTurnStrategy()
  frame = _rsi_exit_frame(
    closes=(100.0, 111.0, 110.0),
    ema_fast=(102.0, 101.0, 98.0),
    ema_slow=(100.0, 100.0, 100.0),
    rsi=(55.0, 50.0, 40.0),
    atr=2.0,
  )
  state = _open_rsi_position_state(
    frame,
    position_average_price=100.0,
    stop_loss_price=90.0,
    take_profit_price=112.0,
    high_watermark_price=112.0,
  )

  envelope = strategy.evaluate(frame, state.parameters, state)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["exit"]["score"] == pytest.approx(0.75)
  assert envelope.trace["exit"]["reason"] == "trailing_active_holding_until_stop"
  assert envelope.trace["exit"]["trailing_stop_price"] == pytest.approx(108.0)
  assert envelope.trace["exit"]["components"]["trend_break"]["active"] is True
  assert envelope.trace["exit"]["components"]["rsi_failure"]["active"] is True


def _rsi_peak_turn_frame(
  rsi_values: tuple[float, float, float],
  *,
  closes: tuple[float, float, float] = (100.0, 101.0, 100.5),
  ema_fast: tuple[float, float, float] | None = None,
  ema_slow: tuple[float, float, float] | None = None,
  atr: float = 2.0,
) -> pd.DataFrame:
  timestamp = datetime(2026, 5, 11, tzinfo=UTC)
  fast_values = ema_fast or tuple(101.0 + index * 0.25 for index in range(3))
  slow_values = ema_slow or tuple(99.0 + index * 0.25 for index in range(3))
  return pd.DataFrame(
    [
      {
        "timestamp": timestamp + timedelta(minutes=5 * index),
        "open": close - 0.5,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0 + index,
        "ema_fast": fast,
        "ema_slow": slow,
        "rsi": rsi,
        "rsi_previous": rsi_values[index - 1] if index >= 1 else 50.0,
        "rsi_previous2": rsi_values[index - 2] if index >= 2 else 50.0,
        "atr": atr,
      }
      for index, (close, fast, slow, rsi) in enumerate(
        zip(closes, fast_values, slow_values, rsi_values, strict=True)
      )
    ]
  )


def _rsi14_escape_frame(
  rsi_values: tuple[float, float, float],
  *,
  closes: tuple[float, float, float],
  ma20: tuple[float, float, float],
  ma60: tuple[float, float, float],
  ma20_slope: float | None = None,
  recent_lower_lows: bool | None = None,
  bar_index: int = 2,
  previous_price_swing_low: float | None = None,
  atr: float,
) -> pd.DataFrame:
  frame = _rsi_peak_turn_frame(
    rsi_values,
    closes=closes,
    atr=atr,
  )
  frame["ma20"] = ma20
  frame["ma60"] = ma60
  frame["bar_index"] = [bar_index - 2, bar_index - 1, bar_index]
  frame["rsi_recent_min"] = frame["rsi"].rolling(window=10, min_periods=1).min()
  frame["rsi_crossed_oversold"] = (
    (frame["rsi"].shift(1) <= 30)
    & (frame["rsi"] > 30)
  )
  frame["rsi_crossed_oversold_recent"] = (
    frame["rsi_crossed_oversold"]
    .rolling(window=3, min_periods=1)
    .max()
    .fillna(False)
    .astype(bool)
  )
  cross_bar_index = frame["bar_index"].where(frame["rsi_crossed_oversold"]).ffill()
  frame["bars_since_rsi_oversold_cross"] = (frame["bar_index"] - cross_bar_index).where(
    frame["bar_index"] - cross_bar_index <= 2
  )
  if previous_price_swing_low is None:
    frame["previous_price_swing_low"] = (
      frame["low"].shift(1).rolling(window=5, min_periods=1).min()
    )
  else:
    frame["previous_price_swing_low"] = previous_price_swing_low
  frame["recent_price_swing_low"] = frame["low"].rolling(window=5, min_periods=1).min()
  slope = ma20_slope if ma20_slope is not None else ma20[-1] - ma20[-2]
  frame["ma20_slope"] = slope
  frame["ma60_slope"] = ma60[-1] - ma60[-2]
  if recent_lower_lows is None:
    frame["recent_lower_lows"] = (
      (frame["low"] < frame["low"].shift(1))
      & (frame["low"].shift(1) < frame["low"].shift(2))
    )
  else:
    frame["recent_lower_lows"] = recent_lower_lows
  return frame


def _rsi_exit_frame(
  *,
  closes: tuple[float, float, float],
  ema_fast: tuple[float, float, float],
  ema_slow: tuple[float, float, float],
  rsi: tuple[float, float, float],
  atr: float = 2.0,
) -> pd.DataFrame:
  timestamp = datetime(2026, 5, 11, tzinfo=UTC)
  return pd.DataFrame(
    [
      {
        "timestamp": timestamp + timedelta(minutes=5 * index),
        "open": close - 0.5,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0 + index,
        "ema_fast": fast,
        "ema_slow": slow,
        "rsi": rsi_value,
        "rsi_previous": rsi[index - 1] if index >= 1 else 50.0,
        "rsi_previous2": rsi[index - 2] if index >= 2 else 50.0,
        "atr": atr,
      }
      for index, (close, fast, slow, rsi_value) in enumerate(
        zip(closes, ema_fast, ema_slow, rsi, strict=True)
      )
    ]
  )


def _open_rsi_position_state(
  frame: pd.DataFrame,
  *,
  position_average_price: float,
  stop_loss_price: float,
  take_profit_price: float,
  high_watermark_price: float | None = None,
  trailing_stop_price: float | None = None,
  parameters: dict[str, object] | None = None,
) -> StrategyExecutionState:
  resolved_parameters = {
    "rsi_exit_level": 45,
    "exit_score_threshold": 0.75,
    "use_llm_regime_hint": False,
  }
  if parameters is not None:
    resolved_parameters.update(parameters)
  return StrategyExecutionState(
    timestamp=frame.iloc[-1]["timestamp"].to_pydatetime(),
    instrument_id="binance:BTC/USDT",
    has_position=True,
    cash=9_000.0,
    position_size=1.0,
    position_average_price=position_average_price,
    position_opened_at=frame.iloc[0]["timestamp"].to_pydatetime(),
    position_stop_loss_price=stop_loss_price,
    position_take_profit_price=take_profit_price,
    position_high_watermark_price=(
      high_watermark_price if high_watermark_price is not None else position_average_price
    ),
    position_trailing_stop_price=trailing_stop_price,
    parameters=resolved_parameters,
  )


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
