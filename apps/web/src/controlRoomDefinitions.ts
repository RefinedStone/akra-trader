import type { KeyboardEvent, MouseEvent } from "react";

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

export type ComparisonHistorySyncWorkspaceSemanticSignal = {
  label: string;
  weight: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentSnapshot = {
  previewSelection: {
    diffItemKey: string | null;
    groupKey: string | null;
    traceKey: string | null;
  };
  replayActionTypeFilter:
    | "all"
    | "manual_anchor"
    | "dependency_selection"
    | "direct_auto_selection"
    | "conflict_blocked"
    | "idle";
  replayEdgeFilter: "all" | string;
  replayGroupFilter: "all" | string;
  replayIndex: number;
  replayScope: "all" | string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy =
  "full"
  | "omit_preview"
  | "summary_only";

export type RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy =
  "1d"
  | "7d"
  | "30d"
  | "manual";

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload = {
  alias_id: string;
  alias_token: string;
  created_at: string;
  created_by_tab_id: string | null;
  created_by_tab_label: string | null;
  expires_at: string | null;
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  redaction_policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  resolution_source: "server";
  revoked_at: string | null;
  revoked_by_tab_id: string | null;
  revoked_by_tab_label: string | null;
  signature: string | null;
  template_key: string;
  template_label: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry = {
  action: string;
  alias_created_at: string | null;
  alias_expires_at: string | null;
  alias_id: string;
  alias_revoked_at: string | null;
  audit_id: string;
  detail: string;
  expires_at: string | null;
  recorded_at: string;
  redaction_policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retention_policy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  source_tab_id: string | null;
  source_tab_label: string | null;
  template_key: string;
  template_label: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload = {
  items: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry[];
  total: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload = {
  deleted_count: number;
  matched_audit_ids?: string[];
  mode: "expired" | "matched" | string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry = {
  artifact_id: string | null;
  completed_at: string | null;
  content_type: string;
  created_at: string;
  content_length: number;
  expires_at: string | null;
  export_format: "json" | "csv" | string;
  filename: string;
  filters: Record<string, unknown>;
  job_id: string;
  record_count: number;
  requested_by_tab_id: string | null;
  requested_by_tab_label: string | null;
  status: string;
  template_key: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload = {
  items: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry[];
  total: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload =
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry & {
    content: string;
  };

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry = {
  action: string;
  audit_id: string;
  detail: string;
  expires_at: string | null;
  export_format: string | null;
  job_id: string;
  recorded_at: string;
  source_tab_id: string | null;
  source_tab_label: string | null;
  template_key: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload = {
  history: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry[];
  job: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload = {
  deleted_artifact_count: number;
  deleted_artifact_ids?: string[];
  deleted_history_count: number;
  deleted_job_count: number;
  deleted_job_ids?: string[];
  mode: "expired" | "matched" | string;
};

export type RunListBoundaryGroupKey =
  | "supporting_identity"
  | "eligible_metrics"
  | "operational_workflow"
  | "operational_order_actions";

export type RunListBoundarySurfaceId =
  | "mode"
  | "lane"
  | "lifecycle"
  | "version"
  | "return"
  | "drawdown"
  | "win_rate"
  | "trades"
  | "compare_toggle"
  | "rerun"
  | "stop"
  | "cancel_order"
  | "replace_order";

export type RunListBoundaryEligibility = "eligible" | "operational" | "supporting";

export type BenchmarkArtifact = {
  kind: string;
  label: string;
  path: string;
  format?: string | null;
  exists: boolean;
  is_directory: boolean;
  summary: Record<string, unknown>;
  sections?: Record<string, Record<string, unknown>>;
  summary_source_path?: string | null;
  source_locations?: {
    summary?: Record<
      string,
      {
        candidate_bindings?: Array<{
          binding_kind?: string | null;
          candidate_id?: string | null;
          runtime_candidate_id?: string | null;
          candidate_path_template?: string | null;
          candidate_value?: string | null;
          symbol_key?: string | null;
        }> | null;
        label_key?: string | null;
        searchable_texts?: string[] | null;
        source_path?: string | null;
      }
    > | null;
    sections?: Record<
      string,
      Array<{
        candidate_bindings?: Array<{
          binding_kind?: string | null;
          candidate_id?: string | null;
          runtime_candidate_id?: string | null;
          candidate_path_template?: string | null;
          candidate_value?: string | null;
          symbol_key?: string | null;
        }> | null;
        line_index?: number | null;
        line_key?: string | null;
        searchable_texts?: string[] | null;
        section_key?: string | null;
        source_path?: string | null;
      }>
    > | null;
  } | null;
};

export type RunListBoundaryContract = {
  scope: "run_list";
  surfaces: Record<
    RunListBoundarySurfaceId,
    {
      eligibility: RunListBoundaryEligibility;
      group: RunListBoundaryGroupKey;
      label: string;
    }
  >;
  groups: Record<
    RunListBoundaryGroupKey,
    {
      copy: string;
      eligibility: RunListBoundaryEligibility;
      surface_ids: RunListBoundarySurfaceId[];
      title: string;
    }
  >;
};

export type RunSurfaceEnforcementState = {
  enabled: boolean;
  family_key: string;
  family_title?: string | null;
  surface_key: string;
  surface_label?: string | null;
  rule_key?: string | null;
  enforcement_point?: string | null;
  enforcement_mode?: string | null;
  level?: string | null;
  fallback_behavior?: string | null;
  source_of_truth?: string | null;
  reason?: string | null;
};

export type RunActionAvailabilityEntry = {
  allowed: boolean;
  reason?: string | null;
  family_key: string;
  surface_key: string;
  rule_key?: string | null;
  enforcement_mode?: string | null;
  level?: string | null;
};

export type DatasetBoundaryContract = {
  contract_version: string;
  provider: string;
  venue: string;
  symbols: string[];
  timeframe: string;
  reproducibility_state: string;
  validation_claim: string;
  boundary_id?: string | null;
  dataset_identity?: string | null;
  sync_checkpoint_id?: string | null;
  requested_start_at?: string | null;
  requested_end_at?: string | null;
  effective_start_at?: string | null;
  effective_end_at?: string | null;
  candle_count: number;
};

export type OperatorLineageSummary = {
  status: string;
  posture: string;
  title: string;
  summary: string;
  operator_action: string;
  category: string;
  validation_claim?: string | null;
  boundary_id?: string | null;
  blocking: boolean;
};

export type Run = {
  config: {
    run_id: string;
    mode: string;
    strategy_id: string;
    strategy_version: string;
    symbols: string[];
    timeframe: string;
    initial_cash: number;
  };
  status: string;
  started_at: string;
  ended_at?: string | null;
  provenance: {
    lane: string;
    reference_id?: string | null;
    reference_version?: string | null;
    integration_mode?: string | null;
    rerun_boundary_id?: string | null;
    rerun_boundary_state: string;
    rerun_source_run_id?: string | null;
    rerun_target_boundary_id?: string | null;
    rerun_match_status: string;
    rerun_validation_category: string;
    rerun_validation_summary?: string | null;
    lineage_summary?: OperatorLineageSummary | null;
    reference?: ReferenceSource | null;
    working_directory?: string | null;
    external_command: string[];
    artifact_paths: string[];
    benchmark_artifacts: BenchmarkArtifact[];
    experiment: {
      tags: string[];
      preset_id?: string | null;
      benchmark_family?: string | null;
    };
    strategy?: {
      strategy_id: string;
      name: string;
      version: string;
      version_lineage: string[];
      runtime: string;
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
      parameter_snapshot: {
        requested: Record<string, unknown>;
        resolved: Record<string, unknown>;
        schema: ParameterSchema;
      };
      supported_timeframes: string[];
      warmup: {
        required_bars: number;
        timeframes: string[];
      };
      reference_id?: string | null;
      reference_path?: string | null;
      entrypoint?: string | null;
    } | null;
    market_data?: {
      provider: string;
      venue: string;
      symbols: string[];
      timeframe: string;
      dataset_identity?: string | null;
      sync_checkpoint_id?: string | null;
      reproducibility_state: string;
      requested_start_at?: string | null;
      requested_end_at?: string | null;
      effective_start_at?: string | null;
      effective_end_at?: string | null;
      candle_count: number;
      sync_status: string;
      last_sync_at?: string | null;
      issues: string[];
      dataset_boundary?: DatasetBoundaryContract | null;
    } | null;
    market_data_by_symbol?: Record<
      string,
      {
        provider: string;
        venue: string;
        symbols: string[];
        timeframe: string;
        dataset_identity?: string | null;
        sync_checkpoint_id?: string | null;
        reproducibility_state: string;
        requested_start_at?: string | null;
        requested_end_at?: string | null;
        effective_start_at?: string | null;
        effective_end_at?: string | null;
        candle_count: number;
        sync_status: string;
        last_sync_at?: string | null;
        issues: string[];
        dataset_boundary?: DatasetBoundaryContract | null;
      }
    >;
    runtime_session?: {
      session_id: string;
      worker_kind: string;
      lifecycle_state: string;
      started_at: string;
      primed_candle_count: number;
      processed_tick_count: number;
      last_heartbeat_at?: string | null;
      last_processed_candle_at?: string | null;
      last_seen_candle_at?: string | null;
      heartbeat_interval_seconds: number;
      heartbeat_timeout_seconds: number;
      recovery_count: number;
      last_recovered_at?: string | null;
      last_recovery_reason?: string | null;
    } | null;
  };
  metrics: Record<string, number>;
  surface_enforcement?: Record<string, RunSurfaceEnforcementState>;
  action_availability?: {
    compare_select: RunActionAvailabilityEntry;
    rerun_backtest: RunActionAvailabilityEntry;
    rerun_sandbox: RunActionAvailabilityEntry;
    rerun_paper: RunActionAvailabilityEntry;
    stop_run: RunActionAvailabilityEntry;
  };
  orders: {
    order_id: string;
    instrument_id: string;
    side: string;
    quantity: number;
    requested_price: number;
    order_type: string;
    status: string;
    created_at: string;
    updated_at?: string | null;
    filled_at?: string | null;
    average_fill_price?: number | null;
    fee_paid: number;
    filled_quantity: number;
    remaining_quantity?: number | null;
    last_synced_at?: string | null;
    action_availability?: {
      cancel: RunActionAvailabilityEntry;
      replace: RunActionAvailabilityEntry;
    };
  }[];
  notes: string[];
};

export type RunComparison = {
  requested_run_ids: string[];
  baseline_run_id: string;
  intent: ComparisonIntent;
  runs: {
    run_id: string;
    mode: string;
    status: string;
    lane: string;
    strategy_id: string;
    strategy_name?: string | null;
    strategy_version: string;
    catalog_semantics: {
      strategy_kind: string;
      execution_model: string;
      parameter_contract: string;
      source_descriptor?: string | null;
      operator_notes: string[];
    };
    symbols: string[];
    timeframe: string;
    started_at: string;
    ended_at?: string | null;
    reference_id?: string | null;
    reference_version?: string | null;
    integration_mode?: string | null;
    reference?: ReferenceSource | null;
    working_directory?: string | null;
    dataset_identity?: string | null;
    experiment: {
      tags: string[];
      preset_id?: string | null;
      benchmark_family?: string | null;
    };
    external_command: string[];
    artifact_paths: string[];
    benchmark_artifacts: BenchmarkArtifact[];
    metrics: Record<string, number>;
    notes: string[];
  }[];
  metric_rows: {
    key: string;
    label: string;
    unit: string;
    higher_is_better?: boolean | null;
    values: Record<string, number | null>;
    deltas_vs_baseline: Record<string, number | null>;
    delta_annotations: Record<string, string>;
    annotation?: string | null;
    best_run_id?: string | null;
  }[];
  narratives: {
    run_id: string;
    baseline_run_id: string;
    comparison_type: string;
    title: string;
    summary: string;
    bullets: string[];
    score_breakdown: {
      metrics: {
        total: number;
        components: Record<string, { score: number; [key: string]: unknown }>;
      };
      semantics: {
        total: number;
        components: Record<string, { score: number; [key: string]: unknown }>;
      };
      context: {
        total: number;
        components: Record<string, { score: number; [key: string]: unknown }>;
      };
      total: number;
    };
    rank: number;
    insight_score: number;
    is_primary: boolean;
  }[];
};

export type RunSurfaceCapabilities = {
  comparison_eligibility_contract: RunListBoundaryContract;
  discovery: {
    shared_contracts: {
      contract_key: string;
      contract_kind: string;
      title: string;
      summary: string;
      source_of_truth: string;
      version: string | null;
      discovery_flow?: string | null;
      related_family_keys: string[];
      member_keys: string[];
      ui_surfaces?: string[];
      schema_sources?: string[];
      policy?: {
        applies_to: string[];
        policy_key: string;
        policy_mode: string;
        source_of_truth: string;
      } | null;
      enforcement?: {
        enforcement_points: string[];
        fallback_behavior: string;
        level: string;
        source_of_truth: string;
      } | null;
      surface_rules?: {
        rule_key: string;
        surface_key: string;
        surface_label: string;
        enforcement_point: string;
        enforcement_mode: string;
        level: string;
        fallback_behavior: string;
        source_of_truth: string;
      }[];
      schema_detail?: Record<string, unknown>;
    }[];
  };
};

export type RunSurfaceSharedContract = RunSurfaceCapabilities["discovery"]["shared_contracts"][number];
export type RunSurfaceCapabilityPolicy = NonNullable<RunSurfaceSharedContract["policy"]>;
export type RunSurfaceCapabilityEnforcement = NonNullable<RunSurfaceSharedContract["enforcement"]>;
export type RunSurfaceCapabilitySurfaceRule = NonNullable<RunSurfaceSharedContract["surface_rules"]>[number];
export type RunSurfaceCapabilityFamilyKey =
  | "comparison_eligibility"
  | "strategy_schema"
  | "collection_query"
  | "provenance_semantics"
  | "execution_controls";
export type RunSurfaceCapabilitySurfaceKey =
  | "run_list_metric_tiles"
  | "boundary_note_panels"
  | "order_workflow_gates"
  | "strategy_catalog_cards"
  | "preset_parameter_editor"
  | "preset_revision_semantic_diffs"
  | "collection_query_discovery_panels"
  | "collection_expression_builders"
  | "collection_parameter_domain_pickers"
  | "run_strategy_snapshot"
  | "reference_provenance_panels"
  | "benchmark_artifact_summaries"
  | "rerun_and_stop_controls"
  | "compare_selection_workflow"
  | "order_replace_cancel_actions";
export type RunSurfaceCapabilityFamily = {
  family_key: RunSurfaceCapabilityFamilyKey;
  title: string;
  summary: string;
  ui_surfaces: string[];
  schema_sources: string[];
  discovery_flow: string;
  policy: RunSurfaceCapabilityPolicy;
  enforcement: RunSurfaceCapabilityEnforcement;
  surface_rules: RunSurfaceCapabilitySurfaceRule[];
};
export type RunSurfaceCapabilityFamilyContract = RunSurfaceSharedContract & {
  discovery_flow: string | null;
  ui_surfaces: string[];
  schema_sources: string[];
  policy: RunSurfaceCapabilityPolicy;
  enforcement: RunSurfaceCapabilityEnforcement;
  surface_rules: RunSurfaceCapabilitySurfaceRule[];
  schema_detail: Record<string, unknown>;
};
export type RunSurfaceCapabilitySchemaContract = RunSurfaceSharedContract & {
  contract_kind: "schema_metadata";
  schema_detail: Record<string, unknown>;
};
export type RunSurfaceSubresourceContract = RunSurfaceSharedContract & {
  contract_kind: "run_subresource";
  schema_detail: Record<string, unknown>;
};
export type RunSurfaceCollectionQueryContract = RunSurfaceSharedContract & {
  contract_kind: "query_collection_schema";
  schema_detail: Record<string, unknown>;
};
export type RunSurfaceCollectionQueryParameterDomain = {
  key: string | null;
  source: string | null;
  values: string[];
  enumSource: {
    kind: string | null;
    surfaceKey: string | null;
    path: string[];
  } | null;
};
export type RunSurfaceCollectionQueryParameter = {
  key: string;
  kind: string;
  description: string;
  examples: string[];
  domain: RunSurfaceCollectionQueryParameterDomain | null;
};
export type RunSurfaceCollectionQueryElementField = {
  key: string;
  queryExposed: boolean;
  valueType: string;
  valuePath: string[];
  valueRoot: boolean;
  title: string | null;
  description: string | null;
  operators: {
    key: string;
    label: string;
    description: string;
    valueShape: string;
  }[];
};
export type RunSurfaceCollectionQuerySchema = {
  path: string[];
  pathTemplate: string[];
  label: string;
  collectionKind: string;
  itemKind: string;
  filterKeys: string[];
  description: string;
  parameters: RunSurfaceCollectionQueryParameter[];
  elementSchema: RunSurfaceCollectionQueryElementField[];
};
export type RunSurfaceCollectionQueryParameterDomainDescriptor = {
  parameterKey: string;
  parameterKind: string;
  collectionLabel: string;
  collectionPath: string[];
  collectionPathTemplate: string[];
  domain: RunSurfaceCollectionQueryParameterDomain | null;
  surfaceKey: string;
};
export type RunSurfaceCollectionQueryExpressionAuthoring = {
  predicateRefs: {
    registryField: string;
    referenceField: string;
  };
  predicateTemplates: {
    registryField: string;
    templateField: string;
    parametersField: string;
    bindingsField: string;
    bindingReferenceField: string;
  };
  collectionNodes: {
    field: string;
    pathField: string;
    pathTemplateField: string;
    bindingsField: string;
    quantifierField: string;
  };
};

export type ComparisonScoreSection = "metrics" | "semantics" | "context";
export type ProvenanceArtifactLineDetailView = "stats" | "context";
export type ProvenanceArtifactLineMicroView = "structure" | "signal" | "note";

export type ComparisonScoreLinkTarget = {
  narrativeRunId: string;
  section: ComparisonScoreSection;
  componentKey: string;
  source: ComparisonScoreLinkSource;
  originRunId: string | null;
  subFocusKey: string | null;
  detailExpanded: boolean | null;
  artifactDetailExpanded: boolean | null;
  artifactLineDetailExpanded: boolean | null;
  artifactLineDetailView: ProvenanceArtifactLineDetailView | null;
  artifactLineMicroView: ProvenanceArtifactLineMicroView | null;
  artifactLineNotePage: number | null;
  artifactLineDetailHoverKey: string | null;
  artifactLineDetailScrubStep: number | null;
  tooltipKey: string | null;
  artifactHoverKey: string | null;
};

export type ComparisonScoreLinkedRunRole = "baseline" | "target";

export type ComparisonScoreLinkSource =
  | "metric"
  | "drillback"
  | "overview"
  | "provenance"
  | "run_card"
  | "run_list";

export type ComparisonHistoryWriteMode = "push" | "replace" | "skip";

export type ComparisonScoreDrillBackOptions = {
  subFocusKey?: string | null;
  tooltipKey?: string | null;
  detailExpanded?: boolean | null;
  artifactDetailExpanded?: boolean | null;
  artifactLineDetailExpanded?: boolean | null;
  artifactLineDetailView?: ProvenanceArtifactLineDetailView | null;
  artifactLineMicroView?: ProvenanceArtifactLineMicroView | null;
  artifactLineNotePage?: number | null;
  artifactLineDetailHoverKey?: string | null;
  artifactLineDetailScrubStep?: number | null;
  artifactHoverKey?: string | null;
  historyMode?: ComparisonHistoryWriteMode;
};

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

export type ProviderProvenanceExportJobEntry = {
  job_id: string;
  export_scope: string;
  export_format: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
  completed_at?: string | null;
  exported_at?: string | null;
  expires_at?: string | null;
  focus_key?: string | null;
  focus_label?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  result_count: number;
  provider_provenance_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  filter_summary?: string | null;
  filters: Record<string, unknown>;
  requested_by_tab_id?: string | null;
  requested_by_tab_label?: string | null;
  available_delivery_targets: string[];
  routing_policy_id?: string | null;
  routing_policy_summary?: string | null;
  routing_targets: string[];
  approval_policy_id?: string | null;
  approval_required: boolean;
  approval_state: string;
  approval_summary?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
  approval_note?: string | null;
  escalation_count: number;
  last_escalated_at?: string | null;
  last_escalated_by?: string | null;
  last_escalation_reason?: string | null;
  last_delivery_targets: string[];
  last_delivery_status?: string | null;
  last_delivery_summary?: string | null;
  artifact_id?: string | null;
  content_length: number;
  content?: string;
};

export type ProviderProvenanceExportJobAuditRecord = {
  audit_id: string;
  job_id: string;
  action: string;
  recorded_at: string;
  expires_at?: string | null;
  export_scope?: string | null;
  export_format?: string | null;
  focus_key?: string | null;
  focus_label?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  market_data_provider?: string | null;
  requested_by_tab_id?: string | null;
  requested_by_tab_label?: string | null;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  routing_policy_id?: string | null;
  routing_targets: string[];
  approval_policy_id?: string | null;
  approval_required: boolean;
  approval_state?: string | null;
  approval_summary?: string | null;
  approved_by?: string | null;
  delivery_targets: string[];
  delivery_status?: string | null;
  delivery_summary?: string | null;
  detail: string;
};

export type ProviderProvenanceExportJobListPayload = {
  items: ProviderProvenanceExportJobEntry[];
  total: number;
};

export type ProviderProvenanceExportJobHistoryPayload = {
  job: ProviderProvenanceExportJobEntry;
  history: ProviderProvenanceExportJobAuditRecord[];
};

export type ProviderProvenanceExportJobEscalationResult = {
  export_job: ProviderProvenanceExportJobEntry;
  audit_record: ProviderProvenanceExportJobAuditRecord;
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
};

export type ProviderProvenanceExportJobPolicyResult = {
  export_job: ProviderProvenanceExportJobEntry;
  audit_record: ProviderProvenanceExportJobAuditRecord;
};

export type ProviderProvenanceExportAnalyticsRollupEntry = {
  key: string;
  label: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  download_count: number;
  focus_count: number;
  requested_by_tab_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  last_exported_at?: string | null;
  last_downloaded_at?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
};

export type ProviderProvenanceExportDriftSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  focus_count: number;
  provider_label_count: number;
  provider_labels: string[];
  vendor_fields: string[];
  drift_intensity: number;
};

export type ProviderProvenanceExportBurnUpSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  export_count: number;
  result_count: number;
  provider_provenance_count: number;
  download_count: number;
  cumulative_export_count: number;
  cumulative_result_count: number;
  cumulative_provider_provenance_count: number;
  cumulative_download_count: number;
};

export type ProviderProvenanceExportTimeSeriesPayload = {
  bucket_size: string;
  window_days: number;
  window_started_at: string;
  window_ended_at: string;
  provider_drift: {
    series: ProviderProvenanceExportDriftSeriesEntry[];
    summary: {
      peak_bucket_key?: string | null;
      peak_bucket_label?: string | null;
      peak_export_count: number;
      peak_provider_provenance_count: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_export_count: number;
      latest_provider_provenance_count: number;
    };
  };
  export_burn_up: {
    series: ProviderProvenanceExportBurnUpSeriesEntry[];
    summary: {
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      cumulative_export_count: number;
      cumulative_result_count: number;
      cumulative_provider_provenance_count: number;
      cumulative_download_count: number;
    };
  };
};

export type ProviderProvenanceSchedulerHealthSnapshot = {
  generated_at: string;
  enabled: boolean;
  status: string;
  summary: string;
  interval_seconds: number;
  batch_limit: number;
  last_cycle_started_at?: string | null;
  last_cycle_finished_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
  last_error?: string | null;
  cycle_count: number;
  success_count: number;
  failure_count: number;
  consecutive_failure_count: number;
  last_executed_count: number;
  total_executed_count: number;
  due_report_count: number;
  oldest_due_at?: string | null;
  max_due_lag_seconds: number;
  issues: string[];
};

export type ProviderProvenanceSchedulerHealthHistoryEntry = {
  record_id: string;
  scheduler_key: string;
  recorded_at: string;
  expires_at?: string | null;
  enabled: boolean;
  status: string;
  summary: string;
  interval_seconds: number;
  batch_limit: number;
  last_cycle_started_at?: string | null;
  last_cycle_finished_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
  last_error?: string | null;
  cycle_count: number;
  success_count: number;
  failure_count: number;
  consecutive_failure_count: number;
  last_executed_count: number;
  total_executed_count: number;
  due_report_count: number;
  oldest_due_at?: string | null;
  max_due_lag_seconds: number;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  issues: string[];
};

export type ProviderProvenanceSchedulerHealthHistoryPayload = {
  generated_at: string;
  query: {
    status?: string | null;
    limit: number;
    offset: number;
  };
  current: ProviderProvenanceSchedulerHealthSnapshot;
  items: ProviderProvenanceSchedulerHealthHistoryEntry[];
  total: number;
  returned: number;
  has_more: boolean;
  next_offset?: number | null;
  previous_offset?: number | null;
};

export type ProviderProvenanceSchedulerAlertHistoryPayload = {
  generated_at: string;
  query: {
    category?: string | null;
    status?: string | null;
    narrative_facet?: string | null;
    search?: string | null;
    limit: number;
    offset: number;
  };
  available_filters: {
    categories: string[];
    statuses: string[];
    narrative_facets: string[];
  };
  summary: {
    total_occurrences: number;
    active_count: number;
    resolved_count: number;
    by_category: {
      category: string;
      total: number;
      active_count: number;
      resolved_count: number;
    }[];
  };
  retrieval_clusters: {
    cluster_id?: string | null;
    rank: number;
    label?: string | null;
    summary?: string | null;
    occurrence_count: number;
    top_score: number;
    average_score: number;
    average_similarity_pct: number;
    semantic_concepts: string[];
    vector_terms: string[];
    categories: string[];
    statuses: string[];
    narrative_facets: string[];
    top_occurrence_id?: string | null;
    top_occurrence_summary?: string | null;
    occurrence_ids: string[];
  }[];
  search_summary?: {
    query_id?: string | null;
    query?: string | null;
    mode?: string | null;
    token_count: number;
    matched_occurrences: number;
    top_score: number;
    max_term_coverage_pct: number;
    phrase_match_count: number;
    operator_count: number;
    semantic_concept_count: number;
    negated_term_count: number;
    boolean_operator_count: number;
    indexed_occurrence_count: number;
    indexed_term_count: number;
    persistence_mode?: string | null;
    relevance_model?: string | null;
    retrieval_cluster_mode?: string | null;
    retrieval_cluster_count: number;
    top_cluster_label?: string | null;
    parsed_terms: string[];
    parsed_phrases: string[];
    parsed_operators: string[];
    semantic_concepts: string[];
    query_plan: string[];
  } | null;
  search_analytics?: {
    query_id: string;
    recorded_at: string;
    recent_query_count: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    relevant_feedback_count: number;
    not_relevant_feedback_count: number;
    helpful_feedback_ratio_pct: number;
    learned_relevance_active: boolean;
    tuning_profile_version?: string | null;
    tuned_feature_count: number;
    channel_adjustments: {
      lexical: number;
      semantic: number;
      operator: number;
    };
    top_field_adjustments: {
      field: string;
      score: number;
    }[];
    top_semantic_adjustments: {
      concept: string;
      score: number;
    }[];
    top_operator_adjustments: {
      operator: string;
      score: number;
    }[];
    recent_queries: {
      query_id: string;
      recorded_at: string;
      query: string;
      matched_occurrences: number;
      top_score: number;
      relevance_model?: string | null;
    }[];
    recent_feedback: {
      feedback_id: string;
      recorded_at: string;
      occurrence_id: string;
      signal: string;
      moderation_status: string;
      matched_fields: string[];
      semantic_concepts: string[];
      operator_hits: string[];
      note?: string | null;
      moderation_note?: string | null;
    }[];
  } | null;
  items: (OperatorAlertEntry & {
    narrative: {
      facet?: string | null;
      facet_flags: string[];
      narrative_mode?: string | null;
      can_reconstruct_narrative: boolean;
      has_post_resolution_history: boolean;
      occurrence_record_count: number;
      post_resolution_record_count: number;
      status_sequence: string[];
      post_resolution_status_sequence: string[];
      narrative_window_ended_at?: string | null;
      next_occurrence_detected_at?: string | null;
    };
    search_match?: {
      score: number;
      matched_terms: string[];
      matched_phrases: string[];
      matched_fields: string[];
      term_coverage_pct: number;
      phrase_match: boolean;
      exact_match: boolean;
      highlights: string[];
      semantic_concepts: string[];
      operator_hits: string[];
      lexical_score: number;
      semantic_score: number;
      operator_score: number;
      learned_score: number;
      feedback_signal_count: number;
      tuning_signals: string[];
      relevance_model?: string | null;
      ranking_reason?: string | null;
    } | null;
    retrieval_cluster?: {
      cluster_id?: string | null;
      rank: number;
      label?: string | null;
      similarity_pct: number;
      semantic_concepts: string[];
      vector_terms: string[];
    } | null;
  })[];
  total: number;
  returned: number;
  has_more: boolean;
  next_offset?: number | null;
  previous_offset?: number | null;
};

export type ProviderProvenanceSchedulerSearchFeedbackResult = {
  feedback_id: string;
  query_id: string;
  query: string;
  occurrence_id: string;
  signal: string;
  moderation_status: string;
  feedback_count: number;
  pending_feedback_count: number;
  approved_feedback_count: number;
  rejected_feedback_count: number;
  relevant_feedback_count: number;
  not_relevant_feedback_count: number;
  helpful_feedback_ratio_pct: number;
  learned_relevance_hint?: string | null;
};

export type ProviderProvenanceSchedulerSearchFeedbackModerationResult = {
  feedback_id: string;
  query_id: string;
  occurrence_id: string;
  moderation_status: string;
  moderated_at?: string | null;
  moderated_by?: string | null;
  moderation_note?: string | null;
  pending_feedback_count: number;
  approved_feedback_count: number;
  rejected_feedback_count: number;
  learned_relevance_hint?: string | null;
};

export type ProviderProvenanceSchedulerSearchDashboardPayload = {
  generated_at: string;
  query: {
    search?: string | null;
    moderation_status?: string | null;
    signal?: string | null;
    query_limit: number;
    feedback_limit: number;
  };
  available_filters: {
    moderation_statuses: string[];
    signals: string[];
  };
  summary: {
    query_count: number;
    distinct_query_count: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    relevant_feedback_count: number;
    not_relevant_feedback_count: number;
  };
  top_queries: {
    query: string;
    query_ids: string[];
    search_count: number;
    last_recorded_at: string;
    top_score: number;
    matched_occurrences_total: number;
    feedback_count: number;
    pending_feedback_count: number;
    approved_feedback_count: number;
    rejected_feedback_count: number;
    semantic_concepts: string[];
    parsed_operators: string[];
    relevance_models: string[];
  }[];
  feedback_items: {
    feedback_id: string;
    recorded_at: string;
    query_id: string;
    query: string;
    occurrence_id: string;
    signal: string;
    actor?: string | null;
    note?: string | null;
    moderation_status: string;
    moderation_note?: string | null;
    moderated_at?: string | null;
    moderated_by?: string | null;
    matched_fields: string[];
    semantic_concepts: string[];
    operator_hits: string[];
    score: number;
  }[];
};

export type ProviderProvenanceSchedulerHealthStatusSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  cycle_count: number;
  healthy_count: number;
  lagging_count: number;
  failed_count: number;
  disabled_count: number;
  starting_count: number;
  dominant_status: string;
  dominant_count: number;
  latest_status: string;
  latest_summary: string;
  executed_report_count: number;
};

export type ProviderProvenanceSchedulerLagTrendSeriesEntry = {
  bucket_key: string;
  bucket_label: string;
  started_at: string;
  ended_at: string;
  cycle_count: number;
  peak_lag_seconds: number;
  latest_lag_seconds: number;
  average_lag_seconds: number;
  peak_due_report_count: number;
  latest_due_report_count: number;
  failure_count: number;
  executed_report_count: number;
};

export type ProviderProvenanceSchedulerHealthTimeSeriesPayload = {
  bucket_size: string;
  window_days: number;
  window_started_at: string;
  window_ended_at: string;
  health_status: {
    series: ProviderProvenanceSchedulerHealthStatusSeriesEntry[];
    summary: {
      peak_cycle_bucket_key?: string | null;
      peak_cycle_bucket_label?: string | null;
      peak_cycle_count: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_status: string;
      latest_cycle_count: number;
    };
  };
  lag_trend: {
    series: ProviderProvenanceSchedulerLagTrendSeriesEntry[];
    summary: {
      peak_lag_bucket_key?: string | null;
      peak_lag_bucket_label?: string | null;
      peak_lag_seconds: number;
      latest_bucket_key?: string | null;
      latest_bucket_label?: string | null;
      latest_lag_seconds: number;
      latest_due_report_count: number;
      latest_failure_count: number;
    };
  };
};

export type ProviderProvenanceSchedulerHealthAnalyticsPayload = {
  generated_at: string;
  query: {
    status?: string | null;
    window_days: number;
    history_limit: number;
    drilldown_bucket_key?: string | null;
    drilldown_history_limit: number;
  };
  current: ProviderProvenanceSchedulerHealthSnapshot;
  totals: {
    record_count: number;
    healthy_count: number;
    lagging_count: number;
    failed_count: number;
    disabled_count: number;
    starting_count: number;
    executed_report_count: number;
    peak_lag_seconds: number;
    peak_due_report_count: number;
  };
  available_filters: {
    statuses: string[];
  };
  time_series: ProviderProvenanceSchedulerHealthTimeSeriesPayload;
  drill_down?: {
    bucket_key: string;
    bucket_label: string;
    bucket_size: "hour";
    window_started_at: string;
    window_ended_at: string;
    total_record_count: number;
    history_limit: number;
    history: ProviderProvenanceSchedulerHealthHistoryEntry[];
    health_status: ProviderProvenanceSchedulerHealthTimeSeriesPayload["health_status"];
    lag_trend: ProviderProvenanceSchedulerHealthTimeSeriesPayload["lag_trend"];
  } | null;
  recent_history: ProviderProvenanceSchedulerHealthHistoryEntry[];
};

export type ProviderProvenanceSchedulerHealthExportPayload = {
  content: string;
  content_type: string;
  exported_at: string;
  filename: string;
  format: "json" | "csv";
  record_count: number;
  total_count: number;
};

export type ProviderProvenanceExportAnalyticsPayload = {
  generated_at: string;
  query: {
    focus_key?: string | null;
    symbol?: string | null;
    timeframe?: string | null;
    provider_label?: string | null;
    vendor_field?: string | null;
    market_data_provider?: string | null;
    venue?: string | null;
    requested_by_tab_id?: string | null;
    status?: string | null;
    search?: string | null;
    result_limit: number;
    window_days: number;
  };
  totals: {
    export_count: number;
    result_count: number;
    provider_provenance_count: number;
    download_count: number;
    unique_focus_count: number;
    provider_label_count: number;
    vendor_field_count: number;
    market_data_provider_count: number;
    requester_count: number;
  };
  available_filters: {
    provider_labels: string[];
    vendor_fields: string[];
    market_data_providers: string[];
    venues: string[];
    timeframes: string[];
    requested_by_tab_ids: string[];
    statuses: string[];
  };
  rollups: {
    providers: ProviderProvenanceExportAnalyticsRollupEntry[];
    vendor_fields: ProviderProvenanceExportAnalyticsRollupEntry[];
    focuses: ProviderProvenanceExportAnalyticsRollupEntry[];
    requesters: ProviderProvenanceExportAnalyticsRollupEntry[];
  };
  time_series: ProviderProvenanceExportTimeSeriesPayload;
  recent_exports: ProviderProvenanceExportJobEntry[];
};

export type ProviderProvenanceAnalyticsWorkspaceQuery = {
  focus_scope: "current_focus" | "all_focuses";
  focus_key?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  provider_label?: string | null;
  vendor_field?: string | null;
  market_data_provider?: string | null;
  venue?: string | null;
  requested_by_tab_id?: string | null;
  status?: string | null;
  scheduler_alert_category?: string | null;
  scheduler_alert_status?: string | null;
  scheduler_alert_narrative_facet?: string | null;
  search?: string | null;
  result_limit: number;
  window_days: number;
};

export type ProviderProvenanceDashboardLayout = {
  highlight_panel:
    | "overview"
    | "drift"
    | "burn_up"
    | "rollups"
    | "recent_exports"
    | "scheduler_alerts";
  show_rollups: boolean;
  show_time_series: boolean;
  show_recent_exports: boolean;
  governance_queue_view?: ProviderProvenanceSchedulerNarrativeGovernanceQueueView | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceQueueView = {
  queue_state?: "pending_approval" | "ready_to_apply" | "completed" | string | null;
  item_type?: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string | null;
  approval_lane?: string | null;
  approval_priority?: string | null;
  policy_template_id?: string | null;
  policy_catalog_id?: string | null;
  source_hierarchy_step_template_id?: string | null;
  source_hierarchy_step_template_name?: string | null;
  search?: string | null;
  sort?: string | null;
};

export type ProviderProvenanceWorkspaceFocus = {
  provider?: string | null;
  venue?: string | null;
  instrument_id?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  provider_provenance_incident_count?: number;
};

export type ProviderProvenanceAnalyticsPresetEntry = {
  preset_id: string;
  name: string;
  description: string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceAnalyticsPresetListPayload = {
  items: ProviderProvenanceAnalyticsPresetEntry[];
  total: number;
};

export type ProviderProvenanceDashboardViewEntry = {
  view_id: string;
  name: string;
  description: string;
  preset_id?: string | null;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceDashboardViewListPayload = {
  items: ProviderProvenanceDashboardViewEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportViewEntry = {
  view_id: string;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportViewListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportViewEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportViewRevisionEntry = {
  revision_id: string;
  view_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload = {
  view: ProviderProvenanceSchedulerStitchedReportViewEntry;
  history: ProviderProvenanceSchedulerStitchedReportViewRevisionEntry[];
};

export type ProviderProvenanceSchedulerStitchedReportViewAuditRecord = {
  audit_id: string;
  view_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  occurrence_limit: number;
  history_limit: number;
  drilldown_history_limit: number;
  filter_summary: string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportViewAuditListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportViewAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry = {
  registry_id: string;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry = {
  revision_id: string;
  registry_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload = {
  registry: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry;
  history: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionEntry[];
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord = {
  audit_id: string;
  registry_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  description: string;
  queue_view: ProviderProvenanceSchedulerNarrativeGovernanceQueueView;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  default_policy_catalog_id?: string | null;
  default_policy_catalog_name?: string | null;
  status: "active" | "deleted" | string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditListPayload = {
  items: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeTemplateEntry = {
  template_id: string;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeTemplateEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry = {
  revision_id: string;
  template_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload = {
  template: ProviderProvenanceSchedulerNarrativeTemplateEntry;
  history: ProviderProvenanceSchedulerNarrativeTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult = {
  item_id: string;
  item_name?: string | null;
  outcome: "applied" | "skipped" | "failed" | string;
  status?: "active" | "deleted" | string | null;
  current_revision_id?: string | null;
  message?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeBulkGovernanceResult = {
  item_type: "template" | "registry" | "stitched_report_view" | string;
  action: "delete" | "restore" | string;
  reason: string;
  requested_count: number;
  applied_count: number;
  skipped_count: number;
  failed_count: number;
  results: ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePreviewItem = {
  item_id: string;
  item_name?: string | null;
  status?: "active" | "deleted" | string | null;
  current_revision_id?: string | null;
  apply_revision_id?: string | null;
  rollback_revision_id?: string | null;
  outcome: "changed" | "skipped" | "failed" | string;
  message?: string | null;
  changed_fields: string[];
  field_diffs: Record<string, { before?: unknown; after?: unknown }>;
  current_snapshot: Record<string, unknown>;
  proposed_snapshot: Record<string, unknown>;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate = {
  policy_template_id: string;
  name: string;
  description: string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry = {
  revision_id: string;
  policy_template_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload = {
  policy_template: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate;
  history: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord = {
  audit_id: string;
  policy_template_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog = {
  catalog_id: string;
  name: string;
  description: string;
  policy_template_ids: string[];
  policy_template_names: string[];
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry = {
  revision_id: string;
  catalog_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  policy_template_ids: string[];
  policy_template_names: string[];
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  status: "active" | "deleted" | string;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload = {
  current: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog;
  history: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord = {
  audit_id: string;
  catalog_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  status: "active" | "deleted" | string;
  default_policy_template_id?: string | null;
  default_policy_template_name?: string | null;
  policy_template_ids: string[];
  policy_template_names: string[];
  item_type_scope: "any" | "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action_scope: "any" | "delete" | "restore" | "update" | string;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  guidance?: string | null;
  hierarchy_steps: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep[];
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate = {
  hierarchy_step_template_id: string;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry = {
  revision_id: string;
  hierarchy_step_template_id: string;
  action: string;
  reason: string;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  recorded_at: string;
  source_revision_id?: string | null;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload = {
  current: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate;
  history: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionEntry[];
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord = {
  audit_id: string;
  hierarchy_step_template_id: string;
  action: string;
  recorded_at: string;
  reason: string;
  detail: string;
  revision_id?: string | null;
  source_revision_id?: string | null;
  name: string;
  description: string;
  item_type: "template" | "registry" | string;
  step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep;
  origin_catalog_id?: string | null;
  origin_catalog_name?: string | null;
  origin_step_id?: string | null;
  governance_policy_template_id?: string | null;
  governance_policy_template_name?: string | null;
  governance_policy_catalog_id?: string | null;
  governance_policy_catalog_name?: string | null;
  governance_approval_lane?: string | null;
  governance_approval_priority?: string | null;
  governance_policy_guidance?: string | null;
  status: "active" | "deleted" | string;
  actor_tab_id?: string | null;
  actor_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep = {
  step_id?: string | null;
  source_template_id?: string | null;
  source_template_name?: string | null;
  item_type: "template" | "registry" | string;
  action: "update" | string;
  item_ids: string[];
  item_names: string[];
  name_prefix?: string | null;
  name_suffix?: string | null;
  description_append?: string | null;
  query_patch: Record<string, unknown>;
  layout_patch: Record<string, unknown>;
  template_id?: string | null;
  clear_template_link: boolean;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlan = {
  plan_id: string;
  item_type: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry" | string;
  action: "delete" | "restore" | "update" | "rollback" | string;
  reason: string;
  status: "previewed" | "approved" | "applied" | "rolled_back" | string;
  queue_state: "pending_approval" | "ready_to_apply" | "completed" | string;
  policy_template_id?: string | null;
  policy_template_name?: string | null;
  policy_catalog_id?: string | null;
  policy_catalog_name?: string | null;
  approval_lane: string;
  approval_priority: "low" | "normal" | "high" | "critical" | string;
  policy_guidance?: string | null;
  source_hierarchy_step_template_id?: string | null;
  source_hierarchy_step_template_name?: string | null;
  hierarchy_key?: string | null;
  hierarchy_name?: string | null;
  hierarchy_position?: number | null;
  hierarchy_total?: number | null;
  request_payload: Record<string, unknown>;
  target_ids: string[];
  preview_requested_count: number;
  preview_changed_count: number;
  preview_skipped_count: number;
  preview_failed_count: number;
  preview_items: ProviderProvenanceSchedulerNarrativeGovernancePreviewItem[];
  rollback_ready_count: number;
  rollback_summary: string;
  created_at: string;
  updated_at: string;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  approved_at?: string | null;
  approved_by_tab_id?: string | null;
  approved_by_tab_label?: string | null;
  approval_note?: string | null;
  applied_at?: string | null;
  applied_by_tab_id?: string | null;
  applied_by_tab_label?: string | null;
  applied_result?: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | null;
  rolled_back_at?: string | null;
  rolled_back_by_tab_id?: string | null;
  rolled_back_by_tab_label?: string | null;
  rollback_note?: string | null;
  rollback_result?: ProviderProvenanceSchedulerNarrativeBulkGovernanceResult | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanListPayload = {
  items: ProviderProvenanceSchedulerNarrativeGovernancePlan[];
  total: number;
  pending_approval_count: number;
  ready_to_apply_count: number;
  completed_count: number;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult = {
  plan_id: string;
  action: string;
  outcome: "succeeded" | "skipped" | "failed" | string;
  status?: string | null;
  queue_state?: string | null;
  message?: string | null;
  plan?: ProviderProvenanceSchedulerNarrativeGovernancePlan | null;
};

export type ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult = {
  action: string;
  requested_count: number;
  succeeded_count: number;
  skipped_count: number;
  failed_count: number;
  results: ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult[];
};

export type ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult = {
  catalog_id: string;
  catalog_name: string;
  hierarchy_key: string;
  hierarchy_name: string;
  plan_count: number;
  summary: string;
  plans: ProviderProvenanceSchedulerNarrativeGovernancePlan[];
};

export type ProviderProvenanceSchedulerNarrativeRegistryEntry = {
  registry_id: string;
  name: string;
  description: string;
  template_id?: string | null;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  created_at: string;
  updated_at: string;
  current_revision_id?: string | null;
  revision_count: number;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
  deleted_at?: string | null;
  deleted_by_tab_id?: string | null;
  deleted_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeRegistryListPayload = {
  items: ProviderProvenanceSchedulerNarrativeRegistryEntry[];
  total: number;
};

export type ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry = {
  revision_id: string;
  registry_id: string;
  action: string;
  reason: string;
  source_revision_id?: string | null;
  name: string;
  description: string;
  template_id?: string | null;
  status: "active" | "deleted" | string;
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  recorded_at: string;
  recorded_by_tab_id?: string | null;
  recorded_by_tab_label?: string | null;
};

export type ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload = {
  registry: ProviderProvenanceSchedulerNarrativeRegistryEntry;
  history: ProviderProvenanceSchedulerNarrativeRegistryRevisionEntry[];
};

export type ProviderProvenanceScheduledReportEntry = {
  report_id: string;
  name: string;
  description: string;
  preset_id?: string | null;
  view_id?: string | null;
  cadence: "daily" | "weekly";
  status: "scheduled" | "paused";
  query: ProviderProvenanceAnalyticsWorkspaceQuery;
  focus: ProviderProvenanceWorkspaceFocus;
  filter_summary: string;
  layout: ProviderProvenanceDashboardLayout;
  created_at: string;
  updated_at: string;
  next_run_at?: string | null;
  last_run_at?: string | null;
  last_export_job_id?: string | null;
  created_by_tab_id?: string | null;
  created_by_tab_label?: string | null;
};

export type ProviderProvenanceScheduledReportListPayload = {
  items: ProviderProvenanceScheduledReportEntry[];
  total: number;
};

export type ProviderProvenanceScheduledReportAuditRecord = {
  audit_id: string;
  report_id: string;
  action: string;
  recorded_at: string;
  expires_at?: string | null;
  source_tab_id?: string | null;
  source_tab_label?: string | null;
  export_job_id?: string | null;
  detail: string;
};

export type ProviderProvenanceScheduledReportHistoryPayload = {
  report: ProviderProvenanceScheduledReportEntry;
  history: ProviderProvenanceScheduledReportAuditRecord[];
};

export type ProviderProvenanceScheduledReportRunResult = {
  report: ProviderProvenanceScheduledReportEntry;
  export_job: ProviderProvenanceExportJobEntry;
};

export type ProviderProvenanceScheduledReportRunDuePayload = {
  generated_at: string;
  due_before: string;
  executed_count: number;
  items: ProviderProvenanceScheduledReportRunResult[];
};

export type OperatorAlertMarketContextFieldProvenance = {
  scope?: string | null;
  path?: string | null;
};

export type OperatorAlertMarketContextProvenance = {
  provider?: string | null;
  vendor_field?: string | null;
  symbol?: OperatorAlertMarketContextFieldProvenance | null;
  symbols?: OperatorAlertMarketContextFieldProvenance | null;
  timeframe?: OperatorAlertMarketContextFieldProvenance | null;
  primary_focus?: OperatorAlertMarketContextFieldProvenance | null;
};

export type OperatorAlertPrimaryFocus = {
  symbol?: string | null;
  timeframe?: string | null;
  candidate_symbols: string[];
  candidate_count: number;
  policy: string;
  reason?: string | null;
};

export type OperatorAlertEntry = {
  alert_id: string;
  severity: string;
  category: string;
  summary: string;
  detail: string;
  detected_at: string;
  run_id?: string | null;
  session_id?: string | null;
  symbol?: string | null;
  symbols: string[];
  timeframe?: string | null;
  primary_focus?: OperatorAlertPrimaryFocus | null;
  occurrence_id?: string | null;
  timeline_key?: string | null;
  timeline_position?: number | null;
  timeline_total?: number | null;
  status: string;
  resolved_at?: string | null;
  source: string;
  delivery_targets: string[];
};

export type OperatorVisibility = {
  generated_at: string;
  alerts: OperatorAlertEntry[];
  alert_history: OperatorAlertEntry[];
  incident_events: {
    event_id: string;
    alert_id: string;
    timestamp: string;
    kind: string;
    severity: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    symbol?: string | null;
    symbols: string[];
    timeframe?: string | null;
    primary_focus?: OperatorAlertPrimaryFocus | null;
    source: string;
    paging_policy_id: string;
    paging_provider?: string | null;
    delivery_targets: string[];
    escalation_targets: string[];
    delivery_state: string;
    acknowledgment_state: string;
    acknowledged_at?: string | null;
    acknowledged_by?: string | null;
    acknowledgment_reason?: string | null;
    escalation_level: number;
    escalation_state: string;
    last_escalated_at?: string | null;
    last_escalated_by?: string | null;
    escalation_reason?: string | null;
    next_escalation_at?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    provider_workflow_reference?: string | null;
    external_status: string;
    external_last_synced_at?: string | null;
    paging_status: string;
    provider_workflow_state: string;
    provider_workflow_action?: string | null;
    provider_workflow_last_attempted_at?: string | null;
    remediation: {
      state: string;
      kind?: string | null;
      owner?: string | null;
      summary?: string | null;
      detail?: string | null;
      runbook?: string | null;
      requested_at?: string | null;
      requested_by?: string | null;
      last_attempted_at?: string | null;
      provider?: string | null;
      reference?: string | null;
      provider_payload: Record<string, unknown>;
      provider_payload_updated_at?: string | null;
      provider_recovery: {
        lifecycle_state: string;
        provider?: string | null;
        job_id?: string | null;
        reference?: string | null;
        workflow_reference?: string | null;
        summary?: string | null;
        detail?: string | null;
        channels: string[];
        symbols: string[];
        timeframe?: string | null;
        market_context_provenance?: OperatorAlertMarketContextProvenance | null;
        updated_at?: string | null;
        verification: {
          state: string;
          checked_at?: string | null;
          summary?: string | null;
          issues: string[];
        };
        telemetry: {
          source: string;
          state: string;
          progress_percent?: number | null;
          attempt_count: number;
          current_step?: string | null;
          last_message?: string | null;
          last_error?: string | null;
          external_run_id?: string | null;
          job_url?: string | null;
          started_at?: string | null;
          finished_at?: string | null;
          updated_at?: string | null;
        };
        status_machine: {
          state: string;
          workflow_state: string;
          workflow_action?: string | null;
          job_state: string;
          sync_state: string;
          last_event_kind?: string | null;
          last_event_at?: string | null;
          last_detail?: string | null;
          attempt_number: number;
        };
        provider_schema_kind?: string | null;
        pagerduty: {
          incident_id?: string | null;
          incident_key?: string | null;
          incident_status: string;
          urgency?: string | null;
          service_id?: string | null;
          service_summary?: string | null;
          escalation_policy_id?: string | null;
          escalation_policy_summary?: string | null;
          html_url?: string | null;
          last_status_change_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            responder_phase: string;
            urgency_phase: string;
            last_transition_at?: string | null;
          };
        };
        opsgenie: {
          alert_id?: string | null;
          alias?: string | null;
          alert_status: string;
          priority?: string | null;
          owner?: string | null;
          acknowledged?: boolean | null;
          seen?: boolean | null;
          tiny_id?: string | null;
          teams: string[];
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            acknowledgment_phase: string;
            ownership_phase: string;
            visibility_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidentio: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          mode?: string | null;
          visibility?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        firehydrant: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          priority?: string | null;
          team?: string | null;
          runbook?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            priority_phase: string;
            last_transition_at?: string | null;
          };
        };
        rootly: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity_id?: string | null;
          private?: boolean | null;
          slug?: string | null;
          url?: string | null;
          acknowledged_at?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            acknowledgment_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        blameless: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          commander?: string | null;
          visibility?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            command_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        xmatters: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assignee?: string | null;
          response_plan?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            response_plan_phase: string;
            last_transition_at?: string | null;
          };
        };
        servicenow: {
          incident_number?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assigned_to?: string | null;
          assignment_group?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            priority_phase: string;
            group_phase: string;
            last_transition_at?: string | null;
          };
        };
        squadcast: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          escalation_policy?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        bigpanda: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          team?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        grafana_oncall: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          escalation_chain?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        splunk_oncall: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          routing_key?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            routing_phase: string;
            last_transition_at?: string | null;
          };
        };
        jira_service_management: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assignee?: string | null;
          service_project?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            priority_phase: string;
            project_phase: string;
            last_transition_at?: string | null;
          };
        };
        pagertree: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          urgency?: string | null;
          assignee?: string | null;
          team?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            urgency_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        alertops: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          owner?: string | null;
          service?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            service_phase: string;
            last_transition_at?: string | null;
          };
        };
        signl4: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          team?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        ilert: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        betterstack: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        onpage: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        allquiet: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        moogsoft: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        spikesh: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        dutycalls: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidenthub: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        resolver: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        openduty: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        cabot: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        haloitsm: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidentmanagerio: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        oneuptime: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        squzy: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        crisescontrol: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        freshservice: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        freshdesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        happyfox: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zendesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zohodesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        helpscout: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        kayako: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        intercom: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        front: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        servicedeskplus: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        sysaid: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        bmchelix: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        solarwindsservicedesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        topdesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        invgateservicedesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        opsramp: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zenduty: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          service?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            service_phase: string;
            last_transition_at?: string | null;
          };
        };
      };
    };
  }[];
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
  audit_events: {
    event_id: string;
    timestamp: string;
    actor: string;
    kind: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    source: string;
  }[];
};

export type GuardedLiveStatus = {
  generated_at: string;
  candidacy_status: string;
  blockers: string[];
  active_alerts: OperatorAlertEntry[];
  alert_history: OperatorAlertEntry[];
  incident_events: {
    event_id: string;
    alert_id: string;
    timestamp: string;
    kind: string;
    severity: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    symbol?: string | null;
    symbols: string[];
    timeframe?: string | null;
    primary_focus?: OperatorAlertPrimaryFocus | null;
    source: string;
    paging_policy_id: string;
    paging_provider?: string | null;
    delivery_targets: string[];
    escalation_targets: string[];
    delivery_state: string;
    acknowledgment_state: string;
    acknowledged_at?: string | null;
    acknowledged_by?: string | null;
    acknowledgment_reason?: string | null;
    escalation_level: number;
    escalation_state: string;
    last_escalated_at?: string | null;
    last_escalated_by?: string | null;
    escalation_reason?: string | null;
    next_escalation_at?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    provider_workflow_reference?: string | null;
    external_status: string;
    external_last_synced_at?: string | null;
    paging_status: string;
    provider_workflow_state: string;
    provider_workflow_action?: string | null;
    provider_workflow_last_attempted_at?: string | null;
    remediation: {
      state: string;
      kind?: string | null;
      owner?: string | null;
      summary?: string | null;
      detail?: string | null;
      runbook?: string | null;
      requested_at?: string | null;
      requested_by?: string | null;
      last_attempted_at?: string | null;
      provider?: string | null;
      reference?: string | null;
      provider_payload: Record<string, unknown>;
      provider_payload_updated_at?: string | null;
      provider_recovery: {
        lifecycle_state: string;
        provider?: string | null;
        job_id?: string | null;
        reference?: string | null;
        workflow_reference?: string | null;
        summary?: string | null;
        detail?: string | null;
        channels: string[];
        symbols: string[];
        timeframe?: string | null;
        updated_at?: string | null;
        verification: {
          state: string;
          checked_at?: string | null;
          summary?: string | null;
          issues: string[];
        };
        telemetry: {
          source: string;
          state: string;
          progress_percent?: number | null;
          attempt_count: number;
          current_step?: string | null;
          last_message?: string | null;
          last_error?: string | null;
          external_run_id?: string | null;
          job_url?: string | null;
          started_at?: string | null;
          finished_at?: string | null;
          updated_at?: string | null;
        };
        status_machine: {
          state: string;
          workflow_state: string;
          workflow_action?: string | null;
          job_state: string;
          sync_state: string;
          last_event_kind?: string | null;
          last_event_at?: string | null;
          last_detail?: string | null;
          attempt_number: number;
        };
        provider_schema_kind?: string | null;
        pagerduty: {
          incident_id?: string | null;
          incident_key?: string | null;
          incident_status: string;
          urgency?: string | null;
          service_id?: string | null;
          service_summary?: string | null;
          escalation_policy_id?: string | null;
          escalation_policy_summary?: string | null;
          html_url?: string | null;
          last_status_change_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            responder_phase: string;
            urgency_phase: string;
            last_transition_at?: string | null;
          };
        };
        opsgenie: {
          alert_id?: string | null;
          alias?: string | null;
          alert_status: string;
          priority?: string | null;
          owner?: string | null;
          acknowledged?: boolean | null;
          seen?: boolean | null;
          tiny_id?: string | null;
          teams: string[];
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            acknowledgment_phase: string;
            ownership_phase: string;
            visibility_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidentio: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          mode?: string | null;
          visibility?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        firehydrant: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          priority?: string | null;
          team?: string | null;
          runbook?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            priority_phase: string;
            last_transition_at?: string | null;
          };
        };
        rootly: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity_id?: string | null;
          private?: boolean | null;
          slug?: string | null;
          url?: string | null;
          acknowledged_at?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            acknowledgment_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        blameless: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          commander?: string | null;
          visibility?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            command_phase: string;
            visibility_phase: string;
            severity_phase: string;
            last_transition_at?: string | null;
          };
        };
        xmatters: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assignee?: string | null;
          response_plan?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            response_plan_phase: string;
            last_transition_at?: string | null;
          };
        };
        servicenow: {
          incident_number?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assigned_to?: string | null;
          assignment_group?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            priority_phase: string;
            group_phase: string;
            last_transition_at?: string | null;
          };
        };
        squadcast: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          escalation_policy?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        bigpanda: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          team?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        grafana_oncall: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          escalation_chain?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        splunk_oncall: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          routing_key?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            routing_phase: string;
            last_transition_at?: string | null;
          };
        };
        jira_service_management: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          assignee?: string | null;
          service_project?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            assignment_phase: string;
            priority_phase: string;
            project_phase: string;
            last_transition_at?: string | null;
          };
        };
        pagertree: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          urgency?: string | null;
          assignee?: string | null;
          team?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            urgency_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        alertops: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          priority?: string | null;
          owner?: string | null;
          service?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            service_phase: string;
            last_transition_at?: string | null;
          };
        };
        signl4: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          team?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            team_phase: string;
            last_transition_at?: string | null;
          };
        };
        ilert: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        betterstack: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        onpage: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        allquiet: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        moogsoft: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        spikesh: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        dutycalls: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidenthub: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        resolver: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        openduty: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        cabot: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        haloitsm: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        incidentmanagerio: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        oneuptime: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        squzy: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        crisescontrol: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        freshservice: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        freshdesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        happyfox: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zendesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zohodesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        helpscout: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        kayako: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        intercom: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        front: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        servicedeskplus: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        sysaid: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        bmchelix: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        solarwindsservicedesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        topdesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        invgateservicedesk: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        opsramp: {
          alert_id?: string | null;
          external_reference?: string | null;
          alert_status: string;
          priority?: string | null;
          escalation_policy?: string | null;
          assignee?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            alert_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            priority_phase: string;
            escalation_phase: string;
            last_transition_at?: string | null;
          };
        };
        zenduty: {
          incident_id?: string | null;
          external_reference?: string | null;
          incident_status: string;
          severity?: string | null;
          assignee?: string | null;
          service?: string | null;
          url?: string | null;
          updated_at?: string | null;
          phase_graph: {
            incident_phase: string;
            workflow_phase: string;
            ownership_phase: string;
            severity_phase: string;
            service_phase: string;
            last_transition_at?: string | null;
          };
        };
      };
    };
  }[];
  delivery_history: {
    delivery_id: string;
    incident_event_id: string;
    alert_id: string;
    incident_kind: string;
    target: string;
    status: string;
    attempted_at: string;
    detail: string;
    attempt_number: number;
    next_retry_at?: string | null;
    phase: string;
    provider_action?: string | null;
    external_provider?: string | null;
    external_reference?: string | null;
    source: string;
  }[];
  kill_switch: {
    state: string;
    reason: string;
    updated_at: string;
    updated_by: string;
    activation_count: number;
    last_engaged_at?: string | null;
    last_released_at?: string | null;
  };
  reconciliation: {
    state: string;
    checked_at?: string | null;
    checked_by?: string | null;
    scope: string;
    summary: string;
    findings: {
      kind: string;
      severity: string;
      summary: string;
      detail: string;
    }[];
    internal_snapshot?: {
      captured_at: string;
      running_run_ids: string[];
      exposures: {
        run_id: string;
        mode: string;
        instrument_id: string;
        quantity: number;
      }[];
      open_order_count: number;
    } | null;
    venue_snapshot?: {
      provider: string;
      venue: string;
      verification_state: string;
      captured_at?: string | null;
      balances: {
        asset: string;
        total: number;
        free?: number | null;
        used?: number | null;
      }[];
      open_orders: {
        order_id: string;
        symbol: string;
        side: string;
        amount: number;
        status: string;
        price?: number | null;
      }[];
      issues: string[];
    } | null;
  };
  recovery: {
    state: string;
    recovered_at?: string | null;
    recovered_by?: string | null;
    reason?: string | null;
    source_snapshot_at?: string | null;
    source_verification_state: string;
    summary: string;
    exposures: {
      instrument_id: string;
      symbol: string;
      asset: string;
      quantity: number;
    }[];
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    issues: string[];
  };
  ownership: {
    state: string;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    symbol?: string | null;
    claimed_at?: string | null;
    claimed_by?: string | null;
    last_heartbeat_at?: string | null;
    last_order_sync_at?: string | null;
    last_resumed_at?: string | null;
    last_reason?: string | null;
    last_released_at?: string | null;
  };
  order_book: {
    state: string;
    synced_at?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    symbol?: string | null;
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    issues: string[];
  };
  session_restore: {
    state: string;
    restored_at?: string | null;
    source: string;
    venue?: string | null;
    symbol?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    open_orders: {
      order_id: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      price?: number | null;
    }[];
    synced_orders: {
      order_id: string;
      venue: string;
      symbol: string;
      side: string;
      amount: number;
      status: string;
      submitted_at: string;
      updated_at?: string | null;
      requested_price?: number | null;
      average_fill_price?: number | null;
      fee_paid?: number | null;
      requested_amount?: number | null;
      filled_amount?: number | null;
      remaining_amount?: number | null;
      issues: string[];
    }[];
    issues: string[];
  };
  session_handoff: {
    state: string;
    handed_off_at?: string | null;
    released_at?: string | null;
    source: string;
    venue?: string | null;
    symbol?: string | null;
    owner_run_id?: string | null;
    owner_session_id?: string | null;
    venue_session_id?: string | null;
    transport: string;
    cursor?: string | null;
    last_event_at?: string | null;
    last_sync_at?: string | null;
    supervision_state: string;
    failover_count: number;
    last_failover_at?: string | null;
    coverage: string[];
    order_book_state: string;
    order_book_last_update_id?: number | null;
    order_book_gap_count: number;
    order_book_rebuild_count: number;
    order_book_last_rebuilt_at?: string | null;
    order_book_bid_level_count: number;
    order_book_ask_level_count: number;
    order_book_best_bid_price?: number | null;
    order_book_best_bid_quantity?: number | null;
    order_book_best_ask_price?: number | null;
    order_book_best_ask_quantity?: number | null;
    order_book_bids: {
      price: number;
      quantity: number;
    }[];
    order_book_asks: {
      price: number;
      quantity: number;
    }[];
    channel_restore_state: string;
    channel_restore_count: number;
    channel_last_restored_at?: string | null;
    channel_continuation_state: string;
    channel_continuation_count: number;
    channel_last_continued_at?: string | null;
    trade_snapshot?: {
      event_id?: string | null;
      price?: number | null;
      quantity?: number | null;
      event_at?: string | null;
    } | null;
    aggregate_trade_snapshot?: {
      event_id?: string | null;
      price?: number | null;
      quantity?: number | null;
      event_at?: string | null;
    } | null;
    book_ticker_snapshot?: {
      bid_price?: number | null;
      bid_quantity?: number | null;
      ask_price?: number | null;
      ask_quantity?: number | null;
      event_at?: string | null;
    } | null;
    mini_ticker_snapshot?: {
      open_price?: number | null;
      close_price?: number | null;
      high_price?: number | null;
      low_price?: number | null;
      base_volume?: number | null;
      quote_volume?: number | null;
      event_at?: string | null;
    } | null;
    kline_snapshot?: {
      timeframe?: string | null;
      open_at?: string | null;
      close_at?: string | null;
      open_price?: number | null;
      high_price?: number | null;
      low_price?: number | null;
      close_price?: number | null;
      volume?: number | null;
      closed: boolean;
      event_at?: string | null;
    } | null;
    last_market_event_at?: string | null;
    last_depth_event_at?: string | null;
    last_kline_event_at?: string | null;
    last_aggregate_trade_event_at?: string | null;
    last_mini_ticker_event_at?: string | null;
    last_account_event_at?: string | null;
    last_balance_event_at?: string | null;
    last_order_list_event_at?: string | null;
    last_trade_event_at?: string | null;
    last_book_ticker_event_at?: string | null;
    active_order_count: number;
    issues: string[];
  };
  audit_events: {
    event_id: string;
    timestamp: string;
    actor: string;
    kind: string;
    summary: string;
    detail: string;
    run_id?: string | null;
    session_id?: string | null;
    source: string;
  }[];
  active_runtime_alert_count: number;
  running_sandbox_count: number;
  running_paper_count: number;
  running_live_count: number;
};

export const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
export const MAX_VISIBLE_GAP_WINDOWS = 3;
export const TOUCH_GAP_WINDOW_SWEEP_HOLD_MS = 220;
export const TOUCH_GAP_WINDOW_SWEEP_MOVE_TOLERANCE_PX = 14;
export const DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE = "Akra Trader Control Room";
export const MAX_COMPARISON_HISTORY_PANEL_ENTRIES = 12;
export const MAX_COMPARISON_HISTORY_SYNC_AUDIT_ENTRIES = 8;
export const CONTROL_ROOM_UI_STATE_STORAGE_KEY = "akra-trader-control-room-ui-state";
export const CONTROL_ROOM_UI_STATE_VERSION = 4;
export const RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX = "akra-trader-run-history-saved-filters";
export const MARKET_DATA_PROVENANCE_EXPORT_STORAGE_KEY = "akra-trader-market-data-provenance-exports";
export const MARKET_DATA_PROVENANCE_EXPORT_STORAGE_VERSION = 1;
export const MAX_MARKET_DATA_PROVENANCE_EXPORT_HISTORY_ENTRIES = 12;
export const COMPARISON_HISTORY_BROWSER_STATE_KEY = "akraTraderComparisonHistory";
export const COMPARISON_HISTORY_BROWSER_STATE_VERSION = 1;
export const COMPARISON_HISTORY_TAB_ID_SESSION_KEY = "akra-trader-comparison-history-tab-id";
export const COMPARISON_HISTORY_SYNC_AUDIT_SESSION_KEY = "akra-trader-comparison-history-sync-audit";
export const COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION = 1;
export const COMPARISON_TOOLTIP_TUNING_STORAGE_KEY = "akra-trader-comparison-tooltip-tuning";
export const COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION = 1;
export const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY = "akra-trader-comparison-tooltip-conflict-ui";
export const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION = 1;
export const COMPARISON_TOOLTIP_TUNING_SHARE_PARAM = "comparisonTooltipTuning";
export const LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY = "akra-trader-gap-window-expansion";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY = "akra-trader-run-surface-replay-history";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY = "akra-trader-run-surface-replay-intent";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION = 2;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY = "akra-trader-run-surface-replay-intent";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY = "akra-trader-run-surface-replay-link-aliases";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY = "akra-trader-run-surface-replay-link-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY = "akra-trader-run-surface-replay-link-signing-secret";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY = "akra-trader-run-surface-replay-link-governance-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY = "akra-trader-run-surface-replay-link-governance";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY = "akra-trader-run-surface-replay-link-governance-sync";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES = 12;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES = 24;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES = 8;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS = 24;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY = "akra-trader-run-surface-replay-history-tab-id";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY = "akra-trader-run-surface-replay-history-sync-audit";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES = 8;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY = "akra-trader-run-surface-replay-history-governance";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION = 1;
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY = "akra-trader-run-surface-replay-history-conflicts";
export const RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION = 1;
export const MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES = 8;
export const COMPARISON_RUN_ID_SEARCH_PARAM = "compare_run_id";
export const COMPARISON_INTENT_SEARCH_PARAM = "compare_intent";
export const COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM = "compare_focus_run_id";
export const COMPARISON_FOCUS_SECTION_SEARCH_PARAM = "compare_focus_section";
export const COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM = "compare_focus_component";
export const COMPARISON_FOCUS_SOURCE_SEARCH_PARAM = "compare_focus_source";
export const COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM = "compare_focus_origin_run_id";
export const COMPARISON_FOCUS_DETAIL_SEARCH_PARAM = "compare_focus_detail";
export const COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM = "compare_focus_expanded";
export const COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM = "compare_focus_artifact_expanded";
export const COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM = "compare_focus_artifact_line_expanded";
export const COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM = "compare_focus_artifact_line_view";
export const COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM = "compare_focus_artifact_line_micro_view";
export const COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM = "compare_focus_artifact_line_note_page";
export const COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM = "compare_focus_artifact_line_hover";
export const COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM = "compare_focus_artifact_line_scrub";
export const COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM = "compare_focus_tooltip";
export const COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM = "compare_focus_artifact_hover";
export const REPLAY_INTENT_TEMPLATE_SEARCH_PARAM = "replay_template";
export const REPLAY_INTENT_SEARCH_PARAM = "replay_intent";
export const REPLAY_INTENT_ALIAS_SEARCH_PARAM = "replay_link";
export const REPLAY_INTENT_SCOPE_SEARCH_PARAM = "replay_scope";
export const REPLAY_INTENT_STEP_SEARCH_PARAM = "replay_step";
export const REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM = "replay_group";
export const REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM = "replay_action";
export const REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM = "replay_edge";
export const REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM = "replay_preview_group";
export const REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM = "replay_preview_trace";
export const REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM = "replay_preview_diff";
export const ALL_FILTER_VALUE = "__all__";
export const MAX_COMPARISON_RUNS = 4;
export const MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES = 5;
export type ExpandedGapWindowSelections = Record<string, string[]>;
export type GapWindowDragSelectionState = {
  anchorGapWindowKey: string;
  baselineSelectedGapWindowKeys: string[];
  latestGapWindowKey: string;
  pointerId: number;
  targetSelected: boolean;
};
export type PendingTouchGapWindowSweepState = {
  anchorGapWindowKey: string;
  baselineSelectedGapWindowKeys: string[];
  latestGapWindowKey: string;
  pointerId: number;
  startClientX: number;
  startClientY: number;
  targetSelected: boolean;
};
export type TouchGapWindowHoldProgressState = {
  anchorGapWindowKey: string;
  targetSelected: boolean;
};
export type TouchGapWindowActivationFeedbackState = {
  activationId: number;
  anchorGapWindowKey: string;
};

export type ControlRoomUiStateV1 = {
  version: 1;
  expandedGapRows: Record<string, boolean>;
};

export type ControlRoomComparisonSelectionState = {
  selectedRunIds: string[];
  intent: ComparisonIntent;
  scoreLink: ComparisonScoreLinkTarget | null;
};

export type ComparisonHistoryStepDescriptor = {
  label: string;
  summary: string;
  title: string;
};

export type ComparisonHistoryBrowserState = {
  version: typeof COMPARISON_HISTORY_BROWSER_STATE_VERSION;
  entryId: string;
  stepIndex: number;
  label: string;
  summary: string;
  title: string;
  selection: ControlRoomComparisonSelectionState;
};

export type ComparisonHistoryPanelEntry = {
  entryId: string;
  stepIndex: number;
  label: string;
  summary: string;
  title: string;
  url: string;
  hidden: boolean;
  pinned: boolean;
  recordedAt: string;
  selection: ControlRoomComparisonSelectionState;
};

export type ComparisonHistoryTabIdentity = {
  tabId: string;
  label: string;
};

export type ComparisonHistoryPanelSyncState = {
  tabId: string;
  tabLabel: string;
  updatedAt: string;
};

export type ComparisonHistorySyncAuditKind = "merge" | "conflict" | "preferences" | "workspace";
export type ComparisonHistorySyncConflictFieldSource = "local" | "remote";
export type ComparisonHistorySyncConflictFieldKey =
  | "stepIndex"
  | "label"
  | "summary"
  | "title"
  | "url"
  | "hidden"
  | "pinned"
  | "selection.intent"
  | "selection.selectedRunIds"
  | "selection.scoreLink";
export type ComparisonHistorySyncWorkspaceFieldKey =
  | "comparisonSelection.intent"
  | "comparisonSelection.selectedRunIds"
  | "comparisonSelection.scoreLink"
  | "expandedGapRows";
export type ComparisonHistorySyncWorkspaceReviewSelectionKey =
  | ComparisonHistorySyncWorkspaceFieldKey
  | `expandedGapRows:${string}`
  | `expandedGapWindows|${string}|${string}`;
export type ComparisonHistorySyncWorkspaceSignalDetailSubviewKey =
  | "interpretation"
  | "lanePosition"
  | "recommendationContext";
export type ComparisonHistorySyncWorkspaceSignalDetailNestedKey =
  | "laneSemantics"
  | "recommendationEffect"
  | "rankContext"
  | "weightShare"
  | "selectionAlignment"
  | "resolutionBasis";
export type ComparisonHistorySyncWorkspaceSignalMicroViewKey =
  | "summary"
  | "trace"
  | "recommendation"
  | "alternative"
  | "position"
  | "score"
  | "share"
  | "impact"
  | "selection"
  | "lane"
  | "gap"
  | "reason";
export type ComparisonHistorySyncWorkspaceSignalMicroInteractionKey =
  | "lane"
  | "polarity"
  | "signal"
  | "source"
  | "support"
  | "tradeoff"
  | "rank"
  | "score"
  | "share"
  | "impact"
  | "selected"
  | "focusedLane"
  | "gap"
  | "reason";
export type ComparisonHistorySyncAuditFilter =
  | "all"
  | "conflicts"
  | "preferences"
  | "workspace"
  | "merges";
export type ComparisonHistorySyncPreferenceFieldKey =
  | "open"
  | "searchQuery"
  | "showPinnedOnly"
  | "auditFilter"
  | "showResolvedAuditEntries";

export type ComparisonHistorySyncConflictReview = {
  entryId: string;
  entryLabel: string;
  localEntry: ComparisonHistoryPanelEntry;
  remoteEntry: ComparisonHistoryPanelEntry;
  selectedSources: Partial<
    Record<ComparisonHistorySyncConflictFieldKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncPreferenceState = {
  open: boolean;
  searchQuery: string;
  showPinnedOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
};

export type ComparisonHistorySyncPreferenceReview = {
  localState: ComparisonHistorySyncPreferenceState;
  remoteState: ComparisonHistorySyncPreferenceState;
  selectedSources: Partial<
    Record<ComparisonHistorySyncPreferenceFieldKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncWorkspaceState = {
  comparisonSelection: ControlRoomComparisonSelectionState;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
};

export type ComparisonHistorySyncWorkspaceReview = {
  localState: ComparisonHistorySyncWorkspaceState;
  remoteState: ComparisonHistorySyncWorkspaceState;
  selectedSources: Partial<
    Record<ComparisonHistorySyncWorkspaceReviewSelectionKey, ComparisonHistorySyncConflictFieldSource>
  >;
  resolvedAt?: string | null;
  resolutionSummary?: string | null;
};

export type ComparisonHistorySyncAuditEntry = {
  auditId: string;
  kind: ComparisonHistorySyncAuditKind;
  summary: string;
  detail: string;
  recordedAt: string;
  sourceTabId: string;
  sourceTabLabel: string;
  conflictReview?: ComparisonHistorySyncConflictReview | null;
  preferenceReview?: ComparisonHistorySyncPreferenceReview | null;
  workspaceReview?: ComparisonHistorySyncWorkspaceReview | null;
};

export type ComparisonHistorySyncAuditTrailState = {
  version: typeof COMPARISON_HISTORY_SYNC_AUDIT_SESSION_VERSION;
  tabId: string;
  entries: ComparisonHistorySyncAuditEntry[];
};

export type ComparisonHistoryPanelState = {
  entries: ComparisonHistoryPanelEntry[];
  activeEntryId: string | null;
};

export type ControlRoomComparisonHistoryPanelUiState = {
  panel: ComparisonHistoryPanelState;
  open: boolean;
  searchQuery: string;
  showPinnedOnly: boolean;
  auditFilter: ComparisonHistorySyncAuditFilter;
  showResolvedAuditEntries: boolean;
  expandedConflictReviewIds: Record<string, boolean>;
  expandedWorkspaceScoreDetailIds: Record<string, boolean>;
  focusedWorkspaceScoreDetailSources: Record<string, ComparisonHistorySyncConflictFieldSource>;
  focusedWorkspaceScoreDetailSignalKeys: Record<string, string>;
  expandedWorkspaceScoreSignalDetailIds: Record<string, boolean>;
  collapsedWorkspaceScoreSignalSubviewIds: Record<string, boolean>;
  collapsedWorkspaceScoreSignalNestedSubviewIds: Record<string, boolean>;
  focusedWorkspaceScoreSignalMicroViews: Record<string, ComparisonHistorySyncWorkspaceSignalMicroViewKey>;
  focusedWorkspaceScoreSignalMicroInteractions: Record<string, ComparisonHistorySyncWorkspaceSignalMicroInteractionKey>;
  hoveredWorkspaceScoreSignalMicroTargets: Record<string, string>;
  scrubbedWorkspaceScoreSignalMicroSteps: Record<string, number>;
  selectedWorkspaceScoreSignalMicroNotePages: Record<string, number>;
  activeWorkspaceOverviewRowId: string | null;
  sync: ComparisonHistoryPanelSyncState | null;
};

export type ComparisonHistorySyncConflictReviewRow = {
  fieldKey: ComparisonHistorySyncConflictFieldKey;
  groupKey: string;
  groupLabel: string;
  label: string;
  localValue: string;
  remoteValue: string;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncConflictReviewGroup = {
  key: string;
  label: string;
  rows: ComparisonHistorySyncConflictReviewRow[];
  summaryLabel: string;
};

export type ComparisonHistorySyncPreferenceReviewRow = {
  fieldKey: ComparisonHistorySyncPreferenceFieldKey;
  label: string;
  localValue: string;
  remoteValue: string;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncWorkspaceReviewRow = {
  fieldKey: ComparisonHistorySyncWorkspaceReviewSelectionKey;
  hasLatestLocalDrift: boolean;
  label: string;
  localHint?: string | null;
  localScore: number;
  localSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  localValue: string;
  remoteScore: number;
  remoteSignals: ComparisonHistorySyncWorkspaceSemanticSignal[];
  remoteValue: string;
  recommendedSource: ComparisonHistorySyncConflictFieldSource;
  recommendationReason: string;
  recommendationStrength: number;
  semanticRank: number;
  selectedSource: ComparisonHistorySyncConflictFieldSource;
};

export type ComparisonHistorySyncWorkspaceRecommendationOverview = {
  totalFieldCount: number;
  localCount: number;
  remoteCount: number;
  latestLocalDriftCount: number;
  rankedDiffCount: number;
  strongest: ComparisonHistorySyncWorkspaceReviewRow | null;
  topLocal: ComparisonHistorySyncWorkspaceReviewRow[];
  topRemote: ComparisonHistorySyncWorkspaceReviewRow[];
};

export type ControlRoomUiStateV2 = {
  version: 2;
  expandedGapRows: Record<string, boolean>;
  comparisonSelection: ControlRoomComparisonSelectionState;
};

export type ControlRoomUiStateV3 = {
  version: 3;
  expandedGapRows: Record<string, boolean>;
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ControlRoomComparisonHistoryPanelUiState;
};

export type ControlRoomUiStateV4 = {
  version: typeof CONTROL_ROOM_UI_STATE_VERSION;
  expandedGapRows: Record<string, boolean>;
  expandedGapWindowSelections: ExpandedGapWindowSelections;
  comparisonSelection: ControlRoomComparisonSelectionState;
  comparisonHistoryPanel: ControlRoomComparisonHistoryPanelUiState;
};

export const COMPARISON_HISTORY_SYNC_CONFLICT_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncConflictFieldKey;
  groupKey: string;
  groupLabel: string;
  label: string;
}> = [
  { fieldKey: "stepIndex", groupKey: "timeline", groupLabel: "Timeline", label: "Step order" },
  { fieldKey: "url", groupKey: "timeline", groupLabel: "Timeline", label: "Deep link" },
  { fieldKey: "label", groupKey: "copy", groupLabel: "Copy", label: "Step label" },
  { fieldKey: "summary", groupKey: "copy", groupLabel: "Copy", label: "Step summary" },
  { fieldKey: "title", groupKey: "copy", groupLabel: "Copy", label: "Document title" },
  { fieldKey: "hidden", groupKey: "flags", groupLabel: "Flags", label: "Visibility" },
  { fieldKey: "pinned", groupKey: "flags", groupLabel: "Flags", label: "Pinned state" },
  { fieldKey: "selection.intent", groupKey: "selection", groupLabel: "Selection", label: "Intent" },
  {
    fieldKey: "selection.selectedRunIds",
    groupKey: "selection",
    groupLabel: "Selection",
    label: "Selected runs",
  },
  {
    fieldKey: "selection.scoreLink",
    groupKey: "selection",
    groupLabel: "Selection",
    label: "Focused score component",
  },
];

export const COMPARISON_HISTORY_SYNC_PREFERENCE_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncPreferenceFieldKey;
  label: string;
}> = [
  { fieldKey: "open", label: "Browser visibility" },
  { fieldKey: "searchQuery", label: "Search filter" },
  { fieldKey: "showPinnedOnly", label: "Pinned-only mode" },
  { fieldKey: "auditFilter", label: "Audit list filter" },
  { fieldKey: "showResolvedAuditEntries", label: "Resolved audit visibility" },
];

export const COMPARISON_HISTORY_SYNC_WORKSPACE_FIELD_DEFINITIONS: Array<{
  fieldKey: ComparisonHistorySyncWorkspaceFieldKey;
  label: string;
}> = [
  { fieldKey: "comparisonSelection.intent", label: "Comparison intent" },
  { fieldKey: "comparisonSelection.selectedRunIds", label: "Selected runs" },
  { fieldKey: "comparisonSelection.scoreLink", label: "Focused score component" },
  { fieldKey: "expandedGapRows", label: "Expanded gap windows" },
];

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

export type ComparisonIntent = "benchmark_validation" | "execution_regression" | "strategy_tuning";
export type ComparisonCueKind = "mode" | "baseline" | "best" | "insight";
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
