from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

RUN_SURFACE_CAPABILITY_SCHEMA_TITLE = "Run-surface capability contract"
RUN_SURFACE_CAPABILITY_SCHEMA_SUMMARY = (
  "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, "
  "provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level enforcement rules."
)
RUN_SURFACE_CAPABILITY_SCHEMA_VERSION = "run-surface-capabilities.v14"
RUN_SURFACE_CAPABILITY_GROUP_ORDER = (
  "eligible_metrics",
  "supporting_identity",
  "operational_workflow",
  "operational_order_actions",
)
RUN_SURFACE_CAPABILITY_FAMILY_ORDER = (
  "comparison_eligibility",
  "strategy_schema",
  "collection_query",
  "provenance_semantics",
  "execution_controls",
)
RUN_SURFACE_SUBRESOURCE_CONTRACT_KEYS = (
  "subresource:orders",
  "subresource:positions",
  "subresource:metrics",
)
RUN_SURFACE_COLLECTION_QUERY_CONTRACT_KEYS = (
  "query_collection:run_list",
)

@dataclass(frozen=True)
class ComparisonEligibilitySurfaceContract:
  eligibility: str
  group: str
  label: str


@dataclass(frozen=True)
class ComparisonEligibilityGroupContract:
  copy: str
  eligibility: str
  surface_ids: tuple[str, ...]
  title: str


@dataclass(frozen=True)
class ComparisonEligibilityContract:
  scope: str = "run_list"
  surfaces: dict[str, ComparisonEligibilitySurfaceContract] = field(default_factory=dict)
  groups: dict[str, ComparisonEligibilityGroupContract] = field(default_factory=dict)


def default_comparison_eligibility_contract() -> ComparisonEligibilityContract:
  return ComparisonEligibilityContract(
    scope="run_list",
    surfaces={
      "cancel_order": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_order_actions",
        label="Cancel order",
      ),
      "compare_toggle": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Add/remove compare",
      ),
      "drawdown": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Drawdown",
      ),
      "lane": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Lane",
      ),
      "lifecycle": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Lifecycle",
      ),
      "mode": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Mode",
      ),
      "replace_order": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_order_actions",
        label="Replace order",
      ),
      "rerun": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Rerun",
      ),
      "return": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Return",
      ),
      "stop": ComparisonEligibilitySurfaceContract(
        eligibility="operational",
        group="operational_workflow",
        label="Stop",
      ),
      "trades": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Trades",
      ),
      "version": ComparisonEligibilitySurfaceContract(
        eligibility="supporting",
        group="supporting_identity",
        label="Version",
      ),
      "win_rate": ComparisonEligibilitySurfaceContract(
        eligibility="eligible",
        group="eligible_metrics",
        label="Win rate",
      ),
    },
    groups={
      "eligible_metrics": ComparisonEligibilityGroupContract(
        copy=(
          "These surfaces participate in comparison scoring or drill-back, so they remain "
          "comparison-eligible."
        ),
        eligibility="eligible",
        surface_ids=("return", "drawdown", "win_rate", "trades"),
        title="Comparison-eligible",
      ),
      "operational_order_actions": ComparisonEligibilityGroupContract(
        copy=(
          "Replace and cancel actions mutate order state, so they stay outside comparison "
          "drill-back even when the preview rows are comparison-eligible."
        ),
        eligibility="operational",
        surface_ids=("cancel_order", "replace_order"),
        title="Operational only",
      ),
      "operational_workflow": ComparisonEligibilityGroupContract(
        copy=(
          "Workflow controls change selection or execution state, so they remain outside "
          "comparison-eligible deep-link scope."
        ),
        eligibility="operational",
        surface_ids=("compare_toggle", "rerun", "stop"),
        title="Operational only",
      ),
      "supporting_identity": ComparisonEligibilityGroupContract(
        copy=(
          "Weak-signal identity and routing context stay descriptive only and do not create "
          "comparison deep-links."
        ),
        eligibility="supporting",
        surface_ids=("mode", "lane", "lifecycle", "version"),
        title="Supporting only",
      ),
    },
  )


