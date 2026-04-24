import { fetchJson } from "./base";
import type {
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceScheduledReportEntry,
  ProviderProvenanceScheduledReportHistoryPayload,
  ProviderProvenanceScheduledReportListPayload,
  ProviderProvenanceScheduledReportRunDuePayload,
  ProviderProvenanceScheduledReportRunResult,
} from "../controlRoomDefinitions";

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
