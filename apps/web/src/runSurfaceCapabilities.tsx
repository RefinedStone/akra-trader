import type {
  ComparisonScoreSection,
  RunListBoundaryContract,
  RunListBoundaryGroupKey,
  RunListBoundarySurfaceId,
  RunSurfaceCapabilities,
  RunSurfaceCapabilityFamily,
  RunSurfaceCapabilityFamilyContract,
  RunSurfaceCapabilityFamilyKey,
  RunSurfaceCapabilitySchemaContract,
  RunSurfaceCapabilitySurfaceKey,
  RunSurfaceCollectionQueryContract,
  RunSurfaceSharedContract,
  RunSurfaceSubresourceContract,
} from "./controlRoomDefinitions";

const RUN_LIST_BOUNDARY_CONTRACT: RunListBoundaryContract = {
  scope: "run_list",
  surfaces: {
    cancel_order: {
      eligibility: "operational",
      group: "operational_order_actions",
      label: "Cancel order",
    },
    compare_toggle: {
      eligibility: "operational",
      group: "operational_workflow",
      label: "Add/remove compare",
    },
    drawdown: {
      eligibility: "eligible",
      group: "eligible_metrics",
      label: "Drawdown",
    },
    lane: {
      eligibility: "supporting",
      group: "supporting_identity",
      label: "Lane",
    },
    lifecycle: {
      eligibility: "supporting",
      group: "supporting_identity",
      label: "Lifecycle",
    },
    mode: {
      eligibility: "supporting",
      group: "supporting_identity",
      label: "Mode",
    },
    replace_order: {
      eligibility: "operational",
      group: "operational_order_actions",
      label: "Replace order",
    },
    rerun: {
      eligibility: "operational",
      group: "operational_workflow",
      label: "Rerun",
    },
    return: {
      eligibility: "eligible",
      group: "eligible_metrics",
      label: "Return",
    },
    stop: {
      eligibility: "operational",
      group: "operational_workflow",
      label: "Stop",
    },
    trades: {
      eligibility: "eligible",
      group: "eligible_metrics",
      label: "Trades",
    },
    version: {
      eligibility: "supporting",
      group: "supporting_identity",
      label: "Version",
    },
    win_rate: {
      eligibility: "eligible",
      group: "eligible_metrics",
      label: "Win rate",
    },
  } satisfies RunListBoundaryContract["surfaces"],
  groups: {
    eligible_metrics: {
      copy: "These surfaces participate in comparison scoring or drill-back, so they remain comparison-eligible.",
      eligibility: "eligible",
      surface_ids: ["return", "drawdown", "win_rate", "trades"],
      title: "Comparison-eligible",
    },
    operational_order_actions: {
      copy: "Replace and cancel actions mutate order state, so they stay outside comparison drill-back even when the preview rows are comparison-eligible.",
      eligibility: "operational",
      surface_ids: ["cancel_order", "replace_order"],
      title: "Operational only",
    },
    operational_workflow: {
      copy: "Workflow controls change selection or execution state, so they remain outside comparison-eligible deep-link scope.",
      eligibility: "operational",
      surface_ids: ["compare_toggle", "rerun", "stop"],
      title: "Operational only",
    },
    supporting_identity: {
      copy: "Weak-signal identity and routing context stay descriptive only and do not create comparison deep-links.",
      eligibility: "supporting",
      surface_ids: ["mode", "lane", "lifecycle", "version"],
      title: "Supporting only",
    },
  } satisfies RunListBoundaryContract["groups"],
};

const DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER: RunListBoundaryGroupKey[] = [
  "eligible_metrics",
  "supporting_identity",
  "operational_workflow",
  "operational_order_actions",
];

const DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER: RunSurfaceCapabilityFamilyKey[] = [
  "comparison_eligibility",
  "strategy_schema",
  "collection_query",
  "provenance_semantics",
  "execution_controls",
];

const DEFAULT_RUN_SURFACE_SUBRESOURCE_CONTRACTS: Array<{
  subresource_key: string;
  body_key: string;
  response_title: string;
  route_path: string;
  route_name: string;
}> = [
  {
    subresource_key: "orders",
    body_key: "orders",
    response_title: "Run order list",
    route_name: "get_run_orders",
    route_path: "/runs/{run_id}/orders",
  },
  {
    subresource_key: "positions",
    body_key: "positions",
    response_title: "Run positions",
    route_name: "get_run_positions",
    route_path: "/runs/{run_id}/positions",
  },
  {
    subresource_key: "metrics",
    body_key: "metrics",
    response_title: "Run metrics",
    route_name: "get_run_metrics",
    route_path: "/runs/{run_id}/metrics",
  },
];

