from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

import joblib
import pandas as pd

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.domain.models import extract_benchmark_artifact_runtime_candidate_id
from akra_trader.domain.models import is_benchmark_artifact_metadata_key


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
        "symbols": ("BTC/USDT",),
        "timeframe": "5m",
        "initial_cash": 10000.0,
        "fee_rate": 0.001,
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
  assert "--pairs" in prepared.command
  assert "BTC/USDT" in prepared.command
  assert "--timeframe=5m" in prepared.command
  assert "--dry-run-wallet=10000.0" in prepared.command
  assert "--fee=0.001" in prepared.command
  assert prepared.working_directory.endswith("reference/NostalgiaForInfinity")
  assert prepared.reference_id == "nostalgia-for-infinity"
  assert prepared.reference.title == "NostalgiaForInfinity"
  assert prepared.integration_mode == "external_runtime"
  assert any(path.endswith("user_data/backtest_results") for path in prepared.artifact_roots)
  assert any(path.endswith("user_data/logs") for path in prepared.artifact_roots)


def test_reference_adapter_uses_metadata_version_when_git_is_missing(monkeypatch) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)

  def raise_missing_git(*args, **kwargs):
    raise FileNotFoundError("git")

  monkeypatch.setattr(
    "akra_trader.adapters.freqtrade_zip_summaries.subprocess.run",
    raise_missing_git,
  )

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
        "entrypoint": "NostalgiaForInfinityNext",
        "version": "reference",
      },
    )(),
  )

  assert prepared.reference_version == "reference"


