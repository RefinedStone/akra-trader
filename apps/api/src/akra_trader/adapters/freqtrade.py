from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from pathlib import Path
import os
import shutil
import subprocess

from akra_trader.adapters.references import ReferenceCatalog
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
    run.provenance.artifact_paths = self._resolve_artifact_paths(
      artifact_roots=prepared.artifact_roots,
      existing_artifacts=existing_artifacts,
    )
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
