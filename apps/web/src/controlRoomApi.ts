import { apiBase } from "./controlRoomDefinitions";
import type {
  MarketDataIngestionJobRecord,
  MarketDataLineageHistoryRecord,
  ProviderProvenanceExportAnalyticsPayload,
  ProviderProvenanceExportJobEntry,
  ProviderProvenanceExportJobHistoryPayload,
  ProviderProvenanceExportJobListPayload,
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
