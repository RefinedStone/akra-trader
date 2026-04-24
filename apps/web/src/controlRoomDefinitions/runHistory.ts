export const RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX = "akra-trader-run-history-saved-filters";

export type RunHistoryFilter = {
  strategy_id: string;
  strategy_version: string;
  preset_id: string;
  benchmark_family: string;
  tag: string;
  dataset_identity: string;
  filter_expr: string;
  collection_query_label: string;
};

export type RunHistorySurfaceKey = "backtest" | "sandbox" | "paper" | "live";

export type SavedRunHistoryFilterPreset = {
  filter_id: string;
  label: string;
  filter: RunHistoryFilter;
  created_at: string;
  updated_at: string;
};

export type SavedRunHistoryFilterPresetStateV1 = {
  version: 1;
  filters: SavedRunHistoryFilterPreset[];
};
