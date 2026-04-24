import { fetchJson } from "./base";
import type {
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditListPayload,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryListPayload,
  ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload,
  ProviderProvenanceSchedulerStitchedReportViewEntry,
  ProviderProvenanceSchedulerStitchedReportViewAuditListPayload,
  ProviderProvenanceSchedulerStitchedReportViewListPayload,
  ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
  ProviderProvenanceSchedulerNarrativeGovernancePlan,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateListPayload,
  ProviderProvenanceSchedulerNarrativeGovernancePlanListPayload,
} from "../controlRoomDefinitions";

export async function createProviderProvenanceSchedulerStitchedReportView(params: {
  name: string;
  description?: string;
  query?: Record<string, unknown>;
  occurrenceLimit?: number;
  historyLimit?: number;
  drilldownHistoryLimit?: number;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewEntry>(
    "/operator/provider-provenance-analytics/scheduler-stitched-report-views",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        ...(params.query ? { query: params.query } : {}),
        ...(typeof params.occurrenceLimit === "number" && Number.isFinite(params.occurrenceLimit)
          ? { occurrence_limit: Math.max(1, Math.min(Math.round(params.occurrenceLimit), 50)) }
          : {}),
        ...(typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)
          ? { history_limit: Math.max(1, Math.min(Math.round(params.historyLimit), 200)) }
          : {}),
        ...(typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)
          ? { drilldown_history_limit: Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100)) }
          : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerStitchedReportViews(params: {
  createdByTabId?: string;
  category?: string;
  narrativeFacet?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.createdByTabId?.trim()) {
    searchParams.set("created_by_tab_id", params.createdByTabId.trim());
  }
  if (params.category?.trim()) {
    searchParams.set("category", params.category.trim());
  }
  if (params.narrativeFacet?.trim()) {
    searchParams.set("narrative_facet", params.narrativeFacet.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerStitchedReportView(params: {
  viewId: string;
  name?: string;
  description?: string;
  query?: Record<string, unknown>;
  occurrenceLimit?: number;
  historyLimit?: number;
  drilldownHistoryLimit?: number;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views/${encodeURIComponent(params.viewId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(typeof params.name === "string" ? { name: params.name } : {}),
        ...(typeof params.description === "string" ? { description: params.description } : {}),
        ...(params.query ? { query: params.query } : {}),
        ...(typeof params.occurrenceLimit === "number" && Number.isFinite(params.occurrenceLimit)
          ? { occurrence_limit: Math.max(1, Math.min(Math.round(params.occurrenceLimit), 50)) }
          : {}),
        ...(typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)
          ? { history_limit: Math.max(1, Math.min(Math.round(params.historyLimit), 200)) }
          : {}),
        ...(typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)
          ? { drilldown_history_limit: Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100)) }
          : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerStitchedReportView(params: {
  viewId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views/${encodeURIComponent(params.viewId)}/delete`,
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

export async function bulkGovernProviderProvenanceSchedulerStitchedReportViews(params: {
  action: "delete" | "restore" | "update";
  viewIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  occurrenceLimit?: number;
  historyLimit?: number;
  drilldownHistoryLimit?: number;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-stitched-report-views/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        view_ids: params.viewIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend?.trim() ? { description_append: params.descriptionAppend.trim() } : {}),
        ...(params.queryPatch ? { query_patch: params.queryPatch } : {}),
        ...(typeof params.occurrenceLimit === "number" && Number.isFinite(params.occurrenceLimit)
          ? { occurrence_limit: Math.max(1, Math.min(Math.round(params.occurrenceLimit), 50)) }
          : {}),
        ...(typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)
          ? { history_limit: Math.max(1, Math.min(Math.round(params.historyLimit), 200)) }
          : {}),
        ...(typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)
          ? { drilldown_history_limit: Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100)) }
          : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerStitchedReportViewRevisions(
  viewId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views/${encodeURIComponent(viewId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerStitchedReportViewRevision(params: {
  viewId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views/${encodeURIComponent(params.viewId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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

export async function listProviderProvenanceSchedulerStitchedReportViewAudits(params: {
  viewId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.viewId?.trim()) {
    searchParams.set("view_id", params.viewId.trim());
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
  return fetchJson<ProviderProvenanceSchedulerStitchedReportViewAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-views/audits${suffix}`,
  );
}

export async function createProviderProvenanceSchedulerStitchedReportGovernanceRegistry(params: {
  name: string;
  description?: string;
  queueView?: Record<string, unknown>;
  defaultPolicyTemplateId?: string;
  defaultPolicyCatalogId?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry>(
    "/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        ...(params.queueView ? { queue_view: params.queueView } : {}),
        ...(typeof params.defaultPolicyTemplateId === "string"
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(typeof params.defaultPolicyCatalogId === "string"
          ? { default_policy_catalog_id: params.defaultPolicyCatalogId }
          : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerStitchedReportGovernanceRegistries(params: {
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 200))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerStitchedReportGovernanceRegistry(params: {
  registryId: string;
  name?: string;
  description?: string;
  queueView?: Record<string, unknown>;
  defaultPolicyTemplateId?: string;
  defaultPolicyCatalogId?: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/${encodeURIComponent(params.registryId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(typeof params.name === "string" ? { name: params.name } : {}),
        ...(typeof params.description === "string" ? { description: params.description } : {}),
        ...(params.queueView ? { queue_view: params.queueView } : {}),
        ...(typeof params.defaultPolicyTemplateId === "string"
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(typeof params.defaultPolicyCatalogId === "string"
          ? { default_policy_catalog_id: params.defaultPolicyCatalogId }
          : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerStitchedReportGovernanceRegistry(params: {
  registryId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/${encodeURIComponent(params.registryId)}/delete`,
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

export async function listProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisions(
  registryId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/${encodeURIComponent(registryId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevision(params: {
  registryId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/${encodeURIComponent(params.registryId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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

export async function bulkGovernProviderProvenanceSchedulerStitchedReportGovernanceRegistries(params: {
  action: "delete" | "restore" | "update";
  registryIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queueViewPatch?: Record<string, unknown>;
  defaultPolicyTemplateId?: string;
  defaultPolicyCatalogId?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        registry_ids: params.registryIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.queueViewPatch ? { queue_view_patch: params.queueViewPatch } : {}),
        ...(params.defaultPolicyTemplateId !== undefined
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(params.defaultPolicyCatalogId !== undefined
          ? { default_policy_catalog_id: params.defaultPolicyCatalogId }
          : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerStitchedReportGovernanceRegistryAudits(params: {
  registryId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.registryId?.trim()) {
    searchParams.set("registry_id", params.registryId.trim());
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
  return fetchJson<ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/audits${suffix}`,
  );
}

export async function listProviderProvenanceSchedulerStitchedReportGovernancePolicyTemplates(params: {
  actionScope?: string;
  approvalLane?: string;
  approvalPriority?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
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
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/policy-templates${suffix}`,
  );
}

export async function listProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogs(params: {
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
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/policy-catalogs${suffix}`,
  );
}

export async function createProviderProvenanceSchedulerStitchedReportGovernancePlan(params: {
  itemIds: string[];
  action: "delete" | "restore" | "update";
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queueViewPatch?: Record<string, unknown>;
  defaultPolicyTemplateId?: string;
  defaultPolicyCatalogId?: string;
  policyTemplateId?: string;
  policyCatalogId?: string;
  approvalLane?: string;
  approvalPriority?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    "/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans",
    {
      method: "POST",
      body: JSON.stringify({
        item_ids: params.itemIds,
        action: params.action,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend?.trim() ? { description_append: params.descriptionAppend.trim() } : {}),
        ...(params.queueViewPatch ? { queue_view_patch: params.queueViewPatch } : {}),
        ...(params.defaultPolicyTemplateId !== undefined
          ? { default_policy_template_id: params.defaultPolicyTemplateId }
          : {}),
        ...(params.defaultPolicyCatalogId !== undefined
          ? { default_policy_catalog_id: params.defaultPolicyCatalogId }
          : {}),
        ...(params.policyTemplateId?.trim() ? { policy_template_id: params.policyTemplateId.trim() } : {}),
        ...(params.policyCatalogId?.trim() ? { policy_catalog_id: params.policyCatalogId.trim() } : {}),
        ...(params.approvalLane?.trim() ? { approval_lane: params.approvalLane.trim() } : {}),
        ...(params.approvalPriority?.trim() ? { approval_priority: params.approvalPriority.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerStitchedReportGovernancePlans(params: {
  status?: string;
  queueState?: string;
  approvalLane?: string;
  approvalPriority?: string;
  policyTemplateId?: string;
  policyCatalogId?: string;
  search?: string;
  sort?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.queueState?.trim()) {
    searchParams.set("queue_state", params.queueState.trim());
  }
  if (params.approvalLane?.trim()) {
    searchParams.set("approval_lane", params.approvalLane.trim());
  }
  if (params.approvalPriority?.trim()) {
    searchParams.set("approval_priority", params.approvalPriority.trim());
  }
  if (params.policyTemplateId !== undefined) {
    searchParams.set("policy_template_id", params.policyTemplateId);
  }
  if (params.policyCatalogId !== undefined) {
    searchParams.set("policy_catalog_id", params.policyCatalogId);
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (params.sort?.trim()) {
    searchParams.set("sort", params.sort.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 100))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlanListPayload>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans${suffix}`,
  );
}

export async function approveProviderProvenanceSchedulerStitchedReportGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  note?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/${encodeURIComponent(params.planId)}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.note?.trim() ? { note: params.note.trim() } : {}),
      }),
    },
  );
}

export async function applyProviderProvenanceSchedulerStitchedReportGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/${encodeURIComponent(params.planId)}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function rollbackProviderProvenanceSchedulerStitchedReportGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  note?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/${encodeURIComponent(params.planId)}/rollback`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.note?.trim() ? { note: params.note.trim() } : {}),
      }),
    },
  );
}
