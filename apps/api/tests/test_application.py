from __future__ import annotations

from datetime import UTC
from datetime import datetime
from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.application import TradingApplication
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunStatus


def build_references():
  repo_root = Path(__file__).resolve().parents[3]
  return load_reference_catalog(repo_root / "reference" / "catalog.toml")


def build_runs_repository(tmp_path: Path) -> SqlAlchemyRunRepository:
  return SqlAlchemyRunRepository(f"sqlite:///{tmp_path / 'runs.sqlite3'}")


def test_backtest_creates_completed_run_with_metrics(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  assert run.status == RunStatus.COMPLETED
  assert run.metrics["initial_cash"] == 10_000
  assert "total_return_pct" in run.metrics
  assert run.config.strategy_id == "ma_cross_v1"
  assert run.provenance.strategy is not None
  assert run.provenance.strategy.strategy_id == "ma_cross_v1"
  assert run.provenance.strategy.lifecycle.stage == "active"
  assert run.provenance.strategy.parameter_snapshot.requested == {}
  assert run.provenance.strategy.parameter_snapshot.resolved == {
    "short_window": 8,
    "long_window": 21,
  }
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.provider == "seeded"
  assert run.provenance.market_data.candle_count > 0
  assert run.provenance.market_data.sync_status == "fixture"

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.COMPLETED
  assert reloaded.metrics == run.metrics
  assert reloaded.provenance.strategy == run.provenance.strategy
  assert reloaded.provenance.market_data == run.provenance.market_data


def test_sandbox_run_is_created_as_running(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=48,
  )

  assert run.status == RunStatus.RUNNING
  assert run.config.mode.value == "sandbox"
  assert run.notes
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.candle_count == 48

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.RUNNING
  assert reloaded.notes == run.notes


def test_stop_sandbox_run_persists_terminal_state(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )

  run = app.start_sandbox_run(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    replay_bars=24,
  )

  stopped = app.stop_sandbox_run(run.config.run_id)

  assert stopped is not None
  assert stopped.status == RunStatus.STOPPED
  assert stopped.ended_at is not None
  assert stopped.notes[-1] == "Sandbox run stopped by operator."

  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)
  assert reloaded is not None
  assert reloaded.status == RunStatus.STOPPED
  assert reloaded.ended_at is not None
  assert reloaded.notes[-1] == "Sandbox run stopped by operator."


def test_reference_backtest_records_external_provenance(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  assert run.provenance.strategy is not None
  assert run.provenance.strategy.runtime == "freqtrade_reference"
  assert run.provenance.strategy.entrypoint == "NostalgiaForInfinityX7"
  assert run.provenance.strategy.parameter_snapshot.requested == {}
  assert run.provenance.strategy.parameter_snapshot.resolved == {}
  assert run.provenance.reference_id == "nostalgia-for-infinity"
  assert run.provenance.reference is not None
  assert run.provenance.reference.title == "NostalgiaForInfinity"
  assert run.provenance.reference.integration_mode == "external_runtime"
  assert run.provenance.integration_mode == "external_runtime"
  assert run.provenance.working_directory.endswith("reference/NostalgiaForInfinity")
  assert run.provenance.external_command
  assert any(path.endswith("user_data/backtest_results") for path in run.provenance.artifact_paths)
  artifact_kinds = {artifact.kind for artifact in run.provenance.benchmark_artifacts}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all(isinstance(artifact.summary, dict) for artifact in run.provenance.benchmark_artifacts)
  assert all(isinstance(artifact.sections, dict) for artifact in run.provenance.benchmark_artifacts)
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.provider == "freqtrade_reference"
  assert run.provenance.market_data.sync_status == "delegated"
  assert run.provenance.market_data_by_symbol["BTC/USDT"].sync_status == "delegated"


def test_registered_strategy_run_records_lifecycle_timestamp(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  strategies = LocalStrategyCatalog()
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=strategies,
    references=build_references(),
    runs=runs,
  )

  app.register_strategy(
    strategy_id="ma_cross_v1",
    module_path="akra_trader.strategies.examples",
    class_name="MovingAverageCrossStrategy",
  )
  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )

  assert run.provenance.strategy is not None
  assert run.provenance.strategy.lifecycle.registered_at is not None
  assert run.provenance.strategy.parameter_snapshot.requested == {"short_window": 13}
  assert run.provenance.strategy.parameter_snapshot.resolved == {
    "short_window": 13,
    "long_window": 21,
  }


def test_list_runs_can_filter_by_strategy_metadata(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )

  app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  filtered = app.list_runs(
    mode="backtest",
    strategy_id="ma_cross_v1",
    strategy_version="1.0.0",
  )

  assert len(filtered) == 1
  assert filtered[0].config.strategy_id == "ma_cross_v1"
  assert filtered[0].config.strategy_version == "1.0.0"


