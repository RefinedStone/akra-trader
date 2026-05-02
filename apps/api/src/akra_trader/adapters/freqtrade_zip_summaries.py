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



class FreqtradeZipSummaryMixin:
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
