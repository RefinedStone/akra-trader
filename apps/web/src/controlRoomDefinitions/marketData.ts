import type { DatasetBoundaryContract } from "./runSurfaceContracts";

export const MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY = "akra-trader-market-data-provenance-exports";
export const MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION = 1;
export const MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES = 12;

export type MarketDataStatus = {
  provider: string;
  venue: string;
  instruments: {
    instrument_id: string;
    timeframe: string;
    candle_count: number;
    first_timestamp: string | null;
    last_timestamp: string | null;
    sync_status: string;
    lag_seconds: number | null;
    last_sync_at: string | null;
    sync_checkpoint: {
      checkpoint_id: string;
      recorded_at: string;
      candle_count: number;
      first_timestamp: string | null;
      last_timestamp: string | null;
      contiguous_missing_candles: number;
    } | null;
    recent_failures: {
      failed_at: string;
      operation: string;
      error: string;
    }[];
    failure_count_24h: number;
    backfill_target_candles: number | null;
    backfill_completion_ratio: number | null;
    backfill_complete: boolean | null;
    backfill_contiguous_completion_ratio: number | null;
    backfill_contiguous_complete: boolean | null;
    backfill_contiguous_missing_candles: number | null;
    backfill_gap_windows: {
      gap_window_id: string;
      start_at: string;
      end_at: string;
      missing_candles: number;
    }[];
    issues: string[];
  }[];
};

export type MarketDataLineageHistoryRecord = {
  history_id: string;
  source_job_id?: string | null;
  provider: string;
  venue: string;
  symbol: string;
  timeframe: string;
  recorded_at: string;
  sync_status: string;
  validation_claim: string;
  reproducibility_state: string;
  boundary_id?: string | null;
  checkpoint_id?: string | null;
  dataset_boundary?: DatasetBoundaryContract | null;
  first_timestamp?: string | null;
  last_timestamp?: string | null;
  candle_count: number;
  lag_seconds?: number | null;
  last_sync_at?: string | null;
  failure_count_24h: number;
  contiguous_missing_candles?: number | null;
  gap_window_count: number;
  last_error?: string | null;
  issues: string[];
};

export type MarketDataIngestionJobRecord = {
  job_id: string;
  provider: string;
  venue: string;
  symbol: string;
  timeframe: string;
  operation: string;
  status: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  fetched_candle_count: number;
  validation_claim?: string | null;
  boundary_id?: string | null;
  checkpoint_id?: string | null;
  lineage_history_id?: string | null;
  requested_start_at?: string | null;
  requested_end_at?: string | null;
  requested_limit?: number | null;
  last_error?: string | null;
};

export type MarketDataCandle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type MarketDataCandlesResponse = {
  symbol: string;
  timeframe: string;
  limit: number;
  candles: MarketDataCandle[];
};

export type OperatorLineageEvidenceRetentionPolicy = {
  policy_key: string;
  lineage_history_days: number;
  lineage_issue_history_days: number;
  ingestion_job_days: number;
  ingestion_issue_job_days: number;
};

export type OperatorLineageEvidenceRetentionResult = {
  policy: OperatorLineageEvidenceRetentionPolicy;
  current_time: string;
  dry_run: boolean;
  lineage_history_cutoff_at: string;
  lineage_issue_history_cutoff_at: string;
  ingestion_job_cutoff_at: string;
  ingestion_issue_job_cutoff_at: string;
  eligible_lineage_history_ids: string[];
  eligible_ingestion_job_ids: string[];
  retained_lineage_history_floor_ids: string[];
  retained_ingestion_job_floor_ids: string[];
  protected_lineage_history_ids: string[];
  protected_ingestion_job_ids: string[];
  deleted_lineage_history_count: number;
  deleted_ingestion_job_count: number;
};

export type OperatorLineageDrillEvidencePack = {
  pack_id: string;
  generated_at: string;
  generated_by: string;
  retention_policy: OperatorLineageEvidenceRetentionPolicy;
  retention_expires_at: string;
  export_format: string;
  scenario_key?: string | null;
  scenario_label?: string | null;
  incident_id?: string | null;
  operator_decision: string;
  final_posture: string;
  venue?: string | null;
  symbols: string[];
  timeframe?: string | null;
  source_run_id?: string | null;
  rerun_id?: string | null;
  dataset_identity?: string | null;
  sync_checkpoint_id?: string | null;
  rerun_boundary_id?: string | null;
  validation_claim?: string | null;
  rerun_validation_category?: string | null;
  lineage_history_filters: Record<string, unknown>;
  ingestion_job_filters: Record<string, unknown>;
  lineage_history_count: number;
  ingestion_job_count: number;
  lineage_history: MarketDataLineageHistoryRecord[];
  ingestion_jobs: MarketDataIngestionJobRecord[];
  content: string;
};

export type MarketDataProvenanceExportSort =
  | "newest"
  | "oldest"
  | "provider"
  | "severity";

export type MarketDataProvenanceExportFilterState = {
  provider: string;
  vendor_field: string;
  search_query: string;
  sort: MarketDataProvenanceExportSort;
};

export type MarketDataProvenanceExportHistoryEntry = {
  export_id: string;
  exported_at: string;
  focus_key: string;
  focus_label: string;
  symbol: string;
  timeframe: string;
  provider: string;
  venue: string;
  result_count: number;
  provider_provenance_count: number;
  provider_labels: string[];
  filter: MarketDataProvenanceExportFilterState;
  content: string;
};

export type MarketDataProvenanceExportStateV1 = {
  version: typeof MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION;
  active_filter: MarketDataProvenanceExportFilterState;
  history: MarketDataProvenanceExportHistoryEntry[];
};

// Runtime placeholders for generated barrel compatibility.
export const MarketDataStatus = undefined;
export const MarketDataLineageHistoryRecord = undefined;
export const MarketDataIngestionJobRecord = undefined;
export const MarketDataCandle = undefined;
export const MarketDataCandlesResponse = undefined;
export const OperatorLineageEvidenceRetentionPolicy = undefined;
export const OperatorLineageEvidenceRetentionResult = undefined;
export const OperatorLineageDrillEvidencePack = undefined;
export const MarketDataProvenanceExportSort = undefined;
export const MarketDataProvenanceExportFilterState = undefined;
export const MarketDataProvenanceExportHistoryEntry = undefined;
export const MarketDataProvenanceExportStateV1 = undefined;
