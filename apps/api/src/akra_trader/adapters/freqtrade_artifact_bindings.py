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



class FreqtradeArtifactBindingMixin:
  def _build_artifact_source_locations(
    self,
    *,
    summary: dict[str, Any],
    sections: dict[str, Any],
    source_path: str,
  ) -> dict[str, Any]:
    summary_locations = {
      key: self._build_artifact_summary_source_location(
        label_key=key,
        value=value,
        source_path=source_path,
      )
      for key, value in summary.items()
    }
    section_locations = {
      section_key: [
        self._build_artifact_section_source_location(
          section_key=section_key,
          line_key=line_key,
          line_index=line_index,
          value=value,
          source_path=source_path,
        )
        for line_index, (line_key, value) in enumerate(section.items())
      ]
      for section_key, section in sections.items()
      if isinstance(section, dict)
    }
    if not summary_locations and not section_locations:
      return {}
    return {
      "summary": summary_locations,
      "sections": section_locations,
    }

  def _build_artifact_summary_source_location(
    self,
    *,
    label_key: str,
    value: Any,
    source_path: str,
  ) -> dict[str, Any]:
    candidate_bindings = self._build_artifact_candidate_bindings(
      label_key=label_key,
      value=value,
    )
    return {
      "candidate_bindings": candidate_bindings,
      "label_key": label_key,
      "searchable_texts": self._collect_artifact_source_search_texts(label_key=label_key, value=value),
      "source_path": source_path,
    }

  def _build_artifact_section_source_location(
    self,
    *,
    section_key: str,
    line_key: str,
    line_index: int,
    value: Any,
    source_path: str,
  ) -> dict[str, Any]:
    candidate_bindings = self._build_artifact_candidate_bindings(
      label_key=line_key,
      section_key=section_key,
      value=value,
    )
    return {
      "candidate_bindings": candidate_bindings,
      "line_index": line_index,
      "line_key": line_key,
      "searchable_texts": self._collect_artifact_source_search_texts(
        label_key=line_key,
        value=value,
        section_key=section_key,
      ),
      "section_key": section_key,
      "source_path": source_path,
    }

  def _build_artifact_candidate_bindings(
    self,
    *,
    label_key: str,
    value: Any,
    section_key: str | None = None,
  ) -> list[dict[str, Any]]:
    symbol_keys = self._collect_artifact_candidate_binding_symbol_keys(value)
    if not symbol_keys:
      return []

    candidate_values = self._collect_artifact_candidate_binding_values(
      label_key=label_key,
      value=value,
      section_key=section_key,
    )
    bindings: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None, str | None, str | None]] = set()

    def add(
      symbol_key: str,
      candidate_value: str | None,
      candidate_id: str | None = None,
      runtime_candidate_id: str | None = None,
    ) -> None:
      normalized_symbol = self._normalize_artifact_candidate_binding_symbol_key(symbol_key)
      if not normalized_symbol:
        return
      normalized_value = candidate_value.strip() if isinstance(candidate_value, str) else None
      normalized_runtime_candidate_id = runtime_candidate_id.strip() if isinstance(runtime_candidate_id, str) else None
      key = (normalized_symbol, normalized_value, candidate_id, normalized_runtime_candidate_id)
      if key in seen:
        return
      seen.add(key)
      bindings.append({
        "binding_kind": "market_data_issue",
        "candidate_id": candidate_id,
        "runtime_candidate_id": normalized_runtime_candidate_id,
        "candidate_path_template": "provenance.market_data_by_symbol.{symbol_key}.issues",
        "candidate_value": normalized_value,
        "symbol_key": normalized_symbol,
      })

    for symbol_key in symbol_keys:
      add(symbol_key, None)
      for candidate_entry in candidate_values:
        candidate_value = candidate_entry["value"]
        if self._artifact_candidate_value_mentions_symbol(candidate_value, symbol_key):
          add(
            symbol_key,
            candidate_value,
            self._build_artifact_candidate_binding_id(
              symbol_key=symbol_key,
              candidate_value=candidate_entry["candidate_id_source"],
            ) if candidate_entry["candidate_id_source"] is not None else None,
            candidate_entry["runtime_candidate_id_source"],
          )
    return bindings

  def _collect_artifact_candidate_binding_values(
    self,
    *,
    label_key: str,
    value: Any,
    section_key: str | None = None,
  ) -> list[dict[str, str | None]]:
    collected: list[dict[str, str | None]] = []
    seen: set[str] = set()
    runtime_candidate_id = extract_benchmark_artifact_runtime_candidate_id(value)

    def add(
      candidate: str | None,
      *,
      canonical: bool = False,
      runtime_candidate_id_source: str | None = None,
    ) -> None:
      if candidate is None:
        return
      normalized = candidate.strip()
      if not normalized:
        return
      key = self._normalize_artifact_source_search_text(normalized)
      if not key or key in seen:
        return
      seen.add(key)
      collected.append({
        "candidate_id_source": normalized if canonical else None,
        "runtime_candidate_id_source": runtime_candidate_id_source.strip()
        if isinstance(runtime_candidate_id_source, str) and runtime_candidate_id_source.strip()
        else None,
        "value": normalized,
      })

    add(self._stringify_artifact_source_value(value))

    if isinstance(value, (str, int, float, bool)):
      add(
        str(value),
        canonical=isinstance(value, str),
        runtime_candidate_id_source=runtime_candidate_id if isinstance(value, str) else None,
      )
    elif isinstance(value, dict):
      for nested_key, nested_value in value.items():
        if is_benchmark_artifact_metadata_key(str(nested_key)):
          continue
        formatted_key = self._format_artifact_source_label(str(nested_key))
        if isinstance(nested_value, (str, int, float, bool)):
          add(f"{formatted_key}: {nested_value}")
          add(
            str(nested_value),
            canonical=isinstance(nested_value, str),
            runtime_candidate_id_source=runtime_candidate_id if isinstance(nested_value, str) else None,
          )
    elif isinstance(value, (list, tuple, set)):
      for item in value:
        if isinstance(item, (str, int, float, bool)):
          add(
            str(item),
            canonical=isinstance(item, str),
            runtime_candidate_id_source=runtime_candidate_id if isinstance(item, str) else None,
          )

    add(self._format_artifact_source_label(label_key))
    if section_key is not None:
      add(self._format_artifact_source_label(section_key))
    return collected

  def _collect_artifact_candidate_binding_symbol_keys(self, value: Any) -> list[str]:
    symbol_keys: list[str] = []
    seen: set[str] = set()

    def add(candidate: str | None) -> None:
      normalized = self._normalize_artifact_candidate_binding_symbol_key(candidate)
      if not normalized or normalized in seen:
        return
      seen.add(normalized)
      symbol_keys.append(normalized)

    def visit(candidate: Any) -> None:
      if candidate in (None, ""):
        return
      if isinstance(candidate, str):
        for match in re.finditer(r"(?<![A-Z0-9])([A-Z0-9]+/[A-Z0-9]+)(?![A-Z0-9])", candidate):
          add(match.group(1))
        return
      if isinstance(candidate, dict):
        for nested_key, nested_value in candidate.items():
          if is_benchmark_artifact_metadata_key(str(nested_key)):
            continue
          if str(nested_key) in {"pair", "symbol", "label", "key"} and isinstance(nested_value, str):
            add(nested_value)
          visit(nested_value)
        return
      if isinstance(candidate, (list, tuple, set)):
        for item in candidate:
          visit(item)

    visit(value)
    return symbol_keys

  @staticmethod
  def _normalize_artifact_candidate_binding_symbol_key(value: str | None) -> str | None:
    if value is None:
      return None
    trimmed = value.strip()
    if not trimmed:
      return None
    if ":" in trimmed:
      trimmed = trimmed.split(":", 1)[1].strip()
    return trimmed or None

  def _artifact_candidate_value_mentions_symbol(self, candidate_value: str, symbol_key: str) -> bool:
    normalized_candidate = self._normalize_artifact_source_search_text(candidate_value)
    if not normalized_candidate:
      return False
    normalized_symbol = self._normalize_artifact_source_search_text(symbol_key)
    if normalized_symbol and normalized_symbol in normalized_candidate:
      return True
    bare_symbol = symbol_key.replace("/", " ")
    normalized_bare_symbol = self._normalize_artifact_source_search_text(bare_symbol)
    return bool(normalized_bare_symbol and normalized_bare_symbol in normalized_candidate)

  @staticmethod
  def _build_artifact_candidate_binding_id(
    *,
    symbol_key: str,
    candidate_value: str | None,
  ) -> str | None:
    if candidate_value is None:
      return None
    trimmed = candidate_value.strip()
    if not trimmed:
      return None
    normalized_symbol = FreqtradeArtifactBindingMixin._normalize_artifact_candidate_binding_symbol_key(symbol_key)
    if normalized_symbol is None:
      return None
    return json.dumps(
      ["market_data_issue", normalized_symbol, trimmed],
      ensure_ascii=False,
      separators=(",", ":"),
    )

  def _collect_artifact_source_search_texts(
    self,
    *,
    label_key: str,
    value: Any,
    section_key: str | None = None,
  ) -> list[str]:
    collected: list[str] = []
    seen: set[str] = set()

    def add(candidate: str | None) -> None:
      if candidate is None:
        return
      normalized = self._normalize_artifact_source_search_text(candidate)
      if not normalized or normalized in seen:
        return
      seen.add(normalized)
      collected.append(candidate)

    add(self._format_artifact_source_label(label_key))
    if section_key is not None:
      add(self._format_artifact_source_label(section_key))
    add(self._stringify_artifact_source_value(value))

    def visit(candidate: Any) -> None:
      if candidate in (None, ""):
        return
      if isinstance(candidate, bool):
        add("true" if candidate else "false")
        return
      if isinstance(candidate, (int, float, str)):
        add(str(candidate))
        return
      if isinstance(candidate, dict):
        for nested_key, nested_value in candidate.items():
          if is_benchmark_artifact_metadata_key(str(nested_key)):
            continue
          formatted_key = self._format_artifact_source_label(str(nested_key))
          add(formatted_key)
          if isinstance(nested_value, (str, int, float, bool)):
            add(f"{formatted_key} {nested_value}")
          visit(nested_value)
        return
      if isinstance(candidate, (list, tuple, set)):
        for item in candidate:
          visit(item)

    visit(value)
    return collected

  @staticmethod
  def _format_artifact_source_label(key: str) -> str:
    return key.replace("_", " ")

  @staticmethod
  def _normalize_artifact_source_search_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()

  def _stringify_artifact_source_value(self, value: Any) -> str | None:
    if value in (None, ""):
      return None
    if isinstance(value, bool):
      return "true" if value else "false"
    if isinstance(value, (str, int, float)):
      return str(value)
    if isinstance(value, dict):
      rendered = [
        f"{self._format_artifact_source_label(str(key))}={nested}"
        for key, nested_value in value.items()
        if not is_benchmark_artifact_metadata_key(str(key))
        if (nested := self._stringify_artifact_source_value(nested_value)) is not None
      ]
      return ", ".join(rendered) if rendered else None
    if isinstance(value, (list, tuple, set)):
      rendered = [
        nested
        for item in value
        if (nested := self._stringify_artifact_source_value(item)) is not None
      ]
      return " | ".join(rendered) if rendered else None
    return str(value)

  @staticmethod
  def _set_summary_entry(summary: dict[str, Any], key: str, value: Any) -> None:
    normalized = FreqtradeArtifactBindingMixin._normalize_summary_value(key, value)
    if normalized is not None:
      summary[key] = normalized

  @staticmethod
  def _normalize_summary_value(key: str, value: Any) -> Any:
    if value in (None, "", [], {}):
      return None
    if key.endswith("_at"):
      return FreqtradeArtifactBindingMixin._normalize_timestamp(value)
    if key.endswith("_count"):
      return FreqtradeArtifactBindingMixin._coerce_count(value)
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
