from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class DatasetBoundaryContract:
  contract_version: str = "dataset_boundary.v1"
  provider: str = "unknown"
  venue: str = ""
  symbols: tuple[str, ...] = ()
  timeframe: str = ""
  reproducibility_state: str = "range_only"
  validation_claim: str = "window_only"
  boundary_id: str | None = None
  dataset_identity: str | None = None
  sync_checkpoint_id: str | None = None
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0

@dataclass(frozen=True)
class MarketDataLineage:
  provider: str
  venue: str
  symbols: tuple[str, ...]
  timeframe: str
  dataset_identity: str | None = None
  sync_checkpoint_id: str | None = None
  reproducibility_state: str = "range_only"
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  effective_start_at: datetime | None = None
  effective_end_at: datetime | None = None
  candle_count: int = 0
  sync_status: str = "unknown"
  last_sync_at: datetime | None = None
  issues: tuple[str, ...] = ()

@dataclass(frozen=True)
class MarketDataLineageHistoryRecord:
  history_id: str
  source_job_id: str | None
  provider: str
  venue: str
  symbol: str
  timeframe: str
  recorded_at: datetime
  sync_status: str
  validation_claim: str
  reproducibility_state: str = "range_only"
  boundary_id: str | None = None
  checkpoint_id: str | None = None
  dataset_boundary: DatasetBoundaryContract | None = None
  first_timestamp: datetime | None = None
  last_timestamp: datetime | None = None
  candle_count: int = 0
  lag_seconds: int | None = None
  last_sync_at: datetime | None = None
  failure_count_24h: int = 0
  contiguous_missing_candles: int | None = None
  gap_window_count: int = 0
  last_error: str | None = None
  issues: tuple[str, ...] = ()

@dataclass(frozen=True)
class MarketDataIngestionJobRecord:
  job_id: str
  provider: str
  venue: str
  symbol: str
  timeframe: str
  operation: str
  status: str
  started_at: datetime
  finished_at: datetime
  duration_ms: int
  fetched_candle_count: int = 0
  validation_claim: str | None = None
  boundary_id: str | None = None
  checkpoint_id: str | None = None
  lineage_history_id: str | None = None
  requested_start_at: datetime | None = None
  requested_end_at: datetime | None = None
  requested_limit: int | None = None
  last_error: str | None = None

@dataclass(frozen=True)
class OperatorLineageEvidenceRetentionPolicy:
  policy_key: str = "operator_lineage_evidence.v1"
  lineage_history_days: int = 90
  lineage_issue_history_days: int = 180
  ingestion_job_days: int = 30
  ingestion_issue_job_days: int = 90

@dataclass(frozen=True)
class OperatorLineageEvidenceRetentionResult:
  policy: OperatorLineageEvidenceRetentionPolicy
  current_time: datetime
  dry_run: bool
  lineage_history_cutoff_at: datetime
  lineage_issue_history_cutoff_at: datetime
  ingestion_job_cutoff_at: datetime
  ingestion_issue_job_cutoff_at: datetime
  eligible_lineage_history_ids: tuple[str, ...] = ()
  eligible_ingestion_job_ids: tuple[str, ...] = ()
  retained_lineage_history_floor_ids: tuple[str, ...] = ()
  retained_ingestion_job_floor_ids: tuple[str, ...] = ()
  protected_lineage_history_ids: tuple[str, ...] = ()
  protected_ingestion_job_ids: tuple[str, ...] = ()
  deleted_lineage_history_count: int = 0
  deleted_ingestion_job_count: int = 0
