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
  assert payload[0]["lifecycle"]["stage"] == "active"
  assert payload[0]["version_lineage"] == ["1.0.0"]
  assert payload[0]["supported_timeframes"] == ["5m", "1h"]


def test_list_strategies_can_filter_by_lane_and_lifecycle_stage(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/strategies?lane=freqtrade_reference&lifecycle_stage=imported")

  assert response.status_code == 200
  payload = response.json()
  assert payload
  assert all(item["runtime"] == "freqtrade_reference" for item in payload)
  assert all(item["lifecycle"]["stage"] == "imported" for item in payload)


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
  assert payload["provenance"]["strategy"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["strategy"]["lifecycle"]["stage"] == "active"
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["requested"] == {}
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 8,
    "long_window": 21,
  }
  assert payload["provenance"]["strategy"]["warmup"]["required_bars"] == 21
  assert payload["provenance"]["strategy"]["warmup"]["timeframes"] == ["5m"]
  assert payload["provenance"]["market_data"]["provider"] == "seeded"
  assert payload["provenance"]["market_data"]["sync_status"] == "fixture"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["provider"] == "seeded"


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
  assert payload["instruments"][0]["backfill_target_candles"] is None
  assert payload["instruments"][0]["backfill_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_contiguous_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_missing_candles"] is None
  assert payload["instruments"][0]["backfill_gap_windows"] == []


def test_runs_endpoint_can_filter_by_strategy_version(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  native_response = client.post(
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
  assert native_response.status_code == 200

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert reference_response.status_code == 200

  filtered = client.get("/api/runs?mode=backtest&strategy_id=ma_cross_v1&strategy_version=1.0.0")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 1
  assert payload[0]["config"]["strategy_id"] == "ma_cross_v1"
  assert payload[0]["config"]["strategy_version"] == "1.0.0"


def test_compare_runs_endpoint_returns_native_and_reference_benchmark_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  native_response = client.post(
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
  assert native_response.status_code == 200
  native_run_id = native_response.json()["config"]["run_id"]

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert reference_response.status_code == 200
  reference_run_id = reference_response.json()["config"]["run_id"]

  comparison_response = client.get(
    f"/api/runs/compare?run_id={native_run_id}&run_id={reference_run_id}"
  )

  assert comparison_response.status_code == 200
  payload = comparison_response.json()
  assert payload["baseline_run_id"] == native_run_id
  assert [run["lane"] for run in payload["runs"]] == ["native", "reference"]
  assert payload["runs"][1]["reference_id"] == "nostalgia-for-infinity"
  assert payload["runs"][1]["integration_mode"] == "external_runtime"
  assert payload["runs"][1]["reference"]["title"] == "NostalgiaForInfinity"
  assert payload["runs"][1]["artifact_paths"]
  assert len(payload["narratives"]) == 1
  assert payload["narratives"][0]["comparison_type"] == "native_vs_reference"
  assert payload["narratives"][0]["run_id"] == reference_run_id
  assert payload["narratives"][0]["rank"] == 1
  assert payload["narratives"][0]["is_primary"] is True
  assert payload["narratives"][0]["insight_score"] > 0
  artifact_kinds = {artifact["kind"] for artifact in payload["runs"][1]["benchmark_artifacts"]}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all("summary" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("sections" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("summary_source_path" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  metric_rows = {row["key"]: row for row in payload["metric_rows"]}
  assert metric_rows["total_return_pct"]["values"][native_run_id] is not None
  assert reference_run_id in metric_rows["trade_count"]["values"]
  assert payload["runs"][1]["notes"]