@dataclass(frozen=True)
class RunSurfaceCapabilities:
  @dataclass(frozen=True)
  class Policy:
    applies_to: tuple[str, ...] = ()
    policy_key: str = ""
    policy_mode: str = ""
    source_of_truth: str = ""

  @dataclass(frozen=True)
  class Enforcement:
    enforcement_points: tuple[str, ...] = ()
    fallback_behavior: str = ""
    level: str = ""
    source_of_truth: str = ""

  @dataclass(frozen=True)
  class SurfaceRule:
    rule_key: str = ""
    surface_key: str = ""
    surface_label: str = ""
    enforcement_point: str = ""
    enforcement_mode: str = ""
    level: str = ""
    fallback_behavior: str = ""
    source_of_truth: str = ""

  comparison_eligibility_contract: ComparisonEligibilityContract = field(
    default_factory=default_comparison_eligibility_contract
  )
  shared_contracts: tuple["RunSurfaceSharedContract", ...] = field(
    default_factory=lambda: default_run_surface_shared_contracts()
  )


@dataclass(frozen=True)
class RunSurfaceSharedContract:
  contract_key: str
  contract_kind: str
  title: str
  summary: str
  source_of_truth: str
  version: str | None = None
  discovery_flow: str | None = None
  related_family_keys: tuple[str, ...] = ()
  member_keys: tuple[str, ...] = ()
  ui_surfaces: tuple[str, ...] = ()
  schema_sources: tuple[str, ...] = ()
  policy: RunSurfaceCapabilities.Policy | None = None
  enforcement: RunSurfaceCapabilities.Enforcement | None = None
  surface_rules: tuple[RunSurfaceCapabilities.SurfaceRule, ...] = ()
  schema_detail: dict[str, Any] = field(default_factory=dict)