const DEFAULT_RUN_SURFACE_CAPABILITY_DISCOVERY: RunSurfaceCapabilities["discovery"] = {
  shared_contracts: [
    {
      contract_key: "schema:run-surface-capabilities",
      contract_kind: "schema_metadata",
      title: "Run-surface capability contract",
      summary:
        "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level enforcement rules.",
      source_of_truth: "run_surface_capabilities.discovery",
      version: "run-surface-capabilities.v14",
      related_family_keys: [
        "comparison_eligibility",
        "strategy_schema",
        "collection_query",
        "provenance_semantics",
        "execution_controls",
      ],
      member_keys: [
        "family:comparison_eligibility",
        "family:strategy_schema",
        "family:collection_query",
        "family:provenance_semantics",
        "family:execution_controls",
        "group:eligible_metrics",
        "group:supporting_identity",
        "group:operational_workflow",
        "group:operational_order_actions",
      ],
      schema_detail: {
        comparison_eligibility_group_order: DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER,
        family_order: DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
        run_subresource_contract_keys: DEFAULT_RUN_SURFACE_SUBRESOURCE_CONTRACTS.map(
          (contract) => `subresource:${contract.subresource_key}`,
        ),
        collection_query_contract_keys: ["query_collection:run_list"],
      },
    },
    {
      contract_key: "family:comparison_eligibility",
      contract_kind: "capability_family",
      title: "Comparison boundary contract",
      summary: "Defines which run-list surfaces are comparison-eligible, supporting-only, or operational-only.",
      source_of_truth: "comparison_eligibility_contract",
      version: null,
      related_family_keys: ["comparison_eligibility"],
      member_keys: ["run_list_metric_tiles", "boundary_note_panels", "order_workflow_gates"],
    },
    {
      contract_key: "family:strategy_schema",
      contract_kind: "capability_family",
      title: "Strategy schema discovery",
      summary: "Publishes typed strategy parameter schema and semantic metadata used by preset and revision workflows.",
      source_of_truth: "strategy_catalog",
      version: null,
      related_family_keys: ["strategy_schema"],
      member_keys: [
        "strategy_catalog_cards",
        "preset_parameter_editor",
        "preset_revision_semantic_diffs",
      ],
    },
    {
      contract_key: "family:provenance_semantics",
      contract_kind: "capability_family",
      title: "Run provenance semantics",
      summary: "Carries semantic run context into snapshot, provenance, artifact, and comparison drill-back surfaces.",
      source_of_truth: "run_provenance_snapshot",
      version: null,
      related_family_keys: ["provenance_semantics"],
      member_keys: [
        "run_strategy_snapshot",
        "reference_provenance_panels",
        "benchmark_artifact_summaries",
      ],
    },
    {
      contract_key: "family:collection_query",
      contract_kind: "capability_family",
      title: "Collection query discovery",
      summary: "Publishes collection expression schemas, parameter domains, enum-source metadata, and parameterized predicate-template authoring metadata used by typed query builders.",
      source_of_truth: "standalone_surface_runtime_bindings.collection_path_specs",
      version: null,
      related_family_keys: ["collection_query"],
      member_keys: [
        "collection_query_discovery_panels",
        "collection_expression_builders",
        "collection_parameter_domain_pickers",
      ],
    },
    {
      contract_key: "family:execution_controls",
      contract_kind: "capability_family",
      title: "Execution control gating",
      summary: "Documents which interactive controls mutate workflow or venue state and therefore stay outside comparison semantics.",
      source_of_truth: "run_surface_capability_endpoint",
      version: null,
      related_family_keys: ["execution_controls"],
      member_keys: [
        "rerun_and_stop_controls",
        "compare_selection_workflow",
        "order_replace_cancel_actions",
      ],
    },
    {
      contract_key: "query_collection:run_list",
      contract_kind: "query_collection_schema",
      title: "Run list collection query schema",
      summary: "Advertises typed collection expression schemas, element fields, and parameter domain metadata for the `run_list` surface.",
      source_of_truth: "standalone_surface_runtime_bindings.collection_path_specs",
      version: null,
      related_family_keys: ["collection_query"],
      member_keys: [
        "collection:orders",
        "collection:provenance.market_data_by_symbol.{symbol_key}.issues",
        "parameter_domain:symbol_key",
      ],
      schema_detail: {
        surface_key: "run_list",
        route_path: "/runs",
        expression_param: "filter_expr",
        expression_authoring: {
          predicate_refs: {
            registry_field: "predicates",
            reference_field: "predicate_ref",
          },
          predicate_templates: {
            registry_field: "predicate_templates",
            template_field: "template",
            parameters_field: "parameters",
            bindings_field: "bindings",
            binding_reference_shape: {
              binding: "<parameter_name>",
            },
          },
          collection_nodes: {
            field: "collection",
            shape: {
              path: "<collection path>",
              path_template: "<collection path template>",
              bindings: {
                "<parameter_key>": "<value or binding reference>",
              },
              quantifier: "any|all|none",
            },
          },
        },
        collection_schemas: [
          {
            path: ["orders"],
            path_template: ["orders"],
            label: "Run orders",
            collection_kind: "object_collection",
            item_kind: "order",
            filter_keys: ["order_status", "order_type"],
            description: "Evaluates predicates against individual run order objects.",
            parameters: [],
            element_schema: [],
          },
          {
            path: ["provenance", "market_data_by_symbol", "issues"],
            path_template: ["provenance", "market_data_by_symbol", "{symbol_key}", "issues"],
            label: "Market-data issues",
            collection_kind: "nested_collection",
            item_kind: "issue_text",
            filter_keys: ["issue_text"],
            description: "Evaluates predicates against flattened issue strings across market-data lineage entries.",
            parameters: [
              {
                key: "symbol_key",
                kind: "dynamic_map_key",
                description: "Symbol-keyed lineage entry inside `market_data_by_symbol`.",
                examples: ["binance:BTC/USDT"],
                domain: {
                  key: "market_data_symbol_key",
                  source: "run.provenance.market_data_by_symbol",
                  values: ["binance:BTC/USDT"],
                  enum_source: {
                    kind: "dynamic_map_keys",
                    surface_key: "run_list",
                    path: ["provenance", "market_data_by_symbol"],
                  },
                },
              },
            ],
            element_schema: [],
          },
        ],
        parameter_domains: [
          {
            parameter_key: "symbol_key",
            parameter_kind: "dynamic_map_key",
            collection_label: "Market-data issues",
            collection_path: ["provenance", "market_data_by_symbol", "issues"],
            collection_path_template: ["provenance", "market_data_by_symbol", "{symbol_key}", "issues"],
            surface_key: "run_list",
            domain: {
              key: "market_data_symbol_key",
              source: "run.provenance.market_data_by_symbol",
              values: ["binance:BTC/USDT"],
              enum_source: {
                kind: "dynamic_map_keys",
                surface_key: "run_list",
                path: ["provenance", "market_data_by_symbol"],
              },
            },
          },
        ],
      },
    },
    {
      contract_key: "subresource:orders",
      contract_kind: "run_subresource",
      title: "Run order list",
      summary: "Declarative route binding and serializer contract for the standalone `orders` run subresource.",
      source_of_truth: "run_subresource_contracts",
      version: null,
      related_family_keys: [],
      member_keys: ["body:orders", "route:get_run_orders"],
      schema_detail: {
        body_key: "orders",
        route_path: "/runs/{run_id}/orders",
        route_name: "get_run_orders",
      },
    },
    {
      contract_key: "subresource:positions",
      contract_kind: "run_subresource",
      title: "Run positions",
      summary: "Declarative route binding and serializer contract for the standalone `positions` run subresource.",
      source_of_truth: "run_subresource_contracts",
      version: null,
      related_family_keys: [],
      member_keys: ["body:positions", "route:get_run_positions"],
      schema_detail: {
        body_key: "positions",
        route_path: "/runs/{run_id}/positions",
        route_name: "get_run_positions",
      },
    },
    {
      contract_key: "subresource:metrics",
      contract_kind: "run_subresource",
      title: "Run metrics",
      summary: "Declarative route binding and serializer contract for the standalone `metrics` run subresource.",
      source_of_truth: "run_subresource_contracts",
      version: null,
      related_family_keys: [],
      member_keys: ["body:metrics", "route:get_run_metrics"],
      schema_detail: {
        body_key: "metrics",
        route_path: "/runs/{run_id}/metrics",
        route_name: "get_run_metrics",
      },
    },
  ],
};

