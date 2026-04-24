import { fetchJson } from "./base";
import type {
  ProviderProvenanceExportAnalyticsPayload,
  ProviderProvenanceExportJobEscalationResult,
  ProviderProvenanceExportJobEntry,
  ProviderProvenanceExportJobHistoryPayload,
  ProviderProvenanceExportJobListPayload,
  ProviderProvenanceExportJobPolicyResult,
} from "../controlRoomDefinitions";

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
