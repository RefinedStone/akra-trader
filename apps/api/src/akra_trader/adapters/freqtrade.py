from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from pathlib import Path
import shutil
import subprocess

from akra_trader.adapters.references import ReferenceCatalog
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunProvenance
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
    )

  def execute_backtest(self, run: RunRecord, metadata: StrategyMetadata) -> RunRecord:
    prepared = self.prepare_backtest(run.config, metadata)
    run.provenance = RunProvenance(
      lane="reference",
      reference_id=prepared.reference_id,
      reference_version=prepared.reference_version,
      integration_mode=prepared.integration_mode,
      working_directory=prepared.working_directory,
      external_command=tuple(prepared.command),
      market_data=MarketDataLineage(
        provider="freqtrade_reference",
        venue=run.config.venue,
        symbols=run.config.symbols,
        timeframe=run.config.timeframe,
        requested_start_at=run.config.start_at,
        requested_end_at=run.config.end_at,
        sync_status="delegated",
      ),
    )
    run.notes.append(f"Prepared NFI reference command: {' '.join(prepared.command)}")

    if shutil.which("freqtrade") is None:
      run.status = RunStatus.FAILED
      run.notes.append(
        "freqtrade runtime was not found in PATH. Install freqtrade and the NFI "
        "dependencies to execute this reference strategy."
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
    run.status = RunStatus.COMPLETED if process.returncode == 0 else RunStatus.FAILED
    run.ended_at = datetime.now(UTC)
    return run

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