def test_benchmark_artifact_runtime_candidate_id_helpers_accept_multiple_source_keys() -> None:
  assert extract_benchmark_artifact_runtime_candidate_id(
    {"runtime_candidate_id": "freqtrade:pair-metric:BTC/USDT"}
  ) == "freqtrade:pair-metric:BTC/USDT"
  assert extract_benchmark_artifact_runtime_candidate_id(
    {"native_candidate_id": "nautilus:order-book-gap:BTC/USDT"}
  ) == "nautilus:order-book-gap:BTC/USDT"
  assert is_benchmark_artifact_metadata_key("__runtime_candidate_id") is True
  assert is_benchmark_artifact_metadata_key("native_runtime_candidate_id") is True
  assert is_benchmark_artifact_metadata_key("label") is False


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
          "NostalgiaForInfinityX7": {
            "run_id": "freqtrade-backtest-001",
            "timeframe": "5m",
            "timeframe_detail": "1m",
            "backtest_start_ts": 1704067200,
            "backtest_end_ts": 1706659200,
            "backtest_start_time": 1713322800,
            "notes": "fixture manifest",
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
            "pairlist": ["BTC/USDT", "ETH/USDT"],
            "results_per_pair": [
              {
                "key": "BTC/USDT",
                "native_candidate_id": "freqtrade:pair-metric:BTC/USDT",
                "trades": 20,
                "profit_total_pct": 12.3,
                "profit_total_abs": 1234.5,
                "winrate": 0.7,
              },
              {
                "key": "ETH/USDT",
                "trades": 22,
                "profit_total_pct": 6.1,
                "profit_total_abs": 605.75,
                "winrate": 0.59,
              },
              {
                "key": "TOTAL",
                "trades": 42,
                "profit_total_pct": 18.4,
                "profit_total_abs": 1840.25,
                "winrate": 0.65,
              },
            ],
            "results_per_enter_tag": [
              {
                "key": "dip_buy",
                "trades": 30,
                "profit_total_pct": 11.5,
                "profit_total_abs": 1150.0,
                "winrate": 0.66,
              },
              {
                "key": "breakout",
                "trades": 12,
                "profit_total_pct": 6.9,
                "profit_total_abs": 690.25,
                "winrate": 0.58,
              },
            ],
            "exit_reason_summary": [
              {
                "key": "roi",
                "trades": 28,
                "profit_total_pct": 14.1,
                "profit_total_abs": 1410.0,
                "winrate": 0.78,
              },
              {
                "key": "stop_loss",
                "trades": 10,
                "profit_total_pct": -1.9,
                "profit_total_abs": -190.0,
                "winrate": 0.1,
              },
            ],
            "left_open_trades": [
              {
                "key": "BTC/USDT",
                "trades": 1,
                "profit_total_pct": 0.2,
                "profit_total_abs": 20.0,
                "winrate": 1.0,
              },
            ],
            "periodic_breakdown": {
              "day": [
                {"date": "01/04/2026", "profit_abs": 100.0, "trades": 4},
                {"date": "02/04/2026", "profit_abs": -25.0, "trades": 2},
              ],
              "week": [
                {"date": "31/03/2026", "profit_abs": 350.0, "trades": 12},
              ],
            },
            "daily_profit": [
              ["2026-04-01", 100.0],
              ["2026-04-02", -25.0],
            ],
            "wallet_stats": {
              "start_balance": 10000,
              "end_balance": 11840.25,
              "high_balance": 11920.0,
              "low_balance": 9840.0,
              "sharpe": 1.8,
              "sortino": 2.1,
              "calmar": 1.6,
              "max_drawdown_account": 0.063,
              "max_drawdown_abs": 620.0,
              "drawdown_start": "2026-04-02 00:00:00",
              "drawdown_end": "2026-04-03 06:00:00",
            },
            "best_pair": {
              "key": "BTC/USDT",
              "trades": 20,
              "profit_total_pct": 12.3,
              "profit_total_abs": 1234.5,
            },
            "worst_pair": {
              "key": "ETH/USDT",
              "trades": 22,
              "profit_total_pct": 6.1,
              "profit_total_abs": 605.75,
            },
            "total_trades": 42,
            "profit_total": 0.184,
            "profit_total_abs": 1840.25,
            "max_drawdown_account": 0.063,
            "market_change": 0.112,
            "stake_currency": "USDT",
            "exchange": "binance",
            "timeframe": "5m",
            "timerange": "20240101-20240131",
            "backtest_start_ts": 1704067200,
            "backtest_end_ts": 1706659200,
          }
        },
        "strategy_comparison": [
          {
            "key": "NostalgiaForInfinityX7",
            "trades": 42,
            "profit_total_pct": 18.4,
            "profit_total_abs": 1840.25,
            "max_drawdown_account": 0.063,
            "winrate": 0.65,
          },
          {
            "key": "AltReference",
            "trades": 39,
            "profit_total_pct": 11.9,
            "profit_total_abs": 1195.0,
            "max_drawdown_account": 0.071,
            "winrate": 0.61,
          },
        ],
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
  assert root_artifact.summary["max_drawdown_pct"] == 6.3
  assert root_artifact.summary["market_change_pct"] == 11.2
  assert root_artifact.summary["timeframe"] == "5m"
  assert root_artifact.summary_source_path == str(snapshot_path)
  assert root_artifact.source_locations["summary"]["trade_count"]["source_path"] == str(snapshot_path)
  assert "42" in root_artifact.source_locations["summary"]["trade_count"]["searchable_texts"]
  assert root_artifact.source_locations["sections"]["pair_metrics"][0]["line_key"] == "count"
  assert root_artifact.source_locations["sections"]["pair_metrics"][0]["line_index"] == 0
  best_pair_bindings = [
    binding
    for binding in root_artifact.source_locations["sections"]["pair_metrics"][2]["candidate_bindings"]
    if binding["symbol_key"] == "BTC/USDT"
  ]
  assert any(binding["binding_kind"] == "market_data_issue" for binding in best_pair_bindings)
  assert any(
    binding["candidate_id"] == "[\"market_data_issue\",\"BTC/USDT\",\"BTC/USDT\"]"
    for binding in best_pair_bindings
  )
  assert any(
    binding["runtime_candidate_id"] == "freqtrade:pair-metric:BTC/USDT"
    for binding in best_pair_bindings
  )
  assert all(
    binding["candidate_path_template"] == "provenance.market_data_by_symbol.{symbol_key}.issues"
    for binding in best_pair_bindings
  )
  assert root_artifact.sections["strategy_comparison"]["count"] == 2
  assert root_artifact.sections["pair_metrics"]["best"]["label"] == "BTC/USDT"
  assert root_artifact.sections["exit_reason_metrics"]["preview"][0]["label"] == "roi"
  assert root_artifact.sections["daily_profit"]["best"]["date"] == "2026-04-01"
  assert root_artifact.sections["wallet_stats"]["sharpe"] == 1.8

  manifest_artifact = artifact_by_kind["result_manifest"]
  assert manifest_artifact.summary["run_id"] == "freqtrade-backtest-001"
  assert manifest_artifact.summary["strategy_name"] == "NostalgiaForInfinityX7"
  assert manifest_artifact.summary["backtest_start_at"] == "2024-01-01T00:00:00+00:00"
  assert manifest_artifact.summary_source_path == str(manifest_path)
  assert manifest_artifact.source_locations["summary"]["run_id"]["source_path"] == str(manifest_path)
  assert "freqtrade-backtest-001" in manifest_artifact.source_locations["summary"]["run_id"]["searchable_texts"]
  assert manifest_artifact.source_locations["sections"]["metadata"][0]["line_key"] == "run_id"
  assert manifest_artifact.source_locations["sections"]["metadata"][0]["line_index"] == 0
  assert manifest_artifact.sections["metadata"]["timeframe_detail"] == "1m"
  assert manifest_artifact.sections["metadata"]["notes"] == "fixture manifest"

  snapshot_artifact = artifact_by_kind["result_snapshot"]
  assert snapshot_artifact.summary["trade_count"] == 42
  assert snapshot_artifact.summary["max_drawdown_pct"] == 6.3
  assert snapshot_artifact.summary["market_change_pct"] == 11.2
  assert snapshot_artifact.summary["timeframe"] == "5m"
  assert snapshot_artifact.summary_source_path == str(snapshot_path)
  assert snapshot_artifact.source_locations["summary"]["trade_count"]["source_path"] == str(snapshot_path)
  assert "42" in snapshot_artifact.source_locations["summary"]["trade_count"]["searchable_texts"]
  assert snapshot_artifact.source_locations["sections"]["pair_metrics"][0]["line_key"] == "count"
  assert snapshot_artifact.source_locations["sections"]["pair_metrics"][0]["line_index"] == 0
  snapshot_best_pair_bindings = [
    binding
    for binding in snapshot_artifact.source_locations["sections"]["pair_metrics"][2]["candidate_bindings"]
    if binding["symbol_key"] == "BTC/USDT"
  ]
  assert any(binding["binding_kind"] == "market_data_issue" for binding in snapshot_best_pair_bindings)
  assert any(
    binding["candidate_id"] == "[\"market_data_issue\",\"BTC/USDT\",\"BTC/USDT\"]"
    for binding in snapshot_best_pair_bindings
  )
  assert any(
    binding["runtime_candidate_id"] == "freqtrade:pair-metric:BTC/USDT"
    for binding in snapshot_best_pair_bindings
  )
  assert all(
    binding["candidate_path_template"] == "provenance.market_data_by_symbol.{symbol_key}.issues"
    for binding in snapshot_best_pair_bindings
  )
  assert snapshot_artifact.sections["pair_metrics"]["total"]["trade_count"] == 42
  assert snapshot_artifact.sections["enter_tag_metrics"]["preview"][0]["label"] == "dip_buy"
  assert snapshot_artifact.sections["periodic_breakdown"]["day"]["worst"]["profit_total_abs"] == -25.0
  assert snapshot_artifact.sections["pair_extremes"]["best"]["label"] == "BTC/USDT"

  log_artifact = artifact_by_kind["runtime_log"]
  assert log_artifact.summary == {}
  assert log_artifact.sections == {}
  assert log_artifact.summary_source_path is None
  assert log_artifact.source_locations == {}


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
        "metadata": {
          "NostalgiaForInfinityX7": {
            "timeframe": "1h",
            "backtest_start_ts": 1706745600,
            "backtest_end_ts": 1709164800,
          }
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
  assert artifact.summary["backtest_start_at"] == "2024-02-01T00:00:00+00:00"
  assert artifact.sections["metadata"]["timeframe"] == "1h"
  assert artifact.summary_source_path == str(manifest_path)


def test_reference_adapter_inspects_zip_artifacts_for_provenance(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)
  result_root = tmp_path / "user_data" / "backtest_results"
  result_root.mkdir(parents=True)

  market_change_buffer = BytesIO()
  pd.DataFrame(
    {
      "date": pd.to_datetime(["2026-04-01T00:00:00Z", "2026-04-02T00:00:00Z"], utc=True),
      "BTC/USDT": [1.02, 1.05],
      "ETH/USDT": [0.98, 1.01],
    }
  ).to_feather(market_change_buffer)
  market_change_buffer.seek(0)

  wallet_buffer = BytesIO()
  pd.DataFrame(
    {
      "date": pd.to_datetime(["2026-04-01T00:00:00Z", "2026-04-02T12:00:00Z"], utc=True),
      "currency": ["USDT", "BTC"],
      "rate": [1.0, 68000.0],
      "balance": [10500.0, 0.25],
    }
  ).to_feather(wallet_buffer)
  wallet_buffer.seek(0)

  signals_buffer = BytesIO()
  joblib.dump(
    {
      "NostalgiaForInfinityX7": {
        "BTC/USDT": pd.DataFrame(
          {
            "date": pd.to_datetime(
              ["2026-04-01T00:00:00Z", "2026-04-01T01:00:00Z"],
              utc=True,
            ),
            "enter_tag": ["dip_buy", "breakout"],
          }
        ),
        "ETH/USDT": pd.DataFrame(
          {
            "date": pd.to_datetime(["2026-04-01T02:00:00Z"], utc=True),
            "enter_tag": ["dip_buy"],
          }
        ),
      }
    },
    signals_buffer,
  )
  signals_buffer.seek(0)

  rejected_buffer = BytesIO()
  joblib.dump(
    {
      "NostalgiaForInfinityX7": {
        "BTC/USDT": pd.DataFrame(
          {
            "date": pd.to_datetime(["2026-04-01T03:00:00Z"], utc=True),
            "reason": ["volume_limit"],
          }
        ),
      }
    },
    rejected_buffer,
  )
  rejected_buffer.seek(0)

  exited_buffer = BytesIO()
  joblib.dump(
    {
      "NostalgiaForInfinityX7": {
        "BTC/USDT": pd.DataFrame(
          {
            "date": pd.to_datetime(["2026-04-01T04:00:00Z"], utc=True),
            "exit_reason": ["roi"],
          }
        ),
      }
    },
    exited_buffer,
  )
  exited_buffer.seek(0)

  snapshot_path = result_root / "backtest-result-20260417_030000.zip"
  with ZipFile(snapshot_path, "w") as archive:
    archive.writestr(
      "backtest-result-20260417_030000.json",
      json.dumps(
        {
          "strategy": {
            "NostalgiaForInfinityX7": {
              "results_per_pair": [
                {
                  "key": "BTC/USDT",
                  "trades": 18,
                  "profit_total_pct": 9.5,
                  "profit_total_abs": 950.0,
                  "winrate": 0.72,
                },
                {
                  "key": "TOTAL",
                  "trades": 18,
                  "profit_total_pct": 9.5,
                  "profit_total_abs": 950.0,
                  "winrate": 0.72,
                },
              ],
              "exit_reason_summary": [
                {
                  "key": "roi",
                  "trades": 15,
                  "profit_total_pct": 10.7,
                  "profit_total_abs": 1070.0,
                  "winrate": 0.86,
                },
              ],
              "wallet_stats": {
                "start_balance": 10000,
                "end_balance": 10950,
                "sharpe": 1.2,
                "max_drawdown_account": 0.041,
              },
              "total_trades": 18,
              "profit_total": 0.095,
              "profit_total_abs": 950.0,
              "max_drawdown_account": 0.041,
              "market_change": 0.057,
              "exchange": "binance",
              "stake_currency": "USDT",
              "timeframe": "15m",
              "timerange": "20240301-20240331",
            }
          },
          "strategy_comparison": [
            {
              "key": "NostalgiaForInfinityX7",
              "trades": 18,
              "profit_total_pct": 9.5,
              "profit_total_abs": 950.0,
              "max_drawdown_account": 0.041,
              "winrate": 0.72,
            }
          ],
        }
      ),
    )
    archive.writestr(
      "backtest-result-20260417_030000_config.json",
      json.dumps(
        {
          "strategy": "NostalgiaForInfinityX7",
          "exchange": {"name": "binance"},
          "stake_currency": "USDT",
          "timeframe": "15m",
          "timerange": "20240301-20240331",
          "trading_mode": "spot",
          "margin_mode": "isolated",
          "max_open_trades": 3,
          "export": "signals",
        }
      ),
    )
    archive.writestr(
      "backtest-result-20260417_030000_NostalgiaForInfinityX7.json",
      json.dumps(
        {
          "strategy_name": "NostalgiaForInfinityX7",
          "params": {
            "buy_threshold": 0.32,
            "sell_threshold": 0.14,
          },
        }
      ),
    )
    archive.writestr("backtest-result-20260417_030000_NostalgiaForInfinityX7.py", "# strategy")
    archive.writestr(
      "backtest-result-20260417_030000_market_change.feather",
      market_change_buffer.getvalue(),
    )
    archive.writestr(
      "backtest-result-20260417_030000_NostalgiaForInfinityX7_wallet.feather",
      wallet_buffer.getvalue(),
    )
    archive.writestr("backtest-result-20260417_030000_signals.pkl", signals_buffer.getvalue())
    archive.writestr("backtest-result-20260417_030000_rejected.pkl", rejected_buffer.getvalue())
    archive.writestr("backtest-result-20260417_030000_exited.pkl", exited_buffer.getvalue())

  artifacts = adapter._build_benchmark_artifacts((
    str(result_root),
    str(snapshot_path),
  ))
  artifact_by_kind = {artifact.kind: artifact for artifact in artifacts}

  snapshot_artifact = artifact_by_kind["result_snapshot"]
  assert snapshot_artifact.summary["strategy_name"] == "NostalgiaForInfinityX7"
  assert snapshot_artifact.summary["trade_count"] == 18
  assert snapshot_artifact.summary["profit_total_pct"] == 9.5
  assert snapshot_artifact.summary["max_drawdown_pct"] == 4.1
  assert snapshot_artifact.summary["market_change_pct"] == 5.7
  assert snapshot_artifact.summary["timeframe"] == "15m"
  assert snapshot_artifact.summary["exchange"] == "binance"
  assert snapshot_artifact.summary_source_path == str(snapshot_path)
  assert snapshot_artifact.sections["zip_contents"]["member_count"] == 9
  assert snapshot_artifact.sections["zip_contents"]["signal_export_count"] == 1
  assert snapshot_artifact.sections["zip_contents"]["wallet_export_count"] == 1
  assert snapshot_artifact.sections["zip_contents"]["strategy_source_count"] == 1
  assert snapshot_artifact.sections["zip_contents"]["strategy_param_count"] == 1
  assert snapshot_artifact.sections["zip_config"]["trading_mode"] == "spot"
  assert snapshot_artifact.sections["zip_config"]["margin_mode"] == "isolated"
  assert snapshot_artifact.sections["zip_strategy_bundle"]["strategy_names"] == ["NostalgiaForInfinityX7"]
  assert snapshot_artifact.sections["zip_strategy_bundle"]["parameter_keys"][
    "backtest-result-20260417_030000_NostalgiaForInfinityX7.json"
  ] == ["buy_threshold", "sell_threshold"]
  assert snapshot_artifact.sections["zip_market_change"]["row_count"] == 2
  assert snapshot_artifact.sections["zip_market_change"]["pair_count"] == 2
  assert snapshot_artifact.sections["zip_market_change"]["date_start"] == "2026-04-01T00:00:00+00:00"
  assert snapshot_artifact.sections["zip_market_change"]["best_pair"] == "BTC/USDT"
  assert snapshot_artifact.sections["zip_market_change"]["best_pair_change_pct"] == 3.0
  assert snapshot_artifact.sections["zip_market_change"]["worst_pair"] == "ETH/USDT"
  assert snapshot_artifact.sections["zip_market_change"]["pair_change_preview"][0]["pair"] == "BTC/USDT"
  assert snapshot_artifact.sections["zip_wallet_exports"]["export_count"] == 1
  assert snapshot_artifact.sections["zip_wallet_exports"]["strategy_count"] == 1
  assert snapshot_artifact.sections["zip_wallet_exports"]["currency_count"] == 2
  assert snapshot_artifact.sections["zip_wallet_exports"]["total_quote_start"] == 10500.0
  assert snapshot_artifact.sections["zip_wallet_exports"]["total_quote_end"] == 17000.0
  assert snapshot_artifact.sections["zip_wallet_exports"]["currency_quote_preview"][0]["currency"] == "BTC"
  assert snapshot_artifact.sections["zip_wallet_exports"]["currency_quote_preview"][0]["latest_quote_value"] == 17000.0
  assert snapshot_artifact.sections["zip_signal_exports"]["strategy_count"] == 1
  assert snapshot_artifact.sections["zip_signal_exports"]["pair_count"] == 2
  assert snapshot_artifact.sections["zip_signal_exports"]["row_count"] == 3
  assert snapshot_artifact.sections["zip_signal_exports"]["enter_tag_counts"][0] == {
    "label": "dip_buy",
    "count": 2,
  }
  assert snapshot_artifact.sections["zip_signal_exports"]["pair_row_preview"][0] == {
    "pair": "BTC/USDT",
    "count": 2,
  }
  assert snapshot_artifact.sections["zip_rejected_exports"]["row_count"] == 1
  assert snapshot_artifact.sections["zip_rejected_exports"]["reason_counts"][0] == {
    "label": "volume_limit",
    "count": 1,
  }
  assert snapshot_artifact.sections["zip_exited_exports"]["row_count"] == 1
  assert snapshot_artifact.sections["zip_exited_exports"]["exit_reason_counts"][0] == {
    "label": "roi",
    "count": 1,
  }
  assert snapshot_artifact.sections["benchmark_story"]["headline"] == (
    "NostalgiaForInfinityX7 returned 9.5% across 18 trades with 4.1% max drawdown "
    "against a 5.7% market move."
  )
  assert snapshot_artifact.sections["benchmark_story"]["market_context"] == (
    "Breadth stayed positive across 2 tracked pairs; BTC/USDT led at +3% while "
    "ETH/USDT lagged at +3%."
  )
  assert snapshot_artifact.sections["benchmark_story"]["portfolio_context"] == (
    "Wallet quote value rose from 10500 to 17000, ranging between 10500 and 17000; "
    "BTC finished as the largest tracked balance at 17000."
  )
  assert snapshot_artifact.sections["benchmark_story"]["signal_context"] == (
    "Signal exports captured 3 rows across 2 pairs; dip_buy was the dominant entry tag "
    "(2) and BTC/USDT generated the most rows (2)."
  )
  assert snapshot_artifact.sections["benchmark_story"]["rejection_context"] == (
    "Rejected entries were limited to 1 row, entirely driven by volume_limit."
  )
  assert snapshot_artifact.sections["benchmark_story"]["exit_context"] == (
    "Exit exports were dominated by roi (1 row), matching the benchmark summary where "
    "roi closed 15 trades for 10.7%."
  )
  assert snapshot_artifact.sections["benchmark_story"]["pair_context"] == (
    "Pair metrics stayed concentrated in BTC/USDT; the aggregate row logged 18 trades "
    "and 9.5% total return."
  )
  assert snapshot_artifact.sections["pair_metrics"]["total"]["trade_count"] == 18
  assert snapshot_artifact.sections["wallet_stats"]["sharpe"] == 1.2

  root_artifact = artifact_by_kind["result_snapshot_root"]
  assert root_artifact.summary["strategy_name"] == "NostalgiaForInfinityX7"
  assert root_artifact.summary["snapshot_count"] == 1
  assert root_artifact.summary_source_path == str(snapshot_path)
  assert root_artifact.sections["zip_contents"]["result_json_entry"] == "backtest-result-20260417_030000.json"
  assert root_artifact.sections["benchmark_story"]["headline"] == (
    "NostalgiaForInfinityX7 returned 9.5% across 18 trades with 4.1% max drawdown "
    "against a 5.7% market move."
  )
