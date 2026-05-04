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

from akra_trader.adapters.freqtrade_artifact_summary import FreqtradeArtifactSummaryMixin
from akra_trader.adapters.freqtrade_benchmark_story import FreqtradeBenchmarkStoryMixin
from akra_trader.adapters.freqtrade_artifact_bindings import FreqtradeArtifactBindingMixin
from akra_trader.adapters.freqtrade_zip_summaries import FreqtradeZipSummaryMixin


@dataclass(frozen=True)
class PreparedCommand:
  command: list[str]
  download_command: list[str] | None
  working_directory: str
  reference_id: str
  reference_version: str | None
  integration_mode: str
  reference: ReferenceSource
  artifact_roots: tuple[str, ...]


class FreqtradeReferenceAdapter(
  FreqtradeArtifactSummaryMixin,
  FreqtradeBenchmarkStoryMixin,
  FreqtradeArtifactBindingMixin,
  FreqtradeZipSummaryMixin,
):
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
    symbols = tuple(getattr(config, "symbols", ()) or ())
    timeframe = getattr(config, "timeframe", None)
    initial_cash = getattr(config, "initial_cash", None)
    fee_rate = getattr(config, "fee_rate", None)
    common_config_args = [
      "--user-data-dir=user_data",
      "--config=configs/exampleconfig.json",
      "--config=configs/exampleconfig_secret.json",
      f"--config=configs/trading_mode-{mode}.json",
      f"--config=configs/blacklist-{exchange}.json",
    ]
    command = [
      "freqtrade",
      "backtesting",
      f"--strategy={metadata.entrypoint}",
      f"--timerange={timerange}",
      *common_config_args,
      f"--config=configs/pairlist-backtest-static-{exchange}-{mode}-usdt.json",
      "--breakdown=day",
      "--export=signals",
    ]
    if symbols:
      command.extend(["--pairs", *symbols])
    if timeframe:
      command.append(f"--timeframe={timeframe}")
    if initial_cash is not None:
      command.append(f"--dry-run-wallet={initial_cash}")
    if fee_rate is not None:
      command.append(f"--fee={fee_rate}")
    download_command = None
    if symbols:
      download_command = [
        "freqtrade",
        "download-data",
        *common_config_args,
        f"--exchange={exchange}",
        f"--timerange={timerange}",
        "--pairs",
        *symbols,
        "--timeframes",
        *self._resolve_download_timeframes(timeframe),
      ]
    return PreparedCommand(
      command=command,
      download_command=download_command,
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
    run.provenance.benchmark_artifacts = ()
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

    if prepared.download_command is not None:
      run.notes.append(
        "Prepared NFI reference data sync command: "
        + " ".join(prepared.download_command)
      )
      download_process = subprocess.run(
        prepared.download_command,
        cwd=prepared.working_directory,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
      )
      download_stdout = download_process.stdout.strip()
      download_stderr = download_process.stderr.strip()
      if download_stdout:
        run.notes.append(download_stdout)
      if download_stderr:
        run.notes.append(download_stderr)
      if download_process.returncode != 0:
        run.status = RunStatus.FAILED
        run.notes.append(
          "Reference backtest data sync failed before execution. "
          "Check the Freqtrade download-data log and retry the backtest."
        )
        run.provenance.artifact_paths = self._resolve_post_run_artifact_paths(
          artifact_roots=prepared.artifact_roots,
          existing_artifacts=existing_artifacts,
          process_succeeded=False,
          reported_artifact_paths=(),
        )
        run.provenance.benchmark_artifacts = self._build_benchmark_artifacts(
          run.provenance.artifact_paths
        )
        run.ended_at = datetime.now(UTC)
        return run

    process = subprocess.run(
      prepared.command,
      cwd=prepared.working_directory,
      check=False,
      capture_output=True,
      text=True,
      shell=False,
    )
    stdout = process.stdout.strip()
    stderr = process.stderr.strip()
    run.notes.append(stdout)
    if stderr:
      run.notes.append(stderr)
    reported_artifact_paths = self._resolve_reported_artifact_paths(
      "\n".join(part for part in (stdout, stderr) if part),
      Path(prepared.working_directory),
    )
    resolved_artifact_paths = self._resolve_post_run_artifact_paths(
      artifact_roots=prepared.artifact_roots,
      existing_artifacts=existing_artifacts,
      process_succeeded=process.returncode == 0,
      reported_artifact_paths=reported_artifact_paths,
    )
    run.provenance.artifact_paths = resolved_artifact_paths
    run.provenance.benchmark_artifacts = self._build_benchmark_artifacts(resolved_artifact_paths)
    run.status = RunStatus.COMPLETED if process.returncode == 0 else RunStatus.FAILED
    if run.status == RunStatus.FAILED and "No data found" in "\n".join((stdout, stderr)):
      run.notes.append(
        "Reference backtest data is missing for the requested Freqtrade timerange. "
        "Download the pair/timeframe data into reference/NostalgiaForInfinity/user_data/data "
        "and re-run the backtest."
      )
    run.ended_at = datetime.now(UTC)
    return run

  def _resolve_post_run_artifact_paths(
    self,
    *,
    artifact_roots: tuple[str, ...],
    existing_artifacts: set[str],
    process_succeeded: bool,
    reported_artifact_paths: tuple[str, ...],
  ) -> tuple[str, ...]:
    if reported_artifact_paths:
      return reported_artifact_paths
    collected_artifacts = self._collect_artifacts(artifact_roots)
    new_artifacts = sorted(collected_artifacts - existing_artifacts)
    if new_artifacts:
      return tuple(new_artifacts)
    if not process_succeeded:
      return tuple(
        artifact_root
        for artifact_root in artifact_roots
        if Path(artifact_root).exists() and Path(artifact_root).name.lower() != "backtest_results"
      )
    return self._resolve_artifact_paths(
      artifact_roots=artifact_roots,
      existing_artifacts=existing_artifacts,
    )

  @staticmethod
  def _resolve_download_timeframes(base_timeframe: str | None) -> tuple[str, ...]:
    return tuple(
      dict.fromkeys(
        timeframe
        for timeframe in (
          base_timeframe,
          "15m",
          "1h",
          "4h",
          "1d",
        )
        if timeframe
      )
    )

  @staticmethod
  def _resolve_reported_artifact_paths(process_output: str, working_directory: Path) -> tuple[str, ...]:
    reported_paths: list[str] = []
    patterns = (
      r"Loading backtest result from (?P<path>[^\n]+)",
      r"dumping (?:json|joblib) to \"(?P<path>[^\"]+)\"",
    )
    for pattern in patterns:
      for match in re.finditer(pattern, process_output):
        raw_path = match.group("path").strip().strip("\"")
        if not raw_path:
          continue
        path = Path(raw_path)
        resolved_path = path if path.is_absolute() else working_directory / path
        if resolved_path.exists():
          reported_paths.append(str(resolved_path))
    return tuple(dict.fromkeys(reported_paths))