const DEFAULT_RUN_SURFACE_CAPABILITY_FAMILIES: RunSurfaceCapabilityFamily[] = [
  {
    family_key: "comparison_eligibility",
    title: "Comparison boundary contract",
    summary: "Defines which run-list surfaces are comparison-eligible, supporting-only, or operational-only.",
    ui_surfaces: ["Run-list metric tiles", "Boundary note panels", "Order workflow gates"],
    schema_sources: [
      "Run-surface capability endpoint",
      "Comparison score drill-back wiring",
      "Run-list boundary notes",
    ],
    discovery_flow: "Shared UI contract panel and run-list boundary notes.",
    policy: {
      applies_to: ["metrics", "supporting_identity", "workflow_controls", "order_actions"],
      policy_key: "comparison_surface_allowlist",
      policy_mode: "allowlist",
      source_of_truth: "comparison_eligibility_contract",
    },
    enforcement: {
      enforcement_points: ["run_list_metric_gating", "drill_back_selection", "boundary_note_rendering"],
      fallback_behavior: "non_eligible_surfaces_remain_descriptive_only",
      level: "hard_gate",
      source_of_truth: "run_surface_capability_endpoint",
    },
    surface_rules: [
      {
        rule_key: "run_list_metric_tile_gate",
        surface_key: "run_list_metric_tiles",
        surface_label: "Run-list metric tiles",
        enforcement_point: "run_list_metric_gating",
        enforcement_mode: "eligible_only_drillback",
        level: "hard_gate",
        fallback_behavior: "render_metric_as_descriptive_only_when_surface_is_not_eligible",
        source_of_truth: "comparison_eligibility_contract.surfaces",
      },
      {
        rule_key: "boundary_note_group_annotation",
        surface_key: "boundary_note_panels",
        surface_label: "Boundary note panels",
        enforcement_point: "boundary_note_rendering",
        enforcement_mode: "group_boundary_annotation",
        level: "hard_gate",
        fallback_behavior: "render_shared_boundary_copy_without_surface_specific_drill_links",
        source_of_truth: "comparison_eligibility_contract.groups",
      },
      {
        rule_key: "order_workflow_score_link_exclusion",
        surface_key: "order_workflow_gates",
        surface_label: "Order workflow gates",
        enforcement_point: "drill_back_selection",
        enforcement_mode: "score_link_exclusion",
        level: "hard_gate",
        fallback_behavior: "keep_operational_workflow_controls_non_selectable",
        source_of_truth: "comparison_eligibility_contract.groups",
      },
    ],
  },
  {
    family_key: "strategy_schema",
    title: "Strategy schema discovery",
    summary: "Publishes typed strategy parameter schema and semantic metadata used by preset and revision workflows.",
    ui_surfaces: ["Strategy catalog cards", "Preset parameter editor", "Preset revision semantic diffs"],
    schema_sources: [
      "Strategy parameter_schema",
      "Strategy catalog_semantics",
      "Supported timeframe metadata",
    ],
    discovery_flow: "Strategy catalog and preset editor schema hints.",
    policy: {
      applies_to: ["strategy_catalog", "preset_editor", "preset_revision_diff"],
      policy_key: "typed_strategy_schema_advertisement",
      policy_mode: "schema_contract",
      source_of_truth: "strategy_catalog",
    },
    enforcement: {
      enforcement_points: ["schema_hint_rendering", "preset_diff_semantics", "parameter_editor_defaults"],
      fallback_behavior: "fallback_to_freeform_parameter_entry_when_schema_missing",
      level: "advisory",
      source_of_truth: "strategy_metadata.parameter_schema",
    },
    surface_rules: [
      {
        rule_key: "strategy_catalog_schema_hints",
        surface_key: "strategy_catalog_cards",
        surface_label: "Strategy catalog cards",
        enforcement_point: "schema_hint_rendering",
        enforcement_mode: "schema_hint_annotation",
        level: "advisory",
        fallback_behavior: "render_strategy_summary_without_typed_parameter_hints",
        source_of_truth: "strategy_metadata.parameter_schema",
      },
      {
        rule_key: "preset_editor_default_hydration",
        surface_key: "preset_parameter_editor",
        surface_label: "Preset parameter editor",
        enforcement_point: "parameter_editor_defaults",
        enforcement_mode: "typed_default_hydration",
        level: "advisory",
        fallback_behavior: "fallback_to_freeform_json_parameter_entry",
        source_of_truth: "strategy_metadata.parameter_schema",
      },
      {
        rule_key: "preset_revision_schema_diff",
        surface_key: "preset_revision_semantic_diffs",
        surface_label: "Preset revision semantic diffs",
        enforcement_point: "preset_diff_semantics",
        enforcement_mode: "schema_aware_delta_annotation",
        level: "advisory",
        fallback_behavior: "render_generic_revision_value_deltas",
        source_of_truth: "strategy_catalog_semantics",
      },
    ],
  },
  {
    family_key: "collection_query",
    title: "Collection query discovery",
    summary: "Publishes collection expression schemas, parameter domains, enum-source metadata, and parameterized predicate-template authoring metadata used by typed query builders.",
    ui_surfaces: [
      "Collection query discovery panels",
      "Collection expression builders",
      "Collection parameter domain pickers",
    ],
    schema_sources: [
      "Collection path schemas",
      "Collection element filter schemas",
      "Collection parameter domain metadata",
    ],
    discovery_flow: "Typed query discovery panels and collection expression builders.",
    policy: {
      applies_to: ["collection_schema", "parameter_domains", "query_builders"],
      policy_key: "typed_collection_query_discovery",
      policy_mode: "schema_contract",
      source_of_truth: "standalone_surface_runtime_bindings.collection_path_specs",
    },
    enforcement: {
      enforcement_points: [
        "collection_schema_discovery",
        "parameter_domain_rendering",
        "collection_shape_validation",
      ],
      fallback_behavior: "fallback_to_raw_filter_expression_authoring_when_collection_query_metadata_is_missing",
      level: "advisory",
      source_of_truth: "typed_query_collection_schemas",
    },
    surface_rules: [
      {
        rule_key: "collection_query_schema_panel",
        surface_key: "collection_query_discovery_panels",
        surface_label: "Collection query discovery panels",
        enforcement_point: "collection_schema_discovery",
        enforcement_mode: "collection_schema_advertisement",
        level: "advisory",
        fallback_behavior: "omit_collection_query_contract_detail_when_discovery_metadata_is_missing",
        source_of_truth: "standalone_surface_runtime_bindings.collection_path_specs",
      },
      {
        rule_key: "collection_expression_builder_schema",
        surface_key: "collection_expression_builders",
        surface_label: "Collection expression builders",
        enforcement_point: "collection_shape_validation",
        enforcement_mode: "shape_validated_builder_contract",
        level: "advisory",
        fallback_behavior: "allow_raw_collection_paths_without_builder_guidance",
        source_of_truth: "typed_query_collection_schema_validation",
      },
      {
        rule_key: "collection_parameter_domain_enum_source",
        surface_key: "collection_parameter_domain_pickers",
        surface_label: "Collection parameter domain pickers",
        enforcement_point: "parameter_domain_rendering",
        enforcement_mode: "domain_and_enum_source_annotation",
        level: "advisory",
        fallback_behavior: "render_parameter_domains_without_enum_source_hints",
        source_of_truth: "collection_query_parameter_domains",
      },
    ],
  },
  {
    family_key: "provenance_semantics",
    title: "Run provenance semantics",
    summary: "Carries semantic run context into snapshot, provenance, artifact, and comparison drill-back surfaces.",
    ui_surfaces: ["Run strategy snapshot", "Reference provenance panels", "Benchmark artifact summaries"],
    schema_sources: [
      "Run provenance strategy snapshot",
      "Benchmark artifact metadata",
      "Catalog semantics snapshots",
    ],
    discovery_flow: "Run cards, provenance panels, and comparison deep-link restoration.",
    policy: {
      applies_to: ["run_snapshot", "artifact_summary", "comparison_deep_link"],
      policy_key: "provenance_semantic_snapshot",
      policy_mode: "snapshot_contract",
      source_of_truth: "run_provenance_snapshot",
    },
    enforcement: {
      enforcement_points: ["snapshot_serialization", "provenance_panel_rendering", "deep_link_restore"],
      fallback_behavior: "render_basic_provenance_without_semantic_focus_when_snapshot_missing",
      level: "snapshot_required",
      source_of_truth: "run_provenance.strategy",
    },
    surface_rules: [
      {
        rule_key: "run_snapshot_semantic_embed",
        surface_key: "run_strategy_snapshot",
        surface_label: "Run strategy snapshot",
        enforcement_point: "snapshot_serialization",
        enforcement_mode: "semantic_snapshot_embed",
        level: "snapshot_required",
        fallback_behavior: "render_snapshot_without_catalog_semantics",
        source_of_truth: "run_provenance.strategy",
      },
      {
        rule_key: "reference_provenance_semantic_render",
        surface_key: "reference_provenance_panels",
        surface_label: "Reference provenance panels",
        enforcement_point: "provenance_panel_rendering",
        enforcement_mode: "semantic_source_highlighting",
        level: "snapshot_required",
        fallback_behavior: "render_provenance_without_semantic_source_emphasis",
        source_of_truth: "run_provenance.strategy.catalog_semantics",
      },
      {
        rule_key: "artifact_deep_link_restore",
        surface_key: "benchmark_artifact_summaries",
        surface_label: "Benchmark artifact summaries",
        enforcement_point: "deep_link_restore",
        enforcement_mode: "artifact_subfocus_restore",
        level: "snapshot_required",
        fallback_behavior: "restore_artifact_panel_without_subfocus_state",
        source_of_truth: "benchmark_artifact_metadata",
      },
    ],
  },
  {
    family_key: "execution_controls",
    title: "Execution control gating",
    summary: "Documents which interactive controls mutate workflow or venue state and therefore stay outside comparison semantics.",
    ui_surfaces: ["Rerun and stop controls", "Compare selection workflow", "Order replace/cancel actions"],
    schema_sources: [
      "Run-surface capability endpoint",
      "Order lifecycle summaries",
      "Runtime state transitions",
    ],
    discovery_flow: "Shared UI control gating and operational-only boundary notes.",
    policy: {
      applies_to: ["rerun_controls", "stop_controls", "order_replace_cancel"],
      policy_key: "operational_control_exclusion",
      policy_mode: "mutation_gate",
      source_of_truth: "run_surface_capability_endpoint",
    },
    enforcement: {
      enforcement_points: ["button_visibility", "order_action_boundary_notes", "comparison_selection_exclusion"],
      fallback_behavior: "controls_remain_operational_only_and_do_not_bind_score_links",
      level: "hard_gate",
      source_of_truth: "run_surface_capability_endpoint",
    },
    surface_rules: [
      {
        rule_key: "rerun_stop_button_gate",
        surface_key: "rerun_and_stop_controls",
        surface_label: "Rerun and stop controls",
        enforcement_point: "button_visibility",
        enforcement_mode: "mutation_control_gate",
        level: "hard_gate",
        fallback_behavior: "render_controls_as_operational_only_without_score_links",
        source_of_truth: "run_surface_capability_endpoint",
      },
      {
        rule_key: "compare_selection_operational_exclusion",
        surface_key: "compare_selection_workflow",
        surface_label: "Compare selection workflow",
        enforcement_point: "comparison_selection_exclusion",
        enforcement_mode: "selection_exclusion_gate",
        level: "hard_gate",
        fallback_behavior: "exclude_mutating_controls_from_comparison_selection",
        source_of_truth: "run_surface_capability_endpoint",
      },
      {
        rule_key: "order_replace_cancel_boundary_note",
        surface_key: "order_replace_cancel_actions",
        surface_label: "Order replace/cancel actions",
        enforcement_point: "order_action_boundary_notes",
        enforcement_mode: "operational_boundary_annotation",
        level: "hard_gate",
        fallback_behavior: "render_order_actions_as_operational_only",
        source_of_truth: "order_lifecycle_summary",
      },
    ],
  },
];

