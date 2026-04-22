from __future__ import annotations

from akra_trader.application_support.run_surfaces import _ensure_run_action_allowed
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.lineage import assess_rerun_validation

from .support import resolve_preview_rerun_window
from .support import resolve_rerun_end_at
from .support import resolve_rerun_parameters
from .support import resolve_rerun_start_at


def rerun_backtest_from_boundary(flow, *, rerun_boundary_id: str) -> RunRecord:
  return rerun_from_boundary(
    flow,
    rerun_boundary_id=rerun_boundary_id,
    target_mode=RunMode.BACKTEST,
    requested_mode_label=RunMode.BACKTEST.value,
  )


def rerun_sandbox_from_boundary(flow, *, rerun_boundary_id: str) -> RunRecord:
  return rerun_from_boundary(
    flow,
    rerun_boundary_id=rerun_boundary_id,
    target_mode=RunMode.SANDBOX,
    requested_mode_label=RunMode.SANDBOX.value,
  )


def rerun_paper_from_boundary(flow, *, rerun_boundary_id: str) -> RunRecord:
  return rerun_from_boundary(
    flow,
    rerun_boundary_id=rerun_boundary_id,
    target_mode=RunMode.PAPER,
    requested_mode_label=RunMode.PAPER.value,
  )


def resolve_rerun_source(flow, *, rerun_boundary_id: str) -> RunRecord:
  candidates = flow.app._runs.list_runs(rerun_boundary_id=rerun_boundary_id)
  if not candidates:
    raise LookupError(f"Rerun boundary not found: {rerun_boundary_id}")
  completed = [run for run in candidates if run.status == RunStatus.COMPLETED]
  return completed[0] if completed else candidates[0]


def rerun_from_boundary(
  flow,
  *,
  rerun_boundary_id: str,
  target_mode: RunMode,
  requested_mode_label: str,
) -> RunRecord:
  app = flow.app
  source_run = resolve_rerun_source(flow, rerun_boundary_id=rerun_boundary_id)
  _ensure_run_action_allowed(
    run=source_run,
    capabilities=app.get_run_surface_capabilities(),
    action_key=f"rerun_{target_mode.value}",
  )
  if len(source_run.config.symbols) != 1:
    raise ValueError(f"Explicit rerun currently supports only single-symbol {requested_mode_label} runs.")
  app._migrate_legacy_preset_from_run(source_run)

  rerun_start_at = resolve_rerun_start_at(source_run)
  rerun_end_at = resolve_rerun_end_at(source_run)
  rerun_parameters = resolve_rerun_parameters(source_run)
  symbol = source_run.config.symbols[0]
  session_window_note: str | None = None

  if target_mode == RunMode.BACKTEST:
    rerun = flow.run_backtest(
      strategy_id=source_run.config.strategy_id,
      symbol=symbol,
      timeframe=source_run.config.timeframe,
      initial_cash=source_run.config.initial_cash,
      fee_rate=source_run.config.fee_rate,
      slippage_bps=source_run.config.slippage_bps,
      parameters=rerun_parameters,
      start_at=rerun_start_at,
      end_at=rerun_end_at,
      tags=source_run.provenance.experiment.tags,
      preset_id=source_run.provenance.experiment.preset_id,
      benchmark_family=source_run.provenance.experiment.benchmark_family,
    )
  elif target_mode in {RunMode.SANDBOX, RunMode.PAPER}:
    preview_start_at, preview_end_at, preview_replay_bars = resolve_preview_rerun_window(source_run)
    if target_mode == RunMode.SANDBOX:
      if preview_replay_bars is None:
        session_window_note = (
          "Sandbox rerun restored the worker session from the stored effective market-data window."
        )
      else:
        session_window_note = (
          "Sandbox rerun restored the stored worker-session priming window."
        )
      rerun = flow.start_sandbox_session(
        strategy_id=source_run.config.strategy_id,
        symbol=symbol,
        timeframe=source_run.config.timeframe,
        initial_cash=source_run.config.initial_cash,
        fee_rate=source_run.config.fee_rate,
        slippage_bps=source_run.config.slippage_bps,
        parameters=rerun_parameters,
        replay_bars=preview_replay_bars,
        start_at=preview_start_at,
        end_at=preview_end_at,
        tags=source_run.provenance.experiment.tags,
        preset_id=source_run.provenance.experiment.preset_id,
        benchmark_family=source_run.provenance.experiment.benchmark_family,
      )
    else:
      if preview_replay_bars is None:
        session_window_note = "Paper rerun seeded the current paper session from the stored effective market-data window."
      else:
        session_window_note = "Paper rerun seeded the current paper session from the stored priming window."
      rerun = flow.start_paper_session(
        strategy_id=source_run.config.strategy_id,
        symbol=symbol,
        timeframe=source_run.config.timeframe,
        initial_cash=source_run.config.initial_cash,
        fee_rate=source_run.config.fee_rate,
        slippage_bps=source_run.config.slippage_bps,
        parameters=rerun_parameters,
        replay_bars=preview_replay_bars,
        start_at=preview_start_at,
        end_at=preview_end_at,
        tags=source_run.provenance.experiment.tags,
        preset_id=source_run.provenance.experiment.preset_id,
        benchmark_family=source_run.provenance.experiment.benchmark_family,
      )
  else:
    raise ValueError(f"Unsupported rerun target mode: {target_mode.value}")

  return persist_explicit_rerun(
    flow,
    rerun=rerun,
    source_run=source_run,
    rerun_boundary_id=rerun_boundary_id,
    requested_mode_label=requested_mode_label,
    preview_window_note=session_window_note,
  )


def persist_explicit_rerun(
  flow,
  *,
  rerun: RunRecord,
  source_run: RunRecord,
  rerun_boundary_id: str,
  requested_mode_label: str,
  preview_window_note: str | None = None,
) -> RunRecord:
  rerun.provenance.rerun_source_run_id = source_run.config.run_id
  rerun.provenance.rerun_target_boundary_id = rerun_boundary_id
  validation = assess_rerun_validation(
    source_run=source_run,
    rerun=rerun,
    expected_boundary_id=rerun_boundary_id,
  )
  rerun.provenance.rerun_match_status = validation.status
  rerun.provenance.rerun_validation_category = validation.category
  rerun.provenance.rerun_validation_summary = validation.summary
  rerun.notes.insert(
    0,
    f"Explicit {requested_mode_label} rerun from boundary {rerun_boundary_id} using source run {source_run.config.run_id}.",
  )
  if rerun.config.mode in {RunMode.SANDBOX, RunMode.PAPER} and preview_window_note is not None:
    rerun.notes.insert(
      1,
      preview_window_note,
    )
  if rerun.provenance.rerun_match_status == "matched":
    rerun.notes.append(validation.summary)
  elif rerun.provenance.rerun_match_status == "unavailable":
    rerun.notes.append(validation.summary)
  else:
    rerun.notes.append(
      "Explicit rerun drifted from the stored rerun boundary. "
      f"Expected {rerun_boundary_id}, got {rerun.provenance.rerun_boundary_id or 'unavailable'}."
    )
    rerun.notes.append(validation.summary)
  return flow.app._runs.save_run(rerun)
