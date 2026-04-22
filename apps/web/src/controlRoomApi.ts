import { apiBase } from "./controlRoomDefinitions";
import type {
  MarketDataIngestionJobRecord,
  MarketDataLineageHistoryRecord,
  ProviderProvenanceAnalyticsPresetEntry,
  ProviderProvenanceAnalyticsPresetListPayload,
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceDashboardViewEntry,
  ProviderProvenanceDashboardViewListPayload,
  ProviderProvenanceExportAnalyticsPayload,
  ProviderProvenanceExportJobEscalationResult,
  ProviderProvenanceExportJobEntry,
  ProviderProvenanceExportJobHistoryPayload,
  ProviderProvenanceExportJobListPayload,
  ProviderProvenanceExportJobPolicyResult,
  ProviderProvenanceSchedulerHealthAnalyticsPayload,
  ProviderProvenanceSchedulerAlertHistoryPayload,
  ProviderProvenanceSchedulerHealthExportPayload,
  ProviderProvenanceSchedulerHealthHistoryPayload,
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
  ProviderProvenanceSchedulerNarrativeRegistryEntry,
  ProviderProvenanceSchedulerNarrativeRegistryListPayload,
  ProviderProvenanceSchedulerNarrativeRegistryRevisionListPayload,
  ProviderProvenanceSchedulerNarrativeTemplateEntry,
  ProviderProvenanceSchedulerNarrativeTemplateListPayload,
  ProviderProvenanceSchedulerNarrativeTemplateRevisionListPayload,
  ProviderProvenanceScheduledReportEntry,
  ProviderProvenanceScheduledReportHistoryPayload,
  ProviderProvenanceScheduledReportListPayload,
  ProviderProvenanceScheduledReportRunDuePayload,
  ProviderProvenanceScheduledReportRunResult,
  RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload,
} from "./controlRoomDefinitions";

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const errorPayload = await response.json() as { detail?: unknown };
      if (typeof errorPayload.detail === "string" && errorPayload.detail.trim()) {
        detail = `${response.status} ${errorPayload.detail}`;
      }
    } catch {
      // Ignore malformed error payloads and fall back to the HTTP status text.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export async function listMarketDataLineageHistory(params: {
  symbol?: string;
  timeframe?: string;
  syncStatus?: string;
  validationClaim?: string;
  sort?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.syncStatus?.trim()) {
    searchParams.set("sync_status", params.syncStatus.trim());
  }
  if (params.validationClaim?.trim()) {
    searchParams.set("validation_claim", params.validationClaim.trim());
  }
  if (params.sort?.trim()) {
    searchParams.set("sort", params.sort.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<MarketDataLineageHistoryRecord[]>(`/market-data/lineage-history${suffix}`);
}

export async function listMarketDataIngestionJobs(params: {
  symbol?: string;
  timeframe?: string;
  operation?: string;
  status?: string;
  sort?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.operation?.trim()) {
    searchParams.set("operation", params.operation.trim());
  }
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.sort?.trim()) {
    searchParams.set("sort", params.sort.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<MarketDataIngestionJobRecord[]>(`/market-data/ingestion-jobs${suffix}`);
}

export async function createProviderProvenanceExportJob(params: {
  content: string;
  requestedByTabId?: string;
  requestedByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceExportJobEntry>("/operator/provider-provenance-exports", {
    method: "POST",
    body: JSON.stringify({
      content: params.content,
      ...(params.requestedByTabId?.trim() ? { requested_by_tab_id: params.requestedByTabId.trim() } : {}),
      ...(params.requestedByTabLabel?.trim() ? { requested_by_tab_label: params.requestedByTabLabel.trim() } : {}),
    }),
  });
}

export async function listProviderProvenanceExportJobs(params: {
  exportScope?: string;
  focusKey?: string;
  limit?: number;
  marketDataProvider?: string;
  providerLabel?: string;
  requestedByTabId?: string;
  search?: string;
  status?: string;
  symbol?: string;
  timeframe?: string;
  vendorField?: string;
  venue?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.exportScope?.trim()) {
    searchParams.set("export_scope", params.exportScope.trim());
  }
  if (params.focusKey?.trim()) {
    searchParams.set("focus_key", params.focusKey.trim());
  }
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.providerLabel?.trim()) {
    searchParams.set("provider_label", params.providerLabel.trim());
  }
  if (params.vendorField?.trim()) {
    searchParams.set("vendor_field", params.vendorField.trim());
  }
  if (params.marketDataProvider?.trim()) {
    searchParams.set("market_data_provider", params.marketDataProvider.trim());
  }
  if (params.venue?.trim()) {
    searchParams.set("venue", params.venue.trim());
  }
  if (params.requestedByTabId?.trim()) {
    searchParams.set("requested_by_tab_id", params.requestedByTabId.trim());
  }
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 500))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceExportJobListPayload>(
    `/operator/provider-provenance-exports${suffix}`,
  );
}

