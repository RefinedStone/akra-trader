from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
import json
from pathlib import Path
import os
import shutil
import subprocess
from typing import Any

from akra_trader.adapters.references import ReferenceCatalog
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyMetadata


@dataclass(frozen=True)
class PreparedCommand:
  command: list[str]
  working_directory: str
  reference_id: str
  reference_version: str | None
  integration_mode: str
  reference: ReferenceSource
  artifact_roots: tuple[str, ...]


class FreqtradeReferenceAdapter:
  def __init__(self, repo_root: Path, references: ReferenceCatalog) -> None:
    self._repo_root = repo_root
    self._references = references

  def prepare_backtest(self, config: RunConfig, metadata: StrategyMetadata) -> PreparedCommand:
    if metadata.reference_id is None:
      raise ValueError("Freqtrade reference strategy is missing reference_id metadata.")
    reference = self._references.get(metadata.reference_id)
    working_directory = self._references.absolute_path(self._repo_root, reference)
    if working_directory is None:
      raise ValueError(f"Reference {metadata.reference_id} does not define a local path.")
    timerange = self._format_timerange(config.start_at, config.end_at)
    mode = "spot"
    exchange = config.venue
    command = [
      "freqtrade",
      "backtesting",
      f"--strategy={metadata.entrypoint}",
      f"--timerange={timerange}",
      "--user-data-dir=user_data",
      "--config=configs/exampleconfig.json",
      "--config=configs/exampleconfig_secret.json",
      f"--config=configs/trading_mode-{mode}.json",
      f"--config=configs/blacklist-{exchange}.json",
      f"--config=configs/pairlist-backtest-static-{exchange}-{mode}-usdt.json",
      "--breakdown=day",
      "--export=signals",
    ]
    return PreparedCommand(
      command=command,
      working_directory=str(working_directory),
      reference_id=reference.reference_id,
      reference_version=self._resolve_reference_version(working_directory, metadata.version),
      integration_mode=reference.integration_mode,
      reference=reference,
      artifact_roots=self._default_artifact_roots(working_directory),
    )

  def execute_backtest(self, run: RunRecord, metadata: StrategyMetadata) -> RunRecord:
    prepared = self.prepare_backtest(run.config, metadata)
    market_data_by_symbol = {
      symbol: MarketDataLineage(
        provider="freqtrade_reference",
        venue=run.config.venue,
        symbols=(symbol,),
        timeframe=run.config.timeframe,
        requested_start_at=run.config.start_at,
        requested_end_at=run.config.end_at,
        sync_status="delegated",
      )
      for symbol in run.config.symbols
    }
    run.provenance.lane = "reference"
    run.provenance.reference_id = prepared.reference_id
    run.provenance.reference_version = prepared.reference_version
    run.provenance.integration_mode = prepared.integration_mode
    run.provenance.reference = prepared.reference
    run.provenance.working_directory = prepared.working_directory
    run.provenance.external_command = tuple(prepared.command)
    run.provenance.artifact_paths = prepared.artifact_roots
    run.provenance.benchmark_artifacts = self._build_benchmark_artifacts(prepared.artifact_roots)
    run.provenance.market_data = MarketDataLineage(
      provider="freqtrade_reference",
      venue=run.config.venue,
      symbols=run.config.symbols,
      timeframe=run.config.timeframe,
      requested_start_at=run.config.start_at,
      requested_end_at=run.config.end_at,
      sync_status="delegated",
    )
    run.provenance.market_data_by_symbol = market_data_by_symbol
    run.notes.append(f"Prepared NFI reference command: {' '.join(prepared.command)}")
    existing_artifacts = self._collect_artifacts(prepared.artifact_roots)

    if shutil.which("freqtrade") is None:
      run.status = RunStatus.FAILED
      run.notes.append(
        "freqtrade runtime was not found in PATH. Install freqtrade and the NFI "
        "dependencies to execute this reference strategy."
      )
      run.notes.append(
        "Reference artifacts would be written under: "
        + ", ".join(prepared.artifact_roots)
      )
      return run

    process = subprocess.run(
      prepared.command,
      cwd=prepared.working_directory,
      check=False,
      capture_output=True,
      text=True,
      shell=False,
    )
    run.notes.append(process.stdout.strip())
    if process.stderr.strip():
      run.notes.append(process.stderr.strip())
    resolved_artifact_paths = self._resolve_artifact_paths(
      artifact_roots=prepared.artifact_roots,
      existing_artifacts=existing_artifacts,
    )
    run.provenance.artifact_paths = resolved_artifact_paths
    run.provenance.benchmark_artifacts = self._build_benchmark_artifacts(resolved_artifact_paths)
    run.status = RunStatus.COMPLETED if process.returncode == 0 else RunStatus.FAILED
    run.ended_at = datetime.now(UTC)
    return run

  @staticmethod
  def _default_artifact_roots(reference_root: Path) -> tuple[str, ...]:
    return (
      str(reference_root / "user_data" / "backtest_results"),
      str(reference_root / "user_data" / "logs"),
    )

  @staticmethod
  def _collect_artifacts(artifact_roots: tuple[str, ...]) -> set[str]:
    artifacts: set[str] = set()
    for artifact_root in artifact_roots:
      root = Path(artifact_root)
      if not root.exists():
        continue
      for current_root, _, filenames in os.walk(root):
        for filename in filenames:
          if filename == ".gitkeep":
            continue
          artifacts.add(str(Path(current_root) / filename))
    return artifacts

  def _resolve_artifact_paths(
    self,
    *,
    artifact_roots: tuple[str, ...],
    existing_artifacts: set[str],
  ) -> tuple[str, ...]:
    collected_artifacts = self._collect_artifacts(artifact_roots)
    new_artifacts = sorted(collected_artifacts - existing_artifacts)
    if new_artifacts:
      return tuple(new_artifacts)
    persisted_roots = [artifact_root for artifact_root in artifact_roots if Path(artifact_root).exists()]
    if persisted_roots:
      return tuple(persisted_roots)
    return artifact_roots

  def _build_benchmark_artifacts(
    self,
    artifact_paths: tuple[str, ...],
  ) -> tuple[BenchmarkArtifact, ...]:
    return tuple(
      self._classify_artifact_path(artifact_path)
      for artifact_path in artifact_paths
    )

  def _classify_artifact_path(self, artifact_path: str) -> BenchmarkArtifact:
    path = Path(artifact_path)
    exists = path.exists()
    is_directory = path.is_dir()
    lower_name = path.name.lower()
    lower_parts = [part.lower() for part in path.parts]
    suffixes = path.suffixes
    format_name = suffixes[-1].lstrip(".") if suffixes else None

    kind = "reference_artifact"
    label = "Reference artifact"
    if lower_name == "backtest_results":
      kind = "result_snapshot_root"
      label = "Backtest results root"
    elif lower_name == "logs":
      kind = "runtime_log_root"
      label = "Runtime logs root"
    elif lower_name.endswith(".meta.json"):
      kind = "result_manifest"
      label = "Backtest result manifest"
      format_name = "json"
    elif "signal" in lower_name:
      kind = "signal_trace"
      label = "Signal trace export"
    elif "logs" in lower_parts or lower_name.endswith(".log"):
      kind = "runtime_log"
      label = "Runtime log"
    elif "backtest_results" in lower_parts and any(suffix in {".json", ".zip"} for suffix in suffixes):
      kind = "result_snapshot"
      label = "Backtest result snapshot"
    elif "backtest_results" in lower_parts and format_name == "csv":
      kind = "result_table"
      label = "Benchmark result table"

    summary, sections, summary_source_path = self._summarize_artifact(path, kind)
    return BenchmarkArtifact(
      kind=kind,
      label=label,
      path=str(path),
      format=format_name,
      exists=exists,
      is_directory=is_directory,
      summary=summary,
      sections=sections,
      summary_source_path=summary_source_path,
    )

  def _summarize_artifact(
    self,
    path: Path,
    kind: str,
  ) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    if not path.exists():
      return {}, {}, None
    if kind == "result_manifest":
      summary, sections = self._extract_summary_from_json(path)
      return summary, sections, str(path) if summary or sections else None
    if kind == "result_snapshot":
      return self._summarize_result_snapshot(path)
    if kind == "result_snapshot_root":
      return self._summarize_result_root(path)
    return {}, {}, None

  def _summarize_result_snapshot(
    self,
    path: Path,
  ) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    summary: dict[str, Any] = {}
    sections: dict[str, Any] = {}
    source_path: str | None = None
    if path.suffix.lower() == ".json":
      snapshot_summary, snapshot_sections = self._extract_summary_from_json(path)
      if snapshot_summary or snapshot_sections:
        summary.update(snapshot_summary)
        sections.update(snapshot_sections)
        source_path = str(path)

    manifest_path = self._find_related_manifest(path)
    if manifest_path is not None:
      manifest_summary, manifest_sections = self._extract_summary_from_json(manifest_path)
      for key, value in manifest_summary.items():
        summary.setdefault(key, value)
      for key, value in manifest_sections.items():
        sections.setdefault(key, value)
      if source_path is None and (manifest_summary or manifest_sections):
        source_path = str(manifest_path)
    return summary, sections, source_path

  def _summarize_result_root(
    self,
    root: Path,
  ) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    if not root.is_dir():
      return {}, {}, None

    manifest_paths = sorted(
      (
        path for path in root.rglob("*.meta.json")
        if path.is_file()
      ),
      key=self._artifact_sort_key,
    )
    snapshot_paths = sorted(
      (
        path for path in root.rglob("*")
        if path.is_file() and self._is_result_snapshot(path)
      ),
      key=self._artifact_sort_key,
    )

    summary: dict[str, Any] = {}
    sections: dict[str, Any] = {}
    source_path: str | None = None
    if snapshot_paths:
      summary, sections, source_path = self._summarize_result_snapshot(snapshot_paths[-1])
    elif manifest_paths:
      manifest_summary, manifest_sections = self._extract_summary_from_json(manifest_paths[-1])
      if manifest_summary or manifest_sections:
        summary = manifest_summary
        sections = manifest_sections
        source_path = str(manifest_paths[-1])

    if manifest_paths:
      summary.setdefault("manifest_count", len(manifest_paths))
    if snapshot_paths:
      summary.setdefault("snapshot_count", len(snapshot_paths))
    return summary, sections, source_path

  def _extract_summary_from_json(self, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = self._read_json_payload(path)
    if payload is None:
      return {}, {}
    return self._summarize_freqtrade_payload(payload)

  def _summarize_freqtrade_payload(self, payload: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if isinstance(payload, list):
      payload = next((item for item in payload if isinstance(item, dict)), None)
    if not isinstance(payload, dict):
      return {}, {}

    strategy_name = self._select_strategy_name(payload)
    strategy_payload = self._select_nested_strategy_payload(payload.get("strategy"), strategy_name)
    metadata_payload = self._select_nested_strategy_payload(payload.get("metadata"), strategy_name)
    comparison_rows = payload.get("strategy_comparison")
    comparison_payload = self._select_comparison_entry(comparison_rows, strategy_name)
    candidates = self._build_summary_candidates(
      payload=payload,
      metadata_payload=metadata_payload,
      strategy_payload=strategy_payload,
      comparison_payload=comparison_payload,
    )
    summary: dict[str, Any] = {}

    selected_strategy_name = strategy_name or self._extract_strategy_name(payload, candidates)
    self._set_summary_entry(summary, "strategy_name", selected_strategy_name)
    self._set_summary_entry(summary, "run_id", self._lookup_value(candidates, "run_id", "backtest_run_id"))
    self._set_summary_entry(summary, "exchange", self._lookup_value(candidates, "exchange", "exchange_name"))
    self._set_summary_entry(summary, "stake_currency", self._lookup_value(candidates, "stake_currency"))
    self._set_summary_entry(summary, "timeframe", self._lookup_value(candidates, "timeframe", "timeframe_detail"))
    self._set_summary_entry(summary, "timerange", self._lookup_value(candidates, "timerange"))
    self._set_summary_entry(
      summary,
      "generated_at",
      self._lookup_value(candidates, "generated_at", "exported_at", "created_at", "export_time"),
    )
    self._set_summary_entry(
      summary,
      "backtest_start_at",
      self._lookup_value(
        candidates,
        "backtest_start_at",
        "backtest_start_ts",
        "backtest_start_time",
        "backtest_start",
      ),
    )
    self._set_summary_entry(
      summary,
      "backtest_end_at",
      self._lookup_value(
        candidates,
        "backtest_end_at",
        "backtest_end_ts",
        "backtest_end_time",
        "backtest_end",
      ),
    )

    pair_count = self._coerce_count(
      self._lookup_value(
        candidates,
        "pair_count",
        "pairs_count",
        "pairlist",
        "pairs",
        "results_per_pair",
        "pair_stats",
      )
    )
    self._set_summary_entry(summary, "pair_count", pair_count)

    trade_count = self._coerce_count(
      self._lookup_value(candidates, "trade_count", "total_trades", "trades")
    )
    self._set_summary_entry(summary, "trade_count", trade_count)
    self._set_summary_entry(
      summary,
      "profit_total_pct",
      self._lookup_pct_value(
        candidates,
        pct_keys=("profit_total_pct", "total_profit_pct", "profit_pct"),
        ratio_keys=("profit_total", "total_profit"),
      ),
    )
    self._set_summary_entry(
      summary,
      "profit_total_abs",
      self._lookup_value(candidates, "profit_total_abs", "total_profit_abs", "profit_total"),
    )
    self._set_summary_entry(
      summary,
      "max_drawdown_pct",
      self._lookup_pct_value(
        candidates,
        pct_keys=("max_drawdown_pct", "absolute_drawdown_pct", "drawdown_pct"),
        ratio_keys=("max_drawdown_account", "max_relative_drawdown"),
      ),
    )
    self._set_summary_entry(
      summary,
      "market_change_pct",
      self._lookup_pct_value(
        candidates,
        pct_keys=("market_change_pct",),
        ratio_keys=("market_change",),
      ),
    )
    sections = self._build_section_summaries(
      payload=payload,
      metadata_payload=metadata_payload,
      strategy_payload=strategy_payload,
      comparison_rows=comparison_rows,
    )
    return summary, sections

  @staticmethod
  def _build_summary_candidates(
    *,
    payload: dict[str, Any],
    metadata_payload: dict[str, Any] | None,
    strategy_payload: dict[str, Any] | None,
    comparison_payload: dict[str, Any] | None,
  ) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for candidate in (metadata_payload, strategy_payload, comparison_payload):
      if isinstance(candidate, dict):
        candidates.append(candidate)
    for key in ("summary", "backtest_result", "result"):
      value = payload.get(key)
      if isinstance(value, dict):
        candidates.append(value)
    candidates.append(payload)
    return candidates

  def _build_section_summaries(
    self,
    *,
    payload: dict[str, Any],
    metadata_payload: dict[str, Any] | None,
    strategy_payload: dict[str, Any] | None,
    comparison_rows: Any,
  ) -> dict[str, Any]:
    sections: dict[str, Any] = {}

    metadata_section = self._summarize_metadata_section(metadata_payload)
    if metadata_section:
      sections["metadata"] = metadata_section

    strategy_comparison_section = self._summarize_table_section(comparison_rows)
    if strategy_comparison_section:
      sections["strategy_comparison"] = strategy_comparison_section

    if not isinstance(strategy_payload, dict):
      return sections

    for source_key, target_key in (
      ("results_per_pair", "pair_metrics"),
      ("results_per_enter_tag", "enter_tag_metrics"),
      ("exit_reason_summary", "exit_reason_metrics"),
      ("mix_tag_stats", "mixed_tag_metrics"),
      ("left_open_trades", "left_open_metrics"),
    ):
      table_section = self._summarize_table_section(strategy_payload.get(source_key))
      if table_section:
        sections[target_key] = table_section

    periodic_breakdown = self._summarize_periodic_breakdown_section(
      strategy_payload.get("periodic_breakdown")
    )
    if periodic_breakdown:
      sections["periodic_breakdown"] = periodic_breakdown

    daily_profit = self._summarize_daily_profit_section(strategy_payload.get("daily_profit"))
    if daily_profit:
      sections["daily_profit"] = daily_profit

    wallet_stats = self._summarize_wallet_stats_section(strategy_payload.get("wallet_stats"))
    if wallet_stats:
      sections["wallet_stats"] = wallet_stats

    pair_extremes = self._summarize_pair_extremes_section(strategy_payload)
    if pair_extremes:
      sections["pair_extremes"] = pair_extremes

    return sections

  def _summarize_metadata_section(self, metadata_payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(metadata_payload, dict):
      return {}
    section: dict[str, Any] = {}
    self._set_summary_entry(section, "run_id", metadata_payload.get("run_id"))
    self._set_summary_entry(section, "timeframe", metadata_payload.get("timeframe"))
    self._set_summary_entry(section, "timeframe_detail", metadata_payload.get("timeframe_detail"))
    self._set_summary_entry(
      section,
      "backtest_start_at",
      metadata_payload.get("backtest_start_ts") or metadata_payload.get("backtest_start_time"),
    )
    self._set_summary_entry(
      section,
      "backtest_end_at",
      metadata_payload.get("backtest_end_ts") or metadata_payload.get("backtest_end_time"),
    )
    self._set_summary_entry(section, "notes", metadata_payload.get("notes"))
    return section

  def _summarize_table_section(self, rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list):
      return {}
    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
      return {}

    content_rows = [
      row for row in dict_rows
      if str(row.get("key", "")).upper() != "TOTAL"
    ] or dict_rows
    total_row = next(
      (
        row for row in dict_rows
        if str(row.get("key", "")).upper() == "TOTAL"
      ),
      None,
    )
    section: dict[str, Any] = {
      "count": len(content_rows),
      "preview": [self._summarize_metric_row(row) for row in content_rows[:3]],
    }
    best_row, worst_row = self._select_best_and_worst_rows(content_rows)
    if best_row is not None:
      section["best"] = self._summarize_metric_row(best_row)
    if worst_row is not None:
      section["worst"] = self._summarize_metric_row(worst_row)
    if total_row is not None:
      section["total"] = self._summarize_metric_row(total_row)
    return section

  def _summarize_periodic_breakdown_section(self, breakdown: Any) -> dict[str, Any]:
    if not isinstance(breakdown, dict):
      return {}
    section: dict[str, Any] = {}
    for period, rows in breakdown.items():
      if not isinstance(rows, list):
        continue
      dict_rows = [row for row in rows if isinstance(row, dict)]
      if not dict_rows:
        continue
      best_row = max(dict_rows, key=lambda row: self._coerce_float(row.get("profit_abs")) or float("-inf"))
      worst_row = min(dict_rows, key=lambda row: self._coerce_float(row.get("profit_abs")) or float("inf"))
      section[period] = {
        "count": len(dict_rows),
        "best": self._summarize_metric_row(best_row),
        "worst": self._summarize_metric_row(worst_row),
      }
    return section

  def _summarize_daily_profit_section(self, daily_profit: Any) -> dict[str, Any]:
    if not isinstance(daily_profit, list):
      return {}
    rows = []
    for row in daily_profit:
      if isinstance(row, (list, tuple)) and len(row) >= 2:
        rows.append({
          "date": row[0],
          "profit_abs": row[1],
        })
      elif isinstance(row, dict):
        rows.append(row)
    if not rows:
      return {}
    best_row = max(rows, key=lambda row: self._coerce_float(row.get("profit_abs")) or float("-inf"))
    worst_row = min(rows, key=lambda row: self._coerce_float(row.get("profit_abs")) or float("inf"))
    return {
      "count": len(rows),
      "best": self._summarize_metric_row(best_row),
      "worst": self._summarize_metric_row(worst_row),
    }

  def _summarize_wallet_stats_section(self, wallet_stats: Any) -> dict[str, Any]:
    if not isinstance(wallet_stats, dict):
      return {}
    section: dict[str, Any] = {}
    for key in (
      "start_balance",
      "end_balance",
      "high_balance",
      "low_balance",
      "sharpe",
      "sortino",
      "calmar",
      "max_drawdown_abs",
      "drawdown_start",
      "drawdown_end",
    ):
      self._set_summary_entry(section, key, wallet_stats.get(key))
    self._set_summary_entry(
      section,
      "max_drawdown_pct",
      self._lookup_pct_value(
        [wallet_stats],
        pct_keys=("max_drawdown_pct",),
        ratio_keys=("max_drawdown_account", "max_relative_drawdown"),
      ),
    )
    return section

  def _summarize_pair_extremes_section(self, strategy_payload: dict[str, Any]) -> dict[str, Any]:
    section: dict[str, Any] = {}
    best_pair = strategy_payload.get("best_pair")
    worst_pair = strategy_payload.get("worst_pair")
    if isinstance(best_pair, dict):
      section["best"] = self._summarize_metric_row(best_pair)
    if isinstance(worst_pair, dict):
      section["worst"] = self._summarize_metric_row(worst_pair)
    return section

  def _summarize_metric_row(self, row: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    self._set_summary_entry(
      summary,
      "label",
      row.get("key") or row.get("date") or row.get("strategy_name") or row.get("name"),
    )
    self._set_summary_entry(summary, "date", row.get("date"))
    self._set_summary_entry(
      summary,
      "trade_count",
      row.get("trades") if row.get("trades") is not None else row.get("trade_count"),
    )
    self._set_summary_entry(
      summary,
      "profit_total_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("profit_total_pct", "profit_mean_pct"),
        ratio_keys=("profit_total", "profit_mean"),
      ),
    )
    self._set_summary_entry(summary, "profit_total_abs", row.get("profit_total_abs") or row.get("profit_abs"))
    self._set_summary_entry(
      summary,
      "win_rate_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("win_rate_pct",),
        ratio_keys=("winrate",),
      ),
    )
    self._set_summary_entry(
      summary,
      "max_drawdown_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("max_drawdown_pct",),
        ratio_keys=("max_drawdown_account",),
      ),
    )
    self._set_summary_entry(summary, "duration", row.get("duration_avg"))
    return summary

  def _select_best_and_worst_rows(
    self,
    rows: list[dict[str, Any]],
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    comparable_rows = [
      row for row in rows
      if self._coerce_float(row.get("profit_total_abs")) is not None
    ]
    if not comparable_rows:
      return None, None
    best_row = max(comparable_rows, key=lambda row: self._coerce_float(row.get("profit_total_abs")) or 0.0)
    worst_row = min(comparable_rows, key=lambda row: self._coerce_float(row.get("profit_total_abs")) or 0.0)
    return best_row, worst_row

  @staticmethod
  def _select_strategy_name(payload: dict[str, Any]) -> str | None:
    strategy = payload.get("strategy")
    if isinstance(strategy, str):
      return strategy
    if isinstance(strategy, dict):
      nested_name = next(
        (
          name
          for name, details in strategy.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if nested_name is not None:
        return nested_name
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
      metadata_name = next(
        (
          name
          for name, details in metadata.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if metadata_name is not None:
        return metadata_name
    strategy_comparison = payload.get("strategy_comparison")
    if isinstance(strategy_comparison, list):
      comparison_name = next(
        (
          row.get("key")
          for row in strategy_comparison
          if isinstance(row, dict) and isinstance(row.get("key"), str)
        ),
        None,
      )
      if isinstance(comparison_name, str):
        return comparison_name
    return None

  @staticmethod
  def _select_nested_strategy_payload(payload: Any, strategy_name: str | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
      return None
    if strategy_name is not None and isinstance(payload.get(strategy_name), dict):
      return payload[strategy_name]
    nested_payload = next(
      (
        value
        for value in payload.values()
        if isinstance(value, dict)
      ),
      None,
    )
    if isinstance(nested_payload, dict):
      return nested_payload
    return payload

  @staticmethod
  def _select_comparison_entry(rows: Any, strategy_name: str | None) -> dict[str, Any] | None:
    if not isinstance(rows, list):
      return None
    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
      return None
    if strategy_name is not None:
      matched_row = next(
        (
          row for row in dict_rows
          if row.get("key") == strategy_name or row.get("strategy_name") == strategy_name
        ),
        None,
      )
      if matched_row is not None:
        return matched_row
    return dict_rows[0]

  @staticmethod
  def _extract_strategy_name(
    payload: dict[str, Any],
    candidates: list[dict[str, Any]],
  ) -> str | None:
    direct_value = FreqtradeReferenceAdapter._lookup_value(
      candidates,
      "strategy_name",
      "strategy",
      "key",
      "name",
    )
    if isinstance(direct_value, str):
      return direct_value
    strategy = payload.get("strategy")
    if isinstance(strategy, str):
      return strategy
    if isinstance(strategy, dict):
      nested_name = next(
        (
          name
          for name, details in strategy.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if nested_name is not None:
        return nested_name
    return None

  @staticmethod
  def _lookup_value(candidates: list[dict[str, Any]], *keys: str) -> Any:
    for candidate in candidates:
      for key in keys:
        if key not in candidate:
          continue
        value = candidate[key]
        if value in (None, "", [], {}):
          continue
        return value
    return None

  @staticmethod
  def _lookup_pct_value(
    candidates: list[dict[str, Any]],
    *,
    pct_keys: tuple[str, ...],
    ratio_keys: tuple[str, ...],
  ) -> float | int | None:
    direct_value = FreqtradeReferenceAdapter._lookup_value(candidates, *pct_keys)
    if isinstance(direct_value, (int, float)):
      return direct_value
    ratio_value = FreqtradeReferenceAdapter._lookup_value(candidates, *ratio_keys)
    if isinstance(ratio_value, (int, float)):
      return round(ratio_value * 100, 4)
    return None

  @staticmethod
  def _set_summary_entry(summary: dict[str, Any], key: str, value: Any) -> None:
    normalized = FreqtradeReferenceAdapter._normalize_summary_value(key, value)
    if normalized is not None:
      summary[key] = normalized

  @staticmethod
  def _normalize_summary_value(key: str, value: Any) -> Any:
    if value in (None, "", [], {}):
      return None
    if key.endswith("_at"):
      return FreqtradeReferenceAdapter._normalize_timestamp(value)
    if key.endswith("_count"):
      return FreqtradeReferenceAdapter._coerce_count(value)
    if isinstance(value, (str, int, float, bool)):
      return value
    if isinstance(value, tuple):
      return [item for item in value]
    return str(value)

  @staticmethod
  def _normalize_timestamp(value: Any) -> str | None:
    if isinstance(value, (int, float)):
      timestamp = value / 1000 if value > 10_000_000_000 else value
      return datetime.fromtimestamp(timestamp, UTC).isoformat()
    if isinstance(value, str):
      return value
    return None

  @staticmethod
  def _coerce_count(value: Any) -> int | None:
    if isinstance(value, bool):
      return int(value)
    if isinstance(value, (int, float)):
      return int(value)
    if isinstance(value, (list, tuple, set, dict)):
      return len(value)
    return None

  @staticmethod
  def _coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
      return float(value)
    if isinstance(value, (int, float)):
      return float(value)
    return None

  @staticmethod
  def _read_json_payload(path: Path) -> Any | None:
    try:
      return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
      return None

  @staticmethod
  def _is_result_snapshot(path: Path) -> bool:
    lower_name = path.name.lower()
    if lower_name.endswith(".meta.json"):
      return False
    return any(suffix in {".json", ".zip"} for suffix in path.suffixes)

  @staticmethod
  def _find_related_manifest(path: Path) -> Path | None:
    if path.is_dir():
      return None
    candidate = path.with_suffix(".meta.json")
    if candidate.exists():
      return candidate
    return None

  @staticmethod
  def _artifact_sort_key(path: Path) -> tuple[float, str]:
    try:
      return path.stat().st_mtime, str(path)
    except OSError:
      return 0.0, str(path)

  @staticmethod
  def _resolve_reference_version(reference_root: Path, fallback: str | None) -> str | None:
    if not reference_root.exists():
      return fallback
    process = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      cwd=reference_root,
      check=False,
      capture_output=True,
      text=True,
      shell=False,
    )
    if process.returncode == 0 and process.stdout.strip():
      return process.stdout.strip()
    return fallback

  @staticmethod
  def _format_timerange(start_at: datetime | None, end_at: datetime | None) -> str:
    if start_at and end_at:
      return f"{start_at:%Y%m%d}-{end_at:%Y%m%d}"
    if start_at:
      return f"{start_at:%Y%m%d}-"
    if end_at:
      return f"-{end_at:%Y%m%d}"
    return "20250101-20250131"
