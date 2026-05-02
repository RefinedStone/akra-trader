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
from akra_trader.domain.models import BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import extract_benchmark_artifact_runtime_candidate_id
from akra_trader.domain.models import is_benchmark_artifact_metadata_key
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyMetadata



class FreqtradeArtifactSummaryMixin:
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
    source_locations = self._build_artifact_source_locations(
      summary=summary,
      sections=sections,
      source_path=summary_source_path or str(path),
    )
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
      source_locations=source_locations,
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