def default_run_surface_shared_contracts() -> tuple[RunSurfaceSharedContract, ...]:
  return (
    RunSurfaceSharedContract(
      contract_key="schema:run-surface-capabilities",
      contract_kind="schema_metadata",
      title=RUN_SURFACE_CAPABILITY_SCHEMA_TITLE,
      summary=RUN_SURFACE_CAPABILITY_SCHEMA_SUMMARY,
      source_of_truth="run_surface_shared_contracts",
      version=RUN_SURFACE_CAPABILITY_SCHEMA_VERSION,
      related_family_keys=RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
      member_keys=tuple(
        [f"family:{family_key}" for family_key in RUN_SURFACE_CAPABILITY_FAMILY_ORDER]
        + [f"group:{group_key}" for group_key in RUN_SURFACE_CAPABILITY_GROUP_ORDER]
      ),
      schema_detail={
        "comparison_eligibility_group_order": RUN_SURFACE_CAPABILITY_GROUP_ORDER,
        "family_order": RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
        "run_subresource_contract_keys": RUN_SURFACE_SUBRESOURCE_CONTRACT_KEYS,
        "collection_query_contract_keys": RUN_SURFACE_COLLECTION_QUERY_CONTRACT_KEYS,
      },
    ),
    RunSurfaceSharedContract(
      contract_key="family:comparison_eligibility",
      contract_kind="capability_family",
      title="Comparison boundary contract",
      summary="Defines which run-list surfaces are comparison-eligible, supporting-only, or operational-only.",
      source_of_truth="comparison_eligibility_contract",
      discovery_flow="Shared UI contract panel and run-list boundary notes.",
      related_family_keys=("comparison_eligibility",),
      member_keys=("run_list_metric_tiles", "boundary_note_panels", "order_workflow_gates"),
      ui_surfaces=(
        "Run-list metric tiles",
        "Boundary note panels",
        "Order workflow gates",
      ),
      schema_sources=(
        "Run-surface capability endpoint",
        "Comparison score drill-back wiring",
        "Run-list boundary notes",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("metrics", "supporting_identity", "workflow_controls", "order_actions"),
        policy_key="comparison_surface_allowlist",
        policy_mode="allowlist",
        source_of_truth="comparison_eligibility_contract",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("run_list_metric_gating", "drill_back_selection", "boundary_note_rendering"),
        fallback_behavior="non_eligible_surfaces_remain_descriptive_only",
        level="hard_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="run_list_metric_tile_gate",
          surface_key="run_list_metric_tiles",
          surface_label="Run-list metric tiles",
          enforcement_point="run_list_metric_gating",
          enforcement_mode="eligible_only_drillback",
          level="hard_gate",
          fallback_behavior="render_metric_as_descriptive_only_when_surface_is_not_eligible",
          source_of_truth="comparison_eligibility_contract.surfaces",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="boundary_note_group_annotation",
          surface_key="boundary_note_panels",
          surface_label="Boundary note panels",
          enforcement_point="boundary_note_rendering",
          enforcement_mode="group_boundary_annotation",
          level="hard_gate",
          fallback_behavior="render_shared_boundary_copy_without_surface_specific_drill_links",
          source_of_truth="comparison_eligibility_contract.groups",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="order_workflow_score_link_exclusion",
          surface_key="order_workflow_gates",
          surface_label="Order workflow gates",
          enforcement_point="drill_back_selection",
          enforcement_mode="score_link_exclusion",
          level="hard_gate",
          fallback_behavior="keep_operational_workflow_controls_non_selectable",
          source_of_truth="comparison_eligibility_contract.groups",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:strategy_schema",
      contract_kind="capability_family",
      title="Strategy schema discovery",
      summary="Publishes typed strategy parameter schema and semantic metadata used by preset and revision workflows.",
      source_of_truth="strategy_catalog",
      discovery_flow="Strategy catalog and preset editor schema hints.",
      related_family_keys=("strategy_schema",),
      member_keys=(
        "strategy_catalog_cards",
        "preset_parameter_editor",
        "preset_revision_semantic_diffs",
      ),
      ui_surfaces=(
        "Strategy catalog cards",
        "Preset parameter editor",
        "Preset revision semantic diffs",
      ),
      schema_sources=(
        "Strategy parameter_schema",
        "Strategy catalog_semantics",
        "Supported timeframe metadata",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("strategy_catalog", "preset_editor", "preset_revision_diff"),
        policy_key="typed_strategy_schema_advertisement",
        policy_mode="schema_contract",
        source_of_truth="strategy_catalog",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("schema_hint_rendering", "preset_diff_semantics", "parameter_editor_defaults"),
        fallback_behavior="fallback_to_freeform_parameter_entry_when_schema_missing",
        level="advisory",
        source_of_truth="strategy_metadata.parameter_schema",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="strategy_catalog_schema_hints",
          surface_key="strategy_catalog_cards",
          surface_label="Strategy catalog cards",
          enforcement_point="schema_hint_rendering",
          enforcement_mode="schema_hint_annotation",
          level="advisory",
          fallback_behavior="render_strategy_summary_without_typed_parameter_hints",
          source_of_truth="strategy_metadata.parameter_schema",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="preset_editor_default_hydration",
          surface_key="preset_parameter_editor",
          surface_label="Preset parameter editor",
          enforcement_point="parameter_editor_defaults",
          enforcement_mode="typed_default_hydration",
          level="advisory",
          fallback_behavior="fallback_to_freeform_json_parameter_entry",
          source_of_truth="strategy_metadata.parameter_schema",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="preset_revision_schema_diff",
          surface_key="preset_revision_semantic_diffs",
          surface_label="Preset revision semantic diffs",
          enforcement_point="preset_diff_semantics",
          enforcement_mode="schema_aware_delta_annotation",
          level="advisory",
          fallback_behavior="render_generic_revision_value_deltas",
          source_of_truth="strategy_catalog_semantics",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:collection_query",
      contract_kind="capability_family",
      title="Collection query discovery",
      summary="Publishes collection expression schemas, parameter domains, enum-source metadata, and parameterized predicate-template authoring metadata used by typed query builders.",
      source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
      discovery_flow="Typed query discovery panels and collection expression builders.",
      related_family_keys=("collection_query",),
      member_keys=(
        "collection_query_discovery_panels",
        "collection_expression_builders",
        "collection_parameter_domain_pickers",
      ),
      ui_surfaces=(
        "Collection query discovery panels",
        "Collection expression builders",
        "Collection parameter domain pickers",
      ),
      schema_sources=(
        "Collection path schemas",
        "Collection element filter schemas",
        "Collection parameter domain metadata",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("collection_schema", "parameter_domains", "query_builders"),
        policy_key="typed_collection_query_discovery",
        policy_mode="schema_contract",
        source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("collection_schema_discovery", "parameter_domain_rendering", "collection_shape_validation"),
        fallback_behavior="fallback_to_raw_filter_expression_authoring_when_collection_query_metadata_is_missing",
        level="advisory",
        source_of_truth="typed_query_collection_schemas",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_query_schema_panel",
          surface_key="collection_query_discovery_panels",
          surface_label="Collection query discovery panels",
          enforcement_point="collection_schema_discovery",
          enforcement_mode="collection_schema_advertisement",
          level="advisory",
          fallback_behavior="omit_collection_query_contract_detail_when_discovery_metadata_is_missing",
          source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_expression_builder_schema",
          surface_key="collection_expression_builders",
          surface_label="Collection expression builders",
          enforcement_point="collection_shape_validation",
          enforcement_mode="shape_validated_builder_contract",
          level="advisory",
          fallback_behavior="allow_raw_collection_paths_without_builder_guidance",
          source_of_truth="typed_query_collection_schema_validation",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="collection_parameter_domain_enum_source",
          surface_key="collection_parameter_domain_pickers",
          surface_label="Collection parameter domain pickers",
          enforcement_point="parameter_domain_rendering",
          enforcement_mode="domain_and_enum_source_annotation",
          level="advisory",
          fallback_behavior="render_parameter_domains_without_enum_source_hints",
          source_of_truth="collection_query_parameter_domains",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:provenance_semantics",
      contract_kind="capability_family",
      title="Run provenance semantics",
      summary="Carries semantic run context into snapshot, provenance, artifact, and comparison drill-back surfaces.",
      source_of_truth="run_provenance_snapshot",
      discovery_flow="Run cards, provenance panels, and comparison deep-link restoration.",
      related_family_keys=("provenance_semantics",),
      member_keys=(
        "run_strategy_snapshot",
        "strategy_provenance_panels",
        "benchmark_artifact_summaries",
      ),
      ui_surfaces=(
        "Run strategy snapshot",
        "Strategy provenance panels",
        "Benchmark artifact summaries",
      ),
      schema_sources=(
        "Run provenance strategy snapshot",
        "Benchmark artifact metadata",
        "Catalog semantics snapshots",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("run_snapshot", "artifact_summary", "comparison_deep_link"),
        policy_key="provenance_semantic_snapshot",
        policy_mode="snapshot_contract",
        source_of_truth="run_provenance_snapshot",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("snapshot_serialization", "provenance_panel_rendering", "deep_link_restore"),
        fallback_behavior="render_basic_provenance_without_semantic_focus_when_snapshot_missing",
        level="snapshot_required",
        source_of_truth="run_provenance.strategy",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="run_snapshot_semantic_embed",
          surface_key="run_strategy_snapshot",
          surface_label="Run strategy snapshot",
          enforcement_point="snapshot_serialization",
          enforcement_mode="semantic_snapshot_embed",
          level="snapshot_required",
          fallback_behavior="render_snapshot_without_catalog_semantics",
          source_of_truth="run_provenance.strategy",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="strategy_provenance_semantic_render",
          surface_key="strategy_provenance_panels",
          surface_label="Strategy provenance panels",
          enforcement_point="provenance_panel_rendering",
          enforcement_mode="semantic_source_highlighting",
          level="snapshot_required",
          fallback_behavior="render_provenance_without_semantic_source_emphasis",
          source_of_truth="run_provenance.strategy.catalog_semantics",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="artifact_deep_link_restore",
          surface_key="benchmark_artifact_summaries",
          surface_label="Benchmark artifact summaries",
          enforcement_point="deep_link_restore",
          enforcement_mode="artifact_subfocus_restore",
          level="snapshot_required",
          fallback_behavior="restore_artifact_panel_without_subfocus_state",
          source_of_truth="benchmark_artifact_metadata",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="family:execution_controls",
      contract_kind="capability_family",
      title="Execution control gating",
      summary="Documents which interactive controls mutate workflow or venue state and therefore stay outside comparison semantics.",
      source_of_truth="run_surface_capability_endpoint",
      discovery_flow="Shared UI control gating and operational-only boundary notes.",
      related_family_keys=("execution_controls",),
      member_keys=(
        "rerun_and_stop_controls",
        "compare_selection_workflow",
        "order_replace_cancel_actions",
      ),
      ui_surfaces=(
        "Rerun and stop controls",
        "Compare selection workflow",
        "Order replace/cancel actions",
      ),
      schema_sources=(
        "Run-surface capability endpoint",
        "Order lifecycle summaries",
        "Runtime state transitions",
      ),
      policy=RunSurfaceCapabilities.Policy(
        applies_to=("rerun_controls", "stop_controls", "order_replace_cancel"),
        policy_key="operational_control_exclusion",
        policy_mode="mutation_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      enforcement=RunSurfaceCapabilities.Enforcement(
        enforcement_points=("button_visibility", "order_action_boundary_notes", "comparison_selection_exclusion"),
        fallback_behavior="controls_remain_operational_only_and_do_not_bind_score_links",
        level="hard_gate",
        source_of_truth="run_surface_capability_endpoint",
      ),
      surface_rules=(
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="rerun_stop_button_gate",
          surface_key="rerun_and_stop_controls",
          surface_label="Rerun and stop controls",
          enforcement_point="button_visibility",
          enforcement_mode="mutation_control_gate",
          level="hard_gate",
          fallback_behavior="render_controls_as_operational_only_without_score_links",
          source_of_truth="run_surface_capability_endpoint",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="compare_selection_operational_exclusion",
          surface_key="compare_selection_workflow",
          surface_label="Compare selection workflow",
          enforcement_point="comparison_selection_exclusion",
          enforcement_mode="selection_exclusion_gate",
          level="hard_gate",
          fallback_behavior="exclude_mutating_controls_from_comparison_selection",
          source_of_truth="run_surface_capability_endpoint",
        ),
        RunSurfaceCapabilities.SurfaceRule(
          rule_key="order_replace_cancel_boundary_note",
          surface_key="order_replace_cancel_actions",
          surface_label="Order replace/cancel actions",
          enforcement_point="order_action_boundary_notes",
          enforcement_mode="operational_boundary_annotation",
          level="hard_gate",
          fallback_behavior="render_order_actions_as_operational_only",
          source_of_truth="order_lifecycle_summary",
        ),
      ),
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:orders",
      contract_kind="run_subresource",
      title="Run order list",
      summary="Declarative route binding and serializer contract for the standalone `orders` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:orders", "route:get_run_orders"),
      schema_detail={
        "body_key": "orders",
        "route_path": "/runs/{run_id}/orders",
        "route_name": "get_run_orders",
      },
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:positions",
      contract_kind="run_subresource",
      title="Run positions",
      summary="Declarative route binding and serializer contract for the standalone `positions` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:positions", "route:get_run_positions"),
      schema_detail={
        "body_key": "positions",
        "route_path": "/runs/{run_id}/positions",
        "route_name": "get_run_positions",
      },
    ),
    RunSurfaceSharedContract(
      contract_key="subresource:metrics",
      contract_kind="run_subresource",
      title="Run metrics",
      summary="Declarative route binding and serializer contract for the standalone `metrics` run subresource.",
      source_of_truth="run_subresource_contracts",
      related_family_keys=(),
      member_keys=("body:metrics", "route:get_run_metrics"),
      schema_detail={
        "body_key": "metrics",
        "route_path": "/runs/{run_id}/metrics",
        "route_name": "get_run_metrics",
      },
    ),
  )
