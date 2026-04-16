from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from akra_trader.config import Settings
from akra_trader.main import create_app


def build_client(database_path: Path) -> TestClient:
  settings = Settings(
    runs_database_url=f"sqlite:///{database_path}",
    market_data_provider="seeded",
  )
  return TestClient(create_app(settings))


def test_list_strategies_returns_builtin_strategy(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/strategies")
  assert response.status_code == 200
  payload = response.json()
  assert payload[0]["strategy_id"] == "ma_cross_v1"


def test_list_references_returns_catalog_entries(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/references")
  assert response.status_code == 200
  payload = response.json()
  assert any(item["reference_id"] == "nautilus-trader" for item in payload)
  assert any(item["reference_id"] == "nostalgia-for-infinity" for item in payload)


def test_backtest_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "completed"
  assert payload["config"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["market_data"]["provider"] == "seeded"
  assert payload["provenance"]["market_data"]["sync_status"] == "fixture"


def test_backtest_run_survives_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"
  client = build_client(database_path)
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert response.status_code == 200
  run_id = response.json()["config"]["run_id"]

  restarted_client = build_client(database_path)
  restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  assert restarted_response.json()["config"]["run_id"] == run_id


def test_sandbox_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 48,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "running"
  assert payload["config"]["mode"] == "sandbox"


def test_paper_alias_still_works(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/paper",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["config"]["mode"] == "sandbox"


def test_market_data_status_endpoint_returns_status_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/market-data/status")

  assert response.status_code == 200
  payload = response.json()
  assert payload["provider"] == "seeded"
  assert payload["instruments"]
  assert "sync_status" in payload["instruments"][0]
