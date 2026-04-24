import type { KeyboardEvent, MouseEvent } from "react";

export const COMPARISON_TOOLTIP_TUNING_STORAGE_KEY = "akra-trader-comparison-tooltip-tuning";
export const COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION = 1;
export const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY = "akra-trader-comparison-tooltip-conflict-ui";
export const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION = 1;
export const COMPARISON_TOOLTIP_TUNING_SHARE_PARAM = "comparisonTooltipTuning";
export const MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES = 5;

export type ComparisonTooltipTargetProps = {
  "aria-describedby"?: string;
  "data-tooltip-visible": "true" | "false";
  onBlur: () => void;
  onFocus: () => void;
  onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  onMouseEnter: (event: MouseEvent<HTMLElement>) => void;
  onMouseLeave: (event: MouseEvent<HTMLElement>) => void;
  onMouseMove?: (event: MouseEvent<HTMLElement>) => void;
};
export type ComparisonTooltipInteractionOptions = {
  hoverCloseDelayMs?: number;
  hoverOpenDelayMs?: number;
};
export type ComparisonTooltipTuning = {
  column_down_sweep_close_ms: number;
  column_down_sweep_hold_ms: number;
  column_down_sweep_open_ms: number;
  column_up_sweep_close_ms: number;
  column_up_sweep_hold_ms: number;
  column_up_sweep_open_ms: number;
  horizontal_distance_ratio: number;
  horizontal_velocity_threshold: number;
  metric_hover_close_ms: number;
  metric_hover_open_ms: number;
  row_sweep_close_ms: number;
  row_sweep_hold_ms: number;
  row_sweep_open_ms: number;
  speed_adjustment_base: number;
  speed_adjustment_max: number;
  speed_adjustment_min: number;
  speed_adjustment_slope: number;
  sweep_time_max_ms: number;
  sweep_time_min_ms: number;
  sweep_time_speed_multiplier: number;
  vertical_distance_ratio: number;
  vertical_velocity_threshold: number;
};
export type ComparisonTooltipTuningPresetStateV1 = {
  current_tuning: ComparisonTooltipTuning;
  presets: Record<string, ComparisonTooltipTuning>;
  selected_preset_name?: string | null;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
export type ComparisonTooltipTuningSinglePresetShareV1 = {
  preset_name: string;
  tuning: ComparisonTooltipTuning;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
export type ComparisonTooltipPresetImportConflictPolicy = "overwrite" | "rename";
export type ComparisonTooltipPresetImportResolution = {
  conflicted: boolean;
  final_preset_name: string;
  imported_preset_name: string;
  policy: ComparisonTooltipPresetImportConflictPolicy;
  renamed: boolean;
  overwritten: boolean;
};
export type ComparisonTooltipPendingPresetImportConflict = {
  imported_preset_name: string;
  proposed_preset_name: string;
  raw: string;
  tuning: ComparisonTooltipTuning;
};
export type ComparisonTooltipPresetConflictPreviewRow = {
  changed: boolean;
  delta_direction: "higher" | "lower" | "same";
  delta_label: string;
  existing_value: number;
  group_key: string;
  group_label: string;
  group_order: number;
  incoming_value: number;
  key: keyof ComparisonTooltipTuning;
  label: string;
};
export type ComparisonTooltipPresetConflictPreviewGroup = {
  changed_count: number;
  higher_count: number;
  key: string;
  label: string;
  lower_count: number;
  rows: ComparisonTooltipPresetConflictPreviewRow[];
  same_count: number;
  summary_label: string;
};
export type ComparisonTooltipConflictSessionUiState = {
  collapsed_unchanged_groups: Record<string, boolean>;
  show_unchanged_conflict_rows: boolean;
  updated_at: string | null;
};
export type ComparisonTooltipConflictUiStateV1 = {
  sessions: Record<string, ComparisonTooltipConflictSessionUiState>;
  version: typeof COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION;
};
export type ComparisonTooltipConflictSessionSummary = {
  group_key: string;
  includes_current: boolean;
  label: string;
  preset_name: string;
  session_count: number;
  sessions: ComparisonTooltipConflictSessionSummarySession[];
};
export type ComparisonTooltipConflictSessionSummarySession = {
  hash: string | null;
  includes_current: boolean;
  label: string;
  metadata: string[];
  session_key: string;
  updated_at: string | null;
};
export type ComparisonTooltipTuningShareImport =
  | {
      kind: "bundle";
      raw: string;
      state: ComparisonTooltipTuningPresetStateV1;
    }
  | {
      kind: "preset";
      preset_name: string;
      raw: string;
      tuning: ComparisonTooltipTuning;
    };
export type ComparisonTooltipLayout = {
  tooltipId: string;
  left: number;
  top: number;
  maxWidth: number;
  arrowLeft: number;
  side: "top" | "bottom";
};

export const DEFAULT_COMPARISON_TOOLTIP_TUNING: ComparisonTooltipTuning = {
  column_down_sweep_close_ms: 80,
  column_down_sweep_hold_ms: 140,
  column_down_sweep_open_ms: 170,
  column_up_sweep_close_ms: 95,
  column_up_sweep_hold_ms: 180,
  column_up_sweep_open_ms: 260,
  horizontal_distance_ratio: 0.32,
  horizontal_velocity_threshold: 0.42,
  metric_hover_close_ms: 70,
  metric_hover_open_ms: 110,
  row_sweep_close_ms: 90,
  row_sweep_hold_ms: 180,
  row_sweep_open_ms: 250,
  speed_adjustment_base: 1.18,
  speed_adjustment_max: 1.12,
  speed_adjustment_min: 0.72,
  speed_adjustment_slope: 0.28,
  sweep_time_max_ms: 126,
  sweep_time_min_ms: 72,
  sweep_time_speed_multiplier: 42,
  vertical_distance_ratio: 0.42,
  vertical_velocity_threshold: 0.34,
};
export const SHOW_COMPARISON_TOOLTIP_TUNING_PANEL = import.meta.env.DEV;
export const DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY: ComparisonTooltipPresetImportConflictPolicy =
  "rename";
export const COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD = 3;
export const PRESET_TIMEFRAME_UNIT_TO_MINUTES: Record<string, number> = {
  d: 1440,
  h: 60,
  m: 1,
  w: 10080,
};
export const PRESET_PROFILE_AGGRESSIVENESS_RANKS: Record<string, number> = {
  aggressive: 4,
  assertive: 3,
  balanced: 2,
  cautious: 1,
  conservative: 1,
  normal: 2,
  safe: 0,
  standard: 2,
};
export const PRESET_PROFILE_SPEED_RANKS: Record<string, number> = {
  balanced: 1,
  fast: 2,
  medium: 1,
  normal: 1,
  slow: 0,
  steady: 0,
  turbo: 3,
};
export const PRESET_PROFILE_CONFIDENCE_RANKS: Record<string, number> = {
  balanced: 1,
  high: 2,
  low: 0,
  medium: 1,
};
export const COMPARISON_TOOLTIP_TUNING_LABELS: Record<keyof ComparisonTooltipTuning, string> = {
  column_down_sweep_close_ms: "Col down close",
  column_down_sweep_hold_ms: "Col down hold",
  column_down_sweep_open_ms: "Col down open",
  column_up_sweep_close_ms: "Col up close",
  column_up_sweep_hold_ms: "Col up hold",
  column_up_sweep_open_ms: "Col up open",
  horizontal_distance_ratio: "Horiz ratio",
  horizontal_velocity_threshold: "Horiz velocity",
  metric_hover_close_ms: "Metric close",
  metric_hover_open_ms: "Metric open",
  row_sweep_close_ms: "Row close",
  row_sweep_hold_ms: "Row hold",
  row_sweep_open_ms: "Row open",
  speed_adjustment_base: "Speed base",
  speed_adjustment_max: "Speed max",
  speed_adjustment_min: "Speed min",
  speed_adjustment_slope: "Speed slope",
  sweep_time_max_ms: "Time max",
  sweep_time_min_ms: "Time min",
  sweep_time_speed_multiplier: "Time speed",
  vertical_distance_ratio: "Vert ratio",
  vertical_velocity_threshold: "Vert velocity",
};
export const COMPARISON_TOOLTIP_TUNING_GROUPS: Record<
  keyof ComparisonTooltipTuning,
  { key: string; label: string; order: number }
> = {
  column_down_sweep_close_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_down_sweep_hold_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_down_sweep_open_ms: {
    key: "column-down-sweep",
    label: "Column Down Sweep",
    order: 4,
  },
  column_up_sweep_close_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  column_up_sweep_hold_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  column_up_sweep_open_ms: {
    key: "column-up-sweep",
    label: "Column Up Sweep",
    order: 5,
  },
  horizontal_distance_ratio: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  horizontal_velocity_threshold: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  metric_hover_close_ms: {
    key: "hover-timing",
    label: "Hover Timing",
    order: 0,
  },
  metric_hover_open_ms: {
    key: "hover-timing",
    label: "Hover Timing",
    order: 0,
  },
  row_sweep_close_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  row_sweep_hold_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  row_sweep_open_ms: {
    key: "row-sweep",
    label: "Row Sweep",
    order: 3,
  },
  speed_adjustment_base: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_max: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_min: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  speed_adjustment_slope: {
    key: "speed-scaling",
    label: "Speed Scaling",
    order: 6,
  },
  sweep_time_max_ms: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  sweep_time_min_ms: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  sweep_time_speed_multiplier: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  vertical_distance_ratio: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
  vertical_velocity_threshold: {
    key: "sweep-detection",
    label: "Sweep Detection",
    order: 2,
  },
};
