from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path
from typing import Callable
from typing import Protocol
from uuid import uuid4

import ccxt
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import SyncCheckpoint
from akra_trader.domain.models import SyncFailure
from akra_trader.lineage import build_candle_dataset_identity
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.lineage import build_sync_checkpoint_identity
from akra_trader.ports import MarketDataPort


from akra_trader.adapters.binance_schema import _TIMEFRAME_SECONDS
from akra_trader.adapters.binance_schema import market_candles
from akra_trader.adapters.binance_schema import market_ingestion_jobs
from akra_trader.adapters.binance_schema import market_lineage_history
from akra_trader.adapters.binance_schema import market_sync_failures
from akra_trader.adapters.binance_schema import market_sync_state
from akra_trader.adapters.binance_schema import CandleCoverage
from akra_trader.adapters.binance_schema import QualitySnapshot
from akra_trader.adapters.binance_schema import SyncState


class CcxtMarketDataStorageMixin:
  def _read_coverage(self, *, symbol: str, timeframe: str) -> CandleCoverage:
    statement = select(
      func.count().label("candle_count"),
      func.min(market_candles.c.timestamp).label("first_timestamp"),
      func.max(market_candles.c.timestamp).label("last_timestamp"),
      func.max(market_candles.c.ingested_at).label("latest_ingested_at"),
    ).where(
      and_(
        market_candles.c.venue == self._venue,
        market_candles.c.symbol == symbol,
        market_candles.c.timeframe == timeframe,
      )
    )
    with self._engine.connect() as connection:
      row = connection.execute(statement).mappings().one()
    return CandleCoverage(
      candle_count=int(row["candle_count"] or 0),
      first_timestamp=self._ensure_utc(row["first_timestamp"]),
      last_timestamp=self._ensure_utc(row["last_timestamp"]),
      latest_ingested_at=self._ensure_utc(row["latest_ingested_at"]),
    )

  def _read_sync_state(self, *, symbol: str, timeframe: str) -> SyncState | None:
    statement = select(market_sync_state).where(
      and_(
        market_sync_state.c.venue == self._venue,
        market_sync_state.c.symbol == symbol,
        market_sync_state.c.timeframe == timeframe,
      )
    )
    with self._engine.connect() as connection:
      row = connection.execute(statement).mappings().first()
    if row is None:
      return None
    checkpoint = None
    if row["checkpoint_id"] is not None and row["checkpoint_recorded_at"] is not None:
      checkpoint = SyncCheckpoint(
        checkpoint_id=row["checkpoint_id"],
        recorded_at=self._ensure_utc(row["checkpoint_recorded_at"]),
        candle_count=int(row["checkpoint_candle_count"] or 0),
        first_timestamp=self._ensure_utc(row["checkpoint_first_timestamp"]),
        last_timestamp=self._ensure_utc(row["checkpoint_last_timestamp"]),
        contiguous_missing_candles=int(row["checkpoint_contiguous_missing_candles"] or 0),
      )
    return SyncState(
      sync_status=row["sync_status"],
      last_sync_at=self._ensure_utc(row["last_sync_at"]),
      last_error=row["last_error"],
      checkpoint=checkpoint,
    )

  def _record_sync_state(
    self,
    *,
    symbol: str,
    timeframe: str,
    sync_status: str,
    last_error: str | None,
  ) -> None:
    row = {
      "venue": self._venue,
      "symbol": symbol,
      "timeframe": timeframe,
      "sync_status": sync_status,
      "last_sync_at": self._clock(),
      "last_error": last_error,
    }
    if sync_status == "synced":
      checkpoint = self._build_sync_checkpoint(
        symbol=symbol,
        timeframe=timeframe,
        coverage=self._read_coverage(symbol=symbol, timeframe=timeframe),
      )
      if checkpoint is not None:
        row.update(
          {
            "checkpoint_id": checkpoint.checkpoint_id,
            "checkpoint_recorded_at": checkpoint.recorded_at,
            "checkpoint_first_timestamp": checkpoint.first_timestamp,
            "checkpoint_last_timestamp": checkpoint.last_timestamp,
            "checkpoint_candle_count": checkpoint.candle_count,
            "checkpoint_contiguous_missing_candles": checkpoint.contiguous_missing_candles,
          }
        )
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(market_sync_state.c.symbol).where(
          and_(
            market_sync_state.c.venue == self._venue,
            market_sync_state.c.symbol == symbol,
            market_sync_state.c.timeframe == timeframe,
          )
        )
      ).first()
      if existing is None:
        connection.execute(insert(market_sync_state).values(**row))
      else:
        connection.execute(
          update(market_sync_state)
          .where(
            and_(
              market_sync_state.c.venue == self._venue,
              market_sync_state.c.symbol == symbol,
              market_sync_state.c.timeframe == timeframe,
            )
          )
          .values(**row)
        )

  def _record_failure_event(
    self,
    *,
    symbol: str,
    timeframe: str,
    operation: str,
    error: str,
  ) -> None:
    with self._engine.begin() as connection:
      connection.execute(
        insert(market_sync_failures).values(
          venue=self._venue,
          symbol=symbol,
          timeframe=timeframe,
          operation=operation,
          failed_at=self._clock(),
          error=error,
        )
      )

  def _new_ingestion_job_id(self) -> str:
    return f"ingest|{uuid4().hex}"

  def _new_lineage_history_id(self) -> str:
    return f"lineage|{uuid4().hex}"

  def _finalize_ingestion_job(
    self,
    *,
    job_id: str,
    symbol: str,
    timeframe: str,
    operation: str,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    requested_start_at: datetime | None,
    requested_end_at: datetime | None,
    requested_limit: int | None,
    fetched_candle_count: int,
    last_error: str | None,
  ) -> None:
    lineage_record = self._record_lineage_history(
      symbol=symbol,
      timeframe=timeframe,
      recorded_at=finished_at,
      source_job_id=job_id,
    )
    self._record_ingestion_job(
      job_id=job_id,
      symbol=symbol,
      timeframe=timeframe,
      operation=operation,
      status=status,
      started_at=started_at,
      finished_at=finished_at,
      requested_start_at=requested_start_at,
      requested_end_at=requested_end_at,
      requested_limit=requested_limit,
      fetched_candle_count=fetched_candle_count,
      last_error=last_error,
      lineage_record=lineage_record,
    )

  def _record_lineage_history(
    self,
    *,
    symbol: str,
    timeframe: str,
    recorded_at: datetime,
    source_job_id: str | None,
  ) -> MarketDataLineageHistoryRecord:
    record = self._build_lineage_history_record(
      symbol=symbol,
      timeframe=timeframe,
      recorded_at=recorded_at,
      source_job_id=source_job_id,
    )
    with self._engine.begin() as connection:
      connection.execute(
        insert(market_lineage_history).values(
          history_id=record.history_id,
          source_job_id=record.source_job_id,
          provider=record.provider,
          venue=record.venue,
          symbol=record.symbol,
          timeframe=record.timeframe,
          recorded_at=record.recorded_at,
          sync_status=record.sync_status,
          validation_claim=record.validation_claim,
          reproducibility_state=record.reproducibility_state,
          boundary_id=record.boundary_id,
          checkpoint_id=record.checkpoint_id,
          first_timestamp=record.first_timestamp,
          last_timestamp=record.last_timestamp,
          candle_count=record.candle_count,
          lag_seconds=record.lag_seconds,
          last_sync_at=record.last_sync_at,
          failure_count_24h=record.failure_count_24h,
          contiguous_missing_candles=record.contiguous_missing_candles,
          gap_window_count=record.gap_window_count,
          last_error=record.last_error,
          issues_json=json.dumps(list(record.issues)),
        )
      )
    return record

  def _build_lineage_history_record(
    self,
    *,
    symbol: str,
    timeframe: str,
    recorded_at: datetime,
    source_job_id: str | None,
  ) -> MarketDataLineageHistoryRecord:
    quality = self._build_quality_snapshot(symbol=symbol, timeframe=timeframe)
    backfill = self._build_backfill_snapshot(
      symbol=symbol,
      timeframe=timeframe,
      coverage=quality.coverage,
    )
    recent_failures = self._read_recent_failures(symbol=symbol, timeframe=timeframe)
    failure_count_24h = self._count_failures_since(
      symbol=symbol,
      timeframe=timeframe,
      since=self._clock() - timedelta(hours=24),
    )
    sync_checkpoint = quality.sync_state.checkpoint if quality.sync_state is not None else None
    if sync_checkpoint is None and quality.coverage.candle_count > 0:
      sync_checkpoint = self._build_sync_checkpoint(
        symbol=symbol,
        timeframe=timeframe,
        coverage=quality.coverage,
        contiguous_missing_candles=backfill.contiguous_missing_candles,
        recorded_at=quality.coverage.latest_ingested_at or recorded_at,
      )
    issues = self._build_status_issues(
      timeframe=timeframe,
      quality=quality,
      backfill=backfill,
      recent_failures=recent_failures,
      failure_count_24h=failure_count_24h,
    )
    lineage = MarketDataLineage(
      provider=self._provider,
      venue=self._venue,
      symbols=(symbol,),
      timeframe=timeframe,
      dataset_identity=None,
      sync_checkpoint_id=sync_checkpoint.checkpoint_id if sync_checkpoint is not None else None,
      reproducibility_state="range_only",
      effective_start_at=quality.coverage.first_timestamp,
      effective_end_at=quality.coverage.last_timestamp,
      candle_count=quality.coverage.candle_count,
      sync_status=quality.sync_status,
      last_sync_at=quality.sync_state.last_sync_at if quality.sync_state is not None else None,
      issues=issues,
    )
    dataset_boundary = build_dataset_boundary_contract(lineage=lineage)
    return MarketDataLineageHistoryRecord(
      history_id=self._new_lineage_history_id(),
      source_job_id=source_job_id,
      provider=self._provider,
      venue=self._venue,
      symbol=symbol,
      timeframe=timeframe,
      recorded_at=recorded_at,
      sync_status=quality.sync_status,
      validation_claim=dataset_boundary.validation_claim if dataset_boundary is not None else "window_only",
      reproducibility_state=lineage.reproducibility_state,
      boundary_id=dataset_boundary.boundary_id if dataset_boundary is not None else None,
      checkpoint_id=sync_checkpoint.checkpoint_id if sync_checkpoint is not None else None,
      dataset_boundary=dataset_boundary,
      first_timestamp=quality.coverage.first_timestamp,
      last_timestamp=quality.coverage.last_timestamp,
      candle_count=quality.coverage.candle_count,
      lag_seconds=quality.lag_seconds,
      last_sync_at=quality.sync_state.last_sync_at if quality.sync_state is not None else None,
      failure_count_24h=failure_count_24h,
      contiguous_missing_candles=backfill.contiguous_missing_candles,
      gap_window_count=len(backfill.gap_windows),
      last_error=quality.sync_state.last_error if quality.sync_state is not None else None,
      issues=issues,
    )

  def _record_ingestion_job(
    self,
    *,
    job_id: str,
    symbol: str,
    timeframe: str,
    operation: str,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    requested_start_at: datetime | None,
    requested_end_at: datetime | None,
    requested_limit: int | None,
    fetched_candle_count: int,
    last_error: str | None,
    lineage_record: MarketDataLineageHistoryRecord,
  ) -> None:
    duration_ms = max(int((finished_at - started_at).total_seconds() * 1000), 0)
    with self._engine.begin() as connection:
      connection.execute(
        insert(market_ingestion_jobs).values(
          job_id=job_id,
          provider=self._provider,
          venue=self._venue,
          symbol=symbol,
          timeframe=timeframe,
          operation=operation,
          status=status,
          started_at=started_at,
          finished_at=finished_at,
          duration_ms=duration_ms,
          fetched_candle_count=fetched_candle_count,
          validation_claim=lineage_record.validation_claim,
          boundary_id=lineage_record.boundary_id,
          checkpoint_id=lineage_record.checkpoint_id,
          lineage_history_id=lineage_record.history_id,
          requested_start_at=requested_start_at,
          requested_end_at=requested_end_at,
          requested_limit=requested_limit,
          last_error=last_error,
        )
      )

  def _read_recent_failures(
    self,
    *,
    symbol: str,
    timeframe: str,
    limit: int = 3,
  ) -> tuple[SyncFailure, ...]:
    statement = (
      select(market_sync_failures)
      .where(
        and_(
          market_sync_failures.c.venue == self._venue,
          market_sync_failures.c.symbol == symbol,
          market_sync_failures.c.timeframe == timeframe,
        )
      )
      .order_by(market_sync_failures.c.failed_at.desc(), market_sync_failures.c.failure_id.desc())
      .limit(limit)
    )
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return tuple(
      SyncFailure(
        failed_at=self._ensure_utc(row["failed_at"]),
        operation=row["operation"],
        error=row["error"],
      )
      for row in rows
    )

  def _count_failures_since(
    self,
    *,
    symbol: str,
    timeframe: str,
    since: datetime,
  ) -> int:
    statement = select(func.count()).where(
      and_(
        market_sync_failures.c.venue == self._venue,
        market_sync_failures.c.symbol == symbol,
        market_sync_failures.c.timeframe == timeframe,
        market_sync_failures.c.failed_at >= since,
      )
    )
    with self._engine.connect() as connection:
      return int(connection.execute(statement).scalar_one())

  def _row_to_lineage_history_record(self, row: dict) -> MarketDataLineageHistoryRecord:
    issues = tuple(json.loads(row["issues_json"])) if row["issues_json"] else ()
    dataset_boundary = None
    if row["boundary_id"] is not None or row["checkpoint_id"] is not None or row["candle_count"]:
      dataset_boundary = build_dataset_boundary_contract(
        lineage=MarketDataLineage(
          provider=row["provider"],
          venue=row["venue"],
          symbols=(row["symbol"],),
          timeframe=row["timeframe"],
          dataset_identity=None,
          sync_checkpoint_id=row["checkpoint_id"],
          reproducibility_state=row["reproducibility_state"] or "range_only",
          effective_start_at=self._ensure_utc(row["first_timestamp"]),
          effective_end_at=self._ensure_utc(row["last_timestamp"]),
          candle_count=int(row["candle_count"] or 0),
          sync_status=row["sync_status"],
          last_sync_at=self._ensure_utc(row["last_sync_at"]),
          issues=issues,
        )
      )
    return MarketDataLineageHistoryRecord(
      history_id=row["history_id"],
      source_job_id=row["source_job_id"],
      provider=row["provider"],
      venue=row["venue"],
      symbol=row["symbol"],
      timeframe=row["timeframe"],
      recorded_at=self._ensure_utc(row["recorded_at"]) or datetime.now(UTC),
      sync_status=row["sync_status"],
      validation_claim=row["validation_claim"],
      reproducibility_state=row["reproducibility_state"] or "range_only",
      boundary_id=row["boundary_id"],
      checkpoint_id=row["checkpoint_id"],
      dataset_boundary=dataset_boundary,
      first_timestamp=self._ensure_utc(row["first_timestamp"]),
      last_timestamp=self._ensure_utc(row["last_timestamp"]),
      candle_count=int(row["candle_count"] or 0),
      lag_seconds=int(row["lag_seconds"]) if row["lag_seconds"] is not None else None,
      last_sync_at=self._ensure_utc(row["last_sync_at"]),
      failure_count_24h=int(row["failure_count_24h"] or 0),
      contiguous_missing_candles=(
        int(row["contiguous_missing_candles"])
        if row["contiguous_missing_candles"] is not None
        else None
      ),
      gap_window_count=int(row["gap_window_count"] or 0),
      last_error=row["last_error"],
      issues=issues,
    )

  def _row_to_ingestion_job_record(self, row: dict) -> MarketDataIngestionJobRecord:
    return MarketDataIngestionJobRecord(
      job_id=row["job_id"],
      provider=row["provider"],
      venue=row["venue"],
      symbol=row["symbol"],
      timeframe=row["timeframe"],
      operation=row["operation"],
      status=row["status"],
      started_at=self._ensure_utc(row["started_at"]) or datetime.now(UTC),
      finished_at=self._ensure_utc(row["finished_at"]) or datetime.now(UTC),
      duration_ms=int(row["duration_ms"] or 0),
      fetched_candle_count=int(row["fetched_candle_count"] or 0),
      validation_claim=row["validation_claim"],
      boundary_id=row["boundary_id"],
      checkpoint_id=row["checkpoint_id"],
      lineage_history_id=row["lineage_history_id"],
      requested_start_at=self._ensure_utc(row["requested_start_at"]),
      requested_end_at=self._ensure_utc(row["requested_end_at"]),
      requested_limit=int(row["requested_limit"]) if row["requested_limit"] is not None else None,
      last_error=row["last_error"],
    )

  def _build_sync_checkpoint(
    self,
    *,
    symbol: str,
    timeframe: str,
    coverage: CandleCoverage,
    contiguous_missing_candles: int | None = None,
    recorded_at: datetime | None = None,
  ) -> SyncCheckpoint | None:
    if coverage.candle_count == 0 or coverage.latest_ingested_at is None:
      return None
    missing_candles = (
      contiguous_missing_candles
      if contiguous_missing_candles is not None
      else self._count_missing_candles(symbol=symbol, timeframe=timeframe)
    )
    return SyncCheckpoint(
      checkpoint_id=build_sync_checkpoint_identity(
        provider=self._provider,
        venue=self._venue,
        symbol=symbol,
        timeframe=timeframe,
        candle_count=coverage.candle_count,
        first_timestamp=coverage.first_timestamp,
        last_timestamp=coverage.last_timestamp,
        latest_ingested_at=coverage.latest_ingested_at,
        contiguous_missing_candles=missing_candles,
      ),
      recorded_at=recorded_at or self._clock(),
      candle_count=coverage.candle_count,
      first_timestamp=coverage.first_timestamp,
      last_timestamp=coverage.last_timestamp,
      contiguous_missing_candles=missing_candles,
    )

  def _build_quality_snapshot(self, *, symbol: str, timeframe: str) -> QualitySnapshot:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    sync_state = self._read_sync_state(symbol=symbol, timeframe=timeframe)
    lag_seconds = self._calculate_lag_seconds(coverage.last_timestamp)
    missing_candles = self._count_missing_candles(symbol=symbol, timeframe=timeframe)
    issues: list[str] = []
    sync_status = "empty"
    if coverage.candle_count > 0:
      sync_status = "synced"
    if sync_state is not None and sync_state.sync_status == "error":
      sync_status = "error"
      issues.append("last_sync_failed")
    elif lag_seconds is not None and lag_seconds > self._freshness_threshold_seconds(timeframe):
      sync_status = "stale"
      issues.append("lagging")
      issues.append(
        f"freshness_threshold_exceeded:{lag_seconds}:{self._freshness_threshold_seconds(timeframe)}"
      )
    if missing_candles > 0:
      issues.append(f"missing_candles:{missing_candles}")
    return QualitySnapshot(
      coverage=coverage,
      sync_state=sync_state,
      lag_seconds=lag_seconds,
      sync_status=sync_status,
      issues=tuple(issues),
    )

  def _build_backfill_snapshot(
    self,
    *,
    symbol: str,
    timeframe: str,
    coverage: CandleCoverage,
  ) -> BackfillSnapshot:
    target_candles = self._historical_candle_limit
    completion_ratio = min(coverage.candle_count / target_candles, 1.0) if target_candles > 0 else 0.0
    complete = coverage.candle_count >= target_candles

    if (
      target_candles <= 0
      or coverage.first_timestamp is None
      or coverage.last_timestamp is None
      or coverage.candle_count == 0
    ):
      return BackfillSnapshot(
        target_candles=target_candles,
        completion_ratio=completion_ratio,
        complete=complete,
        contiguous_completion_ratio=None,
        contiguous_complete=None,
        contiguous_missing_candles=None,
        gap_windows=(),
      )

    timeframe_delta = self._timeframe_delta(timeframe)
    window_start = coverage.first_timestamp
    expected_candle_count = self._estimate_bar_count(
      start_at=coverage.first_timestamp,
      end_at=coverage.last_timestamp,
      timeframe=timeframe,
    )
    if complete:
      window_start = coverage.last_timestamp - (timeframe_delta * max(target_candles - 1, 0))
      expected_candle_count = target_candles

    timestamps = self._read_timestamps(
      symbol=symbol,
      timeframe=timeframe,
      start_at=window_start,
      end_at=coverage.last_timestamp,
    )
    gap_windows = self._build_gap_windows_from_timestamps(
      timestamps=timestamps,
      timeframe=timeframe,
    )
    missing_candles = sum(window.missing_candles for window in gap_windows)
    contiguous_completion_ratio = (
      min(len(timestamps) / expected_candle_count, 1.0)
      if expected_candle_count > 0
      else None
    )
    return BackfillSnapshot(
      target_candles=target_candles,
      completion_ratio=completion_ratio,
      complete=complete,
      contiguous_completion_ratio=contiguous_completion_ratio,
      contiguous_complete=missing_candles == 0,
      contiguous_missing_candles=missing_candles,
      gap_windows=gap_windows,
    )

  def _build_status_issues(
    self,
    *,
    timeframe: str,
    quality: QualitySnapshot,
    backfill: BackfillSnapshot,
    recent_failures: tuple[SyncFailure, ...],
    failure_count_24h: int,
  ) -> tuple[str, ...]:
    issues = list(quality.issues)
    if (
      backfill.target_candles is not None
      and backfill.target_candles > 0
      and quality.coverage.candle_count > 0
      and backfill.complete is False
    ):
      issues.append(
        f"backfill_target_incomplete:{quality.coverage.candle_count}:{backfill.target_candles}"
      )
    if backfill.contiguous_missing_candles is not None and backfill.contiguous_missing_candles > 0:
      issues.append(f"contiguous_backfill_incomplete:{backfill.contiguous_missing_candles}")
      issues.append(f"gap_windows:{len(backfill.gap_windows)}")
    if failure_count_24h > 0:
      issues.append(
        f"{'repeated_sync_failures' if failure_count_24h > 1 else 'recent_sync_failure'}:{failure_count_24h}"
      )
    for failure in recent_failures:
      issues.extend(self._classify_failure_semantics(failure.error))
    return tuple(dict.fromkeys(issues))

  def _repair_gap_windows(self, *, symbol: str, timeframe: str) -> int:
    coverage = self._read_coverage(symbol=symbol, timeframe=timeframe)
    backfill = self._build_backfill_snapshot(
      symbol=symbol,
      timeframe=timeframe,
      coverage=coverage,
    )
    repaired_windows = 0
    for window in backfill.gap_windows:
      if self._sync_range(
        symbol=symbol,
        timeframe=timeframe,
        start_at=window.start_at,
        end_at=window.end_at,
        limit=window.missing_candles,
      ):
        repaired_windows += 1
    return repaired_windows

  def _build_remediation_detail(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
    repaired_windows: int | None = None,
  ) -> str:
    status = self.get_status(timeframe)
    instrument = next(
      (
        candidate
        for candidate in status.instruments
        if self._symbol_from_instrument_id(candidate.instrument_id) == symbol
      ),
      None,
    )
    if instrument is None:
      return f"{kind}:{symbol}:{timeframe}:instrument_status_unavailable"
    detail_parts = [
      f"{kind}:{symbol}:{timeframe}",
      f"sync_status={instrument.sync_status}",
      f"candle_count={instrument.candle_count}",
    ]
    if instrument.last_sync_at is not None:
      detail_parts.append(f"last_sync_at={instrument.last_sync_at.isoformat()}")
    if instrument.lag_seconds is not None:
      detail_parts.append(f"lag_seconds={instrument.lag_seconds}")
    if repaired_windows is not None:
      detail_parts.append(f"repaired_gap_windows={repaired_windows}")
    if instrument.backfill_contiguous_missing_candles is not None:
      detail_parts.append(
        f"remaining_missing_candles={instrument.backfill_contiguous_missing_candles}"
      )
    if instrument.issues:
      detail_parts.append(f"issues={','.join(instrument.issues[:4])}")
    return " | ".join(detail_parts)

  def _classify_failure_semantics(self, error: str) -> tuple[str, ...]:
    normalized = error.lower()
    semantics: list[str] = []
    if "timeout" in normalized or "timed out" in normalized:
      semantics.append(f"{self._venue}_timeout")
    if (
      "rate limit" in normalized
      or "too many requests" in normalized
      or "429" in normalized
      or "throttle" in normalized
    ):
      semantics.append(f"{self._venue}_rate_limited")
    if (
      "network" in normalized
      or "connection" in normalized
      or "socket" in normalized
      or "dns" in normalized
    ):
      semantics.append(f"{self._venue}_network_fault")
    if (
      "auth" in normalized
      or "api key" in normalized
      or "api-key" in normalized
      or "signature" in normalized
      or "forbidden" in normalized
      or "unauthorized" in normalized
      or "permission denied" in normalized
    ):
      semantics.append(f"{self._venue}_auth_fault")
    if (
      "invalid symbol" in normalized
      or "unknown symbol" in normalized
      or "symbol not found" in normalized
      or "market not found" in normalized
      or "unknown market" in normalized
    ):
      semantics.append(f"{self._venue}_symbol_unavailable")
    if (
      "maintenance" in normalized
      or "service unavailable" in normalized
      or "system upgrade" in normalized
    ):
      semantics.append(f"{self._venue}_maintenance")
    if not semantics:
      semantics.append(f"{self._venue}_upstream_fault")
    return tuple(dict.fromkeys(semantics))

  def _count_missing_candles(self, *, symbol: str, timeframe: str) -> int:
    timestamps = self._read_timestamps(symbol=symbol, timeframe=timeframe)
    return sum(
      window.missing_candles
      for window in self._build_gap_windows_from_timestamps(
        timestamps=timestamps,
        timeframe=timeframe,
      )
    )

  def _build_gap_windows_from_timestamps(
    self,
    *,
    timestamps: list[datetime],
    timeframe: str,
  ) -> tuple[GapWindow, ...]:
    if len(timestamps) < 2:
      return ()

    timeframe_delta = self._timeframe_delta(timeframe)
    windows: list[GapWindow] = []
    for previous, current in zip(timestamps, timestamps[1:]):
      gap_size = int((current - previous).total_seconds() // timeframe_delta.total_seconds()) - 1
      if gap_size > 0:
        start_at = previous + timeframe_delta
        end_at = current - timeframe_delta
        occurrence_index = len(windows)
        windows.append(
          GapWindow(
            start_at=start_at,
            end_at=end_at,
            missing_candles=gap_size,
            gap_window_id=(
              f"gw|{occurrence_index}|{start_at.isoformat()}|{end_at.isoformat()}|{gap_size}"
            ),
          )
        )
    return tuple(windows)

  def _read_timestamps(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> list[datetime]:
    statement = select(market_candles.c.timestamp).where(
      and_(
        market_candles.c.venue == self._venue,
        market_candles.c.symbol == symbol,
        market_candles.c.timeframe == timeframe,
      )
    )
    if start_at is not None:
      statement = statement.where(market_candles.c.timestamp >= start_at)
    if end_at is not None:
      statement = statement.where(market_candles.c.timestamp <= end_at)
    statement = statement.order_by(market_candles.c.timestamp.asc())
    with self._engine.connect() as connection:
      return [self._ensure_utc(row[0]) for row in connection.execute(statement).all()]

  def _calculate_lag_seconds(self, last_timestamp: datetime | None) -> int | None:
    if last_timestamp is None:
      return None
    return max(int((self._clock() - last_timestamp).total_seconds()), 0)

  def _estimate_bar_count(self, *, start_at: datetime, end_at: datetime, timeframe: str) -> int:
    if end_at <= start_at:
      return 1
    timeframe_seconds = self._timeframe_seconds(timeframe)
    return max(int(((end_at - start_at).total_seconds() // timeframe_seconds) + 1), 1)

  def _freshness_threshold_seconds(self, timeframe: str) -> int:
    return self._timeframe_seconds(timeframe) * 2

  def _timeframe_delta(self, timeframe: str) -> timedelta:
    return timedelta(seconds=self._timeframe_seconds(timeframe))

  def _timeframe_seconds(self, timeframe: str) -> int:
    if timeframe not in _TIMEFRAME_SECONDS:
      raise ValueError(f"Unsupported timeframe: {timeframe}")
    return _TIMEFRAME_SECONDS[timeframe]

  def _normalize_ohlcv(self, raw_candles: list[list[float]]) -> list[Candle]:
    candles: list[Candle] = []
    for row in raw_candles:
      if len(row) < 6:
        continue
      candles.append(
        Candle(
          timestamp=datetime.fromtimestamp(row[0] / 1000, tz=UTC),
          open=float(row[1]),
          high=float(row[2]),
          low=float(row[3]),
          close=float(row[4]),
          volume=float(row[5]),
        )
      )
    return candles

  def _row_to_candle(self, row: dict) -> Candle:
    return Candle(
      timestamp=self._ensure_utc(row["timestamp"]),
      open=row["open"],
      high=row["high"],
      low=row["low"],
      close=row["close"],
      volume=row["volume"],
    )

  def _to_exchange_milliseconds(self, value: datetime) -> int:
    return int(value.timestamp() * 1000)

  def _ensure_utc(self, value: datetime | None) -> datetime | None:
    if value is None:
      return None
    if value.tzinfo is None:
      return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)

  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_columns = {
      column["name"]
      for column in inspector.get_columns("market_sync_state")
    }
    missing_columns = {
      "checkpoint_id": "TEXT",
      "checkpoint_recorded_at": "TIMESTAMP",
      "checkpoint_first_timestamp": "TIMESTAMP",
      "checkpoint_last_timestamp": "TIMESTAMP",
      "checkpoint_candle_count": "INTEGER",
      "checkpoint_contiguous_missing_candles": "INTEGER",
    }
    with self._engine.begin() as connection:
      for column_name, column_type in missing_columns.items():
        if column_name in existing_columns:
          continue
        connection.exec_driver_sql(
          f"ALTER TABLE market_sync_state ADD COLUMN {column_name} {column_type}"
        )

  def _build_engine(self, database_url: str) -> Engine:
    url = make_url(database_url)
    engine_kwargs = {"pool_pre_ping": True}
    if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
      Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
      return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        **engine_kwargs,
      )
    return create_engine(database_url, **engine_kwargs)
