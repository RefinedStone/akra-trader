import { fetchJson } from "./base";
import type {
  ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
  ProviderProvenanceSchedulerNarrativeGovernancePlan,
  ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditListPayload,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateListPayload,
  ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePlanListPayload,
} from "../controlRoomDefinitions";

export async function createProviderProvenanceSchedulerNarrativeGovernancePlan(params: {
  itemType: "template" | "registry" | "stitched_report_view" | "stitched_report_governance_registry";
  itemIds: string[];
  action: "delete" | "restore" | "update";
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  layoutPatch?: Record<string, unknown>;
  queueViewPatch?: Record<string, unknown>;
  defaultPolicyTemplateId?: string;
  defaultPolicyCatalogId?: string;
  occurrenceLimit?: number;
  historyLimit?: number;
  drilldownHistoryLimit?: number;
  templateId?: string;
  clearTemplateLink?: boolean;
  policyTemplateId?: string;
  policyCatalogId?: string;
  approvalLane?: string;
  approvalPriority?: string;
  hierarchyKey?: string;
  hierarchyName?: string;
  hierarchyPosition?: number;
  hierarchyTotal?: number;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/plans",
    {
      method: "POST",
      body: JSON.stringify({
        item_type: params.itemType,
        item_ids: params.itemIds,
        action: params.action,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend?.trim() ? { description_append: params.descriptionAppend.trim() } : {}),
        ...(params.queryPatch ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch ? { layout_patch: params.layoutPatch } : {}),
        ...(params.queueViewPatch ? { queue_view_patch: params.queueViewPatch } : {}),
        ...(params.defaultPolicyTemplateId !== undefined
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(params.defaultPolicyCatalogId !== undefined
          ? { default_policy_catalog_id: params.defaultPolicyCatalogId }
          : {}),
        ...(typeof params.occurrenceLimit === "number"
          ? { occurrence_limit: Math.max(1, Math.min(Math.round(params.occurrenceLimit), 50)) }
          : {}),
        ...(typeof params.historyLimit === "number"
          ? { history_limit: Math.max(1, Math.min(Math.round(params.historyLimit), 200)) }
          : {}),
        ...(typeof params.drilldownHistoryLimit === "number"
          ? { drilldown_history_limit: Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100)) }
          : {}),
        ...(params.templateId?.trim() ? { template_id: params.templateId.trim() } : {}),
        ...(params.clearTemplateLink ? { clear_template_link: true } : {}),
        ...(params.policyTemplateId?.trim() ? { policy_template_id: params.policyTemplateId.trim() } : {}),
        ...(params.policyCatalogId?.trim() ? { policy_catalog_id: params.policyCatalogId.trim() } : {}),
        ...(params.approvalLane?.trim() ? { approval_lane: params.approvalLane.trim() } : {}),
        ...(params.approvalPriority?.trim() ? { approval_priority: params.approvalPriority.trim() } : {}),
        ...(params.hierarchyKey?.trim() ? { hierarchy_key: params.hierarchyKey.trim() } : {}),
        ...(params.hierarchyName?.trim() ? { hierarchy_name: params.hierarchyName.trim() } : {}),
        ...(typeof params.hierarchyPosition === "number" ? { hierarchy_position: params.hierarchyPosition } : {}),
        ...(typeof params.hierarchyTotal === "number" ? { hierarchy_total: params.hierarchyTotal } : {}),
      }),
    },
  );
}

