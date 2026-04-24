import type { ComparisonIntent } from "./comparisonCore";
import type { ParameterSchema, ReferenceSource } from "./strategyCatalog";

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