def test_compare_runs_returns_side_by_side_native_and_reference_summary(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  comparison = app.compare_runs(run_ids=[native_run.config.run_id, reference_run.config.run_id])

  assert comparison.intent == "benchmark_validation"
  assert comparison.baseline_run_id == native_run.config.run_id
  assert [run.lane for run in comparison.runs] == ["native", "reference"]
  assert comparison.runs[1].reference_id == "nostalgia-for-infinity"
  assert comparison.runs[1].reference is not None
  assert comparison.runs[1].reference.integration_mode == "external_runtime"
  assert comparison.runs[1].artifact_paths
  assert comparison.runs[1].benchmark_artifacts
  assert all(isinstance(artifact.summary, dict) for artifact in comparison.runs[1].benchmark_artifacts)
  assert all(isinstance(artifact.sections, dict) for artifact in comparison.runs[1].benchmark_artifacts)
  assert len(comparison.narratives) == 1
  assert comparison.narratives[0].comparison_type == "native_vs_reference"
  assert comparison.narratives[0].run_id == reference_run.config.run_id
  assert comparison.narratives[0].rank == 1
  assert comparison.narratives[0].is_primary is True
  assert comparison.narratives[0].insight_score > 0
  assert comparison.narratives[0].title.startswith("Benchmark validation")
  assert comparison.narratives[0].summary == (
    "Benchmark validation falls back to persisted reference provenance because direct metric "
    "deltas are partial."
  )
  metric_rows = {row.key: row for row in comparison.metric_rows}
  assert set(metric_rows) == {
    "total_return_pct",
    "max_drawdown_pct",
    "win_rate_pct",
    "trade_count",
  }
  assert metric_rows["total_return_pct"].values[native_run.config.run_id] == native_run.metrics["total_return_pct"]
  assert reference_run.config.run_id in metric_rows["trade_count"].values
  assert comparison.runs[1].notes


def test_compare_runs_uses_reference_artifact_summary_for_divergence_narratives(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  reference_run.provenance.benchmark_artifacts = (
    BenchmarkArtifact(
      kind="result_snapshot_root",
      label="Backtest results root",
      path="/tmp/reference/backtest_results",
      summary={
        "strategy_name": "NostalgiaForInfinityX7",
        "profit_total_pct": 12.4,
        "max_drawdown_pct": 7.2,
        "trade_count": 36,
      },
      sections={
        "benchmark_story": {
          "headline": "NostalgiaForInfinityX7 returned 12.4% across 36 trades with 7.2% max drawdown.",
          "signal_context": "Signal exports captured 36 rows across 10 pairs.",
        },
      },
    ),
  )
  runs.save_run(reference_run)

  comparison = app.compare_runs(run_ids=[native_run.config.run_id, reference_run.config.run_id])

  assert comparison.intent == "benchmark_validation"
  metric_rows = {row.key: row for row in comparison.metric_rows}
  assert metric_rows["total_return_pct"].values[reference_run.config.run_id] == 12.4
  assert metric_rows["max_drawdown_pct"].values[reference_run.config.run_id] == 7.2
  assert metric_rows["trade_count"].values[reference_run.config.run_id] == 36
  assert len(comparison.narratives) == 1
  assert comparison.narratives[0].comparison_type == "native_vs_reference"
  assert comparison.narratives[0].rank == 1
  assert comparison.narratives[0].is_primary is True
  assert comparison.narratives[0].title.startswith("Benchmark validation")
  assert "benchmark drift" in comparison.narratives[0].summary
  assert any(
    bullet.startswith("Benchmark evidence: NostalgiaForInfinityX7 returned 12.4%")
    for bullet in comparison.narratives[0].bullets
  )


def test_compare_runs_reweights_multi_run_narratives_by_intent(tmp_path: Path) -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = build_references()
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )

  baseline_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )
  alternate_native_run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="ETH/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={"short_window": 13},
  )
  reference_run = app.run_backtest(
    strategy_id="nfi_x7_reference",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
  )

  baseline_run.metrics.update({
    "total_return_pct": 10.0,
    "max_drawdown_pct": 5.0,
    "win_rate_pct": 60.0,
    "trade_count": 20,
  })
  alternate_native_run.metrics.update({
    "total_return_pct": 15.0,
    "max_drawdown_pct": 7.0,
    "win_rate_pct": 64.0,
    "trade_count": 30,
  })
  reference_run.provenance.benchmark_artifacts = (
    BenchmarkArtifact(
      kind="result_snapshot_root",
      label="Backtest results root",
      path="/tmp/reference/backtest_results",
      summary={
        "strategy_name": "NostalgiaForInfinityX7",
        "profit_total_pct": 12.0,
        "max_drawdown_pct": 6.0,
        "trade_count": 22,
        "win_rate_pct": 61.0,
      },
      sections={
        "benchmark_story": {
          "headline": "NostalgiaForInfinityX7 returned 12% across 22 trades with 6% max drawdown.",
        },
      },
    ),
  )

  runs.save_run(baseline_run)
  runs.save_run(alternate_native_run)
  runs.save_run(reference_run)

  benchmark_validation = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="benchmark_validation",
  )
  strategy_tuning = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="strategy_tuning",
  )
  execution_regression = app.compare_runs(
    run_ids=[
      baseline_run.config.run_id,
      alternate_native_run.config.run_id,
      reference_run.config.run_id,
    ],
    intent="execution_regression",
  )

  assert benchmark_validation.intent == "benchmark_validation"
  assert [narrative.run_id for narrative in benchmark_validation.narratives] == [
    reference_run.config.run_id,
    alternate_native_run.config.run_id,
  ]
  assert [narrative.rank for narrative in benchmark_validation.narratives] == [1, 2]
  assert benchmark_validation.narratives[0].is_primary is True
  assert benchmark_validation.narratives[0].comparison_type == "native_vs_reference"
  assert benchmark_validation.narratives[0].title.startswith("Benchmark validation")
  assert "benchmark drift" in benchmark_validation.narratives[0].summary
  assert any(
    bullet.startswith("Benchmark evidence:")
    for bullet in benchmark_validation.narratives[0].bullets
  )

  assert strategy_tuning.intent == "strategy_tuning"
  assert [narrative.run_id for narrative in strategy_tuning.narratives] == [
    alternate_native_run.config.run_id,
    reference_run.config.run_id,
  ]
  assert [narrative.rank for narrative in strategy_tuning.narratives] == [1, 2]
  assert strategy_tuning.narratives[0].is_primary is True
  assert strategy_tuning.narratives[0].comparison_type == "native_vs_native"
  assert strategy_tuning.narratives[0].title.startswith("Strategy tuning")
  assert "optimization tradeoffs" in strategy_tuning.narratives[0].summary
  assert any(
    bullet.startswith("Tuning signal:")
    for bullet in strategy_tuning.narratives[0].bullets
  )

  assert execution_regression.intent == "execution_regression"
  assert execution_regression.narratives[0].run_id == alternate_native_run.config.run_id
  assert execution_regression.narratives[0].title.startswith("Execution regression")
  assert "execution drift" in execution_regression.narratives[0].summary
  assert any(
    bullet.startswith("Execution signal:")
    for bullet in execution_regression.narratives[0].bullets
  )
  assert benchmark_validation.narratives[0].insight_score > benchmark_validation.narratives[1].insight_score
  assert strategy_tuning.narratives[0].insight_score > strategy_tuning.narratives[1].insight_score