export function getRunListBoundaryContractSnapshot(contract?: RunListBoundaryContract | null) {
  if (!contract || contract.scope !== "run_list") {
    return RUN_LIST_BOUNDARY_CONTRACT;
  }
  return contract;
}

function getRunSurfaceCapabilityDiscovery(capabilities?: RunSurfaceCapabilities | null) {
  return capabilities?.discovery ?? DEFAULT_RUN_SURFACE_CAPABILITY_DISCOVERY;
}

function getRunSurfaceCapabilityFamilies(): RunSurfaceCapabilityFamily[] {
  return DEFAULT_RUN_SURFACE_CAPABILITY_FAMILIES;
}

function getRunSurfaceSchemaDetailStringArray(
  schemaDetail: Record<string, unknown> | undefined,
  key: string,
  fallback: string[],
) {
  const value = schemaDetail?.[key];
  if (!Array.isArray(value)) {
    return fallback;
  }
  const normalized = value.filter((item): item is string => typeof item === "string");
  return normalized.length ? normalized : fallback;
}

export function getRunSurfaceSharedContracts(
  capabilities?: RunSurfaceCapabilities | null,
): RunSurfaceSharedContract[] {
  const discovery = getRunSurfaceCapabilityDiscovery(capabilities);
  const families = getRunSurfaceCapabilityFamilies();
  const sharedByKey = new Map(
    (discovery.shared_contracts ?? []).map((contract) => [contract.contract_key, contract] as const),
  );
  const schemaContract = sharedByKey.get("schema:run-surface-capabilities");
  const normalizedSchema: RunSurfaceCapabilitySchemaContract = {
    contract_key: "schema:run-surface-capabilities",
    contract_kind: "schema_metadata",
    title: schemaContract?.title ?? "Run-surface capability contract",
    summary:
      schemaContract?.summary
      ?? "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level enforcement rules.",
    source_of_truth: schemaContract?.source_of_truth ?? "run_surface_capabilities.discovery",
    version: schemaContract?.version ?? "run-surface-capabilities.v14",
    discovery_flow: schemaContract?.discovery_flow ?? null,
    related_family_keys: schemaContract?.related_family_keys?.length
      ? schemaContract.related_family_keys
      : [...DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER],
    member_keys: schemaContract?.member_keys?.length
      ? schemaContract.member_keys
      : [
          ...DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER.map((familyKey) => `family:${familyKey}`),
          ...DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER.map((groupKey) => `group:${groupKey}`),
        ],
    ui_surfaces: schemaContract?.ui_surfaces ?? [],
    schema_sources: schemaContract?.schema_sources ?? [],
    policy: schemaContract?.policy ?? null,
    enforcement: schemaContract?.enforcement ?? null,
    surface_rules: schemaContract?.surface_rules ?? [],
    schema_detail: {
      ...(schemaContract?.schema_detail ?? {}),
      comparison_eligibility_group_order: getRunSurfaceSchemaDetailStringArray(
        schemaContract?.schema_detail,
        "comparison_eligibility_group_order",
        DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER,
      ),
      family_order: getRunSurfaceSchemaDetailStringArray(
        schemaContract?.schema_detail,
        "family_order",
        DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
      ),
      run_subresource_contract_keys: getRunSurfaceSchemaDetailStringArray(
        schemaContract?.schema_detail,
        "run_subresource_contract_keys",
        DEFAULT_RUN_SURFACE_SUBRESOURCE_CONTRACTS.map(
          (contract) => `subresource:${contract.subresource_key}`,
        ),
      ),
      collection_query_contract_keys: getRunSurfaceSchemaDetailStringArray(
        schemaContract?.schema_detail,
        "collection_query_contract_keys",
        ["query_collection:run_list"],
      ),
    },
  };
  const familyContracts: RunSurfaceCapabilityFamilyContract[] = families.map((family) => {
    const sharedContract = sharedByKey.get(`family:${family.family_key}`);
    return {
      contract_key: sharedContract?.contract_key ?? `family:${family.family_key}`,
      contract_kind: "capability_family",
      title: sharedContract?.title ?? family.title,
      summary: sharedContract?.summary ?? family.summary,
      source_of_truth: sharedContract?.source_of_truth ?? family.policy.source_of_truth,
      version: sharedContract?.version ?? null,
      discovery_flow: sharedContract?.discovery_flow ?? family.discovery_flow,
      related_family_keys: sharedContract?.related_family_keys?.length
        ? sharedContract.related_family_keys
        : [family.family_key],
      member_keys: sharedContract?.member_keys?.length
        ? sharedContract.member_keys
        : family.surface_rules.map((rule) => rule.surface_key),
      ui_surfaces: sharedContract?.ui_surfaces?.length ? sharedContract.ui_surfaces : family.ui_surfaces,
      schema_sources: sharedContract?.schema_sources?.length
        ? sharedContract.schema_sources
        : family.schema_sources,
      policy: sharedContract?.policy ?? family.policy,
      enforcement: sharedContract?.enforcement ?? family.enforcement,
      surface_rules: sharedContract?.surface_rules?.length ? sharedContract.surface_rules : family.surface_rules,
      schema_detail: sharedContract?.schema_detail ?? {},
    };
  });
  const subresourceContracts: RunSurfaceSubresourceContract[] = DEFAULT_RUN_SURFACE_SUBRESOURCE_CONTRACTS.map(
    (contract) => {
      const sharedContract = sharedByKey.get(`subresource:${contract.subresource_key}`);
      return {
        contract_key: sharedContract?.contract_key ?? `subresource:${contract.subresource_key}`,
        contract_kind: "run_subresource",
        title: sharedContract?.title ?? contract.response_title,
        summary:
          sharedContract?.summary
          ?? `Declarative route binding and serializer contract for the standalone \`${contract.subresource_key}\` run subresource.`,
        source_of_truth: sharedContract?.source_of_truth ?? "run_subresource_contracts",
        version: sharedContract?.version ?? null,
        discovery_flow: sharedContract?.discovery_flow ?? null,
        related_family_keys: sharedContract?.related_family_keys ?? [],
        member_keys: sharedContract?.member_keys?.length
          ? sharedContract.member_keys
          : [`body:${contract.body_key}`, `route:${contract.route_name}`],
        ui_surfaces: sharedContract?.ui_surfaces ?? [],
        schema_sources: sharedContract?.schema_sources ?? [],
        policy: sharedContract?.policy ?? null,
        enforcement: sharedContract?.enforcement ?? null,
        surface_rules: sharedContract?.surface_rules ?? [],
        schema_detail: {
          body_key: contract.body_key,
          route_path: contract.route_path,
          route_name: contract.route_name,
          ...(sharedContract?.schema_detail ?? {}),
        },
      };
    },
  );
  const extraSharedContracts = (discovery.shared_contracts ?? []).filter(
    (contract) =>
      contract.contract_key !== "schema:run-surface-capabilities"
      && contract.contract_kind !== "capability_family"
      && contract.contract_kind !== "run_subresource",
  );
  return [normalizedSchema, ...familyContracts, ...extraSharedContracts, ...subresourceContracts];
}

