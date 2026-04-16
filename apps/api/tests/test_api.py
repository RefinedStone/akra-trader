from __future__ import annotations

from datetime import UTC
from datetime import datetime
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
  assert payload["provenance"]["market_data"]["dataset_identity"].startswith("dataset-v1:")
  assert payload["provenance"]["market_data"]["sync_checkpoint_id"] is None
  assert payload["provenance"]["market_data"]["reproducibility_state"] == "pinned"
  assert payload["provenance"]["market_data"]["sync_status"] == "fixture"
  assert payload["provenance"]["rerun_boundary_id"].startswith("rerun-v1:")
  assert payload["provenance"]["rerun_boundary_state"] == "pinned"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["provider"] == "seeded"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["dataset_identity"].startswith(
    "candles-v1:"
  )


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
  assert payload["notes"][0].startswith("Sandbox worker session primed from the latest market snapshot using ")
  assert payload["provenance"]["runtime_session"]["worker_kind"] == "sandbox_native_worker"
  assert payload["provenance"]["runtime_session"]["lifecycle_state"] == "active"
  assert payload["provenance"]["runtime_session"]["primed_candle_count"] == 48
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert payload["provenance"]["runtime_session"]["recovery_count"] == 0
  assert (
    payload["provenance"]["runtime_session"]["last_processed_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )
  assert (
    payload["provenance"]["runtime_session"]["last_seen_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )


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
  assert payload["config"]["mode"] == "paper"
  assert payload["notes"][0].startswith("Paper session primed from the latest market snapshot using ")
  assert all("Sandbox preview replayed" not in note for note in payload["notes"])
  assert payload["provenance"]["runtime_session"] is None


def test_sandbox_worker_recovers_running_session_after_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as first_client:
    response = first_client.post(
      "/api/runs/sandbox",
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
    run_id = response.json()["config"]["run_id"]

  with build_client(database_path) as restarted_client:
    restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  payload = restarted_response.json()
  assert payload["config"]["mode"] == "sandbox"
  assert payload["provenance"]["runtime_session"]["recovery_count"] >= 1
  assert payload["provenance"]["runtime_session"]["last_recovery_reason"] == "process_restart"
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert any("sandbox_worker_recovered | process_restart" in note for note in payload["notes"])


def test_market_data_status_endpoint_returns_status_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/market-data/status")

  assert response.status_code == 200
  payload = response.json()
  assert payload["provider"] == "seeded"
  assert payload["instruments"]
  assert "sync_status" in payload["instruments"][0]
  assert payload["instruments"][0]["sync_checkpoint"] is None
  assert payload["instruments"][0]["recent_failures"] == []
  assert payload["instruments"][0]["failure_count_24h"] == 0
  assert payload["instruments"][0]["backfill_target_candles"] is None
  assert payload["instruments"][0]["backfill_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_contiguous_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_missing_candles"] is None
  assert payload["instruments"][0]["backfill_gap_windows"] == []


def test_operator_visibility_endpoint_reports_stale_runtime_alerts(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    clock = lambda: datetime(2025, 1, 3, 13, 0, tzinfo=UTC)
    app._clock = clock
    app._sandbox_worker_heartbeat_timeout_seconds = 15
    app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )
    app._clock = lambda: datetime(2025, 1, 3, 13, 0, 20, tzinfo=UTC)

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "stale_runtime"
  assert payload["alerts"][0]["severity"] == "warning"
  assert payload["audit_events"][0]["kind"] == "sandbox_worker_stale"


def test_operator_visibility_endpoint_reports_worker_failures(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )

    def fail_worker(*, run):
      raise RuntimeError("worker crash")

    app._load_sandbox_worker_candles = fail_worker
    app.maintain_sandbox_worker_sessions()

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "worker_failure"
  assert payload["alerts"][0]["severity"] == "critical"
  assert any(event["kind"] == "sandbox_worker_failed" for event in payload["audit_events"])


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


def test_runs_endpoint_can_filter_by_rerun_boundary_id(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  first_response = client.post(
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
  assert first_response.status_code == 200
  rerun_boundary_id = first_response.json()["provenance"]["rerun_boundary_id"]

  second_response = client.post(
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
  assert second_response.status_code == 200

  other_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 12000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert other_response.status_code == 200

  filtered = client.get(f"/api/runs?rerun_boundary_id={rerun_boundary_id}")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 2
  assert all(item["provenance"]["rerun_boundary_id"] == rerun_boundary_id for item in payload)


def test_runs_endpoint_filters_paper_history_separately_from_sandbox(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  sandbox_response = client.post(
    "/api/runs/sandbox",
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
  assert sandbox_response.status_code == 200

  paper_response = client.post(
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
  assert paper_response.status_code == 200

  sandbox_filtered = client.get("/api/runs?mode=sandbox")
  paper_filtered = client.get("/api/runs?mode=paper")

  assert sandbox_filtered.status_code == 200
  assert paper_filtered.status_code == 200
  assert [item["config"]["mode"] for item in sandbox_filtered.json()] == ["sandbox"]
  assert [item["config"]["mode"] for item in paper_filtered.json()] == ["paper"]


def test_rerun_boundary_endpoint_creates_backtest_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/backtests")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]
  assert rerun_payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 13,
    "long_window": 21,
  }


def test_rerun_boundary_endpoint_creates_sandbox_run_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/sandbox",
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
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["config"]["mode"] == "sandbox"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_paper_endpoint_replays_boundary_with_expected_mode_drift(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/paper")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["mode"] == "paper"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "drifted"
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_endpoint_returns_not_found_for_unknown_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/backtests")

  assert response.status_code == 404

  sandbox_response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/sandbox")

  assert sandbox_response.status_code == 404


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
    f"/api/runs/compare?run_id={native_run_id}&run_id={reference_run_id}&intent=strategy_tuning"
  )

  assert comparison_response.status_code == 200
  payload = comparison_response.json()
  assert payload["intent"] == "strategy_tuning"
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
  assert payload["narratives"][0]["title"].startswith("Strategy tuning")
  artifact_kinds = {artifact["kind"] for artifact in payload["runs"][1]["benchmark_artifacts"]}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all("summary" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("sections" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("summary_source_path" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  metric_rows = {row["key"]: row for row in payload["metric_rows"]}
  assert metric_rows["total_return_pct"]["annotation"] == (
    "Tuning read: return deltas show optimization edge versus the baseline."
  )
  assert metric_rows["total_return_pct"]["delta_annotations"][native_run_id] == "tuning baseline"
  assert metric_rows["total_return_pct"]["values"][native_run_id] is not None
  assert reference_run_id in metric_rows["trade_count"]["values"]
  assert payload["runs"][1]["notes"]
