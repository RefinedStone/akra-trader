from __future__ import annotations

from datetime import UTC
from datetime import datetime

import pytest

from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.lineage import assess_rerun_validation
from akra_trader.lineage import build_dataset_boundary_contract


def _build_lineage(
  *,
  reproducibility_state: str,
  dataset_identity: str | None,
  sync_checkpoint_id: str | None,
) -> MarketDataLineage:
  return MarketDataLineage(
    provider="seeded",
    venue="binance",
    symbols=("BTC/USDT",),
    timeframe="5m",
    dataset_identity=dataset_identity,
    sync_checkpoint_id=sync_checkpoint_id,
    reproducibility_state=reproducibility_state,
    requested_start_at=datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
    requested_end_at=datetime(2025, 1, 1, 1, 0, tzinfo=UTC),
    effective_start_at=datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
    effective_end_at=datetime(2025, 1, 1, 1, 0, tzinfo=UTC),
    candle_count=13,
    sync_status="synced",
  )


def _build_run(
  *,
  run_id: str,
  mode: RunMode,
  lineage: MarketDataLineage,
  rerun_boundary_id: str,
) -> RunRecord:
  return RunRecord(
    config=RunConfig(
      run_id=run_id,
      mode=mode,
      strategy_id="ma_cross_v1",
      strategy_version="1.0.0",
      venue="binance",
      symbols=("BTC/USDT",),
      timeframe="5m",
      parameters={"short_window": 8, "long_window": 21},
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
    ),
    provenance=RunProvenance(
      market_data=lineage,
      rerun_boundary_id=rerun_boundary_id,
    ),
  )


@pytest.mark.parametrize(
  ("lineage", "expected_claim", "expected_boundary_id"),
  [
    (
      _build_lineage(
        reproducibility_state="pinned",
        dataset_identity="dataset-v1:exact",
        sync_checkpoint_id="checkpoint-group-v1:exact",
      ),
      "exact_dataset",
      "dataset-v1:exact",
    ),
    (
      _build_lineage(
        reproducibility_state="partial",
        dataset_identity=None,
        sync_checkpoint_id="checkpoint-group-v1:checkpoint",
      ),
      "checkpoint_window",
      "checkpoint-group-v1:checkpoint",
    ),
    (
      _build_lineage(
        reproducibility_state="range_only",
        dataset_identity=None,
        sync_checkpoint_id=None,
      ),
      "window_only",
      None,
    ),
    (
      _build_lineage(
        reproducibility_state="delegated",
        dataset_identity=None,
        sync_checkpoint_id=None,
      ),
      "delegated",
      None,
    ),
  ],
)
def test_build_dataset_boundary_contract_resolves_claims(
  lineage: MarketDataLineage,
  expected_claim: str,
  expected_boundary_id: str | None,
) -> None:
  contract = build_dataset_boundary_contract(lineage=lineage)

  assert contract is not None
  assert contract.contract_version == "dataset_boundary.v1"
  assert contract.validation_claim == expected_claim
  assert contract.boundary_id == expected_boundary_id
  assert contract.effective_start_at == lineage.effective_start_at
  assert contract.effective_end_at == lineage.effective_end_at


def test_assess_rerun_validation_reports_exact_match() -> None:
  lineage = _build_lineage(
    reproducibility_state="pinned",
    dataset_identity="dataset-v1:exact",
    sync_checkpoint_id="checkpoint-group-v1:exact",
  )
  source = _build_run(
    run_id="source",
    mode=RunMode.BACKTEST,
    lineage=lineage,
    rerun_boundary_id="rerun-v1:exact",
  )
  rerun = _build_run(
    run_id="rerun",
    mode=RunMode.BACKTEST,
    lineage=lineage,
    rerun_boundary_id="rerun-v1:exact",
  )

  assessment = assess_rerun_validation(
    source_run=source,
    rerun=rerun,
    expected_boundary_id="rerun-v1:exact",
  )

  assert assessment.status == "matched"
  assert assessment.category == "exact_match"


def test_assess_rerun_validation_reports_mode_translation() -> None:
  lineage = _build_lineage(
    reproducibility_state="pinned",
    dataset_identity="dataset-v1:exact",
    sync_checkpoint_id="checkpoint-group-v1:exact",
  )
  source = _build_run(
    run_id="source",
    mode=RunMode.BACKTEST,
    lineage=lineage,
    rerun_boundary_id="rerun-v1:backtest",
  )
  rerun = _build_run(
    run_id="rerun",
    mode=RunMode.PAPER,
    lineage=lineage,
    rerun_boundary_id="rerun-v1:paper",
  )

  assessment = assess_rerun_validation(
    source_run=source,
    rerun=rerun,
    expected_boundary_id="rerun-v1:backtest",
  )

  assert assessment.status == "drifted"
  assert assessment.category == "mode_translation"


def test_assess_rerun_validation_reports_dataset_change() -> None:
  source = _build_run(
    run_id="source",
    mode=RunMode.BACKTEST,
    lineage=_build_lineage(
      reproducibility_state="pinned",
      dataset_identity="dataset-v1:source",
      sync_checkpoint_id="checkpoint-group-v1:source",
    ),
    rerun_boundary_id="rerun-v1:source",
  )
  rerun = _build_run(
    run_id="rerun",
    mode=RunMode.BACKTEST,
    lineage=_build_lineage(
      reproducibility_state="pinned",
      dataset_identity="dataset-v1:target",
      sync_checkpoint_id="checkpoint-group-v1:source",
    ),
    rerun_boundary_id="rerun-v1:target",
  )

  assessment = assess_rerun_validation(
    source_run=source,
    rerun=rerun,
    expected_boundary_id="rerun-v1:source",
  )

  assert assessment.status == "drifted"
  assert assessment.category == "dataset_changed"