export async function createProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(params: {
  name: string;
  description?: string;
  itemTypeScope?: string;
  actionScope?: string;
  approvalLane?: string;
  approvalPriority?: string;
  guidance?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.itemTypeScope?.trim() ? { item_type_scope: params.itemTypeScope.trim() } : {}),
        ...(params.actionScope?.trim() ? { action_scope: params.actionScope.trim() } : {}),
        ...(params.approvalLane?.trim() ? { approval_lane: params.approvalLane.trim() } : {}),
        ...(params.approvalPriority?.trim() ? { approval_priority: params.approvalPriority.trim() } : {}),
        ...(params.guidance?.trim() ? { guidance: params.guidance.trim() } : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplates(params: {
  itemTypeScope?: string;
  actionScope?: string;
  approvalLane?: string;
  approvalPriority?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.itemTypeScope?.trim()) {
    searchParams.set("item_type_scope", params.itemTypeScope.trim());
  }
  if (params.actionScope?.trim()) {
    searchParams.set("action_scope", params.actionScope.trim());
  }
  if (params.approvalLane?.trim()) {
    searchParams.set("approval_lane", params.approvalLane.trim());
  }
  if (params.approvalPriority?.trim()) {
    searchParams.set("approval_priority", params.approvalPriority.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 200))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(params: {
  policyTemplateId: string;
  name?: string;
  description?: string;
  itemTypeScope?: string;
  actionScope?: string;
  approvalLane?: string;
  approvalPriority?: string;
  guidance?: string | null;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/${encodeURIComponent(params.policyTemplateId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.itemTypeScope !== undefined ? { item_type_scope: params.itemTypeScope } : {}),
        ...(params.actionScope !== undefined ? { action_scope: params.actionScope } : {}),
        ...(params.approvalLane !== undefined ? { approval_lane: params.approvalLane } : {}),
        ...(params.approvalPriority !== undefined ? { approval_priority: params.approvalPriority } : {}),
        ...(params.guidance !== undefined ? { guidance: params.guidance } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate(params: {
  policyTemplateId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/${encodeURIComponent(params.policyTemplateId)}/delete`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisions(
  policyTemplateId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/${encodeURIComponent(policyTemplateId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevision(params: {
  policyTemplateId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/${encodeURIComponent(params.policyTemplateId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAudits(params: {
  policyTemplateId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.policyTemplateId?.trim()) {
    searchParams.set("policy_template_id", params.policyTemplateId.trim());
  }
  if (params.action?.trim()) {
    searchParams.set("action", params.action.trim());
  }
  if (params.actorTabId?.trim()) {
    searchParams.set("actor_tab_id", params.actorTabId.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 200))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/audits${suffix}`,
  );
}

export async function createProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(params: {
  name: string;
  description?: string;
  policyTemplateIds: string[];
  defaultPolicyTemplateId?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        ...(params.description !== undefined ? { description: params.description } : {}),
        policy_template_ids: params.policyTemplateIds,
        ...(params.defaultPolicyTemplateId?.trim()
          ? { default_policy_template_id: params.defaultPolicyTemplateId.trim() }
          : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogs(params: {
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 100))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(params: {
  catalogId: string;
  name?: string;
  description?: string;
  policyTemplateIds?: string[];
  defaultPolicyTemplateId?: string | null;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.policyTemplateIds !== undefined ? { policy_template_ids: params.policyTemplateIds } : {}),
        ...(params.defaultPolicyTemplateId !== undefined
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(params: {
  catalogId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/delete`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkGovernance(params: {
  action: "delete" | "restore" | "update";
  catalogIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  defaultPolicyTemplateId?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        catalog_ids: params.catalogIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.defaultPolicyTemplateId?.trim()
          ? { default_policy_template_id: params.defaultPolicyTemplateId.trim() }
          : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisions(
  catalogId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(catalogId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevision(params: {
  catalogId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAudits(params: {
  catalogId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.catalogId?.trim()) {
    searchParams.set("catalog_id", params.catalogId.trim());
  }
  if (params.action?.trim()) {
    searchParams.set("action", params.action.trim());
  }
  if (params.actorTabId?.trim()) {
    searchParams.set("actor_tab_id", params.actorTabId.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 200))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/audits${suffix}`,
  );
}

export async function captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(params: {
  catalogId: string;
  hierarchySteps: Array<{
    stepId?: string;
    itemType: "template" | "registry";
    itemIds: string[];
    namePrefix?: string;
    nameSuffix?: string;
    descriptionAppend?: string;
    queryPatch?: Record<string, unknown>;
    layoutPatch?: Record<string, unknown>;
    templateId?: string;
    clearTemplateLink?: boolean;
  }>;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/hierarchy`,
    {
      method: "POST",
      body: JSON.stringify({
        hierarchy_steps: params.hierarchySteps.map((step) => ({
          ...(step.stepId?.trim() ? { step_id: step.stepId.trim() } : {}),
          item_type: step.itemType,
          item_ids: step.itemIds,
          action: "update",
          ...(step.namePrefix !== undefined ? { name_prefix: step.namePrefix } : {}),
          ...(step.nameSuffix !== undefined ? { name_suffix: step.nameSuffix } : {}),
          ...(step.descriptionAppend !== undefined ? { description_append: step.descriptionAppend } : {}),
          ...(step.queryPatch ? { query_patch: step.queryPatch } : {}),
          ...(step.layoutPatch ? { layout_patch: step.layoutPatch } : {}),
          ...(step.templateId?.trim() ? { template_id: step.templateId.trim() } : {}),
          ...(step.clearTemplateLink ? { clear_template_link: true } : {}),
        })),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function updateProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep(params: {
  catalogId: string;
  stepId: string;
  itemIds?: string[];
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  layoutPatch?: Record<string, unknown>;
  templateId?: string;
  clearTemplateLink?: boolean;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/hierarchy-steps/${encodeURIComponent(params.stepId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.itemIds !== undefined ? { item_ids: params.itemIds } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.queryPatch !== undefined ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch !== undefined ? { layout_patch: params.layoutPatch } : {}),
        ...(params.templateId !== undefined ? { template_id: params.templateId } : {}),
        ...(params.clearTemplateLink !== undefined ? { clear_template_link: params.clearTemplateLink } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepRevision(params: {
  catalogId: string;
  stepId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/hierarchy-steps/${encodeURIComponent(params.stepId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkGovernance(params: {
  catalogId: string;
  action: "delete" | "update";
  stepIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  layoutPatch?: Record<string, unknown>;
  templateId?: string;
  clearTemplateLink?: boolean;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/hierarchy-steps/bulk-governance`,
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        step_ids: params.stepIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.queryPatch !== undefined ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch !== undefined ? { layout_patch: params.layoutPatch } : {}),
        ...(params.templateId !== undefined ? { template_id: params.templateId } : {}),
        ...(params.clearTemplateLink !== undefined ? { clear_template_link: params.clearTemplateLink } : {}),
      }),
    },
  );
}

export * from "./providerProvenanceSchedulerNarrativeGovernanceHierarchy";