export function getRunSurfaceCapabilitySchemaContract(
  capabilities?: RunSurfaceCapabilities | null,
): RunSurfaceCapabilitySchemaContract | null {
  return (
    getRunSurfaceSharedContracts(capabilities).find(
      (contract): contract is RunSurfaceCapabilitySchemaContract =>
        contract.contract_key === "schema:run-surface-capabilities" && contract.contract_kind === "schema_metadata",
    ) ?? null
  );
}

export function getRunSurfaceCapabilityFamilyOrder(capabilities?: RunSurfaceCapabilities | null) {
  return getRunSurfaceSchemaDetailStringArray(
    getRunSurfaceCapabilitySchemaContract(capabilities)?.schema_detail,
    "family_order",
    DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
  ).filter((familyKey): familyKey is RunSurfaceCapabilityFamilyKey =>
    DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER.includes(familyKey as RunSurfaceCapabilityFamilyKey),
  );
}

export function getRunSurfaceCapabilityGroupOrder(capabilities?: RunSurfaceCapabilities | null) {
  return getRunSurfaceSchemaDetailStringArray(
    getRunSurfaceCapabilitySchemaContract(capabilities)?.schema_detail,
    "comparison_eligibility_group_order",
    DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER,
  ).filter((groupKey): groupKey is RunListBoundaryGroupKey =>
    DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER.includes(groupKey as RunListBoundaryGroupKey),
  );
}

