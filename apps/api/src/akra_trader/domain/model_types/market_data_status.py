from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass(frozen=True)
class InstrumentStatus:
  instrument_id: str
  timeframe: str
  candle_count: int
  first_timestamp: datetime | None
  last_timestamp: datetime | None
  sync_status: str = "empty"
  lag_seconds: int | None = None
  last_sync_at: datetime | None = None
  sync_checkpoint: "SyncCheckpoint" | None = None
  recent_failures: tuple["SyncFailure", ...] = ()
  failure_count_24h: int = 0
  backfill_target_candles: int | None = None
  backfill_completion_ratio: float | None = None
  backfill_complete: bool | None = None
  backfill_contiguous_completion_ratio: float | None = None
  backfill_contiguous_complete: bool | None = None
  backfill_contiguous_missing_candles: int | None = None
  backfill_gap_windows: tuple["GapWindow", ...] = ()
  issues: tuple[str, ...] = ()

@dataclass(frozen=True)
class MarketDataStatus:
  provider: str
  venue: str
  instruments: list[InstrumentStatus]

@dataclass(frozen=True)
class GapWindow:
  start_at: datetime
  end_at: datetime
  missing_candles: int
  gap_window_id: str = ""

  def __post_init__(self) -> None:
    if self.gap_window_id:
      return
    payload = "|".join([
      self.start_at.isoformat(),
      self.end_at.isoformat(),
      str(self.missing_candles),
    ])
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    object.__setattr__(
      self,
      "gap_window_id",
      f"gw|0|{self.start_at.isoformat()}|{self.end_at.isoformat()}|{self.missing_candles}|{digest}",
    )

@dataclass(frozen=True)
class SyncCheckpoint:
  checkpoint_id: str
  recorded_at: datetime
  candle_count: int
  first_timestamp: datetime | None = None
  last_timestamp: datetime | None = None
  contiguous_missing_candles: int = 0

@dataclass(frozen=True)
class SyncFailure:
  failed_at: datetime
  operation: str
  error: str
