import {
  CSSProperties,
  FormEvent,
  KeyboardEvent,
  MouseEvent,
  forwardRef,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type ParameterSchema = Record<
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

type Strategy = {
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

type ReferenceSource = {
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

type ExperimentPresetRevision = {
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

type ExperimentPreset = {
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

type PresetRevisionFilterState = {
  action: string;
  query: string;
};

type PresetStructuredDiffRow = {
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

type PresetStructuredDiffGroup = {
  changed_count: number;
  higher_count: number;
  key: string;
  label: string;
  lower_count: number;
  rows: PresetStructuredDiffRow[];
  same_count: number;
  summary_label: string;
};

type PresetStructuredDiffDeltaValue = {
  direction: "higher" | "lower" | "same";
  label: string;
};

type PresetRevisionDiff = {
  basisLabel: string;
  changeCount: number;
  changedGroups: PresetStructuredDiffGroup[];
  unchangedGroups: PresetStructuredDiffGroup[];
  searchTexts: string[];
  summary: string;
};

type PresetDraftConflict = {
  changeCount: number;
  groups: PresetStructuredDiffGroup[];
  hasInvalidParameters: boolean;
  summary: string;
};

type BenchmarkArtifact = {
  kind: string;
  label: string;
  path: string;
  format?: string | null;
  exists: boolean;
  is_directory: boolean;
  summary: Record<string, unknown>;
  sections?: Record<string, Record<string, unknown>>;
  summary_source_path?: string | null;
};

type Run = {
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
  }[];
  notes: string[];
};

type RunComparison = {
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

type ComparisonScoreSection = "metrics" | "semantics" | "context";

type ComparisonScoreLinkTarget = {
  narrativeRunId: string;
  section: ComparisonScoreSection;
  componentKey: string;
};

type ComparisonScoreLinkedRunRole = "baseline" | "target";

type ComparisonScoreLinkSource = "metric" | "narrative" | "provenance";

type ComparisonHistoryWriteMode = "push" | "replace" | "skip";

type MarketDataStatus = {
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
      start_at: string;
      end_at: string;
      missing_candles: number;
    }[];
    issues: string[];
  }[];
};

type OperatorVisibility = {
  generated_at: string;
  alerts: {
    alert_id: string;
    severity: string;
    category: string;
    summary: string;
    detail: string;
    detected_at: string;
    run_id?: string | null;
    session_id?: string | null;
    status: string;
    resolved_at?: string | null;
    source: string;
    delivery_targets: string[];
  }[];
  alert_history: {
    alert_id: string;
    severity: string;
    category: string;
    summary: string;
    detail: string;
    detected_at: string;
    run_id?: string | null;
    session_id?: string | null;
    status: string;
    resolved_at?: string | null;
    source: string;
    delivery_targets: string[];
  }[];
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

type GuardedLiveStatus = {
  generated_at: string;
  candidacy_status: string;
  blockers: string[];
  active_alerts: {
    alert_id: string;
    severity: string;
    category: string;
    summary: string;
    detail: string;
    detected_at: string;
    run_id?: string | null;
    session_id?: string | null;
    status: string;
    resolved_at?: string | null;
    source: string;
    delivery_targets: string[];
  }[];
  alert_history: {
    alert_id: string;
    severity: string;
    category: string;
    summary: string;
    detail: string;
    detected_at: string;
    run_id?: string | null;
    session_id?: string | null;
    status: string;
    resolved_at?: string | null;
    source: string;
    delivery_targets: string[];
  }[];
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

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const MAX_VISIBLE_GAP_WINDOWS = 3;
const DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE = "Akra Trader Control Room";
const MAX_COMPARISON_HISTORY_PANEL_ENTRIES = 12;
const CONTROL_ROOM_UI_STATE_STORAGE_KEY = "akra-trader-control-room-ui-state";
const CONTROL_ROOM_UI_STATE_VERSION = 2;
const COMPARISON_HISTORY_BROWSER_STATE_KEY = "akraTraderComparisonHistory";
const COMPARISON_HISTORY_BROWSER_STATE_VERSION = 1;
const COMPARISON_TOOLTIP_TUNING_STORAGE_KEY = "akra-trader-comparison-tooltip-tuning";
const COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION = 1;
const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY = "akra-trader-comparison-tooltip-conflict-ui";
const COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION = 1;
const COMPARISON_TOOLTIP_TUNING_SHARE_PARAM = "comparisonTooltipTuning";
const LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY = "akra-trader-gap-window-expansion";
const COMPARISON_RUN_ID_SEARCH_PARAM = "compare_run_id";
const COMPARISON_INTENT_SEARCH_PARAM = "compare_intent";
const COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM = "compare_focus_run_id";
const COMPARISON_FOCUS_SECTION_SEARCH_PARAM = "compare_focus_section";
const COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM = "compare_focus_component";
const ALL_FILTER_VALUE = "__all__";
const MAX_COMPARISON_RUNS = 4;
const MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES = 5;

type ControlRoomUiStateV1 = {
  version: 1;
  expandedGapRows: Record<string, boolean>;
};

type ControlRoomComparisonSelectionState = {
  selectedRunIds: string[];
  intent: ComparisonIntent;
  scoreLink: ComparisonScoreLinkTarget | null;
};

type ComparisonHistoryStepDescriptor = {
  label: string;
  summary: string;
  title: string;
};

type ComparisonHistoryBrowserState = {
  version: typeof COMPARISON_HISTORY_BROWSER_STATE_VERSION;
  entryId: string;
  label: string;
  summary: string;
  title: string;
  selection: ControlRoomComparisonSelectionState;
};

type ComparisonHistoryPanelEntry = {
  entryId: string;
  label: string;
  summary: string;
  title: string;
  url: string;
  selection: ControlRoomComparisonSelectionState;
};

type ComparisonHistoryPanelState = {
  entries: ComparisonHistoryPanelEntry[];
  activeEntryId: string | null;
};

type ControlRoomUiStateV2 = {
  version: typeof CONTROL_ROOM_UI_STATE_VERSION;
  expandedGapRows: Record<string, boolean>;
  comparisonSelection: ControlRoomComparisonSelectionState;
};

type RunHistoryFilter = {
  strategy_id: string;
  strategy_version: string;
  preset_id: string;
  benchmark_family: string;
  tag: string;
  dataset_identity: string;
};

type ComparisonIntent = "benchmark_validation" | "execution_regression" | "strategy_tuning";
type ComparisonCueKind = "mode" | "baseline" | "best" | "insight";
type ComparisonTooltipTargetProps = {
  "aria-describedby"?: string;
  "data-tooltip-visible": "true" | "false";
  onBlur: () => void;
  onFocus: () => void;
  onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  onMouseEnter: (event: MouseEvent<HTMLElement>) => void;
  onMouseLeave: (event: MouseEvent<HTMLElement>) => void;
  onMouseMove?: (event: MouseEvent<HTMLElement>) => void;
};
type ComparisonTooltipInteractionOptions = {
  hoverCloseDelayMs?: number;
  hoverOpenDelayMs?: number;
};
type ComparisonTooltipTuning = {
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
type ComparisonTooltipTuningPresetStateV1 = {
  current_tuning: ComparisonTooltipTuning;
  presets: Record<string, ComparisonTooltipTuning>;
  selected_preset_name?: string | null;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
type ComparisonTooltipTuningSinglePresetShareV1 = {
  preset_name: string;
  tuning: ComparisonTooltipTuning;
  version: typeof COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION;
};
type ComparisonTooltipPresetImportConflictPolicy = "overwrite" | "rename";
type ComparisonTooltipPresetImportResolution = {
  conflicted: boolean;
  final_preset_name: string;
  imported_preset_name: string;
  policy: ComparisonTooltipPresetImportConflictPolicy;
  renamed: boolean;
  overwritten: boolean;
};
type ComparisonTooltipPendingPresetImportConflict = {
  imported_preset_name: string;
  proposed_preset_name: string;
  raw: string;
  tuning: ComparisonTooltipTuning;
};
type ComparisonTooltipPresetConflictPreviewRow = {
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
type ComparisonTooltipPresetConflictPreviewGroup = {
  changed_count: number;
  higher_count: number;
  key: string;
  label: string;
  lower_count: number;
  rows: ComparisonTooltipPresetConflictPreviewRow[];
  same_count: number;
  summary_label: string;
};
type ComparisonTooltipConflictSessionUiState = {
  collapsed_unchanged_groups: Record<string, boolean>;
  show_unchanged_conflict_rows: boolean;
  updated_at: string | null;
};
type ComparisonTooltipConflictUiStateV1 = {
  sessions: Record<string, ComparisonTooltipConflictSessionUiState>;
  version: typeof COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION;
};
type ComparisonTooltipConflictSessionSummary = {
  group_key: string;
  includes_current: boolean;
  label: string;
  preset_name: string;
  session_count: number;
  sessions: ComparisonTooltipConflictSessionSummarySession[];
};
type ComparisonTooltipConflictSessionSummarySession = {
  hash: string | null;
  includes_current: boolean;
  label: string;
  metadata: string[];
  session_key: string;
  updated_at: string | null;
};
type ComparisonTooltipTuningShareImport =
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
type ComparisonTooltipLayout = {
  tooltipId: string;
  left: number;
  top: number;
  maxWidth: number;
  arrowLeft: number;
  side: "top" | "bottom";
};

const DEFAULT_COMPARISON_TOOLTIP_TUNING: ComparisonTooltipTuning = {
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
const SHOW_COMPARISON_TOOLTIP_TUNING_PANEL = import.meta.env.DEV;
const DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY: ComparisonTooltipPresetImportConflictPolicy =
  "rename";
const COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD = 3;
const PRESET_TIMEFRAME_UNIT_TO_MINUTES: Record<string, number> = {
  d: 1440,
  h: 60,
  m: 1,
  w: 10080,
};
const PRESET_PROFILE_AGGRESSIVENESS_RANKS: Record<string, number> = {
  aggressive: 4,
  assertive: 3,
  balanced: 2,
  cautious: 1,
  conservative: 1,
  normal: 2,
  safe: 0,
  standard: 2,
};
const PRESET_PROFILE_SPEED_RANKS: Record<string, number> = {
  balanced: 1,
  fast: 2,
  medium: 1,
  normal: 1,
  slow: 0,
  steady: 0,
  turbo: 3,
};
const PRESET_PROFILE_CONFIDENCE_RANKS: Record<string, number> = {
  balanced: 1,
  high: 2,
  low: 0,
  medium: 1,
};
const COMPARISON_TOOLTIP_TUNING_LABELS: Record<keyof ComparisonTooltipTuning, string> = {
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
const COMPARISON_TOOLTIP_TUNING_GROUPS: Record<
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

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

const defaultRunForm = {
  strategy_id: "ma_cross_v1",
  symbol: "BTC/USDT",
  timeframe: "5m",
  initial_cash: 10000,
  fee_rate: 0.001,
  slippage_bps: 3,
  tags_text: "",
  preset_id: "",
  benchmark_family: "",
};

const defaultPresetForm = {
  name: "",
  preset_id: "",
  description: "",
  strategy_id: "",
  timeframe: "5m",
  benchmark_family: "",
  tags_text: "",
  parameters_text: "",
};

const defaultPresetRevisionFilter: PresetRevisionFilterState = {
  action: "all",
  query: "",
};

function buildPresetFormFromPreset(preset: ExperimentPreset) {
  return {
    name: preset.name,
    preset_id: preset.preset_id,
    description: preset.description,
    strategy_id: preset.strategy_id ?? "",
    timeframe: preset.timeframe ?? "",
    benchmark_family: preset.benchmark_family ?? "",
    tags_text: preset.tags.join(", "),
    parameters_text: Object.keys(preset.parameters).length
      ? JSON.stringify(preset.parameters, null, 2)
      : "",
  };
}

function buildCurrentPresetRevisionSnapshot(preset: ExperimentPreset): ExperimentPresetRevision {
  return {
    revision_id: `${preset.preset_id}:current`,
    actor: preset.lifecycle.updated_by,
    reason: preset.lifecycle.last_action,
    created_at: preset.updated_at,
    action: "current",
    source_revision_id: null,
    name: preset.name,
    description: preset.description,
    strategy_id: preset.strategy_id ?? null,
    timeframe: preset.timeframe ?? null,
    benchmark_family: preset.benchmark_family ?? null,
    tags: [...preset.tags],
    parameters: { ...preset.parameters },
  };
}

function buildEmptyPresetRevisionSnapshot(): ExperimentPresetRevision {
  return {
    revision_id: "empty",
    actor: "",
    reason: "",
    created_at: "",
    action: "empty",
    source_revision_id: null,
    name: "",
    description: "",
    strategy_id: null,
    timeframe: null,
    benchmark_family: null,
    tags: [],
    parameters: {},
  };
}

function formatPresetStructuredDiffDisplayValue(value: string) {
  return value || "none";
}

function isPresetStructuredDiffObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isPresetStructuredDiffScalar(value: unknown) {
  return value === null || ["boolean", "number", "string"].includes(typeof value);
}

function arePresetStructuredDiffValuesEquivalent(left: unknown, right: unknown) {
  if (left === right) {
    return true;
  }
  if (
    typeof left === "number" &&
    Number.isNaN(left) &&
    typeof right === "number" &&
    Number.isNaN(right)
  ) {
    return true;
  }
  if (
    (Array.isArray(left) || isPresetStructuredDiffObject(left)) &&
    (Array.isArray(right) || isPresetStructuredDiffObject(right))
  ) {
    return JSON.stringify(left) === JSON.stringify(right);
  }
  return false;
}

function matchesPresetParameterSchemaType(value: unknown, expectedType?: string) {
  if (value === undefined || !expectedType) {
    return true;
  }
  switch (expectedType) {
    case "integer":
      return typeof value === "number" && Number.isInteger(value);
    case "number":
      return typeof value === "number" && Number.isFinite(value);
    case "boolean":
      return typeof value === "boolean";
    case "string":
      return typeof value === "string";
    case "array":
      return Array.isArray(value);
    case "object":
      return isPresetStructuredDiffObject(value);
    default:
      return true;
  }
}

function joinPresetStructuredDiffHints(...parts: Array<string | undefined>) {
  return parts.filter((part): part is string => Boolean(part)).join(" · ") || undefined;
}

function tokenizePresetParameterPath(pathSegments: string[]) {
  return pathSegments
    .flatMap((segment) => segment.toLowerCase().match(/[a-z0-9]+/g) ?? [])
    .filter((token) => !/^\d+$/.test(token));
}

function parsePresetTimeframeToMinutes(value: unknown) {
  if (typeof value !== "string") {
    return null;
  }
  const match = value.trim().match(/^(\d+)([mhdw])$/i);
  if (!match) {
    return null;
  }
  const amount = Number(match[1]);
  const unit = PRESET_TIMEFRAME_UNIT_TO_MINUTES[match[2].toLowerCase()];
  if (!Number.isFinite(amount) || !unit) {
    return null;
  }
  return amount * unit;
}

function buildPresetRankedStringDelta(
  existingRaw: unknown,
  incomingRaw: unknown,
  ranks: Record<string, number>,
  higherLabel: string,
  lowerLabel: string,
): PresetStructuredDiffDeltaValue | undefined {
  if (typeof existingRaw !== "string" || typeof incomingRaw !== "string") {
    return undefined;
  }
  const existingRank = ranks[existingRaw.trim().toLowerCase()];
  const incomingRank = ranks[incomingRaw.trim().toLowerCase()];
  if (existingRank === undefined || incomingRank === undefined || existingRank === incomingRank) {
    return undefined;
  }
  return {
    direction: incomingRank > existingRank ? "higher" : "lower",
    label: incomingRank > existingRank ? higherLabel : lowerLabel,
  };
}

function buildPresetParameterStrategyContext(
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  if (!schemaEntry) {
    return {
      delta: undefined,
      hint: undefined,
    };
  }
  const hint =
    typeof schemaEntry.semantic_hint === "string" && schemaEntry.semantic_hint.trim()
      ? `Strategy: ${schemaEntry.semantic_hint.trim()}`
      : undefined;
  const higherLabel =
    typeof schemaEntry.delta_higher_label === "string" && schemaEntry.delta_higher_label.trim()
      ? schemaEntry.delta_higher_label.trim()
      : undefined;
  const lowerLabel =
    typeof schemaEntry.delta_lower_label === "string" && schemaEntry.delta_lower_label.trim()
      ? schemaEntry.delta_lower_label.trim()
      : undefined;
  if (!higherLabel || !lowerLabel) {
    return {
      delta: undefined,
      hint,
    };
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw) &&
    existingRaw !== incomingRaw
  ) {
    return {
      delta: {
        direction: incomingRaw > existingRaw ? "higher" : "lower",
        label: incomingRaw > existingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean" && existingRaw !== incomingRaw) {
    return {
      delta: {
        direction: incomingRaw ? "higher" : "lower",
        label: incomingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  const existingTimeframe = parsePresetTimeframeToMinutes(existingRaw);
  const incomingTimeframe = parsePresetTimeframeToMinutes(incomingRaw);
  if (
    existingTimeframe !== null &&
    incomingTimeframe !== null &&
    existingTimeframe !== incomingTimeframe
  ) {
    return {
      delta: {
        direction: incomingTimeframe > existingTimeframe ? "higher" : "lower",
        label: incomingTimeframe > existingTimeframe ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (
    typeof existingRaw === "string" &&
    typeof incomingRaw === "string" &&
    schemaEntry.semantic_ranks
  ) {
    return {
      delta: buildPresetRankedStringDelta(
        existingRaw,
        incomingRaw,
        schemaEntry.semantic_ranks,
        higherLabel,
        lowerLabel,
      ),
      hint,
    };
  }
  return {
    delta: undefined,
    hint,
  };
}

function buildPresetParameterDomainContext(
  pathSegments: string[],
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  const tokens = tokenizePresetParameterPath(pathSegments);
  const tokenSet = new Set(tokens);
  const timeframeExisting = parsePresetTimeframeToMinutes(existingRaw);
  const timeframeIncoming = parsePresetTimeframeToMinutes(incomingRaw);
  const existingNumeric = typeof existingRaw === "number" && Number.isFinite(existingRaw);
  const incomingNumeric = typeof incomingRaw === "number" && Number.isFinite(incomingRaw);
  const hasNumericPair = existingNumeric && incomingNumeric;
  const hasTimeframeCue =
    schemaEntry?.unit === "timeframe" ||
    tokenSet.has("timeframe") ||
    tokenSet.has("interval") ||
    tokenSet.has("cadence") ||
    timeframeExisting !== null ||
    timeframeIncoming !== null;
  if (hasTimeframeCue) {
    return {
      delta:
        timeframeExisting !== null &&
        timeframeIncoming !== null &&
        timeframeExisting !== timeframeIncoming
          ? {
              direction: timeframeIncoming > timeframeExisting ? ("higher" as const) : ("lower" as const),
              label: timeframeIncoming > timeframeExisting ? "slower cadence" : "faster cadence",
            }
          : undefined,
      hint: "Domain: timeframe cadence",
    };
  }

  if (tokenSet.has("stop") && tokenSet.has("loss")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "wider stop" : "tighter stop",
          }
        : undefined,
      hint: "Domain: stop-loss guardrail",
    };
  }
  if ((tokenSet.has("take") && tokenSet.has("profit")) || tokenSet.has("target") || tokenSet.has("tp")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "farther target" : "closer target",
          }
        : undefined,
      hint: "Domain: profit target",
    };
  }
  if (
    tokenSet.has("window") ||
    tokenSet.has("lookback") ||
    tokenSet.has("period") ||
    tokenSet.has("bars") ||
    tokenSet.has("bar") ||
    tokenSet.has("length")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "longer lookback" : "shorter lookback",
          }
        : undefined,
      hint: "Domain: lookback window",
    };
  }
  if (tokenSet.has("threshold") || tokenSet.has("trigger")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "stricter threshold" : "looser threshold",
          }
        : undefined,
      hint: "Domain: decision threshold",
    };
  }
  if (tokenSet.has("confidence")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher confidence gate" : "lower confidence gate",
          }
        : undefined,
      hint: "Domain: confidence gate",
    };
  }
  if (
    tokenSet.has("position") ||
    tokenSet.has("allocation") ||
    tokenSet.has("exposure") ||
    tokenSet.has("leverage") ||
    tokenSet.has("size") ||
    tokenSet.has("notional")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher exposure cap" : "lower exposure cap",
          }
        : undefined,
      hint: "Domain: sizing / exposure",
    };
  }
  if (
    tokenSet.has("risk") ||
    tokenSet.has("drawdown") ||
    tokenSet.has("loss") ||
    tokenSet.has("fraction") ||
    tokenSet.has("ratio") ||
    tokenSet.has("pct") ||
    tokenSet.has("percent")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "larger risk budget" : "smaller risk budget",
          }
        : undefined,
      hint: "Domain: risk / ratio budget",
    };
  }

  if (tokenSet.has("profile") || tokenSet.has("mode") || tokenSet.has("style") || tokenSet.has("regime")) {
    return {
      delta:
        typeof existingRaw === "string" && typeof incomingRaw === "string"
          ? buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_AGGRESSIVENESS_RANKS,
              "more aggressive profile",
              "more conservative profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_SPEED_RANKS,
              "faster profile",
              "slower profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_CONFIDENCE_RANKS,
              "higher confidence profile",
              "lower confidence profile",
            )
          : undefined,
      hint: "Domain: categorical profile",
    };
  }

  if (Array.isArray(schemaEntry?.enum) && schemaEntry.enum.length) {
    return {
      delta: undefined,
      hint: "Domain: categorical selection",
    };
  }

  if (
    tokenSet.has("allow") ||
    tokenSet.has("enable") ||
    tokenSet.has("disable") ||
    tokenSet.has("reduce") ||
    tokenSet.has("exit")
  ) {
    return {
      delta: undefined,
      hint: "Domain: execution guardrail",
    };
  }

  return {
    delta: undefined,
    hint: undefined,
  };
}

function formatPresetParameterSchemaHint(schemaEntry?: ParameterSchema[string]) {
  if (!schemaEntry) {
    return undefined;
  }
  const parts: string[] = [];
  if (schemaEntry.type) {
    parts.push(schemaEntry.type);
  }
  if (schemaEntry.default !== undefined) {
    parts.push(`default ${formatParameterValue(schemaEntry.default)}`);
  }
  if (Array.isArray(schemaEntry.enum) && schemaEntry.enum.length) {
    parts.push(`options ${schemaEntry.enum.map((value) => formatParameterValue(value)).join("/")}`);
  }
  if (typeof schemaEntry.minimum === "number") {
    parts.push(`min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`);
  }
  if (typeof schemaEntry.maximum === "number") {
    parts.push(`max ${formatComparisonTooltipTuningValue(schemaEntry.maximum)}`);
  }
  if (schemaEntry.unit) {
    parts.push(`unit ${schemaEntry.unit}`);
  }
  if (!parts.length) {
    return undefined;
  }
  return `Schema: ${parts.join(" · ")}`;
}

function getPresetParameterSchemaEntry(
  parameterSchema: ParameterSchema | undefined,
  pathSegments: string[],
) {
  const rootSegment = pathSegments.find((segment) => !segment.startsWith("["));
  if (!rootSegment) {
    return undefined;
  }
  return parameterSchema?.[rootSegment];
}

function buildPresetStructuredDiffDelta(
  existingValue: string,
  incomingValue: string,
  existingRaw: unknown = existingValue,
  incomingRaw: unknown = incomingValue,
  schemaEntry?: ParameterSchema[string],
  domainDelta?: PresetStructuredDiffDeltaValue,
) {
  if (existingValue === incomingValue) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  if (schemaEntry?.type) {
    const existingMatchesType = matchesPresetParameterSchemaType(existingRaw, schemaEntry.type);
    const incomingMatchesType = matchesPresetParameterSchemaType(incomingRaw, schemaEntry.type);
    if (incomingRaw !== undefined && !incomingMatchesType) {
      return {
        direction: "lower" as const,
        label: `expected ${schemaEntry.type}`,
      };
    }
    if (existingRaw !== undefined && !existingMatchesType && incomingMatchesType) {
      return {
        direction: "higher" as const,
        label: `matches ${schemaEntry.type}`,
      };
    }
  }
  if (schemaEntry?.default !== undefined) {
    const existingIsDefault = arePresetStructuredDiffValuesEquivalent(existingRaw, schemaEntry.default);
    const incomingIsDefault = arePresetStructuredDiffValuesEquivalent(incomingRaw, schemaEntry.default);
    if (existingRaw === undefined && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `explicit default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (!existingIsDefault && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `back to default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (existingIsDefault && !incomingIsDefault) {
      return {
        direction:
          domainDelta?.direction ??
          (typeof incomingRaw === "number" &&
          typeof schemaEntry.default === "number" &&
          Number.isFinite(incomingRaw) &&
          Number.isFinite(schemaEntry.default)
            ? incomingRaw >= schemaEntry.default
              ? ("higher" as const)
              : ("lower" as const)
            : ("higher" as const)),
        label: domainDelta
          ? `${domainDelta.label} vs default ${formatParameterValue(schemaEntry.default)}`
          : `override default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (incomingRaw === undefined && !existingIsDefault) {
      return {
        direction: "lower" as const,
        label: "cleared override",
      };
    }
  }
  if (
    typeof schemaEntry?.minimum === "number" &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    const existingMeetsMinimum =
      typeof existingRaw === "number" &&
      Number.isFinite(existingRaw) &&
      existingRaw >= schemaEntry.minimum;
    if (incomingRaw < schemaEntry.minimum) {
      return {
        direction: "lower" as const,
        label: `below min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
    if (!existingMeetsMinimum && incomingRaw >= schemaEntry.minimum) {
      return {
        direction: "higher" as const,
        label: `meets min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
  }
  if (!existingValue && incomingValue) {
    return {
      direction: "higher" as const,
      label: "added",
    };
  }
  if (existingValue && !incomingValue) {
    return {
      direction: "lower" as const,
      label: "removed",
    };
  }
  if (domainDelta) {
    return domainDelta;
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    const delta = incomingRaw - existingRaw;
    if (delta === 0) {
      return {
        direction: "same" as const,
        label: "match",
      };
    }
    return {
      direction: delta > 0 ? ("higher" as const) : ("lower" as const),
      label: `${delta > 0 ? "higher " : "lower "}${delta > 0 ? "+" : ""}${formatComparisonTooltipTuningValue(delta)}`,
    };
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean") {
    return {
      direction: incomingRaw ? ("higher" as const) : ("lower" as const),
      label: incomingRaw ? "enabled" : "disabled",
    };
  }
  if (
    Array.isArray(existingRaw) &&
    Array.isArray(incomingRaw) &&
    existingRaw.every(isPresetStructuredDiffScalar) &&
    incomingRaw.every(isPresetStructuredDiffScalar)
  ) {
    const existingItems = existingRaw.map((item) => formatParameterValue(item));
    const incomingItems = incomingRaw.map((item) => formatParameterValue(item));
    const addedItems = incomingItems.filter((item) => !existingItems.includes(item));
    const removedItems = existingItems.filter((item) => !incomingItems.includes(item));
    if (addedItems.length && !removedItems.length) {
      return {
        direction: "higher" as const,
        label: `${addedItems.length} added`,
      };
    }
    if (removedItems.length && !addedItems.length) {
      return {
        direction: "lower" as const,
        label: `${removedItems.length} removed`,
      };
    }
    if (addedItems.length || removedItems.length) {
      return {
        direction: addedItems.length >= removedItems.length ? ("higher" as const) : ("lower" as const),
        label: `${addedItems.length} added · ${removedItems.length} removed`,
      };
    }
  }
  return {
    direction: "higher" as const,
    label: "changed",
  };
}

function summarizePresetStructuredDiffGroup(group: PresetStructuredDiffGroup) {
  if (!group.changed_count) {
    return `${group.same_count} unchanged`;
  }
  const parts = [`${group.changed_count} changed`];
  if (group.higher_count) {
    parts.push(`${group.higher_count} higher/add`);
  }
  if (group.lower_count) {
    parts.push(`${group.lower_count} lower/remove`);
  }
  if (group.same_count) {
    parts.push(`${group.same_count} unchanged`);
  }
  return parts.join(" · ");
}

function groupPresetStructuredDiffRows(rows: PresetStructuredDiffRow[]) {
  const groups = rows.reduce<Record<string, PresetStructuredDiffGroup>>((accumulator, row) => {
    const existing = accumulator[row.group_key] ?? {
      changed_count: 0,
      higher_count: 0,
      key: row.group_key,
      label: row.group_label,
      lower_count: 0,
      rows: [],
      same_count: 0,
      summary_label: "",
    };
    existing.rows.push(row);
    if (row.changed) {
      existing.changed_count += 1;
      if (row.delta_direction === "higher") {
        existing.higher_count += 1;
      } else if (row.delta_direction === "lower") {
        existing.lower_count += 1;
      }
    } else {
      existing.same_count += 1;
    }
    accumulator[row.group_key] = existing;
    return accumulator;
  }, {});
  return Object.values(groups)
    .map((group) => ({
      ...group,
      rows: group.rows.sort((left, right) => left.label.localeCompare(right.label)),
      summary_label: summarizePresetStructuredDiffGroup(group),
    }))
    .sort((left, right) => {
      const leftOrder = left.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder - rightOrder || left.label.localeCompare(right.label);
    });
}

function buildPresetStructuredDiffRows(
  existing: ExperimentPresetRevision,
  incoming: ExperimentPresetRevision,
  parameterSchema?: ParameterSchema,
) {
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
    existingRaw: unknown = existingValue,
    incomingRaw: unknown = incomingValue,
    semanticHint?: string,
    schemaEntry?: ParameterSchema[string],
    domainDelta?: PresetStructuredDiffDeltaValue,
  ) => {
    const delta = buildPresetStructuredDiffDelta(
      existingValue,
      incomingValue,
      existingRaw,
      incomingRaw,
      schemaEntry,
      domainDelta,
    );
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
      semantic_hint: semanticHint,
    });
  };
  const formatParameterPathLabel = (segments: string[]) =>
    segments.reduce((label, segment) => {
      if (!label) {
        return segment;
      }
      if (segment.startsWith("[")) {
        return `${label}${segment}`;
      }
      return `${label}.${segment}`;
    }, "");
  const pushParameterRow = (
    pathSegments: string[],
    existingParameter: unknown,
    incomingParameter: unknown,
  ) => {
    const label = formatParameterPathLabel(pathSegments) || "Parameter bundle";
    const existingValue = existingParameter === undefined ? "" : formatParameterValue(existingParameter);
    const incomingValue = incomingParameter === undefined ? "" : formatParameterValue(incomingParameter);
    const schemaEntry = getPresetParameterSchemaEntry(parameterSchema, pathSegments);
    const strategyContext = buildPresetParameterStrategyContext(
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    const domainContext = buildPresetParameterDomainContext(
      pathSegments,
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    pushRow(
      `parameter:${label}`,
      label,
      existingValue,
      incomingValue,
      "parameters",
      "Parameters",
      3,
      existingParameter,
      incomingParameter,
      joinPresetStructuredDiffHints(
        formatPresetParameterSchemaHint(schemaEntry),
        strategyContext.hint,
        domainContext.hint,
      ),
      schemaEntry,
      strategyContext.delta ?? domainContext.delta,
    );
  };
  const appendParameterRows = (
    existingParameter: unknown,
    incomingParameter: unknown,
    pathSegments: string[] = [],
  ) => {
    if (isPresetStructuredDiffObject(existingParameter) && incomingParameter === undefined) {
      appendParameterRows(existingParameter, {}, pathSegments);
      return;
    }
    if (existingParameter === undefined && isPresetStructuredDiffObject(incomingParameter)) {
      appendParameterRows({}, incomingParameter, pathSegments);
      return;
    }
    if (Array.isArray(existingParameter) && incomingParameter === undefined) {
      if (existingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows(existingParameter, [], pathSegments);
      }
      return;
    }
    if (existingParameter === undefined && Array.isArray(incomingParameter)) {
      if (incomingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows([], incomingParameter, pathSegments);
      }
      return;
    }
    if (
      Array.isArray(existingParameter) &&
      Array.isArray(incomingParameter) &&
      existingParameter.every(isPresetStructuredDiffScalar) &&
      incomingParameter.every(isPresetStructuredDiffScalar)
    ) {
      pushParameterRow(pathSegments, existingParameter, incomingParameter);
      return;
    }
    if (Array.isArray(existingParameter) && Array.isArray(incomingParameter)) {
      const length = Math.max(existingParameter.length, incomingParameter.length);
      for (let index = 0; index < length; index += 1) {
        appendParameterRows(existingParameter[index], incomingParameter[index], [...pathSegments, `[${index}]`]);
      }
      return;
    }
    if (isPresetStructuredDiffObject(existingParameter) && isPresetStructuredDiffObject(incomingParameter)) {
      const keys = Array.from(
        new Set([...Object.keys(existingParameter), ...Object.keys(incomingParameter)]),
      ).sort();
      if (!keys.length) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
        return;
      }
      keys.forEach((key) => {
        appendParameterRows(existingParameter[key], incomingParameter[key], [...pathSegments, key]);
      });
      return;
    }
    pushParameterRow(pathSegments, existingParameter, incomingParameter);
  };

  pushRow("name", "Name", existing.name, incoming.name, "identity", "Identity", 0);
  pushRow(
    "description",
    "Description",
    existing.description,
    incoming.description,
    "identity",
    "Identity",
    0,
  );
  pushRow(
    "strategy",
    "Strategy",
    existing.strategy_id ?? "",
    incoming.strategy_id ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "timeframe",
    "Timeframe",
    existing.timeframe ?? "",
    incoming.timeframe ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    existing.benchmark_family ?? "",
    incoming.benchmark_family ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    existing.tags.join(", "),
    incoming.tags.join(", "),
    "metadata",
    "Metadata",
    2,
  );

  const parameterKeys = Array.from(
    new Set([...Object.keys(existing.parameters), ...Object.keys(incoming.parameters)]),
  ).sort();
  if (!parameterKeys.length) {
    pushRow("parameters", "Parameter bundle", "", "", "parameters", "Parameters", 3);
  } else {
    parameterKeys.forEach((key) => {
      appendParameterRows(existing.parameters[key], incoming.parameters[key], [key]);
    });
  }
  return rows;
}

function describePresetRevisionDiff(
  revision: ExperimentPresetRevision,
  reference: ExperimentPresetRevision | null,
  basisLabel: string,
  parameterSchema?: ParameterSchema,
): PresetRevisionDiff {
  const rows = buildPresetStructuredDiffRows(
    reference ?? buildEmptyPresetRevisionSnapshot(),
    revision,
    parameterSchema,
  );
  const changedGroups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const unchangedGroups = groupPresetStructuredDiffRows(rows.filter((row) => !row.changed));
  const searchTexts = rows.map(
    (row) =>
      `${row.label} ${row.semantic_hint ?? ""} ${row.existing_value} ${row.incoming_value} ${row.delta_label}`,
  );
  const changeCount = changedGroups.reduce((total, group) => total + group.changed_count, 0);

  return {
    basisLabel,
    changeCount,
    changedGroups,
    unchangedGroups,
    searchTexts,
    summary: changeCount
      ? `${changeCount} change${changeCount === 1 ? "" : "s"} vs ${basisLabel}.`
      : `Matches ${basisLabel}.`,
  };
}

function describePresetDraftConflict(
  preset: ExperimentPreset,
  form: typeof defaultPresetForm,
  parameterSchema?: ParameterSchema,
): PresetDraftConflict {
  const savedForm = buildPresetFormFromPreset(preset);
  let normalizedDraftParameters = form.parameters_text.trim();
  let parsedDraftParameters: Record<string, unknown> = {};
  let hasInvalidParameters = false;
  if (normalizedDraftParameters) {
    try {
      parsedDraftParameters = parseJsonObjectInput(form.parameters_text);
      normalizedDraftParameters = JSON.stringify(parsedDraftParameters, null, 2);
    } catch {
      hasInvalidParameters = true;
    }
  }
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
  ) => {
    const delta = buildPresetStructuredDiffDelta(existingValue, incomingValue);
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
    });
  };
  pushRow("name", "Name", savedForm.name, form.name, "identity", "Draft fields", 0);
  pushRow(
    "description",
    "Description",
    savedForm.description,
    form.description,
    "identity",
    "Draft fields",
    0,
  );
  pushRow("strategy", "Strategy", savedForm.strategy_id, form.strategy_id, "scope", "Scope", 1);
  pushRow(
    "timeframe",
    "Timeframe",
    savedForm.timeframe.trim(),
    form.timeframe.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    savedForm.benchmark_family.trim(),
    form.benchmark_family.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    parseExperimentTags(savedForm.tags_text).join(", "),
    parseExperimentTags(form.tags_text).join(", "),
    "metadata",
    "Metadata",
    2,
  );
  if (hasInvalidParameters) {
    pushRow(
      "parameters_json",
      "Parameters JSON (invalid draft)",
      savedForm.parameters_text.trim(),
      normalizedDraftParameters,
      "parameters",
      "Parameters",
      3,
    );
  } else {
    const revisionRows = buildPresetStructuredDiffRows(
      buildCurrentPresetRevisionSnapshot(preset),
      {
        ...buildCurrentPresetRevisionSnapshot(preset),
        name: form.name,
        description: form.description,
        strategy_id: form.strategy_id || null,
        timeframe: form.timeframe.trim() || null,
        benchmark_family: form.benchmark_family.trim() || null,
        tags: parseExperimentTags(form.tags_text),
        parameters: parsedDraftParameters,
      },
      parameterSchema,
    );
    rows.push(...revisionRows.filter((row) => row.group_key === "parameters"));
  }
  const groups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const changeCount = groups.reduce((total, group) => total + group.changed_count, 0);
  return {
    changeCount,
    groups,
    hasInvalidParameters,
    summary: changeCount
      ? `${changeCount} unsaved draft field${changeCount === 1 ? "" : "s"} differ from the saved bundle.`
      : "Current draft matches the saved bundle.",
  };
}

function matchesPresetRevisionFilter(
  revision: ExperimentPresetRevision,
  diff: PresetRevisionDiff,
  filter: PresetRevisionFilterState,
) {
  if (filter.action !== "all" && revision.action !== filter.action) {
    return false;
  }
  const query = filter.query.trim().toLowerCase();
  if (!query) {
    return true;
  }
  const searchable = [
    revision.revision_id,
    revision.actor,
    revision.reason,
    revision.action,
    revision.name,
    revision.description,
    revision.strategy_id ?? "",
    revision.timeframe ?? "",
    revision.benchmark_family ?? "",
    revision.tags.join(" "),
    Object.keys(revision.parameters).join(" "),
    diff.summary,
    ...diff.searchTexts,
  ]
    .join(" ")
    .toLowerCase();
  return searchable.includes(query);
}

function formatRelativeTimestampLabel(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) {
    return formatTimestamp(value);
  }
  const relative = formatComparisonTooltipConflictSessionRelativeTime(timestamp, new Date());
  return relative ? `${relative} · ${formatTimestamp(value)}` : formatTimestamp(value);
}

const defaultRunHistoryFilter: RunHistoryFilter = {
  strategy_id: ALL_FILTER_VALUE,
  strategy_version: ALL_FILTER_VALUE,
  preset_id: "",
  benchmark_family: "",
  tag: "",
  dataset_identity: "",
};

const DEFAULT_COMPARISON_INTENT: ComparisonIntent = "benchmark_validation";
const comparisonIntentOptions: ComparisonIntent[] = [
  "benchmark_validation",
  "execution_regression",
  "strategy_tuning",
];

function parseExperimentTags(value: string) {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
    ),
  );
}

function parseJsonObjectInput(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return {};
  }
  const parsed = JSON.parse(trimmed) as unknown;
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Parameter bundle must be a JSON object.");
  }
  return parsed as Record<string, unknown>;
}

function formatPresetLifecycleStage(stage: string) {
  return stage.replaceAll("_", " ");
}

function buildRunSubmissionPayload(form: typeof defaultRunForm, extras: Record<string, unknown> = {}) {
  const presetId = form.preset_id.trim();
  const benchmarkFamily = form.benchmark_family.trim();
  return {
    strategy_id: form.strategy_id,
    symbol: form.symbol,
    timeframe: form.timeframe,
    initial_cash: form.initial_cash,
    fee_rate: form.fee_rate,
    slippage_bps: form.slippage_bps,
    parameters: {},
    tags: parseExperimentTags(form.tags_text),
    preset_id: presetId || null,
    benchmark_family: benchmarkFamily || null,
    ...extras,
  };
}

function normalizeRunFormPreset(
  current: typeof defaultRunForm,
  presets: ExperimentPreset[],
) {
  if (!current.preset_id) {
    return current;
  }
  const matchingPreset = presets.find((preset) => preset.preset_id === current.preset_id);
  if (
    matchingPreset &&
    matchingPreset.lifecycle.stage !== "archived" &&
    (!matchingPreset.strategy_id || matchingPreset.strategy_id === current.strategy_id) &&
    (!matchingPreset.timeframe || matchingPreset.timeframe === current.timeframe)
  ) {
    return current;
  }
  return {
    ...current,
    preset_id: "",
  };
}

export default function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [references, setReferences] = useState<ReferenceSource[]>([]);
  const [presets, setPresets] = useState<ExperimentPreset[]>([]);
  const [backtests, setBacktests] = useState<Run[]>([]);
  const [sandboxRuns, setSandboxRuns] = useState<Run[]>([]);
  const [paperRuns, setPaperRuns] = useState<Run[]>([]);
  const [liveRuns, setLiveRuns] = useState<Run[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketDataStatus | null>(null);
  const [operatorVisibility, setOperatorVisibility] = useState<OperatorVisibility | null>(null);
  const [guardedLive, setGuardedLive] = useState<GuardedLiveStatus | null>(null);
  const [statusText, setStatusText] = useState("Loading control room...");
  const [guardedLiveReason, setGuardedLiveReason] = useState("operator_safety_drill");
  const [liveOrderReplacementDrafts, setLiveOrderReplacementDrafts] = useState<
    Record<string, LiveOrderReplacementDraft>
  >({});
  const [presetForm, setPresetForm] = useState(defaultPresetForm);
  const [editingPresetId, setEditingPresetId] = useState<string | null>(null);
  const [expandedPresetRevisionIds, setExpandedPresetRevisionIds] = useState<Record<string, boolean>>({});
  const [backtestForm, setBacktestForm] = useState(defaultRunForm);
  const [sandboxForm, setSandboxForm] = useState(defaultRunForm);
  const [liveForm, setLiveForm] = useState(defaultRunForm);
  const [backtestRunFilter, setBacktestRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const [sandboxRunFilter, setSandboxRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const [paperRunFilter, setPaperRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const [liveRunFilter, setLiveRunFilter] = useState<RunHistoryFilter>(defaultRunHistoryFilter);
  const initialComparisonSelectionRef = useRef<ControlRoomComparisonSelectionState | null>(null);
  if (!initialComparisonSelectionRef.current) {
    initialComparisonSelectionRef.current = loadPersistedComparisonSelection();
  }
  const [selectedComparisonRunIds, setSelectedComparisonRunIds] = useState<string[]>(
    () => initialComparisonSelectionRef.current?.selectedRunIds ?? [],
  );
  const [comparisonIntent, setComparisonIntent] = useState<ComparisonIntent>(
    () => initialComparisonSelectionRef.current?.intent ?? DEFAULT_COMPARISON_INTENT,
  );
  const [selectedComparisonScoreLink, setSelectedComparisonScoreLink] =
    useState<ComparisonScoreLinkTarget | null>(
      () => initialComparisonSelectionRef.current?.scoreLink ?? null,
    );
  const [runComparison, setRunComparison] = useState<RunComparison | null>(null);
  const [runComparisonLoading, setRunComparisonLoading] = useState(false);
  const [runComparisonError, setRunComparisonError] = useState<string | null>(null);
  const [expandedGapRows, setExpandedGapRows] = useState<Record<string, boolean>>(
    loadExpandedGapRows,
  );
  const [comparisonHistoryPanel, setComparisonHistoryPanel] = useState<ComparisonHistoryPanelState>({
    entries: [],
    activeEntryId: null,
  });
  const [comparisonHistoryPanelOpen, setComparisonHistoryPanelOpen] = useState(false);
  const comparisonHistoryWriteModeRef = useRef<ComparisonHistoryWriteMode>("replace");
  const comparisonHistoryUrlRef = useRef<string | null>(null);
  const comparisonSelection = useMemo(
    () =>
      normalizeControlRoomComparisonSelection({
        intent: comparisonIntent,
        scoreLink: selectedComparisonScoreLink,
        selectedRunIds: selectedComparisonRunIds,
      }),
    [comparisonIntent, selectedComparisonRunIds, selectedComparisonScoreLink],
  );
  const comparisonHistoryStep = useMemo(
    () => buildComparisonHistoryStepDescriptor(comparisonSelection, backtests, runComparison),
    [backtests, comparisonSelection, runComparison],
  );
  const comparisonHistoryActiveIndex = useMemo(
    () =>
      comparisonHistoryPanel.activeEntryId
        ? comparisonHistoryPanel.entries.findIndex(
            (entry) => entry.entryId === comparisonHistoryPanel.activeEntryId,
          )
        : -1,
    [comparisonHistoryPanel],
  );
  const applyComparisonSelectionState = (
    value: ControlRoomComparisonSelectionState,
  ) => {
    const normalizedValue = normalizeControlRoomComparisonSelection(value);
    setSelectedComparisonRunIds(normalizedValue.selectedRunIds);
    setComparisonIntent(normalizedValue.intent);
    setSelectedComparisonScoreLink(normalizedValue.scoreLink);
  };
  const queueComparisonHistoryWriteMode = (mode: ComparisonHistoryWriteMode) => {
    comparisonHistoryWriteModeRef.current = mode;
  };
  const handleComparisonIntentChange = (intent: ComparisonIntent) => {
    if (intent === comparisonIntent) {
      return;
    }
    queueComparisonHistoryWriteMode("push");
    setComparisonIntent(intent);
  };
  const handleSelectedComparisonScoreLinkChange = (
    value: ComparisonScoreLinkTarget | null,
    historyMode: ComparisonHistoryWriteMode = "push",
  ) => {
    queueComparisonHistoryWriteMode(historyMode);
    setSelectedComparisonScoreLink(value);
  };

  async function loadAll() {
    setStatusText("Refreshing data plane...");
    try {
      const [
        strategiesResponse,
        referencesResponse,
        presetsResponse,
        backtestsResponse,
        sandboxResponse,
        paperResponse,
        liveResponse,
        marketResponse,
        operatorResponse,
        guardedLiveResponse,
      ] = await Promise.all([
        fetchJson<Strategy[]>("/strategies"),
        fetchJson<ReferenceSource[]>("/references"),
        fetchJson<ExperimentPreset[]>("/presets"),
        fetchJson<Run[]>(buildRunsPath("backtest", backtestRunFilter)),
        fetchJson<Run[]>(buildRunsPath("sandbox", sandboxRunFilter)),
        fetchJson<Run[]>(buildRunsPath("paper", paperRunFilter)),
        fetchJson<Run[]>(buildRunsPath("live", liveRunFilter)),
        fetchJson<MarketDataStatus>("/market-data/status"),
        fetchJson<OperatorVisibility>("/operator/visibility"),
        fetchJson<GuardedLiveStatus>("/guarded-live"),
      ]);
      setStrategies(strategiesResponse);
      setReferences(referencesResponse);
      setPresets(presetsResponse);
      setBacktests(backtestsResponse);
      setSandboxRuns(sandboxResponse);
      setPaperRuns(paperResponse);
      setLiveRuns(liveResponse);
      setMarketStatus(marketResponse);
      setOperatorVisibility(operatorResponse);
      setGuardedLive(guardedLiveResponse);
      setStatusText("Control room synchronized.");
    } catch (error) {
      setStatusText(`Load failed: ${(error as Error).message}`);
    }
  }

  useEffect(() => {
    void loadAll();
  }, [backtestRunFilter, sandboxRunFilter, paperRunFilter, liveRunFilter]);

  useEffect(() => {
    if (!strategies.length) {
      return;
    }
    const preferredNative = strategies.find((strategy) => strategy.runtime === "native") ?? strategies[0];
    setBacktestForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
    setSandboxForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
    setLiveForm((current) => ({ ...current, strategy_id: preferredNative.strategy_id }));
  }, [strategies]);

  useEffect(() => {
    setBacktestForm((current) => normalizeRunFormPreset(current, presets));
    setSandboxForm((current) => normalizeRunFormPreset(current, presets));
    setLiveForm((current) => normalizeRunFormPreset(current, presets));
    setBacktestRunFilter((current) => normalizeRunHistoryPresetFilter(current, presets));
    setSandboxRunFilter((current) => normalizeRunHistoryPresetFilter(current, presets));
    setPaperRunFilter((current) => normalizeRunHistoryPresetFilter(current, presets));
    setLiveRunFilter((current) => normalizeRunHistoryPresetFilter(current, presets));
  }, [presets]);

  useEffect(() => {
    if (!editingPresetId) {
      return;
    }
    const editingPreset = presets.find((preset) => preset.preset_id === editingPresetId);
    if (!editingPreset) {
      setEditingPresetId(null);
      setPresetForm((current) => ({
        ...defaultPresetForm,
        strategy_id: current.strategy_id,
        timeframe: current.timeframe,
      }));
      return;
    }
    setPresetForm(buildPresetFormFromPreset(editingPreset));
  }, [editingPresetId, presets]);

  useEffect(() => {
    if (!strategies.length) {
      return;
    }
    setBacktestRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
    setSandboxRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
    setPaperRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
    setLiveRunFilter((current) => normalizeRunHistoryFilter(current, strategies));
  }, [strategies]);

  useEffect(() => {
    const availableRunIds = new Set(backtests.map((run) => run.config.run_id));
    setSelectedComparisonRunIds((current) => {
      const next = current.filter((runId) => availableRunIds.has(runId));
      if (next.length !== current.length) {
        queueComparisonHistoryWriteMode("replace");
      }
      return next.length === current.length ? current : next;
    });
  }, [backtests]);

  useEffect(() => {
    if (!selectedComparisonScoreLink) {
      return;
    }
    if (selectedComparisonRunIds.includes(selectedComparisonScoreLink.narrativeRunId)) {
      return;
    }
    handleSelectedComparisonScoreLinkChange(null, "replace");
  }, [selectedComparisonRunIds, selectedComparisonScoreLink]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const handlePopState = (event: PopStateEvent) => {
      queueComparisonHistoryWriteMode("skip");
      const historyBrowserState = readComparisonHistoryBrowserState(event.state);
      const nextSelection =
        loadComparisonSelectionFromUrl()
        ?? historyBrowserState?.selection
        ?? defaultControlRoomComparisonSelectionState();
      if (historyBrowserState) {
        setComparisonHistoryPanel((current) =>
          reconcileComparisonHistoryPanelState(
            current,
            buildComparisonHistoryPanelEntry(
              historyBrowserState,
              `${window.location.pathname}${window.location.search}${window.location.hash}`,
            ),
            "activate",
          ),
        );
      } else {
        setComparisonHistoryPanel({
          entries: [],
          activeEntryId: null,
        });
      }
      applyComparisonSelectionState(nextSelection);
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (selectedComparisonRunIds.length < 2) {
      setRunComparison(null);
      setRunComparisonError(null);
      setRunComparisonLoading(false);
      return;
    }

    let cancelled = false;
    setRunComparisonLoading(true);
    setRunComparisonError(null);

    void fetchJson<RunComparison>(buildRunComparisonPath(selectedComparisonRunIds, comparisonIntent))
      .then((payload) => {
        if (cancelled) {
          return;
        }
        setRunComparison(payload);
      })
      .catch((error) => {
        if (cancelled) {
          return;
        }
        setRunComparison(null);
        setRunComparisonError((error as Error).message);
      })
      .finally(() => {
        if (!cancelled) {
          setRunComparisonLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedComparisonRunIds, comparisonIntent]);

  useEffect(() => {
    persistControlRoomUiState({
      comparisonSelection,
      expandedGapRows,
    });
  }, [comparisonSelection, expandedGapRows]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const nextUrl = buildComparisonSelectionHistoryUrl(comparisonSelection);
    const currentUrl = buildComparisonSelectionHistoryUrl(
      loadComparisonSelectionFromUrl() ?? defaultControlRoomComparisonSelectionState(),
    );
    const currentBrowserState = readComparisonHistoryBrowserState(window.history.state);
    const nextEntryId =
      comparisonHistoryWriteModeRef.current === "push"
        ? buildComparisonHistoryEntryId()
        : currentBrowserState?.entryId ?? buildComparisonHistoryEntryId();
    const nextBrowserState = readComparisonHistoryBrowserState(buildComparisonHistoryBrowserState(
      window.history.state,
      comparisonSelection,
      comparisonHistoryStep,
      nextEntryId,
    ));
    if (!nextBrowserState) {
      return;
    }
    const metadataChanged = !isSameComparisonHistoryBrowserState(
      currentBrowserState,
      nextBrowserState,
    );
    const writeMode = comparisonHistoryWriteModeRef.current;
    comparisonHistoryWriteModeRef.current = "replace";

    if (comparisonHistoryUrlRef.current === null) {
      comparisonHistoryUrlRef.current = nextUrl;
      if (currentUrl !== nextUrl || metadataChanged) {
        persistComparisonSelectionToUrl(comparisonSelection, comparisonHistoryStep, nextEntryId, "replace");
      }
      setComparisonHistoryPanel((current) =>
        reconcileComparisonHistoryPanelState(
          current,
          buildComparisonHistoryPanelEntry(nextBrowserState, nextUrl),
          "replace",
        ),
      );
      return;
    }

    if (writeMode === "skip") {
      comparisonHistoryUrlRef.current = nextUrl;
      setComparisonHistoryPanel((current) =>
        reconcileComparisonHistoryPanelState(
          current,
          buildComparisonHistoryPanelEntry(currentBrowserState ?? nextBrowserState, nextUrl),
          currentBrowserState ? "activate" : "replace",
        ),
      );
      return;
    }

    if (
      comparisonHistoryUrlRef.current === nextUrl
      && currentUrl === nextUrl
      && !metadataChanged
    ) {
      return;
    }

    if (writeMode === "push") {
      if (currentUrl !== nextUrl) {
        persistComparisonSelectionToUrl(
          comparisonSelection,
          comparisonHistoryStep,
          nextEntryId,
          "push",
        );
      } else if (metadataChanged) {
        persistComparisonSelectionToUrl(
          comparisonSelection,
          comparisonHistoryStep,
          nextEntryId,
          "replace",
        );
      }
      comparisonHistoryUrlRef.current = nextUrl;
      setComparisonHistoryPanel((current) =>
        reconcileComparisonHistoryPanelState(
          current,
          buildComparisonHistoryPanelEntry(nextBrowserState, nextUrl),
          currentUrl !== nextUrl ? "push" : "replace",
        ),
      );
      return;
    }

    if (currentUrl !== nextUrl || metadataChanged) {
      persistComparisonSelectionToUrl(
        comparisonSelection,
        comparisonHistoryStep,
        nextEntryId,
        "replace",
      );
    }
    comparisonHistoryUrlRef.current = nextUrl;
    setComparisonHistoryPanel((current) =>
      reconcileComparisonHistoryPanelState(
        current,
        buildComparisonHistoryPanelEntry(nextBrowserState, nextUrl),
        "replace",
      ),
    );
  }, [comparisonHistoryStep, comparisonSelection]);

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.title = comparisonHistoryStep.title;
  }, [comparisonHistoryStep]);

  const handleNavigateComparisonHistoryEntry = (entryId: string) => {
    if (typeof window === "undefined") {
      return;
    }
    const targetIndex = comparisonHistoryPanel.entries.findIndex((entry) => entry.entryId === entryId);
    if (targetIndex < 0 || comparisonHistoryActiveIndex < 0) {
      return;
    }
    const delta = targetIndex - comparisonHistoryActiveIndex;
    if (delta === 0) {
      return;
    }
    window.history.go(delta);
  };

  const handleNavigateComparisonHistoryRelative = (delta: number) => {
    if (typeof window === "undefined" || delta === 0 || comparisonHistoryActiveIndex < 0) {
      return;
    }
    const targetIndex = comparisonHistoryActiveIndex + delta;
    if (targetIndex < 0 || targetIndex >= comparisonHistoryPanel.entries.length) {
      return;
    }
    window.history.go(delta);
  };

  useEffect(() => {
    if (!marketStatus) {
      return;
    }
    setExpandedGapRows((current) => pruneExpandedGapRows(current, marketStatus));
  }, [marketStatus]);

  const strategyGroups = useMemo(() => {
    return {
      native: strategies.filter((strategy) => strategy.runtime === "native"),
      reference: strategies.filter((strategy) => strategy.runtime === "freqtrade_reference"),
      future: strategies.filter((strategy) => strategy.runtime === "decision_engine"),
    };
  }, [strategies]);

  const backfillSummary = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    const tracked = marketStatus.instruments.filter(
      (instrument) => instrument.backfill_target_candles !== null,
    );
    if (!tracked.length) {
      return null;
    }
    const contiguousTracked = tracked.filter(
      (instrument) => instrument.backfill_contiguous_completion_ratio !== null,
    );
    const targetCandles = tracked.reduce(
      (total, instrument) => total + (instrument.backfill_target_candles ?? 0),
      0,
    );
    const coveredCandles = tracked.reduce(
      (total, instrument) =>
        total +
        Math.min(
          instrument.candle_count,
          instrument.backfill_target_candles ?? instrument.candle_count,
        ),
      0,
    );
    const completeCount = tracked.filter((instrument) => instrument.backfill_complete).length;
    return {
      targetCandles,
      coveredCandles,
      completeCount,
      instrumentCount: tracked.length,
      completionRatio: targetCandles > 0 ? coveredCandles / targetCandles : null,
      contiguousQualityRatio:
        contiguousTracked.length > 0
          ? contiguousTracked.reduce(
              (total, instrument) =>
                total + (instrument.backfill_contiguous_completion_ratio ?? 0),
              0,
            ) / contiguousTracked.length
          : null,
      contiguousCompleteCount: contiguousTracked.filter(
        (instrument) => instrument.backfill_contiguous_complete,
      ).length,
      contiguousInstrumentCount: contiguousTracked.length,
    };
  }, [marketStatus]);

  const failureSummary = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    const instrumentsWithFailures = marketStatus.instruments.filter(
      (instrument) => instrument.failure_count_24h > 0,
    );
    return {
      failureCount24h: marketStatus.instruments.reduce(
        (total, instrument) => total + instrument.failure_count_24h,
        0,
      ),
      affectedInstrumentCount: instrumentsWithFailures.length,
      lastFailureAt:
        instrumentsWithFailures
          .flatMap((instrument) => instrument.recent_failures.map((failure) => failure.failed_at))
          .sort()
          .at(-1) ?? null,
    };
  }, [marketStatus]);

  const operatorSummary = useMemo(() => {
    if (!operatorVisibility) {
      return null;
    }
    const criticalCount = operatorVisibility.alerts.filter((alert) => alert.severity === "critical").length;
    const warningCount = operatorVisibility.alerts.filter((alert) => alert.severity === "warning").length;
    return {
      alertCount: operatorVisibility.alerts.length,
      criticalCount,
      warningCount,
      historyCount: operatorVisibility.alert_history.length,
      incidentCount: operatorVisibility.incident_events.length,
      deliveryCount: operatorVisibility.delivery_history.length,
      latestAuditAt: operatorVisibility.audit_events[0]?.timestamp ?? null,
    };
  }, [operatorVisibility]);

  const guardedLiveSummary = useMemo(() => {
    if (!guardedLive) {
      return null;
    }
    return {
      blockerCount: guardedLive.blockers.length,
      latestAuditAt: guardedLive.audit_events[0]?.timestamp ?? null,
      latestReconciliationAt: guardedLive.reconciliation.checked_at ?? null,
      latestRecoveryAt: guardedLive.recovery.recovered_at ?? null,
      latestOrderSyncAt: guardedLive.order_book.synced_at ?? guardedLive.ownership.last_order_sync_at ?? null,
      latestSessionRestoreAt: guardedLive.session_restore.restored_at ?? null,
      latestSessionHandoffAt: guardedLive.session_handoff.last_sync_at ?? guardedLive.session_handoff.handed_off_at ?? null,
    };
  }, [guardedLive]);

  const activeGuardedLiveAlertIds = useMemo(
    () => new Set((guardedLive?.active_alerts ?? []).map((alert) => alert.alert_id)),
    [guardedLive],
  );

  function resolveGuardedLiveReason(fallback: string) {
    const trimmed = guardedLiveReason.trim();
    return trimmed.length ? trimmed : fallback;
  }

  async function handlePresetSubmit(event: FormEvent) {
    event.preventDefault();
    const editing = editingPresetId !== null;
    setStatusText(editing ? "Updating experiment preset..." : "Saving experiment preset...");
    try {
      const parameters = parseJsonObjectInput(presetForm.parameters_text);
      const payload = {
        name: presetForm.name,
        description: presetForm.description,
        strategy_id: presetForm.strategy_id || null,
        timeframe: presetForm.timeframe.trim() || null,
        benchmark_family: presetForm.benchmark_family.trim() || null,
        tags: parseExperimentTags(presetForm.tags_text),
        parameters,
      };
      const savedPreset = editing
        ? await fetchJson<ExperimentPreset>(`/presets/${encodeURIComponent(editingPresetId)}`, {
            method: "PATCH",
            body: JSON.stringify({
              ...payload,
              actor: "operator",
              reason: "control_room_bundle_edit",
            }),
          })
        : await fetchJson<ExperimentPreset>("/presets", {
            method: "POST",
            body: JSON.stringify({
              ...payload,
              preset_id: presetForm.preset_id.trim() || null,
            }),
          });
      setPresetForm(
        editing
          ? buildPresetFormFromPreset(savedPreset)
          : {
              ...defaultPresetForm,
              strategy_id: presetForm.strategy_id,
              timeframe: presetForm.timeframe,
            },
      );
      if (editing) {
        setExpandedPresetRevisionIds((current) => ({ ...current, [savedPreset.preset_id]: true }));
      }
      await loadAll();
    } catch (error) {
      setStatusText(`Preset ${editing ? "update" : "save"} failed: ${(error as Error).message}`);
    }
  }

  async function applyPresetLifecycleAction(presetId: string, action: "promote" | "archive" | "restore") {
    setStatusText(`Applying preset lifecycle action ${action} to ${presetId}...`);
    try {
      await fetchJson<ExperimentPreset>(`/presets/${encodeURIComponent(presetId)}/lifecycle`, {
        method: "POST",
        body: JSON.stringify({
          action,
          actor: "operator",
          reason: `preset_${action}`,
        }),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Preset lifecycle action failed: ${(error as Error).message}`);
    }
  }

  function beginPresetEdit(preset: ExperimentPreset) {
    setEditingPresetId(preset.preset_id);
    setExpandedPresetRevisionIds((current) => ({ ...current, [preset.preset_id]: true }));
    setPresetForm(buildPresetFormFromPreset(preset));
    setStatusText(`Editing preset ${preset.preset_id}.`);
  }

  function resetPresetEditor() {
    setEditingPresetId(null);
    setPresetForm((current) => ({
      ...defaultPresetForm,
      strategy_id: current.strategy_id,
      timeframe: current.timeframe || "5m",
    }));
    setStatusText("Preset editor reset.");
  }

  function togglePresetRevisions(presetId: string) {
    setExpandedPresetRevisionIds((current) => ({
      ...current,
      [presetId]: !current[presetId],
    }));
  }

  async function restorePresetRevision(presetId: string, revisionId: string) {
    setStatusText(`Restoring preset bundle ${revisionId} for ${presetId}...`);
    try {
      const restoredPreset = await fetchJson<ExperimentPreset>(
        `/presets/${encodeURIComponent(presetId)}/revisions/${encodeURIComponent(revisionId)}/restore`,
        {
          method: "POST",
          body: JSON.stringify({
            actor: "operator",
            reason: "control_room_revision_restore",
          }),
        },
      );
      setExpandedPresetRevisionIds((current) => ({ ...current, [presetId]: true }));
      if (editingPresetId === restoredPreset.preset_id) {
        setPresetForm(buildPresetFormFromPreset(restoredPreset));
      }
      await loadAll();
    } catch (error) {
      setStatusText(`Preset revision restore failed: ${(error as Error).message}`);
    }
  }

  async function handleBacktestSubmit(event: FormEvent) {
    event.preventDefault();
    setStatusText("Running backtest...");
    try {
      await fetchJson<Run>("/runs/backtests", {
        method: "POST",
        body: JSON.stringify(buildRunSubmissionPayload(backtestForm)),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Backtest failed: ${(error as Error).message}`);
    }
  }

  async function handleSandboxSubmit(event: FormEvent) {
    event.preventDefault();
    setStatusText("Starting sandbox worker session...");
    try {
      await fetchJson<Run>("/runs/sandbox", {
        method: "POST",
        body: JSON.stringify(buildRunSubmissionPayload(sandboxForm, { replay_bars: 96 })),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Sandbox worker start failed: ${(error as Error).message}`);
    }
  }

  async function handleLiveSubmit(event: FormEvent) {
    event.preventDefault();
    const operatorReason = resolveGuardedLiveReason("guarded_live_launch");
    setStatusText("Starting guarded-live worker...");
    try {
      await fetchJson<Run>("/runs/live", {
        method: "POST",
        body: JSON.stringify(
          buildRunSubmissionPayload(liveForm, {
            replay_bars: 96,
            operator_reason: operatorReason,
          }),
        ),
      });
      await loadAll();
    } catch (error) {
      setStatusText(`Guarded-live start failed: ${(error as Error).message}`);
    }
  }

  async function stopSandboxRun(runId: string) {
    setStatusText(`Stopping sandbox worker ${runId}...`);
    try {
      await fetchJson<Run>(`/runs/sandbox/${runId}/stop`, { method: "POST" });
      await loadAll();
    } catch (error) {
      setStatusText(`Sandbox worker stop failed: ${(error as Error).message}`);
    }
  }

  async function stopPaperRun(runId: string) {
    setStatusText(`Stopping paper run ${runId}...`);
    try {
      await fetchJson<Run>(`/runs/paper/${runId}/stop`, { method: "POST" });
      await loadAll();
    } catch (error) {
      setStatusText(`Paper stop failed: ${(error as Error).message}`);
    }
  }

  async function stopLiveRun(runId: string) {
    setStatusText(`Stopping guarded-live worker ${runId}...`);
    try {
      await fetchJson<Run>(`/runs/live/${runId}/stop`, { method: "POST" });
      await loadAll();
    } catch (error) {
      setStatusText(`Guarded-live stop failed: ${(error as Error).message}`);
    }
  }

  function getLiveOrderReplacementDraft(runId: string, order: Run["orders"][number]): LiveOrderReplacementDraft {
    const key = buildLiveOrderDraftKey(runId, order.order_id);
    return liveOrderReplacementDrafts[key] ?? {
      price: formatEditableNumber(order.requested_price),
      quantity: "",
    };
  }

  function setLiveOrderReplacementDraft(
    runId: string,
    orderId: string,
    draft: LiveOrderReplacementDraft,
  ) {
    const key = buildLiveOrderDraftKey(runId, orderId);
    setLiveOrderReplacementDrafts((current) => ({
      ...current,
      [key]: draft,
    }));
  }

  async function cancelLiveOrder(runId: string, orderId: string) {
    const reason = resolveGuardedLiveReason("manual_order_cancel");
    setStatusText(`Canceling guarded-live order ${orderId}...`);
    try {
      await fetchJson<Run>(`/runs/live/${runId}/orders/${orderId}/cancel`, {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText(`Guarded-live order ${orderId} canceled.`);
    } catch (error) {
      setStatusText(`Guarded-live order cancel failed: ${(error as Error).message}`);
    }
  }

  async function replaceLiveOrder(
    runId: string,
    orderId: string,
    draft: LiveOrderReplacementDraft,
  ) {
    const price = Number(draft.price);
    if (!Number.isFinite(price) || price <= 0) {
      setStatusText(`Replacement price for ${orderId} must be positive.`);
      return;
    }
    const quantity = draft.quantity.trim().length ? Number(draft.quantity) : undefined;
    if (quantity !== undefined && (!Number.isFinite(quantity) || quantity <= 0)) {
      setStatusText(`Replacement quantity for ${orderId} must be positive when provided.`);
      return;
    }
    const reason = resolveGuardedLiveReason("manual_order_replace");
    setStatusText(`Replacing guarded-live order ${orderId}...`);
    try {
      const run = await fetchJson<Run>(`/runs/live/${runId}/orders/${orderId}/replace`, {
        method: "POST",
        body: JSON.stringify({
          actor: "operator",
          reason,
          price,
          quantity,
        }),
      });
      setLiveOrderReplacementDrafts((current) => {
        const next = { ...current };
        delete next[buildLiveOrderDraftKey(runId, orderId)];
        const replacementOrder = run.orders.at(-1);
        if (replacementOrder) {
          next[buildLiveOrderDraftKey(runId, replacementOrder.order_id)] = {
            price: formatEditableNumber(replacementOrder.requested_price),
            quantity: "",
          };
        }
        return next;
      });
      await loadAll();
      setStatusText(`Guarded-live order ${orderId} replaced.`);
    } catch (error) {
      setStatusText(`Guarded-live order replace failed: ${(error as Error).message}`);
    }
  }

  async function rerunBacktest(rerunBoundaryId: string) {
    setStatusText(`Rerunning boundary ${rerunBoundaryId}...`);
    try {
      const run = await fetchJson<Run>(`/runs/rerun-boundaries/${encodeURIComponent(rerunBoundaryId)}/backtests`, {
        method: "POST",
      });
      await loadAll();
      setStatusText(
        run.provenance.rerun_match_status === "matched"
          ? `Rerun completed and matched boundary ${rerunBoundaryId}.`
          : `Rerun completed with boundary drift from ${rerunBoundaryId}.`,
      );
    } catch (error) {
      setStatusText(`Rerun failed: ${(error as Error).message}`);
    }
  }

  async function rerunSandbox(rerunBoundaryId: string) {
    setStatusText(`Restoring sandbox worker for boundary ${rerunBoundaryId}...`);
    try {
      const run = await fetchJson<Run>(`/runs/rerun-boundaries/${encodeURIComponent(rerunBoundaryId)}/sandbox`, {
        method: "POST",
      });
      await loadAll();
      setStatusText(
        run.provenance.rerun_match_status === "matched"
          ? `Sandbox worker started and matched boundary ${rerunBoundaryId}.`
          : `Sandbox worker started with expected drift from boundary ${rerunBoundaryId}.`,
      );
    } catch (error) {
      setStatusText(`Sandbox worker restore failed: ${(error as Error).message}`);
    }
  }

  async function rerunPaper(rerunBoundaryId: string) {
    setStatusText(`Starting paper session for boundary ${rerunBoundaryId}...`);
    try {
      const run = await fetchJson<Run>(`/runs/rerun-boundaries/${encodeURIComponent(rerunBoundaryId)}/paper`, {
        method: "POST",
      });
      await loadAll();
      setStatusText(
        run.provenance.rerun_match_status === "matched"
          ? `Paper session started and matched boundary ${rerunBoundaryId}.`
          : `Paper session started with expected boundary translation from ${rerunBoundaryId}.`,
      );
    } catch (error) {
      setStatusText(`Paper session failed: ${(error as Error).message}`);
    }
  }

  async function engageGuardedLiveKillSwitch() {
    const reason = resolveGuardedLiveReason("operator_safety_drill");
    setStatusText("Engaging guarded-live kill switch...");
    try {
      await fetchJson<GuardedLiveStatus>("/guarded-live/kill-switch/engage", {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText("Guarded-live kill switch engaged.");
    } catch (error) {
      setStatusText(`Kill switch engagement failed: ${(error as Error).message}`);
    }
  }

  async function releaseGuardedLiveKillSwitch() {
    const reason = resolveGuardedLiveReason("operator_resume_drill");
    setStatusText("Releasing guarded-live kill switch...");
    try {
      await fetchJson<GuardedLiveStatus>("/guarded-live/kill-switch/release", {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText("Guarded-live kill switch released.");
    } catch (error) {
      setStatusText(`Kill switch release failed: ${(error as Error).message}`);
    }
  }

  async function runGuardedLiveReconciliation() {
    const reason = resolveGuardedLiveReason("operator_reconciliation_drill");
    setStatusText("Running guarded-live reconciliation...");
    try {
      await fetchJson<GuardedLiveStatus>("/guarded-live/reconciliation", {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText("Guarded-live reconciliation recorded.");
    } catch (error) {
      setStatusText(`Reconciliation failed: ${(error as Error).message}`);
    }
  }

  async function recoverGuardedLiveRuntime() {
    const reason = resolveGuardedLiveReason("post_fault_runtime_recovery");
    setStatusText("Recovering guarded-live runtime state...");
    try {
      await fetchJson<GuardedLiveStatus>("/guarded-live/recovery", {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText("Guarded-live runtime recovery recorded.");
    } catch (error) {
      setStatusText(`Runtime recovery failed: ${(error as Error).message}`);
    }
  }

  async function resumeGuardedLiveRun() {
    const reason = resolveGuardedLiveReason("process_restart_resume");
    setStatusText("Resuming guarded-live owner...");
    try {
      const run = await fetchJson<Run>("/guarded-live/resume", {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText(`Guarded-live owner resumed on run ${run.config.run_id}.`);
    } catch (error) {
      setStatusText(`Guarded-live resume failed: ${(error as Error).message}`);
    }
  }

  async function acknowledgeGuardedLiveIncident(eventId: string) {
    const reason = resolveGuardedLiveReason("incident_acknowledged");
    setStatusText(`Acknowledging guarded-live incident ${eventId}...`);
    try {
      await fetchJson<GuardedLiveStatus>(`/guarded-live/incidents/${encodeURIComponent(eventId)}/acknowledge`, {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText(`Guarded-live incident ${eventId} acknowledged.`);
    } catch (error) {
      setStatusText(`Incident acknowledgment failed: ${(error as Error).message}`);
    }
  }

  async function remediateGuardedLiveIncident(eventId: string) {
    const reason = resolveGuardedLiveReason("incident_remediation_requested");
    setStatusText(`Requesting guarded-live remediation for ${eventId}...`);
    try {
      await fetchJson<GuardedLiveStatus>(`/guarded-live/incidents/${encodeURIComponent(eventId)}/remediate`, {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText(`Guarded-live remediation requested for ${eventId}.`);
    } catch (error) {
      setStatusText(`Incident remediation failed: ${(error as Error).message}`);
    }
  }

  async function escalateGuardedLiveIncident(eventId: string) {
    const reason = resolveGuardedLiveReason("incident_escalated");
    setStatusText(`Escalating guarded-live incident ${eventId}...`);
    try {
      await fetchJson<GuardedLiveStatus>(`/guarded-live/incidents/${encodeURIComponent(eventId)}/escalate`, {
        method: "POST",
        body: JSON.stringify({ actor: "operator", reason }),
      });
      await loadAll();
      setStatusText(`Guarded-live incident ${eventId} escalated.`);
    } catch (error) {
      setStatusText(`Incident escalation failed: ${(error as Error).message}`);
    }
  }

  function toggleComparisonRun(runId: string) {
    setSelectedComparisonRunIds((current) => {
      if (current.includes(runId)) {
        queueComparisonHistoryWriteMode("push");
        return current.filter((value) => value !== runId);
      }
      if (current.length >= MAX_COMPARISON_RUNS) {
        setStatusText(`Comparison supports up to ${MAX_COMPARISON_RUNS} backtests at once.`);
        return current;
      }
      queueComparisonHistoryWriteMode("push");
      return [...current, runId];
    });
  }

  function clearComparisonRuns() {
    queueComparisonHistoryWriteMode("push");
    setSelectedComparisonScoreLink(null);
    setSelectedComparisonRunIds([]);
  }

  function selectBenchmarkPair() {
    const nativeRun = pickLatestBenchmarkRun(backtests, "native");
    const referenceRun = pickLatestBenchmarkRun(backtests, "reference");

    if (!nativeRun || !referenceRun) {
      setStatusText("Benchmark comparison needs one native and one reference backtest.");
      return;
    }

    queueComparisonHistoryWriteMode("push");
    setComparisonIntent(DEFAULT_COMPARISON_INTENT);
    setSelectedComparisonScoreLink(null);
    setSelectedComparisonRunIds([nativeRun.config.run_id, referenceRun.config.run_id]);
  }

  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Akra Trader / Hexagonal Control Room</p>
          <h1>Strategy operations with native engines and NFI reference delegates.</h1>
          <p className="hero-copy">
            The backend separates feature building, decision context creation, and execution so
            rule-based strategies, Freqtrade references, and future LLM policies can share the
            same orchestration layer.
          </p>
        </div>
        <aside className="hero-panel">
          <span className="status-indicator" />
          <strong>{statusText}</strong>
          <p>API base: {apiBase}</p>
        </aside>
      </header>

      <main className="grid">
        <section className="panel panel-wide">
          <div className="section-heading">
            <div>
              <p className="kicker">Strategy catalog</p>
              <h2>Runtime tiers</h2>
            </div>
            <button className="ghost-button" onClick={() => void loadAll()}>
              Refresh
            </button>
          </div>

          <div className="strategy-columns">
            <StrategyColumn title="Native" strategies={strategyGroups.native} accent="amber" />
            <StrategyColumn title="NFI References" strategies={strategyGroups.reference} accent="cyan" />
            <StrategyColumn title="Future LLM" strategies={strategyGroups.future} accent="ember" />
          </div>
        </section>

        <section className="panel">
          <p className="kicker">Backtest</p>
          <h2>Launch a run</h2>
          <RunForm
            form={backtestForm}
            setForm={setBacktestForm}
            strategies={strategies}
            presets={presets}
            onSubmit={handleBacktestSubmit}
          />
        </section>

        <section className="panel">
          <p className="kicker">Sandbox</p>
          <h2>Start sandbox worker</h2>
          <RunForm
            form={sandboxForm}
            setForm={setSandboxForm}
            strategies={strategies.filter((strategy) => strategy.runtime === "native")}
            presets={presets}
            onSubmit={handleSandboxSubmit}
          />
        </section>

        <section className="panel">
          <p className="kicker">Guarded live</p>
          <h2>Start live worker</h2>
          <RunForm
            form={liveForm}
            setForm={setLiveForm}
            strategies={strategies.filter((strategy) => strategy.runtime === "native")}
            presets={presets}
            onSubmit={handleLiveSubmit}
          />
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Experiment OS</p>
          <h2>Scenario presets</h2>
          <PresetCatalogPanel
            form={presetForm}
            presets={presets}
            setForm={setPresetForm}
            strategies={strategies}
            editingPresetId={editingPresetId}
            expandedPresetRevisionIds={expandedPresetRevisionIds}
            onEditPreset={beginPresetEdit}
            onResetEditor={resetPresetEditor}
            onLifecycleAction={applyPresetLifecycleAction}
            onRestoreRevision={restorePresetRevision}
            onSubmit={handlePresetSubmit}
            onToggleRevisions={togglePresetRevisions}
          />
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Reference lane</p>
          <h2>Third-party references</h2>
          <ReferenceCatalog references={references} />
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Data plane</p>
          <h2>Market data status</h2>
          {marketStatus ? (
            <div className="status-grid">
              <div className="metric-tile">
                <span>Provider</span>
                <strong>{marketStatus.provider}</strong>
              </div>
              <div className="metric-tile">
                <span>Venue</span>
                <strong>{marketStatus.venue}</strong>
              </div>
              <div className="metric-tile">
                <span>Tracked symbols</span>
                <strong>{marketStatus.instruments.length}</strong>
              </div>
              {failureSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Failures 24h</span>
                    <strong>{failureSummary.failureCount24h}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Affected instruments</span>
                    <strong>{failureSummary.affectedInstrumentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest failure</span>
                    <strong>{formatTimestamp(failureSummary.lastFailureAt)}</strong>
                  </div>
                </>
              ) : null}
              {backfillSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Backfill count</span>
                    <strong>{formatCompletion(backfillSummary.completionRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Count complete</span>
                    <strong>
                      {backfillSummary.completeCount} / {backfillSummary.instrumentCount}
                    </strong>
                  </div>
                  <div className="metric-tile">
                    <span>Contiguous quality</span>
                    <strong>{formatCompletion(backfillSummary.contiguousQualityRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Gap-free spans</span>
                    <strong>
                      {backfillSummary.contiguousInstrumentCount > 0
                        ? `${backfillSummary.contiguousCompleteCount} / ${backfillSummary.contiguousInstrumentCount}`
                        : "n/a"}
                    </strong>
                  </div>
                </>
              ) : null}
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Instrument</th>
                    <th>Timeframe</th>
                    <th>Sync</th>
                    <th>Candles</th>
                    <th>Target</th>
                    <th>Count</th>
                    <th>Quality</th>
                    <th>Lag</th>
                    <th>Latest</th>
                    <th>Checkpoint</th>
                    <th>Failures</th>
                    <th>Issues</th>
                  </tr>
                </thead>
                <tbody>
                  {marketStatus.instruments.map((instrument) => (
                    <tr key={instrument.instrument_id}>
                      <td>{instrument.instrument_id}</td>
                      <td>{instrument.timeframe}</td>
                      <td>{instrument.sync_status}</td>
                      <td>{instrument.candle_count}</td>
                      <td>{instrument.backfill_target_candles ?? "n/a"}</td>
                      <td>
                        <BackfillCountStatus instrument={instrument} />
                      </td>
                      <td>
                        <BackfillQualityStatus
                          expanded={Boolean(expandedGapRows[instrumentGapRowKey(instrument)])}
                          instrument={instrument}
                          onToggle={() => {
                            const key = instrumentGapRowKey(instrument);
                            setExpandedGapRows((current) => toggleExpandedGapRow(current, key));
                          }}
                        />
                      </td>
                      <td>{instrument.lag_seconds ?? "n/a"}</td>
                      <td>{instrument.last_timestamp ?? "n/a"}</td>
                      <td>
                        <SyncCheckpointStatus instrument={instrument} />
                      </td>
                      <td>
                        <SyncFailureStatus instrument={instrument} />
                      </td>
                      <td>{instrument.issues.length ? instrument.issues.join(", ") : "ok"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No data status loaded.</p>
          )}
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Operator trust</p>
          <h2>Runtime alerts and audit</h2>
          {operatorVisibility ? (
            <div className="status-grid">
              {operatorSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Active alerts</span>
                    <strong>{operatorSummary.alertCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Critical</span>
                    <strong>{operatorSummary.criticalCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Warnings</span>
                    <strong>{operatorSummary.warningCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest audit</span>
                    <strong>{formatTimestamp(operatorSummary.latestAuditAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Alert history</span>
                    <strong>{operatorSummary.historyCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Incidents</span>
                    <strong>{operatorSummary.incidentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Deliveries</span>
                    <strong>{operatorSummary.deliveryCount}</strong>
                  </div>
                </>
              ) : null}
              <div className="status-grid-two-column">
                <div>
                  <h3>Active alerts</h3>
                  {operatorVisibility.alerts.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Category</th>
                          <th>Summary</th>
                          <th>Detected</th>
                          <th>Run</th>
                        </tr>
                      </thead>
                      <tbody>
                        {operatorVisibility.alerts.map((alert) => (
                          <tr key={alert.alert_id}>
                            <td>{alert.severity}</td>
                            <td>{alert.category}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                            <td>{alert.run_id ?? "n/a"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No active runtime alerts.</p>
                  )}
                </div>
                <div>
                  <h3>Recent audit</h3>
                  {operatorVisibility.audit_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Actor</th>
                          <th>Kind</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {operatorVisibility.audit_events.slice(0, 8).map((event) => (
                          <tr key={event.event_id}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.actor}</td>
                            <td>{event.kind}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No runtime audit events recorded.</p>
                  )}
                </div>
              </div>
              <div>
                <h3>Incident events</h3>
                {operatorVisibility.incident_events.length ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>When</th>
                        <th>Kind</th>
                        <th>Severity</th>
                        <th>Summary</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorVisibility.incident_events.slice(0, 8).map((event) => (
                        <tr key={`incident-${event.event_id}`}>
                          <td>{formatTimestamp(event.timestamp)}</td>
                          <td>{event.kind}</td>
                          <td>{event.severity}</td>
                          <td>
                            <strong>{event.summary}</strong>
                            <p className="run-lineage-symbol-copy">{event.detail}</p>
                            <p className="run-lineage-symbol-copy">
                              Delivery: {event.delivery_state}
                              {event.delivery_targets.length ? ` via ${event.delivery_targets.join(", ")}` : ""}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Ack: {event.acknowledgment_state}
                              {event.acknowledged_by ? ` by ${event.acknowledged_by}` : ""}
                              {event.acknowledged_at ? ` at ${formatTimestamp(event.acknowledged_at)}` : ""}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Escalation: level {event.escalation_level} / {event.escalation_state}
                              {event.last_escalated_by ? ` by ${event.last_escalated_by}` : ""}
                              {event.last_escalated_at ? ` at ${formatTimestamp(event.last_escalated_at)}` : ""}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              External: {event.external_status}
                              {event.external_provider ? ` via ${event.external_provider}` : ""}
                              {event.external_reference ? ` (${event.external_reference})` : ""}
                              {event.external_last_synced_at
                                ? ` at ${formatTimestamp(event.external_last_synced_at)}`
                                : ""}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Paging: {event.paging_status}
                              {event.paging_policy_id ? ` via ${event.paging_policy_id}` : ""}
                              {event.paging_provider ? ` (${event.paging_provider})` : ""}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Provider workflow: {event.provider_workflow_state}
                              {event.provider_workflow_action ? ` / ${event.provider_workflow_action}` : ""}
                              {event.provider_workflow_reference ? ` (${event.provider_workflow_reference})` : ""}
                              {event.provider_workflow_last_attempted_at
                                ? ` at ${formatTimestamp(event.provider_workflow_last_attempted_at)}`
                                : ""}
                            </p>
                            {event.remediation.state !== "not_applicable" ? (
                              <>
                                <p className="run-lineage-symbol-copy">
                                  Remediation: {event.remediation.state}
                                  {event.remediation.summary ? ` / ${event.remediation.summary}` : ""}
                                  {event.remediation.runbook ? ` (${event.remediation.runbook})` : ""}
                                  {event.remediation.requested_by ? ` by ${event.remediation.requested_by}` : ""}
                                  {event.remediation.last_attempted_at
                                    ? ` at ${formatTimestamp(event.remediation.last_attempted_at)}`
                                    : ""}
                                </p>
                                {Object.keys(event.remediation.provider_payload).length ? (
                                  <p className="run-lineage-symbol-copy">
                                    Provider recovery payload: {formatParameterMap(event.remediation.provider_payload)}
                                    {event.remediation.provider_payload_updated_at
                                      ? ` at ${formatTimestamp(event.remediation.provider_payload_updated_at)}`
                                      : ""}
                                  </p>
                                ) : null}
                                {event.remediation.provider_recovery.lifecycle_state !== "not_synced" ? (
                                  <>
                                    <p className="run-lineage-symbol-copy">
                                      Provider recovery: {event.remediation.provider_recovery.lifecycle_state}
                                      {event.remediation.provider_recovery.job_id
                                        ? ` / job ${event.remediation.provider_recovery.job_id}`
                                        : ""}
                                      {event.remediation.provider_recovery.channels.length
                                        ? ` / channels ${event.remediation.provider_recovery.channels.join(", ")}`
                                        : ""}
                                      {event.remediation.provider_recovery.symbols.length
                                        ? ` / symbols ${event.remediation.provider_recovery.symbols.join(", ")}`
                                        : ""}
                                      {event.remediation.provider_recovery.timeframe
                                        ? ` / ${event.remediation.provider_recovery.timeframe}`
                                        : ""}
                                      {event.remediation.provider_recovery.verification.state !== "unknown"
                                        ? ` / verification ${event.remediation.provider_recovery.verification.state}`
                                        : ""}
                                      {event.remediation.provider_recovery.updated_at
                                        ? ` at ${formatTimestamp(event.remediation.provider_recovery.updated_at)}`
                                        : ""}
                                    </p>
                                    <p className="run-lineage-symbol-copy">
                                      Recovery machine: {event.remediation.provider_recovery.status_machine.state}
                                      {` / workflow ${event.remediation.provider_recovery.status_machine.workflow_state}`}
                                      {event.remediation.provider_recovery.status_machine.workflow_action
                                        ? ` (${event.remediation.provider_recovery.status_machine.workflow_action})`
                                        : ""}
                                      {` / job ${event.remediation.provider_recovery.status_machine.job_state}`}
                                      {` / sync ${event.remediation.provider_recovery.status_machine.sync_state}`}
                                      {event.remediation.provider_recovery.status_machine.attempt_number
                                        ? ` / attempt ${event.remediation.provider_recovery.status_machine.attempt_number}`
                                        : ""}
                                      {event.remediation.provider_recovery.status_machine.last_event_kind
                                        ? ` / event ${event.remediation.provider_recovery.status_machine.last_event_kind}`
                                        : ""}
                                      {event.remediation.provider_recovery.status_machine.last_event_at
                                        ? ` at ${formatTimestamp(event.remediation.provider_recovery.status_machine.last_event_at)}`
                                        : ""}
                                    </p>
                                    {formatProviderRecoveryTelemetry(event.remediation.provider_recovery) ? (
                                      <p className="run-lineage-symbol-copy">
                                        {formatProviderRecoveryTelemetry(event.remediation.provider_recovery)}
                                      </p>
                                    ) : null}
                                    {formatProviderRecoverySchema(event.remediation.provider_recovery) ? (
                                      <p className="run-lineage-symbol-copy">
                                        {formatProviderRecoverySchema(event.remediation.provider_recovery)}
                                      </p>
                                    ) : null}
                                  </>
                                ) : null}
                              </>
                            ) : null}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="empty-state">No persisted incident events recorded.</p>
                )}
              </div>
              <div>
                <h3>Alert history</h3>
                {operatorVisibility.alert_history.length ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Severity</th>
                        <th>Summary</th>
                        <th>Detected</th>
                        <th>Resolved</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorVisibility.alert_history.slice(0, 8).map((alert) => (
                        <tr key={`history-${alert.alert_id}`}>
                          <td>{alert.status}</td>
                          <td>{alert.severity}</td>
                          <td>
                            <strong>{alert.summary}</strong>
                            <p className="run-lineage-symbol-copy">{alert.detail}</p>
                            <p className="run-lineage-symbol-copy">
                              Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                            </p>
                          </td>
                          <td>{formatTimestamp(alert.detected_at)}</td>
                          <td>{formatTimestamp(alert.resolved_at ?? null)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="empty-state">No persisted live-path alert history recorded.</p>
                )}
              </div>
              <div>
                <h3>Delivery history</h3>
                {operatorVisibility.delivery_history.length ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>When</th>
                        <th>Target</th>
                        <th>Status</th>
                        <th>Attempt</th>
                        <th>Next retry</th>
                        <th>Detail</th>
                      </tr>
                    </thead>
                    <tbody>
                        {operatorVisibility.delivery_history.slice(0, 8).map((record) => (
                          <tr key={`delivery-${record.delivery_id}`}>
                            <td>{formatTimestamp(record.attempted_at)}</td>
                            <td>{record.target}</td>
                            <td>{record.status}</td>
                            <td>{record.attempt_number}</td>
                            <td>{formatTimestamp(record.next_retry_at ?? null)}</td>
                            <td>
                              <strong>{record.incident_kind}</strong>
                              <p className="run-lineage-symbol-copy">Phase: {record.phase}</p>
                              {record.provider_action ? (
                                <p className="run-lineage-symbol-copy">
                                  Provider action: {record.provider_action}
                                </p>
                              ) : null}
                              <p className="run-lineage-symbol-copy">
                                External: {record.external_provider ?? "n/a"}
                                {record.external_reference ? ` (${record.external_reference})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">{record.detail}</p>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="empty-state">No outbound delivery attempts recorded.</p>
                )}
              </div>
            </div>
          ) : (
            <p>No operator visibility loaded.</p>
          )}
        </section>

        <section className="panel panel-wide">
          <p className="kicker">Guarded live</p>
          <h2>Kill switch and reconciliation</h2>
          {guardedLive ? (
            <div className="status-grid">
              {guardedLiveSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Candidacy</span>
                    <strong>{guardedLive.candidacy_status}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Kill switch</span>
                    <strong>{guardedLive.kill_switch.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Runtime alerts</span>
                    <strong>{guardedLive.active_runtime_alert_count}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Venue verification</span>
                    <strong>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last reconciliation</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestReconciliationAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last recovery</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestRecoveryAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Blockers</span>
                    <strong>{guardedLiveSummary.blockerCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Live owner</span>
                    <strong>{guardedLive.ownership.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Order-book sync</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestOrderSyncAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session restore</span>
                    <strong>{guardedLive.session_restore.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session handoff</span>
                    <strong>{guardedLive.session_handoff.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest audit</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestAuditAt)}</strong>
                  </div>
                </>
              ) : null}
              <div className="control-action-row">
                <label className="control-action-field">
                  <span>Operator reason</span>
                  <input
                    onChange={(event) => setGuardedLiveReason(event.target.value)}
                    placeholder="operator_safety_drill"
                    type="text"
                    value={guardedLiveReason}
                  />
                </label>
                <button className="ghost-button" onClick={() => void runGuardedLiveReconciliation()} type="button">
                  Run reconciliation
                </button>
                <button className="ghost-button" onClick={() => void recoverGuardedLiveRuntime()} type="button">
                  Recover runtime state
                </button>
                <button className="ghost-button" onClick={() => void resumeGuardedLiveRun()} type="button">
                  Resume live owner
                </button>
                <button className="ghost-button" onClick={() => void engageGuardedLiveKillSwitch()} type="button">
                  Engage kill switch
                </button>
                <button className="ghost-button" onClick={() => void releaseGuardedLiveKillSwitch()} type="button">
                  Release kill switch
                </button>
              </div>
              <div className="status-grid-two-column">
                <div>
                  <h3>Current guardrails</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Kill switch</th>
                        <td>{guardedLive.kill_switch.state}</td>
                      </tr>
                      <tr>
                        <th>Updated by</th>
                        <td>{guardedLive.kill_switch.updated_by}</td>
                      </tr>
                      <tr>
                        <th>Updated at</th>
                        <td>{formatTimestamp(guardedLive.kill_switch.updated_at)}</td>
                      </tr>
                      <tr>
                        <th>Reason</th>
                        <td>{guardedLive.kill_switch.reason}</td>
                      </tr>
                      <tr>
                        <th>Running sandbox</th>
                        <td>{guardedLive.running_sandbox_count}</td>
                      </tr>
                      <tr>
                        <th>Running paper</th>
                        <td>{guardedLive.running_paper_count}</td>
                      </tr>
                      <tr>
                        <th>Running live</th>
                        <td>{guardedLive.running_live_count}</td>
                      </tr>
                      <tr>
                        <th>Owner state</th>
                        <td>{guardedLive.ownership.state}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.ownership.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.ownership.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner symbol</th>
                        <td>{guardedLive.ownership.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Claimed at</th>
                        <td>{formatTimestamp(guardedLive.ownership.claimed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last resume</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_resumed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order sync</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_order_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Restore state</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Restore source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionRestoreAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Handoff state</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Handoff transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Last handoff sync</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionHandoffAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Reconciliation scope</th>
                        <td>{guardedLive.reconciliation.scope}</td>
                      </tr>
                      <tr>
                        <th>Venue snapshot</th>
                        <td>
                          {guardedLive.reconciliation.venue_snapshot
                            ? `${guardedLive.reconciliation.venue_snapshot.provider} / ${guardedLive.reconciliation.venue_snapshot.venue}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Venue verified</th>
                        <td>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Venue captured</th>
                        <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot?.captured_at ?? null)}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Candidate blockers</h3>
                  {guardedLive.blockers.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Blocker</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.blockers.map((blocker) => (
                          <tr key={blocker}>
                            <td>{blocker}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live blockers recorded.</p>
                  )}
                </div>
                <div>
                  <h3>Reconciliation findings</h3>
                  {guardedLive.reconciliation.findings.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Finding</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.findings.map((finding) => (
                          <tr key={`${finding.kind}-${finding.summary}`}>
                            <td>{finding.severity}</td>
                            <td>{finding.kind}</td>
                            <td>
                              <strong>{finding.summary}</strong>
                              <p className="run-lineage-symbol-copy">{finding.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">{guardedLive.reconciliation.summary}</p>
                  )}
                  <h3>Venue snapshot</h3>
                  {guardedLive.reconciliation.venue_snapshot ? (
                    <table className="data-table">
                      <tbody>
                        <tr>
                          <th>Provider</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.provider}</td>
                        </tr>
                        <tr>
                          <th>Venue</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.venue}</td>
                        </tr>
                        <tr>
                          <th>State</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.verification_state}</td>
                        </tr>
                        <tr>
                          <th>Captured</th>
                          <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot.captured_at ?? null)}</td>
                        </tr>
                        <tr>
                          <th>Issues</th>
                          <td>
                            {guardedLive.reconciliation.venue_snapshot.issues.length
                              ? guardedLive.reconciliation.venue_snapshot.issues.join(", ")
                              : "none"}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue snapshot recorded yet.</p>
                  )}
                  <h3>Internal exposures</h3>
                  {guardedLive.reconciliation.internal_snapshot?.exposures?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Run</th>
                          <th>Mode</th>
                          <th>Instrument</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.internal_snapshot.exposures.map((exposure) => (
                          <tr key={`${exposure.run_id}-${exposure.instrument_id}`}>
                            <td>{exposure.run_id}</td>
                            <td>{exposure.mode}</td>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No internal open exposures recorded.</p>
                  )}
                  <h3>Venue balances</h3>
                  {guardedLive.reconciliation.venue_snapshot?.balances?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Asset</th>
                          <th>Total</th>
                          <th>Free</th>
                          <th>Used</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.balances.map((balance) => (
                          <tr key={balance.asset}>
                            <td>{balance.asset}</td>
                            <td>{balance.total.toFixed(8)}</td>
                            <td>{balance.free === null || balance.free === undefined ? "n/a" : balance.free.toFixed(8)}</td>
                            <td>{balance.used === null || balance.used === undefined ? "n/a" : balance.used.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue balances captured.</p>
                  )}
                  <h3>Venue open orders</h3>
                  {guardedLive.reconciliation.venue_snapshot?.open_orders?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue open orders captured.</p>
                  )}
                  <h3>Recovered runtime</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Recovery state</th>
                        <td>{guardedLive.recovery.state}</td>
                      </tr>
                      <tr>
                        <th>Recovered at</th>
                        <td>{formatTimestamp(guardedLive.recovery.recovered_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Recovered by</th>
                        <td>{guardedLive.recovery.recovered_by ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Source snapshot</th>
                        <td>{formatTimestamp(guardedLive.recovery.source_snapshot_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Source state</th>
                        <td>{guardedLive.recovery.source_verification_state}</td>
                      </tr>
                      <tr>
                        <th>Summary</th>
                        <td>{guardedLive.recovery.summary}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.recovery.issues.length ? guardedLive.recovery.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered exposures</h3>
                  {guardedLive.recovery.exposures.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Instrument</th>
                          <th>Asset</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.exposures.map((exposure) => (
                          <tr key={`${exposure.instrument_id}-${exposure.asset}`}>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.asset}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue exposures recorded.</p>
                  )}
                  <h3>Recovered open orders</h3>
                  {guardedLive.recovery.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue orders recorded.</p>
                  )}
                  <h3>Venue-native session restore</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLive.session_restore.restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue</th>
                        <td>{guardedLive.session_restore.venue ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.session_restore.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_restore.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_restore.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_restore.issues.length ? guardedLive.session_restore.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.session_restore.synced_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Status</th>
                          <th>Filled</th>
                          <th>Remaining</th>
                          <th>Updated</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.session_restore.synced_orders.map((order) => (
                          <tr key={`restored-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.status}</td>
                            <td>{(order.filled_amount ?? 0).toFixed(8)}</td>
                            <td>{(order.remaining_amount ?? 0).toFixed(8)}</td>
                            <td>{formatTimestamp(order.updated_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue-native session lifecycle rows restored yet.</p>
                  )}
                  <h3>Venue-native session stream</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_handoff.source}</td>
                      </tr>
                      <tr>
                        <th>Transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Stream started at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.handed_off_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Released at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.released_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last stream sync</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Supervision</th>
                        <td>{guardedLive.session_handoff.supervision_state}</td>
                      </tr>
                      <tr>
                        <th>Failovers</th>
                        <td>{guardedLive.session_handoff.failover_count}</td>
                      </tr>
                      <tr>
                        <th>Last failover</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_failover_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Coverage</th>
                        <td>{guardedLive.session_handoff.coverage.length ? guardedLive.session_handoff.coverage.join(", ") : "none"}</td>
                      </tr>
                      <tr>
                        <th>Order book state</th>
                        <td>{guardedLive.session_handoff.order_book_state}</td>
                      </tr>
                      <tr>
                        <th>Last depth update ID</th>
                        <td>{guardedLive.session_handoff.order_book_last_update_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Depth gap count</th>
                        <td>{guardedLive.session_handoff.order_book_gap_count}</td>
                      </tr>
                      <tr>
                        <th>Rebuild count</th>
                        <td>{guardedLive.session_handoff.order_book_rebuild_count}</td>
                      </tr>
                      <tr>
                        <th>Last rebuilt at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.order_book_last_rebuilt_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Bid levels</th>
                        <td>{guardedLive.session_handoff.order_book_bid_level_count}</td>
                      </tr>
                      <tr>
                        <th>Ask levels</th>
                        <td>{guardedLive.session_handoff.order_book_ask_level_count}</td>
                      </tr>
                      <tr>
                        <th>Channel restore</th>
                        <td>{guardedLive.session_handoff.channel_restore_state}</td>
                      </tr>
                      <tr>
                        <th>Channel restore count</th>
                        <td>{guardedLive.session_handoff.channel_restore_count}</td>
                      </tr>
                      <tr>
                        <th>Last channel restore</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Channel continuation</th>
                        <td>{guardedLive.session_handoff.channel_continuation_state}</td>
                      </tr>
                      <tr>
                        <th>Continuation count</th>
                        <td>{guardedLive.session_handoff.channel_continuation_count}</td>
                      </tr>
                      <tr>
                        <th>Last continued at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_continued_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Best bid</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_bid_price != null
                            ? `${guardedLive.session_handoff.order_book_best_bid_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_bid_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Best ask</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_ask_price != null
                            ? `${guardedLive.session_handoff.order_book_best_ask_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_ask_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Last market event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_market_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last aggregate trade</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_aggregate_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last mini ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_mini_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last depth update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_depth_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last kline update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_kline_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last account event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_account_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last balance event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_balance_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order-list event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_order_list_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last trade tick</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last book ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_book_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue session</th>
                        <td>{guardedLive.session_handoff.venue_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Cursor</th>
                        <td>{guardedLive.session_handoff.cursor ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Active orders</th>
                        <td>{guardedLive.session_handoff.active_order_count}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_handoff.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_handoff.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_handoff.issues.length ? guardedLive.session_handoff.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered venue order book</h3>
                  {guardedLive.session_handoff.order_book_bids.length
                    || guardedLive.session_handoff.order_book_asks.length ? (
                      <div className="status-grid-two-column">
                        <section>
                          <h4>Recovered bids</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_bids.slice(0, 5).map((level) => (
                                <tr key={`handoff-bid-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                        <section>
                          <h4>Recovered asks</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_asks.slice(0, 5).map((level) => (
                                <tr key={`handoff-ask-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                      </div>
                    ) : (
                      <p className="empty-state">No recovered venue order-book levels recorded.</p>
                    )}
                  <h3>Recovered market channels</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Trade tick</th>
                        <td>
                          {guardedLive.session_handoff.trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Aggregate trade</th>
                        <td>
                          {guardedLive.session_handoff.aggregate_trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Book ticker</th>
                        <td>
                          {guardedLive.session_handoff.book_ticker_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_quantity)} / ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `open ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.open_price)}, close ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.close_price)}, high ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.high_price)}, low ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.low_price)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker volume</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `base ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.base_volume)}, quote ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.quote_volume)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Kline snapshot</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${guardedLive.session_handoff.kline_snapshot.timeframe ?? "n/a"} | o ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.open_price)}, h ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.high_price)}, l ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.low_price)}, c ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.close_price)}, v ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.volume)}, closed ${guardedLive.session_handoff.kline_snapshot.closed ? "yes" : "no"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Trade snapshot time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Aggregate trade time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.aggregate_trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Book ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.book_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Mini ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.mini_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Kline open / close</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${formatTimestamp(guardedLive.session_handoff.kline_snapshot.open_at ?? null)} -> ${formatTimestamp(guardedLive.session_handoff.kline_snapshot.close_at ?? null)}`
                            : "n/a"}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Durable order book</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Sync state</th>
                        <td>{guardedLive.order_book.state}</td>
                      </tr>
                      <tr>
                        <th>Synced at</th>
                        <td>{formatTimestamp(guardedLive.order_book.synced_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.order_book.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.order_book.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.order_book.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.order_book.issues.length ? guardedLive.order_book.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.order_book.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.order_book.open_orders.map((order) => (
                          <tr key={`durable-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No durable guarded-live open orders recorded.</p>
                  )}
                  <h3>Guarded-live alerts</h3>
                  {guardedLive.active_alerts.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Category</th>
                          <th>Summary</th>
                          <th>Detected</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.active_alerts.map((alert) => (
                          <tr key={`guarded-live-alert-${alert.alert_id}`}>
                            <td>{alert.severity}</td>
                            <td>{alert.category}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No active guarded-live alerts.</p>
                  )}
                  <h3>Guarded-live alert history</h3>
                  {guardedLive.alert_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Status</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Detected</th>
                          <th>Resolved</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.alert_history.slice(0, 8).map((alert) => (
                          <tr key={`guarded-live-alert-history-${alert.alert_id}`}>
                            <td>{alert.status}</td>
                            <td>{alert.severity}</td>
                            <td>
                              <strong>{alert.summary}</strong>
                              <p className="run-lineage-symbol-copy">{alert.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                              </p>
                            </td>
                            <td>{formatTimestamp(alert.detected_at)}</td>
                            <td>{formatTimestamp(alert.resolved_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live alert history recorded.</p>
                  )}
                  <h3>Guarded-live incidents</h3>
                  {guardedLive.incident_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Kind</th>
                          <th>Severity</th>
                          <th>Summary</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.incident_events.slice(0, 8).map((event) => (
                          <tr key={`guarded-live-incident-${event.event_id}`}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.kind}</td>
                            <td>{event.severity}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                              <p className="run-lineage-symbol-copy">
                                Delivery: {event.delivery_state}
                                {event.delivery_targets.length ? ` via ${event.delivery_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Ack: {event.acknowledgment_state}
                                {event.acknowledged_by ? ` by ${event.acknowledged_by}` : ""}
                                {event.acknowledged_at ? ` at ${formatTimestamp(event.acknowledged_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Escalation: level {event.escalation_level} / {event.escalation_state}
                                {event.last_escalated_by ? ` by ${event.last_escalated_by}` : ""}
                                {event.last_escalated_at ? ` at ${formatTimestamp(event.last_escalated_at)}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Next escalation: {formatTimestamp(event.next_escalation_at ?? null)}
                                {event.escalation_targets.length ? ` via ${event.escalation_targets.join(", ")}` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                External: {event.external_status}
                                {event.external_provider ? ` via ${event.external_provider}` : ""}
                                {event.external_reference ? ` (${event.external_reference})` : ""}
                                {event.external_last_synced_at
                                  ? ` at ${formatTimestamp(event.external_last_synced_at)}`
                                  : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Paging: {event.paging_status}
                                {event.paging_policy_id ? ` via ${event.paging_policy_id}` : ""}
                                {event.paging_provider ? ` (${event.paging_provider})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">
                                Provider workflow: {event.provider_workflow_state}
                                {event.provider_workflow_action ? ` / ${event.provider_workflow_action}` : ""}
                                {event.provider_workflow_reference
                                  ? ` (${event.provider_workflow_reference})`
                                  : ""}
                                {event.provider_workflow_last_attempted_at
                                  ? ` at ${formatTimestamp(event.provider_workflow_last_attempted_at)}`
                                  : ""}
                              </p>
                              {event.remediation.state !== "not_applicable" ? (
                                <>
                                  <p className="run-lineage-symbol-copy">
                                    Remediation: {event.remediation.state}
                                    {event.remediation.summary ? ` / ${event.remediation.summary}` : ""}
                                    {event.remediation.runbook ? ` (${event.remediation.runbook})` : ""}
                                    {event.remediation.requested_by
                                      ? ` by ${event.remediation.requested_by}`
                                      : ""}
                                    {event.remediation.last_attempted_at
                                      ? ` at ${formatTimestamp(event.remediation.last_attempted_at)}`
                                      : ""}
                                  </p>
                                  {event.remediation.detail ? (
                                    <p className="run-lineage-symbol-copy">
                                      Remediation detail: {event.remediation.detail}
                                    </p>
                                  ) : null}
                                  {Object.keys(event.remediation.provider_payload).length ? (
                                    <p className="run-lineage-symbol-copy">
                                      Provider recovery payload: {formatParameterMap(event.remediation.provider_payload)}
                                      {event.remediation.provider_payload_updated_at
                                        ? ` at ${formatTimestamp(event.remediation.provider_payload_updated_at)}`
                                        : ""}
                                    </p>
                                  ) : null}
                                  {event.remediation.provider_recovery.lifecycle_state !== "not_synced" ? (
                                    <>
                                      <p className="run-lineage-symbol-copy">
                                        Provider recovery: {event.remediation.provider_recovery.lifecycle_state}
                                        {event.remediation.provider_recovery.job_id
                                          ? ` / job ${event.remediation.provider_recovery.job_id}`
                                          : ""}
                                        {event.remediation.provider_recovery.channels.length
                                          ? ` / channels ${event.remediation.provider_recovery.channels.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.symbols.length
                                          ? ` / symbols ${event.remediation.provider_recovery.symbols.join(", ")}`
                                          : ""}
                                        {event.remediation.provider_recovery.timeframe
                                          ? ` / ${event.remediation.provider_recovery.timeframe}`
                                          : ""}
                                        {event.remediation.provider_recovery.verification.state !== "unknown"
                                          ? ` / verification ${event.remediation.provider_recovery.verification.state}`
                                          : ""}
                                        {event.remediation.provider_recovery.updated_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.updated_at)}`
                                          : ""}
                                      </p>
                                      <p className="run-lineage-symbol-copy">
                                        Recovery machine: {event.remediation.provider_recovery.status_machine.state}
                                        {` / workflow ${event.remediation.provider_recovery.status_machine.workflow_state}`}
                                        {event.remediation.provider_recovery.status_machine.workflow_action
                                          ? ` (${event.remediation.provider_recovery.status_machine.workflow_action})`
                                          : ""}
                                        {` / job ${event.remediation.provider_recovery.status_machine.job_state}`}
                                        {` / sync ${event.remediation.provider_recovery.status_machine.sync_state}`}
                                        {event.remediation.provider_recovery.status_machine.attempt_number
                                          ? ` / attempt ${event.remediation.provider_recovery.status_machine.attempt_number}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_kind
                                          ? ` / event ${event.remediation.provider_recovery.status_machine.last_event_kind}`
                                          : ""}
                                        {event.remediation.provider_recovery.status_machine.last_event_at
                                          ? ` at ${formatTimestamp(event.remediation.provider_recovery.status_machine.last_event_at)}`
                                          : ""}
                                      </p>
                                      {formatProviderRecoveryTelemetry(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoveryTelemetry(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                      {formatProviderRecoverySchema(event.remediation.provider_recovery) ? (
                                        <p className="run-lineage-symbol-copy">
                                          {formatProviderRecoverySchema(event.remediation.provider_recovery)}
                                        </p>
                                      ) : null}
                                    </>
                                  ) : null}
                                </>
                              ) : null}
                              {event.acknowledgment_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Ack reason: {event.acknowledgment_reason}
                                </p>
                              ) : null}
                              {event.escalation_reason ? (
                                <p className="run-lineage-symbol-copy">
                                  Escalation reason: {event.escalation_reason}
                                </p>
                              ) : null}
                            </td>
                            <td>
                              {event.kind === "incident_opened" && activeGuardedLiveAlertIds.has(event.alert_id) ? (
                                <>
                                  {event.remediation.state !== "not_applicable" ? (
                                    <button
                                      className="ghost-button"
                                      onClick={() => void remediateGuardedLiveIncident(event.event_id)}
                                      type="button"
                                    >
                                      Request remediation
                                    </button>
                                  ) : null}
                                  <button
                                    className="ghost-button"
                                    disabled={event.acknowledgment_state === "acknowledged"}
                                    onClick={() => void acknowledgeGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Acknowledge
                                  </button>
                                  <button
                                    className="ghost-button"
                                    onClick={() => void escalateGuardedLiveIncident(event.event_id)}
                                    type="button"
                                  >
                                    Escalate
                                  </button>
                                </>
                              ) : (
                                <span className="run-lineage-symbol-copy">No action</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live incident events recorded.</p>
                  )}
                  <h3>Guarded-live delivery history</h3>
                  {guardedLive.delivery_history.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Target</th>
                          <th>Status</th>
                          <th>Attempt</th>
                          <th>Next retry</th>
                          <th>Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.delivery_history.slice(0, 8).map((record) => (
                          <tr key={`guarded-live-delivery-${record.delivery_id}`}>
                            <td>{formatTimestamp(record.attempted_at)}</td>
                            <td>{record.target}</td>
                            <td>{record.status}</td>
                            <td>{record.attempt_number}</td>
                            <td>{formatTimestamp(record.next_retry_at ?? null)}</td>
                            <td>
                              <strong>{record.incident_kind}</strong>
                              <p className="run-lineage-symbol-copy">Phase: {record.phase}</p>
                              {record.provider_action ? (
                                <p className="run-lineage-symbol-copy">
                                  Provider action: {record.provider_action}
                                </p>
                              ) : null}
                              <p className="run-lineage-symbol-copy">
                                External: {record.external_provider ?? "n/a"}
                                {record.external_reference ? ` (${record.external_reference})` : ""}
                              </p>
                              <p className="run-lineage-symbol-copy">{record.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live outbound delivery attempts recorded.</p>
                  )}
                  <h3>Guarded-live audit</h3>
                  {guardedLive.audit_events.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>When</th>
                          <th>Actor</th>
                          <th>Kind</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.audit_events.slice(0, 8).map((event) => (
                          <tr key={event.event_id}>
                            <td>{formatTimestamp(event.timestamp)}</td>
                            <td>{event.actor}</td>
                            <td>{event.kind}</td>
                            <td>
                              <strong>{event.summary}</strong>
                              <p className="run-lineage-symbol-copy">{event.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live audit events recorded.</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <p>No guarded-live status loaded.</p>
          )}
        </section>

        <RunSection
          title="Recent backtests"
          runs={backtests}
          presets={presets}
          strategies={strategies}
          filter={backtestRunFilter}
          setFilter={setBacktestRunFilter}
          comparison={{
            selectedRunIds: selectedComparisonRunIds,
            comparisonIntent,
            historyStep: comparisonHistoryStep,
            historyEntries: comparisonHistoryPanel.entries,
            activeHistoryEntryId: comparisonHistoryPanel.activeEntryId,
            historyBrowserOpen: comparisonHistoryPanelOpen,
            canNavigateHistoryBackward: comparisonHistoryActiveIndex > 0,
            canNavigateHistoryForward:
              comparisonHistoryActiveIndex >= 0
              && comparisonHistoryActiveIndex < comparisonHistoryPanel.entries.length - 1,
            selectedScoreLink: selectedComparisonScoreLink,
            payload: runComparison,
            loading: runComparisonLoading,
            error: runComparisonError,
            onChangeComparisonIntent: handleComparisonIntentChange,
            onChangeSelectedScoreLink: handleSelectedComparisonScoreLinkChange,
            onToggleHistoryBrowser: () => setComparisonHistoryPanelOpen((current) => !current),
            onNavigateHistoryEntry: handleNavigateComparisonHistoryEntry,
            onNavigateHistoryRelative: handleNavigateComparisonHistoryRelative,
            onToggleRunSelection: toggleComparisonRun,
            onClearSelection: clearComparisonRuns,
            onSelectBenchmarkPair: selectBenchmarkPair,
          }}
          rerunActions={[
            {
              label: "Rerun backtest",
              onRerun: rerunBacktest,
            },
            {
              label: "Start sandbox worker",
              onRerun: rerunSandbox,
            },
            {
              label: "Start paper session",
              onRerun: rerunPaper,
            },
          ]}
        />
        <RunSection
          title="Sandbox runs"
          runs={sandboxRuns}
          presets={presets}
          strategies={strategies}
          filter={sandboxRunFilter}
          setFilter={setSandboxRunFilter}
          rerunActions={[
            {
              label: "Restore sandbox worker",
              onRerun: rerunSandbox,
            },
            {
              label: "Start paper session",
              onRerun: rerunPaper,
            },
          ]}
          onStop={stopSandboxRun}
        />
        <RunSection
          title="Paper runs"
          runs={paperRuns}
          presets={presets}
          strategies={strategies}
          filter={paperRunFilter}
          setFilter={setPaperRunFilter}
          rerunActions={[
            {
              label: "Start sandbox worker",
              onRerun: rerunSandbox,
            },
            {
              label: "Start paper session",
              onRerun: rerunPaper,
            },
          ]}
          onStop={stopPaperRun}
        />
        <RunSection
          title="Guarded live runs"
          runs={liveRuns}
          presets={presets}
          strategies={strategies}
          filter={liveRunFilter}
          setFilter={setLiveRunFilter}
          onStop={stopLiveRun}
          getOrderControls={(run) => ({
            getReplacementDraft: (_orderId, order) => getLiveOrderReplacementDraft(run.config.run_id, order),
            onChangeReplacementDraft: (orderId, draft) =>
              setLiveOrderReplacementDraft(run.config.run_id, orderId, draft),
            onCancelOrder: (orderId) => cancelLiveOrder(run.config.run_id, orderId),
            onReplaceOrder: (orderId, draft) => replaceLiveOrder(run.config.run_id, orderId, draft),
          })}
        />
      </main>
    </div>
  );
}

function BackfillCountStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.backfill_target_candles === null) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_completion_ratio)}</strong>
      <span>
        {Math.min(instrument.candle_count, instrument.backfill_target_candles)} /{" "}
        {instrument.backfill_target_candles}
        {instrument.backfill_complete ? " ready" : ""}
      </span>
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function BackfillQualityStatus({
  expanded,
  instrument,
  onToggle,
}: {
  expanded: boolean;
  instrument: MarketDataStatus["instruments"][number];
  onToggle: () => void;
}) {
  if (instrument.backfill_contiguous_completion_ratio === null) {
    return <span>n/a</span>;
  }
  const canToggleGapWindows = instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS;
  const gapLines = expanded
    ? formatGapWindows(instrument.backfill_gap_windows)
    : summarizeGapWindows(instrument.backfill_gap_windows);
  return (
    <div className="progress-stack">
      <strong>{formatCompletion(instrument.backfill_contiguous_completion_ratio)}</strong>
      <span>
        {instrument.backfill_contiguous_complete
          ? "gap-free"
          : `gaps: ${instrument.backfill_contiguous_missing_candles ?? 0}`}
      </span>
      {gapLines.length ? (
        <div className="progress-detail-list">
          {gapLines.map((line) => (
            <span
              className={line.kind === "summary" ? "progress-detail-summary" : undefined}
              key={line.key}
            >
              {line.label}
            </span>
          ))}
        </div>
      ) : null}
      {canToggleGapWindows ? (
        <button
          className="progress-toggle"
          onClick={onToggle}
          type="button"
        >
          {expanded
            ? "Collapse gaps"
            : `Show all ${instrument.backfill_gap_windows.length} gaps`}
        </button>
      ) : null}
      <div className="progress-track" aria-hidden="true">
        <span
          style={{
            width: `${Math.round((instrument.backfill_contiguous_completion_ratio ?? 0) * 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function SyncCheckpointStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  const checkpoint = instrument.sync_checkpoint;
  if (!checkpoint) {
    return <span>n/a</span>;
  }
  return (
    <div className="progress-stack">
      <strong title={checkpoint.checkpoint_id}>{shortenIdentifier(checkpoint.checkpoint_id)}</strong>
      <span>
        {checkpoint.candle_count} candles
        {checkpoint.contiguous_missing_candles > 0
          ? ` / gaps ${checkpoint.contiguous_missing_candles}`
          : " / gap-free"}
      </span>
      <span>{formatTimestamp(checkpoint.recorded_at)}</span>
    </div>
  );
}

function SyncFailureStatus({
  instrument,
}: {
  instrument: MarketDataStatus["instruments"][number];
}) {
  if (instrument.failure_count_24h === 0 && instrument.recent_failures.length === 0) {
    return <span>clear</span>;
  }
  const latestFailure = instrument.recent_failures[0];
  return (
    <div className="progress-stack">
      <strong>{instrument.failure_count_24h} in 24h</strong>
      <span>
        {latestFailure
          ? `${latestFailure.operation} @ ${formatTimestamp(latestFailure.failed_at)}`
          : "history unavailable"}
      </span>
      {latestFailure ? (
        <span title={latestFailure.error}>{truncateLabel(latestFailure.error, 56)}</span>
      ) : null}
    </div>
  );
}

function formatCompletion(value: number | null) {
  if (value === null) {
    return "n/a";
  }
  return `${Math.round(value * 100)}%`;
}

function summarizeGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  if (gapWindows.length <= MAX_VISIBLE_GAP_WINDOWS) {
    return formatGapWindows(gapWindows);
  }

  const recentWindows = gapWindows.slice(-(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedWindows = gapWindows.slice(0, -(MAX_VISIBLE_GAP_WINDOWS - 1));
  const collapsedMissing = collapsedWindows.reduce(
    (total, gap) => total + gap.missing_candles,
    0,
  );
  const lastCollapsedWindow = collapsedWindows[collapsedWindows.length - 1];

  return [
    {
      key: `summary-${collapsedWindows[0].start_at}-${lastCollapsedWindow.end_at}`,
      kind: "summary" as const,
      label:
        `${collapsedWindows.length} older windows | ` +
        `${formatRange(collapsedWindows[0].start_at, lastCollapsedWindow.end_at)} | ` +
        `${collapsedMissing} missing`,
    },
    ...formatGapWindows(recentWindows),
  ];
}

function formatGapWindows(
  gapWindows: MarketDataStatus["instruments"][number]["backfill_gap_windows"],
) {
  return gapWindows.map((gap, index) => ({
    key: `${gap.start_at}-${gap.end_at}-${index}`,
    kind: "exact" as const,
    label: `${formatRange(gap.start_at, gap.end_at)} (${gap.missing_candles})`,
  }));
}

function instrumentGapRowKey(instrument: MarketDataStatus["instruments"][number]) {
  return `${instrument.instrument_id}:${instrument.timeframe}`;
}

function toggleExpandedGapRow(current: Record<string, boolean>, key: string) {
  if (current[key]) {
    const next = { ...current };
    delete next[key];
    return next;
  }
  return { ...current, [key]: true };
}

function pruneExpandedGapRows(
  current: Record<string, boolean>,
  marketStatus: MarketDataStatus,
) {
  const activeKeys = new Set(
    marketStatus.instruments
      .filter((instrument) => instrument.backfill_gap_windows.length > MAX_VISIBLE_GAP_WINDOWS)
      .map((instrument) => instrumentGapRowKey(instrument)),
  );
  const next = Object.fromEntries(
    Object.entries(current).filter(([key, expanded]) => expanded && activeKeys.has(key)),
  );
  const currentKeys = Object.keys(current);
  const nextKeys = Object.keys(next);
  if (
    currentKeys.length === nextKeys.length &&
    currentKeys.every((key) => next[key] === current[key])
  ) {
    return current;
  }
  return next;
}

function loadExpandedGapRows() {
  const persistedState = loadControlRoomUiState();
  if (persistedState) {
    return persistedState.expandedGapRows;
  }
  return loadLegacyExpandedGapRows();
}

function defaultControlRoomComparisonSelectionState(): ControlRoomComparisonSelectionState {
  return {
    selectedRunIds: [],
    intent: DEFAULT_COMPARISON_INTENT,
    scoreLink: null,
  };
}

function loadPersistedComparisonSelection(): ControlRoomComparisonSelectionState {
  const urlSelection = loadComparisonSelectionFromUrl();
  if (urlSelection) {
    return urlSelection;
  }
  return loadControlRoomUiState()?.comparisonSelection ?? defaultControlRoomComparisonSelectionState();
}

function loadControlRoomUiState(): ControlRoomUiStateV2 | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(CONTROL_ROOM_UI_STATE_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (isControlRoomUiStateV2(parsed)) {
      return {
        version: parsed.version,
        expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
        comparisonSelection: normalizeControlRoomComparisonSelection(parsed.comparisonSelection),
      };
    }
    if (!isControlRoomUiStateV1(parsed)) {
      return null;
    }
    return {
      version: CONTROL_ROOM_UI_STATE_VERSION,
      expandedGapRows: filterExpandedGapRows(parsed.expandedGapRows),
      comparisonSelection: defaultControlRoomComparisonSelectionState(),
    };
  } catch {
    return null;
  }
}

function persistControlRoomUiState(state: {
  comparisonSelection: ControlRoomComparisonSelectionState;
  expandedGapRows: Record<string, boolean>;
}) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: ControlRoomUiStateV2 = {
      version: CONTROL_ROOM_UI_STATE_VERSION,
      comparisonSelection: normalizeControlRoomComparisonSelection(state.comparisonSelection),
      expandedGapRows: filterExpandedGapRows(state.expandedGapRows),
    };
    window.localStorage.setItem(
      CONTROL_ROOM_UI_STATE_STORAGE_KEY,
      JSON.stringify(nextState),
    );
    window.localStorage.removeItem(LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY);
  } catch {
    return;
  }
}

function loadComparisonSelectionFromUrl(): ControlRoomComparisonSelectionState | null {
  if (typeof window === "undefined") {
    return null;
  }
  const params = new URLSearchParams(window.location.search);
  const hasComparisonParams = [
    COMPARISON_RUN_ID_SEARCH_PARAM,
    COMPARISON_INTENT_SEARCH_PARAM,
    COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM,
    COMPARISON_FOCUS_SECTION_SEARCH_PARAM,
    COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM,
  ].some((key) => params.has(key));
  if (!hasComparisonParams) {
    return null;
  }
  const selectedRunIds = normalizeComparisonRunIdList(params.getAll(COMPARISON_RUN_ID_SEARCH_PARAM));
  const intent = normalizeComparisonIntent(params.get(COMPARISON_INTENT_SEARCH_PARAM));
  const focusRunId = params.get(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM)?.trim() ?? "";
  const focusSection = normalizeComparisonScoreSection(
    params.get(COMPARISON_FOCUS_SECTION_SEARCH_PARAM),
  );
  const focusComponent = params.get(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM)?.trim() ?? "";

  return {
    intent,
    scoreLink:
      focusRunId && focusSection && focusComponent
        ? {
            componentKey: focusComponent,
            narrativeRunId: focusRunId,
            section: focusSection,
          }
        : null,
    selectedRunIds,
  };
}

function buildComparisonSelectionHistoryUrl(
  selection: ControlRoomComparisonSelectionState,
  baseHref?: string,
) {
  const url =
    typeof window !== "undefined"
      ? new URL(baseHref ?? window.location.href)
      : new URL(baseHref ?? "http://localhost/");
  const params = url.searchParams;
  params.delete(COMPARISON_RUN_ID_SEARCH_PARAM);
  params.delete(COMPARISON_INTENT_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_SECTION_SEARCH_PARAM);
  params.delete(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM);

  const normalizedSelection = normalizeControlRoomComparisonSelection(selection);
  normalizedSelection.selectedRunIds.forEach((runId) => params.append(COMPARISON_RUN_ID_SEARCH_PARAM, runId));
  if (normalizedSelection.intent !== DEFAULT_COMPARISON_INTENT || normalizedSelection.selectedRunIds.length) {
    params.set(COMPARISON_INTENT_SEARCH_PARAM, normalizedSelection.intent);
  }
  if (normalizedSelection.scoreLink && normalizedSelection.selectedRunIds.length) {
    params.set(COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM, normalizedSelection.scoreLink.narrativeRunId);
    params.set(COMPARISON_FOCUS_SECTION_SEARCH_PARAM, normalizedSelection.scoreLink.section);
    params.set(COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM, normalizedSelection.scoreLink.componentKey);
  }
  const nextSearch = params.toString();
  return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
}

function readComparisonHistoryBrowserState(value: unknown): ComparisonHistoryBrowserState | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const candidate = (value as Record<string, unknown>)[COMPARISON_HISTORY_BROWSER_STATE_KEY];
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
    return null;
  }
  const parsed = candidate as Partial<ComparisonHistoryBrowserState>;
  if (
    parsed.version !== COMPARISON_HISTORY_BROWSER_STATE_VERSION
    || typeof parsed.entryId !== "string"
    || typeof parsed.label !== "string"
    || typeof parsed.summary !== "string"
    || typeof parsed.title !== "string"
  ) {
    return null;
  }
  return {
    version: parsed.version,
    entryId: parsed.entryId,
    label: parsed.label,
    summary: parsed.summary,
    title: parsed.title,
    selection: normalizeControlRoomComparisonSelection(parsed.selection),
  };
}

function buildComparisonHistoryBrowserState(
  currentState: unknown,
  selection: ControlRoomComparisonSelectionState,
  step: ComparisonHistoryStepDescriptor,
  entryId: string,
) {
  const nextState =
    currentState && typeof currentState === "object" && !Array.isArray(currentState)
      ? { ...(currentState as Record<string, unknown>) }
      : {};
  nextState[COMPARISON_HISTORY_BROWSER_STATE_KEY] = {
    version: COMPARISON_HISTORY_BROWSER_STATE_VERSION,
    entryId,
    label: step.label,
    summary: step.summary,
    title: step.title,
    selection: normalizeControlRoomComparisonSelection(selection),
  } satisfies ComparisonHistoryBrowserState;
  return nextState;
}

function isSameComparisonHistoryBrowserState(
  left: ComparisonHistoryBrowserState | null,
  right: ComparisonHistoryBrowserState | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return (
    left.label === right.label
    && left.summary === right.summary
    && left.title === right.title
    && isSameComparisonSelection(left.selection, right.selection)
  );
}

function persistComparisonSelectionToUrl(
  selection: ControlRoomComparisonSelectionState,
  step: ComparisonHistoryStepDescriptor,
  entryId: string,
  mode: Exclude<ComparisonHistoryWriteMode, "skip"> = "replace",
) {
  if (typeof window === "undefined") {
    return;
  }
  const nextUrl = buildComparisonSelectionHistoryUrl(selection);
  const nextState = buildComparisonHistoryBrowserState(window.history.state, selection, step, entryId);
  if (typeof document !== "undefined") {
    document.title = step.title;
  }
  if (mode === "push") {
    window.history.pushState(nextState, step.title, nextUrl);
    return;
  }
  window.history.replaceState(nextState, step.title, nextUrl);
}

function buildComparisonHistoryEntryId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `compare-step-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function buildComparisonHistoryPanelEntry(
  browserState: ComparisonHistoryBrowserState,
  url: string,
): ComparisonHistoryPanelEntry {
  return {
    entryId: browserState.entryId,
    label: browserState.label,
    summary: browserState.summary,
    title: browserState.title,
    url,
    selection: normalizeControlRoomComparisonSelection(browserState.selection),
  };
}

function reconcileComparisonHistoryPanelState(
  current: ComparisonHistoryPanelState,
  entry: ComparisonHistoryPanelEntry,
  mode: "push" | "replace" | "activate",
): ComparisonHistoryPanelState {
  const existingIndex = current.entries.findIndex((candidate) => candidate.entryId === entry.entryId);

  if (mode === "activate") {
    if (existingIndex >= 0) {
      return {
        entries: current.entries.map((candidate, index) => (index === existingIndex ? entry : candidate)),
        activeEntryId: entry.entryId,
      };
    }
    return {
      entries: [entry],
      activeEntryId: entry.entryId,
    };
  }

  if (mode === "push") {
    const activeIndex = current.activeEntryId
      ? current.entries.findIndex((candidate) => candidate.entryId === current.activeEntryId)
      : current.entries.length - 1;
    const baseEntries = activeIndex >= 0 ? current.entries.slice(0, activeIndex + 1) : [];
    const nextEntries = [...baseEntries.filter((candidate) => candidate.entryId !== entry.entryId), entry];
    return {
      entries: nextEntries.slice(-MAX_COMPARISON_HISTORY_PANEL_ENTRIES),
      activeEntryId: entry.entryId,
    };
  }

  if (existingIndex >= 0) {
    return {
      entries: current.entries.map((candidate, index) => (index === existingIndex ? entry : candidate)),
      activeEntryId: entry.entryId,
    };
  }

  const activeIndex = current.activeEntryId
    ? current.entries.findIndex((candidate) => candidate.entryId === current.activeEntryId)
    : -1;
  if (activeIndex >= 0) {
    return {
      entries: current.entries.map((candidate, index) => (index === activeIndex ? entry : candidate)),
      activeEntryId: entry.entryId,
    };
  }

  return {
    entries: [entry],
    activeEntryId: entry.entryId,
  };
}

function loadLegacyExpandedGapRows() {
  if (typeof window === "undefined") {
    return {};
  }
  try {
    const raw = window.localStorage.getItem(LEGACY_GAP_WINDOW_EXPANSION_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return {};
    }
    return filterExpandedGapRows(parsed);
  } catch {
    return {};
  }
}

function filterExpandedGapRows(value: unknown) {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).filter((entry): entry is [string, boolean] => entry[1] === true),
  );
}

function normalizeControlRoomComparisonSelection(
  value: Partial<ControlRoomComparisonSelectionState> | null | undefined,
): ControlRoomComparisonSelectionState {
  const selectedRunIds = normalizeComparisonRunIdList(value?.selectedRunIds);
  const scoreLink = normalizeComparisonScoreLinkTarget(value?.scoreLink);
  return {
    intent: normalizeComparisonIntent(value?.intent),
    selectedRunIds,
    scoreLink:
      scoreLink && selectedRunIds.includes(scoreLink.narrativeRunId)
        ? scoreLink
        : null,
  };
}

function isSameComparisonSelection(
  left: Partial<ControlRoomComparisonSelectionState> | null | undefined,
  right: Partial<ControlRoomComparisonSelectionState> | null | undefined,
) {
  const normalizedLeft = normalizeControlRoomComparisonSelection(left);
  const normalizedRight = normalizeControlRoomComparisonSelection(right);
  return (
    normalizedLeft.intent === normalizedRight.intent
    && normalizedLeft.selectedRunIds.length === normalizedRight.selectedRunIds.length
    && normalizedLeft.selectedRunIds.every((runId, index) => runId === normalizedRight.selectedRunIds[index])
    && (
      (normalizedLeft.scoreLink === null && normalizedRight.scoreLink === null)
      || (
        normalizedLeft.scoreLink !== null
        && normalizedRight.scoreLink !== null
        && normalizedLeft.scoreLink.narrativeRunId === normalizedRight.scoreLink.narrativeRunId
        && normalizedLeft.scoreLink.section === normalizedRight.scoreLink.section
        && normalizedLeft.scoreLink.componentKey === normalizedRight.scoreLink.componentKey
      )
    )
  );
}

function formatComparisonHistoryPanelEntryMeta(entry: ComparisonHistoryPanelEntry) {
  const parts = [
    formatComparisonIntentLabel(entry.selection.intent),
    `${entry.selection.selectedRunIds.length} run${entry.selection.selectedRunIds.length === 1 ? "" : "s"}`,
  ];
  if (entry.selection.scoreLink) {
    parts.push(
      formatComparisonScoreComponentLabel(
        entry.selection.scoreLink.section,
        entry.selection.scoreLink.componentKey,
      ),
    );
  }
  return parts.join(" / ");
}

function buildComparisonHistoryStepDescriptor(
  selection: ControlRoomComparisonSelectionState,
  runs: Run[],
  comparison: RunComparison | null,
): ComparisonHistoryStepDescriptor {
  const normalizedSelection = normalizeControlRoomComparisonSelection(selection);
  const intentLabel = formatComparisonIntentLabel(normalizedSelection.intent);
  const selectedRuns = normalizedSelection.selectedRunIds.map((runId) => ({
    runId,
    label: resolveComparisonHistoryRunLabel(runId, runs, comparison),
  }));
  const baselineRunId =
    comparison?.baseline_run_id && normalizedSelection.selectedRunIds.includes(comparison.baseline_run_id)
      ? comparison.baseline_run_id
      : selectedRuns[0]?.runId ?? null;
  const baselineLabel = baselineRunId
    ? resolveComparisonHistoryRunLabel(baselineRunId, runs, comparison)
    : null;
  const comparisonTargets = selectedRuns.filter((candidate) => candidate.runId !== baselineRunId);
  const primaryNarrative = comparison?.narratives.find((candidate) => candidate.is_primary) ?? comparison?.narratives[0] ?? null;

  if (normalizedSelection.scoreLink) {
    const componentLabel = formatComparisonScoreComponentLabel(
      normalizedSelection.scoreLink.section,
      normalizedSelection.scoreLink.componentKey,
    );
    const focusRunLabel = resolveComparisonHistoryRunLabel(
      normalizedSelection.scoreLink.narrativeRunId,
      runs,
      comparison,
    );
    const focusNarrative = comparison?.narratives.find(
      (candidate) => candidate.run_id === normalizedSelection.scoreLink?.narrativeRunId,
    ) ?? null;
    const label = `${truncateLabel(componentLabel, 24)} focus`;
    const summary = [
      `${componentLabel} is pinned to ${focusRunLabel}.`,
      normalizedSelection.selectedRunIds.length > 1
        ? `${intentLabel} across ${normalizedSelection.selectedRunIds.length} runs.`
        : `${intentLabel} with one staged run.`,
      baselineLabel && baselineRunId !== normalizedSelection.scoreLink.narrativeRunId
        ? `Baseline ${baselineLabel}.`
        : null,
      focusNarrative?.title ? `Story: ${truncateLabel(focusNarrative.title, 104)}.` : null,
    ]
      .filter(Boolean)
      .join(" ");
    return {
      label,
      summary,
      title: `Compare: ${label} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  if (!selectedRuns.length) {
    return {
      label: "Comparison cleared",
      summary: `No runs selected. ${intentLabel} is ready for the next comparison step.`,
      title: `Compare: cleared | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  if (selectedRuns.length === 1) {
    const onlyRun = selectedRuns[0];
    const label = `${truncateLabel(onlyRun.label, 28)} staged`;
    return {
      label,
      summary: `${onlyRun.label} is staged for ${intentLabel.toLowerCase()}. Select one more run to open comparison insights.`,
      title: `Compare: ${label} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
    };
  }

  const comparisonLabel =
    baselineLabel && comparisonTargets[0]
      ? `${truncateLabel(baselineLabel, 18)} vs ${truncateLabel(comparisonTargets[0].label, 18)}${
          comparisonTargets.length > 1 ? ` +${comparisonTargets.length - 1}` : ""
        }`
      : `${truncateLabel(selectedRuns[0].label, 18)} +${selectedRuns.length - 1}`;
  const summary = [
    baselineLabel
      ? `Baseline ${baselineLabel}${comparisonTargets[0] ? ` against ${comparisonTargets[0].label}` : ""}${
          comparisonTargets.length > 1 ? ` and ${comparisonTargets.length - 1} more runs` : ""
        }.`
      : `Tracking ${selectedRuns.length} runs.`,
    `${intentLabel} is active.`,
    primaryNarrative?.title ? `Top insight: ${truncateLabel(primaryNarrative.title, 104)}.` : null,
  ]
    .filter(Boolean)
    .join(" ");
  return {
    label: comparisonLabel,
    summary,
    title: `Compare: ${comparisonLabel} | ${DEFAULT_CONTROL_ROOM_DOCUMENT_TITLE}`,
  };
}

function resolveComparisonHistoryRunLabel(
  runId: string,
  runs: Run[],
  comparison: RunComparison | null,
) {
  const comparisonRun = comparison?.runs.find((candidate) => candidate.run_id === runId);
  if (comparisonRun) {
    return (
      comparisonRun.reference?.title
      ?? comparisonRun.strategy_name
      ?? comparisonRun.strategy_id
      ?? shortenIdentifier(runId)
    );
  }
  const run = runs.find((candidate) => candidate.config.run_id === runId);
  if (!run) {
    return shortenIdentifier(runId);
  }
  return (
    run.provenance.reference?.title
    ?? run.provenance.strategy?.name
    ?? run.config.strategy_id
    ?? shortenIdentifier(runId)
  );
}

function normalizeComparisonRunIdList(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return Array.from(
    new Set(
      value
        .map((item) => String(item).trim())
        .filter(Boolean),
    ),
  ).slice(0, MAX_COMPARISON_RUNS);
}

function normalizeComparisonIntent(value: unknown): ComparisonIntent {
  return comparisonIntentOptions.includes(value as ComparisonIntent)
    ? (value as ComparisonIntent)
    : DEFAULT_COMPARISON_INTENT;
}

function normalizeComparisonScoreSection(value: unknown): ComparisonScoreSection | null {
  return value === "metrics" || value === "semantics" || value === "context"
    ? value
    : null;
}

function normalizeComparisonScoreLinkTarget(value: unknown): ComparisonScoreLinkTarget | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<ComparisonScoreLinkTarget>;
  const narrativeRunId =
    typeof candidate.narrativeRunId === "string" ? candidate.narrativeRunId.trim() : "";
  const componentKey = typeof candidate.componentKey === "string" ? candidate.componentKey.trim() : "";
  const section = normalizeComparisonScoreSection(candidate.section);
  if (!narrativeRunId || !componentKey || !section) {
    return null;
  }
  return {
    componentKey,
    narrativeRunId,
    section,
  };
}

function isControlRoomUiStateV1(value: unknown): value is ControlRoomUiStateV1 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV1>;
  return (
    candidate.version === 1 &&
    candidate.expandedGapRows !== undefined
  );
}

function isControlRoomUiStateV2(value: unknown): value is ControlRoomUiStateV2 {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ControlRoomUiStateV2>;
  return (
    candidate.version === CONTROL_ROOM_UI_STATE_VERSION &&
    candidate.expandedGapRows !== undefined &&
    candidate.comparisonSelection !== undefined
  );
}

function buildRunsPath(mode: string, filter: RunHistoryFilter) {
  const params = new URLSearchParams({ mode });
  if (filter.strategy_id !== ALL_FILTER_VALUE) {
    params.set("strategy_id", filter.strategy_id);
  }
  if (filter.strategy_version !== ALL_FILTER_VALUE) {
    params.set("strategy_version", filter.strategy_version);
  }
  if (filter.preset_id.trim()) {
    params.set("preset_id", filter.preset_id.trim());
  }
  if (filter.benchmark_family.trim()) {
    params.set("benchmark_family", filter.benchmark_family.trim());
  }
  if (filter.tag.trim()) {
    parseExperimentTags(filter.tag).forEach((tag) => params.append("tag", tag));
  }
  if (filter.dataset_identity.trim()) {
    params.set("dataset_identity", filter.dataset_identity.trim());
  }
  return `/runs?${params.toString()}`;
}

function buildRunComparisonPath(runIds: string[], intent: ComparisonIntent) {
  const params = new URLSearchParams();
  runIds.forEach((runId) => params.append("run_id", runId));
  params.set("intent", intent);
  return `/runs/compare?${params.toString()}`;
}

function normalizeRunHistoryFilter(current: RunHistoryFilter, strategies: Strategy[]) {
  const availableStrategyIds = new Set(strategies.map((strategy) => strategy.strategy_id));
  if (
    current.strategy_id !== ALL_FILTER_VALUE &&
    !availableStrategyIds.has(current.strategy_id)
  ) {
    return {
      ...defaultRunHistoryFilter,
      preset_id: current.preset_id,
      benchmark_family: current.benchmark_family,
      tag: current.tag,
      dataset_identity: current.dataset_identity,
    };
  }
  const availableVersions = getStrategyVersionOptions(strategies, current.strategy_id);
  if (
    current.strategy_version !== ALL_FILTER_VALUE &&
    !availableVersions.includes(current.strategy_version)
  ) {
    return { ...current, strategy_version: ALL_FILTER_VALUE };
  }
  return current;
}

function normalizeRunHistoryPresetFilter(
  current: RunHistoryFilter,
  presets: ExperimentPreset[],
) {
  if (!current.preset_id) {
    return current;
  }
  const matchingPreset = presets.find((preset) => preset.preset_id === current.preset_id);
  if (
    matchingPreset &&
    (
      current.strategy_id === ALL_FILTER_VALUE ||
      !matchingPreset.strategy_id ||
      matchingPreset.strategy_id === current.strategy_id
    )
  ) {
    return current;
  }
  return {
    ...current,
    preset_id: "",
  };
}

function getStrategyVersionOptions(strategies: Strategy[], strategyId: string) {
  const scopedStrategies =
    strategyId === ALL_FILTER_VALUE
      ? strategies
      : strategies.filter((strategy) => strategy.strategy_id === strategyId);
  return Array.from(
    new Set(
      scopedStrategies.flatMap((strategy) =>
        strategy.version_lineage.length ? strategy.version_lineage : [strategy.version],
      ),
    ),
  ).sort();
}

function pickLatestBenchmarkRun(runs: Run[], lane: string) {
  return (
    runs.find((run) => run.provenance.lane === lane && run.status === "completed") ??
    runs.find((run) => run.provenance.lane === lane) ??
    null
  );
}

function StrategyColumn({
  title,
  strategies,
  accent,
}: {
  title: string;
  strategies: Strategy[];
  accent: string;
}) {
  return (
    <div className={`strategy-column ${accent}`}>
      <h3>{title}</h3>
      {strategies.length ? (
        strategies.map((strategy) => (
          <article className="strategy-card" key={strategy.strategy_id}>
            <div className="strategy-head">
              <div>
                <strong>{strategy.name}</strong>
                <div className="strategy-badges">
                  <span className="meta-pill">{formatLaneLabel(strategy.runtime)}</span>
                  <span className="meta-pill subtle">{strategy.lifecycle.stage}</span>
                  <span className="meta-pill subtle">{strategy.version}</span>
                </div>
              </div>
              <span>{formatVersionLineage(strategy.version_lineage, strategy.version)}</span>
            </div>
            <p>{strategy.description}</p>
            {strategy.catalog_semantics.execution_model ? (
              <p className="run-note">{strategy.catalog_semantics.execution_model}</p>
            ) : null}
            <dl>
              <div>
                <dt>ID</dt>
                <dd>{strategy.strategy_id}</dd>
              </div>
              <div>
                <dt>Timeframes</dt>
                <dd>{strategy.supported_timeframes.join(", ")}</dd>
              </div>
              <div>
                <dt>Assets</dt>
                <dd>{strategy.asset_types.join(", ")}</dd>
              </div>
              <div>
                <dt>Defaults</dt>
                <dd>{formatParameterMap(extractDefaultParameters(strategy.parameter_schema))}</dd>
              </div>
              {strategy.catalog_semantics.parameter_contract ? (
                <div>
                  <dt>Parameter contract</dt>
                  <dd>{strategy.catalog_semantics.parameter_contract}</dd>
                </div>
              ) : null}
              {strategy.catalog_semantics.source_descriptor ? (
                <div>
                  <dt>Source</dt>
                  <dd>{strategy.catalog_semantics.source_descriptor}</dd>
                </div>
              ) : null}
              {strategy.reference_path ? (
                <div>
                  <dt>Reference</dt>
                  <dd>{strategy.reference_path}</dd>
                </div>
              ) : null}
              {strategy.reference_id ? (
                <div>
                  <dt>Reference ID</dt>
                  <dd>{strategy.reference_id}</dd>
                </div>
              ) : null}
              {strategy.lifecycle.registered_at ? (
                <div>
                  <dt>Registered</dt>
                  <dd>{formatTimestamp(strategy.lifecycle.registered_at)}</dd>
                </div>
              ) : null}
              {strategy.catalog_semantics.operator_notes.length ? (
                <div>
                  <dt>Operator notes</dt>
                  <dd>{strategy.catalog_semantics.operator_notes.join(" | ")}</dd>
                </div>
              ) : null}
            </dl>
          </article>
        ))
      ) : (
        <p className="empty-state">No strategies registered.</p>
      )}
    </div>
  );
}

function ReferenceCatalog({ references }: { references: ReferenceSource[] }) {
  return references.length ? (
    <div className="run-list">
      {references.map((reference) => (
        <article className="run-card" key={reference.reference_id}>
          <div className="run-card-head">
            <div>
              <strong>{reference.title}</strong>
              <span>{reference.reference_id}</span>
            </div>
            <div className="run-status completed">{reference.integration_mode}</div>
          </div>
          <div className="run-metrics">
            <Metric label="License" value={reference.license} />
            <Metric label="Runtime" value={reference.runtime ?? "n/a"} />
          </div>
          <p className="run-note">{reference.summary}</p>
        </article>
      ))}
    </div>
  ) : (
    <p className="empty-state">No references registered.</p>
  );
}

function PresetStructuredDiffPreview({
  changedGroups,
  emptyMessage,
  leftColumnLabel,
  rightColumnLabel,
  title,
  unchangedGroups,
}: {
  changedGroups: PresetStructuredDiffGroup[];
  emptyMessage: string;
  leftColumnLabel: string;
  rightColumnLabel: string;
  title: string;
  unchangedGroups: PresetStructuredDiffGroup[];
}) {
  const [showUnchangedGroups, setShowUnchangedGroups] = useState(false);
  const unchangedRowCount = unchangedGroups.reduce((total, group) => total + group.rows.length, 0);
  const renderGroupRows = (group: PresetStructuredDiffGroup) =>
    group.rows.map((row) => (
      <div
        className={`comparison-dev-conflict-preview-row ${row.changed ? "is-changed" : ""}`}
        key={row.key}
      >
        <span className="comparison-dev-conflict-preview-label-group">
          <span className="comparison-dev-conflict-preview-label">{row.label}</span>
          {row.semantic_hint ? (
            <span className="comparison-dev-conflict-preview-hint">{row.semantic_hint}</span>
          ) : null}
          <span className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}>
            {row.delta_label}
          </span>
        </span>
        <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
          {row.existing_value}
        </span>
        <span
          className={`comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-${
            row.changed ? row.delta_direction : "same"
          }`}
        >
          {row.incoming_value}
        </span>
      </div>
    ));

  return (
    <div className="comparison-dev-session-summary">
      <p className="comparison-dev-session-summary-title">{title}</p>
      <div className="comparison-dev-conflict-preview">
        <div className="comparison-dev-conflict-preview-row comparison-dev-conflict-preview-head">
          <span>Field</span>
          <span>{leftColumnLabel}</span>
          <span>{rightColumnLabel}</span>
        </div>
        {changedGroups.length ? (
          changedGroups.map((group) => (
            <div className="comparison-dev-conflict-preview-group" key={group.key}>
              <div className="comparison-dev-conflict-preview-group-title">
                <span>{group.label}</span>
                <span className="comparison-dev-conflict-preview-group-meta">
                  <span className="comparison-dev-conflict-preview-group-summary">{group.summary_label}</span>
                </span>
              </div>
              {renderGroupRows(group)}
            </div>
          ))
        ) : (
          <p className="empty-state">{emptyMessage}</p>
        )}
        {unchangedRowCount ? (
          <button
            className="comparison-dev-conflict-toggle"
            onClick={() => setShowUnchangedGroups((current) => !current)}
            type="button"
          >
            {showUnchangedGroups
              ? `Hide ${unchangedRowCount} unchanged field${unchangedRowCount === 1 ? "" : "s"}`
              : `Show ${unchangedRowCount} unchanged field${unchangedRowCount === 1 ? "" : "s"}`}
          </button>
        ) : null}
        {showUnchangedGroups
          ? unchangedGroups.map((group) => (
              <div className="comparison-dev-conflict-preview-group" key={group.key}>
                <div className="comparison-dev-conflict-preview-group-title">
                  <span>{group.label}</span>
                  <span className="comparison-dev-conflict-preview-group-meta">
                    <span className="comparison-dev-conflict-preview-group-summary">{group.summary_label}</span>
                  </span>
                </div>
                {renderGroupRows(group)}
              </div>
            ))
          : null}
      </div>
    </div>
  );
}

function PresetCatalogPanel({
  form,
  presets,
  setForm,
  strategies,
  editingPresetId,
  expandedPresetRevisionIds,
  onEditPreset,
  onResetEditor,
  onLifecycleAction,
  onRestoreRevision,
  onSubmit,
  onToggleRevisions,
}: {
  form: typeof defaultPresetForm;
  presets: ExperimentPreset[];
  setForm: (updater: (value: typeof defaultPresetForm) => typeof defaultPresetForm) => void;
  strategies: Strategy[];
  editingPresetId: string | null;
  expandedPresetRevisionIds: Record<string, boolean>;
  onEditPreset: (preset: ExperimentPreset) => void;
  onResetEditor: () => void;
  onLifecycleAction: (presetId: string, action: "promote" | "archive" | "restore") => Promise<void> | void;
  onRestoreRevision: (presetId: string, revisionId: string) => Promise<void> | void;
  onSubmit: (event: FormEvent) => Promise<void> | void;
  onToggleRevisions: (presetId: string) => void;
}) {
  const isEditing = editingPresetId !== null;
  const findStrategyParameterSchema = (strategyId?: string | null) =>
    strategies.find((strategy) => strategy.strategy_id === strategyId)?.parameter_schema;
  const [revisionFiltersByPreset, setRevisionFiltersByPreset] = useState<
    Record<string, PresetRevisionFilterState>
  >({});
  const [expandedRevisionDiffIds, setExpandedRevisionDiffIds] = useState<Record<string, boolean>>({});
  const [restoreDraftConflictAcknowledgements, setRestoreDraftConflictAcknowledgements] = useState<
    Record<string, boolean>
  >({});
  const [pendingRestoreTarget, setPendingRestoreTarget] = useState<{
    presetId: string;
    revisionId: string;
  } | null>(null);

  async function confirmRevisionRestore(presetId: string, revisionId: string) {
    await onRestoreRevision(presetId, revisionId);
    setRestoreDraftConflictAcknowledgements((current) => {
      const next = { ...current };
      delete next[`${presetId}:${revisionId}`];
      return next;
    });
    setPendingRestoreTarget((current) =>
      current?.presetId === presetId && current?.revisionId === revisionId ? null : current,
    );
  }

  return (
    <>
      <form className="run-form" onSubmit={onSubmit}>
        <label>
          Name
          <input
            placeholder="Core 5m"
            value={form.name}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
          />
        </label>
        <label>
          Preset ID
          <input
            disabled={isEditing}
            placeholder="core_5m"
            value={form.preset_id}
            onChange={(event) => setForm((current) => ({ ...current, preset_id: event.target.value }))}
          />
        </label>
        <label>
          Strategy
          <select
            value={form.strategy_id}
            onChange={(event) => setForm((current) => ({ ...current, strategy_id: event.target.value }))}
          >
            <option value="">Any strategy</option>
            {strategies.map((strategy) => (
              <option key={strategy.strategy_id} value={strategy.strategy_id}>
                {strategy.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Timeframe
          <input
            placeholder="5m"
            value={form.timeframe}
            onChange={(event) => setForm((current) => ({ ...current, timeframe: event.target.value }))}
          />
        </label>
        <label>
          Benchmark family
          <input
            placeholder="native_validation"
            value={form.benchmark_family}
            onChange={(event) =>
              setForm((current) => ({ ...current, benchmark_family: event.target.value }))
            }
          />
        </label>
        <label>
          Tags
          <input
            placeholder="baseline, momentum"
            value={form.tags_text}
            onChange={(event) => setForm((current) => ({ ...current, tags_text: event.target.value }))}
          />
        </label>
        <label>
          Description
          <input
            placeholder="Reusable backtest baseline"
            value={form.description}
            onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
          />
        </label>
        <label>
          Parameters JSON
          <textarea
            placeholder='{"short_window": 5, "long_window": 13}'
            rows={4}
            value={form.parameters_text}
            onChange={(event) =>
              setForm((current) => ({ ...current, parameters_text: event.target.value }))
            }
          />
        </label>
        {isEditing ? (
          <p className="run-note">
            Editing {editingPresetId}. Preset IDs are immutable, so this form updates the current bundle and records a
            new revision.
          </p>
        ) : null}
        <div className="run-actions">
          <button type="submit">{isEditing ? "Save revision" : "Save preset"}</button>
          {isEditing ? (
            <button className="ghost-button" onClick={onResetEditor} type="button">
              New preset
            </button>
          ) : null}
        </div>
      </form>

      {presets.length ? (
        <div className="run-list">
          {presets.map((preset) => (
            <article className="run-card" key={preset.preset_id}>
              {(() => {
                const revisions = [...preset.revisions].reverse();
                const latestRevisionId = revisions[0]?.revision_id;
                const revisionsExpanded = Boolean(expandedPresetRevisionIds[preset.preset_id]);
                const revisionFilter = revisionFiltersByPreset[preset.preset_id] ?? defaultPresetRevisionFilter;
                const draftConflict =
                  editingPresetId === preset.preset_id
                    ? describePresetDraftConflict(
                        preset,
                        form,
                        findStrategyParameterSchema(form.strategy_id || preset.strategy_id),
                      )
                    : null;
                const visibleRevisionEntries = revisions
                  .map((revision, index) => {
                    const diffReference =
                      revision.revision_id === latestRevisionId
                        ? revisions[index + 1] ?? null
                        : buildCurrentPresetRevisionSnapshot(preset);
                    const diffBasisLabel =
                      revision.revision_id === latestRevisionId
                        ? revisions[index + 1]
                          ? "previous snapshot"
                          : "initial revision"
                        : "current bundle";
                    const diff = describePresetRevisionDiff(
                      revision,
                      diffReference,
                      diffBasisLabel,
                      findStrategyParameterSchema(revision.strategy_id ?? preset.strategy_id),
                    );
                    return { diff, revision };
                  })
                  .filter(({ diff, revision }) => matchesPresetRevisionFilter(revision, diff, revisionFilter));
                return (
                  <>
                    <div className="run-card-head">
                      <div>
                        <strong>{preset.name}</strong>
                        <span>{preset.preset_id}</span>
                      </div>
                      <div className={`run-status ${preset.lifecycle.stage === "archived" ? "failed" : "completed"}`}>
                        {formatPresetLifecycleStage(preset.lifecycle.stage)}
                      </div>
                    </div>
                    <div className="run-metrics">
                      <Metric label="Strategy" value={preset.strategy_id ?? "any"} />
                      <Metric label="Timeframe" value={preset.timeframe ?? "any"} />
                      <Metric label="Params" value={formatParameterMap(preset.parameters)} />
                      <Metric label="Revisions" value={String(preset.revisions.length)} />
                      <Metric label="Updated" value={formatTimestamp(preset.updated_at)} />
                    </div>
                    <ExperimentMetadataPills
                      benchmarkFamily={preset.benchmark_family}
                      presetId={preset.preset_id}
                      tags={preset.tags}
                    />
                    <p className="run-note">
                      Lifecycle: {formatPresetLifecycleStage(preset.lifecycle.stage)} via{" "}
                      {preset.lifecycle.last_action} by {preset.lifecycle.updated_by} at{" "}
                      {formatTimestamp(preset.lifecycle.updated_at)}.
                    </p>
                    {preset.description ? <p className="run-note">{preset.description}</p> : null}
                    <div className="run-actions">
                      <button className="ghost-button" onClick={() => onEditPreset(preset)} type="button">
                        {editingPresetId === preset.preset_id ? "Editing bundle" : "Edit bundle"}
                      </button>
                      <button
                        className="ghost-button"
                        onClick={() => onToggleRevisions(preset.preset_id)}
                        type="button"
                      >
                        {revisionsExpanded ? "Hide revisions" : `Show revisions (${preset.revisions.length})`}
                      </button>
                      {preset.lifecycle.stage !== "archived" ? (
                        <>
                          {preset.lifecycle.stage !== "live_candidate" ? (
                            <button
                              className="ghost-button"
                              onClick={() => void onLifecycleAction(preset.preset_id, "promote")}
                              type="button"
                            >
                              Promote
                            </button>
                          ) : null}
                          <button
                            className="ghost-button danger"
                            onClick={() => void onLifecycleAction(preset.preset_id, "archive")}
                            type="button"
                          >
                            Archive
                          </button>
                        </>
                      ) : (
                        <button
                          className="ghost-button"
                          onClick={() => void onLifecycleAction(preset.preset_id, "restore")}
                          type="button"
                        >
                          Restore to draft
                        </button>
                      )}
                    </div>
                    {revisionsExpanded ? (
                      <>
                        <div className="run-form">
                          <label>
                            Search revisions
                            <input
                              placeholder="actor, reason, parameter, tag"
                              value={revisionFilter.query}
                              onChange={(event) =>
                                setRevisionFiltersByPreset((current) => ({
                                  ...current,
                                  [preset.preset_id]: {
                                    ...(current[preset.preset_id] ?? defaultPresetRevisionFilter),
                                    query: event.target.value,
                                  },
                                }))
                              }
                            />
                          </label>
                          <label>
                            Action
                            <select
                              value={revisionFilter.action}
                              onChange={(event) =>
                                setRevisionFiltersByPreset((current) => ({
                                  ...current,
                                  [preset.preset_id]: {
                                    ...(current[preset.preset_id] ?? defaultPresetRevisionFilter),
                                    action: event.target.value,
                                  },
                                }))
                              }
                            >
                              <option value="all">All actions</option>
                              <option value="created">Created</option>
                              <option value="updated">Updated</option>
                              <option value="restored">Restored</option>
                              <option value="migrated">Migrated</option>
                            </select>
                          </label>
                        </div>
                        <p className="run-note">
                          Showing {visibleRevisionEntries.length} of {revisions.length} revision
                          {revisions.length === 1 ? "" : "s"}.
                        </p>
                        {visibleRevisionEntries.length ? (
                          <div className="run-list">
                            {visibleRevisionEntries.map(({ revision, diff }) => {
                              const diffExpanded = Boolean(expandedRevisionDiffIds[revision.revision_id]);
                              const confirmingRestore =
                                pendingRestoreTarget?.presetId === preset.preset_id &&
                                pendingRestoreTarget?.revisionId === revision.revision_id;
                              const acknowledgementKey = `${preset.preset_id}:${revision.revision_id}`;
                              const hasDraftConflict = Boolean(draftConflict && draftConflict.changeCount);
                              const draftConflictAcknowledged = Boolean(
                                restoreDraftConflictAcknowledgements[acknowledgementKey],
                              );
                              return (
                                <article className="run-card" key={revision.revision_id}>
                                  <div className="run-card-head">
                                    <div>
                                      <strong>{revision.revision_id}</strong>
                                      <span>{revision.action}</span>
                                    </div>
                                    <div
                                      className={`run-status ${
                                        revision.revision_id === latestRevisionId ? "completed" : "pending"
                                      }`}
                                    >
                                      {revision.revision_id === latestRevisionId ? "current bundle" : "snapshot"}
                                    </div>
                                  </div>
                                  <div className="run-metrics">
                                    <Metric label="Actor" value={revision.actor} />
                                    <Metric label="Recorded" value={formatRelativeTimestampLabel(revision.created_at)} />
                                    <Metric label="Strategy" value={revision.strategy_id ?? "any"} />
                                    <Metric label="Diff" value={`${diff.changeCount} change${diff.changeCount === 1 ? "" : "s"}`} />
                                  </div>
                                  <ExperimentMetadataPills
                                    benchmarkFamily={revision.benchmark_family}
                                    tags={revision.tags}
                                  />
                                  <p className="run-note">
                                    Reason: {revision.reason}. {diff.summary}
                                    {revision.source_revision_id ? ` Restored from ${revision.source_revision_id}.` : ""}
                                  </p>
                                  {revision.description ? <p className="run-note">{revision.description}</p> : null}
                                  <div className="run-actions">
                                    <button
                                      className="ghost-button"
                                      onClick={() =>
                                        setExpandedRevisionDiffIds((current) => ({
                                          ...current,
                                          [revision.revision_id]: !current[revision.revision_id],
                                        }))
                                      }
                                      type="button"
                                    >
                                      {diffExpanded ? "Hide diff" : `Show diff vs ${diff.basisLabel}`}
                                    </button>
                                    {revision.revision_id !== latestRevisionId ? (
                                      <button
                                        className="ghost-button"
                                        onClick={() => {
                                          setPendingRestoreTarget({
                                            presetId: preset.preset_id,
                                            revisionId: revision.revision_id,
                                          });
                                          setRestoreDraftConflictAcknowledgements((current) => ({
                                            ...current,
                                            [acknowledgementKey]: false,
                                          }));
                                        }}
                                        type="button"
                                      >
                                        Restore bundle
                                      </button>
                                    ) : null}
                                  </div>
                                  {diffExpanded ? (
                                    <PresetStructuredDiffPreview
                                      changedGroups={diff.changedGroups}
                                      emptyMessage={diff.summary}
                                      leftColumnLabel={diff.basisLabel}
                                      rightColumnLabel="Revision snapshot"
                                      title={`Diff vs ${diff.basisLabel}`}
                                      unchangedGroups={diff.unchangedGroups}
                                    />
                                  ) : null}
                                  {confirmingRestore ? (
                                    <div className="comparison-dev-confirm-card">
                                      <p className="comparison-dev-feedback">
                                        Restore {revision.revision_id} into {preset.preset_id}? This will create a new
                                        current revision from the selected snapshot.
                                      </p>
                                      <p className="run-note">{diff.summary}</p>
                                      <PresetStructuredDiffPreview
                                        changedGroups={diff.changedGroups}
                                        emptyMessage={diff.summary}
                                        leftColumnLabel="Current bundle"
                                        rightColumnLabel="Restore target"
                                        title="Restore impact"
                                        unchangedGroups={diff.unchangedGroups}
                                      />
                                      {hasDraftConflict && draftConflict ? (
                                        <>
                                          <p className="comparison-dev-feedback">
                                            {draftConflict.summary}
                                            {draftConflict.hasInvalidParameters
                                              ? " The current draft also contains invalid parameter JSON."
                                              : ""}
                                          </p>
                                          <PresetStructuredDiffPreview
                                            changedGroups={draftConflict.groups}
                                            emptyMessage={draftConflict.summary}
                                            leftColumnLabel="Saved bundle"
                                            rightColumnLabel="Current draft"
                                            title="Unsaved draft conflict"
                                            unchangedGroups={[]}
                                          />
                                          <label className="run-note">
                                            <input
                                              checked={draftConflictAcknowledged}
                                              onChange={(event) =>
                                                setRestoreDraftConflictAcknowledgements((current) => ({
                                                  ...current,
                                                  [acknowledgementKey]: event.target.checked,
                                                }))
                                              }
                                              type="checkbox"
                                            />{" "}
                                            I understand this restore will discard the unsaved draft for{" "}
                                            {preset.preset_id}.
                                          </label>
                                        </>
                                      ) : null}
                                      <div className="comparison-dev-actions comparison-dev-actions-inline">
                                        <button
                                          className="ghost-button comparison-dev-reset"
                                          disabled={hasDraftConflict && !draftConflictAcknowledged}
                                          onClick={() => void confirmRevisionRestore(preset.preset_id, revision.revision_id)}
                                          type="button"
                                        >
                                          {hasDraftConflict ? "Discard draft and restore" : "Confirm restore"}
                                        </button>
                                        <button
                                          className="ghost-button comparison-dev-reset"
                                          onClick={() => {
                                            setPendingRestoreTarget(null);
                                            setRestoreDraftConflictAcknowledgements((current) => {
                                              const next = { ...current };
                                              delete next[acknowledgementKey];
                                              return next;
                                            });
                                          }}
                                          type="button"
                                        >
                                          Cancel
                                        </button>
                                      </div>
                                    </div>
                                  ) : null}
                                </article>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="empty-state">No revisions match the current filter.</p>
                        )}
                      </>
                    ) : null}
                  </>
                );
              })()}
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">No durable presets saved yet.</p>
      )}
    </>
  );
}

function RunForm({
  form,
  setForm,
  strategies,
  presets,
  onSubmit,
}: {
  form: typeof defaultRunForm;
  setForm: (updater: (value: typeof defaultRunForm) => typeof defaultRunForm) => void;
  strategies: Strategy[];
  presets: ExperimentPreset[];
  onSubmit: (event: FormEvent) => Promise<void> | void;
}) {
  const availablePresets = presets.filter(
    (preset) =>
      preset.lifecycle.stage !== "archived" &&
      (!preset.strategy_id || preset.strategy_id === form.strategy_id) &&
      (!preset.timeframe || preset.timeframe === form.timeframe),
  );
  const selectedPreset = availablePresets.find((preset) => preset.preset_id === form.preset_id) ?? null;

  return (
    <form className="run-form" onSubmit={onSubmit}>
      <label>
        Strategy
        <select
          value={form.strategy_id}
          onChange={(event) => setForm((current) => ({ ...current, strategy_id: event.target.value }))}
        >
          {strategies.map((strategy) => (
            <option key={strategy.strategy_id} value={strategy.strategy_id}>
              {strategy.name} / {strategy.runtime}
            </option>
          ))}
        </select>
      </label>
      <label>
        Symbol
        <input
          value={form.symbol}
          onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value }))}
        />
      </label>
      <label>
        Timeframe
        <input
          value={form.timeframe}
          onChange={(event) => setForm((current) => ({ ...current, timeframe: event.target.value }))}
        />
      </label>
      <label>
        Initial cash
        <input
          type="number"
          value={form.initial_cash}
          onChange={(event) => setForm((current) => ({ ...current, initial_cash: Number(event.target.value) }))}
        />
      </label>
      <label>
        Fee rate
        <input
          type="number"
          step="0.0001"
          value={form.fee_rate}
          onChange={(event) => setForm((current) => ({ ...current, fee_rate: Number(event.target.value) }))}
        />
      </label>
      <label>
        Slippage (bps)
        <input
          type="number"
          value={form.slippage_bps}
          onChange={(event) => setForm((current) => ({ ...current, slippage_bps: Number(event.target.value) }))}
        />
      </label>
      <label>
        Preset
        <select
          value={form.preset_id}
          onChange={(event) => setForm((current) => ({ ...current, preset_id: event.target.value }))}
        >
          <option value="">No preset</option>
          {availablePresets.map((preset) => (
            <option key={preset.preset_id} value={preset.preset_id}>
              {preset.name} ({preset.preset_id})
            </option>
          ))}
        </select>
      </label>
      <label>
        Benchmark family
        <input
          placeholder={selectedPreset?.benchmark_family ?? "native_vs_nfi"}
          value={form.benchmark_family}
          onChange={(event) =>
            setForm((current) => ({ ...current, benchmark_family: event.target.value }))
          }
        />
      </label>
      <label>
        Tags
        <input
          placeholder="baseline, momentum"
          value={form.tags_text}
          onChange={(event) => setForm((current) => ({ ...current, tags_text: event.target.value }))}
        />
      </label>
      {selectedPreset ? (
        <div className="run-note">
          Preset stage: {formatPresetLifecycleStage(selectedPreset.lifecycle.stage)}. Parameters:{" "}
          {formatParameterMap(selectedPreset.parameters)}.
        </div>
      ) : null}
      <button type="submit">Submit</button>
    </form>
  );
}

function ExperimentMetadataPills({
  benchmarkFamily,
  datasetIdentity,
  presetId,
  tags,
}: {
  benchmarkFamily?: string | null;
  datasetIdentity?: string | null;
  presetId?: string | null;
  tags: string[];
}) {
  if (!tags.length && !presetId && !benchmarkFamily && !datasetIdentity) {
    return null;
  }
  return (
    <div className="strategy-badges">
      {presetId ? (
        <span className="meta-pill subtle" title={presetId}>
          preset {presetId}
        </span>
      ) : null}
      {benchmarkFamily ? (
        <span className="meta-pill subtle" title={benchmarkFamily}>
          benchmark {benchmarkFamily}
        </span>
      ) : null}
      {datasetIdentity ? (
        <span className="meta-pill subtle" title={datasetIdentity}>
          dataset {shortenIdentifier(datasetIdentity)}
        </span>
      ) : null}
      {tags.map((tag) => (
        <span className="meta-pill subtle" key={tag}>
          #{tag}
        </span>
      ))}
    </div>
  );
}

type RunSectionComparisonControls = {
  selectedRunIds: string[];
  comparisonIntent: ComparisonIntent;
  historyStep: ComparisonHistoryStepDescriptor;
  historyEntries: ComparisonHistoryPanelEntry[];
  activeHistoryEntryId: string | null;
  historyBrowserOpen: boolean;
  canNavigateHistoryBackward: boolean;
  canNavigateHistoryForward: boolean;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  payload: RunComparison | null;
  loading: boolean;
  error: string | null;
  onChangeComparisonIntent: (intent: ComparisonIntent) => void;
  onChangeSelectedScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  onToggleHistoryBrowser: () => void;
  onNavigateHistoryEntry: (entryId: string) => void;
  onNavigateHistoryRelative: (delta: number) => void;
  onToggleRunSelection: (runId: string) => void;
  onClearSelection: () => void;
  onSelectBenchmarkPair: () => void;
};

type RunSectionRerunAction = {
  label: string;
  onRerun: (rerunBoundaryId: string) => Promise<void>;
};

type LiveOrderReplacementDraft = {
  price: string;
  quantity: string;
};

type RunOrderControls = {
  getReplacementDraft: (orderId: string, order: Run["orders"][number]) => LiveOrderReplacementDraft;
  onChangeReplacementDraft: (orderId: string, draft: LiveOrderReplacementDraft) => void;
  onCancelOrder: (orderId: string) => Promise<void>;
  onReplaceOrder: (orderId: string, draft: LiveOrderReplacementDraft) => Promise<void>;
};

function RunSection({
  title,
  runs,
  presets,
  strategies,
  filter,
  setFilter,
  comparison,
  rerunActions,
  onStop,
  getOrderControls,
}: {
  title: string;
  runs: Run[];
  presets: ExperimentPreset[];
  strategies: Strategy[];
  filter: RunHistoryFilter;
  setFilter: (updater: (value: RunHistoryFilter) => RunHistoryFilter) => void;
  comparison?: RunSectionComparisonControls;
  rerunActions?: RunSectionRerunAction[];
  onStop?: (runId: string) => Promise<void>;
  getOrderControls?: (run: Run) => RunOrderControls | null;
}) {
  const versionOptions = getStrategyVersionOptions(strategies, filter.strategy_id);
  const presetOptions = presets.filter(
    (preset) =>
      !preset.strategy_id ||
      filter.strategy_id === ALL_FILTER_VALUE ||
      preset.strategy_id === filter.strategy_id,
  );

  return (
    <section className="panel panel-wide">
      <div className="section-heading">
        <div>
          <p className="kicker">Execution plane</p>
          <h2>{title}</h2>
        </div>
        <div className="section-controls">
          <div className="filter-bar">
            <label>
              Strategy
              <select
                value={filter.strategy_id}
                onChange={(event) =>
                  setFilter((current) => {
                    const strategyId = event.target.value;
                    const nextVersionOptions = getStrategyVersionOptions(strategies, strategyId);
                    const nextVersion = nextVersionOptions.includes(current.strategy_version)
                      ? current.strategy_version
                      : ALL_FILTER_VALUE;
                    return {
                      ...current,
                      strategy_id: strategyId,
                      strategy_version: nextVersion,
                    };
                  })
                }
              >
                <option value={ALL_FILTER_VALUE}>All strategies</option>
                {strategies.map((strategy) => (
                  <option key={strategy.strategy_id} value={strategy.strategy_id}>
                    {strategy.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Version
              <select
                value={filter.strategy_version}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    strategy_version: event.target.value,
                  }))
                }
              >
                <option value={ALL_FILTER_VALUE}>All versions</option>
                {versionOptions.map((version) => (
                  <option key={version} value={version}>
                    {version}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Preset
              <select
                value={filter.preset_id}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    preset_id: event.target.value,
                  }))
                }
              >
                <option value="">All presets</option>
                {presetOptions.map((preset) => (
                  <option key={preset.preset_id} value={preset.preset_id}>
                    {preset.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Benchmark
              <input
                placeholder="All families"
                value={filter.benchmark_family}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    benchmark_family: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              Tag
              <input
                placeholder="baseline"
                value={filter.tag}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    tag: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              Dataset
              <input
                placeholder="dataset-v1:..."
                value={filter.dataset_identity}
                onChange={(event) =>
                  setFilter((current) => ({
                    ...current,
                    dataset_identity: event.target.value,
                  }))
                }
              />
            </label>
          </div>
          {comparison ? (
            <div className="comparison-toolbar">
              <div className="comparison-history-step" aria-live="polite">
                <p className="comparison-history-step-label">{comparison.historyStep.label}</p>
                <p className="comparison-history-step-summary">{comparison.historyStep.summary}</p>
              </div>
              <button className="ghost-button" onClick={comparison.onToggleHistoryBrowser} type="button">
                {comparison.historyBrowserOpen
                  ? "Hide history browser"
                  : `History browser (${comparison.historyEntries.length})`}
              </button>
              <span>
                Compare {comparison.selectedRunIds.length} / {MAX_COMPARISON_RUNS}
              </span>
              <label className="comparison-intent-field">
                Intent
                <select
                  value={comparison.comparisonIntent}
                  onChange={(event) => comparison.onChangeComparisonIntent(event.target.value as ComparisonIntent)}
                >
                  {comparisonIntentOptions.map((intent) => (
                    <option key={intent} value={intent}>
                      {formatComparisonIntentLabel(intent)}
                    </option>
                  ))}
                </select>
              </label>
              <button className="ghost-button" onClick={comparison.onSelectBenchmarkPair} type="button">
                Benchmark native vs NFI
              </button>
              <button
                className="ghost-button"
                disabled={!comparison.selectedRunIds.length}
                onClick={comparison.onClearSelection}
                type="button"
              >
                Clear compare
              </button>
              {comparison.historyBrowserOpen ? (
                <div className="comparison-history-browser">
                  <div className="comparison-history-browser-head">
                    <div>
                      <p className="comparison-history-browser-title">Comparison history browser</p>
                      <p className="comparison-history-browser-copy">
                        Jump directly to an earlier comparison step from this browser session.
                      </p>
                    </div>
                    <div className="comparison-history-browser-actions">
                      <button
                        className="ghost-button"
                        disabled={!comparison.canNavigateHistoryBackward}
                        onClick={() => comparison.onNavigateHistoryRelative(-1)}
                        type="button"
                      >
                        Back step
                      </button>
                      <button
                        className="ghost-button"
                        disabled={!comparison.canNavigateHistoryForward}
                        onClick={() => comparison.onNavigateHistoryRelative(1)}
                        type="button"
                      >
                        Forward step
                      </button>
                    </div>
                  </div>
                  {comparison.historyEntries.length ? (
                    <div className="comparison-history-browser-list">
                      {comparison.historyEntries.map((entry, index) => {
                        const isActive = entry.entryId === comparison.activeHistoryEntryId;
                        return (
                          <button
                            aria-current={isActive ? "step" : undefined}
                            className={`comparison-history-browser-entry ${
                              isActive ? "is-active" : ""
                            }`}
                            key={entry.entryId}
                            onClick={() => comparison.onNavigateHistoryEntry(entry.entryId)}
                            type="button"
                          >
                            <div className="comparison-history-browser-entry-head">
                              <span className="comparison-history-browser-entry-order">
                                Step {index + 1}
                              </span>
                              <span className="comparison-history-browser-entry-label">
                                {entry.label}
                              </span>
                              {isActive ? (
                                <span className="comparison-history-browser-entry-badge">
                                  Current
                                </span>
                              ) : null}
                            </div>
                            <p className="comparison-history-browser-entry-meta">
                              {formatComparisonHistoryPanelEntryMeta(entry)}
                            </p>
                            <p className="comparison-history-browser-entry-summary">
                              {entry.summary}
                            </p>
                          </button>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="comparison-history-browser-empty">
                      The current document session has not recorded comparison steps yet.
                    </p>
                  )}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
      {runs.length ? (
        <div className="run-list">
          {runs.map((run) => {
            const orderControls = getOrderControls ? getOrderControls(run) : null;
            return (
              <article className="run-card" key={run.config.run_id}>
              <div className="run-card-head">
                <div>
                  <strong>{run.config.strategy_id}</strong>
                  <span>
                    {run.config.symbols.join(", ")} / {run.config.strategy_version}
                  </span>
                </div>
                <div className={`run-status ${run.status}`}>{run.status}</div>
              </div>
              <div className="run-metrics">
                <Metric label="Mode" value={run.config.mode} />
                <Metric label="Lane" value={run.provenance.lane} />
                <Metric
                  label="Lifecycle"
                  value={run.provenance.strategy?.lifecycle.stage ?? "n/a"}
                />
                <Metric label="Version" value={run.config.strategy_version} />
                <Metric label="Return" value={formatMetric(run.metrics.total_return_pct, "%")} />
                <Metric label="Drawdown" value={formatMetric(run.metrics.max_drawdown_pct, "%")} />
                <Metric label="Win rate" value={formatMetric(run.metrics.win_rate_pct, "%")} />
                <Metric label="Trades" value={formatMetric(run.metrics.trade_count)} />
              </div>
              <ExperimentMetadataPills
                benchmarkFamily={run.provenance.experiment.benchmark_family}
                datasetIdentity={run.provenance.market_data?.dataset_identity}
                presetId={run.provenance.experiment.preset_id}
                tags={run.provenance.experiment.tags}
              />
              {run.provenance.strategy ? (
                <RunStrategySnapshot strategy={run.provenance.strategy} />
              ) : null}
              <p className="run-note">
                {run.provenance.reference_id
                  ? `Reference ${run.provenance.reference_id} (${run.provenance.reference_version ?? "unknown"})`
                  : run.notes[0] ?? "No notes recorded."}
              </p>
              {run.provenance.reference ? (
                <ReferenceRunProvenanceSummary
                  artifactPaths={run.provenance.artifact_paths}
                  benchmarkArtifacts={run.provenance.benchmark_artifacts}
                  externalCommand={run.provenance.external_command}
                  reference={run.provenance.reference}
                  referenceVersion={run.provenance.reference_version}
                  strategySemantics={run.provenance.strategy?.catalog_semantics}
                  workingDirectory={run.provenance.working_directory}
                />
              ) : null}
              {run.provenance.runtime_session ? (
                <RunRuntimeSessionSummary runtimeSession={run.provenance.runtime_session} />
              ) : null}
              {run.orders.length ? (
                <RunOrderLifecycleSummary orders={run.orders} orderControls={orderControls} />
              ) : null}
              {run.provenance.market_data ? (
                <RunMarketDataLineage
                  lineage={run.provenance.market_data}
                  lineageBySymbol={run.provenance.market_data_by_symbol}
                  rerunBoundaryId={run.provenance.rerun_boundary_id}
                  rerunBoundaryState={run.provenance.rerun_boundary_state}
                  rerunMatchStatus={run.provenance.rerun_match_status}
                  rerunSourceRunId={run.provenance.rerun_source_run_id}
                  rerunTargetBoundaryId={run.provenance.rerun_target_boundary_id}
                />
              ) : null}
              <div className="run-card-actions">
                {comparison ? (
                  <button
                    className="ghost-button"
                    onClick={() => comparison.onToggleRunSelection(run.config.run_id)}
                    type="button"
                  >
                    {comparison.selectedRunIds.includes(run.config.run_id)
                      ? "Remove from compare"
                      : "Add to compare"}
                  </button>
                ) : null}
                {rerunActions && run.provenance.rerun_boundary_id
                  ? rerunActions.map((action) => (
                    <button
                      className="ghost-button"
                      key={action.label}
                      onClick={() => void action.onRerun(run.provenance.rerun_boundary_id!)}
                      type="button"
                    >
                      {action.label}
                    </button>
                  ))
                  : null}
                {onStop && run.status === "running" ? (
                  <button className="ghost-button" onClick={() => void onStop(run.config.run_id)} type="button">
                    Stop
                  </button>
                ) : null}
              </div>
              </article>
            );
          })}
        </div>
      ) : (
        <p className="empty-state">No runs yet.</p>
      )}
      {comparison ? (
        <RunComparisonPanel
          comparison={comparison.payload}
          error={comparison.error}
          loading={comparison.loading}
          onChangeScoreLink={comparison.onChangeSelectedScoreLink}
          selectedScoreLink={comparison.selectedScoreLink}
          selectedRunIds={comparison.selectedRunIds}
        />
      ) : null}
    </section>
  );
}

function RunComparisonPanel({
  comparison,
  error,
  loading,
  onChangeScoreLink,
  selectedScoreLink,
  selectedRunIds,
}: {
  comparison: RunComparison | null;
  error: string | null;
  loading: boolean;
  onChangeScoreLink: (
    value: ComparisonScoreLinkTarget | null,
    historyMode?: ComparisonHistoryWriteMode,
  ) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  selectedRunIds: string[];
}) {
  if (!selectedRunIds.length) {
    return null;
  }

  if (selectedRunIds.length < 2) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Select at least two backtests to compare them side by side.</p>
      </section>
    );
  }

  if (loading) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Preparing side-by-side benchmark view...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="comparison-panel comparison-panel-empty">
        <p className="kicker">Comparison deck</p>
        <p className="empty-state">Comparison failed: {error}</p>
      </section>
    );
  }

  if (!comparison) {
    return null;
  }

  const [primaryNarrative, ...secondaryNarratives] = comparison.narratives;
  const tooltipScopeId = sanitizeComparisonTooltipId(useId());
  const tooltipTargetRefs = useRef(new Map<string, HTMLElement>());
  const tooltipBubbleRefs = useRef(new Map<string, HTMLSpanElement>());
  const narrativeCardRefs = useRef(new Map<string, HTMLElement>());
  const tooltipOpenTimerRef = useRef<number | null>(null);
  const tooltipCloseTimerRef = useRef<number | null>(null);
  const metricPointerSampleRef = useRef<{
    cellHeight: number;
    cellWidth: number;
    metricRowKey: string;
    runColumnKey: string;
    time: number;
    x: number;
    y: number;
  } | null>(null);
  const metricSweepStateRef = useRef<{
    axis: "column_down" | "column_up" | "row";
    contextKey: string;
    until: number;
  } | null>(null);
  const [activeTooltipId, setActiveTooltipId] = useState<string | null>(null);
  const [activeTooltipLayout, setActiveTooltipLayout] = useState<ComparisonTooltipLayout | null>(
    null,
  );
  const [dismissedTooltipId, setDismissedTooltipId] = useState<string | null>(null);
  const [tooltipTuning, setTooltipTuning] = useState<ComparisonTooltipTuning>(
    DEFAULT_COMPARISON_TOOLTIP_TUNING,
  );
  const [tooltipTuningPresets, setTooltipTuningPresets] = useState<
    Record<string, ComparisonTooltipTuning>
  >({});
  const [selectedTooltipPresetName, setSelectedTooltipPresetName] = useState("");
  const [tooltipPresetDraftName, setTooltipPresetDraftName] = useState("");
  const [pendingTooltipPresetImportConflict, setPendingTooltipPresetImportConflict] =
    useState<ComparisonTooltipPendingPresetImportConflict | null>(null);
  const [selectedScoreLinkSource, setSelectedScoreLinkSource] =
    useState<ComparisonScoreLinkSource | null>(null);
  const [tooltipShareDraft, setTooltipShareDraft] = useState("");
  const [tooltipShareFeedback, setTooltipShareFeedback] = useState<string | null>(null);
  const [hasHydratedTooltipTuningState, setHasHydratedTooltipTuningState] = useState(
    !SHOW_COMPARISON_TOOLTIP_TUNING_PANEL,
  );
  const intentClassName = getComparisonIntentClassName(comparison.intent);
  const intentTooltip = formatComparisonIntentTooltip(comparison.intent);
  const baselineTooltip = formatComparisonCueTooltip(comparison.intent, "baseline");
  const bestTooltip = formatComparisonCueTooltip(comparison.intent, "best");
  const insightTooltip = formatComparisonCueTooltip(comparison.intent, "insight");
  const intentChipTooltipId = buildComparisonTooltipId(tooltipScopeId, "intent-chip");
  const legendModeTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-mode");
  const legendBaselineTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-baseline");
  const legendBestTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-best");
  const legendInsightTooltipId = buildComparisonTooltipId(tooltipScopeId, "legend-insight");
  const baselineRunTooltipId = buildComparisonTooltipId(
    tooltipScopeId,
    "baseline-run",
    comparison.baseline_run_id,
  );
  const topInsightTooltipId = buildComparisonTooltipId(tooltipScopeId, "top-insight");
  const featuredNarrativeTooltipId = primaryNarrative
    ? buildComparisonTooltipId(tooltipScopeId, "featured-narrative", primaryNarrative.run_id)
    : undefined;
  const metricTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.metric_hover_close_ms,
    hoverOpenDelayMs: tooltipTuning.metric_hover_open_ms,
  };
  const metricRowSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.row_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.row_sweep_open_ms,
  };
  const metricColumnDownSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.column_down_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.column_down_sweep_open_ms,
  };
  const metricColumnUpSweepTooltipInteraction: ComparisonTooltipInteractionOptions = {
    hoverCloseDelayMs: tooltipTuning.column_up_sweep_close_ms,
    hoverOpenDelayMs: tooltipTuning.column_up_sweep_open_ms,
  };
  const selectedTooltipPreset = selectedTooltipPresetName
    ? tooltipTuningPresets[selectedTooltipPresetName] ?? null
    : null;
  const createTooltipTuningPresetState = (): ComparisonTooltipTuningPresetStateV1 => ({
    current_tuning: { ...tooltipTuning },
    presets: cloneComparisonTooltipPresetMap(tooltipTuningPresets),
    selected_preset_name: selectedTooltipPresetName || null,
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  });
  const tooltipShareUrl = useMemo(
    () => buildComparisonTooltipTuningShareUrl(createTooltipTuningPresetState()),
    [selectedTooltipPresetName, tooltipTuning, tooltipTuningPresets],
  );
  const selectedTooltipPresetShareUrl = useMemo(() => {
    if (!selectedTooltipPresetName || !selectedTooltipPreset) {
      return "";
    }
    return buildComparisonTooltipTuningShareUrl(
      createComparisonTooltipTuningSinglePresetShare(
        selectedTooltipPresetName,
        selectedTooltipPreset,
      ),
    );
  }, [selectedTooltipPreset, selectedTooltipPresetName]);

  const applyTooltipTuningPresetState = (state: ComparisonTooltipTuningPresetStateV1) => {
    setTooltipTuning({ ...state.current_tuning });
    setTooltipTuningPresets(cloneComparisonTooltipPresetMap(state.presets));
    const nextSelectedPresetName = state.selected_preset_name ?? "";
    setSelectedTooltipPresetName(nextSelectedPresetName);
    setTooltipPresetDraftName(nextSelectedPresetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const updateTooltipShareDraft = (value: string) => {
    setTooltipShareDraft(value);
    setPendingTooltipPresetImportConflict(null);
  };

  const applySingleTooltipPresetImport = (
    importedPresetName: string,
    tuning: ComparisonTooltipTuning,
    options?: {
      policy?: ComparisonTooltipPresetImportConflictPolicy;
      renamedPresetName?: string;
      verb?: "Imported" | "Loaded";
    },
  ) => {
    const mergedPreset = mergeComparisonTooltipSinglePresetIntoState(
      createTooltipTuningPresetState(),
      importedPresetName,
      tuning,
      options?.policy ?? "overwrite",
      options?.renamedPresetName,
    );
    applyTooltipTuningPresetState(mergedPreset.state);
    setTooltipShareDraft(
      JSON.stringify(
        createComparisonTooltipTuningSinglePresetShare(
          mergedPreset.resolution.final_preset_name,
          tuning,
        ),
        null,
        2,
      ),
    );
    setTooltipShareFeedback(
      formatComparisonTooltipPresetImportFeedback(mergedPreset.resolution, {
        verb: options?.verb,
      }),
    );
  };

  const beginPendingTooltipPresetImportConflict = (
    importedShare: Extract<ComparisonTooltipTuningShareImport, { kind: "preset" }>,
  ) => {
    setPendingTooltipPresetImportConflict({
      imported_preset_name: importedShare.preset_name,
      proposed_preset_name: createAvailableComparisonTooltipPresetName(
        tooltipTuningPresets,
        importedShare.preset_name,
      ),
      raw: importedShare.raw,
      tuning: importedShare.tuning,
    });
    setTooltipShareDraft(importedShare.raw);
    setTooltipShareFeedback(
      `Preset "${importedShare.preset_name}" already exists. Choose rename, overwrite, or skip.`,
    );
  };

  const updateTooltipTuning = (
    key: keyof ComparisonTooltipTuning,
    rawValue: string,
  ) => {
    const nextValue = Number(rawValue);
    if (!Number.isFinite(nextValue)) {
      return;
    }
    setTooltipTuning((current) => ({
      ...current,
      [key]: nextValue,
    }));
    setSelectedTooltipPresetName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const exportTooltipPresetBundle = () => {
    const nextState = createTooltipTuningPresetState();
    setTooltipShareDraft(JSON.stringify(nextState, null, 2));
    setTooltipShareFeedback(
      `Exported current tuning with ${Object.keys(nextState.presets).length} saved preset(s).`,
    );
    setPendingTooltipPresetImportConflict(null);
  };

  const exportSelectedTooltipPreset = () => {
    if (!selectedTooltipPresetName || !selectedTooltipPreset) {
      setTooltipShareFeedback("Select a saved preset to export a single named preset.");
      return;
    }
    const presetShare = createComparisonTooltipTuningSinglePresetShare(
      selectedTooltipPresetName,
      selectedTooltipPreset,
    );
    setTooltipShareDraft(JSON.stringify(presetShare, null, 2));
    setTooltipShareFeedback(`Exported preset "${selectedTooltipPresetName}".`);
    setPendingTooltipPresetImportConflict(null);
  };

  const importTooltipPresetBundle = () => {
    const importedShare = parseComparisonTooltipTuningShareImport(tooltipShareDraft);
    if (!importedShare) {
      setTooltipShareFeedback(
        "Import failed. Provide valid tooltip tuning JSON for a bundle or named preset.",
      );
      return;
    }
    if (importedShare.kind === "bundle") {
      applyTooltipTuningPresetState(importedShare.state);
      setTooltipShareDraft(importedShare.raw);
      setTooltipShareFeedback(
        `Imported current tuning with ${Object.keys(importedShare.state.presets).length} saved preset(s).`,
      );
      return;
    }
    if (tooltipTuningPresets[importedShare.preset_name]) {
      beginPendingTooltipPresetImportConflict(importedShare);
      return;
    }
    applySingleTooltipPresetImport(importedShare.preset_name, importedShare.tuning, {
      policy: "overwrite",
    });
  };

  const updatePendingTooltipPresetImportName = (value: string) => {
    setPendingTooltipPresetImportConflict((current) =>
      current
        ? {
            ...current,
            proposed_preset_name: value,
          }
        : current,
    );
  };

  const resolvePendingTooltipPresetImportConflict = (
    action: "overwrite" | "rename" | "skip",
  ) => {
    if (!pendingTooltipPresetImportConflict) {
      return;
    }
    if (action === "skip") {
      setPendingTooltipPresetImportConflict(null);
      setTooltipShareFeedback(
        `Skipped importing preset "${pendingTooltipPresetImportConflict.imported_preset_name}".`,
      );
      return;
    }
    if (action === "overwrite") {
      applySingleTooltipPresetImport(
        pendingTooltipPresetImportConflict.imported_preset_name,
        pendingTooltipPresetImportConflict.tuning,
        { policy: "overwrite" },
      );
      return;
    }
    const renamedPresetName = pendingTooltipPresetImportConflict.proposed_preset_name.trim();
    if (!renamedPresetName) {
      setTooltipShareFeedback("Enter a new preset name before importing with rename.");
      return;
    }
    if (tooltipTuningPresets[renamedPresetName]) {
      setTooltipShareFeedback(
        `Preset "${renamedPresetName}" already exists. Choose a different rename target.`,
      );
      return;
    }
    applySingleTooltipPresetImport(
      pendingTooltipPresetImportConflict.imported_preset_name,
      pendingTooltipPresetImportConflict.tuning,
      {
        policy: "rename",
        renamedPresetName,
      },
    );
  };

  const copyTooltipShareUrl = async () => {
    if (!navigator.clipboard?.writeText) {
      setTooltipShareFeedback("Clipboard is unavailable. Copy the share URL from the field.");
      return;
    }
    try {
      await navigator.clipboard.writeText(tooltipShareUrl);
      setTooltipShareFeedback("Copied a share URL for the current tooltip tuning bundle.");
    } catch {
      setTooltipShareFeedback("Clipboard copy failed. Copy the share URL from the field.");
    }
  };

  const copySelectedTooltipPresetShareUrl = async () => {
    if (!selectedTooltipPresetName || !selectedTooltipPresetShareUrl) {
      setTooltipShareFeedback("Select a saved preset to share a single preset URL.");
      return;
    }
    if (!navigator.clipboard?.writeText) {
      setTooltipShareFeedback(
        "Clipboard is unavailable. Copy the selected preset URL from the field.",
      );
      return;
    }
    try {
      await navigator.clipboard.writeText(selectedTooltipPresetShareUrl);
      setTooltipShareFeedback(`Copied a share URL for preset "${selectedTooltipPresetName}".`);
    } catch {
      setTooltipShareFeedback("Clipboard copy failed. Copy the selected preset URL from the field.");
    }
  };

  const saveTooltipPreset = () => {
    const presetName = tooltipPresetDraftName.trim();
    if (!presetName) {
      return;
    }
    setTooltipTuningPresets((current) => ({
      ...current,
      [presetName]: { ...tooltipTuning },
    }));
    setSelectedTooltipPresetName(presetName);
    setTooltipPresetDraftName(presetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const loadTooltipPreset = (presetName: string) => {
    if (!presetName) {
      setSelectedTooltipPresetName("");
      return;
    }
    const preset = tooltipTuningPresets[presetName];
    if (!preset) {
      return;
    }
    setTooltipTuning({ ...preset });
    setSelectedTooltipPresetName(presetName);
    setTooltipPresetDraftName(presetName);
    setPendingTooltipPresetImportConflict(null);
  };

  const deleteTooltipPreset = () => {
    if (!selectedTooltipPresetName) {
      return;
    }
    setTooltipTuningPresets((current) => {
      const next = { ...current };
      delete next[selectedTooltipPresetName];
      return next;
    });
    setSelectedTooltipPresetName("");
    setTooltipPresetDraftName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const resetTooltipTuning = () => {
    setTooltipTuning(DEFAULT_COMPARISON_TOOLTIP_TUNING);
    setSelectedTooltipPresetName("");
    setPendingTooltipPresetImportConflict(null);
  };

  const clearComparisonTooltipOpenTimer = () => {
    if (tooltipOpenTimerRef.current !== null) {
      window.clearTimeout(tooltipOpenTimerRef.current);
      tooltipOpenTimerRef.current = null;
    }
  };

  const clearComparisonTooltipCloseTimer = () => {
    if (tooltipCloseTimerRef.current !== null) {
      window.clearTimeout(tooltipCloseTimerRef.current);
      tooltipCloseTimerRef.current = null;
    }
  };

  const clearComparisonTooltipTimers = () => {
    clearComparisonTooltipOpenTimer();
    clearComparisonTooltipCloseTimer();
  };

  const showComparisonTooltip = (tooltipId: string) => {
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipId(tooltipId);
  };

  const hideComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setDismissedTooltipId((current) => (current === tooltipId ? null : current));
  };

  const dismissComparisonTooltip = (tooltipId: string) => {
    setActiveTooltipId((current) => (current === tooltipId ? null : current));
    setActiveTooltipLayout((current) => (current?.tooltipId === tooltipId ? null : current));
    setDismissedTooltipId(tooltipId);
  };

  const scheduleComparisonTooltipShow = (
    tooltipId: string,
    options?: ComparisonTooltipInteractionOptions,
  ) => {
    clearComparisonTooltipCloseTimer();
    const delayMs = options?.hoverOpenDelayMs ?? 0;
    if (delayMs <= 0) {
      clearComparisonTooltipOpenTimer();
      showComparisonTooltip(tooltipId);
      return;
    }
    clearComparisonTooltipOpenTimer();
    tooltipOpenTimerRef.current = window.setTimeout(() => {
      tooltipOpenTimerRef.current = null;
      showComparisonTooltip(tooltipId);
    }, delayMs);
  };

  const scheduleComparisonTooltipHide = (
    tooltipId: string,
    options?: ComparisonTooltipInteractionOptions,
  ) => {
    clearComparisonTooltipOpenTimer();
    const delayMs = options?.hoverCloseDelayMs ?? 0;
    if (delayMs <= 0) {
      clearComparisonTooltipCloseTimer();
      hideComparisonTooltip(tooltipId);
      return;
    }
    clearComparisonTooltipCloseTimer();
    tooltipCloseTimerRef.current = window.setTimeout(() => {
      tooltipCloseTimerRef.current = null;
      hideComparisonTooltip(tooltipId);
    }, delayMs);
  };

  const registerComparisonTooltipTargetRef = (tooltipId?: string) => (node: HTMLElement | null) => {
    if (!tooltipId) {
      return;
    }
    if (node) {
      tooltipTargetRefs.current.set(tooltipId, node);
      return;
    }
    tooltipTargetRefs.current.delete(tooltipId);
  };

  const registerComparisonTooltipBubbleRef =
    (tooltipId: string) => (node: HTMLSpanElement | null) => {
      if (node) {
        tooltipBubbleRefs.current.set(tooltipId, node);
        return;
      }
      tooltipBubbleRefs.current.delete(tooltipId);
    };

  const registerComparisonNarrativeCardRef =
    (runId: string) => (node: HTMLElement | null) => {
      if (node) {
        narrativeCardRefs.current.set(runId, node);
        return;
      }
      narrativeCardRefs.current.delete(runId);
    };

  const updateSelectedScoreLink = (
    nextSelection: ComparisonScoreLinkTarget | null,
    source: ComparisonScoreLinkSource | null,
  ) => {
    onChangeScoreLink(nextSelection, source ? "push" : "replace");
    setSelectedScoreLinkSource(nextSelection ? source : null);
  };

  const handleComparisonScoreDrillBack = (
    runId: string,
    section: ComparisonScoreSection,
    componentKey: string,
    source: ComparisonScoreLinkSource,
  ) => {
    const nextSelection = resolveComparisonScoreDrillBackTarget(
      comparison,
      selectedScoreLink,
      runId,
      section,
      componentKey,
    );
    if (!nextSelection) {
      return;
    }
    const isSameSelection =
      selectedScoreLink?.narrativeRunId === nextSelection.narrativeRunId
      && selectedScoreLink.section === nextSelection.section
      && selectedScoreLink.componentKey === nextSelection.componentKey;
    updateSelectedScoreLink(isSameSelection ? null : nextSelection, source);
  };

  const getComparisonTooltipTargetProps = (
    tooltipId?: string,
    options?: ComparisonTooltipInteractionOptions,
  ): ComparisonTooltipTargetProps | undefined => {
    if (!tooltipId) {
      return undefined;
    }

    return {
      "aria-describedby": dismissedTooltipId === tooltipId ? undefined : tooltipId,
      "data-tooltip-visible":
        activeTooltipId === tooltipId && dismissedTooltipId !== tooltipId ? "true" : "false",
      onBlur: () => {
        clearComparisonTooltipTimers();
        hideComparisonTooltip(tooltipId);
      },
      onFocus: () => {
        clearComparisonTooltipTimers();
        showComparisonTooltip(tooltipId);
      },
      onKeyDown: (event: KeyboardEvent<HTMLElement>) => {
        if (event.key === "Escape") {
          clearComparisonTooltipTimers();
          dismissComparisonTooltip(tooltipId);
          event.stopPropagation();
        }
      },
      onMouseEnter: () => scheduleComparisonTooltipShow(tooltipId, options),
      onMouseLeave: () => scheduleComparisonTooltipHide(tooltipId, options),
    };
  };

  const recordMetricPointerSample = (
    event: MouseEvent<HTMLElement>,
    metricRowKey: string,
    runColumnKey: string,
  ) => {
    const cellRect = event.currentTarget.getBoundingClientRect();
    metricPointerSampleRef.current = {
      cellHeight: cellRect.height,
      cellWidth: cellRect.width,
      metricRowKey,
      runColumnKey,
      time: event.timeStamp,
      x: event.clientX,
      y: event.clientY,
    };
  };

  const resolveMetricTooltipInteraction = (
    event: MouseEvent<HTMLElement>,
    metricRowKey: string,
    runColumnKey: string,
  ) => {
    const cellRect = event.currentTarget.getBoundingClientRect();
    const sample = {
      cellHeight: cellRect.height,
      cellWidth: cellRect.width,
      metricRowKey,
      runColumnKey,
      time: event.timeStamp,
      x: event.clientX,
      y: event.clientY,
    };
    const previousSample = metricPointerSampleRef.current;
    metricPointerSampleRef.current = sample;

    if (!previousSample) {
      return metricTooltipInteraction;
    }

    const deltaTime = Math.max(sample.time - previousSample.time, 1);
    const deltaX = Math.abs(sample.x - previousSample.x);
    const deltaY = Math.abs(sample.y - previousSample.y);
    const signedDeltaY = sample.y - previousSample.y;
    const horizontalVelocity = deltaX / deltaTime;
    const verticalVelocity = deltaY / deltaTime;
    const pointerSpeed = Math.hypot(deltaX, deltaY) / deltaTime;
    const averageCellWidth = (sample.cellWidth + previousSample.cellWidth) / 2;
    const averageCellHeight = (sample.cellHeight + previousSample.cellHeight) / 2;
    const sweepTimeThreshold = getAdaptiveMetricSweepTimeThreshold(pointerSpeed, tooltipTuning);
    const horizontalDistanceThreshold = getAdaptiveMetricSweepDistanceThreshold(
      averageCellWidth,
      pointerSpeed,
      "horizontal",
      tooltipTuning,
    );
    const verticalDistanceThreshold = getAdaptiveMetricSweepDistanceThreshold(
      averageCellHeight,
      pointerSpeed,
      "vertical",
      tooltipTuning,
    );
    const isSameMetricRow = previousSample.metricRowKey === metricRowKey;
    const isSameRunColumn = previousSample.runColumnKey === runColumnKey;
    const isHorizontalSweep =
      isSameMetricRow &&
      deltaTime <= sweepTimeThreshold &&
      deltaX >= horizontalDistanceThreshold &&
      deltaX >= deltaY * 2 &&
      horizontalVelocity >= tooltipTuning.horizontal_velocity_threshold;
    const isVerticalSweep =
      isSameRunColumn &&
      deltaTime <= sweepTimeThreshold &&
      deltaY >= verticalDistanceThreshold &&
      deltaY >= deltaX * 2 &&
      verticalVelocity >= tooltipTuning.vertical_velocity_threshold;
    const columnSweepAxis = signedDeltaY >= 0 ? "column_down" : "column_up";

    if (isHorizontalSweep) {
      metricSweepStateRef.current = {
        axis: "row",
        contextKey: metricRowKey,
        until: sample.time + tooltipTuning.row_sweep_hold_ms,
      };
      return metricRowSweepTooltipInteraction;
    }

    if (isVerticalSweep) {
      metricSweepStateRef.current = {
        axis: columnSweepAxis,
        contextKey: runColumnKey,
        until:
          sample.time +
          (columnSweepAxis === "column_down"
            ? tooltipTuning.column_down_sweep_hold_ms
            : tooltipTuning.column_up_sweep_hold_ms),
      };
      return columnSweepAxis === "column_down"
        ? metricColumnDownSweepTooltipInteraction
        : metricColumnUpSweepTooltipInteraction;
    }

    if (
      metricSweepStateRef.current &&
      sample.time < metricSweepStateRef.current.until
    ) {
      if (
        metricSweepStateRef.current.axis === "row" &&
        metricSweepStateRef.current.contextKey === metricRowKey
      ) {
        return metricRowSweepTooltipInteraction;
      }
      if (
        (metricSweepStateRef.current.axis === "column_down" ||
          metricSweepStateRef.current.axis === "column_up") &&
        metricSweepStateRef.current.contextKey === runColumnKey
      ) {
        return metricSweepStateRef.current.axis === "column_down"
          ? metricColumnDownSweepTooltipInteraction
          : metricColumnUpSweepTooltipInteraction;
      }
    }

    if (
      (!isSameMetricRow && metricSweepStateRef.current?.axis === "row") ||
      (!isSameRunColumn &&
        (metricSweepStateRef.current?.axis === "column_down" ||
          metricSweepStateRef.current?.axis === "column_up"))
    ) {
      metricSweepStateRef.current = null;
    }

    return metricTooltipInteraction;
  };

  const getMetricComparisonTooltipTargetProps = (
    tooltipId?: string,
    metricRowKey?: string,
    runColumnKey?: string,
  ): ComparisonTooltipTargetProps | undefined => {
    const baseProps = getComparisonTooltipTargetProps(tooltipId, metricTooltipInteraction);

    if (!baseProps || !tooltipId || !metricRowKey || !runColumnKey) {
      return baseProps;
    }

    return {
      ...baseProps,
      onMouseEnter: (event: MouseEvent<HTMLElement>) => {
        const interaction = resolveMetricTooltipInteraction(event, metricRowKey, runColumnKey);
        scheduleComparisonTooltipShow(tooltipId, interaction);
      },
      onMouseLeave: (event: MouseEvent<HTMLElement>) => {
        recordMetricPointerSample(event, metricRowKey, runColumnKey);
        scheduleComparisonTooltipHide(tooltipId, metricTooltipInteraction);
      },
      onMouseMove: (event: MouseEvent<HTMLElement>) =>
        recordMetricPointerSample(event, metricRowKey, runColumnKey),
    };
  };

  useEffect(() => clearComparisonTooltipTimers, []);

  useEffect(() => {
    if (!SHOW_COMPARISON_TOOLTIP_TUNING_PANEL) {
      return;
    }
    const storedState = loadComparisonTooltipTuningPresetState();
    const sharedImport = loadComparisonTooltipTuningShareImportFromUrl();
    const appliedImport = sharedImport
      ? applyComparisonTooltipTuningShareImport(
          storedState,
          sharedImport,
          DEFAULT_COMPARISON_TOOLTIP_PRESET_IMPORT_CONFLICT_POLICY,
        )
      : null;
    applyTooltipTuningPresetState(appliedImport?.state ?? storedState);
    if (sharedImport) {
      if (appliedImport?.kind === "preset" && sharedImport.kind === "preset") {
        setTooltipShareDraft(
          JSON.stringify(
            createComparisonTooltipTuningSinglePresetShare(
              appliedImport.resolution.final_preset_name,
              sharedImport.tuning,
            ),
            null,
            2,
          ),
        );
        setTooltipShareFeedback(
          formatComparisonTooltipPresetImportFeedback(appliedImport.resolution, {
            verb: "Loaded",
          }),
        );
      } else {
        setTooltipShareDraft(sharedImport.raw);
        setTooltipShareFeedback(
          sharedImport.kind === "bundle"
            ? "Loaded tooltip tuning presets from the share URL."
            : `Loaded preset "${sharedImport.preset_name}" from the share URL.`,
        );
      }
    }
    setHasHydratedTooltipTuningState(true);
  }, []);

  useEffect(() => {
    if (!SHOW_COMPARISON_TOOLTIP_TUNING_PANEL || !hasHydratedTooltipTuningState) {
      return;
    }
    persistComparisonTooltipTuningPresetState({
      current_tuning: tooltipTuning,
      presets: tooltipTuningPresets,
      selected_preset_name: selectedTooltipPresetName || null,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    });
  }, [
    hasHydratedTooltipTuningState,
    selectedTooltipPresetName,
    tooltipTuning,
    tooltipTuningPresets,
  ]);

  useLayoutEffect(() => {
    if (!activeTooltipId) {
      setActiveTooltipLayout(null);
      return;
    }

    const updateTooltipLayout = () => {
      const target = tooltipTargetRefs.current.get(activeTooltipId);
      const bubble = tooltipBubbleRefs.current.get(activeTooltipId);

      if (!target || !bubble) {
        setActiveTooltipLayout(null);
        return;
      }

      const viewportPadding = 16;
      const boundaryPadding = 12;
      const gap = 14;
      const targetRect = target.getBoundingClientRect();
      const boundaryRect = getComparisonTooltipBoundaryRect(target);
      const minLeft = Math.max(
        viewportPadding,
        boundaryRect ? boundaryRect.left + boundaryPadding : viewportPadding,
      );
      const maxRight = Math.min(
        window.innerWidth - viewportPadding,
        boundaryRect ? boundaryRect.right - boundaryPadding : window.innerWidth - viewportPadding,
      );
      const availableWidth = Math.max(180, maxRight - minLeft);
      bubble.style.maxWidth = `${availableWidth}px`;
      const bubbleRect = bubble.getBoundingClientRect();
      const bubbleWidth = Math.min(bubbleRect.width, availableWidth);
      const preferredLeft = targetRect.left + targetRect.width / 2 - bubbleWidth / 2;
      const maxLeft = Math.max(minLeft, maxRight - bubbleWidth);
      const left = clampComparisonNumber(preferredLeft, minLeft, maxLeft);
      const spaceBelow = window.innerHeight - viewportPadding - (targetRect.bottom + gap);
      const spaceAbove = targetRect.top - viewportPadding - gap;
      const side =
        spaceBelow >= bubbleRect.height || spaceBelow >= spaceAbove ? "bottom" : "top";
      const top =
        side === "bottom"
          ? Math.min(targetRect.bottom + gap, window.innerHeight - viewportPadding - bubbleRect.height)
          : Math.max(viewportPadding, targetRect.top - gap - bubbleRect.height);
      const targetCenter = targetRect.left + targetRect.width / 2;
      const arrowLeft = clampComparisonNumber(targetCenter - left, 18, bubbleWidth - 18);

      setActiveTooltipLayout({
        arrowLeft,
        left,
        maxWidth: availableWidth,
        side,
        tooltipId: activeTooltipId,
        top,
      });
    };

    updateTooltipLayout();
    window.addEventListener("resize", updateTooltipLayout);
    window.addEventListener("scroll", updateTooltipLayout, true);
    return () => {
      window.removeEventListener("resize", updateTooltipLayout);
      window.removeEventListener("scroll", updateTooltipLayout, true);
    };
  }, [activeTooltipId]);

  useEffect(() => {
    if (!selectedScoreLink) {
      return;
    }

    const narrative = comparison.narratives.find(
      (candidate) => candidate.run_id === selectedScoreLink.narrativeRunId,
    );
    if (!narrative) {
      updateSelectedScoreLink(null, null);
      return;
    }

    const sectionBreakdown = narrative.score_breakdown[selectedScoreLink.section];
    if (!(selectedScoreLink.componentKey in sectionBreakdown.components)) {
      updateSelectedScoreLink(null, null);
    }
  }, [comparison, selectedScoreLink]);

  useEffect(() => {
    if (!selectedScoreLink || selectedScoreLinkSource === "narrative") {
      return;
    }
    const narrativeCard = narrativeCardRefs.current.get(selectedScoreLink.narrativeRunId);
    if (!narrativeCard) {
      return;
    }
    narrativeCard.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }, [selectedScoreLink, selectedScoreLinkSource]);

  return (
    <section className={`comparison-panel ${intentClassName}`}>
      <div className="comparison-head">
        <div>
          <p className="kicker comparison-mode-kicker">
            <span aria-hidden="true" className="comparison-intent-icon" />
            <span>Comparison deck</span>
          </p>
          <h3>Native and reference backtests, side by side</h3>
        </div>
        <p className="comparison-baseline">
          <span>Baseline: {comparison.baseline_run_id}</span>
          <span
            className="comparison-intent-chip comparison-cue comparison-tooltip"
            ref={registerComparisonTooltipTargetRef(intentChipTooltipId)}
            tabIndex={0}
            {...getComparisonTooltipTargetProps(intentChipTooltipId)}
          >
            <span aria-hidden="true" className="comparison-intent-icon" />
            <span>{formatComparisonIntentLabel(comparison.intent)}</span>
            <ComparisonTooltipBubble
              id={intentChipTooltipId}
              layout={
                activeTooltipLayout?.tooltipId === intentChipTooltipId ? activeTooltipLayout : null
              }
              ref={registerComparisonTooltipBubbleRef(intentChipTooltipId)}
              text={intentTooltip}
            />
          </span>
        </p>
      </div>
      <div aria-label="Comparison legend" className="comparison-legend">
        <span
          className="comparison-legend-item comparison-legend-item-mode comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendModeTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendModeTooltipId)}
        >
          <span aria-hidden="true" className="comparison-intent-icon" />
          <span>{formatComparisonIntentLegend(comparison.intent)}</span>
          <ComparisonTooltipBubble
            id={legendModeTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendModeTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendModeTooltipId)}
            text={intentTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendBaselineTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendBaselineTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch baseline" />
          <span>Baseline run</span>
          <ComparisonTooltipBubble
            id={legendBaselineTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendBaselineTooltipId
                ? activeTooltipLayout
                : null
            }
            ref={registerComparisonTooltipBubbleRef(legendBaselineTooltipId)}
            text={baselineTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendBestTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendBestTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch best" />
          <span>Best metric</span>
          <ComparisonTooltipBubble
            id={legendBestTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendBestTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendBestTooltipId)}
            text={bestTooltip}
          />
        </span>
        <span
          className="comparison-legend-item comparison-cue comparison-tooltip"
          ref={registerComparisonTooltipTargetRef(legendInsightTooltipId)}
          tabIndex={0}
          {...getComparisonTooltipTargetProps(legendInsightTooltipId)}
        >
          <span aria-hidden="true" className="comparison-legend-swatch insight" />
          <span>Top insight</span>
          <ComparisonTooltipBubble
            id={legendInsightTooltipId}
            layout={
              activeTooltipLayout?.tooltipId === legendInsightTooltipId ? activeTooltipLayout : null
            }
            ref={registerComparisonTooltipBubbleRef(legendInsightTooltipId)}
            text={insightTooltip}
          />
        </span>
      </div>
      {SHOW_COMPARISON_TOOLTIP_TUNING_PANEL ? (
        <ComparisonTooltipTuningPanel
          onChangePendingPresetImportName={updatePendingTooltipPresetImportName}
          onChangePresetDraftName={setTooltipPresetDraftName}
          onChangeShareDraft={updateTooltipShareDraft}
          onChangeValue={updateTooltipTuning}
          onCopyShareUrl={copyTooltipShareUrl}
          onCopySelectedPresetShareUrl={copySelectedTooltipPresetShareUrl}
          onDeletePreset={deleteTooltipPreset}
          onExportJson={exportTooltipPresetBundle}
          onExportSelectedPresetJson={exportSelectedTooltipPreset}
          onImportJson={importTooltipPresetBundle}
          onLoadPreset={loadTooltipPreset}
          onResolvePendingPresetImportConflict={resolvePendingTooltipPresetImportConflict}
          onReset={resetTooltipTuning}
          onSavePreset={saveTooltipPreset}
          onSetShareFeedback={setTooltipShareFeedback}
          pendingPresetImportConflict={pendingTooltipPresetImportConflict}
          presetDraftName={tooltipPresetDraftName}
          presets={tooltipTuningPresets}
          shareDraft={tooltipShareDraft}
          shareFeedback={tooltipShareFeedback}
          shareUrl={tooltipShareUrl}
          selectedPresetShareUrl={selectedTooltipPresetShareUrl}
          selectedPresetName={selectedTooltipPresetName}
          tuning={tooltipTuning}
        />
      ) : null}
      <div className="comparison-run-grid">
        {comparison.runs.map((run) => {
          const linkedRunRole = getComparisonScoreLinkedRunRole(
            selectedScoreLink,
            comparison.baseline_run_id,
            run.run_id,
          );
          const linkedSelection = linkedRunRole ? selectedScoreLink : null;
          const highlightStatus =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["status_bonus"], "context");
          const highlightStrategyKind =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["strategy_kind", "vocabulary"], "semantics");
          const highlightExecutionModel =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["execution_model", "vocabulary"], "semantics");
          const highlightParameterContract =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["parameter_contract", "vocabulary"], "semantics");
          const highlightSourceDescriptor =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, [
              "source_descriptor",
              "vocabulary",
              "native_reference_bonus",
              "reference_bonus",
              "reference_floor",
            ]);
          const highlightOperatorNotes =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, ["vocabulary"], "semantics");
          const highlightReferenceBadge =
            Boolean(linkedSelection)
            && isComparisonScoreLinkMatch(linkedSelection, [
              "source_descriptor",
              "provenance_richness",
              "native_reference_bonus",
              "reference_bonus",
              "reference_floor",
              "benchmark_story_bonus",
            ]);

          return (
            <article
              className={`comparison-run-card ${
                run.run_id === comparison.baseline_run_id
                  ? "baseline comparison-cue-card comparison-tooltip"
                  : ""
              } ${linkedRunRole ? "is-linked" : ""} ${
                linkedRunRole === "target" ? "is-linked-target" : ""
              } ${linkedRunRole === "baseline" ? "is-linked-baseline" : ""}`.trim()}
              key={run.run_id}
              ref={
                run.run_id === comparison.baseline_run_id
                  ? registerComparisonTooltipTargetRef(baselineRunTooltipId)
                  : undefined
              }
              tabIndex={run.run_id === comparison.baseline_run_id ? 0 : undefined}
              {...(run.run_id === comparison.baseline_run_id
                ? getComparisonTooltipTargetProps(baselineRunTooltipId)
                : {})}
            >
              <div className="comparison-run-head">
                <strong>{run.strategy_name ?? run.strategy_id}</strong>
                <div className={`run-status ${run.status} ${highlightStatus ? "comparison-linked-badge" : ""}`}>
                  {run.status}
                </div>
              </div>
              <div className="strategy-badges">
                <span className="meta-pill">{run.lane}</span>
                <span className="meta-pill subtle">{run.strategy_version}</span>
                {run.catalog_semantics.strategy_kind ? (
                  <span
                    className={`meta-pill subtle ${highlightStrategyKind ? "comparison-linked-badge" : ""}`}
                  >
                    {run.catalog_semantics.strategy_kind}
                  </span>
                ) : null}
                {run.reference_id ? (
                  <span
                    className={`meta-pill subtle ${highlightReferenceBadge ? "comparison-linked-badge" : ""}`}
                  >
                    {run.reference_id}
                  </span>
                ) : null}
              </div>
              <p className="run-note">
                {run.strategy_id} / {run.symbols.join(", ")} / {run.timeframe}
              </p>
              {run.catalog_semantics.execution_model ? (
                <p className={`run-note ${highlightExecutionModel ? "comparison-linked-copy" : ""}`}>
                  Execution model: {run.catalog_semantics.execution_model}
                </p>
              ) : null}
              {run.catalog_semantics.parameter_contract ? (
                <p className={`run-note ${highlightParameterContract ? "comparison-linked-copy" : ""}`}>
                  Parameter contract: {run.catalog_semantics.parameter_contract}
                </p>
              ) : null}
              {run.catalog_semantics.source_descriptor ? (
                <p className={`run-note ${highlightSourceDescriptor ? "comparison-linked-copy" : ""}`}>
                  Semantic source: {run.catalog_semantics.source_descriptor}
                </p>
              ) : null}
              {run.catalog_semantics.operator_notes.length ? (
                <p className={`run-note ${highlightOperatorNotes ? "comparison-linked-copy" : ""}`}>
                  Operator notes: {run.catalog_semantics.operator_notes.join(" | ")}
                </p>
              ) : null}
              <ExperimentMetadataPills
                benchmarkFamily={run.experiment.benchmark_family}
                datasetIdentity={run.dataset_identity}
                presetId={run.experiment.preset_id}
                tags={run.experiment.tags}
              />
              <p className="run-note">
                Started {formatTimestamp(run.started_at)}
                {run.ended_at ? ` / Ended ${formatTimestamp(run.ended_at)}` : ""}
              </p>
              {run.reference ? (
                <ReferenceRunProvenanceSummary
                  artifactPaths={run.artifact_paths}
                  benchmarkArtifacts={run.benchmark_artifacts}
                  externalCommand={run.external_command}
                  linkedScore={
                    linkedSelection && linkedRunRole && linkedSelection.section !== "metrics"
                      ? {
                          ...linkedSelection,
                          role: linkedRunRole,
                        }
                      : null
                  }
                  onDrillBackScoreLink={(section, componentKey) =>
                    handleComparisonScoreDrillBack(
                      run.run_id,
                      section,
                      componentKey,
                      "provenance",
                    )
                  }
                  reference={run.reference}
                  referenceVersion={run.reference_version}
                  strategySemantics={run.catalog_semantics}
                  workingDirectory={run.working_directory}
                />
              ) : null}
              {run.run_id === comparison.baseline_run_id ? (
                <ComparisonTooltipBubble
                  id={baselineRunTooltipId}
                  layout={
                    activeTooltipLayout?.tooltipId === baselineRunTooltipId
                      ? activeTooltipLayout
                      : null
                  }
                  ref={registerComparisonTooltipBubbleRef(baselineRunTooltipId)}
                  text={baselineTooltip}
                />
              ) : null}
            </article>
          );
        })}
      </div>
      {primaryNarrative ? (
        <div className="comparison-top-story">
          <p
            className="kicker comparison-top-kicker comparison-cue comparison-tooltip"
            ref={registerComparisonTooltipTargetRef(topInsightTooltipId)}
            tabIndex={0}
            {...getComparisonTooltipTargetProps(topInsightTooltipId)}
          >
            <span aria-hidden="true" className="comparison-legend-swatch insight" />
            <span>Top insight / {formatComparisonIntentLabel(comparison.intent)}</span>
            <ComparisonTooltipBubble
              id={topInsightTooltipId}
              layout={
                activeTooltipLayout?.tooltipId === topInsightTooltipId ? activeTooltipLayout : null
              }
              ref={registerComparisonTooltipBubbleRef(topInsightTooltipId)}
              text={insightTooltip}
            />
          </p>
          <ComparisonNarrativeCard
            activeTooltipLayout={activeTooltipLayout}
            comparison={comparison}
            featured
            narrative={primaryNarrative}
            onSelectScoreLink={(value) => updateSelectedScoreLink(value, "narrative")}
            registerCardRef={registerComparisonNarrativeCardRef}
            registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
            registerTooltipTargetRef={registerComparisonTooltipTargetRef}
            selectedScoreLink={selectedScoreLink}
            tooltipId={featuredNarrativeTooltipId}
            tooltipTargetProps={
              featuredNarrativeTooltipId
                ? getComparisonTooltipTargetProps(featuredNarrativeTooltipId)
                : undefined
            }
            tooltip={insightTooltip}
          />
        </div>
      ) : null}
      {secondaryNarratives.length ? (
        <div className="comparison-story-grid">
          {secondaryNarratives.map((narrative) => (
            <ComparisonNarrativeCard
              activeTooltipLayout={activeTooltipLayout}
              comparison={comparison}
              key={`${narrative.baseline_run_id}-${narrative.run_id}`}
              narrative={narrative}
              onSelectScoreLink={(value) => updateSelectedScoreLink(value, "narrative")}
              registerCardRef={registerComparisonNarrativeCardRef}
              registerTooltipBubbleRef={registerComparisonTooltipBubbleRef}
              registerTooltipTargetRef={registerComparisonTooltipTargetRef}
              selectedScoreLink={selectedScoreLink}
            />
          ))}
        </div>
      ) : null}
      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Metric</th>
              {comparison.runs.map((run) => (
                <th key={run.run_id}>{run.strategy_name ?? run.strategy_id}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.metric_rows.map((metricRow) => {
              const metricRowLinked = isComparisonScoreLinkMatch(
                selectedScoreLink,
                [metricRow.key],
                "metrics",
              );

              return (
                <tr className={metricRowLinked ? "comparison-linked-metric-row" : undefined} key={metricRow.key}>
                  <th className={metricRowLinked ? "comparison-linked-metric-label" : undefined}>
                    <span>{metricRow.label}</span>
                    {metricRow.annotation ? (
                      <small className="comparison-metric-annotation">{metricRow.annotation}</small>
                    ) : null}
                  </th>
                  {comparison.runs.map((run) => {
                    const metricDrillBackTarget = resolveComparisonScoreDrillBackTarget(
                      comparison,
                      selectedScoreLink,
                      run.run_id,
                      "metrics",
                      metricRow.key,
                    );
                    const cellTooltip =
                      buildComparisonCellTooltip(
                        comparison.intent,
                        metricRow.label,
                        run.run_id === comparison.baseline_run_id,
                        metricRow.best_run_id === run.run_id,
                      ) || undefined;
                    const cellTooltipId = cellTooltip
                      ? buildComparisonTooltipId(tooltipScopeId, "metric", metricRow.key, run.run_id)
                      : undefined;
                    const metricTooltipTargetProps = cellTooltipId
                      ? getMetricComparisonTooltipTargetProps(
                          cellTooltipId,
                          metricRow.key,
                          run.run_id,
                        )
                      : undefined;
                    const linkedRunRole = metricRowLinked
                      ? getComparisonScoreLinkedRunRole(
                          selectedScoreLink,
                          comparison.baseline_run_id,
                          run.run_id,
                        )
                      : null;
                    const metricCellPressed =
                      Boolean(metricDrillBackTarget)
                      && selectedScoreLink?.narrativeRunId === metricDrillBackTarget?.narrativeRunId
                      && selectedScoreLink?.section === "metrics"
                      && selectedScoreLink?.componentKey === metricRow.key;
                    const cellClassName =
                      [
                        metricRow.best_run_id === run.run_id ? "comparison-best" : "",
                        run.run_id === comparison.baseline_run_id ? "comparison-baseline-cell" : "",
                        cellTooltip ? "comparison-cue comparison-tooltip comparison-cell-cue" : "",
                        metricDrillBackTarget ? "comparison-drillback-target" : "",
                        metricRowLinked ? "comparison-linked-metric-cell" : "",
                        linkedRunRole === "target" ? "comparison-linked-metric-cell-target" : "",
                        linkedRunRole === "baseline" ? "comparison-linked-metric-cell-baseline" : "",
                      ]
                        .filter(Boolean)
                        .join(" ") || undefined;

                    return (
                      <td
                        {...(metricTooltipTargetProps ?? {})}
                        aria-label={
                          metricDrillBackTarget
                            ? `Trace ${metricRow.label} score component for ${run.strategy_name ?? run.strategy_id}`
                            : undefined
                        }
                        aria-pressed={metricDrillBackTarget ? metricCellPressed : undefined}
                        className={cellClassName}
                        key={`${metricRow.key}-${run.run_id}`}
                        onClick={
                          metricDrillBackTarget
                            ? () =>
                                handleComparisonScoreDrillBack(
                                  run.run_id,
                                  "metrics",
                                  metricRow.key,
                                  "metric",
                                )
                            : undefined
                        }
                        onKeyDown={(event) => {
                          metricTooltipTargetProps?.onKeyDown?.(event);
                          if (
                            event.defaultPrevented
                            || !metricDrillBackTarget
                            || (event.key !== "Enter" && event.key !== " ")
                          ) {
                            return;
                          }
                          event.preventDefault();
                          handleComparisonScoreDrillBack(
                            run.run_id,
                            "metrics",
                            metricRow.key,
                            "metric",
                          );
                        }}
                        ref={
                          cellTooltipId
                            ? registerComparisonTooltipTargetRef(cellTooltipId)
                            : undefined
                        }
                        role={metricDrillBackTarget ? "button" : undefined}
                        tabIndex={metricDrillBackTarget || cellTooltip ? 0 : undefined}
                      >
                        <strong>
                          {formatComparisonMetric(metricRow.values[run.run_id], metricRow.unit)}
                        </strong>
                        <span className="comparison-delta">
                          {run.run_id === comparison.baseline_run_id
                            ? metricRow.delta_annotations[run.run_id] ?? "baseline"
                            : metricRow.delta_annotations[run.run_id] ?? formatComparisonDelta(
                                metricRow.deltas_vs_baseline[run.run_id],
                                metricRow.unit,
                              )}
                        </span>
                        {cellTooltipId && cellTooltip ? (
                          <ComparisonTooltipBubble
                            id={cellTooltipId}
                            layout={
                              activeTooltipLayout?.tooltipId === cellTooltipId
                                ? activeTooltipLayout
                                : null
                            }
                            ref={registerComparisonTooltipBubbleRef(cellTooltipId)}
                            text={cellTooltip}
                          />
                        ) : null}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
            <tr>
              <th>Notes</th>
              {comparison.runs.map((run) => (
                <td key={`notes-${run.run_id}`}>
                  <p className="comparison-note-copy">{summarizeRunNotes(run.notes)}</p>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ComparisonNarrativeCard({
  activeTooltipLayout,
  comparison,
  narrative,
  featured = false,
  onSelectScoreLink,
  registerCardRef,
  registerTooltipBubbleRef,
  registerTooltipTargetRef,
  selectedScoreLink,
  tooltipId,
  tooltipTargetProps,
  tooltip,
}: {
  activeTooltipLayout: ComparisonTooltipLayout | null;
  comparison: RunComparison;
  narrative: RunComparison["narratives"][number];
  featured?: boolean;
  onSelectScoreLink: (value: ComparisonScoreLinkTarget | null) => void;
  registerCardRef: (runId: string) => (node: HTMLElement | null) => void;
  registerTooltipBubbleRef: (tooltipId: string) => (node: HTMLSpanElement | null) => void;
  registerTooltipTargetRef: (tooltipId?: string) => (node: HTMLElement | null) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
  tooltipId?: string;
  tooltipTargetProps?: ComparisonTooltipTargetProps;
  tooltip?: string;
}) {
  const run = comparison.runs.find((candidate) => candidate.run_id === narrative.run_id);
  const runLabel = run?.reference?.title ?? run?.strategy_name ?? run?.strategy_id ?? narrative.run_id;
  const setCardRef = (node: HTMLElement | null) => {
    registerCardRef(narrative.run_id)(node);
    if (tooltipId) {
      registerTooltipTargetRef(tooltipId)(node);
    }
  };

  return (
    <article
      className={`comparison-story-card ${
        featured ? "featured comparison-cue-card comparison-tooltip" : ""
      } ${selectedScoreLink?.narrativeRunId === narrative.run_id ? "is-linked" : ""}`.trim()}
      ref={setCardRef}
      tabIndex={tooltip ? 0 : undefined}
      {...tooltipTargetProps}
    >
      <div className="comparison-story-head">
        <span>{formatComparisonNarrativeLabel(narrative.comparison_type)}</span>
        <strong>{runLabel}</strong>
      </div>
      <div className="comparison-story-meta">
        <span>#{narrative.rank}</span>
        <span>Score {formatComparisonScoreValue(narrative.insight_score)}</span>
      </div>
      <ComparisonNarrativeScoreBreakdown
        breakdown={narrative.score_breakdown}
        narrativeRunId={narrative.run_id}
        onSelectScoreLink={onSelectScoreLink}
        selectedScoreLink={selectedScoreLink}
      />
      <p className="comparison-story-title">{narrative.title}</p>
      <p className="comparison-story-summary">{narrative.summary}</p>
      {narrative.bullets.length ? (
        <ul className="comparison-story-list">
          {narrative.bullets.map((bullet) => (
            <li key={`${narrative.run_id}-${bullet}`}>{bullet}</li>
          ))}
        </ul>
      ) : null}
      {tooltipId && tooltip ? (
        <ComparisonTooltipBubble
          id={tooltipId}
          layout={activeTooltipLayout?.tooltipId === tooltipId ? activeTooltipLayout : null}
          ref={registerTooltipBubbleRef(tooltipId)}
          text={tooltip}
        />
      ) : null}
    </article>
  );
}

function ComparisonNarrativeScoreBreakdown({
  breakdown,
  narrativeRunId,
  onSelectScoreLink,
  selectedScoreLink,
}: {
  breakdown: RunComparison["narratives"][number]["score_breakdown"];
  narrativeRunId: string;
  onSelectScoreLink: (value: ComparisonScoreLinkTarget | null) => void;
  selectedScoreLink: ComparisonScoreLinkTarget | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const sections: Array<{
    key: ComparisonScoreSection;
    label: string;
    total: number;
    highlights: string[];
    components: Record<string, { score: number; [key: string]: unknown }>;
  }> = [
    {
      key: "metrics",
      label: "Metrics",
      total: breakdown.metrics.total,
      highlights: buildComparisonScoreHighlights("metrics", breakdown.metrics.components),
      components: breakdown.metrics.components,
    },
    {
      key: "semantics",
      label: "Semantics",
      total: breakdown.semantics.total,
      highlights: buildComparisonScoreHighlights("semantics", breakdown.semantics.components),
      components: breakdown.semantics.components,
    },
    {
      key: "context",
      label: "Context",
      total: breakdown.context.total,
      highlights: buildComparisonScoreHighlights("context", breakdown.context.components),
      components: breakdown.context.components,
    },
  ];
  const activeSelection =
    selectedScoreLink?.narrativeRunId === narrativeRunId ? selectedScoreLink : null;
  const activeSelectionLabel = activeSelection
    ? formatComparisonScoreComponentLabel(activeSelection.section, activeSelection.componentKey)
    : null;

  useEffect(() => {
    if (activeSelection) {
      setExpanded(true);
    }
  }, [activeSelection]);

  return (
    <section className="comparison-score-breakdown" aria-label="Narrative score breakdown">
      <div className="comparison-score-breakdown-head">
        <span>Score breakdown</span>
        <strong>{formatComparisonScoreValue(breakdown.total)}</strong>
      </div>
      <div className="comparison-score-breakdown-grid">
        {sections.map((section) => (
          <article className="comparison-score-breakdown-card" key={section.key}>
            <div className="comparison-score-breakdown-card-head">
              <span>{section.label}</span>
              <strong>{formatComparisonScoreValue(section.total)}</strong>
            </div>
            <p className="comparison-score-breakdown-copy">
              {section.highlights.length ? section.highlights.join(" / ") : "No active contribution"}
            </p>
          </article>
        ))}
      </div>
      {activeSelectionLabel ? (
        <p className="comparison-score-link-copy">
          Tracing {activeSelectionLabel} into the run deck, metric table, and provenance panels.
        </p>
      ) : null}
      <button
        aria-expanded={expanded}
        className="comparison-score-breakdown-toggle"
        onClick={() => setExpanded((current) => !current)}
        type="button"
      >
        {expanded ? "Hide score details" : "Show score details"}
      </button>
      {expanded ? (
        <div className="comparison-score-detail-grid">
          {sections.map((section) => (
            <article className="comparison-score-detail-card" key={section.key}>
              <div className="comparison-score-detail-card-head">
                <span>{section.label}</span>
                <strong>{formatComparisonScoreValue(section.total)}</strong>
              </div>
              <div className="comparison-score-detail-list">
                {buildComparisonScoreDetailRows(section.key, section.components).map((row) => {
                  const rowIsLinked =
                    activeSelection?.section === section.key
                    && activeSelection.componentKey === row.key;
                  return (
                    <button
                      aria-pressed={rowIsLinked}
                      className={`comparison-score-detail-row ${row.score > 0 ? "is-active" : ""} ${
                        rowIsLinked ? "is-linked" : ""
                      }`}
                      key={`${section.key}-${row.key}`}
                      onClick={() =>
                        onSelectScoreLink(
                          rowIsLinked
                            ? null
                            : {
                                narrativeRunId,
                                section: section.key,
                                componentKey: row.key,
                              },
                        )
                      }
                      type="button"
                    >
                      <div className="comparison-score-detail-row-head">
                        <span>{row.label}</span>
                        <strong>{formatComparisonScoreValue(row.score)}</strong>
                      </div>
                      <p className="comparison-score-detail-row-copy">
                        {row.details.length ? row.details.join(" / ") : "No active contribution"}
                      </p>
                    </button>
                  );
                })}
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

const ComparisonTooltipBubble = forwardRef<
  HTMLSpanElement,
  { id: string; layout: ComparisonTooltipLayout | null; text: string }
>(function ComparisonTooltipBubble({ id, layout, text }, ref) {
  const style: CSSProperties & { "--comparison-tooltip-arrow-left"?: string } = {
    left: layout?.left ?? 0,
    maxWidth: layout ? `${layout.maxWidth}px` : undefined,
    top: layout?.top ?? 0,
    "--comparison-tooltip-arrow-left": layout ? `${layout.arrowLeft}px` : undefined,
  };

  return (
    <span
      className="comparison-tooltip-bubble"
      data-tooltip-side={layout?.side ?? "bottom"}
      id={id}
      ref={ref}
      role="tooltip"
      style={style}
    >
      {text}
    </span>
  );
});

function ComparisonTooltipTuningPanel({
  pendingPresetImportConflict,
  presetDraftName,
  presets,
  shareDraft,
  shareFeedback,
  shareUrl,
  selectedPresetShareUrl,
  selectedPresetName,
  onChangePendingPresetImportName,
  onChangePresetDraftName,
  onChangeShareDraft,
  tuning,
  onChangeValue,
  onCopyShareUrl,
  onCopySelectedPresetShareUrl,
  onDeletePreset,
  onExportJson,
  onExportSelectedPresetJson,
  onImportJson,
  onLoadPreset,
  onResolvePendingPresetImportConflict,
  onReset,
  onSavePreset,
  onSetShareFeedback,
}: {
  pendingPresetImportConflict: ComparisonTooltipPendingPresetImportConflict | null;
  presetDraftName: string;
  presets: Record<string, ComparisonTooltipTuning>;
  shareDraft: string;
  shareFeedback: string | null;
  shareUrl: string;
  selectedPresetShareUrl: string;
  selectedPresetName: string;
  onChangePendingPresetImportName: (value: string) => void;
  onChangePresetDraftName: (value: string) => void;
  onChangeShareDraft: (value: string) => void;
  tuning: ComparisonTooltipTuning;
  onChangeValue: (key: keyof ComparisonTooltipTuning, value: string) => void;
  onCopyShareUrl: () => void;
  onCopySelectedPresetShareUrl: () => void;
  onDeletePreset: () => void;
  onExportJson: () => void;
  onExportSelectedPresetJson: () => void;
  onImportJson: () => void;
  onLoadPreset: (name: string) => void;
  onResolvePendingPresetImportConflict: (action: "overwrite" | "rename" | "skip") => void;
  onReset: () => void;
  onSavePreset: () => void;
  onSetShareFeedback: (value: string | null) => void;
}) {
  const [conflictSessionUiStateMap, setConflictSessionUiStateMap] = useState<
    Record<string, ComparisonTooltipConflictSessionUiState>
  >({});
  const [isConfirmingResetAllConflictViews, setIsConfirmingResetAllConflictViews] =
    useState(false);
  const [showAllSavedConflictSessionSummaries, setShowAllSavedConflictSessionSummaries] =
    useState(false);
  const [expandedSavedConflictSessionSummaryGroups, setExpandedSavedConflictSessionSummaryGroups] =
    useState<Record<string, boolean>>({});
  const [savedConflictSessionSummaryNowMs, setSavedConflictSessionSummaryNowMs] = useState(() =>
    Date.now(),
  );
  const presetNames = Object.keys(presets).sort((left, right) => left.localeCompare(right));
  const conflictExistingPreset = pendingPresetImportConflict
    ? presets[pendingPresetImportConflict.imported_preset_name] ?? null
    : null;
  const conflictSessionKey = pendingPresetImportConflict
    ? buildComparisonTooltipConflictSessionKey(pendingPresetImportConflict)
    : null;
  const conflictPreviewRows =
    pendingPresetImportConflict && conflictExistingPreset
      ? buildComparisonTooltipPresetConflictPreviewRows(
          conflictExistingPreset,
          pendingPresetImportConflict.tuning,
        )
      : [];
  const changedConflictPreviewRows = conflictPreviewRows.filter((row) => row.changed);
  const unchangedConflictPreviewRows = conflictPreviewRows.filter((row) => !row.changed);
  const changedConflictPreviewGroups = groupComparisonTooltipPresetConflictPreviewRows(
    changedConflictPreviewRows,
  );
  const unchangedConflictPreviewGroups = groupComparisonTooltipPresetConflictPreviewRows(
    unchangedConflictPreviewRows,
  );
  const changedConflictPreviewCount = changedConflictPreviewRows.length;
  const unchangedConflictPreviewCount = unchangedConflictPreviewRows.length;
  const currentConflictSessionUiState = conflictSessionKey
    ? conflictSessionUiStateMap[conflictSessionKey] ?? null
    : null;
  const savedConflictSessionCount = Object.keys(conflictSessionUiStateMap).length;
  const savedConflictSessionSummaries = buildComparisonTooltipConflictSessionSummaries(
    conflictSessionUiStateMap,
    conflictSessionKey,
    savedConflictSessionSummaryNowMs,
  );
  const savedConflictSessionSummaryUpdatedAtTimestamps = Object.values(
    conflictSessionUiStateMap,
  ).reduce<number[]>((timestamps, session) => {
    const timestamp = parseComparisonTooltipConflictSessionUpdatedAt(session.updated_at);
    if (timestamp) {
      timestamps.push(timestamp);
    }
    return timestamps;
  }, []);
  const visibleSavedConflictSessionSummaries = savedConflictSessionSummaries.slice(
    0,
    MAX_VISIBLE_COMPARISON_TOOLTIP_CONFLICT_SESSION_SUMMARIES,
  );
  const hiddenSavedConflictSessionSummaryCount = Math.max(
    0,
    savedConflictSessionSummaries.length - visibleSavedConflictSessionSummaries.length,
  );
  const displayedSavedConflictSessionSummaries = showAllSavedConflictSessionSummaries
    ? savedConflictSessionSummaries
    : visibleSavedConflictSessionSummaries;
  const savedConflictSessionSummaryRefreshMs =
    getComparisonTooltipConflictSessionRelativeTimeRefreshMs(
      savedConflictSessionSummaryUpdatedAtTimestamps,
      savedConflictSessionSummaryNowMs,
    );
  const showUnchangedConflictRows =
    currentConflictSessionUiState?.show_unchanged_conflict_rows ?? false;
  const collapsedUnchangedConflictGroups =
    currentConflictSessionUiState?.collapsed_unchanged_groups ?? {};

  useEffect(() => {
    setConflictSessionUiStateMap(loadComparisonTooltipConflictUiState().sessions);
  }, []);

  useEffect(() => {
    persistComparisonTooltipConflictUiState({
      sessions: conflictSessionUiStateMap,
      version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
    });
  }, [conflictSessionUiStateMap]);

  useEffect(() => {
    if (!savedConflictSessionCount && isConfirmingResetAllConflictViews) {
      setIsConfirmingResetAllConflictViews(false);
    }
  }, [isConfirmingResetAllConflictViews, savedConflictSessionCount]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews || !hiddenSavedConflictSessionSummaryCount) {
      setShowAllSavedConflictSessionSummaries(false);
    }
  }, [hiddenSavedConflictSessionSummaryCount, isConfirmingResetAllConflictViews]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews) {
      setExpandedSavedConflictSessionSummaryGroups({});
    }
  }, [isConfirmingResetAllConflictViews]);

  useEffect(() => {
    if (!isConfirmingResetAllConflictViews || !savedConflictSessionSummaryRefreshMs) {
      return;
    }
    const timeoutId = window.setTimeout(
      () => setSavedConflictSessionSummaryNowMs(Date.now()),
      savedConflictSessionSummaryRefreshMs,
    );
    return () => window.clearTimeout(timeoutId);
  }, [isConfirmingResetAllConflictViews, savedConflictSessionSummaryRefreshMs]);

  const updateCurrentConflictSessionUiState = (
    updater: (
      current: ComparisonTooltipConflictSessionUiState,
    ) => ComparisonTooltipConflictSessionUiState,
  ) => {
    if (!conflictSessionKey) {
      return;
    }
    setConflictSessionUiStateMap((current) => {
      const nextCurrent = current[conflictSessionKey] ?? {
        collapsed_unchanged_groups: {},
        show_unchanged_conflict_rows: false,
        updated_at: null,
      };
      const nextSession = updater(nextCurrent);
      return {
        ...current,
        [conflictSessionKey]: {
          ...nextSession,
          updated_at: new Date().toISOString(),
        },
      };
    });
  };

  const ensureUnchangedConflictGroupCollapseState = () => {
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      collapsed_unchanged_groups: seedComparisonTooltipUnchangedConflictGroupCollapseState(
        unchangedConflictPreviewGroups,
        current.collapsed_unchanged_groups,
      ),
    }));
  };

  const toggleShowUnchangedConflictRows = () => {
    if (!showUnchangedConflictRows) {
      ensureUnchangedConflictGroupCollapseState();
    }
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      show_unchanged_conflict_rows: !current.show_unchanged_conflict_rows,
    }));
  };

  const isUnchangedConflictGroupCollapsed = (
    group: ComparisonTooltipPresetConflictPreviewGroup,
  ) =>
    collapsedUnchangedConflictGroups[group.key] ??
    group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD;

  const toggleUnchangedConflictGroupCollapse = (
    group: ComparisonTooltipPresetConflictPreviewGroup,
  ) => {
    updateCurrentConflictSessionUiState((current) => ({
      ...current,
      collapsed_unchanged_groups: {
        ...current.collapsed_unchanged_groups,
        [group.key]:
          !(current.collapsed_unchanged_groups[group.key] ??
            group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD),
      },
    }));
  };

  const resetCurrentConflictSessionUiState = () => {
    if (!conflictSessionKey || !currentConflictSessionUiState) {
      onSetShareFeedback("No saved view state exists for the current conflict session.");
      return;
    }
    setConflictSessionUiStateMap((current) => {
      const next = { ...current };
      delete next[conflictSessionKey];
      return next;
    });
    onSetShareFeedback("Reset saved view state for the current conflict session.");
  };

  const requestResetAllConflictSessionUiState = () => {
    if (!savedConflictSessionCount) {
      onSetShareFeedback("No saved conflict-view state exists to reset.");
      return;
    }
    setIsConfirmingResetAllConflictViews(true);
    setShowAllSavedConflictSessionSummaries(false);
    setExpandedSavedConflictSessionSummaryGroups({});
    setSavedConflictSessionSummaryNowMs(Date.now());
    onSetShareFeedback(null);
  };

  const cancelResetAllConflictSessionUiState = () => {
    setIsConfirmingResetAllConflictViews(false);
    onSetShareFeedback("Canceled clearing saved conflict-view state.");
  };

  const resetAllConflictSessionUiState = () => {
    if (!savedConflictSessionCount) {
      onSetShareFeedback("No saved conflict-view state exists to reset.");
      return;
    }
    setConflictSessionUiStateMap({});
    setIsConfirmingResetAllConflictViews(false);
    onSetShareFeedback("Reset all saved conflict-view state.");
  };

  return (
    <details className="comparison-dev-panel">
      <summary className="comparison-dev-summary">
        Dev only: tooltip sweep tuning
      </summary>
      <p className="comparison-dev-copy">
        Tune sweep detection and suppression live while scanning dense comparison cells.
      </p>
      <div className="comparison-dev-preset-bar">
        <label className="comparison-dev-field">
          <span>Preset</span>
          <select
            onChange={(event) => onLoadPreset(event.target.value)}
            value={selectedPresetName}
          >
            <option value="">Draft only</option>
            {presetNames.map((presetName) => (
              <option key={presetName} value={presetName}>
                {presetName}
              </option>
            ))}
          </select>
        </label>
        <label className="comparison-dev-field">
          <span>Preset name</span>
          <input
            onChange={(event) => onChangePresetDraftName(event.target.value)}
            placeholder="session-a"
            type="text"
            value={presetDraftName}
          />
        </label>
        <div className="comparison-dev-actions comparison-dev-actions-inline">
          <button className="ghost-button comparison-dev-reset" onClick={onSavePreset} type="button">
            Save preset
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onDeletePreset}
            type="button"
          >
            Delete preset
          </button>
        </div>
      </div>
      <div className="comparison-dev-share-block">
        <label className="comparison-dev-field comparison-dev-share-url-field">
          <span>Bundle share URL</span>
          <input
            onFocus={(event) => event.currentTarget.select()}
            readOnly
            type="text"
            value={shareUrl}
          />
        </label>
        <label className="comparison-dev-field comparison-dev-share-url-field">
          <span>Selected preset share URL</span>
          <input
            onFocus={(event) => event.currentTarget.select()}
            placeholder="Save and select a preset to share it alone."
            readOnly
            type="text"
            value={selectedPresetShareUrl}
          />
        </label>
        <div className="comparison-dev-actions comparison-dev-actions-inline">
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onCopyShareUrl}
            type="button"
          >
            Copy bundle URL
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onCopySelectedPresetShareUrl}
            type="button"
          >
            Copy preset URL
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onExportJson}
            type="button"
          >
            Export bundle JSON
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            disabled={!selectedPresetName}
            onClick={onExportSelectedPresetJson}
            type="button"
          >
            Export preset JSON
          </button>
          <button
            className="ghost-button comparison-dev-reset"
            onClick={onImportJson}
            type="button"
          >
            Import JSON
          </button>
        </div>
        <label className="comparison-dev-field">
          <span>Bundle or preset JSON</span>
          <textarea
            onChange={(event) => onChangeShareDraft(event.target.value)}
            placeholder='{"current_tuning": {...}, "presets": {...}} or {"preset_name": "session-a", "tuning": {...}}'
            rows={8}
            value={shareDraft}
          />
        </label>
        <div className="comparison-dev-state-controls">
          <p className="comparison-dev-feedback">
            Saved conflict views: {savedConflictSessionCount}
          </p>
          <div className="comparison-dev-actions comparison-dev-actions-inline">
            <button
              className="ghost-button comparison-dev-reset"
              disabled={!currentConflictSessionUiState}
              onClick={resetCurrentConflictSessionUiState}
              type="button"
            >
              Reset current view
            </button>
            <button
              className="ghost-button comparison-dev-reset"
              disabled={!savedConflictSessionCount}
              onClick={requestResetAllConflictSessionUiState}
              type="button"
            >
              Reset all saved views
            </button>
          </div>
          {isConfirmingResetAllConflictViews ? (
            <div className="comparison-dev-confirm-card">
              <p className="comparison-dev-feedback">
                Clear all saved conflict views? This removes {savedConflictSessionCount} remembered
                {" "}
                session{savedConflictSessionCount === 1 ? "" : "s"} for conflict preview layout.
              </p>
              {visibleSavedConflictSessionSummaries.length ? (
                <div className="comparison-dev-session-summary">
                  <p className="comparison-dev-session-summary-title">Sessions queued for clearing</p>
                  <ul className="comparison-dev-session-summary-list">
                    {displayedSavedConflictSessionSummaries.map((summary) => (
                      <li
                        className="comparison-dev-session-summary-group"
                        key={summary.group_key}
                      >
                        <div className="comparison-dev-session-summary-item">
                          <div className="comparison-dev-session-summary-item-copy">
                            <span>{summary.label}</span>
                            {summary.includes_current ? (
                              <span className="comparison-dev-session-summary-badge">current</span>
                            ) : null}
                          </div>
                          <button
                            className="comparison-dev-session-group-toggle"
                            onClick={() =>
                              setExpandedSavedConflictSessionSummaryGroups((current) => ({
                                ...current,
                                [summary.group_key]: !current[summary.group_key],
                              }))
                            }
                            type="button"
                          >
                            {expandedSavedConflictSessionSummaryGroups[summary.group_key]
                              ? "Hide sessions"
                              : `Show ${summary.session_count} session${
                                  summary.session_count === 1 ? "" : "s"
                                }`}
                          </button>
                        </div>
                        {expandedSavedConflictSessionSummaryGroups[summary.group_key] ? (
                          <ul className="comparison-dev-session-detail-list">
                            {summary.sessions.map((session) => (
                              <li
                                className="comparison-dev-session-detail-item"
                                key={session.session_key}
                              >
                                <div className="comparison-dev-session-detail-copy">
                                  <span className="comparison-dev-session-detail-label">
                                    {session.label}
                                  </span>
                                  <span className="comparison-dev-session-detail-meta">
                                    {session.metadata.map((item) => (
                                      <span
                                        className="comparison-dev-session-detail-chip"
                                        key={item}
                                      >
                                        {item}
                                      </span>
                                    ))}
                                  </span>
                                </div>
                                {session.includes_current ? (
                                  <span className="comparison-dev-session-summary-badge">
                                    current
                                  </span>
                                ) : null}
                              </li>
                            ))}
                          </ul>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                  {hiddenSavedConflictSessionSummaryCount ? (
                    <button
                      className="comparison-dev-session-summary-toggle"
                      onClick={() =>
                        setShowAllSavedConflictSessionSummaries((current) => !current)
                      }
                      type="button"
                    >
                      {showAllSavedConflictSessionSummaries
                        ? "Show fewer preset groups"
                        : `Show all ${savedConflictSessionSummaries.length} preset groups`}
                    </button>
                  ) : null}
                </div>
              ) : null}
              <div className="comparison-dev-actions comparison-dev-actions-inline">
                <button
                  className="ghost-button comparison-dev-reset comparison-dev-reset-danger"
                  onClick={resetAllConflictSessionUiState}
                  type="button"
                >
                  Confirm clear all
                </button>
                <button
                  className="ghost-button comparison-dev-reset"
                  onClick={cancelResetAllConflictSessionUiState}
                  type="button"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : null}
        </div>
        {pendingPresetImportConflict ? (
          <div className="comparison-dev-conflict-card">
            <p className="comparison-dev-conflict-title">
              Preset name collision: {pendingPresetImportConflict.imported_preset_name}
            </p>
            <p className="comparison-dev-feedback">
              A preset with that name already exists. Rename the import, overwrite the local
              preset, or skip this import.
            </p>
            {conflictExistingPreset ? (
              <>
                <p className="comparison-dev-feedback">
                  {changedConflictPreviewCount
                    ? `${changedConflictPreviewCount} tuning value(s) differ and ${unchangedConflictPreviewCount} match.`
                    : "Incoming preset matches the existing preset exactly."}
                </p>
                <div className="comparison-dev-conflict-preview">
                  <div className="comparison-dev-conflict-preview-row comparison-dev-conflict-preview-head">
                    <span>Setting</span>
                    <span>Existing</span>
                    <span>Incoming</span>
                  </div>
                  {changedConflictPreviewGroups.map((group) => (
                    <div className="comparison-dev-conflict-preview-group" key={group.key}>
                      <div className="comparison-dev-conflict-preview-group-title">
                        <span>{group.label}</span>
                        <span className="comparison-dev-conflict-preview-group-meta">
                          <span className="comparison-dev-conflict-preview-group-summary">
                            {group.summary_label}
                          </span>
                        </span>
                      </div>
                      {group.rows.map((row) => (
                        <div
                          className={`comparison-dev-conflict-preview-row ${
                            row.changed ? "is-changed" : ""
                          }`}
                          key={row.key}
                        >
                          <span className="comparison-dev-conflict-preview-label-group">
                            <span className="comparison-dev-conflict-preview-label">{row.label}</span>
                            <span
                              className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}
                            >
                              {row.delta_label}
                            </span>
                          </span>
                          <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
                            {formatComparisonTooltipTuningValue(row.existing_value)}
                          </span>
                          <span
                            className={`comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-${row.delta_direction}`}
                          >
                            {formatComparisonTooltipTuningValue(row.incoming_value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  ))}
                  {unchangedConflictPreviewCount ? (
                    <button
                      className="comparison-dev-conflict-toggle"
                      onClick={toggleShowUnchangedConflictRows}
                      type="button"
                    >
                      {showUnchangedConflictRows
                        ? `Hide ${unchangedConflictPreviewCount} unchanged value(s)`
                        : `Show ${unchangedConflictPreviewCount} unchanged value(s)`}
                    </button>
                  ) : null}
                  {showUnchangedConflictRows
                    ? unchangedConflictPreviewGroups.map((group) => (
                        <div className="comparison-dev-conflict-preview-group" key={group.key}>
                          <div className="comparison-dev-conflict-preview-group-title">
                            <span>{group.label}</span>
                            <span className="comparison-dev-conflict-preview-group-meta">
                              <span className="comparison-dev-conflict-preview-group-summary">
                                {group.summary_label}
                              </span>
                              {group.rows.length >=
                              COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD ? (
                                <button
                                  className="comparison-dev-conflict-preview-group-toggle"
                                  onClick={() => toggleUnchangedConflictGroupCollapse(group)}
                                  type="button"
                                >
                                  {isUnchangedConflictGroupCollapsed(group)
                                    ? "Show rows"
                                    : "Hide rows"}
                                </button>
                              ) : null}
                            </span>
                          </div>
                          {isUnchangedConflictGroupCollapsed(group)
                            ? null
                            : group.rows.map((row) => (
                                <div className="comparison-dev-conflict-preview-row" key={row.key}>
                                  <span className="comparison-dev-conflict-preview-label-group">
                                    <span className="comparison-dev-conflict-preview-label">
                                      {row.label}
                                    </span>
                                    <span
                                      className={`comparison-dev-conflict-delta comparison-dev-conflict-delta-${row.delta_direction}`}
                                    >
                                      {row.delta_label}
                                    </span>
                                  </span>
                                  <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-existing">
                                    {formatComparisonTooltipTuningValue(row.existing_value)}
                                  </span>
                                  <span className="comparison-dev-conflict-preview-value comparison-dev-conflict-preview-value-incoming comparison-dev-conflict-preview-value-same">
                                    {formatComparisonTooltipTuningValue(row.incoming_value)}
                                  </span>
                                </div>
                              ))}
                        </div>
                      ))
                    : null}
                </div>
              </>
            ) : null}
            <label className="comparison-dev-field">
              <span>Renamed preset</span>
              <input
                onChange={(event) => onChangePendingPresetImportName(event.target.value)}
                type="text"
                value={pendingPresetImportConflict.proposed_preset_name}
              />
            </label>
            <div className="comparison-dev-actions comparison-dev-actions-inline">
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("rename")}
                type="button"
              >
                Rename and import
              </button>
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("overwrite")}
                type="button"
              >
                Overwrite existing
              </button>
              <button
                className="ghost-button comparison-dev-reset"
                onClick={() => onResolvePendingPresetImportConflict("skip")}
                type="button"
              >
                Skip import
              </button>
            </div>
          </div>
        ) : null}
        {shareFeedback ? <p className="comparison-dev-feedback">{shareFeedback}</p> : null}
      </div>
      <div className="comparison-dev-grid">
        <ComparisonTooltipTuningField
          label="Metric open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="metric_hover_open_ms"
          value={tuning.metric_hover_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Metric close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="metric_hover_close_ms"
          value={tuning.metric_hover_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Row open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_open_ms"
          value={tuning.row_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Row close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_close_ms"
          value={tuning.row_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Row hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="row_sweep_hold_ms"
          value={tuning.row_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_open_ms"
          value={tuning.column_down_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_close_ms"
          value={tuning.column_down_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Col down hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_down_sweep_hold_ms"
          value={tuning.column_down_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up open"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_open_ms"
          value={tuning.column_up_sweep_open_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up close"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_close_ms"
          value={tuning.column_up_sweep_close_ms}
        />
        <ComparisonTooltipTuningField
          label="Col up hold"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="column_up_sweep_hold_ms"
          value={tuning.column_up_sweep_hold_ms}
        />
        <ComparisonTooltipTuningField
          label="Time min"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_min_ms"
          value={tuning.sweep_time_min_ms}
        />
        <ComparisonTooltipTuningField
          label="Time max"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_max_ms"
          value={tuning.sweep_time_max_ms}
        />
        <ComparisonTooltipTuningField
          label="Time speed"
          onChangeValue={onChangeValue}
          step="1"
          tuningKey="sweep_time_speed_multiplier"
          value={tuning.sweep_time_speed_multiplier}
        />
        <ComparisonTooltipTuningField
          label="Horiz ratio"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="horizontal_distance_ratio"
          value={tuning.horizontal_distance_ratio}
        />
        <ComparisonTooltipTuningField
          label="Horiz velocity"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="horizontal_velocity_threshold"
          value={tuning.horizontal_velocity_threshold}
        />
        <ComparisonTooltipTuningField
          label="Vert ratio"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="vertical_distance_ratio"
          value={tuning.vertical_distance_ratio}
        />
        <ComparisonTooltipTuningField
          label="Vert velocity"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="vertical_velocity_threshold"
          value={tuning.vertical_velocity_threshold}
        />
        <ComparisonTooltipTuningField
          label="Speed base"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_base"
          value={tuning.speed_adjustment_base}
        />
        <ComparisonTooltipTuningField
          label="Speed slope"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_slope"
          value={tuning.speed_adjustment_slope}
        />
        <ComparisonTooltipTuningField
          label="Speed min"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_min"
          value={tuning.speed_adjustment_min}
        />
        <ComparisonTooltipTuningField
          label="Speed max"
          onChangeValue={onChangeValue}
          step="0.01"
          tuningKey="speed_adjustment_max"
          value={tuning.speed_adjustment_max}
        />
      </div>
      <div className="comparison-dev-actions">
        <button className="ghost-button comparison-dev-reset" onClick={onReset} type="button">
          Reset tuning
        </button>
      </div>
    </details>
  );
}

function ComparisonTooltipTuningField({
  label,
  onChangeValue,
  step,
  tuningKey,
  value,
}: {
  label: string;
  onChangeValue: (key: keyof ComparisonTooltipTuning, value: string) => void;
  step: string;
  tuningKey: keyof ComparisonTooltipTuning;
  value: number;
}) {
  return (
    <label className="comparison-dev-field">
      <span>{label}</span>
      <input
        min="0"
        onChange={(event) => onChangeValue(tuningKey, event.target.value)}
        step={step}
        type="number"
        value={value}
      />
    </label>
  );
}

function sanitizeComparisonTooltipId(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]+/g, "-");
}

function loadComparisonTooltipTuningPresetState(): ComparisonTooltipTuningPresetStateV1 {
  try {
    const raw = window.localStorage.getItem(COMPARISON_TOOLTIP_TUNING_STORAGE_KEY);
    if (!raw) {
      return createDefaultComparisonTooltipTuningPresetState();
    }
    const parsed = parseComparisonTooltipTuningPresetState(raw, { requireVersion: true });
    if (!parsed) {
      return createDefaultComparisonTooltipTuningPresetState();
    }
    return parsed;
  } catch {
    return createDefaultComparisonTooltipTuningPresetState();
  }
}

function loadComparisonTooltipConflictUiState(): ComparisonTooltipConflictUiStateV1 {
  try {
    const raw = window.localStorage.getItem(COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY);
    if (!raw) {
      return createDefaultComparisonTooltipConflictUiState();
    }
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipConflictUiStateV1> | null;
    if (!parsed || parsed.version !== COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION) {
      return createDefaultComparisonTooltipConflictUiState();
    }
    return {
      sessions: normalizeComparisonTooltipConflictSessionUiStateMap(parsed.sessions),
      version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
    };
  } catch {
    return createDefaultComparisonTooltipConflictUiState();
  }
}

function loadComparisonTooltipTuningShareImportFromUrl(): ComparisonTooltipTuningShareImport | null {
  try {
    const url = new URL(window.location.href);
    const sharedValue = url.searchParams.get(COMPARISON_TOOLTIP_TUNING_SHARE_PARAM);
    if (!sharedValue) {
      return null;
    }
    const decoded = decodeComparisonTooltipTuningSharePayload(sharedValue);
    if (!decoded) {
      return null;
    }
    return parseComparisonTooltipTuningShareImport(decoded);
  } catch {
    return null;
  }
}

function persistComparisonTooltipTuningPresetState(
  state: ComparisonTooltipTuningPresetStateV1,
) {
  try {
    window.localStorage.setItem(COMPARISON_TOOLTIP_TUNING_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore localStorage failures in dev-only tuning controls.
  }
}

function persistComparisonTooltipConflictUiState(state: ComparisonTooltipConflictUiStateV1) {
  try {
    window.localStorage.setItem(COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore localStorage failures in dev-only tuning controls.
  }
}

function createDefaultComparisonTooltipTuningPresetState(): ComparisonTooltipTuningPresetStateV1 {
  return {
    current_tuning: { ...DEFAULT_COMPARISON_TOOLTIP_TUNING },
    presets: {},
    selected_preset_name: null,
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  };
}

function createDefaultComparisonTooltipConflictUiState(): ComparisonTooltipConflictUiStateV1 {
  return {
    sessions: {},
    version: COMPARISON_TOOLTIP_CONFLICT_UI_STORAGE_VERSION,
  };
}

function createComparisonTooltipTuningSinglePresetShare(
  presetName: string,
  tuning: ComparisonTooltipTuning,
): ComparisonTooltipTuningSinglePresetShareV1 {
  return {
    preset_name: presetName,
    tuning: { ...tuning },
    version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
  };
}

function cloneComparisonTooltipPresetMap(
  value: Record<string, ComparisonTooltipTuning>,
): Record<string, ComparisonTooltipTuning> {
  return Object.fromEntries(
    Object.entries(value).map(([key, preset]) => [key, { ...preset }]),
  );
}

function normalizeComparisonTooltipConflictSessionUiStateMap(
  value: unknown,
): Record<string, ComparisonTooltipConflictSessionUiState> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, ComparisonTooltipConflictSessionUiState>>(
    (accumulator, [key, session]) => {
      if (!key.trim() || !session || typeof session !== "object") {
        return accumulator;
      }
      const parsed = session as Partial<ComparisonTooltipConflictSessionUiState>;
      accumulator[key] = {
        collapsed_unchanged_groups: normalizeComparisonTooltipBooleanMap(
          parsed.collapsed_unchanged_groups,
        ),
        show_unchanged_conflict_rows: parsed.show_unchanged_conflict_rows === true,
        updated_at:
          typeof parsed.updated_at === "string" && parsed.updated_at.trim()
            ? parsed.updated_at
            : null,
      };
      return accumulator;
    },
    {},
  );
}

function normalizeComparisonTooltipBooleanMap(value: unknown): Record<string, boolean> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, boolean>>((accumulator, [key, flag]) => {
    if (!key.trim() || typeof flag !== "boolean") {
      return accumulator;
    }
    accumulator[key] = flag;
    return accumulator;
  }, {});
}

function parseComparisonTooltipTuningPresetState(
  raw: string,
  options?: { requireVersion?: boolean },
): ComparisonTooltipTuningPresetStateV1 | null {
  try {
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipTuningPresetStateV1> | null;
    if (!parsed) {
      return null;
    }
    if (options?.requireVersion && parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION) {
      return null;
    }
    if (
      typeof parsed.version === "number" &&
      parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION
    ) {
      return null;
    }
    if (!("current_tuning" in parsed) && !("presets" in parsed)) {
      return null;
    }
    const presets = normalizeComparisonTooltipPresetMap(parsed.presets);
    const selectedPresetName =
      typeof parsed.selected_preset_name === "string" && presets[parsed.selected_preset_name]
        ? parsed.selected_preset_name
        : null;
    return {
      current_tuning: normalizeComparisonTooltipTuning(parsed.current_tuning),
      presets,
      selected_preset_name: selectedPresetName,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    };
  } catch {
    return null;
  }
}

function parseComparisonTooltipTuningShareImport(
  raw: string,
): ComparisonTooltipTuningShareImport | null {
  const bundleState = parseComparisonTooltipTuningPresetState(raw);
  if (bundleState) {
    return {
      kind: "bundle",
      raw,
      state: bundleState,
    };
  }
  try {
    const parsed = JSON.parse(raw) as Partial<ComparisonTooltipTuningSinglePresetShareV1> | null;
    if (!parsed) {
      return null;
    }
    if (
      typeof parsed.version === "number" &&
      parsed.version !== COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION
    ) {
      return null;
    }
    if (typeof parsed.preset_name !== "string" || !parsed.preset_name.trim()) {
      return null;
    }
    return {
      kind: "preset",
      preset_name: parsed.preset_name.trim(),
      raw,
      tuning: normalizeComparisonTooltipTuning(parsed.tuning),
    };
  } catch {
    return null;
  }
}

function applyComparisonTooltipTuningShareImport(
  baseState: ComparisonTooltipTuningPresetStateV1,
  importedShare: ComparisonTooltipTuningShareImport,
  presetImportConflictPolicy: ComparisonTooltipPresetImportConflictPolicy,
):
  | {
      kind: "bundle";
      state: ComparisonTooltipTuningPresetStateV1;
    }
  | {
      kind: "preset";
      resolution: ComparisonTooltipPresetImportResolution;
      state: ComparisonTooltipTuningPresetStateV1;
    } {
  if (importedShare.kind === "bundle") {
    return {
      kind: "bundle",
      state: importedShare.state,
    };
  }
  return {
    kind: "preset",
    ...mergeComparisonTooltipSinglePresetIntoState(
      baseState,
      importedShare.preset_name,
      importedShare.tuning,
      presetImportConflictPolicy,
    ),
  };
}

function mergeComparisonTooltipSinglePresetIntoState(
  baseState: ComparisonTooltipTuningPresetStateV1,
  presetName: string,
  tuning: ComparisonTooltipTuning,
  presetImportConflictPolicy: ComparisonTooltipPresetImportConflictPolicy,
  renamedPresetName?: string,
): {
  resolution: ComparisonTooltipPresetImportResolution;
  state: ComparisonTooltipTuningPresetStateV1;
} {
  const importedPresetName = presetName.trim();
  const conflicted = Boolean(baseState.presets[importedPresetName]);
  const requestedPresetName =
    presetImportConflictPolicy === "rename" ? renamedPresetName?.trim() : undefined;
  const finalPresetName =
    presetImportConflictPolicy === "rename"
      ? requestedPresetName && requestedPresetName !== importedPresetName
        ? requestedPresetName
        : conflicted
          ? createAvailableComparisonTooltipPresetName(baseState.presets, importedPresetName)
          : importedPresetName
      : importedPresetName;

  return {
    resolution: {
      conflicted,
      final_preset_name: finalPresetName,
      imported_preset_name: importedPresetName,
      policy: presetImportConflictPolicy,
      renamed: conflicted && finalPresetName !== importedPresetName,
      overwritten: conflicted && finalPresetName === importedPresetName,
    },
    state: {
      current_tuning: { ...tuning },
      presets: {
        ...cloneComparisonTooltipPresetMap(baseState.presets),
        [finalPresetName]: { ...tuning },
      },
      selected_preset_name: finalPresetName,
      version: COMPARISON_TOOLTIP_TUNING_STORAGE_VERSION,
    },
  };
}

function createAvailableComparisonTooltipPresetName(
  presets: Record<string, ComparisonTooltipTuning>,
  presetName: string,
) {
  const normalizedBaseName = presetName.trim() || "imported-preset";
  if (!presets[normalizedBaseName]) {
    return normalizedBaseName;
  }
  const firstCandidate = `${normalizedBaseName} (import)`;
  if (!presets[firstCandidate]) {
    return firstCandidate;
  }
  let suffix = 2;
  while (presets[`${normalizedBaseName} (import ${suffix})`]) {
    suffix += 1;
  }
  return `${normalizedBaseName} (import ${suffix})`;
}

function buildComparisonTooltipPresetConflictPreviewRows(
  existingTuning: ComparisonTooltipTuning,
  incomingTuning: ComparisonTooltipTuning,
): ComparisonTooltipPresetConflictPreviewRow[] {
  return (
    Object.keys(DEFAULT_COMPARISON_TOOLTIP_TUNING) as Array<keyof ComparisonTooltipTuning>
  ).map((key) => {
    const existingValue = existingTuning[key];
    const incomingValue = incomingTuning[key];
    const delta = formatComparisonTooltipTuningDelta(existingValue, incomingValue);
    const group = COMPARISON_TOOLTIP_TUNING_GROUPS[key];
    return {
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: existingValue,
      group_key: group.key,
      group_label: group.label,
      group_order: group.order,
      incoming_value: incomingValue,
      key,
      label: COMPARISON_TOOLTIP_TUNING_LABELS[key],
    };
  });
}

function groupComparisonTooltipPresetConflictPreviewRows(
  rows: ComparisonTooltipPresetConflictPreviewRow[],
): ComparisonTooltipPresetConflictPreviewGroup[] {
  const groups = rows.reduce<Map<string, ComparisonTooltipPresetConflictPreviewGroup>>(
    (accumulator, row) => {
      const existingGroup = accumulator.get(row.group_key);
      if (existingGroup) {
        existingGroup.rows.push(row);
        return accumulator;
      }
      accumulator.set(row.group_key, {
        changed_count: 0,
        higher_count: 0,
        key: row.group_key,
        label: row.group_label,
        lower_count: 0,
        rows: [row],
        same_count: 0,
        summary_label: "",
      });
      return accumulator;
    },
    new Map(),
  );

  return [...groups.values()]
    .sort((left, right) => {
      const leftOrder = left.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder - rightOrder || left.label.localeCompare(right.label);
    })
    .map((group) => ({
      ...group,
      changed_count: group.rows.filter((row) => row.changed).length,
      higher_count: group.rows.filter((row) => row.delta_direction === "higher").length,
      lower_count: group.rows.filter((row) => row.delta_direction === "lower").length,
      rows: [...group.rows].sort((left, right) => left.label.localeCompare(right.label)),
      same_count: group.rows.filter((row) => row.delta_direction === "same").length,
      summary_label: formatComparisonTooltipPresetConflictGroupSummary(group.rows),
    }));
}

function seedComparisonTooltipUnchangedConflictGroupCollapseState(
  groups: ComparisonTooltipPresetConflictPreviewGroup[],
  current: Record<string, boolean>,
) {
  return groups.reduce<Record<string, boolean>>((accumulator, group) => {
    if (Object.prototype.hasOwnProperty.call(accumulator, group.key)) {
      return accumulator;
    }
    accumulator[group.key] =
      group.rows.length >= COMPARISON_TOOLTIP_UNCHANGED_GROUP_COLLAPSE_THRESHOLD;
    return accumulator;
  }, { ...current });
}

function buildComparisonTooltipConflictSessionKey(
  pendingConflict: ComparisonTooltipPendingPresetImportConflict,
) {
  return `${pendingConflict.imported_preset_name}:${hashComparisonTooltipConflictSessionRaw(
    pendingConflict.raw,
  )}`;
}

function buildComparisonTooltipConflictSessionSummaries(
  sessions: Record<string, ComparisonTooltipConflictSessionUiState>,
  currentConflictSessionKey: string | null,
  referenceNowMs: number,
): ComparisonTooltipConflictSessionSummary[] {
  const groupedSessions = Object.keys(sessions).reduce<
    Record<string, Omit<ComparisonTooltipConflictSessionSummary, "label">>
  >((accumulator, sessionKey) => {
    const parsed = parseComparisonTooltipConflictSessionKey(sessionKey);
    const presetName = parsed.preset_name || "Unnamed preset";
    const current = accumulator[presetName] ?? {
      group_key: presetName,
      includes_current: false,
      preset_name: presetName,
      session_count: 0,
      sessions: [],
    };
    const includesCurrent = sessionKey === currentConflictSessionKey;
    current.includes_current ||= includesCurrent;
    current.session_count += 1;
    current.sessions.push({
      hash: parsed.hash,
      includes_current: includesCurrent,
      label: "",
      metadata: [],
      session_key: sessionKey,
      updated_at: sessions[sessionKey]?.updated_at ?? null,
    });
    accumulator[presetName] = current;
    return accumulator;
  }, {});

  return Object.values(groupedSessions)
    .sort((left, right) => {
      if (left.includes_current !== right.includes_current) {
        return left.includes_current ? -1 : 1;
      }
      if (left.session_count !== right.session_count) {
        return right.session_count - left.session_count;
      }
      return left.preset_name.localeCompare(right.preset_name);
    })
    .map((summary) => ({
      ...summary,
      label: formatComparisonTooltipConflictSessionSummary(summary),
      sessions: [...summary.sessions]
        .sort((left, right) => {
          if (left.includes_current !== right.includes_current) {
            return left.includes_current ? -1 : 1;
          }
          const leftUpdatedAt = parseComparisonTooltipConflictSessionUpdatedAt(left.updated_at);
          const rightUpdatedAt = parseComparisonTooltipConflictSessionUpdatedAt(right.updated_at);
          if (leftUpdatedAt !== rightUpdatedAt) {
            return rightUpdatedAt - leftUpdatedAt;
          }
          return (left.hash ?? "").localeCompare(right.hash ?? "");
        })
        .map((session, index) => ({
          ...session,
          label: formatComparisonTooltipConflictSessionSummarySession(
            session,
            index,
            summary.session_count,
          ),
          metadata: formatComparisonTooltipConflictSessionMetadata(
            sessions[session.session_key],
            session.hash,
            referenceNowMs,
          ),
        })),
    }));
}

function parseComparisonTooltipConflictSessionKey(sessionKey: string) {
  const separatorIndex = sessionKey.lastIndexOf(":");
  if (separatorIndex <= 0 || separatorIndex === sessionKey.length - 1) {
    return {
      hash: null,
      preset_name: sessionKey.trim(),
    };
  }
  return {
    hash: sessionKey.slice(separatorIndex + 1).trim() || null,
    preset_name: sessionKey.slice(0, separatorIndex).trim(),
  };
}

function formatComparisonTooltipConflictSessionSummary(
  summary: Omit<ComparisonTooltipConflictSessionSummary, "label">,
) {
  if (summary.session_count === 1) {
    return summary.preset_name;
  }
  return `${summary.preset_name} (${summary.session_count} saved sessions)`;
}

function formatComparisonTooltipConflictSessionSummarySession(
  session: Omit<ComparisonTooltipConflictSessionSummarySession, "label">,
  index: number,
  totalSessions: number,
) {
  if (totalSessions === 1) {
    return "Saved session";
  }
  return `Saved session ${index + 1}`;
}

function formatComparisonTooltipConflictSessionMetadata(
  session: ComparisonTooltipConflictSessionUiState,
  hash: string | null,
  referenceNowMs: number,
) {
  const metadata: string[] = [];
  metadata.push(
    formatComparisonTooltipConflictSessionUpdatedAtLabel(session.updated_at, referenceNowMs),
  );
  metadata.push(
    session.show_unchanged_conflict_rows ? "unchanged rows visible" : "unchanged rows hidden",
  );

  const groupStates = Object.values(session.collapsed_unchanged_groups);
  const collapsedCount = groupStates.filter(Boolean).length;
  const expandedCount = groupStates.length - collapsedCount;

  if (!groupStates.length) {
    metadata.push("default group layout");
    return metadata;
  }

  if (expandedCount && collapsedCount) {
    metadata.push(`${expandedCount} expanded, ${collapsedCount} collapsed`);
    return metadata;
  }
  if (expandedCount) {
    metadata.push(`${expandedCount} expanded group${expandedCount === 1 ? "" : "s"}`);
  } else {
    metadata.push(`${collapsedCount} collapsed group${collapsedCount === 1 ? "" : "s"}`);
  }
  if (hash) {
    metadata.push(`ID ${hash.slice(0, 8)}`);
  }
  return metadata;
}

function parseComparisonTooltipConflictSessionUpdatedAt(value: string | null) {
  if (!value) {
    return 0;
  }
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function formatComparisonTooltipConflictSessionUpdatedAtLabel(
  value: string | null,
  referenceNowMs: number,
) {
  const timestamp = parseComparisonTooltipConflictSessionUpdatedAt(value);
  if (!timestamp) {
    return "updated time unavailable";
  }
  const date = new Date(timestamp);
  const now = new Date(referenceNowMs);
  const absoluteLabel = new Intl.DateTimeFormat(undefined, {
    ...(date.getFullYear() === now.getFullYear() ? {} : { year: "numeric" }),
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    month: "short",
  }).format(date);
  const relativeLabel = formatComparisonTooltipConflictSessionRelativeTime(timestamp, now);
  return relativeLabel
    ? `updated ${relativeLabel} · ${absoluteLabel}`
    : `updated ${absoluteLabel}`;
}

function formatComparisonTooltipConflictSessionRelativeTime(
  timestamp: number,
  now: Date,
) {
  const elapsedMs = timestamp - now.getTime();
  const absElapsedMs = Math.abs(elapsedMs);
  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;
  const yearMs = 365 * dayMs;

  const formatRelative = (value: number, unit: Intl.RelativeTimeFormatUnit) =>
    new Intl.RelativeTimeFormat(undefined, { numeric: "auto", style: "short" }).format(
      value,
      unit,
    );

  if (absElapsedMs < minuteMs) {
    return formatRelative(Math.round(elapsedMs / 1000), "second");
  }
  if (absElapsedMs < hourMs) {
    return formatRelative(Math.round(elapsedMs / minuteMs), "minute");
  }
  if (absElapsedMs < dayMs) {
    return formatRelative(Math.round(elapsedMs / hourMs), "hour");
  }
  if (absElapsedMs < weekMs) {
    return formatRelative(Math.round(elapsedMs / dayMs), "day");
  }
  if (absElapsedMs < monthMs) {
    return formatRelative(Math.round(elapsedMs / weekMs), "week");
  }
  if (absElapsedMs < yearMs) {
    return formatRelative(Math.round(elapsedMs / monthMs), "month");
  }
  return formatRelative(Math.round(elapsedMs / yearMs), "year");
}

function getComparisonTooltipConflictSessionRelativeTimeRefreshMs(
  timestamps: number[],
  referenceNowMs: number,
) {
  if (!timestamps.length) {
    return null;
  }

  const youngestAgeMs = timestamps.reduce((youngest, timestamp) => {
    const ageMs = Math.abs(referenceNowMs - timestamp);
    return Math.min(youngest, ageMs);
  }, Number.POSITIVE_INFINITY);

  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;

  if (youngestAgeMs < minuteMs) {
    return 5 * 1000;
  }
  if (youngestAgeMs < hourMs) {
    return minuteMs;
  }
  if (youngestAgeMs < dayMs) {
    return 5 * minuteMs;
  }
  if (youngestAgeMs < weekMs) {
    return hourMs;
  }
  if (youngestAgeMs < monthMs) {
    return 6 * hourMs;
  }
  return dayMs;
}

function hashComparisonTooltipConflictSessionRaw(value: string) {
  let hash = 5381;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }
  return (hash >>> 0).toString(36);
}

function formatComparisonTooltipTuningValue(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function formatComparisonTooltipTuningDelta(existingValue: number, incomingValue: number) {
  const delta = incomingValue - existingValue;
  if (delta === 0) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  return {
    direction: delta > 0 ? ("higher" as const) : ("lower" as const),
    label: `${delta > 0 ? "higher " : "lower "}${delta > 0 ? "+" : ""}${formatComparisonTooltipTuningValue(delta)}`,
  };
}

function formatComparisonTooltipPresetConflictGroupSummary(
  rows: ComparisonTooltipPresetConflictPreviewRow[],
) {
  const changedCount = rows.filter((row) => row.changed).length;
  const higherCount = rows.filter((row) => row.delta_direction === "higher").length;
  const lowerCount = rows.filter((row) => row.delta_direction === "lower").length;
  const sameCount = rows.filter((row) => row.delta_direction === "same").length;

  if (!changedCount) {
    return `${sameCount} match${sameCount === 1 ? "" : "es"}`;
  }

  const parts = [`${changedCount} changed`];
  if (higherCount) {
    parts.push(`${higherCount} higher`);
  }
  if (lowerCount) {
    parts.push(`${lowerCount} lower`);
  }
  if (sameCount) {
    parts.push(`${sameCount} match${sameCount === 1 ? "" : "es"}`);
  }
  return parts.join(" · ");
}

function formatComparisonTooltipPresetImportFeedback(
  resolution: ComparisonTooltipPresetImportResolution,
  options?: { verb?: "Imported" | "Loaded" },
) {
  const verb = options?.verb ?? "Imported";
  if (!resolution.conflicted) {
    return `${verb} preset "${resolution.final_preset_name}" into the current tuning bundle.`;
  }
  if (resolution.renamed) {
    return `${verb} preset "${resolution.imported_preset_name}" as "${resolution.final_preset_name}" because that name already existed.`;
  }
  return `${verb} preset "${resolution.final_preset_name}" and overwrote the existing preset with the same name.`;
}

function normalizeComparisonTooltipPresetMap(
  value: unknown,
): Record<string, ComparisonTooltipTuning> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return Object.entries(value).reduce<Record<string, ComparisonTooltipTuning>>(
    (accumulator, [key, preset]) => {
      if (!key.trim()) {
        return accumulator;
      }
      accumulator[key] = normalizeComparisonTooltipTuning(preset);
      return accumulator;
    },
    {},
  );
}

function normalizeComparisonTooltipTuning(value: unknown): ComparisonTooltipTuning {
  if (!value || typeof value !== "object") {
    return { ...DEFAULT_COMPARISON_TOOLTIP_TUNING };
  }
  const parsed = value as Partial<Record<keyof ComparisonTooltipTuning, unknown>>;
  const next = { ...DEFAULT_COMPARISON_TOOLTIP_TUNING };
  (
    Object.keys(DEFAULT_COMPARISON_TOOLTIP_TUNING) as Array<keyof ComparisonTooltipTuning>
  ).forEach((key) => {
    const candidate = parsed[key];
    if (typeof candidate === "number" && Number.isFinite(candidate)) {
      next[key] = candidate;
    }
  });
  return next;
}

function buildComparisonTooltipTuningShareUrl(
  state: ComparisonTooltipTuningPresetStateV1 | ComparisonTooltipTuningSinglePresetShareV1,
) {
  const url = new URL(window.location.href);
  url.searchParams.set(
    COMPARISON_TOOLTIP_TUNING_SHARE_PARAM,
    encodeComparisonTooltipTuningSharePayload(JSON.stringify(state)),
  );
  return url.toString();
}

function encodeComparisonTooltipTuningSharePayload(value: string) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return window
    .btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function decodeComparisonTooltipTuningSharePayload(value: string) {
  try {
    let normalized = value.replace(/-/g, "+").replace(/_/g, "/");
    while (normalized.length % 4 !== 0) {
      normalized += "=";
    }
    const binary = window.atob(normalized);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  } catch {
    return null;
  }
}

function buildComparisonTooltipId(baseId: string, ...parts: Array<string | null | undefined>) {
  return sanitizeComparisonTooltipId([baseId, ...parts].filter(Boolean).join("-"));
}

function getComparisonTooltipBoundaryRect(target: HTMLElement) {
  return target.closest(".comparison-table-wrap")?.getBoundingClientRect() ?? null;
}

function getAdaptiveMetricSweepTimeThreshold(
  pointerSpeed: number,
  tuning: ComparisonTooltipTuning,
) {
  return clampComparisonNumber(
    tuning.sweep_time_min_ms + pointerSpeed * tuning.sweep_time_speed_multiplier,
    tuning.sweep_time_min_ms,
    tuning.sweep_time_max_ms,
  );
}

function getAdaptiveMetricSweepDistanceThreshold(
  cellSize: number,
  pointerSpeed: number,
  axis: "horizontal" | "vertical",
  tuning: ComparisonTooltipTuning,
) {
  const baseRatio =
    axis === "horizontal" ? tuning.horizontal_distance_ratio : tuning.vertical_distance_ratio;
  const minimum = axis === "horizontal" ? 16 : 12;
  const maximum = axis === "horizontal" ? 44 : 34;
  const baseThreshold = clampComparisonNumber(cellSize * baseRatio, minimum, maximum);
  const speedAdjustment = clampComparisonNumber(
    tuning.speed_adjustment_base - pointerSpeed * tuning.speed_adjustment_slope,
    tuning.speed_adjustment_min,
    tuning.speed_adjustment_max,
  );
  return baseThreshold * speedAdjustment;
}

function clampComparisonNumber(value: number, minimum: number, maximum: number) {
  if (maximum < minimum) {
    return minimum;
  }
  return Math.min(Math.max(value, minimum), maximum);
}

function ReferenceRunProvenanceSummary({
  artifactPaths,
  benchmarkArtifacts,
  externalCommand,
  linkedScore,
  onDrillBackScoreLink,
  reference,
  referenceVersion,
  strategySemantics,
  workingDirectory,
}: {
  artifactPaths: string[];
  benchmarkArtifacts: BenchmarkArtifact[];
  externalCommand: string[];
  linkedScore?: (ComparisonScoreLinkTarget & { role: ComparisonScoreLinkedRunRole }) | null;
  onDrillBackScoreLink?: (section: ComparisonScoreSection, componentKey: string) => void;
  reference: ReferenceSource;
  referenceVersion?: string | null;
  strategySemantics?: {
    strategy_kind: string;
    execution_model: string;
    parameter_contract: string;
    source_descriptor?: string | null;
    operator_notes: string[];
  } | null;
  workingDirectory?: string | null;
}) {
  const linkedScoreSelection = linkedScore ?? null;
  const highlightStrategyKind =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["strategy_kind", "vocabulary"], "semantics");
  const highlightExecutionModel =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["execution_model", "vocabulary"], "semantics");
  const highlightParameterContract =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["parameter_contract", "vocabulary"], "semantics");
  const highlightSourceDescriptor =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "source_descriptor",
      "vocabulary",
      "native_reference_bonus",
      "reference_bonus",
      "reference_floor",
    ]);
  const highlightReferenceIdentity =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "source_descriptor",
      "provenance_richness",
      "native_reference_bonus",
      "reference_bonus",
      "reference_floor",
      "benchmark_story_bonus",
    ]);
  const highlightOperatorNotes =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["vocabulary"], "semantics");
  const highlightExecutionContext =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, [
      "provenance_richness",
      "reference_bonus",
      "reference_floor",
      "native_reference_bonus",
      "benchmark_story_bonus",
    ]);
  const highlightArtifacts =
    Boolean(linkedScoreSelection)
    && isComparisonScoreLinkMatch(linkedScoreSelection, ["provenance_richness", "benchmark_story_bonus"]);
  const highlightPanel =
    highlightStrategyKind
    || highlightExecutionModel
    || highlightParameterContract
    || highlightSourceDescriptor
    || highlightReferenceIdentity
    || highlightOperatorNotes
    || highlightExecutionContext
    || highlightArtifacts;
  const renderProvenanceCopyLine = ({
    children,
    componentKey,
    highlighted = false,
    section,
  }: {
    children: string;
    componentKey?: string;
    highlighted?: boolean;
    section?: ComparisonScoreSection;
  }) => {
    const className =
      [
        highlighted ? "comparison-linked-copy" : "",
        section && componentKey && onDrillBackScoreLink
          ? "reference-provenance-link comparison-drillback-target"
          : "",
      ]
        .filter(Boolean)
        .join(" ") || undefined;
    if (!section || !componentKey || !onDrillBackScoreLink) {
      return <p className={className}>{children}</p>;
    }
    const isPressed =
      linkedScoreSelection?.section === section && linkedScoreSelection.componentKey === componentKey;
    return (
      <button
        aria-label={`Trace ${formatComparisonScoreComponentLabel(section, componentKey)}`}
        aria-pressed={isPressed}
        className={className}
        onClick={() => onDrillBackScoreLink(section, componentKey)}
        onKeyDown={(event) => {
          if (event.key !== "Enter" && event.key !== " ") {
            return;
          }
          event.preventDefault();
          onDrillBackScoreLink(section, componentKey);
        }}
        type="button"
      >
        {children}
      </button>
    );
  };

  return (
    <section
      className={`reference-provenance ${highlightPanel ? "comparison-linked-panel" : ""} ${
        linkedScore?.role === "target" ? "comparison-linked-panel-target" : ""
      } ${linkedScore?.role === "baseline" ? "comparison-linked-panel-baseline" : ""}`.trim()}
    >
      <div className="reference-provenance-head">
        <span>Reference provenance</span>
        <strong>{reference.integration_mode}</strong>
      </div>
      <div className="reference-provenance-grid">
        <Metric label="Reference" value={reference.title} />
        <Metric label="License" value={reference.license} />
        <Metric label="Version" value={referenceVersion ?? "unknown"} />
        <Metric label="Runtime" value={reference.runtime ?? "n/a"} />
      </div>
      <div className="reference-provenance-copy">
        {renderProvenanceCopyLine({
          children: `ID: ${reference.reference_id}`,
          componentKey: "source_descriptor",
          highlighted: highlightReferenceIdentity,
          section: "semantics",
        })}
        {reference.homepage
          ? renderProvenanceCopyLine({
              children: `Homepage: ${reference.homepage}`,
              componentKey: "source_descriptor",
              highlighted: highlightReferenceIdentity,
              section: "semantics",
            })
          : null}
        {strategySemantics?.strategy_kind ? (
          renderProvenanceCopyLine({
            children: `Semantic kind: ${strategySemantics.strategy_kind}`,
            componentKey: "strategy_kind",
            highlighted: highlightStrategyKind,
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.execution_model ? (
          renderProvenanceCopyLine({
            children: `Execution model: ${strategySemantics.execution_model}`,
            componentKey: "execution_model",
            highlighted: highlightExecutionModel,
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.parameter_contract ? (
          renderProvenanceCopyLine({
            children: `Parameter contract: ${strategySemantics.parameter_contract}`,
            componentKey: "parameter_contract",
            highlighted: highlightParameterContract,
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.source_descriptor ? (
          renderProvenanceCopyLine({
            children: `Semantic source: ${strategySemantics.source_descriptor}`,
            componentKey: "source_descriptor",
            highlighted: highlightSourceDescriptor,
            section: "semantics",
          })
        ) : null}
        {strategySemantics?.operator_notes?.length ? (
          renderProvenanceCopyLine({
            children: `Operator notes: ${strategySemantics.operator_notes.join(" | ")}`,
            componentKey: "vocabulary",
            highlighted: highlightOperatorNotes,
            section: "semantics",
          })
        ) : null}
        {workingDirectory
          ? renderProvenanceCopyLine({
              children: `Working dir: ${workingDirectory}`,
              componentKey: "provenance_richness",
              highlighted: highlightExecutionContext,
              section: "context",
            })
          : null}
        {externalCommand.length
          ? renderProvenanceCopyLine({
              children: `Command: ${externalCommand.join(" ")}`,
              componentKey: "provenance_richness",
              highlighted: highlightExecutionContext,
              section: "context",
            })
          : null}
        {benchmarkArtifacts.length ? (
          <div className="reference-artifact-list">
            {benchmarkArtifacts.map((artifact) => {
              const summaryEntries = formatBenchmarkArtifactSummaryEntries(artifact.summary);
              const sectionEntries = formatBenchmarkArtifactSectionEntries(artifact.sections ?? {});
              const artifactComponentKey =
                summaryEntries.length || sectionEntries.length ? "benchmark_story_bonus" : "provenance_richness";
              const artifactIsPressed =
                linkedScoreSelection?.section === "context"
                && linkedScoreSelection.componentKey === artifactComponentKey;
              return (
                <article
                  aria-label={`Trace ${formatComparisonScoreComponentLabel("context", artifactComponentKey)}`}
                  aria-pressed={onDrillBackScoreLink ? artifactIsPressed : undefined}
                  className={`reference-artifact-card ${highlightArtifacts ? "is-linked" : ""} ${
                    onDrillBackScoreLink ? "is-drillback comparison-drillback-target" : ""
                  }`.trim()}
                  key={`${artifact.kind}-${artifact.path}`}
                  onClick={
                    onDrillBackScoreLink
                      ? () => onDrillBackScoreLink("context", artifactComponentKey)
                      : undefined
                  }
                  onKeyDown={
                    onDrillBackScoreLink
                      ? (event) => {
                          if (event.key !== "Enter" && event.key !== " ") {
                            return;
                          }
                          event.preventDefault();
                          onDrillBackScoreLink("context", artifactComponentKey);
                        }
                      : undefined
                  }
                  role={onDrillBackScoreLink ? "button" : undefined}
                  tabIndex={onDrillBackScoreLink ? 0 : undefined}
                >
                  <div className="reference-artifact-head">
                    <strong>{artifact.label}</strong>
                    <span>{artifact.kind}</span>
                  </div>
                  <p>{artifact.path}</p>
                  <p>
                    {artifact.is_directory ? "directory" : "file"}
                    {artifact.format ? ` / ${artifact.format}` : ""}
                    {artifact.exists ? "" : " / missing"}
                  </p>
                  {artifact.summary_source_path && artifact.summary_source_path !== artifact.path ? (
                    <p>Summary source: {artifact.summary_source_path}</p>
                  ) : null}
                  {summaryEntries.length ? (
                    <dl className="reference-artifact-summary">
                      {summaryEntries.map(([key, value]) => (
                        <div className="reference-artifact-summary-row" key={`${artifact.path}-${key}`}>
                          <dt>{formatBenchmarkArtifactSummaryLabel(key)}</dt>
                          <dd>{value}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                  {sectionEntries.length ? (
                    <div className="reference-artifact-sections">
                      {sectionEntries.map(([key, lines]) => (
                        <article className="reference-artifact-section-card" key={`${artifact.path}-${key}`}>
                          <div className="reference-artifact-section-head">
                            <strong>{formatBenchmarkArtifactSectionLabel(key)}</strong>
                          </div>
                          <div className="reference-artifact-section-body">
                            {lines.map((line) => (
                              <p key={`${artifact.path}-${key}-${line}`}>{line}</p>
                            ))}
                          </div>
                        </article>
                      ))}
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        ) : (
          renderProvenanceCopyLine({
            children: `Artifacts: ${artifactPaths.length ? artifactPaths.join(" | ") : "none recorded"}`,
            componentKey: "provenance_richness",
            highlighted: highlightArtifacts,
            section: "context",
          })
        )}
      </div>
    </section>
  );
}

function RunStrategySnapshot({
  strategy,
}: {
  strategy: NonNullable<Run["provenance"]["strategy"]>;
}) {
  return (
    <section className="run-strategy">
      <div className="run-strategy-head">
        <span>Strategy snapshot</span>
        <strong>{formatLaneLabel(strategy.runtime)}</strong>
      </div>
      <div className="run-strategy-grid">
        <Metric label="Version" value={strategy.version} />
        <Metric label="Lifecycle" value={strategy.lifecycle.stage} />
        <Metric label="Semantic kind" value={strategy.catalog_semantics.strategy_kind} />
        <Metric label="Warmup" value={`${strategy.warmup.required_bars} bars`} />
        <Metric label="TFs" value={strategy.warmup.timeframes.join(", ")} />
      </div>
      <div className="run-strategy-copy">
        <p>Supported timeframes: {strategy.supported_timeframes.join(", ") || "n/a"}</p>
        <p>Version lineage: {formatVersionLineage(strategy.version_lineage, strategy.version)}</p>
        {strategy.catalog_semantics.execution_model ? (
          <p>Execution model: {strategy.catalog_semantics.execution_model}</p>
        ) : null}
        {strategy.catalog_semantics.parameter_contract ? (
          <p>Parameter contract: {strategy.catalog_semantics.parameter_contract}</p>
        ) : null}
        {strategy.catalog_semantics.source_descriptor ? (
          <p>Source: {strategy.catalog_semantics.source_descriptor}</p>
        ) : null}
        <p>Resolved params: {formatParameterMap(strategy.parameter_snapshot.resolved)}</p>
        <p>Requested params: {formatParameterMap(strategy.parameter_snapshot.requested)}</p>
        {strategy.entrypoint ? <p>Entrypoint: {strategy.entrypoint}</p> : null}
        {strategy.lifecycle.registered_at ? (
          <p>Registered: {formatTimestamp(strategy.lifecycle.registered_at)}</p>
        ) : null}
        {strategy.catalog_semantics.operator_notes.length ? (
          <p>Operator notes: {strategy.catalog_semantics.operator_notes.join(" | ")}</p>
        ) : null}
      </div>
    </section>
  );
}

function RunRuntimeSessionSummary({
  runtimeSession,
}: {
  runtimeSession: NonNullable<Run["provenance"]["runtime_session"]>;
}) {
  return (
    <section className="run-lineage">
      <div className="run-lineage-head">
        <span>Runtime session</span>
        <strong>{runtimeSession.worker_kind}</strong>
      </div>
      <div className="run-lineage-grid">
        <Metric label="State" value={runtimeSession.lifecycle_state} />
        <Metric label="Ticks" value={String(runtimeSession.processed_tick_count)} />
        <Metric label="Recoveries" value={String(runtimeSession.recovery_count)} />
        <Metric
          label="Heartbeat"
          value={`${runtimeSession.heartbeat_interval_seconds}s / ${runtimeSession.heartbeat_timeout_seconds}s`}
        />
        <Metric label="Primed bars" value={String(runtimeSession.primed_candle_count)} />
      </div>
      <div className="run-lineage-copy">
        <p>Session: {runtimeSession.session_id}</p>
        <p>Started: {formatTimestamp(runtimeSession.started_at)}</p>
        <p>Last heartbeat: {formatTimestamp(runtimeSession.last_heartbeat_at)}</p>
        <p>Last processed candle: {formatTimestamp(runtimeSession.last_processed_candle_at)}</p>
        <p>Last seen candle: {formatTimestamp(runtimeSession.last_seen_candle_at)}</p>
        <p>Last recovery: {formatTimestamp(runtimeSession.last_recovered_at)}</p>
        <p>Recovery reason: {runtimeSession.last_recovery_reason ?? "none"}</p>
      </div>
    </section>
  );
}

function RunOrderLifecycleSummary({
  orders,
  orderControls,
}: {
  orders: Run["orders"];
  orderControls?: RunOrderControls | null;
}) {
  const openCount = orders.filter((order) => order.status === "open").length;
  const partialCount = orders.filter((order) => order.status === "partially_filled").length;
  const filledCount = orders.filter((order) => order.status === "filled").length;
  const canceledCount = orders.filter((order) => order.status === "canceled").length;
  const rejectedCount = orders.filter((order) => order.status === "rejected").length;
  const latestSyncAt =
    orders
      .map((order) => order.last_synced_at ?? order.updated_at ?? null)
      .filter((value): value is string => Boolean(value))
      .sort()
      .at(-1) ?? null;
  const previewOrders = [...orders]
    .sort((left, right) => {
      const leftActive = left.status === "open" || left.status === "partially_filled";
      const rightActive = right.status === "open" || right.status === "partially_filled";
      if (leftActive !== rightActive) {
        return leftActive ? -1 : 1;
      }
      const leftTimestamp = left.last_synced_at ?? left.updated_at ?? left.created_at;
      const rightTimestamp = right.last_synced_at ?? right.updated_at ?? right.created_at;
      return rightTimestamp.localeCompare(leftTimestamp);
    })
    .slice(0, 4);

  return (
    <section className="run-lineage">
      <div className="run-lineage-head">
        <span>Order lifecycle</span>
        <strong>{orders.length} tracked</strong>
      </div>
      <div className="run-lineage-grid">
        <Metric label="Open" value={String(openCount)} />
        <Metric label="Partial" value={String(partialCount)} />
        <Metric label="Filled" value={String(filledCount)} />
        <Metric label="Canceled" value={String(canceledCount)} />
        <Metric label="Rejected" value={String(rejectedCount)} />
      </div>
      <div className="run-lineage-copy">
        <p>Last order sync: {formatTimestamp(latestSyncAt)}</p>
      </div>
      <div className="run-lineage-symbols">
        {previewOrders.map((order) => (
          <article className="run-lineage-symbol-card" key={order.order_id}>
            <div className="run-lineage-symbol-head">
              <strong>{order.order_id}</strong>
              <span>{order.status}</span>
            </div>
            <div className="run-lineage-symbol-grid">
              <Metric label="Side" value={order.side} />
              <Metric label="Qty" value={order.quantity.toFixed(8)} />
              <Metric label="Filled" value={order.filled_quantity.toFixed(8)} />
              <Metric
                label="Remain"
                value={(order.remaining_quantity ?? Math.max(order.quantity - order.filled_quantity, 0)).toFixed(8)}
              />
            </div>
            <p className="run-lineage-symbol-copy">Instrument: {order.instrument_id}</p>
            <p className="run-lineage-symbol-copy">
              Avg fill:{" "}
              {order.average_fill_price === null || order.average_fill_price === undefined
                ? "n/a"
                : order.average_fill_price}
            </p>
            <p className="run-lineage-symbol-copy">Updated: {formatTimestamp(order.updated_at ?? null)}</p>
            <p className="run-lineage-symbol-copy">Synced: {formatTimestamp(order.last_synced_at ?? null)}</p>
            {orderControls && (order.status === "open" || order.status === "partially_filled") ? (
              <RunOrderActionControls order={order} orderControls={orderControls} />
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function RunOrderActionControls({
  order,
  orderControls,
}: {
  order: Run["orders"][number];
  orderControls: RunOrderControls;
}) {
  const remainingQuantity = order.remaining_quantity ?? Math.max(order.quantity - order.filled_quantity, 0);
  const draft = orderControls.getReplacementDraft(order.order_id, order);

  return (
    <div className="run-lineage-order-controls">
      <div className="run-lineage-order-fields">
        <label>
          New px
          <input
            min="0"
            onChange={(event) =>
              orderControls.onChangeReplacementDraft(order.order_id, {
                ...draft,
                price: event.target.value,
              })
            }
            step="any"
            type="number"
            value={draft.price}
          />
        </label>
        <label>
          Qty
          <input
            min="0"
            onChange={(event) =>
              orderControls.onChangeReplacementDraft(order.order_id, {
                ...draft,
                quantity: event.target.value,
              })
            }
            placeholder={remainingQuantity.toFixed(8)}
            step="any"
            type="number"
            value={draft.quantity}
          />
        </label>
      </div>
      <div className="run-lineage-order-actions">
        <button className="ghost-button" onClick={() => void orderControls.onCancelOrder(order.order_id)} type="button">
          Cancel order
        </button>
        <button
          className="ghost-button"
          onClick={() => void orderControls.onReplaceOrder(order.order_id, draft)}
          type="button"
        >
          Replace order
        </button>
      </div>
      <p className="run-lineage-symbol-copy">
        Blank qty uses the current remaining amount: {remainingQuantity.toFixed(8)}
      </p>
    </div>
  );
}

function RunMarketDataLineage({
  lineage,
  lineageBySymbol,
  rerunBoundaryId,
  rerunBoundaryState,
  rerunMatchStatus,
  rerunSourceRunId,
  rerunTargetBoundaryId,
}: {
  lineage: NonNullable<Run["provenance"]["market_data"]>;
  lineageBySymbol?: NonNullable<Run["provenance"]["market_data_by_symbol"]>;
  rerunBoundaryId?: string | null;
  rerunBoundaryState: string;
  rerunMatchStatus: string;
  rerunSourceRunId?: string | null;
  rerunTargetBoundaryId?: string | null;
}) {
  const symbolEntries = Object.entries(lineageBySymbol ?? {});

  return (
    <section className="run-lineage">
      <div className="run-lineage-head">
        <span>Data lineage</span>
        <strong>{lineage.provider}</strong>
      </div>
      <div className="run-lineage-grid">
        <Metric label="Provider" value={lineage.provider} />
        <Metric label="Sync" value={lineage.sync_status} />
        <Metric label="Repro" value={lineage.reproducibility_state} />
        <Metric label="Boundary" value={rerunBoundaryState} />
        <Metric label="Candles" value={String(lineage.candle_count)} />
        <Metric label="Timeframe" value={lineage.timeframe} />
      </div>
      <div className="run-lineage-copy">
        <p>
          {lineage.venue}:{lineage.symbols.join(", ")}
        </p>
        <p>Requested window: {formatRange(lineage.requested_start_at, lineage.requested_end_at)}</p>
        <p>Effective window: {formatRange(lineage.effective_start_at, lineage.effective_end_at)}</p>
        <p>Dataset ID: {lineage.dataset_identity ?? "unavailable"}</p>
        <p>Sync checkpoint: {lineage.sync_checkpoint_id ?? "unavailable"}</p>
        <p>Rerun boundary: {rerunBoundaryId ?? "unavailable"}</p>
        <p>Rerun status: {rerunMatchStatus}</p>
        <p>Rerun source: {rerunSourceRunId ?? "n/a"}</p>
        <p>Rerun target: {rerunTargetBoundaryId ?? "n/a"}</p>
        <p>Last sync: {formatTimestamp(lineage.last_sync_at)}</p>
        <p>Issues: {lineage.issues.length ? lineage.issues.join(", ") : "none"}</p>
      </div>
      {symbolEntries.length ? (
        <div className="run-lineage-symbols">
          {symbolEntries.map(([symbol, symbolLineage]) => (
            <article className="run-lineage-symbol-card" key={symbol}>
              <div className="run-lineage-symbol-head">
                <strong>{symbol}</strong>
                <span>{symbolLineage.sync_status}</span>
              </div>
              <div className="run-lineage-symbol-grid">
                <Metric label="Candles" value={String(symbolLineage.candle_count)} />
                <Metric label="Provider" value={symbolLineage.provider} />
                <Metric label="Repro" value={symbolLineage.reproducibility_state} />
                <Metric label="Window" value={formatRange(symbolLineage.effective_start_at, symbolLineage.effective_end_at)} />
              </div>
              <p className="run-lineage-symbol-copy">Dataset ID: {symbolLineage.dataset_identity ?? "unavailable"}</p>
              <p className="run-lineage-symbol-copy">
                Sync checkpoint: {symbolLineage.sync_checkpoint_id ?? "unavailable"}
              </p>
              <p className="run-lineage-symbol-copy">Last sync: {formatTimestamp(symbolLineage.last_sync_at)}</p>
              <p className="run-lineage-symbol-copy">
                Issues: {symbolLineage.issues.length ? symbolLineage.issues.join(", ") : "none"}
              </p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-tile">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatMetric(value?: number, suffix = "") {
  if (value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function formatComparisonScoreValue(value: number) {
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function buildComparisonScoreHighlights(
  section: "metrics" | "semantics" | "context",
  components: Record<string, { score: number; [key: string]: unknown }>,
) {
  return Object.entries(components)
    .filter(([, component]) => component.score > 0)
    .sort((left, right) => right[1].score - left[1].score)
    .slice(0, 3)
    .map(([key, component]) => formatComparisonScoreHighlight(section, key, component));
}

function buildComparisonScoreDetailRows(
  section: "metrics" | "semantics" | "context",
  components: Record<string, { score: number; [key: string]: unknown }>,
) {
  return Object.entries(components)
    .sort((left, right) => {
      if (right[1].score !== left[1].score) {
        return right[1].score - left[1].score;
      }
      return formatComparisonScoreComponentLabel(section, left[0]).localeCompare(
        formatComparisonScoreComponentLabel(section, right[0]),
      );
    })
    .map(([key, component]) => ({
      key,
      label: formatComparisonScoreComponentLabel(section, key),
      score: component.score,
      details: buildComparisonScoreComponentDetails(section, key, component),
    }));
}

function formatComparisonScoreHighlight(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  const label = formatComparisonScoreComponentLabel(section, key);
  const detail = formatComparisonScoreComponentDetail(section, key, component);
  const score = formatComparisonScoreValue(component.score);
  return detail ? `${label} ${score} (${detail})` : `${label} ${score}`;
}

function formatComparisonScoreComponentLabel(
  section: "metrics" | "semantics" | "context",
  key: string,
) {
  const labels: Record<string, string> = {
    total_return_pct: "Return delta",
    max_drawdown_pct: "Drawdown delta",
    win_rate_pct: "Win-rate delta",
    trade_count: "Trade-flow delta",
    strategy_kind: "Strategy kind",
    execution_model: "Execution model",
    source_descriptor: "Source descriptor",
    parameter_contract: "Parameter contract",
    vocabulary: "Vocabulary richness",
    provenance_richness: "Provenance richness",
    native_reference_bonus: "Native/reference bonus",
    reference_bonus: "Reference bonus",
    status_bonus: "Status split",
    benchmark_story_bonus: "Benchmark story",
    reference_floor: "Reference floor",
  };
  return labels[key] ?? `${section} ${key.replace(/_/g, " ")}`;
}

function formatComparisonScoreComponentDetail(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  if (section === "metrics" && typeof component.delta === "number") {
    return `delta ${formatComparisonScoreSignedValue(component.delta)}`;
  }
  if (section === "semantics" && key === "vocabulary") {
    const changedKeys = Array.isArray(component.changed_keys) ? component.changed_keys.length : 0;
    if (changedKeys > 0) {
      return `${changedKeys} changed key${changedKeys === 1 ? "" : "s"}`;
    }
  }
  if (
    section === "semantics"
    && key === "provenance_richness"
    && typeof component.units === "number"
  ) {
    return `${formatComparisonScoreValue(component.units)} units`;
  }
  if (typeof component.applied === "boolean") {
    return component.applied ? "applied" : "inactive";
  }
  return "";
}

function buildComparisonScoreComponentDetails(
  section: "metrics" | "semantics" | "context",
  key: string,
  component: { score: number; [key: string]: unknown },
) {
  const details: string[] = [];
  if (section === "metrics") {
    if (typeof component.delta === "number") {
      details.push(`Delta ${formatComparisonScoreSignedValue(component.delta)}`);
    }
    if (typeof component.effective_delta === "number") {
      details.push(`Effective ${formatComparisonScoreValue(component.effective_delta)}`);
    }
    if (typeof component.weight === "number") {
      details.push(`Weight ${formatComparisonScoreValue(component.weight)}`);
    }
    return details;
  }

  if (section === "semantics" && key === "vocabulary") {
    const changedKeys = Array.isArray(component.changed_keys)
      ? component.changed_keys.map((item) => String(item))
      : [];
    if (changedKeys.length) {
      details.push(`Changed keys: ${changedKeys.join(", ")}`);
    }
    if (typeof component.schema_richness_delta === "number") {
      details.push(`Schema delta ${formatComparisonScoreValue(component.schema_richness_delta)}`);
    }
  }

  if (section === "semantics" && key === "provenance_richness") {
    if (typeof component.baseline_units === "number" && typeof component.target_units === "number") {
      details.push(
        `Units ${formatComparisonScoreValue(component.baseline_units)} -> ${formatComparisonScoreValue(component.target_units)}`,
      );
    }
  }

  if ("baseline" in component || "target" in component) {
    const baseline = formatComparisonScoreComponentRawValue(component.baseline);
    const target = formatComparisonScoreComponentRawValue(component.target);
    if (baseline || target) {
      details.push(`Baseline ${baseline || "n/a"} -> Target ${target || "n/a"}`);
    }
  }

  if (typeof component.units === "number") {
    details.push(`Units ${formatComparisonScoreValue(component.units)}`);
  }
  if (typeof component.capped_units === "number") {
    details.push(`Capped ${formatComparisonScoreValue(component.capped_units)}`);
  }
  if (typeof component.weight === "number") {
    details.push(`Weight ${formatComparisonScoreValue(component.weight)}`);
  }
  if (typeof component.applied === "boolean") {
    details.push(component.applied ? "Applied" : "Inactive");
  }
  return details;
}

function formatComparisonScoreComponentRawValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "";
  }
  if (typeof value === "number") {
    return formatComparisonScoreValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (Array.isArray(value)) {
    return value
      .map((item): string => formatComparisonScoreComponentRawValue(item))
      .filter(Boolean)
      .join(", ");
  }
  return String(value);
}

function formatComparisonScoreSignedValue(value: number) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatComparisonScoreValue(value)}`;
}

function getComparisonScoreLinkedRunRole(
  selection: ComparisonScoreLinkTarget | null,
  baselineRunId: string,
  runId: string,
): ComparisonScoreLinkedRunRole | null {
  if (!selection) {
    return null;
  }
  if (runId === selection.narrativeRunId) {
    return "target";
  }
  if (runId === baselineRunId) {
    return "baseline";
  }
  return null;
}

function resolveComparisonScoreDrillBackTarget(
  comparison: RunComparison,
  selection: ComparisonScoreLinkTarget | null,
  runId: string,
  section: ComparisonScoreSection,
  componentKey: string,
): ComparisonScoreLinkTarget | null {
  const narrativeSupportsComponent = (narrative: RunComparison["narratives"][number]) =>
    Object.prototype.hasOwnProperty.call(narrative.score_breakdown[section].components, componentKey);

  if (runId !== comparison.baseline_run_id) {
    const directNarrative = comparison.narratives.find(
      (narrative) => narrative.run_id === runId && narrativeSupportsComponent(narrative),
    );
    return directNarrative
      ? {
          componentKey,
          narrativeRunId: directNarrative.run_id,
          section,
        }
      : null;
  }

  const selectedNarrative =
    selection
      ? comparison.narratives.find(
          (narrative) =>
            narrative.run_id === selection.narrativeRunId && narrativeSupportsComponent(narrative),
        ) ?? null
      : null;
  const primaryNarrative =
    comparison.narratives.find(
      (narrative) => narrative.is_primary && narrativeSupportsComponent(narrative),
    ) ?? null;
  const fallbackNarrative = comparison.narratives.find(narrativeSupportsComponent) ?? null;
  const resolvedNarrative = selectedNarrative ?? primaryNarrative ?? fallbackNarrative;

  return resolvedNarrative
    ? {
        componentKey,
        narrativeRunId: resolvedNarrative.run_id,
        section,
      }
    : null;
}

function isComparisonScoreLinkMatch(
  selection: ComparisonScoreLinkTarget | null,
  componentKeys: string[],
  section?: ComparisonScoreSection,
) {
  return Boolean(
    selection
    && (!section || selection.section === section)
    && componentKeys.includes(selection.componentKey),
  );
}

function formatEditableNumber(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(8).replace(/\.?0+$/, "");
}

function formatFixedNumber(value?: number | null) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return value.toFixed(8);
}

function buildLiveOrderDraftKey(runId: string, orderId: string) {
  return `${runId}:${orderId}`;
}

function formatComparisonMetric(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (unit === "pct") {
    return `${value}%`;
  }
  return String(value);
}

function formatComparisonDelta(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) {
    return "delta n/a";
  }
  const prefix = value > 0 ? "+" : "";
  if (unit === "pct") {
    return `${prefix}${value}% vs baseline`;
  }
  return `${prefix}${value} vs baseline`;
}

function formatComparisonNarrativeLabel(value: string) {
  switch (value) {
    case "native_vs_reference":
      return "Native vs reference";
    case "reference_vs_reference":
      return "Reference vs reference";
    case "native_vs_native":
      return "Native vs native";
    default:
      return "Run divergence";
  }
}

function formatComparisonIntentLabel(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark validation";
    case "execution_regression":
      return "Execution regression";
    case "strategy_tuning":
      return "Strategy tuning";
    default:
      return value;
  }
}

function formatComparisonIntentLegend(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark drift cues";
    case "execution_regression":
      return "Regression risk cues";
    case "strategy_tuning":
      return "Tuning edge cues";
    default:
      return value;
  }
}

function formatComparisonIntentTooltip(value: ComparisonIntent) {
  switch (value) {
    case "benchmark_validation":
      return "Benchmark validation emphasizes drift from the reference benchmark. Cyan cues point to where native results confirm or diverge from the benchmark.";
    case "execution_regression":
      return "Execution regression emphasizes operational drift and regression risk. Ember cues point to where behavior degraded or recovered versus the control run.";
    case "strategy_tuning":
      return "Strategy tuning emphasizes optimization edge and tradeoffs. Green cues point to where parameter changes improved or hurt the candidate run.";
    default:
      return value;
  }
}

function formatComparisonCueTooltip(
  intent: ComparisonIntent,
  cue: ComparisonCueKind,
  metricLabel?: string,
) {
  switch (cue) {
    case "mode":
      return formatComparisonIntentTooltip(intent);
    case "baseline":
      switch (intent) {
        case "benchmark_validation":
          return "This baseline run anchors benchmark validation. Read the other runs as benchmark drift versus this control.";
        case "execution_regression":
          return "This baseline run is the control execution. Read the other runs as regression or recovery against it.";
        case "strategy_tuning":
          return "This baseline run is the incumbent tuning point. Read the other runs as edge or penalty against it.";
        default:
          return "This run is the comparison baseline.";
      }
    case "best":
      switch (intent) {
        case "benchmark_validation":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In validation mode, treat it as benchmark evidence rather than an automatic winner.`;
        case "execution_regression":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In regression mode, use it to spot recovered or degraded execution behavior quickly.`;
        case "strategy_tuning":
          return `${metricLabel ?? "This metric"} is highlighted because it shows the strongest observed outcome here. In tuning mode, use it to spot candidate improvements and tradeoffs quickly.`;
        default:
          return `${metricLabel ?? "This metric"} is highlighted because it is the strongest observed outcome in this row.`;
      }
    case "insight":
      switch (intent) {
        case "benchmark_validation":
          return "The featured insight summarizes the most important benchmark drift to inspect first.";
        case "execution_regression":
          return "The featured insight summarizes the sharpest regression signal to inspect first.";
        case "strategy_tuning":
          return "The featured insight summarizes the most actionable tuning edge or penalty first.";
        default:
          return "This is the primary comparison insight.";
      }
    default:
      return formatComparisonIntentTooltip(intent);
  }
}

function buildComparisonCellTooltip(
  intent: ComparisonIntent,
  metricLabel: string,
  isBaseline: boolean,
  isBest: boolean,
) {
  const messages: string[] = [];

  if (isBaseline) {
    messages.push(formatComparisonCueTooltip(intent, "baseline"));
  }

  if (isBest) {
    messages.push(formatComparisonCueTooltip(intent, "best", metricLabel));
  }

  return messages.join(" ");
}

function getComparisonIntentClassName(value: ComparisonIntent) {
  return `comparison-intent-${value.replaceAll("_", "-")}`;
}

function formatLaneLabel(runtime: string) {
  switch (runtime) {
    case "freqtrade_reference":
      return "reference";
    case "decision_engine":
      return "decision";
    default:
      return runtime;
  }
}

function formatVersionLineage(versionLineage: string[], fallbackVersion: string) {
  const values = versionLineage.length ? versionLineage : [fallbackVersion];
  return values.join(" -> ");
}

function extractDefaultParameters(schema: ParameterSchema) {
  return Object.fromEntries(
    Object.entries(schema)
      .filter(([, definition]) => definition.default !== undefined)
      .map(([name, definition]) => [name, definition.default]),
  );
}

function formatParameterMap(values: Record<string, unknown>) {
  const entries = Object.entries(values);
  if (!entries.length) {
    return "none";
  }
  return entries
    .map(([name, value]) => `${name}=${formatParameterValue(value)}`)
    .join(", ");
}

function formatParameterValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((item) => formatParameterValue(item)).join("|");
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function summarizeRunNotes(notes: string[]) {
  if (!notes.length) {
    return "No notes recorded.";
  }
  if (notes.length === 1) {
    return notes[0];
  }
  return `${notes[0]} | Final: ${notes[notes.length - 1]} | ${notes.length} notes`;
}

function formatTimestamp(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

function formatProviderRecoverySchema(providerRecovery: {
  provider_schema_kind?: string | null;
  pagerduty: {
    incident_id?: string | null;
    incident_key?: string | null;
    incident_status: string;
    urgency?: string | null;
    service_summary?: string | null;
    escalation_policy_summary?: string | null;
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
}) {
  if (providerRecovery.provider_schema_kind === "pagerduty") {
    const details = [
      providerRecovery.pagerduty.incident_id ? `incident ${providerRecovery.pagerduty.incident_id}` : null,
      providerRecovery.pagerduty.incident_status !== "unknown"
        ? `status ${providerRecovery.pagerduty.incident_status}`
        : null,
      providerRecovery.pagerduty.urgency ? `urgency ${providerRecovery.pagerduty.urgency}` : null,
      providerRecovery.pagerduty.service_summary ? `service ${providerRecovery.pagerduty.service_summary}` : null,
      providerRecovery.pagerduty.escalation_policy_summary
        ? `policy ${providerRecovery.pagerduty.escalation_policy_summary}`
        : null,
      providerRecovery.pagerduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagerduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagerduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagerduty.phase_graph.responder_phase !== "unknown"
        ? `responder ${providerRecovery.pagerduty.phase_graph.responder_phase}`
        : null,
      providerRecovery.pagerduty.last_status_change_at
        ? `changed ${formatTimestamp(providerRecovery.pagerduty.last_status_change_at)}`
        : null,
      providerRecovery.pagerduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagerduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsgenie") {
    const details = [
      providerRecovery.opsgenie.alert_id ? `alert ${providerRecovery.opsgenie.alert_id}` : null,
      providerRecovery.opsgenie.alert_status !== "unknown"
        ? `status ${providerRecovery.opsgenie.alert_status}`
        : null,
      providerRecovery.opsgenie.priority ? `priority ${providerRecovery.opsgenie.priority}` : null,
      providerRecovery.opsgenie.owner ? `owner ${providerRecovery.opsgenie.owner}` : null,
      providerRecovery.opsgenie.teams.length
        ? `teams ${providerRecovery.opsgenie.teams.join(", ")}`
        : null,
      providerRecovery.opsgenie.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsgenie.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsgenie.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsgenie.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsgenie.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsgenie.updated_at
        ? `updated ${formatTimestamp(providerRecovery.opsgenie.updated_at)}`
        : null,
      providerRecovery.opsgenie.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsgenie.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Opsgenie schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentio") {
    const details = [
      providerRecovery.incidentio.incident_id ? `incident ${providerRecovery.incidentio.incident_id}` : null,
      providerRecovery.incidentio.incident_status !== "unknown"
        ? `status ${providerRecovery.incidentio.incident_status}`
        : null,
      providerRecovery.incidentio.severity ? `severity ${providerRecovery.incidentio.severity}` : null,
      providerRecovery.incidentio.assignee ? `assignee ${providerRecovery.incidentio.assignee}` : null,
      providerRecovery.incidentio.visibility ? `visibility ${providerRecovery.incidentio.visibility}` : null,
      providerRecovery.incidentio.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.incidentio.phase_graph.incident_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentio.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.incidentio.phase_graph.assignment_phase}`
        : null,
      providerRecovery.incidentio.updated_at
        ? `updated ${formatTimestamp(providerRecovery.incidentio.updated_at)}`
        : null,
      providerRecovery.incidentio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incident.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "firehydrant") {
    const details = [
      providerRecovery.firehydrant.incident_id
        ? `incident ${providerRecovery.firehydrant.incident_id}`
        : null,
      providerRecovery.firehydrant.incident_status !== "unknown"
        ? `status ${providerRecovery.firehydrant.incident_status}`
        : null,
      providerRecovery.firehydrant.severity ? `severity ${providerRecovery.firehydrant.severity}` : null,
      providerRecovery.firehydrant.priority ? `priority ${providerRecovery.firehydrant.priority}` : null,
      providerRecovery.firehydrant.team ? `team ${providerRecovery.firehydrant.team}` : null,
      providerRecovery.firehydrant.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.firehydrant.phase_graph.incident_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.firehydrant.phase_graph.workflow_phase}`
        : null,
      providerRecovery.firehydrant.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.firehydrant.phase_graph.ownership_phase}`
        : null,
      providerRecovery.firehydrant.updated_at
        ? `updated ${formatTimestamp(providerRecovery.firehydrant.updated_at)}`
        : null,
      providerRecovery.firehydrant.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.firehydrant.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `FireHydrant schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "rootly") {
    const details = [
      providerRecovery.rootly.incident_id ? `incident ${providerRecovery.rootly.incident_id}` : null,
      providerRecovery.rootly.incident_status !== "unknown"
        ? `status ${providerRecovery.rootly.incident_status}`
        : null,
      providerRecovery.rootly.severity_id ? `severity ${providerRecovery.rootly.severity_id}` : null,
      providerRecovery.rootly.private === true
        ? "private"
        : providerRecovery.rootly.private === false
          ? "public"
          : null,
      providerRecovery.rootly.slug ? `slug ${providerRecovery.rootly.slug}` : null,
      providerRecovery.rootly.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.rootly.phase_graph.incident_phase}`
        : null,
      providerRecovery.rootly.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.rootly.phase_graph.workflow_phase}`
        : null,
      providerRecovery.rootly.phase_graph.acknowledgment_phase !== "unknown"
        ? `ack ${providerRecovery.rootly.phase_graph.acknowledgment_phase}`
        : null,
      providerRecovery.rootly.updated_at
        ? `updated ${formatTimestamp(providerRecovery.rootly.updated_at)}`
        : null,
      providerRecovery.rootly.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.rootly.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Rootly schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "blameless") {
    const details = [
      providerRecovery.blameless.incident_id ? `incident ${providerRecovery.blameless.incident_id}` : null,
      providerRecovery.blameless.incident_status !== "unknown"
        ? `status ${providerRecovery.blameless.incident_status}`
        : null,
      providerRecovery.blameless.severity ? `severity ${providerRecovery.blameless.severity}` : null,
      providerRecovery.blameless.commander ? `commander ${providerRecovery.blameless.commander}` : null,
      providerRecovery.blameless.visibility ? `visibility ${providerRecovery.blameless.visibility}` : null,
      providerRecovery.blameless.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.blameless.phase_graph.incident_phase}`
        : null,
      providerRecovery.blameless.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.blameless.phase_graph.workflow_phase}`
        : null,
      providerRecovery.blameless.phase_graph.command_phase !== "unknown"
        ? `command ${providerRecovery.blameless.phase_graph.command_phase}`
        : null,
      providerRecovery.blameless.updated_at
        ? `updated ${formatTimestamp(providerRecovery.blameless.updated_at)}`
        : null,
      providerRecovery.blameless.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.blameless.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Blameless schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "xmatters") {
    const details = [
      providerRecovery.xmatters.incident_id ? `incident ${providerRecovery.xmatters.incident_id}` : null,
      providerRecovery.xmatters.incident_status !== "unknown"
        ? `status ${providerRecovery.xmatters.incident_status}`
        : null,
      providerRecovery.xmatters.priority ? `priority ${providerRecovery.xmatters.priority}` : null,
      providerRecovery.xmatters.assignee ? `assignee ${providerRecovery.xmatters.assignee}` : null,
      providerRecovery.xmatters.response_plan
        ? `response plan ${providerRecovery.xmatters.response_plan}`
        : null,
      providerRecovery.xmatters.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.xmatters.phase_graph.incident_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.xmatters.phase_graph.workflow_phase}`
        : null,
      providerRecovery.xmatters.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.xmatters.phase_graph.ownership_phase}`
        : null,
      providerRecovery.xmatters.updated_at
        ? `updated ${formatTimestamp(providerRecovery.xmatters.updated_at)}`
        : null,
      providerRecovery.xmatters.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.xmatters.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `xMatters schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicenow") {
    const details = [
      providerRecovery.servicenow.incident_number
        ? `incident ${providerRecovery.servicenow.incident_number}`
        : null,
      providerRecovery.servicenow.incident_status !== "unknown"
        ? `status ${providerRecovery.servicenow.incident_status}`
        : null,
      providerRecovery.servicenow.priority ? `priority ${providerRecovery.servicenow.priority}` : null,
      providerRecovery.servicenow.assigned_to
        ? `assigned to ${providerRecovery.servicenow.assigned_to}`
        : null,
      providerRecovery.servicenow.assignment_group
        ? `group ${providerRecovery.servicenow.assignment_group}`
        : null,
      providerRecovery.servicenow.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.servicenow.phase_graph.incident_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicenow.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicenow.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.servicenow.phase_graph.assignment_phase}`
        : null,
      providerRecovery.servicenow.updated_at
        ? `updated ${formatTimestamp(providerRecovery.servicenow.updated_at)}`
        : null,
      providerRecovery.servicenow.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicenow.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ServiceNow schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squadcast") {
    const details = [
      providerRecovery.squadcast.incident_id ? `incident ${providerRecovery.squadcast.incident_id}` : null,
      providerRecovery.squadcast.incident_status !== "unknown"
        ? `status ${providerRecovery.squadcast.incident_status}`
        : null,
      providerRecovery.squadcast.severity ? `severity ${providerRecovery.squadcast.severity}` : null,
      providerRecovery.squadcast.assignee ? `assignee ${providerRecovery.squadcast.assignee}` : null,
      providerRecovery.squadcast.escalation_policy
        ? `policy ${providerRecovery.squadcast.escalation_policy}`
        : null,
      providerRecovery.squadcast.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.squadcast.phase_graph.incident_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squadcast.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squadcast.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squadcast.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squadcast.updated_at
        ? `updated ${formatTimestamp(providerRecovery.squadcast.updated_at)}`
        : null,
      providerRecovery.squadcast.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squadcast.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squadcast schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "bigpanda") {
    const details = [
      providerRecovery.bigpanda.incident_id ? `incident ${providerRecovery.bigpanda.incident_id}` : null,
      providerRecovery.bigpanda.incident_status !== "unknown"
        ? `status ${providerRecovery.bigpanda.incident_status}`
        : null,
      providerRecovery.bigpanda.severity ? `severity ${providerRecovery.bigpanda.severity}` : null,
      providerRecovery.bigpanda.assignee ? `assignee ${providerRecovery.bigpanda.assignee}` : null,
      providerRecovery.bigpanda.team ? `team ${providerRecovery.bigpanda.team}` : null,
      providerRecovery.bigpanda.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.bigpanda.phase_graph.incident_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bigpanda.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bigpanda.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bigpanda.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bigpanda.updated_at
        ? `updated ${formatTimestamp(providerRecovery.bigpanda.updated_at)}`
        : null,
      providerRecovery.bigpanda.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bigpanda.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BigPanda schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "grafana_oncall") {
    const details = [
      providerRecovery.grafana_oncall.incident_id
        ? `incident ${providerRecovery.grafana_oncall.incident_id}`
        : null,
      providerRecovery.grafana_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.grafana_oncall.incident_status}`
        : null,
      providerRecovery.grafana_oncall.severity
        ? `severity ${providerRecovery.grafana_oncall.severity}`
        : null,
      providerRecovery.grafana_oncall.assignee
        ? `assignee ${providerRecovery.grafana_oncall.assignee}`
        : null,
      providerRecovery.grafana_oncall.escalation_chain
        ? `chain ${providerRecovery.grafana_oncall.escalation_chain}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.grafana_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.grafana_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.grafana_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.grafana_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.grafana_oncall.updated_at)}`
        : null,
      providerRecovery.grafana_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.grafana_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Grafana OnCall schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "splunk_oncall") {
    const details = [
      providerRecovery.splunk_oncall.incident_id
        ? `incident ${providerRecovery.splunk_oncall.incident_id}`
        : null,
      providerRecovery.splunk_oncall.incident_status !== "unknown"
        ? `status ${providerRecovery.splunk_oncall.incident_status}`
        : null,
      providerRecovery.splunk_oncall.severity
        ? `severity ${providerRecovery.splunk_oncall.severity}`
        : null,
      providerRecovery.splunk_oncall.assignee
        ? `assignee ${providerRecovery.splunk_oncall.assignee}`
        : null,
      providerRecovery.splunk_oncall.routing_key
        ? `routing ${providerRecovery.splunk_oncall.routing_key}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.splunk_oncall.phase_graph.incident_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.splunk_oncall.phase_graph.workflow_phase}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.splunk_oncall.phase_graph.ownership_phase}`
        : null,
      providerRecovery.splunk_oncall.updated_at
        ? `updated ${formatTimestamp(providerRecovery.splunk_oncall.updated_at)}`
        : null,
      providerRecovery.splunk_oncall.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.splunk_oncall.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Splunk On-Call schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "jira_service_management") {
    const details = [
      providerRecovery.jira_service_management.incident_id
        ? `incident ${providerRecovery.jira_service_management.incident_id}`
        : null,
      providerRecovery.jira_service_management.incident_status !== "unknown"
        ? `status ${providerRecovery.jira_service_management.incident_status}`
        : null,
      providerRecovery.jira_service_management.priority
        ? `priority ${providerRecovery.jira_service_management.priority}`
        : null,
      providerRecovery.jira_service_management.assignee
        ? `assignee ${providerRecovery.jira_service_management.assignee}`
        : null,
      providerRecovery.jira_service_management.service_project
        ? `project ${providerRecovery.jira_service_management.service_project}`
        : null,
      providerRecovery.jira_service_management.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.jira_service_management.phase_graph.incident_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.jira_service_management.phase_graph.workflow_phase}`
        : null,
      providerRecovery.jira_service_management.phase_graph.assignment_phase !== "unknown"
        ? `assignment ${providerRecovery.jira_service_management.phase_graph.assignment_phase}`
        : null,
      providerRecovery.jira_service_management.updated_at
        ? `updated ${formatTimestamp(providerRecovery.jira_service_management.updated_at)}`
        : null,
      providerRecovery.jira_service_management.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.jira_service_management.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `Jira Service Management schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "pagertree") {
    const details = [
      providerRecovery.pagertree.incident_id ? `incident ${providerRecovery.pagertree.incident_id}` : null,
      providerRecovery.pagertree.incident_status !== "unknown"
        ? `status ${providerRecovery.pagertree.incident_status}`
        : null,
      providerRecovery.pagertree.urgency ? `urgency ${providerRecovery.pagertree.urgency}` : null,
      providerRecovery.pagertree.assignee ? `assignee ${providerRecovery.pagertree.assignee}` : null,
      providerRecovery.pagertree.team ? `team ${providerRecovery.pagertree.team}` : null,
      providerRecovery.pagertree.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.pagertree.phase_graph.incident_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.pagertree.phase_graph.workflow_phase}`
        : null,
      providerRecovery.pagertree.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.pagertree.phase_graph.ownership_phase}`
        : null,
      providerRecovery.pagertree.updated_at
        ? `updated ${formatTimestamp(providerRecovery.pagertree.updated_at)}`
        : null,
      providerRecovery.pagertree.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.pagertree.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `PagerTree schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "alertops") {
    const details = [
      providerRecovery.alertops.incident_id ? `incident ${providerRecovery.alertops.incident_id}` : null,
      providerRecovery.alertops.incident_status !== "unknown"
        ? `status ${providerRecovery.alertops.incident_status}`
        : null,
      providerRecovery.alertops.priority ? `priority ${providerRecovery.alertops.priority}` : null,
      providerRecovery.alertops.owner ? `owner ${providerRecovery.alertops.owner}` : null,
      providerRecovery.alertops.service ? `service ${providerRecovery.alertops.service}` : null,
      providerRecovery.alertops.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.alertops.phase_graph.incident_phase}`
        : null,
      providerRecovery.alertops.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.alertops.phase_graph.workflow_phase}`
        : null,
      providerRecovery.alertops.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.alertops.phase_graph.ownership_phase}`
        : null,
      providerRecovery.alertops.updated_at
        ? `updated ${formatTimestamp(providerRecovery.alertops.updated_at)}`
        : null,
      providerRecovery.alertops.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.alertops.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `AlertOps schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "signl4") {
    const details = [
      providerRecovery.signl4.alert_id ? `alert ${providerRecovery.signl4.alert_id}` : null,
      providerRecovery.signl4.alert_status !== "unknown"
        ? `status ${providerRecovery.signl4.alert_status}`
        : null,
      providerRecovery.signl4.priority ? `priority ${providerRecovery.signl4.priority}` : null,
      providerRecovery.signl4.team ? `team ${providerRecovery.signl4.team}` : null,
      providerRecovery.signl4.assignee ? `assignee ${providerRecovery.signl4.assignee}` : null,
      providerRecovery.signl4.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.signl4.phase_graph.alert_phase}`
        : null,
      providerRecovery.signl4.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.signl4.phase_graph.workflow_phase}`
        : null,
      providerRecovery.signl4.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.signl4.phase_graph.ownership_phase}`
        : null,
      providerRecovery.signl4.phase_graph.priority_phase !== "unknown"
        ? `priority phase ${providerRecovery.signl4.phase_graph.priority_phase}`
        : null,
      providerRecovery.signl4.phase_graph.team_phase !== "unknown"
        ? `team phase ${providerRecovery.signl4.phase_graph.team_phase}`
        : null,
      providerRecovery.signl4.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.signl4.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SIGNL4 schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "ilert") {
    const details = [
      providerRecovery.ilert.alert_id ? `alert ${providerRecovery.ilert.alert_id}` : null,
      providerRecovery.ilert.alert_status !== "unknown"
        ? `status ${providerRecovery.ilert.alert_status}`
        : null,
      providerRecovery.ilert.priority ? `priority ${providerRecovery.ilert.priority}` : null,
      providerRecovery.ilert.escalation_policy
        ? `policy ${providerRecovery.ilert.escalation_policy}`
        : null,
      providerRecovery.ilert.assignee ? `assignee ${providerRecovery.ilert.assignee}` : null,
      providerRecovery.ilert.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.ilert.phase_graph.alert_phase}`
        : null,
      providerRecovery.ilert.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.ilert.phase_graph.workflow_phase}`
        : null,
      providerRecovery.ilert.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.ilert.phase_graph.ownership_phase}`
        : null,
      providerRecovery.ilert.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.ilert.phase_graph.escalation_phase}`
        : null,
      providerRecovery.ilert.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.ilert.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `iLert schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "betterstack") {
    const details = [
      providerRecovery.betterstack.alert_id ? `alert ${providerRecovery.betterstack.alert_id}` : null,
      providerRecovery.betterstack.alert_status !== "unknown"
        ? `status ${providerRecovery.betterstack.alert_status}`
        : null,
      providerRecovery.betterstack.priority
        ? `priority ${providerRecovery.betterstack.priority}`
        : null,
      providerRecovery.betterstack.escalation_policy
        ? `policy ${providerRecovery.betterstack.escalation_policy}`
        : null,
      providerRecovery.betterstack.assignee
        ? `assignee ${providerRecovery.betterstack.assignee}`
        : null,
      providerRecovery.betterstack.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.betterstack.phase_graph.alert_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.betterstack.phase_graph.workflow_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.betterstack.phase_graph.ownership_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.betterstack.phase_graph.escalation_phase}`
        : null,
      providerRecovery.betterstack.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.betterstack.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Better Stack schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "onpage") {
    const details = [
      providerRecovery.onpage.alert_id ? `alert ${providerRecovery.onpage.alert_id}` : null,
      providerRecovery.onpage.alert_status !== "unknown"
        ? `status ${providerRecovery.onpage.alert_status}`
        : null,
      providerRecovery.onpage.priority ? `priority ${providerRecovery.onpage.priority}` : null,
      providerRecovery.onpage.escalation_policy
        ? `policy ${providerRecovery.onpage.escalation_policy}`
        : null,
      providerRecovery.onpage.assignee ? `assignee ${providerRecovery.onpage.assignee}` : null,
      providerRecovery.onpage.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.onpage.phase_graph.alert_phase}`
        : null,
      providerRecovery.onpage.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.onpage.phase_graph.workflow_phase}`
        : null,
      providerRecovery.onpage.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.onpage.phase_graph.ownership_phase}`
        : null,
      providerRecovery.onpage.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.onpage.phase_graph.escalation_phase}`
        : null,
      providerRecovery.onpage.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.onpage.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OnPage schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "allquiet") {
    const details = [
      providerRecovery.allquiet.alert_id ? `alert ${providerRecovery.allquiet.alert_id}` : null,
      providerRecovery.allquiet.alert_status !== "unknown"
        ? `status ${providerRecovery.allquiet.alert_status}`
        : null,
      providerRecovery.allquiet.priority ? `priority ${providerRecovery.allquiet.priority}` : null,
      providerRecovery.allquiet.escalation_policy
        ? `policy ${providerRecovery.allquiet.escalation_policy}`
        : null,
      providerRecovery.allquiet.assignee ? `assignee ${providerRecovery.allquiet.assignee}` : null,
      providerRecovery.allquiet.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.allquiet.phase_graph.alert_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.allquiet.phase_graph.workflow_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.allquiet.phase_graph.ownership_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.allquiet.phase_graph.escalation_phase}`
        : null,
      providerRecovery.allquiet.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.allquiet.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `All Quiet schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "moogsoft") {
    const details = [
      providerRecovery.moogsoft.alert_id ? `alert ${providerRecovery.moogsoft.alert_id}` : null,
      providerRecovery.moogsoft.alert_status !== "unknown"
        ? `status ${providerRecovery.moogsoft.alert_status}`
        : null,
      providerRecovery.moogsoft.priority ? `priority ${providerRecovery.moogsoft.priority}` : null,
      providerRecovery.moogsoft.escalation_policy
        ? `policy ${providerRecovery.moogsoft.escalation_policy}`
        : null,
      providerRecovery.moogsoft.assignee ? `assignee ${providerRecovery.moogsoft.assignee}` : null,
      providerRecovery.moogsoft.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.moogsoft.phase_graph.alert_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.moogsoft.phase_graph.workflow_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.moogsoft.phase_graph.ownership_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.moogsoft.phase_graph.escalation_phase}`
        : null,
      providerRecovery.moogsoft.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.moogsoft.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Moogsoft schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "spikesh") {
    const details = [
      providerRecovery.spikesh.alert_id ? `alert ${providerRecovery.spikesh.alert_id}` : null,
      providerRecovery.spikesh.alert_status !== "unknown"
        ? `status ${providerRecovery.spikesh.alert_status}`
        : null,
      providerRecovery.spikesh.priority ? `priority ${providerRecovery.spikesh.priority}` : null,
      providerRecovery.spikesh.escalation_policy
        ? `policy ${providerRecovery.spikesh.escalation_policy}`
        : null,
      providerRecovery.spikesh.assignee ? `assignee ${providerRecovery.spikesh.assignee}` : null,
      providerRecovery.spikesh.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.spikesh.phase_graph.alert_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.spikesh.phase_graph.workflow_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.spikesh.phase_graph.ownership_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.spikesh.phase_graph.escalation_phase}`
        : null,
      providerRecovery.spikesh.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.spikesh.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Spike.sh schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "dutycalls") {
    const details = [
      providerRecovery.dutycalls.alert_id ? `alert ${providerRecovery.dutycalls.alert_id}` : null,
      providerRecovery.dutycalls.alert_status !== "unknown"
        ? `status ${providerRecovery.dutycalls.alert_status}`
        : null,
      providerRecovery.dutycalls.priority ? `priority ${providerRecovery.dutycalls.priority}` : null,
      providerRecovery.dutycalls.escalation_policy
        ? `policy ${providerRecovery.dutycalls.escalation_policy}`
        : null,
      providerRecovery.dutycalls.assignee ? `assignee ${providerRecovery.dutycalls.assignee}` : null,
      providerRecovery.dutycalls.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.dutycalls.phase_graph.alert_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.dutycalls.phase_graph.workflow_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.dutycalls.phase_graph.ownership_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.dutycalls.phase_graph.escalation_phase}`
        : null,
      providerRecovery.dutycalls.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.dutycalls.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `DutyCalls schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidenthub") {
    const details = [
      providerRecovery.incidenthub.alert_id ? `alert ${providerRecovery.incidenthub.alert_id}` : null,
      providerRecovery.incidenthub.alert_status !== "unknown"
        ? `status ${providerRecovery.incidenthub.alert_status}`
        : null,
      providerRecovery.incidenthub.priority ? `priority ${providerRecovery.incidenthub.priority}` : null,
      providerRecovery.incidenthub.escalation_policy
        ? `policy ${providerRecovery.incidenthub.escalation_policy}`
        : null,
      providerRecovery.incidenthub.assignee ? `assignee ${providerRecovery.incidenthub.assignee}` : null,
      providerRecovery.incidenthub.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidenthub.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidenthub.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidenthub.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidenthub.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidenthub.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidenthub.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `IncidentHub schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "resolver") {
    const details = [
      providerRecovery.resolver.alert_id ? `alert ${providerRecovery.resolver.alert_id}` : null,
      providerRecovery.resolver.alert_status !== "unknown"
        ? `status ${providerRecovery.resolver.alert_status}`
        : null,
      providerRecovery.resolver.priority ? `priority ${providerRecovery.resolver.priority}` : null,
      providerRecovery.resolver.escalation_policy
        ? `policy ${providerRecovery.resolver.escalation_policy}`
        : null,
      providerRecovery.resolver.assignee ? `assignee ${providerRecovery.resolver.assignee}` : null,
      providerRecovery.resolver.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.resolver.phase_graph.alert_phase}`
        : null,
      providerRecovery.resolver.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.resolver.phase_graph.workflow_phase}`
        : null,
      providerRecovery.resolver.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.resolver.phase_graph.ownership_phase}`
        : null,
      providerRecovery.resolver.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.resolver.phase_graph.escalation_phase}`
        : null,
      providerRecovery.resolver.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.resolver.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Resolver schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "openduty") {
    const details = [
      providerRecovery.openduty.alert_id ? `alert ${providerRecovery.openduty.alert_id}` : null,
      providerRecovery.openduty.alert_status !== "unknown"
        ? `status ${providerRecovery.openduty.alert_status}`
        : null,
      providerRecovery.openduty.priority ? `priority ${providerRecovery.openduty.priority}` : null,
      providerRecovery.openduty.escalation_policy
        ? `policy ${providerRecovery.openduty.escalation_policy}`
        : null,
      providerRecovery.openduty.assignee ? `assignee ${providerRecovery.openduty.assignee}` : null,
      providerRecovery.openduty.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.openduty.phase_graph.alert_phase}`
        : null,
      providerRecovery.openduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.openduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.openduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.openduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.openduty.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.openduty.phase_graph.escalation_phase}`
        : null,
      providerRecovery.openduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.openduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpenDuty schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "cabot") {
    const details = [
      providerRecovery.cabot.alert_id ? `alert ${providerRecovery.cabot.alert_id}` : null,
      providerRecovery.cabot.alert_status !== "unknown"
        ? `status ${providerRecovery.cabot.alert_status}`
        : null,
      providerRecovery.cabot.priority ? `priority ${providerRecovery.cabot.priority}` : null,
      providerRecovery.cabot.escalation_policy
        ? `policy ${providerRecovery.cabot.escalation_policy}`
        : null,
      providerRecovery.cabot.assignee ? `assignee ${providerRecovery.cabot.assignee}` : null,
      providerRecovery.cabot.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.cabot.phase_graph.alert_phase}`
        : null,
      providerRecovery.cabot.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.cabot.phase_graph.workflow_phase}`
        : null,
      providerRecovery.cabot.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.cabot.phase_graph.ownership_phase}`
        : null,
      providerRecovery.cabot.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.cabot.phase_graph.escalation_phase}`
        : null,
      providerRecovery.cabot.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.cabot.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Cabot schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "haloitsm") {
    const details = [
      providerRecovery.haloitsm.alert_id ? `alert ${providerRecovery.haloitsm.alert_id}` : null,
      providerRecovery.haloitsm.alert_status !== "unknown"
        ? `status ${providerRecovery.haloitsm.alert_status}`
        : null,
      providerRecovery.haloitsm.priority ? `priority ${providerRecovery.haloitsm.priority}` : null,
      providerRecovery.haloitsm.escalation_policy
        ? `policy ${providerRecovery.haloitsm.escalation_policy}`
        : null,
      providerRecovery.haloitsm.assignee ? `assignee ${providerRecovery.haloitsm.assignee}` : null,
      providerRecovery.haloitsm.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.haloitsm.phase_graph.alert_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.haloitsm.phase_graph.workflow_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.haloitsm.phase_graph.ownership_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.haloitsm.phase_graph.escalation_phase}`
        : null,
      providerRecovery.haloitsm.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.haloitsm.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HaloITSM schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "incidentmanagerio") {
    const details = [
      providerRecovery.incidentmanagerio.alert_id
        ? `alert ${providerRecovery.incidentmanagerio.alert_id}`
        : null,
      providerRecovery.incidentmanagerio.alert_status !== "unknown"
        ? `status ${providerRecovery.incidentmanagerio.alert_status}`
        : null,
      providerRecovery.incidentmanagerio.priority
        ? `priority ${providerRecovery.incidentmanagerio.priority}`
        : null,
      providerRecovery.incidentmanagerio.escalation_policy
        ? `policy ${providerRecovery.incidentmanagerio.escalation_policy}`
        : null,
      providerRecovery.incidentmanagerio.assignee
        ? `assignee ${providerRecovery.incidentmanagerio.assignee}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.incidentmanagerio.phase_graph.alert_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.incidentmanagerio.phase_graph.workflow_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.incidentmanagerio.phase_graph.ownership_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.incidentmanagerio.phase_graph.escalation_phase}`
        : null,
      providerRecovery.incidentmanagerio.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.incidentmanagerio.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `incidentmanager.io schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "oneuptime") {
    const details = [
      providerRecovery.oneuptime.alert_id ? `alert ${providerRecovery.oneuptime.alert_id}` : null,
      providerRecovery.oneuptime.alert_status !== "unknown"
        ? `status ${providerRecovery.oneuptime.alert_status}`
        : null,
      providerRecovery.oneuptime.priority ? `priority ${providerRecovery.oneuptime.priority}` : null,
      providerRecovery.oneuptime.escalation_policy
        ? `policy ${providerRecovery.oneuptime.escalation_policy}`
        : null,
      providerRecovery.oneuptime.assignee ? `assignee ${providerRecovery.oneuptime.assignee}` : null,
      providerRecovery.oneuptime.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.oneuptime.phase_graph.alert_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.oneuptime.phase_graph.workflow_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.oneuptime.phase_graph.ownership_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.oneuptime.phase_graph.escalation_phase}`
        : null,
      providerRecovery.oneuptime.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.oneuptime.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OneUptime schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "squzy") {
    const details = [
      providerRecovery.squzy.alert_id ? `alert ${providerRecovery.squzy.alert_id}` : null,
      providerRecovery.squzy.alert_status !== "unknown"
        ? `status ${providerRecovery.squzy.alert_status}`
        : null,
      providerRecovery.squzy.priority ? `priority ${providerRecovery.squzy.priority}` : null,
      providerRecovery.squzy.escalation_policy
        ? `policy ${providerRecovery.squzy.escalation_policy}`
        : null,
      providerRecovery.squzy.assignee ? `assignee ${providerRecovery.squzy.assignee}` : null,
      providerRecovery.squzy.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.squzy.phase_graph.alert_phase}`
        : null,
      providerRecovery.squzy.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.squzy.phase_graph.workflow_phase}`
        : null,
      providerRecovery.squzy.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.squzy.phase_graph.ownership_phase}`
        : null,
      providerRecovery.squzy.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.squzy.phase_graph.escalation_phase}`
        : null,
      providerRecovery.squzy.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.squzy.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Squzy schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "crisescontrol") {
    const details = [
      providerRecovery.crisescontrol.alert_id
        ? `alert ${providerRecovery.crisescontrol.alert_id}`
        : null,
      providerRecovery.crisescontrol.alert_status !== "unknown"
        ? `status ${providerRecovery.crisescontrol.alert_status}`
        : null,
      providerRecovery.crisescontrol.priority
        ? `priority ${providerRecovery.crisescontrol.priority}`
        : null,
      providerRecovery.crisescontrol.escalation_policy
        ? `policy ${providerRecovery.crisescontrol.escalation_policy}`
        : null,
      providerRecovery.crisescontrol.assignee
        ? `assignee ${providerRecovery.crisescontrol.assignee}`
        : null,
      providerRecovery.crisescontrol.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.crisescontrol.phase_graph.alert_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.crisescontrol.phase_graph.workflow_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.crisescontrol.phase_graph.ownership_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.crisescontrol.phase_graph.escalation_phase}`
        : null,
      providerRecovery.crisescontrol.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.crisescontrol.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Crises Control schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshservice") {
    const details = [
      providerRecovery.freshservice.alert_id
        ? `alert ${providerRecovery.freshservice.alert_id}`
        : null,
      providerRecovery.freshservice.alert_status !== "unknown"
        ? `status ${providerRecovery.freshservice.alert_status}`
        : null,
      providerRecovery.freshservice.priority
        ? `priority ${providerRecovery.freshservice.priority}`
        : null,
      providerRecovery.freshservice.escalation_policy
        ? `policy ${providerRecovery.freshservice.escalation_policy}`
        : null,
      providerRecovery.freshservice.assignee
        ? `assignee ${providerRecovery.freshservice.assignee}`
        : null,
      providerRecovery.freshservice.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshservice.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshservice.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshservice.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshservice.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshservice.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshservice.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshservice schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "freshdesk") {
    const details = [
      providerRecovery.freshdesk.alert_id
        ? `alert ${providerRecovery.freshdesk.alert_id}`
        : null,
      providerRecovery.freshdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.freshdesk.alert_status}`
        : null,
      providerRecovery.freshdesk.priority
        ? `priority ${providerRecovery.freshdesk.priority}`
        : null,
      providerRecovery.freshdesk.escalation_policy
        ? `policy ${providerRecovery.freshdesk.escalation_policy}`
        : null,
      providerRecovery.freshdesk.assignee
        ? `assignee ${providerRecovery.freshdesk.assignee}`
        : null,
      providerRecovery.freshdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.freshdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.freshdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.freshdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.freshdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.freshdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.freshdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Freshdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "happyfox") {
    const details = [
      providerRecovery.happyfox.alert_id
        ? `alert ${providerRecovery.happyfox.alert_id}`
        : null,
      providerRecovery.happyfox.alert_status !== "unknown"
        ? `status ${providerRecovery.happyfox.alert_status}`
        : null,
      providerRecovery.happyfox.priority
        ? `priority ${providerRecovery.happyfox.priority}`
        : null,
      providerRecovery.happyfox.escalation_policy
        ? `policy ${providerRecovery.happyfox.escalation_policy}`
        : null,
      providerRecovery.happyfox.assignee
        ? `assignee ${providerRecovery.happyfox.assignee}`
        : null,
      providerRecovery.happyfox.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.happyfox.phase_graph.alert_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.happyfox.phase_graph.workflow_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.happyfox.phase_graph.ownership_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.happyfox.phase_graph.escalation_phase}`
        : null,
      providerRecovery.happyfox.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.happyfox.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `HappyFox schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zendesk") {
    const details = [
      providerRecovery.zendesk.alert_id
        ? `alert ${providerRecovery.zendesk.alert_id}`
        : null,
      providerRecovery.zendesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zendesk.alert_status}`
        : null,
      providerRecovery.zendesk.priority
        ? `priority ${providerRecovery.zendesk.priority}`
        : null,
      providerRecovery.zendesk.escalation_policy
        ? `policy ${providerRecovery.zendesk.escalation_policy}`
        : null,
      providerRecovery.zendesk.assignee
        ? `assignee ${providerRecovery.zendesk.assignee}`
        : null,
      providerRecovery.zendesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zendesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zendesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zendesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zendesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zendesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zendesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zendesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zohodesk") {
    const details = [
      providerRecovery.zohodesk.alert_id
        ? `alert ${providerRecovery.zohodesk.alert_id}`
        : null,
      providerRecovery.zohodesk.alert_status !== "unknown"
        ? `status ${providerRecovery.zohodesk.alert_status}`
        : null,
      providerRecovery.zohodesk.priority
        ? `priority ${providerRecovery.zohodesk.priority}`
        : null,
      providerRecovery.zohodesk.escalation_policy
        ? `policy ${providerRecovery.zohodesk.escalation_policy}`
        : null,
      providerRecovery.zohodesk.assignee
        ? `assignee ${providerRecovery.zohodesk.assignee}`
        : null,
      providerRecovery.zohodesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.zohodesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zohodesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zohodesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.zohodesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.zohodesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zohodesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zoho Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "helpscout") {
    const details = [
      providerRecovery.helpscout.alert_id
        ? `alert ${providerRecovery.helpscout.alert_id}`
        : null,
      providerRecovery.helpscout.alert_status !== "unknown"
        ? `status ${providerRecovery.helpscout.alert_status}`
        : null,
      providerRecovery.helpscout.priority
        ? `priority ${providerRecovery.helpscout.priority}`
        : null,
      providerRecovery.helpscout.escalation_policy
        ? `policy ${providerRecovery.helpscout.escalation_policy}`
        : null,
      providerRecovery.helpscout.assignee
        ? `assignee ${providerRecovery.helpscout.assignee}`
        : null,
      providerRecovery.helpscout.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.helpscout.phase_graph.alert_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.helpscout.phase_graph.workflow_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.helpscout.phase_graph.ownership_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.helpscout.phase_graph.escalation_phase}`
        : null,
      providerRecovery.helpscout.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.helpscout.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Help Scout schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "kayako") {
    const details = [
      providerRecovery.kayako.alert_id
        ? `case ${providerRecovery.kayako.alert_id}`
        : null,
      providerRecovery.kayako.alert_status !== "unknown"
        ? `status ${providerRecovery.kayako.alert_status}`
        : null,
      providerRecovery.kayako.priority
        ? `priority ${providerRecovery.kayako.priority}`
        : null,
      providerRecovery.kayako.escalation_policy
        ? `policy ${providerRecovery.kayako.escalation_policy}`
        : null,
      providerRecovery.kayako.assignee
        ? `assignee ${providerRecovery.kayako.assignee}`
        : null,
      providerRecovery.kayako.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.kayako.phase_graph.alert_phase}`
        : null,
      providerRecovery.kayako.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.kayako.phase_graph.workflow_phase}`
        : null,
      providerRecovery.kayako.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.kayako.phase_graph.ownership_phase}`
        : null,
      providerRecovery.kayako.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.kayako.phase_graph.escalation_phase}`
        : null,
      providerRecovery.kayako.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.kayako.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Kayako schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "intercom") {
    const details = [
      providerRecovery.intercom.alert_id
        ? `conversation ${providerRecovery.intercom.alert_id}`
        : null,
      providerRecovery.intercom.alert_status !== "unknown"
        ? `status ${providerRecovery.intercom.alert_status}`
        : null,
      providerRecovery.intercom.priority
        ? `priority ${providerRecovery.intercom.priority}`
        : null,
      providerRecovery.intercom.escalation_policy
        ? `policy ${providerRecovery.intercom.escalation_policy}`
        : null,
      providerRecovery.intercom.assignee
        ? `assignee ${providerRecovery.intercom.assignee}`
        : null,
      providerRecovery.intercom.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.intercom.phase_graph.alert_phase}`
        : null,
      providerRecovery.intercom.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.intercom.phase_graph.workflow_phase}`
        : null,
      providerRecovery.intercom.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.intercom.phase_graph.ownership_phase}`
        : null,
      providerRecovery.intercom.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.intercom.phase_graph.escalation_phase}`
        : null,
      providerRecovery.intercom.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.intercom.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Intercom schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "front") {
    const details = [
      providerRecovery.front.alert_id
        ? `conversation ${providerRecovery.front.alert_id}`
        : null,
      providerRecovery.front.alert_status !== "unknown"
        ? `status ${providerRecovery.front.alert_status}`
        : null,
      providerRecovery.front.priority
        ? `priority ${providerRecovery.front.priority}`
        : null,
      providerRecovery.front.escalation_policy
        ? `policy ${providerRecovery.front.escalation_policy}`
        : null,
      providerRecovery.front.assignee
        ? `assignee ${providerRecovery.front.assignee}`
        : null,
      providerRecovery.front.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.front.phase_graph.alert_phase}`
        : null,
      providerRecovery.front.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.front.phase_graph.workflow_phase}`
        : null,
      providerRecovery.front.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.front.phase_graph.ownership_phase}`
        : null,
      providerRecovery.front.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.front.phase_graph.escalation_phase}`
        : null,
      providerRecovery.front.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.front.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Front schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "servicedeskplus") {
    const details = [
      providerRecovery.servicedeskplus.alert_id
        ? `alert ${providerRecovery.servicedeskplus.alert_id}`
        : null,
      providerRecovery.servicedeskplus.alert_status !== "unknown"
        ? `status ${providerRecovery.servicedeskplus.alert_status}`
        : null,
      providerRecovery.servicedeskplus.priority
        ? `priority ${providerRecovery.servicedeskplus.priority}`
        : null,
      providerRecovery.servicedeskplus.escalation_policy
        ? `policy ${providerRecovery.servicedeskplus.escalation_policy}`
        : null,
      providerRecovery.servicedeskplus.assignee
        ? `assignee ${providerRecovery.servicedeskplus.assignee}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.servicedeskplus.phase_graph.alert_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.servicedeskplus.phase_graph.workflow_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.servicedeskplus.phase_graph.ownership_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.servicedeskplus.phase_graph.escalation_phase}`
        : null,
      providerRecovery.servicedeskplus.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.servicedeskplus.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `ManageEngine ServiceDesk Plus schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "sysaid") {
    const details = [
      providerRecovery.sysaid.alert_id ? `alert ${providerRecovery.sysaid.alert_id}` : null,
      providerRecovery.sysaid.alert_status !== "unknown"
        ? `status ${providerRecovery.sysaid.alert_status}`
        : null,
      providerRecovery.sysaid.priority ? `priority ${providerRecovery.sysaid.priority}` : null,
      providerRecovery.sysaid.escalation_policy
        ? `policy ${providerRecovery.sysaid.escalation_policy}`
        : null,
      providerRecovery.sysaid.assignee ? `assignee ${providerRecovery.sysaid.assignee}` : null,
      providerRecovery.sysaid.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.sysaid.phase_graph.alert_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.sysaid.phase_graph.workflow_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.sysaid.phase_graph.ownership_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.sysaid.phase_graph.escalation_phase}`
        : null,
      providerRecovery.sysaid.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.sysaid.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `SysAid schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "bmchelix") {
    const details = [
      providerRecovery.bmchelix.alert_id ? `alert ${providerRecovery.bmchelix.alert_id}` : null,
      providerRecovery.bmchelix.alert_status !== "unknown"
        ? `status ${providerRecovery.bmchelix.alert_status}`
        : null,
      providerRecovery.bmchelix.priority ? `priority ${providerRecovery.bmchelix.priority}` : null,
      providerRecovery.bmchelix.escalation_policy
        ? `policy ${providerRecovery.bmchelix.escalation_policy}`
        : null,
      providerRecovery.bmchelix.assignee ? `assignee ${providerRecovery.bmchelix.assignee}` : null,
      providerRecovery.bmchelix.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.bmchelix.phase_graph.alert_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.bmchelix.phase_graph.workflow_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.bmchelix.phase_graph.ownership_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.bmchelix.phase_graph.escalation_phase}`
        : null,
      providerRecovery.bmchelix.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.bmchelix.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `BMC Helix schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "solarwindsservicedesk") {
    const details = [
      providerRecovery.solarwindsservicedesk.alert_id
        ? `alert ${providerRecovery.solarwindsservicedesk.alert_id}`
        : null,
      providerRecovery.solarwindsservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.solarwindsservicedesk.alert_status}`
        : null,
      providerRecovery.solarwindsservicedesk.priority
        ? `priority ${providerRecovery.solarwindsservicedesk.priority}`
        : null,
      providerRecovery.solarwindsservicedesk.escalation_policy
        ? `policy ${providerRecovery.solarwindsservicedesk.escalation_policy}`
        : null,
      providerRecovery.solarwindsservicedesk.assignee
        ? `assignee ${providerRecovery.solarwindsservicedesk.assignee}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.solarwindsservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.solarwindsservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.solarwindsservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.solarwindsservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.solarwindsservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `SolarWinds Service Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "topdesk") {
    const details = [
      providerRecovery.topdesk.alert_id ? `alert ${providerRecovery.topdesk.alert_id}` : null,
      providerRecovery.topdesk.alert_status !== "unknown"
        ? `status ${providerRecovery.topdesk.alert_status}`
        : null,
      providerRecovery.topdesk.priority ? `priority ${providerRecovery.topdesk.priority}` : null,
      providerRecovery.topdesk.escalation_policy
        ? `policy ${providerRecovery.topdesk.escalation_policy}`
        : null,
      providerRecovery.topdesk.assignee ? `assignee ${providerRecovery.topdesk.assignee}` : null,
      providerRecovery.topdesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.topdesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.topdesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.topdesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.topdesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.topdesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.topdesk.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `TOPdesk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "invgateservicedesk") {
    const details = [
      providerRecovery.invgateservicedesk.alert_id
        ? `alert ${providerRecovery.invgateservicedesk.alert_id}`
        : null,
      providerRecovery.invgateservicedesk.alert_status !== "unknown"
        ? `status ${providerRecovery.invgateservicedesk.alert_status}`
        : null,
      providerRecovery.invgateservicedesk.priority
        ? `priority ${providerRecovery.invgateservicedesk.priority}`
        : null,
      providerRecovery.invgateservicedesk.escalation_policy
        ? `policy ${providerRecovery.invgateservicedesk.escalation_policy}`
        : null,
      providerRecovery.invgateservicedesk.assignee
        ? `assignee ${providerRecovery.invgateservicedesk.assignee}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.invgateservicedesk.phase_graph.alert_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.invgateservicedesk.phase_graph.workflow_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.invgateservicedesk.phase_graph.ownership_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.invgateservicedesk.phase_graph.escalation_phase}`
        : null,
      providerRecovery.invgateservicedesk.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(
            providerRecovery.invgateservicedesk.phase_graph.last_transition_at
          )}`
        : null,
    ].filter(Boolean);
    return details.length ? `InvGate Service Desk schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "opsramp") {
    const details = [
      providerRecovery.opsramp.alert_id ? `alert ${providerRecovery.opsramp.alert_id}` : null,
      providerRecovery.opsramp.alert_status !== "unknown"
        ? `status ${providerRecovery.opsramp.alert_status}`
        : null,
      providerRecovery.opsramp.priority ? `priority ${providerRecovery.opsramp.priority}` : null,
      providerRecovery.opsramp.escalation_policy
        ? `policy ${providerRecovery.opsramp.escalation_policy}`
        : null,
      providerRecovery.opsramp.assignee ? `assignee ${providerRecovery.opsramp.assignee}` : null,
      providerRecovery.opsramp.phase_graph.alert_phase !== "unknown"
        ? `alert phase ${providerRecovery.opsramp.phase_graph.alert_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.opsramp.phase_graph.workflow_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.opsramp.phase_graph.ownership_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.escalation_phase !== "unknown"
        ? `escalation ${providerRecovery.opsramp.phase_graph.escalation_phase}`
        : null,
      providerRecovery.opsramp.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.opsramp.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `OpsRamp schema: ${details.join(" / ")}` : null;
  }
  if (providerRecovery.provider_schema_kind === "zenduty") {
    const details = [
      providerRecovery.zenduty.incident_id ? `incident ${providerRecovery.zenduty.incident_id}` : null,
      providerRecovery.zenduty.incident_status !== "unknown"
        ? `status ${providerRecovery.zenduty.incident_status}`
        : null,
      providerRecovery.zenduty.severity ? `severity ${providerRecovery.zenduty.severity}` : null,
      providerRecovery.zenduty.assignee ? `assignee ${providerRecovery.zenduty.assignee}` : null,
      providerRecovery.zenduty.service ? `service ${providerRecovery.zenduty.service}` : null,
      providerRecovery.zenduty.phase_graph.incident_phase !== "unknown"
        ? `incident phase ${providerRecovery.zenduty.phase_graph.incident_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.workflow_phase !== "unknown"
        ? `workflow ${providerRecovery.zenduty.phase_graph.workflow_phase}`
        : null,
      providerRecovery.zenduty.phase_graph.ownership_phase !== "unknown"
        ? `ownership ${providerRecovery.zenduty.phase_graph.ownership_phase}`
        : null,
      providerRecovery.zenduty.updated_at
        ? `updated ${formatTimestamp(providerRecovery.zenduty.updated_at)}`
        : null,
      providerRecovery.zenduty.phase_graph.last_transition_at
        ? `phase changed ${formatTimestamp(providerRecovery.zenduty.phase_graph.last_transition_at)}`
        : null,
    ].filter(Boolean);
    return details.length ? `Zenduty schema: ${details.join(" / ")}` : null;
  }
  return null;
}

function formatProviderRecoveryTelemetry(providerRecovery: {
  telemetry: {
    source: string;
    state: string;
    progress_percent?: number | null;
    attempt_count: number;
    current_step?: string | null;
    last_message?: string | null;
    last_error?: string | null;
    external_run_id?: string | null;
    updated_at?: string | null;
  };
}) {
  const details = [
    providerRecovery.telemetry.source !== "unknown"
      ? `source ${providerRecovery.telemetry.source}`
      : null,
    providerRecovery.telemetry.state !== "unknown"
      ? `state ${providerRecovery.telemetry.state}`
      : null,
    providerRecovery.telemetry.progress_percent != null
      ? `progress ${providerRecovery.telemetry.progress_percent}%`
      : null,
    providerRecovery.telemetry.attempt_count
      ? `attempts ${providerRecovery.telemetry.attempt_count}`
      : null,
    providerRecovery.telemetry.current_step
      ? `step ${providerRecovery.telemetry.current_step}`
      : null,
    providerRecovery.telemetry.external_run_id
      ? `run ${providerRecovery.telemetry.external_run_id}`
      : null,
    providerRecovery.telemetry.updated_at
      ? `updated ${formatTimestamp(providerRecovery.telemetry.updated_at)}`
      : null,
    providerRecovery.telemetry.last_error
      ? `error ${providerRecovery.telemetry.last_error}`
      : providerRecovery.telemetry.last_message
        ? `message ${providerRecovery.telemetry.last_message}`
        : null,
  ].filter(Boolean);
  return details.length ? `Recovery telemetry: ${details.join(" / ")}` : null;
}

function shortenIdentifier(value: string, maxLength = 18) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function truncateLabel(value: string, maxLength = 56) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}

function formatRange(start?: string | null, end?: string | null) {
  if (!start && !end) {
    return "open-ended";
  }
  return `${formatTimestamp(start)} -> ${formatTimestamp(end)}`;
}

const benchmarkArtifactSummaryOrder = [
  "strategy_name",
  "run_id",
  "exchange",
  "stake_currency",
  "timeframe",
  "timerange",
  "generated_at",
  "backtest_start_at",
  "backtest_end_at",
  "pair_count",
  "trade_count",
  "profit_total_pct",
  "profit_total_abs",
  "max_drawdown_pct",
  "market_change_pct",
  "manifest_count",
  "snapshot_count",
] as const;

const benchmarkArtifactSummaryLabels: Record<string, string> = {
  headline: "Headline",
  market_context: "Market read",
  portfolio_context: "Portfolio read",
  signal_context: "Signal read",
  rejection_context: "Rejections",
  exit_context: "Exit read",
  pair_context: "Pair read",
  strategy_name: "Strategy",
  run_id: "Run ID",
  exchange: "Exchange",
  stake_currency: "Stake",
  timeframe: "TF",
  timerange: "Timerange",
  generated_at: "Generated",
  backtest_start_at: "Backtest start",
  backtest_end_at: "Backtest end",
  pair_count: "Pairs",
  trade_count: "Trades",
  profit_total_pct: "Total return",
  profit_total_abs: "Total PnL",
  max_drawdown_pct: "Max DD",
  market_change_pct: "Market move",
  manifest_count: "Manifests",
  snapshot_count: "Snapshots",
  timeframe_detail: "TF detail",
  notes: "Notes",
  win_rate_pct: "Win rate",
  date: "Date",
  duration: "Duration",
  drawdown_start: "DD start",
  drawdown_end: "DD end",
  start_balance: "Start balance",
  end_balance: "End balance",
  high_balance: "High balance",
  low_balance: "Low balance",
  sharpe: "Sharpe",
  sortino: "Sortino",
  calmar: "Calmar",
  member_count: "Members",
  entry_preview: "Entries",
  market_change_export_count: "Market exports",
  wallet_export_count: "Wallet exports",
  signal_export_count: "Signal exports",
  rejected_export_count: "Rejected exports",
  exited_export_count: "Exited exports",
  strategy_source_count: "Strategy sources",
  strategy_param_count: "Strategy params",
  result_json_entry: "Result JSON",
  config_json_entry: "Config JSON",
  strategy: "Strategy",
  trading_mode: "Trading mode",
  margin_mode: "Margin mode",
  max_open_trades: "Max open trades",
  export: "Export",
  source_files: "Source files",
  parameter_files: "Parameter files",
  strategy_names: "Strategy names",
  parameter_keys: "Parameter keys",
  entry: "Entry",
  row_count: "Rows",
  total_row_count: "Total rows",
  frame_count: "Frames",
  column_count: "Columns",
  columns: "Column list",
  date_start: "Start",
  date_end: "End",
  export_count: "Exports",
  strategies: "Strategies",
  currencies: "Currencies",
  currency_count: "Currency count",
  entries: "Entries",
  unreadable_entries: "Unreadable",
  inspection_status: "Inspection",
  pair_change_preview: "Pair moves",
  best_pair: "Best pair",
  best_pair_change_pct: "Best pair move",
  worst_pair: "Worst pair",
  worst_pair_change_pct: "Worst pair move",
  positive_pair_count: "Positive pairs",
  negative_pair_count: "Negative pairs",
  start_value: "Start value",
  end_value: "End value",
  change_pct: "Change",
  total_quote_start: "Quote start",
  total_quote_end: "Quote end",
  total_quote_high: "Quote high",
  total_quote_low: "Quote low",
  currency_quote_preview: "Currency quote preview",
  latest_balance: "Latest balance",
  latest_quote_value: "Latest quote value",
  strategy_row_preview: "Strategy rows",
  pair_row_preview: "Pair rows",
  semantic_columns: "Semantic columns",
  enter_tag_counts: "Entry tag counts",
  reason_counts: "Reason counts",
  exit_reason_counts: "Exit reason counts",
};

const benchmarkArtifactSectionOrder = [
  "benchmark_story",
  "zip_contents",
  "zip_config",
  "zip_strategy_bundle",
  "zip_market_change",
  "zip_wallet_exports",
  "zip_signal_exports",
  "zip_rejected_exports",
  "zip_exited_exports",
  "metadata",
  "strategy_comparison",
  "pair_metrics",
  "pair_extremes",
  "enter_tag_metrics",
  "exit_reason_metrics",
  "mixed_tag_metrics",
  "left_open_metrics",
  "periodic_breakdown",
  "daily_profit",
  "wallet_stats",
] as const;

const benchmarkArtifactSectionLabels: Record<string, string> = {
  benchmark_story: "Benchmark narrative",
  zip_contents: "Zip contents",
  zip_config: "Embedded config",
  zip_strategy_bundle: "Strategy bundle",
  zip_market_change: "Market change export",
  zip_wallet_exports: "Wallet exports",
  zip_signal_exports: "Signal exports",
  zip_rejected_exports: "Rejected exports",
  zip_exited_exports: "Exited exports",
  metadata: "Metadata",
  strategy_comparison: "Strategy comparison",
  pair_metrics: "Pair metrics",
  pair_extremes: "Pair extremes",
  enter_tag_metrics: "Entry tags",
  exit_reason_metrics: "Exit reasons",
  mixed_tag_metrics: "Mixed tags",
  left_open_metrics: "Left open",
  periodic_breakdown: "Periodic breakdown",
  daily_profit: "Daily profit",
  wallet_stats: "Wallet stats",
};

function formatBenchmarkArtifactSummaryEntries(summary: Record<string, unknown>) {
  return Object.entries(summary)
    .map(([key, value]) => [key, formatBenchmarkArtifactSummaryValue(key, value)] as const)
    .filter(([, value]) => value !== null)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSummarySortIndex(leftKey);
      const rightIndex = benchmarkArtifactSummarySortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSummarySortIndex(key: string) {
  const index = benchmarkArtifactSummaryOrder.indexOf(key as (typeof benchmarkArtifactSummaryOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSummaryOrder.length + 100;
}

function formatBenchmarkArtifactSummaryLabel(key: string) {
  return benchmarkArtifactSummaryLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSummaryValue(key: string, value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    if (key.endsWith("_pct")) {
      return `${value}%`;
    }
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function formatBenchmarkArtifactSectionEntries(sections: Record<string, Record<string, unknown>>) {
  return Object.entries(sections)
    .map(([key, section]) => [key, formatBenchmarkArtifactSectionLines(section)] as const)
    .filter(([, lines]) => lines.length > 0)
    .sort(([leftKey], [rightKey]) => {
      const leftIndex = benchmarkArtifactSectionSortIndex(leftKey);
      const rightIndex = benchmarkArtifactSectionSortIndex(rightKey);
      if (leftIndex === rightIndex) {
        return leftKey.localeCompare(rightKey);
      }
      return leftIndex - rightIndex;
    });
}

function benchmarkArtifactSectionSortIndex(key: string) {
  const index = benchmarkArtifactSectionOrder.indexOf(key as (typeof benchmarkArtifactSectionOrder)[number]);
  if (index >= 0) {
    return index;
  }
  return benchmarkArtifactSectionOrder.length + 100;
}

function formatBenchmarkArtifactSectionLabel(key: string) {
  return benchmarkArtifactSectionLabels[key] ?? key.replaceAll("_", " ");
}

function formatBenchmarkArtifactSectionLines(section: Record<string, unknown>) {
  return Object.entries(section)
    .map(([key, value]) => {
      const inlineValue = formatBenchmarkArtifactSectionValue(value);
      if (inlineValue === null) {
        return null;
      }
      return `${formatBenchmarkArtifactSummaryLabel(key)}: ${inlineValue}`;
    })
    .filter((line): line is string => line !== null);
}

function formatBenchmarkArtifactSectionValue(value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return null;
    }
    const preview = value.slice(0, 3).map((item) => formatBenchmarkArtifactInlineValue(item)).join(" | ");
    if (value.length > 3) {
      return `${preview} | +${value.length - 3} more`;
    }
    return preview;
  }
  if (typeof value === "object") {
    return formatBenchmarkArtifactInlineValue(value);
  }
  return String(value);
}

function formatBenchmarkArtifactInlineValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatBenchmarkArtifactInlineValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, nestedValue]) => {
        const formattedValue = formatBenchmarkArtifactSummaryValue(key, nestedValue);
        if (formattedValue === null) {
          return null;
        }
        return `${formatBenchmarkArtifactSummaryLabel(key)}=${formattedValue}`;
      })
      .filter((entry): entry is string => entry !== null)
      .join(", ");
  }
  return String(value);
}
