import { fetchJson } from "./base";
import type {
  ProviderProvenanceSchedulerSearchDashboardPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload,
  ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload,
  ProviderProvenanceSchedulerSearchModerationPlanEntry,
  ProviderProvenanceSchedulerSearchModerationPlanListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload,
  ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload,
  ProviderProvenanceSchedulerSearchFeedbackResult,
  ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult,
  ProviderProvenanceSchedulerSearchFeedbackModerationResult,
  ProviderProvenanceSchedulerNarrativeBulkGovernanceResult,
} from "../controlRoomDefinitions";

export async function recordProviderProvenanceSchedulerSearchFeedback(params: {
  queryId: string;
  query: string;
  occurrenceId: string;
  signal: "relevant" | "not_relevant";
  matchedFields?: string[];
  semanticConcepts?: string[];
  operatorHits?: string[];
  lexicalScore?: number;
  semanticScore?: number;
  operatorScore?: number;
  score?: number;
  rankingReason?: string | null;
  note?: string | null;
  actor?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchFeedbackResult>(
    "/operator/provider-provenance-analytics/scheduler-alerts/search-feedback",
    {
      method: "POST",
      body: JSON.stringify({
        query_id: params.queryId,
        query: params.query,
        occurrence_id: params.occurrenceId,
        signal: params.signal,
        matched_fields: params.matchedFields ?? [],
        semantic_concepts: params.semanticConcepts ?? [],
        operator_hits: params.operatorHits ?? [],
        lexical_score:
          typeof params.lexicalScore === "number" && Number.isFinite(params.lexicalScore)
            ? Math.max(0, Math.round(params.lexicalScore))
            : 0,
        semantic_score:
          typeof params.semanticScore === "number" && Number.isFinite(params.semanticScore)
            ? Math.max(0, Math.round(params.semanticScore))
            : 0,
        operator_score:
          typeof params.operatorScore === "number" && Number.isFinite(params.operatorScore)
            ? Math.max(0, Math.round(params.operatorScore))
            : 0,
        score:
          typeof params.score === "number" && Number.isFinite(params.score)
            ? Math.max(0, Math.round(params.score))
            : 0,
        ranking_reason: params.rankingReason ?? null,
        note: params.note ?? null,
        actor: params.actor?.trim() || "operator",
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function getProviderProvenanceSchedulerSearchDashboard(params: {
  search?: string;
  moderationStatus?: string;
  signal?: "relevant" | "not_relevant";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  queryLimit?: number;
  feedbackLimit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (params.moderationStatus?.trim()) {
    searchParams.set("moderation_status", params.moderationStatus.trim());
  }
  if (params.signal?.trim()) {
    searchParams.set("signal", params.signal.trim());
  }
  if (params.governanceView?.trim()) {
    searchParams.set("governance_view", params.governanceView.trim());
  }
  if (typeof params.windowDays === "number" && Number.isFinite(params.windowDays)) {
    searchParams.set("window_days", String(Math.max(7, Math.min(Math.round(params.windowDays), 180))));
  }
  if (typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)) {
    searchParams.set(
      "stale_pending_hours",
      String(Math.max(1, Math.min(Math.round(params.stalePendingHours), 24 * 30))),
    );
  }
  if (typeof params.queryLimit === "number" && Number.isFinite(params.queryLimit)) {
    searchParams.set("query_limit", String(Math.max(1, Math.min(Math.round(params.queryLimit), 50))));
  }
  if (typeof params.feedbackLimit === "number" && Number.isFinite(params.feedbackLimit)) {
    searchParams.set("feedback_limit", String(Math.max(1, Math.min(Math.round(params.feedbackLimit), 100))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchDashboardPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/dashboard${suffix}`,
  );
}

export async function moderateProviderProvenanceSchedulerSearchFeedback(params: {
  feedbackId: string;
  moderationStatus: "pending" | "approved" | "rejected";
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchFeedbackModerationResult>(
    `/operator/provider-provenance-analytics/scheduler-search/feedback/${encodeURIComponent(params.feedbackId)}/moderate`,
    {
      method: "POST",
      body: JSON.stringify({
        moderation_status: params.moderationStatus,
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function moderateProviderProvenanceSchedulerSearchFeedbackBatch(params: {
  feedbackIds: string[];
  moderationStatus: "pending" | "approved" | "rejected";
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchFeedbackBatchModerationResult>(
    "/operator/provider-provenance-analytics/scheduler-search/feedback/batch-moderate",
    {
      method: "POST",
      body: JSON.stringify({
        feedback_ids: params.feedbackIds,
        moderation_status: params.moderationStatus,
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function createProviderProvenanceSchedulerSearchModerationPolicyCatalog(params: {
  name: string;
  description?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        default_moderation_status: params.defaultModerationStatus ?? "approved",
        governance_view: params.governanceView ?? "pending_queue",
        window_days: params.windowDays ?? 30,
        stale_pending_hours: params.stalePendingHours ?? 24,
        minimum_score: params.minimumScore ?? 0,
        require_note: params.requireNote ?? false,
        created_by_tab_id: params.createdByTabId?.trim() || null,
        created_by_tab_label: params.createdByTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationPolicyCatalogs() {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogListPayload>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
  );
}

export async function updateProviderProvenanceSchedulerSearchModerationPolicyCatalog(params: {
  catalogId: string;
  name?: string;
  description?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/${encodeURIComponent(params.catalogId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(typeof params.name === "string" ? { name: params.name } : {}),
        ...(typeof params.description === "string" ? { description: params.description } : {}),
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: Math.max(7, Math.min(Math.round(params.windowDays), 180)) }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: Math.max(1, Math.min(Math.round(params.stalePendingHours), 24 * 30)) }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: Math.max(Math.round(params.minimumScore), 0) }
          : {}),
        ...(typeof params.requireNote === "boolean" ? { require_note: params.requireNote } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerSearchModerationPolicyCatalog(params: {
  catalogId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/${encodeURIComponent(params.catalogId)}/delete`,
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

export async function listProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisions(
  catalogId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/${encodeURIComponent(catalogId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogRevision(params: {
  catalogId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/${encodeURIComponent(params.catalogId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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

export async function listProviderProvenanceSchedulerSearchModerationPolicyCatalogAudits(params: {
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
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/audits${suffix}`,
  );
}

export async function bulkGovernProviderProvenanceSchedulerSearchModerationPolicyCatalogs(params: {
  action: "delete" | "restore" | "update";
  catalogIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/bulk-governance",
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
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: Math.max(7, Math.min(Math.round(params.windowDays), 180)) }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: Math.max(1, Math.min(Math.round(params.stalePendingHours), 24 * 30)) }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: Math.max(Math.round(params.minimumScore), 0) }
          : {}),
        ...(typeof params.requireNote === "boolean" ? { require_note: params.requireNote } : {}),
      }),
    },
  );
}

export async function stageProviderProvenanceSchedulerSearchModerationPlan(params: {
  feedbackIds: string[];
  policyCatalogId?: string;
  moderationStatus?: "pending" | "approved" | "rejected";
  actor?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPlanEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans",
    {
      method: "POST",
      body: JSON.stringify({
        feedback_ids: params.feedbackIds,
        policy_catalog_id: params.policyCatalogId?.trim() || null,
        moderation_status: params.moderationStatus ?? null,
        actor: params.actor?.trim() || "operator",
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationPlans(params: {
  queueState?: string;
  policyCatalogId?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.queueState?.trim()) {
    searchParams.set("queue_state", params.queueState.trim());
  }
  if (params.policyCatalogId?.trim()) {
    searchParams.set("policy_catalog_id", params.policyCatalogId.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPlanListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-plans${suffix}`,
  );
}

export async function approveProviderProvenanceSchedulerSearchModerationPlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-plans/${encodeURIComponent(params.planId)}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function applyProviderProvenanceSchedulerSearchModerationPlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationPlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-plans/${encodeURIComponent(params.planId)}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy(params: {
  name: string;
  description?: string | null;
  actionScope?: "any" | "update" | "delete" | "restore";
  requireApprovalNote?: boolean;
  guidance?: string | null;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        action_scope: params.actionScope ?? "any",
        require_approval_note: params.requireApprovalNote ?? false,
        guidance: params.guidance ?? null,
        name_prefix: params.namePrefix ?? null,
        name_suffix: params.nameSuffix ?? null,
        description_append: params.descriptionAppend ?? null,
        default_moderation_status: params.defaultModerationStatus ?? "approved",
        governance_view: params.governanceView ?? "pending_queue",
        window_days: params.windowDays ?? 30,
        stale_pending_hours: params.stalePendingHours ?? 24,
        minimum_score: params.minimumScore ?? 0,
        require_note: params.requireNote ?? false,
        created_by_tab_id: params.createdByTabId?.trim() || null,
        created_by_tab_label: params.createdByTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies(params: {
  actionScope?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.actionScope?.trim()) {
    searchParams.set("action_scope", params.actionScope.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy(params: {
  governancePolicyId: string;
  name?: string | null;
  description?: string | null;
  actionScope?: "any" | "update" | "delete" | "restore";
  requireApprovalNote?: boolean;
  guidance?: string | null;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string | null;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/${encodeURIComponent(params.governancePolicyId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.actionScope ? { action_scope: params.actionScope } : {}),
        ...(params.requireApprovalNote !== undefined ? { require_approval_note: params.requireApprovalNote } : {}),
        ...(params.guidance !== undefined ? { guidance: params.guidance } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: params.windowDays }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: params.stalePendingHours }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: params.minimumScore }
          : {}),
        ...(params.requireNote !== undefined ? { require_note: params.requireNote } : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicy(params: {
  governancePolicyId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string | null;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/${encodeURIComponent(params.governancePolicyId)}/delete`,
    {
      method: "POST",
      body: JSON.stringify({
        actor_tab_id: params.actorTabId?.trim() || null,
        actor_tab_label: params.actorTabLabel?.trim() || null,
        reason: params.reason?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisions(
  governancePolicyId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/${encodeURIComponent(governancePolicyId)}/revisions`,
  );
}

export async function restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevision(params: {
  governancePolicyId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string | null;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/${encodeURIComponent(params.governancePolicyId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
    {
      method: "POST",
      body: JSON.stringify({
        actor_tab_id: params.actorTabId?.trim() || null,
        actor_tab_label: params.actorTabLabel?.trim() || null,
        reason: params.reason?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits(params: {
  governancePolicyId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.governancePolicyId?.trim()) {
    searchParams.set("governance_policy_id", params.governancePolicyId.trim());
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
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/audits${suffix}`,
  );
}

export async function bulkGovernProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicies(params: {
  action: "update" | "delete" | "restore";
  governancePolicyIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string | null;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  actionScope?: "any" | "update" | "delete" | "restore";
  requireApprovalNote?: boolean;
  guidance?: string | null;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        governance_policy_ids: params.governancePolicyIds,
        actor_tab_id: params.actorTabId?.trim() || null,
        actor_tab_label: params.actorTabLabel?.trim() || null,
        reason: params.reason?.trim() || null,
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: params.windowDays }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: params.stalePendingHours }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: params.minimumScore }
          : {}),
        ...(params.requireNote !== undefined ? { require_note: params.requireNote } : {}),
        ...(params.actionScope ? { action_scope: params.actionScope } : {}),
        ...(params.requireApprovalNote !== undefined ? { require_approval_note: params.requireApprovalNote } : {}),
        ...(params.guidance !== undefined ? { guidance: params.guidance } : {}),
      }),
    },
  );
}

export async function stageProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan(params: {
  catalogIds: string[];
  action: "update" | "delete" | "restore";
  governancePolicyId?: string;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  actor?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans",
    {
      method: "POST",
      body: JSON.stringify({
        catalog_ids: params.catalogIds,
        action: params.action,
        governance_policy_id: params.governancePolicyId?.trim() || null,
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: Math.max(7, Math.min(Math.round(params.windowDays), 180)) }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: Math.max(1, Math.min(Math.round(params.stalePendingHours), 24 * 30)) }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: Math.max(Math.round(params.minimumScore), 0) }
          : {}),
        ...(typeof params.requireNote === "boolean" ? { require_note: params.requireNote } : {}),
        actor: params.actor?.trim() || "operator",
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernancePlans(params: {
  queueState?: string;
  governancePolicyId?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.queueState?.trim()) {
    searchParams.set("queue_state", params.queueState.trim());
  }
  if (params.governancePolicyId?.trim()) {
    searchParams.set("governance_policy_id", params.governancePolicyId.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans${suffix}`,
  );
}

export async function approveProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/${encodeURIComponent(params.planId)}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function applyProviderProvenanceSchedulerSearchModerationCatalogGovernancePlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/${encodeURIComponent(params.planId)}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicy(params: {
  name: string;
  description?: string;
  actionScope?: "any" | "update" | "delete" | "restore";
  requireApprovalNote?: boolean;
  guidance?: string | null;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  policyActionScope?: "any" | "update" | "delete" | "restore" | null;
  policyRequireApprovalNote?: boolean | null;
  policyGuidance?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected" | null;
  governanceView?: string | null;
  windowDays?: number | null;
  stalePendingHours?: number | null;
  minimumScore?: number | null;
  requireNote?: boolean | null;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        action_scope: params.actionScope ?? "any",
        require_approval_note: params.requireApprovalNote ?? false,
        guidance: params.guidance ?? null,
        name_prefix: params.namePrefix ?? null,
        name_suffix: params.nameSuffix ?? null,
        description_append: params.descriptionAppend ?? null,
        policy_action_scope: params.policyActionScope ?? null,
        policy_require_approval_note: params.policyRequireApprovalNote ?? null,
        policy_guidance: params.policyGuidance ?? null,
        default_moderation_status: params.defaultModerationStatus ?? null,
        governance_view: params.governanceView ?? null,
        window_days: params.windowDays ?? null,
        stale_pending_hours: params.stalePendingHours ?? null,
        minimum_score: params.minimumScore ?? null,
        require_note: params.requireNote ?? null,
        created_by_tab_id: params.createdByTabId?.trim() || null,
        created_by_tab_label: params.createdByTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies(params: {
  actionScope?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.actionScope?.trim()) {
    searchParams.set("action_scope", params.actionScope.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies${suffix}`,
  );
}

export async function stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan(params: {
  governancePolicyIds: string[];
  action: "update" | "delete" | "restore";
  metaPolicyId?: string;
  namePrefix?: string | null;
  nameSuffix?: string | null;
  descriptionAppend?: string | null;
  actionScope?: "any" | "update" | "delete" | "restore";
  requireApprovalNote?: boolean;
  guidance?: string | null;
  defaultModerationStatus?: "pending" | "approved" | "rejected";
  governanceView?: string;
  windowDays?: number;
  stalePendingHours?: number;
  minimumScore?: number;
  requireNote?: boolean;
  actor?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry>(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans",
    {
      method: "POST",
      body: JSON.stringify({
        governance_policy_ids: params.governancePolicyIds,
        action: params.action,
        meta_policy_id: params.metaPolicyId?.trim() || null,
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined ? { description_append: params.descriptionAppend } : {}),
        ...(params.actionScope ? { action_scope: params.actionScope } : {}),
        ...(params.requireApprovalNote !== undefined ? { require_approval_note: params.requireApprovalNote } : {}),
        ...(params.guidance !== undefined ? { guidance: params.guidance } : {}),
        ...(params.defaultModerationStatus ? { default_moderation_status: params.defaultModerationStatus } : {}),
        ...(params.governanceView ? { governance_view: params.governanceView } : {}),
        ...(typeof params.windowDays === "number" && Number.isFinite(params.windowDays)
          ? { window_days: Math.max(7, Math.min(Math.round(params.windowDays), 180)) }
          : {}),
        ...(typeof params.stalePendingHours === "number" && Number.isFinite(params.stalePendingHours)
          ? { stale_pending_hours: Math.max(1, Math.min(Math.round(params.stalePendingHours), 24 * 30)) }
          : {}),
        ...(typeof params.minimumScore === "number" && Number.isFinite(params.minimumScore)
          ? { minimum_score: Math.max(Math.round(params.minimumScore), 0) }
          : {}),
        ...(typeof params.requireNote === "boolean" ? { require_note: params.requireNote } : {}),
        actor: params.actor?.trim() || "operator",
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans(params: {
  queueState?: string;
  metaPolicyId?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.queueState?.trim()) {
    searchParams.set("queue_state", params.queueState.trim());
  }
  if (params.metaPolicyId?.trim()) {
    searchParams.set("meta_policy_id", params.metaPolicyId.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanListPayload>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans${suffix}`,
  );
}

export async function approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/${encodeURIComponent(params.planId)}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}

export async function applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlan(params: {
  planId: string;
  actor?: string;
  note?: string | null;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry>(
    `/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/${encodeURIComponent(params.planId)}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        actor: params.actor?.trim() || "operator",
        note: params.note ?? null,
        source_tab_id: params.sourceTabId?.trim() || null,
        source_tab_label: params.sourceTabLabel?.trim() || null,
      }),
    },
  );
}