def test_backtest_failure_still_records_requested_market_lineage(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )

  run = app.run_backtest(
    strategy_id="ma_cross_v1",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
    parameters={},
    start_at=datetime(2030, 1, 1, tzinfo=UTC),
  )

  assert run.status == RunStatus.FAILED
  assert run.provenance.market_data is not None
  assert run.provenance.market_data.requested_start_at == datetime(2030, 1, 1, tzinfo=UTC)
  assert run.provenance.market_data.candle_count == 0


def test_multi_symbol_run_records_market_lineage_per_symbol(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    references=build_references(),
    runs=runs,
  )
  config = RunConfig(
    run_id="multi-symbol-lineage",
    mode=RunMode.BACKTEST,
    strategy_id="ma_cross_v1",
    strategy_version="1.0.0",
    venue="binance",
    symbols=("BTC/USDT", "ETH/USDT"),
    timeframe="5m",
    parameters={},
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=3,
  )

  run = app._simulate_run(config=config, active_bars=24)
  runs.save_run(run)
  reloaded = build_runs_repository(tmp_path).get_run(run.config.run_id)

  assert run.provenance.market_data is not None
  assert run.provenance.market_data.symbols == ("BTC/USDT", "ETH/USDT")
  assert run.provenance.market_data.candle_count == 48
  assert run.provenance.market_data.sync_status == "fixture"
  assert run.provenance.market_data_by_symbol["BTC/USDT"].symbols == ("BTC/USDT",)
  assert run.provenance.market_data_by_symbol["BTC/USDT"].candle_count == 24
  assert run.provenance.market_data_by_symbol["ETH/USDT"].symbols == ("ETH/USDT",)
  assert run.provenance.market_data_by_symbol["ETH/USDT"].candle_count == 24
  assert reloaded is not None
  assert reloaded.provenance.market_data_by_symbol == run.provenance.market_data_by_symbol