export function getRunSurfaceSubresourceContracts(capabilities?: RunSurfaceCapabilities | null) {
  return getRunSurfaceSharedContracts(capabilities).filter(
    (contract): contract is RunSurfaceSubresourceContract => contract.contract_kind === "run_subresource",
  );
}

export function getRunSurfaceCollectionQueryContracts(capabilities?: RunSurfaceCapabilities | null) {
  return getRunSurfaceSharedContracts(capabilities).filter(
    (contract): contract is RunSurfaceCollectionQueryContract =>
      contract.contract_kind === "query_collection_schema",
  );
}

export function getRunSurfaceCapabilityFamily(
  capabilities: RunSurfaceCapabilities | null | undefined,
  familyKey: RunSurfaceCapabilityFamilyKey,
) {
  return (
    getRunSurfaceSharedContracts(capabilities).find(
      (contract): contract is RunSurfaceCapabilityFamilyContract =>
        contract.contract_key === `family:${familyKey}` && contract.contract_kind === "capability_family",
    ) ?? null
  );
}

function getRunSurfaceCapabilitySurfaceRule(
  capabilities: RunSurfaceCapabilities | null | undefined,
  familyKey: RunSurfaceCapabilityFamilyKey,
  surfaceKey: RunSurfaceCapabilitySurfaceKey,
) {
  return (
    getRunSurfaceCapabilityFamily(capabilities, familyKey)?.surface_rules.find(
      (rule) => rule.surface_key === surfaceKey,
    ) ?? null
  );
}

