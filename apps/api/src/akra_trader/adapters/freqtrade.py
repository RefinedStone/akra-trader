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

    summary, summary_source_path = self._summarize_artifact(path, kind)
    return BenchmarkArtifact(
      kind=kind,
      label=label,
      path=str(path),
      format=format_name,
      exists=exists,
      is_directory=is_directory,
      summary=summary,
      summary_source_path=summary_source_path,
    )

  def _summarize_artifact(
    self,
    path: Path,
    kind: str,
  ) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
      return {}, None
    if kind == "result_manifest":
      summary = self._extract_summary_from_json(path)
      return summary, str(path) if summary else None
    if kind == "result_snapshot":
      return self._summarize_result_snapshot(path)
    if kind == "result_snapshot_root":
      return self._summarize_result_root(path)
    return {}, None

  def _summarize_result_snapshot(self, path: Path) -> tuple[dict[str, Any], str | None]:
    summary: dict[str, Any] = {}
    source_path: str | None = None
    if path.suffix.lower() == ".json":
      snapshot_summary = self._extract_summary_from_json(path)
      if snapshot_summary:
        summary.update(snapshot_summary)
        source_path = str(path)

    manifest_path = self._find_related_manifest(path)
    if manifest_path is not None:
      manifest_summary = self._extract_summary_from_json(manifest_path)
      for key, value in manifest_summary.items():
        summary.setdefault(key, value)
      if source_path is None and manifest_summary:
        source_path = str(manifest_path)
    return summary, source_path

  def _summarize_result_root(self, root: Path) -> tuple[dict[str, Any], str | None]:
    if not root.is_dir():
      return {}, None

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
    source_path: str | None = None
    if snapshot_paths:
      summary, source_path = self._summarize_result_snapshot(snapshot_paths[-1])
    elif manifest_paths:
      manifest_summary = self._extract_summary_from_json(manifest_paths[-1])
      if manifest_summary:
        summary = manifest_summary
        source_path = str(manifest_paths[-1])

    if manifest_paths:
      summary.setdefault("manifest_count", len(manifest_paths))
    if snapshot_paths:
      summary.setdefault("snapshot_count", len(snapshot_paths))
    return summary, source_path

  def _extract_summary_from_json(self, path: Path) -> dict[str, Any]:
    payload = self._read_json_payload(path)
    if payload is None:
      return {}
    return self._summarize_freqtrade_payload(payload)

  def _summarize_freqtrade_payload(self, payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
      payload = next((item for item in payload if isinstance(item, dict)), None)
    if not isinstance(payload, dict):
      return {}

    candidates = self._build_summary_candidates(payload)
    summary: dict[str, Any] = {}

    self._set_summary_entry(summary, "strategy_name", self._extract_strategy_name(payload, candidates))
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
      self._lookup_value(candidates, "backtest_start_time", "backtest_start_at", "backtest_start"),
    )
    self._set_summary_entry(
      summary,
      "backtest_end_at",
      self._lookup_value(candidates, "backtest_end_time", "backtest_end_at", "backtest_end"),
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
      self._lookup_value(candidates, "profit_total_pct", "total_profit_pct", "profit_pct"),
    )
    self._set_summary_entry(
      summary,
      "profit_total_abs",
      self._lookup_value(candidates, "profit_total_abs", "total_profit_abs", "profit_total"),
    )
    self._set_summary_entry(
      summary,
      "max_drawdown_pct",
      self._lookup_value(candidates, "max_drawdown_pct", "absolute_drawdown_pct", "drawdown_pct"),
    )
    self._set_summary_entry(
      summary,
      "market_change_pct",
      self._lookup_value(candidates, "market_change_pct", "market_change"),
    )
    return summary

  @staticmethod
  def _build_summary_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for key in ("summary", "metadata", "backtest_result", "result"):
      value = payload.get(key)
      if isinstance(value, dict):
        candidates.append(value)

    strategy_comparison = payload.get("strategy_comparison")
    if isinstance(strategy_comparison, list):
      first_comparison = next((item for item in strategy_comparison if isinstance(item, dict)), None)
      if first_comparison is not None:
        candidates.append(first_comparison)

    strategy = payload.get("strategy")
    if isinstance(strategy, dict):
      nested_strategy = next(
        (
          {"strategy_name": name, **details}
          for name, details in strategy.items()
          if isinstance(details, dict)
        ),
        None,
      )
      if nested_strategy is not None:
        candidates.append(nested_strategy)
      else:
        candidates.append(strategy)

    candidates.append(payload)
    return candidates

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
