import { fetchJson } from "./base";
import type {
  ProviderProvenanceSchedulerHealthAnalyticsPayload,
  ProviderProvenanceSchedulerAlertHistoryPayload,
  ProviderProvenanceSchedulerHealthExportPayload,
  ProviderProvenanceSchedulerHealthHistoryPayload,
} from "../controlRoomDefinitions";

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
