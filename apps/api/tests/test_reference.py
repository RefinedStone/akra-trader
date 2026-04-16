from __future__ import annotations

import json
from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.references import load_reference_catalog


def test_reference_adapter_builds_nfi_command() -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)
  prepared = adapter.prepare_backtest(
    config=type(
      "Config",
      (),
      {
        "start_at": None,
        "end_at": None,
        "venue": "binance",
      },
    )(),
    metadata=type(
      "Metadata",
      (),
      {
        "reference_id": "nostalgia-for-infinity",
        "entrypoint": "NostalgiaForInfinityX7",
        "version": "reference",
      },
    )(),
  )

  assert prepared.command[0] == "freqtrade"
  assert "--strategy=NostalgiaForInfinityX7" in prepared.command
  assert prepared.working_directory.endswith("reference/NostalgiaForInfinity")
  assert prepared.reference_id == "nostalgia-for-infinity"
  assert prepared.reference.title == "NostalgiaForInfinity"
  assert prepared.integration_mode == "external_runtime"
  assert any(path.endswith("user_data/backtest_results") for path in prepared.artifact_roots)
  assert any(path.endswith("user_data/logs") for path in prepared.artifact_roots)


def test_reference_adapter_enriches_benchmark_artifacts_from_manifest_and_summary(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)
  result_root = tmp_path / "user_data" / "backtest_results"
  log_root = tmp_path / "user_data" / "logs"
  result_root.mkdir(parents=True)
  log_root.mkdir(parents=True)

  manifest_path = result_root / "backtest-result-20260417_030000.meta.json"
  snapshot_path = result_root / "backtest-result-20260417_030000.json"
  log_path = log_root / "freqtrade.log"

  manifest_path.write_text(
    json.dumps(
      {
        "metadata": {
          "run_id": "freqtrade-backtest-001",
          "exchange": "binance",
          "stake_currency": "USDT",
          "generated_at": "2026-04-17T03:00:00+00:00",
        },
        "strategy": {
          "NostalgiaForInfinityX7": {
            "timeframe": "5m",
            "timerange": "20240101-20240131",
            "backtest_start_time": 1704067200,
            "backtest_end_time": 1706659200,
            "pairlist": ["BTC/USDT", "ETH/USDT"],
          }
        },
      }
    ),
    encoding="utf-8",
  )
  snapshot_path.write_text(
    json.dumps(
      {
        "strategy": {
          "NostalgiaForInfinityX7": {
            "total_trades": 42,
            "profit_total_pct": 18.4,
            "profit_total_abs": 1840.25,
            "max_drawdown_pct": 6.3,
            "market_change_pct": 11.2,
          }
        }
      }
    ),
    encoding="utf-8",
  )
  log_path.write_text("backtest complete\n", encoding="utf-8")

  artifacts = adapter._build_benchmark_artifacts((
    str(result_root),
    str(manifest_path),
    str(snapshot_path),
    str(log_path),
  ))

  artifact_by_kind = {artifact.kind: artifact for artifact in artifacts}

  root_artifact = artifact_by_kind["result_snapshot_root"]
  assert root_artifact.summary["manifest_count"] == 1
  assert root_artifact.summary["snapshot_count"] == 1
  assert root_artifact.summary["strategy_name"] == "NostalgiaForInfinityX7"
  assert root_artifact.summary["trade_count"] == 42
  assert root_artifact.summary["profit_total_pct"] == 18.4
  assert root_artifact.summary["timeframe"] == "5m"
  assert root_artifact.summary_source_path == str(snapshot_path)

  manifest_artifact = artifact_by_kind["result_manifest"]
  assert manifest_artifact.summary["run_id"] == "freqtrade-backtest-001"
  assert manifest_artifact.summary["pair_count"] == 2
  assert manifest_artifact.summary["backtest_start_at"] == "2024-01-01T00:00:00+00:00"
  assert manifest_artifact.summary_source_path == str(manifest_path)

  snapshot_artifact = artifact_by_kind["result_snapshot"]
  assert snapshot_artifact.summary["trade_count"] == 42
  assert snapshot_artifact.summary["max_drawdown_pct"] == 6.3
  assert snapshot_artifact.summary["timeframe"] == "5m"
  assert snapshot_artifact.summary_source_path == str(snapshot_path)

  log_artifact = artifact_by_kind["runtime_log"]
  assert log_artifact.summary == {}
  assert log_artifact.summary_source_path is None


def test_reference_adapter_uses_manifest_summary_for_zip_snapshots(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)
  result_root = tmp_path / "user_data" / "backtest_results"
  result_root.mkdir(parents=True)

  manifest_path = result_root / "backtest-result-20260417_030000.meta.json"
  snapshot_path = result_root / "backtest-result-20260417_030000.zip"
  manifest_path.write_text(
    json.dumps(
      {
        "strategy": {
          "NostalgiaForInfinityX7": {
            "timeframe": "1h",
            "timerange": "20240201-20240229",
            "pairlist": ["BTC/USDT"],
          }
        },
        "metadata": {
          "generated_at": "2026-04-17T03:15:00+00:00",
        },
      }
    ),
    encoding="utf-8",
  )
  snapshot_path.write_text("", encoding="utf-8")

  artifact = adapter._build_benchmark_artifacts((str(snapshot_path),))[0]

  assert artifact.kind == "result_snapshot"
  assert artifact.summary["strategy_name"] == "NostalgiaForInfinityX7"
  assert artifact.summary["timeframe"] == "1h"
  assert artifact.summary["pair_count"] == 1
  assert artifact.summary_source_path == str(manifest_path)