export async function escalateProviderProvenanceExportJob(params: {
  jobId: string;
  actor?: string;
  reason?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
  deliveryTargets?: string[];
}) {
  return fetchJson<ProviderProvenanceExportJobEscalationResult>(
    `/operator/provider-provenance-exports/${encodeURIComponent(params.jobId)}/escalate`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actor?.trim() ? { actor: params.actor.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.sourceTabLabel?.trim() ? { source_tab_label: params.sourceTabLabel.trim() } : {}),
        ...(params.deliveryTargets?.length ? { delivery_targets: params.deliveryTargets } : {}),
      }),
    },
  );
}

export async function updateProviderProvenanceExportJobPolicy(params: {
  jobId: string;
  actor?: string;
  routingPolicyId?: string;
  approvalPolicyId?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
  deliveryTargets?: string[];
}) {
  return fetchJson<ProviderProvenanceExportJobPolicyResult>(
    `/operator/provider-provenance-exports/${encodeURIComponent(params.jobId)}/policy`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actor?.trim() ? { actor: params.actor.trim() } : {}),
        ...(params.routingPolicyId?.trim() ? { routing_policy_id: params.routingPolicyId.trim() } : {}),
        ...(params.approvalPolicyId?.trim() ? { approval_policy_id: params.approvalPolicyId.trim() } : {}),
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.sourceTabLabel?.trim() ? { source_tab_label: params.sourceTabLabel.trim() } : {}),
        ...(params.deliveryTargets?.length ? { delivery_targets: params.deliveryTargets } : {}),
      }),
    },
  );
}

