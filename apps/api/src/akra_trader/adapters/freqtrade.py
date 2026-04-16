from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from io import BytesIO
import json
from pathlib import Path
import os
import re
import shutil
import subprocess
from typing import Any
from zipfile import BadZipFile
from zipfile import ZipFile

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
        sync_checkpoint_id=None,
        reproducibility_state="delegated",
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
      sync_checkpoint_id=None,
      reproducibility_state="delegated",
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
    elif path.suffix.lower() == ".zip":
      zip_summary, zip_sections = self._inspect_zip_snapshot(path)
      if zip_summary or zip_sections:
        summary.update(zip_summary)
        sections.update(zip_sections)
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

  def _inspect_zip_snapshot(self, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
      with ZipFile(path, "r") as archive:
        members = [
          member
          for member in archive.namelist()
          if member and not member.endswith("/")
        ]
        sections: dict[str, Any] = {}
        zip_contents = self._summarize_zip_members(members)
        if zip_contents:
          sections["zip_contents"] = zip_contents

        result_member, result_payload = self._find_zip_result_payload(archive, members)
        summary: dict[str, Any] = {}
        if result_payload is not None:
          result_summary, result_sections = self._summarize_freqtrade_payload(result_payload)
          summary.update(result_summary)
          self._merge_sections(sections, result_sections)
          if "zip_contents" in sections and result_member is not None:
            sections["zip_contents"]["result_json_entry"] = result_member

        config_member, config_payload = self._find_zip_config_payload(archive, members)
        config_section = self._summarize_zip_config_payload(config_payload)
        if config_section:
          sections["zip_config"] = config_section
          if "zip_contents" in sections and config_member is not None:
            sections["zip_contents"]["config_json_entry"] = config_member
          for key in ("exchange", "timeframe", "timeframe_detail", "stake_currency", "timerange"):
            summary.setdefault(key, config_section.get(key))
          self._set_summary_entry(summary, "strategy_name", summary.get("strategy_name") or config_section.get("strategy"))

        strategy_bundle = self._summarize_zip_strategy_bundle(archive, members)
        if strategy_bundle:
          sections["zip_strategy_bundle"] = strategy_bundle
          if "zip_contents" in sections:
            if "source_files" in strategy_bundle:
              sections["zip_contents"]["strategy_source_count"] = len(strategy_bundle["source_files"])
            if "parameter_files" in strategy_bundle:
              sections["zip_contents"]["strategy_param_count"] = len(strategy_bundle["parameter_files"])
          self._set_summary_entry(
            summary,
            "strategy_name",
            summary.get("strategy_name")
            or self._first_value(strategy_bundle.get("strategy_names")),
          )

        market_change_section = self._summarize_zip_market_change_export(archive, members)
        if market_change_section:
          sections["zip_market_change"] = market_change_section

        wallet_exports_section = self._summarize_zip_wallet_exports(archive, members)
        if wallet_exports_section:
          sections["zip_wallet_exports"] = wallet_exports_section

        for suffix, section_key in (
          ("signals.pkl", "zip_signal_exports"),
          ("rejected.pkl", "zip_rejected_exports"),
          ("exited.pkl", "zip_exited_exports"),
        ):
          pickle_section = self._summarize_zip_pickle_exports(
            archive=archive,
            members=members,
            suffix=suffix,
          )
          if pickle_section:
            sections[section_key] = pickle_section

        benchmark_story = self._build_benchmark_story(summary, sections)
        if benchmark_story:
          sections["benchmark_story"] = benchmark_story

        return summary, sections
    except (BadZipFile, OSError):
      return {}, {}

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

  def _build_benchmark_story(
    self,
    summary: dict[str, Any],
    sections: dict[str, Any],
  ) -> dict[str, Any]:
    story: dict[str, Any] = {}
    for key, value in (
      ("headline", self._describe_benchmark_headline(summary)),
      ("market_context", self._describe_market_context(sections.get("zip_market_change"))),
      (
        "portfolio_context",
        self._describe_portfolio_context(
          sections.get("zip_wallet_exports"),
        ),
      ),
      ("signal_context", self._describe_signal_context(sections.get("zip_signal_exports"))),
      ("rejection_context", self._describe_rejection_context(sections.get("zip_rejected_exports"))),
      (
        "exit_context",
        self._describe_exit_context(
          sections.get("zip_exited_exports"),
          sections.get("exit_reason_metrics"),
        ),
      ),
      (
        "pair_context",
        self._describe_pair_context(
          sections.get("pair_metrics"),
          sections.get("pair_extremes"),
        ),
      ),
    ):
      self._set_summary_entry(story, key, value)
    return story

  def _describe_benchmark_headline(self, summary: dict[str, Any]) -> str | None:
    strategy_name = summary.get("strategy_name")
    profit_total_pct = self._format_pct_text(summary.get("profit_total_pct"))
    trade_count = self._format_count_phrase(summary.get("trade_count"), "trade")
    max_drawdown_pct = self._format_pct_text(summary.get("max_drawdown_pct"))
    market_change_pct = self._format_pct_text(summary.get("market_change_pct"))

    if strategy_name is None and profit_total_pct is None and trade_count is None:
      return None

    subject = str(strategy_name) if strategy_name is not None else "Benchmark run"
    sentence = subject
    if profit_total_pct is not None:
      sentence += f" returned {profit_total_pct}"
    if trade_count is not None:
      connector = " across " if profit_total_pct is not None else " recorded "
      sentence += f"{connector}{trade_count}"
    if max_drawdown_pct is not None:
      connector = " with " if profit_total_pct is not None or trade_count is not None else " had "
      sentence += f"{connector}{max_drawdown_pct} max drawdown"
    if market_change_pct is not None:
      connector = " against " if profit_total_pct is not None or trade_count is not None else " with "
      sentence += f"{connector}a {market_change_pct} market move"
    return sentence + "."

  def _describe_market_context(self, market_section: Any) -> str | None:
    if not isinstance(market_section, dict):
      return None
    pair_count = self._coerce_count(market_section.get("pair_count"))
    if pair_count is None:
      return None

    positive_pair_count = self._coerce_count(market_section.get("positive_pair_count"))
    negative_pair_count = self._coerce_count(market_section.get("negative_pair_count"))
    if positive_pair_count == pair_count:
      opening = f"Breadth stayed positive across {pair_count} tracked pairs"
    elif negative_pair_count == pair_count:
      opening = f"Breadth stayed negative across {pair_count} tracked pairs"
    elif positive_pair_count is not None and negative_pair_count is not None:
      opening = (
        f"Breadth was mixed across {pair_count} tracked pairs "
        f"({positive_pair_count} positive / {negative_pair_count} negative)"
      )
    else:
      opening = f"Tracked market breadth covered {pair_count} pairs"

    best_pair = market_section.get("best_pair")
    best_pair_change_pct = self._format_signed_pct_text(market_section.get("best_pair_change_pct"))
    worst_pair = market_section.get("worst_pair")
    worst_pair_change_pct = self._format_signed_pct_text(market_section.get("worst_pair_change_pct"))
    if best_pair is None or best_pair_change_pct is None:
      return opening + "."
    if worst_pair is None or worst_pair_change_pct is None:
      return f"{opening}; {best_pair} led at {best_pair_change_pct}."
    return (
      f"{opening}; {best_pair} led at {best_pair_change_pct} "
      f"while {worst_pair} lagged at {worst_pair_change_pct}."
    )

  def _describe_portfolio_context(self, wallet_section: Any) -> str | None:
    if not isinstance(wallet_section, dict):
      return None
    start_value = self._coerce_float(wallet_section.get("total_quote_start"))
    end_value = self._coerce_float(wallet_section.get("total_quote_end"))
    high_value = self._format_number_text(wallet_section.get("total_quote_high"))
    low_value = self._format_number_text(wallet_section.get("total_quote_low"))
    if start_value is None or end_value is None:
      return None

    start_text = self._format_number_text(start_value)
    end_text = self._format_number_text(end_value)
    if start_text is None or end_text is None:
      return None

    if end_value > start_value:
      sentence = f"Wallet quote value rose from {start_text} to {end_text}"
    elif end_value < start_value:
      sentence = f"Wallet quote value fell from {start_text} to {end_text}"
    else:
      sentence = f"Wallet quote value held flat at {start_text}"
    if low_value is not None and high_value is not None:
      sentence += f", ranging between {low_value} and {high_value}"

    currency_preview = wallet_section.get("currency_quote_preview")
    if isinstance(currency_preview, list) and currency_preview:
      leading_currency = currency_preview[0]
      if isinstance(leading_currency, dict):
        currency = leading_currency.get("currency")
        latest_quote_value = self._format_number_text(leading_currency.get("latest_quote_value"))
        if currency is not None and latest_quote_value is not None:
          sentence += f"; {currency} finished as the largest tracked balance at {latest_quote_value}"
    return sentence + "."

  def _describe_signal_context(self, signal_section: Any) -> str | None:
    if not isinstance(signal_section, dict):
      return None
    row_count = self._format_count_phrase(signal_section.get("row_count"), "row")
    if row_count is None:
      return None
    pair_count = self._format_count_phrase(signal_section.get("pair_count"), "pair")
    sentence = f"Signal exports captured {row_count}"
    if pair_count is not None:
      sentence += f" across {pair_count}"

    details: list[str] = []
    dominant_tag = self._first_ranked_section_entry(signal_section.get("enter_tag_counts"))
    if dominant_tag is not None:
      details.append(
        f"{dominant_tag['label']} was the dominant entry tag ({dominant_tag['count']})"
      )
    dominant_pair = self._first_ranked_section_entry(
      signal_section.get("pair_row_preview"),
      label_key="pair",
    )
    if dominant_pair is not None:
      details.append(
        f"{dominant_pair['label']} generated the most rows ({dominant_pair['count']})"
      )
    if details:
      sentence += "; " + " and ".join(details)
    return sentence + "."

  def _describe_rejection_context(self, rejection_section: Any) -> str | None:
    if not isinstance(rejection_section, dict):
      return None
    row_count = self._coerce_count(rejection_section.get("row_count"))
    if row_count is None:
      return None
    leading_reason = self._first_ranked_section_entry(rejection_section.get("reason_counts"))
    if row_count == 0:
      return "Rejected entries were not captured in the embedded export."
    if leading_reason is None:
      return f"Rejected entries accounted for {row_count} rows."
    if row_count == 1:
      return f"Rejected entries were limited to 1 row, entirely driven by {leading_reason['label']}."
    return (
      f"Rejected entries accounted for {row_count} rows, led by "
      f"{leading_reason['label']} ({leading_reason['count']})."
    )

  def _describe_exit_context(
    self,
    exit_section: Any,
    exit_reason_metrics: Any,
  ) -> str | None:
    if not isinstance(exit_section, dict):
      return None
    row_count = self._coerce_count(exit_section.get("row_count"))
    leading_exit = self._first_ranked_section_entry(exit_section.get("exit_reason_counts"))
    if row_count is None or leading_exit is None:
      return None

    sentence = (
      f"Exit exports were dominated by {leading_exit['label']} "
      f"({self._format_count_phrase(leading_exit['count'], 'row')})."
    )
    if isinstance(exit_reason_metrics, dict):
      preview_rows = exit_reason_metrics.get("preview")
      if isinstance(preview_rows, list):
        matching_row = next(
          (
            row
            for row in preview_rows
            if isinstance(row, dict) and row.get("label") == leading_exit["label"]
          ),
          None,
        )
        if isinstance(matching_row, dict):
          trade_count = self._format_count_phrase(matching_row.get("trade_count"), "trade")
          profit_total_pct = self._format_pct_text(matching_row.get("profit_total_pct"))
          if trade_count is not None and profit_total_pct is not None:
            sentence = (
              sentence[:-1]
              + f", matching the benchmark summary where {leading_exit['label']} "
              f"closed {trade_count} for {profit_total_pct}."
            )
    return sentence

  def _describe_pair_context(
    self,
    pair_metrics: Any,
    pair_extremes: Any,
  ) -> str | None:
    best_label: str | None = None
    total_trade_count: str | None = None
    total_return: str | None = None

    if isinstance(pair_metrics, dict):
      best_row = pair_metrics.get("best")
      if isinstance(best_row, dict) and isinstance(best_row.get("label"), str):
        best_label = best_row["label"]
      total_row = pair_metrics.get("total")
      if isinstance(total_row, dict):
        total_trade_count = self._format_count_phrase(total_row.get("trade_count"), "trade")
        total_return = self._format_pct_text(total_row.get("profit_total_pct"))

    if best_label is None and isinstance(pair_extremes, dict):
      best_row = pair_extremes.get("best")
      if isinstance(best_row, dict) and isinstance(best_row.get("label"), str):
        best_label = best_row["label"]

    if best_label is None and total_trade_count is None and total_return is None:
      return None

    opening = (
      f"Pair metrics stayed concentrated in {best_label}"
      if best_label is not None
      else "Pair metrics remained available in the embedded result tables"
    )
    details: list[str] = []
    if total_trade_count is not None:
      details.append(f"the aggregate row logged {total_trade_count}")
    if total_return is not None:
      details.append(f"{total_return} total return")
    if not details:
      return opening + "."
    if len(details) == 1:
      return f"{opening}; {details[0]}."
    return f"{opening}; {details[0]} and {details[1]}."

  @staticmethod
  def _first_ranked_section_entry(
    value: Any,
    *,
    label_key: str = "label",
  ) -> dict[str, Any] | None:
    if not isinstance(value, list) or not value:
      return None
    entry = value[0]
    if not isinstance(entry, dict):
      return None
    label = entry.get(label_key)
    count = FreqtradeReferenceAdapter._coerce_count(entry.get("count"))
    if not isinstance(label, str) or count is None:
      return None
    return {
      "label": label,
      "count": count,
    }

  @staticmethod
  def _format_number_text(value: Any) -> str | None:
    number = FreqtradeReferenceAdapter._coerce_float(value)
    if number is None:
      return None
    rounded = round(number, 4)
    if float(rounded).is_integer():
      return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")

  @staticmethod
  def _format_pct_text(value: Any) -> str | None:
    number_text = FreqtradeReferenceAdapter._format_number_text(value)
    if number_text is None:
      return None
    return f"{number_text}%"

  @staticmethod
  def _format_signed_pct_text(value: Any) -> str | None:
    number = FreqtradeReferenceAdapter._coerce_float(value)
    if number is None:
      return None
    pct_text = FreqtradeReferenceAdapter._format_pct_text(number)
    if pct_text is None:
      return None
    if number > 0:
      return f"+{pct_text}"
    return pct_text

  @staticmethod
  def _format_count_phrase(value: Any, singular: str) -> str | None:
    count = FreqtradeReferenceAdapter._coerce_count(value)
    if count is None:
      return None
    suffix = singular if count == 1 else f"{singular}s"
    return f"{count} {suffix}"

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
  def _merge_sections(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
      target[key] = value

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
  def _read_zip_json_payload(archive: ZipFile, member: str) -> Any | None:
    try:
      with archive.open(member, "r") as file_handle:
        return json.loads(file_handle.read().decode("utf-8"))
    except (KeyError, OSError, UnicodeDecodeError, json.JSONDecodeError):
      return None

  def _find_zip_result_payload(
    self,
    archive: ZipFile,
    members: list[str],
  ) -> tuple[str | None, Any | None]:
    for member in members:
      if not member.lower().endswith(".json"):
        continue
      if member.lower().endswith("_config.json"):
        continue
      payload = self._read_zip_json_payload(archive, member)
      if isinstance(payload, dict) and (
        "strategy" in payload or "strategy_comparison" in payload or "metadata" in payload
      ):
        return member, payload
    return None, None

  def _find_zip_config_payload(
    self,
    archive: ZipFile,
    members: list[str],
  ) -> tuple[str | None, dict[str, Any] | None]:
    config_member = next(
      (
        member for member in members
        if member.lower().endswith("_config.json")
      ),
      None,
    )
    if config_member is None:
      return None, None
    payload = self._read_zip_json_payload(archive, config_member)
    return config_member, payload if isinstance(payload, dict) else None

  def _summarize_zip_members(self, members: list[str]) -> dict[str, Any]:
    if not members:
      return {}
    lower_members = [member.lower() for member in members]
    return {
      "member_count": len(members),
      "entry_preview": members[:6],
      "market_change_export_count": sum(member.endswith("_market_change.feather") for member in lower_members),
      "wallet_export_count": sum(member.endswith("_wallet.feather") for member in lower_members),
      "signal_export_count": sum(member.endswith("_signals.pkl") for member in lower_members),
      "rejected_export_count": sum(member.endswith("_rejected.pkl") for member in lower_members),
      "exited_export_count": sum(member.endswith("_exited.pkl") for member in lower_members),
      "strategy_source_count": sum(member.endswith(".py") for member in lower_members),
    }

  def _summarize_zip_config_payload(self, payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
      return {}
    section: dict[str, Any] = {}
    self._set_summary_entry(section, "strategy", payload.get("strategy"))
    self._set_summary_entry(section, "timeframe", payload.get("timeframe"))
    self._set_summary_entry(section, "timeframe_detail", payload.get("timeframe_detail"))
    self._set_summary_entry(section, "stake_currency", payload.get("stake_currency"))
    self._set_summary_entry(section, "timerange", payload.get("timerange"))
    self._set_summary_entry(section, "trading_mode", payload.get("trading_mode"))
    self._set_summary_entry(section, "margin_mode", payload.get("margin_mode"))
    self._set_summary_entry(section, "max_open_trades", payload.get("max_open_trades"))
    self._set_summary_entry(section, "export", payload.get("export"))
    self._set_summary_entry(section, "exchange", self._extract_config_exchange_name(payload.get("exchange")))
    return section

  def _summarize_zip_strategy_bundle(
    self,
    archive: ZipFile,
    members: list[str],
  ) -> dict[str, Any]:
    source_files = [
      member for member in members
      if member.lower().endswith(".py")
    ]
    parameter_files = [
      member
      for member in members
      if self._is_zip_strategy_parameter_member(archive, member)
    ]
    strategy_names: list[str] = []
    parameter_keys: dict[str, list[str]] = {}
    for parameter_file in parameter_files[:5]:
      payload = self._read_zip_json_payload(archive, parameter_file)
      if not isinstance(payload, dict):
        continue
      strategy_name = payload.get("strategy_name")
      if isinstance(strategy_name, str):
        strategy_names.append(strategy_name)
      params = payload.get("params")
      if isinstance(params, dict):
        parameter_keys[self._zip_member_name(parameter_file)] = list(params.keys())[:8]
    section: dict[str, Any] = {}
    if source_files:
      section["source_files"] = source_files[:5]
    if parameter_files:
      section["parameter_files"] = parameter_files[:5]
    if strategy_names:
      section["strategy_names"] = strategy_names[:5]
    if parameter_keys:
      section["parameter_keys"] = parameter_keys
    return section

  def _summarize_zip_market_change_export(
    self,
    archive: ZipFile,
    members: list[str],
  ) -> dict[str, Any]:
    market_change_member = next(
      (
        member for member in members
        if member.lower().endswith("_market_change.feather")
      ),
      None,
    )
    if market_change_member is None:
      return {}
    dataframe = self._read_zip_feather_frame(archive, market_change_member)
    if dataframe is None:
      return {
        "entry": market_change_member,
        "inspection_status": "unreadable",
      }
    section = self._summarize_dataframe(dataframe)
    section["entry"] = market_change_member
    non_temporal_columns = [
      column
      for column in dataframe.columns
      if str(column) not in {"date", "open_date", "close_date", "timestamp"}
    ]
    if non_temporal_columns:
      section["pair_count"] = len(non_temporal_columns)
      section["pairs"] = non_temporal_columns[:8]
      pair_change_summary = self._summarize_market_change_pairs(dataframe, non_temporal_columns)
      section.update(pair_change_summary)
    return section

  def _summarize_zip_wallet_exports(
    self,
    archive: ZipFile,
    members: list[str],
  ) -> dict[str, Any]:
    wallet_members = [
      member for member in members
      if member.lower().endswith("_wallet.feather")
    ]
    if not wallet_members:
      return {}

    entries: list[dict[str, Any]] = []
    strategies: list[str] = []
    currencies: set[str] = set()
    total_row_count = 0
    unreadable_entries: list[str] = []
    wallet_frames: list[Any] = []

    for member in wallet_members:
      dataframe = self._read_zip_feather_frame(archive, member)
      if dataframe is None:
        unreadable_entries.append(member)
        continue
      total_row_count += len(dataframe)
      strategy_name = self._extract_strategy_name_from_export_member(member, "_wallet.feather")
      if strategy_name is not None:
        strategies.append(strategy_name)
      if "currency" in dataframe.columns:
        currencies.update(
          str(value)
          for value in dataframe["currency"].dropna().astype(str).unique().tolist()
        )
      wallet_frames.append(dataframe)
      entry = self._summarize_dataframe(dataframe)
      entry["entry"] = member
      if strategy_name is not None:
        entry["strategy"] = strategy_name
      if "currency" in dataframe.columns:
        entry["currency_count"] = int(dataframe["currency"].nunique(dropna=True))
      entries.append(entry)

    section: dict[str, Any] = {
      "export_count": len(wallet_members),
      "total_row_count": total_row_count,
      "entries": entries[:3],
    }
    if strategies:
      section["strategies"] = strategies[:8]
      section["strategy_count"] = len(set(strategies))
    if currencies:
      ordered_currencies = sorted(currencies)
      section["currencies"] = ordered_currencies[:8]
      section["currency_count"] = len(ordered_currencies)
    wallet_semantics = self._summarize_wallet_frames(wallet_frames)
    section.update(wallet_semantics)
    if unreadable_entries:
      section["unreadable_entries"] = unreadable_entries[:5]
    return section

  def _summarize_zip_pickle_exports(
    self,
    *,
    archive: ZipFile,
    members: list[str],
    suffix: str,
  ) -> dict[str, Any]:
    pickle_members = [
      member for member in members
      if member.lower().endswith(suffix)
    ]
    if not pickle_members:
      return {}

    strategies: set[str] = set()
    pairs: set[str] = set()
    entries: list[dict[str, Any]] = []
    total_row_count = 0
    total_frame_count = 0
    unreadable_entries: list[str] = []
    strategy_row_counts: Counter[str] = Counter()
    pair_row_counts: Counter[str] = Counter()
    semantic_counters: dict[str, Counter[str]] = {}
    semantic_columns: set[str] = set()

    for member in pickle_members:
      payload = self._read_zip_pickle_payload(archive, member)
      if payload is None:
        unreadable_entries.append(member)
        continue
      frames = self._iter_pickle_payload_frames(payload)
      payload_entries = self._summarize_pickle_frames(frames, member)
      if not payload_entries:
        unreadable_entries.append(member)
        continue
      for payload_entry, (strategy_name, pair_name, dataframe) in zip(payload_entries, frames, strict=False):
        total_frame_count += 1
        row_count = payload_entry.get("row_count")
        if isinstance(row_count, int):
          total_row_count += row_count
        if isinstance(strategy_name, str):
          strategies.add(strategy_name)
          if isinstance(row_count, int):
            strategy_row_counts[strategy_name] += row_count
        if isinstance(pair_name, str):
          pairs.add(pair_name)
          if isinstance(row_count, int):
            pair_row_counts[pair_name] += row_count
        dataframe_semantics = self._summarize_pickle_dataframe_semantics(dataframe, suffix)
        for semantic_key, values in dataframe_semantics.items():
          semantic_columns.add(semantic_key)
          semantic_counters.setdefault(semantic_key, Counter()).update(values)
      entries.extend(payload_entries)

    section: dict[str, Any] = {
      "export_count": len(pickle_members),
      "frame_count": total_frame_count,
      "row_count": total_row_count,
      "entries": entries[:5],
    }
    if strategies:
      ordered_strategies = sorted(strategies)
      section["strategy_count"] = len(ordered_strategies)
      section["strategies"] = ordered_strategies[:8]
    if pairs:
      ordered_pairs = sorted(pairs)
      section["pair_count"] = len(ordered_pairs)
      section["pairs"] = ordered_pairs[:8]
    if strategy_row_counts:
      section["strategy_row_preview"] = self._rank_counter(strategy_row_counts, label_key="strategy")
    if pair_row_counts:
      section["pair_row_preview"] = self._rank_counter(pair_row_counts, label_key="pair")
    if semantic_columns:
      section["semantic_columns"] = sorted(semantic_columns)
    for semantic_key, counter in semantic_counters.items():
      if counter:
        section[f"{semantic_key}_counts"] = self._rank_counter(counter)
    if unreadable_entries:
      section["unreadable_entries"] = unreadable_entries[:5]
    return section

  def _iter_pickle_payload_frames(
    self,
    payload: Any,
  ) -> list[tuple[str | None, str | None, Any]]:
    try:
      import pandas as pd
    except ImportError:
      return []

    frames: list[tuple[str | None, str | None, Any]] = []

    if isinstance(payload, dict):
      for strategy_key, strategy_value in payload.items():
        strategy_name = strategy_key if isinstance(strategy_key, str) else None
        if isinstance(strategy_value, dict):
          for pair_key, pair_value in strategy_value.items():
            pair_name = pair_key if isinstance(pair_key, str) else None
            if isinstance(pair_value, pd.DataFrame):
              frames.append((strategy_name, pair_name, pair_value))
        elif isinstance(strategy_value, pd.DataFrame):
          frames.append((strategy_name, None, strategy_value))
    elif isinstance(payload, pd.DataFrame):
      frames.append((None, None, payload))

    return frames

  def _summarize_pickle_frames(
    self,
    frames: list[tuple[str | None, str | None, Any]],
    member: str,
  ) -> list[dict[str, Any]]:
    if not frames:
      return []

    entries: list[dict[str, Any]] = []
    for strategy_name, pair_name, dataframe in frames:
      entry = self._summarize_dataframe(dataframe)
      entry["entry"] = member
      if strategy_name is not None:
        entry["strategy"] = strategy_name
      if pair_name is not None:
        entry["pair"] = pair_name
      entries.append(entry)
    return entries

  def _read_zip_feather_frame(
    self,
    archive: ZipFile,
    member: str,
  ) -> Any | None:
    try:
      import pandas as pd
    except ImportError:
      return None
    try:
      with archive.open(member, "r") as file_handle:
        return pd.read_feather(BytesIO(file_handle.read()))
    except Exception:
      return None

  def _read_zip_pickle_payload(
    self,
    archive: ZipFile,
    member: str,
  ) -> Any | None:
    try:
      import joblib
    except ImportError:
      return None
    try:
      with archive.open(member, "r") as file_handle:
        return joblib.load(BytesIO(file_handle.read()))
    except Exception:
      return None

  def _summarize_dataframe(self, dataframe: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
      "row_count": len(dataframe),
      "column_count": len(dataframe.columns),
      "columns": [str(column) for column in dataframe.columns[:8]],
    }
    date_start, date_end = self._extract_dataframe_time_range(dataframe)
    self._set_summary_entry(summary, "date_start", date_start)
    self._set_summary_entry(summary, "date_end", date_end)
    return summary

  def _summarize_market_change_pairs(
    self,
    dataframe: Any,
    pair_columns: list[Any],
  ) -> dict[str, Any]:
    try:
      import pandas as pd
    except ImportError:
      return {}
    ordered_dataframe = self._sort_dataframe_by_time(dataframe)
    pair_summaries: list[dict[str, Any]] = []
    for column in pair_columns:
      series = pd.to_numeric(ordered_dataframe[column], errors="coerce").dropna()
      if series.empty:
        continue
      start_value = float(series.iloc[0])
      end_value = float(series.iloc[-1])
      delta_pct = round((end_value - start_value) * 100, 4)
      pair_summaries.append(
        {
          "pair": str(column),
          "start_value": round(start_value, 6),
          "end_value": round(end_value, 6),
          "change_pct": delta_pct,
        }
      )
    if not pair_summaries:
      return {}
    ordered_pairs = sorted(pair_summaries, key=lambda item: item["change_pct"], reverse=True)
    return {
      "pair_change_preview": ordered_pairs[:3],
      "best_pair": ordered_pairs[0]["pair"],
      "best_pair_change_pct": ordered_pairs[0]["change_pct"],
      "worst_pair": ordered_pairs[-1]["pair"],
      "worst_pair_change_pct": ordered_pairs[-1]["change_pct"],
      "positive_pair_count": sum(1 for item in ordered_pairs if item["change_pct"] > 0),
      "negative_pair_count": sum(1 for item in ordered_pairs if item["change_pct"] < 0),
    }

  def _summarize_wallet_frames(self, frames: list[Any]) -> dict[str, Any]:
    if not frames:
      return {}
    try:
      import pandas as pd
    except ImportError:
      return {}
    combined = pd.concat(frames, ignore_index=True)
    if combined.empty:
      return {}

    section: dict[str, Any] = {}
    date_column = self._detect_dataframe_time_column(combined)
    if {"rate", "balance"}.issubset(set(combined.columns)):
      quote_values = pd.to_numeric(combined["rate"], errors="coerce") * pd.to_numeric(
        combined["balance"],
        errors="coerce",
      )
      combined = combined.assign(__quote_value=quote_values)
      if date_column is not None:
        ordered = self._sort_dataframe_by_time(combined)
        grouped = ordered.groupby(date_column)["__quote_value"].sum(min_count=1).dropna()
        if not grouped.empty:
          section["total_quote_start"] = round(float(grouped.iloc[0]), 4)
          section["total_quote_end"] = round(float(grouped.iloc[-1]), 4)
          section["total_quote_high"] = round(float(grouped.max()), 4)
          section["total_quote_low"] = round(float(grouped.min()), 4)
      if "currency" in combined.columns:
        latest_preview = self._summarize_wallet_currency_preview(combined, date_column)
        if latest_preview:
          section["currency_quote_preview"] = latest_preview
    return section

  def _summarize_wallet_currency_preview(
    self,
    dataframe: Any,
    date_column: str | None,
  ) -> list[dict[str, Any]]:
    try:
      import pandas as pd
    except ImportError:
      return []
    if "currency" not in dataframe.columns or "__quote_value" not in dataframe.columns:
      return []
    if date_column is not None:
      ordered = dataframe.sort_values(date_column)
      latest_rows = ordered.groupby("currency", as_index=False).tail(1)
    else:
      latest_rows = dataframe.groupby("currency", as_index=False).tail(1)
    previews: list[dict[str, Any]] = []
    for _, row in latest_rows.iterrows():
      previews.append(
        {
          "currency": str(row["currency"]),
          "latest_balance": round(float(row["balance"]), 6) if pd.notna(row["balance"]) else None,
          "latest_quote_value": round(float(row["__quote_value"]), 4)
          if pd.notna(row["__quote_value"])
          else None,
        }
      )
    previews.sort(key=lambda item: item.get("latest_quote_value") or 0.0, reverse=True)
    return previews[:3]

  def _summarize_pickle_dataframe_semantics(
    self,
    dataframe: Any,
    suffix: str,
  ) -> dict[str, Counter[str]]:
    columns_by_suffix = {
      "signals.pkl": ("enter_tag", "action", "side"),
      "rejected.pkl": ("reason", "enter_tag", "action"),
      "exited.pkl": ("exit_reason", "enter_tag", "action"),
    }
    semantic_counters: dict[str, Counter[str]] = {}
    for column in columns_by_suffix.get(suffix, ()):
      if column not in dataframe.columns:
        continue
      values = dataframe[column].dropna().astype(str).tolist()
      filtered_values = [value for value in values if value]
      if filtered_values:
        semantic_counters[column] = Counter(filtered_values)
    return semantic_counters

  def _sort_dataframe_by_time(self, dataframe: Any) -> Any:
    date_column = self._detect_dataframe_time_column(dataframe)
    if date_column is None:
      return dataframe
    return dataframe.sort_values(date_column)

  def _detect_dataframe_time_column(self, dataframe: Any) -> str | None:
    candidate_columns = ("date", "open_date", "close_date", "timestamp")
    for column in candidate_columns:
      if column in dataframe.columns:
        return column
    try:
      import pandas as pd
    except ImportError:
      return None
    for column in dataframe.columns:
      if pd.api.types.is_datetime64_any_dtype(dataframe[column]):
        return str(column)
    return None

  def _rank_counter(
    self,
    counter: Counter[str],
    *,
    label_key: str = "label",
  ) -> list[dict[str, Any]]:
    ranked = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [
      {
        label_key: label,
        "count": count,
      }
      for label, count in ranked[:5]
    ]

  def _extract_dataframe_time_range(self, dataframe: Any) -> tuple[str | None, str | None]:
    candidate_columns = ("date", "open_date", "close_date", "timestamp")
    for column in candidate_columns:
      if column not in dataframe.columns:
        continue
      date_start, date_end = self._summarize_series_time_range(dataframe[column])
      if date_start is not None or date_end is not None:
        return date_start, date_end

    try:
      import pandas as pd
    except ImportError:
      return None, None

    for column in dataframe.columns:
      series = dataframe[column]
      if pd.api.types.is_datetime64_any_dtype(series):
        return self._summarize_series_time_range(series)
    return None, None

  def _summarize_series_time_range(self, series: Any) -> tuple[str | None, str | None]:
    try:
      import pandas as pd
    except ImportError:
      return None, None
    try:
      datetime_series = pd.to_datetime(series, utc=True, errors="coerce").dropna()
    except (ValueError, TypeError):
      return None, None
    if datetime_series.empty:
      return None, None
    return (
      datetime_series.min().isoformat(),
      datetime_series.max().isoformat(),
    )

  def _is_zip_strategy_parameter_member(self, archive: ZipFile, member: str) -> bool:
    if not member.lower().endswith(".json"):
      return False
    if member.lower().endswith("_config.json"):
      return False
    payload = self._read_zip_json_payload(archive, member)
    if not isinstance(payload, dict):
      return False
    return "strategy_name" in payload or "params" in payload

  @staticmethod
  def _extract_config_exchange_name(exchange: Any) -> str | None:
    if isinstance(exchange, str):
      return exchange
    if isinstance(exchange, dict):
      name = exchange.get("name")
      if isinstance(name, str):
        return name
    return None

  @staticmethod
  def _zip_member_name(member: str) -> str:
    return Path(member).name

  def _extract_strategy_name_from_export_member(
    self,
    member: str,
    suffix: str,
  ) -> str | None:
    filename = self._zip_member_name(member)
    if not filename.endswith(suffix):
      return None
    stem = filename[:-len(suffix)]
    for pattern in (
      r"^backtest-result-\d{8}_\d{6}_(.+)$",
      r"^backtest-result-\d{4}(?:_\d{2}){5}_(.+)$",
      r"^.+?_(.+)$",
    ):
      matched = re.match(pattern, stem)
      if matched is not None:
        strategy_name = matched.group(1)
        if strategy_name:
          return strategy_name
    return None

  @staticmethod
  def _first_value(value: Any) -> Any:
    if isinstance(value, list) and value:
      return value[0]
    return value

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