function hasRunSurfaceCapabilitySurfaceRule(
  capabilities: RunSurfaceCapabilities | null | undefined,
  familyKey: RunSurfaceCapabilityFamilyKey,
  surfaceKey: RunSurfaceCapabilitySurfaceKey,
  enforcementPoint?: string,
) {
  const rule = getRunSurfaceCapabilitySurfaceRule(capabilities, familyKey, surfaceKey);
  if (!rule) {
    return false;
  }
  return !enforcementPoint || rule.enforcement_point === enforcementPoint;
}

export function shouldEnableRunListMetricDrillBack(
  surfaceId: RunListBoundarySurfaceId,
  capabilities: RunSurfaceCapabilities | null | undefined,
  contract?: RunListBoundaryContract | null,
) {
  return (
    hasRunSurfaceCapabilitySurfaceRule(
      capabilities,
      "comparison_eligibility",
      "run_list_metric_tiles",
      "run_list_metric_gating",
    )
    && isRunListComparisonEligibleSurface(surfaceId, contract)
  );
}

export function shouldEnableStrategyCatalogSchemaHints(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "strategy_schema",
    "strategy_catalog_cards",
    "schema_hint_rendering",
  );
}

export function shouldHydratePresetParameterDefaults(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "strategy_schema",
    "preset_parameter_editor",
    "parameter_editor_defaults",
  );
}

