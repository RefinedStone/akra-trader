export type ParameterSchema = Record<
  string,
  {
    default?: unknown;
    delta_higher_label?: string;
    delta_lower_label?: string;
    description?: string;
    enum?: unknown[];
    minimum?: number;
    maximum?: number;
    semantic_hint?: string;
    semantic_ranks?: Record<string, number>;
    type?: string;
    unit?: string;
  }
>;

export type Strategy = {
  strategy_id: string;
  name: string;
  version: string;
  version_lineage: string[];
  runtime: string;
  asset_types: string[];
  supported_timeframes: string[];
  parameter_schema: ParameterSchema;
  description: string;
  lifecycle: {
    stage: string;
    registered_at?: string | null;
  };
  catalog_semantics: {
    strategy_kind: string;
    execution_model: string;
    parameter_contract: string;
    source_descriptor?: string | null;
    operator_notes: string[];
  };
  reference_id?: string | null;
  reference_path?: string | null;
  entrypoint?: string | null;
};

export type ReferenceSource = {
  reference_id: string;
  title: string;
  kind?: string;
  homepage?: string;
  license: string;
  integration_mode: string;
  local_path?: string | null;
  runtime?: string | null;
  summary: string;
};

export type ExperimentPresetRevision = {
  revision_id: string;
  actor: string;
  reason: string;
  created_at: string;
  action: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  strategy_id?: string | null;
  timeframe?: string | null;
  benchmark_family?: string | null;
  tags: string[];
  parameters: Record<string, unknown>;
};

export type ExperimentPreset = {
  preset_id: string;
  name: string;
  description: string;
  strategy_id?: string | null;
  timeframe?: string | null;
  benchmark_family?: string | null;
  tags: string[];
  parameters: Record<string, unknown>;
  lifecycle: {
    stage: string;
    updated_at: string;
    updated_by: string;
    last_action: string;
    history: {
      action: string;
      actor: string;
      reason: string;
      occurred_at: string;
      from_stage?: string | null;
      to_stage: string;
      lineage_evidence_pack_id?: string | null;
      lineage_evidence_retention_expires_at?: string | null;
      lineage_evidence_summary?: string | null;
    }[];
  };
  revisions: ExperimentPresetRevision[];
  created_at: string;
  updated_at: string;
};

export type PresetRevisionFilterState = {
  action: string;
  query: string;
};

export type PresetStructuredDiffRow = {
  changed: boolean;
  delta_direction: "higher" | "lower" | "same";
  delta_label: string;
  existing_value: string;
  group_key: string;
  group_label: string;
  group_order: number;
  incoming_value: string;
  key: string;
  label: string;
  semantic_hint?: string;
};

export type PresetStructuredDiffGroup = {
  changed_count: number;
  higher_count: number;
  key: string;
  label: string;
  lower_count: number;
  rows: PresetStructuredDiffRow[];
  same_count: number;
  summary_label: string;
};

export type PresetStructuredDiffDeltaValue = {
  direction: "higher" | "lower" | "same";
  label: string;
};

export type PresetRevisionDiff = {
  basisLabel: string;
  changeCount: number;
  changedGroups: PresetStructuredDiffGroup[];
  unchangedGroups: PresetStructuredDiffGroup[];
  searchTexts: string[];
  summary: string;
};

export type PresetDraftConflict = {
  changeCount: number;
  groups: PresetStructuredDiffGroup[];
  hasInvalidParameters: boolean;
  summary: string;
};