export async function approveProviderProvenanceExportJob(params: {
  jobId: string;
  actor?: string;
  note?: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceExportJobPolicyResult>(
    `/operator/provider-provenance-exports/${encodeURIComponent(params.jobId)}/approval`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actor?.trim() ? { actor: params.actor.trim() } : {}),
        ...(params.note?.trim() ? { note: params.note.trim() } : {}),
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.sourceTabLabel?.trim() ? { source_tab_label: params.sourceTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function getProviderProvenanceExportAnalytics(params: {
  focusKey?: string;
  marketDataProvider?: string;
  providerLabel?: string;
  requestedByTabId?: string;
  resultLimit?: number;
  search?: string;
  status?: string;
  symbol?: string;
  timeframe?: string;
  vendorField?: string;
  venue?: string;
  windowDays?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.focusKey?.trim()) {
    searchParams.set("focus_key", params.focusKey.trim());
  }
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.providerLabel?.trim()) {
    searchParams.set("provider_label", params.providerLabel.trim());
  }
  if (params.vendorField?.trim()) {
    searchParams.set("vendor_field", params.vendorField.trim());
  }
  if (params.marketDataProvider?.trim()) {
    searchParams.set("market_data_provider", params.marketDataProvider.trim());
  }
  if (params.venue?.trim()) {
    searchParams.set("venue", params.venue.trim());
  }
  if (params.requestedByTabId?.trim()) {
    searchParams.set("requested_by_tab_id", params.requestedByTabId.trim());
  }
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.resultLimit === "number" && Number.isFinite(params.resultLimit)) {
    searchParams.set("result_limit", `${Math.max(1, Math.min(Math.round(params.resultLimit), 50))}`);
  }
  if (typeof params.windowDays === "number" && Number.isFinite(params.windowDays)) {
    searchParams.set("window_days", `${Math.max(3, Math.min(Math.round(params.windowDays), 90))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceExportAnalyticsPayload>(
    `/operator/provider-provenance-exports/analytics${suffix}`,
  );
}

export async function getProviderProvenanceSchedulerHealthAnalytics(params: {
  status?: string;
  windowDays?: number;
  historyLimit?: number;
  drilldownBucketKey?: string;
  drilldownHistoryLimit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (typeof params.windowDays === "number" && Number.isFinite(params.windowDays)) {
    searchParams.set("window_days", `${Math.max(3, Math.min(Math.round(params.windowDays), 90))}`);
  }
  if (typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)) {
    searchParams.set("history_limit", `${Math.max(1, Math.min(Math.round(params.historyLimit), 50))}`);
  }
  if (params.drilldownBucketKey?.trim()) {
    searchParams.set("drilldown_bucket_key", params.drilldownBucketKey.trim());
  }
  if (typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)) {
    searchParams.set("drilldown_history_limit", `${Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerHealthAnalyticsPayload>(
    `/operator/provider-provenance-analytics/scheduler-health/analytics${suffix}`,
  );
}

export async function listProviderProvenanceSchedulerHealthHistory(params: {
  status?: string;
  limit?: number;
  offset?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  if (typeof params.offset === "number" && Number.isFinite(params.offset)) {
    searchParams.set("offset", `${Math.max(0, Math.min(Math.round(params.offset), 10000))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerHealthHistoryPayload>(
    `/operator/provider-provenance-analytics/scheduler-health${suffix}`,
  );
}

export async function listProviderProvenanceSchedulerAlertHistory(params: {
  category?: string;
  status?: string;
  narrativeFacet?: string;
  search?: string;
  limit?: number;
  offset?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.category?.trim()) {
    searchParams.set("category", params.category.trim());
  }
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
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
  if (typeof params.offset === "number" && Number.isFinite(params.offset)) {
    searchParams.set("offset", `${Math.max(0, Math.min(Math.round(params.offset), 10000))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerAlertHistoryPayload>(
    `/operator/provider-provenance-analytics/scheduler-alerts${suffix}`,
  );
}

export async function exportProviderProvenanceSchedulerHealth(params: {
  status?: string;
  windowDays?: number;
  historyLimit?: number;
  drilldownBucketKey?: string;
  drilldownHistoryLimit?: number;
  offset?: number;
  limit?: number;
  format: "json" | "csv";
}) {
  const searchParams = new URLSearchParams();
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (typeof params.windowDays === "number" && Number.isFinite(params.windowDays)) {
    searchParams.set("window_days", `${Math.max(3, Math.min(Math.round(params.windowDays), 90))}`);
  }
  if (typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)) {
    searchParams.set("history_limit", `${Math.max(1, Math.min(Math.round(params.historyLimit), 50))}`);
  }
  if (params.drilldownBucketKey?.trim()) {
    searchParams.set("drilldown_bucket_key", params.drilldownBucketKey.trim());
  }
  if (typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)) {
    searchParams.set("drilldown_history_limit", `${Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100))}`);
  }
  if (typeof params.offset === "number" && Number.isFinite(params.offset)) {
    searchParams.set("offset", `${Math.max(0, Math.min(Math.round(params.offset), 10000))}`);
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  searchParams.set("format", params.format);
  return fetchJson<ProviderProvenanceSchedulerHealthExportPayload>(
    `/operator/provider-provenance-analytics/scheduler-health/export?${searchParams.toString()}`,
  );
}

export async function reconstructProviderProvenanceSchedulerHealthExport(params: {
  alertCategory: string;
  detectedAt: string;
  resolvedAt?: string | null;
  narrativeMode?: "matched_status" | "mixed_status_post_resolution";
  format?: "json" | "csv";
  historyLimit?: number;
  drilldownHistoryLimit?: number;
}) {
  return fetchJson<ProviderProvenanceSchedulerHealthExportPayload>(
    "/operator/provider-provenance-analytics/scheduler-health/reconstruct-export",
    {
      method: "POST",
      body: JSON.stringify({
        alert_category: params.alertCategory,
        detected_at: params.detectedAt,
        resolved_at: params.resolvedAt ?? null,
        narrative_mode: params.narrativeMode ?? "matched_status",
        format: params.format ?? "json",
        history_limit:
          typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)
            ? Math.max(1, Math.min(Math.round(params.historyLimit), 200))
            : 25,
        drilldown_history_limit:
          typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)
            ? Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100))
            : 24,
      }),
    },
  );
}

export async function exportProviderProvenanceSchedulerStitchedNarrativeReport(params: {
  alertCategory?: string;
  status?: string;
  narrativeFacet?: string;
  search?: string;
  offset?: number;
  occurrenceLimit?: number;
  format?: "json" | "csv";
  historyLimit?: number;
  drilldownHistoryLimit?: number;
}) {
  return fetchJson<ProviderProvenanceSchedulerHealthExportPayload>(
    "/operator/provider-provenance-analytics/scheduler-alerts/report-export",
    {
      method: "POST",
      body: JSON.stringify({
        alert_category: params.alertCategory?.trim() || null,
        status: params.status?.trim() || null,
        narrative_facet: params.narrativeFacet?.trim() || null,
        search: params.search?.trim() || null,
        offset:
          typeof params.offset === "number" && Number.isFinite(params.offset)
            ? Math.max(0, Math.min(Math.round(params.offset), 10000))
            : 0,
        occurrence_limit:
          typeof params.occurrenceLimit === "number" && Number.isFinite(params.occurrenceLimit)
            ? Math.max(1, Math.min(Math.round(params.occurrenceLimit), 50))
            : 8,
        format: params.format ?? "json",
        history_limit:
          typeof params.historyLimit === "number" && Number.isFinite(params.historyLimit)
            ? Math.max(1, Math.min(Math.round(params.historyLimit), 200))
            : 25,
        drilldown_history_limit:
          typeof params.drilldownHistoryLimit === "number" && Number.isFinite(params.drilldownHistoryLimit)
            ? Math.max(1, Math.min(Math.round(params.drilldownHistoryLimit), 100))
            : 24,
      }),
    },
  );
}

export async function downloadProviderProvenanceExportJob(params: {
  jobId: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.sourceTabId?.trim()) {
    searchParams.set("source_tab_id", params.sourceTabId.trim());
  }
  if (params.sourceTabLabel?.trim()) {
    searchParams.set("source_tab_label", params.sourceTabLabel.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceExportJobEntry & { content: string }>(
    `/operator/provider-provenance-exports/${encodeURIComponent(params.jobId)}/download${suffix}`,
  );
}

export async function getProviderProvenanceExportJobHistory(jobId: string) {
  return fetchJson<ProviderProvenanceExportJobHistoryPayload>(
    `/operator/provider-provenance-exports/${encodeURIComponent(jobId)}/history`,
  );
}

export async function createProviderProvenanceAnalyticsPreset(params: {
  name: string;
  description?: string;
  query: Record<string, unknown>;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceAnalyticsPresetEntry>(
    "/operator/provider-provenance-analytics/presets",
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

export async function listProviderProvenanceAnalyticsPresets(params: {
  createdByTabId?: string;
  focusScope?: "current_focus" | "all_focuses";
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
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceAnalyticsPresetListPayload>(
    `/operator/provider-provenance-analytics/presets${suffix}`,
  );
}

export async function createProviderProvenanceDashboardView(params: {
  name: string;
  description?: string;
  query?: Record<string, unknown>;
  layout: ProviderProvenanceDashboardLayout;
  presetId?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceDashboardViewEntry>(
    "/operator/provider-provenance-analytics/views",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        ...(params.query ? { query: params.query } : {}),
        layout: params.layout,
        ...(params.presetId?.trim() ? { preset_id: params.presetId.trim() } : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceDashboardViews(params: {
  presetId?: string;
  createdByTabId?: string;
  focusScope?: "current_focus" | "all_focuses";
  highlightPanel?: ProviderProvenanceDashboardLayout["highlight_panel"];
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.presetId?.trim()) {
    searchParams.set("preset_id", params.presetId.trim());
  }
  if (params.createdByTabId?.trim()) {
    searchParams.set("created_by_tab_id", params.createdByTabId.trim());
  }
  if (params.focusScope?.trim()) {
    searchParams.set("focus_scope", params.focusScope.trim());
  }
  if (params.highlightPanel?.trim()) {
    searchParams.set("highlight_panel", params.highlightPanel.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceDashboardViewListPayload>(
    `/operator/provider-provenance-analytics/views${suffix}`,
  );
}

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

export async function createProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(params: {
  name: string;
  description?: string;
  step?: {
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
  };
  originCatalogId?: string;
  originStepId?: string;
  governancePolicyTemplateId?: string;
  governancePolicyCatalogId?: string;
  governanceApprovalLane?: string;
  governanceApprovalPriority?: string;
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.step
          ? {
              step: {
                ...(params.step.stepId?.trim() ? { step_id: params.step.stepId.trim() } : {}),
                item_type: params.step.itemType,
                item_ids: params.step.itemIds,
                action: "update",
                ...(params.step.namePrefix !== undefined ? { name_prefix: params.step.namePrefix } : {}),
                ...(params.step.nameSuffix !== undefined ? { name_suffix: params.step.nameSuffix } : {}),
                ...(params.step.descriptionAppend !== undefined
                  ? { description_append: params.step.descriptionAppend }
                  : {}),
                ...(params.step.queryPatch ? { query_patch: params.step.queryPatch } : {}),
                ...(params.step.layoutPatch ? { layout_patch: params.step.layoutPatch } : {}),
                ...(params.step.templateId?.trim() ? { template_id: params.step.templateId.trim() } : {}),
                ...(params.step.clearTemplateLink ? { clear_template_link: true } : {}),
              },
            }
          : {}),
        ...(params.originCatalogId?.trim() ? { origin_catalog_id: params.originCatalogId.trim() } : {}),
        ...(params.originStepId?.trim() ? { origin_step_id: params.originStepId.trim() } : {}),
        ...(params.governancePolicyTemplateId?.trim()
          ? { governance_policy_template_id: params.governancePolicyTemplateId.trim() }
          : {}),
        ...(params.governancePolicyCatalogId?.trim()
          ? { governance_policy_catalog_id: params.governancePolicyCatalogId.trim() }
          : {}),
        ...(params.governanceApprovalLane?.trim()
          ? { governance_approval_lane: params.governanceApprovalLane.trim() }
          : {}),
        ...(params.governanceApprovalPriority?.trim()
          ? { governance_approval_priority: params.governanceApprovalPriority.trim() }
          : {}),
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim()
          ? { created_by_tab_label: params.createdByTabLabel.trim() }
          : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates(params: {
  itemType?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.itemType?.trim()) {
    searchParams.set("item_type", params.itemType.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", String(Math.max(1, Math.min(Math.round(params.limit), 100))));
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates${suffix}`,
  );
}

export async function updateProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(params: {
  hierarchyStepTemplateId: string;
  name?: string;
  description?: string;
  itemIds?: string[];
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  layoutPatch?: Record<string, unknown>;
  templateId?: string;
  clearTemplateLink?: boolean;
  governancePolicyTemplateId?: string;
  governancePolicyCatalogId?: string;
  governanceApprovalLane?: string;
  governanceApprovalPriority?: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(params.hierarchyStepTemplateId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        ...(params.name !== undefined ? { name: params.name } : {}),
        ...(params.description !== undefined ? { description: params.description } : {}),
        ...(params.itemIds !== undefined ? { item_ids: params.itemIds } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined
          ? { description_append: params.descriptionAppend }
          : {}),
        ...(params.queryPatch !== undefined ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch !== undefined ? { layout_patch: params.layoutPatch } : {}),
        ...(params.templateId !== undefined ? { template_id: params.templateId } : {}),
        ...(params.clearTemplateLink !== undefined ? { clear_template_link: params.clearTemplateLink } : {}),
        ...(params.governancePolicyTemplateId !== undefined
          ? { governance_policy_template_id: params.governancePolicyTemplateId }
          : {}),
        ...(params.governancePolicyCatalogId !== undefined
          ? { governance_policy_catalog_id: params.governancePolicyCatalogId }
          : {}),
        ...(params.governanceApprovalLane !== undefined
          ? { governance_approval_lane: params.governanceApprovalLane }
          : {}),
        ...(params.governanceApprovalPriority !== undefined
          ? { governance_approval_priority: params.governanceApprovalPriority }
          : {}),
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function deleteProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(params: {
  hierarchyStepTemplateId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(params.hierarchyStepTemplateId)}/delete`,
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

export async function runProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateBulkGovernance(params: {
  action: "delete" | "restore" | "update";
  hierarchyStepTemplateIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
  namePrefix?: string;
  nameSuffix?: string;
  descriptionAppend?: string;
  itemIds?: string[];
  stepNamePrefix?: string;
  stepNameSuffix?: string;
  stepDescriptionAppend?: string;
  queryPatch?: Record<string, unknown>;
  layoutPatch?: Record<string, unknown>;
  templateId?: string;
  clearTemplateLink?: boolean;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/bulk-governance",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        hierarchy_step_template_ids: params.hierarchyStepTemplateIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
        ...(params.namePrefix !== undefined ? { name_prefix: params.namePrefix } : {}),
        ...(params.nameSuffix !== undefined ? { name_suffix: params.nameSuffix } : {}),
        ...(params.descriptionAppend !== undefined
          ? { description_append: params.descriptionAppend }
          : {}),
        ...(params.itemIds !== undefined ? { item_ids: params.itemIds } : {}),
        ...(params.stepNamePrefix !== undefined ? { step_name_prefix: params.stepNamePrefix } : {}),
        ...(params.stepNameSuffix !== undefined ? { step_name_suffix: params.stepNameSuffix } : {}),
        ...(params.stepDescriptionAppend !== undefined
          ? { step_description_append: params.stepDescriptionAppend }
          : {}),
        ...(params.queryPatch !== undefined ? { query_patch: params.queryPatch } : {}),
        ...(params.layoutPatch !== undefined ? { layout_patch: params.layoutPatch } : {}),
        ...(params.templateId !== undefined ? { template_id: params.templateId } : {}),
        ...(params.clearTemplateLink !== undefined ? { clear_template_link: params.clearTemplateLink } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisions(
  hierarchyStepTemplateId: string,
) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(hierarchyStepTemplateId)}/revisions`,
  );
}

export async function listProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAudits(params: {
  hierarchyStepTemplateId?: string;
  action?: string;
  actorTabId?: string;
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.hierarchyStepTemplateId?.trim()) {
    searchParams.set("hierarchy_step_template_id", params.hierarchyStepTemplateId.trim());
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
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditListPayload>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/audits${suffix}`,
  );
}

export async function restoreProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevision(params: {
  hierarchyStepTemplateId: string;
  revisionId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(params.hierarchyStepTemplateId)}/revisions/${encodeURIComponent(params.revisionId)}/restore`,
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

export async function applyProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(params: {
  hierarchyStepTemplateId: string;
  catalogIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeBulkGovernanceResult>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(params.hierarchyStepTemplateId)}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        catalog_ids: params.catalogIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate(params: {
  hierarchyStepTemplateId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/${encodeURIComponent(params.hierarchyStepTemplateId)}/stage`,
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

export async function stageProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates(params: {
  hierarchyStepTemplateIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/stage-batch",
    {
      method: "POST",
      body: JSON.stringify({
        hierarchy_step_template_ids: params.hierarchyStepTemplateIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.reason?.trim() ? { reason: params.reason.trim() } : {}),
      }),
    },
  );
}

export async function stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(params: {
  catalogId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  reason?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/${encodeURIComponent(params.catalogId)}/stage`,
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

export async function listProviderProvenanceSchedulerNarrativeGovernancePlans(params: {
  itemType?: string;
  status?: string;
  queueState?: string;
  approvalLane?: string;
  approvalPriority?: string;
  policyTemplateId?: string;
  policyCatalogId?: string;
  sourceHierarchyStepTemplateId?: string;
  search?: string;
  sort?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.itemType?.trim()) {
    searchParams.set("item_type", params.itemType.trim());
  }
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
  if (typeof params.policyTemplateId === "string") {
    searchParams.set(
      "policy_template_id",
      params.policyTemplateId === "" ? "__none__" : params.policyTemplateId.trim(),
    );
  }
  if (typeof params.policyCatalogId === "string") {
    searchParams.set(
      "policy_catalog_id",
      params.policyCatalogId === "" ? "__none__" : params.policyCatalogId.trim(),
    );
  }
  if (typeof params.sourceHierarchyStepTemplateId === "string") {
    searchParams.set(
      "source_hierarchy_step_template_id",
      params.sourceHierarchyStepTemplateId === ""
        ? "__none__"
        : params.sourceHierarchyStepTemplateId.trim(),
    );
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
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/plans${suffix}`,
  );
}

export async function approveProviderProvenanceSchedulerNarrativeGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  note?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/${params.planId}/approve`,
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

export async function applyProviderProvenanceSchedulerNarrativeGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/${params.planId}/apply`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function runProviderProvenanceSchedulerNarrativeGovernancePlanBatchAction(params: {
  action: "approve" | "apply";
  planIds: string[];
  actorTabId?: string;
  actorTabLabel?: string;
  note?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult>(
    "/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/batch",
    {
      method: "POST",
      body: JSON.stringify({
        action: params.action,
        plan_ids: params.planIds,
        ...(params.actorTabId?.trim() ? { actor_tab_id: params.actorTabId.trim() } : {}),
        ...(params.actorTabLabel?.trim() ? { actor_tab_label: params.actorTabLabel.trim() } : {}),
        ...(params.note?.trim() ? { note: params.note.trim() } : {}),
      }),
    },
  );
}

export async function rollbackProviderProvenanceSchedulerNarrativeGovernancePlan(params: {
  planId: string;
  actorTabId?: string;
  actorTabLabel?: string;
  note?: string;
}) {
  return fetchJson<ProviderProvenanceSchedulerNarrativeGovernancePlan>(
    `/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/${params.planId}/rollback`,
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

export async function createProviderProvenanceScheduledReport(params: {
  name: string;
  description?: string;
  query?: Record<string, unknown>;
  layout?: ProviderProvenanceDashboardLayout;
  presetId?: string;
  viewId?: string;
  cadence: "daily" | "weekly";
  status: "scheduled" | "paused";
  createdByTabId?: string;
  createdByTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceScheduledReportEntry>(
    "/operator/provider-provenance-analytics/reports",
    {
      method: "POST",
      body: JSON.stringify({
        name: params.name,
        description: params.description ?? "",
        ...(params.query ? { query: params.query } : {}),
        ...(params.layout ? { layout: params.layout } : {}),
        ...(params.presetId?.trim() ? { preset_id: params.presetId.trim() } : {}),
        ...(params.viewId?.trim() ? { view_id: params.viewId.trim() } : {}),
        cadence: params.cadence,
        status: params.status,
        ...(params.createdByTabId?.trim() ? { created_by_tab_id: params.createdByTabId.trim() } : {}),
        ...(params.createdByTabLabel?.trim() ? { created_by_tab_label: params.createdByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listProviderProvenanceScheduledReports(params: {
  status?: "scheduled" | "paused";
  cadence?: "daily" | "weekly";
  presetId?: string;
  viewId?: string;
  createdByTabId?: string;
  focusScope?: "current_focus" | "all_focuses";
  search?: string;
  limit?: number;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.cadence?.trim()) {
    searchParams.set("cadence", params.cadence.trim());
  }
  if (params.presetId?.trim()) {
    searchParams.set("preset_id", params.presetId.trim());
  }
  if (params.viewId?.trim()) {
    searchParams.set("view_id", params.viewId.trim());
  }
  if (params.createdByTabId?.trim()) {
    searchParams.set("created_by_tab_id", params.createdByTabId.trim());
  }
  if (params.focusScope?.trim()) {
    searchParams.set("focus_scope", params.focusScope.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 200))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<ProviderProvenanceScheduledReportListPayload>(
    `/operator/provider-provenance-analytics/reports${suffix}`,
  );
}

export async function runProviderProvenanceScheduledReport(params: {
  reportId: string;
  sourceTabId?: string;
  sourceTabLabel?: string;
}) {
  return fetchJson<ProviderProvenanceScheduledReportRunResult>(
    `/operator/provider-provenance-analytics/reports/${encodeURIComponent(params.reportId)}/run`,
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.sourceTabLabel?.trim() ? { source_tab_label: params.sourceTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function runDueProviderProvenanceScheduledReports(params: {
  sourceTabId?: string;
  sourceTabLabel?: string;
  dueBefore?: string;
  limit?: number;
} = {}) {
  return fetchJson<ProviderProvenanceScheduledReportRunDuePayload>(
    "/operator/provider-provenance-analytics/reports/run-due",
    {
      method: "POST",
      body: JSON.stringify({
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.sourceTabLabel?.trim() ? { source_tab_label: params.sourceTabLabel.trim() } : {}),
        ...(params.dueBefore?.trim() ? { due_before: params.dueBefore.trim() } : {}),
        ...(typeof params.limit === "number" && Number.isFinite(params.limit)
          ? { limit: Math.max(1, Math.min(Math.round(params.limit), 100)) }
          : {}),
      }),
    },
  );
}

export async function getProviderProvenanceScheduledReportHistory(reportId: string) {
  return fetchJson<ProviderProvenanceScheduledReportHistoryPayload>(
    `/operator/provider-provenance-analytics/reports/${encodeURIComponent(reportId)}/history`,
  );
}

export async function createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias(
  payload: {
    intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    sourceTabId: string;
    sourceTabLabel: string;
    templateKey: string;
    templateLabel: string;
  },
) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload>("/replay-links/aliases", {
    method: "POST",
    body: JSON.stringify({
      intent: payload.intent,
      redaction_policy: payload.redactionPolicy,
      retention_policy: payload.retentionPolicy,
      source_tab_id: payload.sourceTabId,
      source_tab_label: payload.sourceTabLabel,
      template_key: payload.templateKey,
      template_label: payload.templateLabel,
    }),
  });
}

export async function resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias(aliasToken: string) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload>(
    `/replay-links/aliases/${encodeURIComponent(aliasToken)}`,
  );
}

export async function revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias(
  aliasToken: string,
  payload: { sourceTabId: string; sourceTabLabel: string },
) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload>(
    `/replay-links/aliases/${encodeURIComponent(aliasToken)}/revoke`,
    {
      method: "POST",
      body: JSON.stringify({
        source_tab_id: payload.sourceTabId,
        source_tab_label: payload.sourceTabLabel,
      }),
    },
  );
}

export async function listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits(params: {
  adminToken?: string;
  action?: string;
  aliasId?: string;
  limit?: number;
  retentionPolicy?: string;
  search?: string;
  sourceTabId?: string;
  templateKey?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.aliasId?.trim()) {
    searchParams.set("alias_id", params.aliasId.trim());
  }
  if (params.templateKey?.trim()) {
    searchParams.set("template_key", params.templateKey.trim());
  }
  if (params.action?.trim() && params.action !== "all") {
    searchParams.set("action", params.action.trim());
  }
  if (params.retentionPolicy?.trim() && params.retentionPolicy !== "all") {
    searchParams.set("retention_policy", params.retentionPolicy.trim());
  }
  if (params.sourceTabId?.trim()) {
    searchParams.set("source_tab_id", params.sourceTabId.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 500))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload>(
    `/replay-links/audits${suffix}`,
    {
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
    },
  );
}

export async function pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits(params: {
  adminToken?: string;
  action?: string;
  aliasId?: string;
  includeManual?: boolean;
  pruneMode: "expired" | "matched";
  recordedBefore?: string;
  retentionPolicy?: string;
  search?: string;
  sourceTabId?: string;
  templateKey?: string;
}) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload>(
    "/replay-links/audits/prune",
    {
      method: "POST",
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
      body: JSON.stringify({
        prune_mode: params.pruneMode,
        ...(params.aliasId?.trim() ? { alias_id: params.aliasId.trim() } : {}),
        ...(params.templateKey?.trim() ? { template_key: params.templateKey.trim() } : {}),
        ...(params.action?.trim() && params.action !== "all" ? { action: params.action.trim() } : {}),
        ...(params.retentionPolicy?.trim() && params.retentionPolicy !== "all"
          ? { retention_policy: params.retentionPolicy.trim() }
          : {}),
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.search?.trim() ? { search: params.search.trim() } : {}),
        ...(params.recordedBefore?.trim() ? { recorded_before: params.recordedBefore.trim() } : {}),
        include_manual: Boolean(params.includeManual),
      }),
    },
  );
}

export async function exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits(params: {
  adminToken?: string;
  action?: string;
  aliasId?: string;
  exportFormat: "json" | "csv";
  retentionPolicy?: string;
  search?: string;
  sourceTabId?: string;
  templateKey?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.aliasId?.trim()) {
    searchParams.set("alias_id", params.aliasId.trim());
  }
  if (params.templateKey?.trim()) {
    searchParams.set("template_key", params.templateKey.trim());
  }
  if (params.action?.trim() && params.action !== "all") {
    searchParams.set("action", params.action.trim());
  }
  if (params.retentionPolicy?.trim() && params.retentionPolicy !== "all") {
    searchParams.set("retention_policy", params.retentionPolicy.trim());
  }
  if (params.sourceTabId?.trim()) {
    searchParams.set("source_tab_id", params.sourceTabId.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  searchParams.set("format", params.exportFormat);
  return fetchJson<{
    content: string;
    content_type: string;
    exported_at: string;
    filename: string;
    format: "json" | "csv";
    record_count: number;
  }>(`/replay-links/audits/export?${searchParams.toString()}`, {
    headers: params.adminToken?.trim()
      ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
      : undefined,
  });
}

export async function createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob(params: {
  adminToken?: string;
  action?: string;
  aliasId?: string;
  exportFormat: "json" | "csv";
  requestedByTabId?: string;
  requestedByTabLabel?: string;
  retentionPolicy?: string;
  search?: string;
  sourceTabId?: string;
  templateKey?: string;
}) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry>(
    "/replay-links/audits/export-jobs",
    {
      method: "POST",
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
      body: JSON.stringify({
        format: params.exportFormat,
        ...(params.aliasId?.trim() ? { alias_id: params.aliasId.trim() } : {}),
        ...(params.templateKey?.trim() ? { template_key: params.templateKey.trim() } : {}),
        ...(params.action?.trim() && params.action !== "all" ? { action: params.action.trim() } : {}),
        ...(params.retentionPolicy?.trim() && params.retentionPolicy !== "all"
          ? { retention_policy: params.retentionPolicy.trim() }
          : {}),
        ...(params.sourceTabId?.trim() ? { source_tab_id: params.sourceTabId.trim() } : {}),
        ...(params.search?.trim() ? { search: params.search.trim() } : {}),
        ...(params.requestedByTabId?.trim() ? { requested_by_tab_id: params.requestedByTabId.trim() } : {}),
        ...(params.requestedByTabLabel?.trim() ? { requested_by_tab_label: params.requestedByTabLabel.trim() } : {}),
      }),
    },
  );
}

export async function listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs(params: {
  adminToken?: string;
  exportFormat?: string;
  limit?: number;
  requestedByTabId?: string;
  search?: string;
  status?: string;
  templateKey?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.templateKey?.trim()) {
    searchParams.set("template_key", params.templateKey.trim());
  }
  if (params.exportFormat?.trim() && params.exportFormat !== "all") {
    searchParams.set("format", params.exportFormat.trim());
  }
  if (params.status?.trim() && params.status !== "all") {
    searchParams.set("status", params.status.trim());
  }
  if (params.requestedByTabId?.trim()) {
    searchParams.set("requested_by_tab_id", params.requestedByTabId.trim());
  }
  if (params.search?.trim()) {
    searchParams.set("search", params.search.trim());
  }
  if (typeof params.limit === "number" && Number.isFinite(params.limit)) {
    searchParams.set("limit", `${Math.max(1, Math.min(Math.round(params.limit), 500))}`);
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload>(
    `/replay-links/audits/export-jobs${suffix}`,
    {
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
    },
  );
}

export async function downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob(params: {
  adminToken?: string;
  jobId: string;
}) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload>(
    `/replay-links/audits/export-jobs/${encodeURIComponent(params.jobId)}/download`,
    {
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
    },
  );
}

export async function getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory(params: {
  adminToken?: string;
  jobId: string;
}) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload>(
    `/replay-links/audits/export-jobs/${encodeURIComponent(params.jobId)}/history`,
    {
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
    },
  );
}

export async function pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs(params: {
  adminToken?: string;
  createdBefore?: string;
  exportFormat?: string;
  pruneMode: "expired" | "matched";
  requestedByTabId?: string;
  search?: string;
  status?: string;
  templateKey?: string;
}) {
  return fetchJson<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload>(
    "/replay-links/audits/export-jobs/prune",
    {
      method: "POST",
      headers: params.adminToken?.trim()
        ? { "X-Akra-Replay-Audit-Admin-Token": params.adminToken.trim() }
        : undefined,
      body: JSON.stringify({
        prune_mode: params.pruneMode,
        ...(params.templateKey?.trim() ? { template_key: params.templateKey.trim() } : {}),
        ...(params.exportFormat?.trim() && params.exportFormat !== "all"
          ? { format: params.exportFormat.trim() }
          : {}),
        ...(params.status?.trim() && params.status !== "all" ? { status: params.status.trim() } : {}),
        ...(params.requestedByTabId?.trim() ? { requested_by_tab_id: params.requestedByTabId.trim() } : {}),
        ...(params.search?.trim() ? { search: params.search.trim() } : {}),
        ...(params.createdBefore?.trim() ? { created_before: params.createdBefore.trim() } : {}),
      }),
    },
  );
}
