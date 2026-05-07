import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { RuntimeOperatorPanel } from "./RuntimeOperatorPanel";

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
  if (name.startsWith("build")) {
    return (value: unknown) => JSON.stringify(value ?? "none");
  }
  if (name.startsWith("format") || name.startsWith("summarize")) {
    return (value: unknown) => String(value ?? "n/a");
  }
  if (name.startsWith("get")) {
    return (value: unknown) => String(value ?? "n/a");
  }
  if (name.startsWith("is")) {
    return () => false;
  }
  if (
    name.startsWith("acknowledge")
    || name.startsWith("apply")
    || name.startsWith("approve")
    || name.startsWith("copy")
    || name.startsWith("clear")
    || name.startsWith("delete")
    || name.startsWith("download")
    || name.startsWith("edit")
    || name.startsWith("escalate")
    || name.startsWith("focus")
    || name.startsWith("handle")
    || name.startsWith("load")
    || name.startsWith("moderate")
    || name.startsWith("normalize")
    || name.startsWith("open")
    || name.startsWith("recover")
    || name.startsWith("remove")
    || name.startsWith("reset")
    || name.startsWith("resolve")
    || name.startsWith("restore")
    || name.startsWith("rollback")
    || name.startsWith("run")
    || name.startsWith("save")
    || name.startsWith("set")
    || name.startsWith("share")
    || name.startsWith("stage")
    || name.startsWith("submit")
    || name.startsWith("toggle")
    || name.startsWith("trigger")
    || name.startsWith("update")
  ) {
    return vi.fn();
  }
  if (
    name.endsWith("Alerts")
    || name.endsWith("Audits")
    || name.endsWith("Catalogs")
    || name.endsWith("Clusters")
    || name.endsWith("Entries")
    || name.endsWith("Events")
    || name.endsWith("Exports")
    || name.endsWith("Fields")
    || name.endsWith("History")
    || name.endsWith("Items")
    || name.endsWith("Jobs")
    || name.endsWith("Options")
    || name.endsWith("Plans")
    || name.endsWith("Presets")
    || name.endsWith("Registries")
    || name.endsWith("Reports")
    || name.endsWith("Templates")
    || name.endsWith("Views")
  ) {
    return [];
  }
  if (name.endsWith("ById") || name.endsWith("ByOccurrenceId") || name.endsWith("IdSet")) {
    return new Map();
  }
  if (name.endsWith("Draft")) {
    return {};
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
  if (name.endsWith("QueueSummary") || name.endsWith("Summary")) {
    return {};
  }
  if (name.endsWith("Count") || name.endsWith("Max") || name.endsWith("Offset")) {
    return 0;
  }
  if (name.endsWith("Error") || name.endsWith("Feedback") || name.endsWith("Id")) {
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
    linkedOperatorAlertById: new Map(),
    linkedOperatorIncidentEventById: new Map(),
    marketStatus: null,
    operatorSummary: {
      alertCount: 0,
      criticalCount: 0,
      deliveryCount: 0,
      historyCount: 0,
      incidentCount: 0,
      latestAuditAt: null,
      warningCount: 0,
    },
    operatorVisibility: {
      alert_history: [],
      alerts: [],
      audit_events: [],
      delivery_history: [],
      incident_events: [],
    },
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

describe("RuntimeOperatorPanel", () => {
  it("renders the operator trust panel without missing model bindings", () => {
    render(<RuntimeOperatorPanel model={buildModel()} />);

    expect(screen.getByText("Runtime alerts and audit")).toBeInTheDocument();
    expect(screen.getByText("No active runtime alerts.")).toBeInTheDocument();
    expect(screen.queryByText("Start export workflow")).not.toBeInTheDocument();
    expect(screen.queryByText("Escalate snapshot")).not.toBeInTheDocument();
  });
});
