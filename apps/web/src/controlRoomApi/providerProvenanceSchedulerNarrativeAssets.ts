import { fetchJson } from "./base";
import type {
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
  ProviderProvenanceSchedulerNarrativeRegistryEntry,
  ProviderProvenanceSchedulerNarrativeRegistryListPayload,
  ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeTemplateEntry,
  ProviderProvenanceSchedulerNarrativeTemplateListPayload,
  ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload,
} from "../controlRoomDefinitions";

export async function createProviderProvenanceSchedulerNarrativeTemplate(params: {
  name: string;
  description?: string;
  query: Record<string, unknown>;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateEntry>(
    "/operator/provider-provenance-analytics/scheduler-narrative-templates",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        query: params.query,
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeTemplates(params: {
  createdByTabId?: string;
  focusScope?: "current_focus" | "all_focuses";
  category?: string;
  narrativeFacet?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.createdByTabId?.trim()) {
    searchParams.set("created_by_tab_id", params.createdByTabId.trim());
  }
  if (params.focusScope?.trim()) {
    searchParams.set("focus_scope", params.focusScope.trim());
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
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-templates${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerNarrativeTemplate(params: {
  templateId: string;
  name?: string;
  description?: string;
  query?: Record<string, unknown>;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-templates/${encodeURIComponent(params.templateId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.query !== undefined ? { query: params.query } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerNarrativeTemplate(params: {
  templateId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-templates/${encodeURIComponent(params.templateId)}/delete`,
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

export async function bulkGovernProviderProvenanceSchedulerNarrativeTemplates(params: {
  action: "delete" | "restore" | "update";
  templateIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-narrative-templates/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        template_ids: params.templateIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix?.trim() ? { name_prefix: params.namePrefix.trim() } : {}),
        ...(params.nameSuffix?.trim() ? { name_suffix: params.nameSuffix.trim() } : {}),
        ...(params.descriptionAppend?.trim() ? { description_append: params.descriptionAppend.trim() } : {}),
        ...(params.queryPatch ? { query_patch: params.queryPatch } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeTemplateRevisions(templateId: string) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-templates/${encodeURIComponent(templateId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeTemplateRevision(params: {
  templateId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeTemplateEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-templates/${encodeURIComponent(params.templateId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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

export async function createProviderProvenanceSchedulerNarrativeRegistryEntry(params: {
  name: string;
  description?: string;
  query: Record<string, unknown>;
  layout?: ProviderProvenanceDashboardLayout;
  templateId?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryEntry>(
    "/operator/provider-provenance-analytics/scheduler-narrative-registry",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        query: params.query,
        ...(params.layout ? { layout: params.layout } : {}),
        ...(params.templateId?.trim() ? { template_id: params.templateId.trim() } : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeRegistryEntries(params: {
  templateId?: string;
  createdByTabId?: string;
  focusScope?: "current_focus" | "all_focuses";
  category?: string;
  narrativeFacet?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.templateId?.trim()) {
    searchParams.set("template_id", params.templateId.trim());
  }
  if (params.createdByTabId?.trim()) {
    searchParams.set("created_by_tab_id", params.createdByTabId.trim());
  }
  if (params.focusScope?.trim()) {
    searchParams.set("focus_scope", params.focusScope.trim());
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
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-registry${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerNarrativeRegistryEntry(params: {
  registryId: string;
  name?: string;
  description?: string;
  query?: Record<string, unknown>;
  layout?: ProviderProvenanceDashboardLayout;
  templateId?: string | null;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-registry/${encodeURIComponent(params.registryId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.query !== undefined ? { query: params.query } : {}),
        ...(params.layout !== undefined ? { layout: params.layout } : {}),
        ...(params.templateId !== undefined ? { template_id: params.templateId } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerNarrativeRegistryEntry(params: {
  registryId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-registry/${encodeURIComponent(params.registryId)}/delete`,
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

export async function bulkGovernProviderProvenanceSchedulerNarrativeRegistryEntries(params: {
  action: "delete" | "restore" | "update";
  registryIds: string[];
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
    "/operator/provider-provenance-analytics/scheduler-narrative-registry/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        registry_ids: params.registryIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix?.trim() ? { name_prefix: params.namePrefix.trim() } : {}),
        ...(params.nameSuffix?.trim() ? { name_suffix: params.nameSuffix.trim() } : {}),
        ...(params.descriptionAppend?.trim() ? { description_append: params.descriptionAppend.trim() } : {}),
        ...(params.queryPatch ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch ? { layout_patch: params.layoutPatch } : {}),
        ...(params.templateId?.trim() ? { template_id: params.templateId.trim() } : {}),
        ...(params.clearTemplateLink ? { clear_template_link: true } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeRegistryRevisions(registryId: string) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-registry/${encodeURIComponent(registryId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeRegistryRevision(params: {
  registryId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeRegistryEntry>(
    `/operator/provider-provenance-analytics/scheduler-narrative-registry/${encodeURIComponent(params.registryId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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
