import { fetchJson } from "./base";
import type {
  ProviderProvenanceAnalyticsPresetEntry,
  ProviderProvenanceAnalyticsPresetListPayload,
  ProviderProvenanceDashboardLayout,
  ProviderProvenanceDashboardViewEntry,
  ProviderProvenanceDashboardViewListPayload,
} from "../controlRoomDefinitions";

export * from "./providerProvenanceExports";
export * from "./providerProvenanceReports";
export * from "./providerProvenanceSchedulerCore";
export * from "./providerProvenanceSchedulerSearch";
export * from "./providerProvenanceSchedulerStitched";
export * from "./providerProvenanceSchedulerNarrativeAssets";
export * from "./providerProvenanceSchedulerNarrativeGovernance";

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
