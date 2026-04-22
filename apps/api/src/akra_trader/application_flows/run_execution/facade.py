from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Iterable

from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord

from . import launches
from . import queries
from . import reruns
from . import support


@dataclass(slots=True)
class RunExecutionFlow:
  app: Any

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: Iterable[str] = (),
  ) -> list[RunRecord]:
    return queries.list_runs(
      self,
      mode,
      strategy_id=strategy_id,
      strategy_version=strategy_version,
      rerun_boundary_id=rerun_boundary_id,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
      dataset_identity=dataset_identity,
      tags=tags,
    )

  def get_run(self, run_id: str) -> RunRecord | None:
    return queries.get_run(self, run_id)

  def rerun_backtest_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return reruns.rerun_backtest_from_boundary(self, rerun_boundary_id=rerun_boundary_id)

  def rerun_sandbox_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return reruns.rerun_sandbox_from_boundary(self, rerun_boundary_id=rerun_boundary_id)

  def rerun_paper_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return reruns.rerun_paper_from_boundary(self, rerun_boundary_id=rerun_boundary_id)

  def run_backtest(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return launches.run_backtest(
      self,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def start_sandbox_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return launches.start_sandbox_run(
      self,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def start_paper_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return launches.start_paper_run(
      self,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def start_sandbox_session(self, **kwargs: Any) -> RunRecord:
    return launches.start_sandbox_session(self, **kwargs)

  def start_paper_session(self, **kwargs: Any) -> RunRecord:
    return launches.start_paper_session(self, **kwargs)

  def start_native_session(self, **kwargs: Any) -> RunRecord:
    return launches.start_native_session(self, **kwargs)

  def resolve_rerun_source(self, *, rerun_boundary_id: str) -> RunRecord:
    return reruns.resolve_rerun_source(self, rerun_boundary_id=rerun_boundary_id)

  def rerun_from_boundary(
    self,
    *,
    rerun_boundary_id: str,
    target_mode: RunMode,
    requested_mode_label: str,
  ) -> RunRecord:
    return reruns.rerun_from_boundary(
      self,
      rerun_boundary_id=rerun_boundary_id,
      target_mode=target_mode,
      requested_mode_label=requested_mode_label,
    )

  def persist_explicit_rerun(
    self,
    *,
    rerun: RunRecord,
    source_run: RunRecord,
    rerun_boundary_id: str,
    requested_mode_label: str,
    preview_window_note: str | None = None,
  ) -> RunRecord:
    return reruns.persist_explicit_rerun(
      self,
      rerun=rerun,
      source_run=source_run,
      rerun_boundary_id=rerun_boundary_id,
      requested_mode_label=requested_mode_label,
      preview_window_note=preview_window_note,
    )

  def resolve_rerun_parameters(self, run: RunRecord) -> dict:
    return support.resolve_rerun_parameters(run)

  def resolve_rerun_start_at(self, run: RunRecord) -> datetime | None:
    return support.resolve_rerun_start_at(run)

  def resolve_rerun_end_at(self, run: RunRecord) -> datetime | None:
    return support.resolve_rerun_end_at(run)

  def resolve_preview_rerun_window(self, run: RunRecord) -> tuple[datetime | None, datetime | None, int | None]:
    return support.resolve_preview_rerun_window(run)