export function shouldEnableRunSnapshotSemantics(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "provenance_semantics",
    "run_strategy_snapshot",
    "snapshot_serialization",
  );
}

export function shouldEnableReferenceProvenanceSemantics(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "provenance_semantics",
    "reference_provenance_panels",
    "provenance_panel_rendering",
  );
}

export function shouldRenderWorkflowControlBoundaryNote(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return (
    hasRunSurfaceCapabilitySurfaceRule(
      capabilities,
      "execution_controls",
      "compare_selection_workflow",
      "comparison_selection_exclusion",
    )
    || hasRunSurfaceCapabilitySurfaceRule(
      capabilities,
      "execution_controls",
      "rerun_and_stop_controls",
      "button_visibility",
    )
  );
}

export function shouldRenderOrderActionBoundaryNote(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "execution_controls",
    "order_replace_cancel_actions",
    "order_action_boundary_notes",
  );
}

function getRunListBoundaryGroupContract(
  groupKey: RunListBoundaryGroupKey,
  contract?: RunListBoundaryContract | null,
) {
  const resolvedContract = getRunListBoundaryContractSnapshot(contract);
  const group = resolvedContract.groups[groupKey];
  return {
    ...group,
    surfaces: group.surface_ids.map((surfaceId) => resolvedContract.surfaces[surfaceId].label),
  };
}

export function getRunListBoundarySurfaceLabel(
  surfaceId: RunListBoundarySurfaceId,
  contract?: RunListBoundaryContract | null,
) {
  return getRunListBoundaryContractSnapshot(contract).surfaces[surfaceId].label;
}

function isRunListComparisonEligibleSurface(
  surfaceId: RunListBoundarySurfaceId,
  contract?: RunListBoundaryContract | null,
) {
  return getRunListBoundaryContractSnapshot(contract).surfaces[surfaceId].eligibility === "eligible";
}

export function RunListComparisonBoundaryNote({
  groupKey,
  contract,
}: {
  groupKey: RunListBoundaryGroupKey;
  contract?: RunListBoundaryContract | null;
}) {
  const resolvedContract = getRunListBoundaryGroupContract(groupKey, contract);
  return (
    <div className={`run-list-boundary-note ${resolvedContract.eligibility}`.trim()}>
      <div className="run-list-boundary-note-head">
        <span>{resolvedContract.title}</span>
        <p>{resolvedContract.copy}</p>
      </div>
      <div className="run-list-boundary-note-surfaces">
        {resolvedContract.surfaces.map((surface) => (
          <span className="run-list-boundary-note-surface" key={surface}>
            {surface}
          </span>
        ))}
      </div>
    </div>
  );
}
