from __future__ import annotations

from copy import deepcopy
from datetime import datetime

from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord


def resolve_rerun_parameters(run: RunRecord) -> dict:
  strategy = run.provenance.strategy
  if strategy is not None:
    return deepcopy(strategy.parameter_snapshot.resolved)
  return deepcopy(run.config.parameters)


def resolve_rerun_start_at(run: RunRecord) -> datetime | None:
  market_data = run.provenance.market_data
  if market_data is None:
    return run.config.start_at
  return (
    market_data.effective_start_at
    or market_data.requested_start_at
    or run.config.start_at
  )


def resolve_rerun_end_at(run: RunRecord) -> datetime | None:
  market_data = run.provenance.market_data
  if market_data is None:
    return run.config.end_at
  return (
    market_data.effective_end_at
    or market_data.requested_end_at
    or run.config.end_at
  )


def resolve_preview_rerun_window(run: RunRecord) -> tuple[datetime | None, datetime | None, int | None]:
  market_data = run.provenance.market_data
  if (
    run.config.mode in {RunMode.SANDBOX, RunMode.PAPER}
    and run.config.start_at is None
    and run.config.end_at is None
    and market_data is not None
    and market_data.candle_count > 0
  ):
    return None, None, market_data.candle_count
  return (
    resolve_rerun_start_at(run),
    resolve_rerun_end_at(run),
    None,
  )
