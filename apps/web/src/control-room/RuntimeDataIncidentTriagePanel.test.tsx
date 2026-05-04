import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { RuntimeDataIncidentTriagePanel } from "./RuntimeDataIncidentTriagePanel";

function TestDisclosure({
  children,
  summary,
  title,
}: {
  children: ReactNode;
  summary: ReactNode;
  title: string;
}) {
  return (
    <section>
      <h3>{title}</h3>
      <p>{summary}</p>
      {children}
    </section>
  );
}

function fallbackModelValue(name: string) {
  if (name.startsWith("format")) {
    return (value: unknown) => String(value ?? "n/a");
  }
  if (
    name.startsWith("copy")
    || name.startsWith("clear")
    || name.startsWith("handle")
    || name.startsWith("load")
    || name.startsWith("normalize")
    || name.startsWith("reset")
    || name.startsWith("resolve")
    || name.startsWith("set")
    || name.startsWith("toggle")
  ) {
    return vi.fn();
  }
  if (
    name.endsWith("Entries")
    || name.endsWith("Events")
    || name.endsWith("Exports")
    || name.endsWith("History")
    || name.endsWith("Jobs")
    || name.endsWith("Options")
  ) {
    return [];
  }
  if (name.endsWith("ById") || name.endsWith("ByOccurrenceId") || name.endsWith("IdSet")) {
    return new Map();
  }
  if (name.endsWith("Filter")) {
    return { provider: "__all__", search_query: "", sort: "newest", vendor_field: "__all__" };
  }
  if (name.endsWith("Layout")) {
    return { highlight_panel: "overview" };
  }
  if (name.endsWith("Query")) {
    return {
      market_data_provider: "__all__",
      provider_label: "__all__",
      requested_by_tab_id: "__all__",
      scope: "current_focus",
      search_query: "",
      vendor_field: "__all__",
      window_days: 14,
    };
  }
  if (name.endsWith("Count") || name.endsWith("Max")) {
    return 0;
  }
  if (name.endsWith("Error") || name.endsWith("Id")) {
    return null;
  }
  if (name.endsWith("Loading")) {
    return false;
  }
  return undefined;
}

function buildModel(overrides: Record<string, unknown> = {}) {
  const base = {
    ALL_FILTER_VALUE: "__all__",
    PanelDisclosure: TestDisclosure,
    activeMarketInstrument: null,
    autoLinkedMarketInstrumentLink: null,
    focusedMarketWorkflowSummary: null,
    focusedMultiSymbolPrimaryLink: null,
    incidentFocusedInstruments: [],
    marketStatus: null,
    ...overrides,
  };

  return new Proxy(base, {
    get(target, prop) {
      if (typeof prop !== "string") {
        return undefined;
      }
      if (prop in target) {
        return target[prop as keyof typeof target];
      }
      return fallbackModelValue(prop);
    },
  });
}

describe("RuntimeDataIncidentTriagePanel", () => {
  it("renders the unloaded market-data state without throwing", () => {
    render(<RuntimeDataIncidentTriagePanel model={buildModel()} />);

    expect(screen.getByText("Data incident triage")).toBeInTheDocument();
    expect(
      screen.getByText("Load market-data status before reviewing lineage workflow history."),
    ).toBeInTheDocument();
  });

  it("renders a focused market-data workflow without missing model bindings", () => {
    render(
      <RuntimeDataIncidentTriagePanel
        model={buildModel({
          activeMarketInstrument: { sync_status: "synced" },
          filteredFocusedMarketProviderProvenanceEvents: [],
          focusedMarketIncidentHistory: [],
          focusedMarketProviderProvenanceCount: 0,
          focusedMarketWorkflowSummary: {
            failedJobCount: 0,
            focusLabel: "BTC/USDT · 5m",
            incidentHistoryCount: 0,
            ingestionJobCount: 0,
            latestJob: null,
            latestLineage: null,
            lineageCount: 0,
            linkedAlertCount: 0,
            linkedIncidentCount: 0,
            reviewSnapshotCount: 0,
          },
          marketDataIngestionJobs: [],
          marketDataLineageHistory: [],
          marketDataProvenanceExportFilter: {
            provider: "__all__",
            search_query: "",
            sort: "newest",
            vendor_field: "__all__",
          },
          marketDataProvenanceExportHistory: [],
          marketStatus: { instruments: [] },
          providerProvenanceAnalytics: {
            available_filters: {
              market_data_providers: [],
              provider_labels: [],
              requested_by_tab_ids: [],
              vendor_fields: [],
            },
            totals: {
              export_count: 0,
              unique_focus_count: 0,
            },
          },
          sharedProviderProvenanceExports: [],
        })}
      />,
    );

    expect(screen.getByText("BTC/USDT · 5m")).toBeInTheDocument();
    expect(screen.getByText("Provider provenance export")).toBeInTheDocument();
  });
});
