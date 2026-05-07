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
import {
  DEFAULT_RUN_SURFACE_CAPABILITY_DISCOVERY,
  DEFAULT_RUN_SURFACE_CAPABILITY_FAMILIES,
  DEFAULT_RUN_SURFACE_CAPABILITY_FAMILY_ORDER,
  DEFAULT_RUN_SURFACE_CAPABILITY_GROUP_ORDER,
  DEFAULT_RUN_SURFACE_SUBRESOURCE_CONTRACTS,
  RUN_LIST_BOUNDARY_CONTRACT,
} from "./runSurfaceCapabilityDefaults";

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

export function shouldEnableStrategyProvenanceSemantics(
  capabilities: RunSurfaceCapabilities | null | undefined,
) {
  return hasRunSurfaceCapabilitySurfaceRule(
    capabilities,
    "provenance_semantics",
    "strategy_provenance_panels",
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
