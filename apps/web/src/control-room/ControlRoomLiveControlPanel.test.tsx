import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { ControlRoomLiveControlPanel } from "./ControlRoomLiveControlPanel";

function TestDisclosure({
  children,
  summary,
  title,
}: {
  children: ReactNode;
  summary?: string;
  title: string;
}) {
  return (
    <section>
      <h3>{title}</h3>
      {summary ? <p>{summary}</p> : null}
      {children}
    </section>
  );
}

function buildModel(overrides: Record<string, unknown> = {}) {
  return {
    PanelDisclosure: TestDisclosure,
    activeGuardedLiveAlertIds: [],
    acknowledgeGuardedLiveIncident: vi.fn(),
    engageGuardedLiveKillSwitch: vi.fn(),
    escalateGuardedLiveIncident: vi.fn(),
    formatFixedNumber: (value: number | null | undefined) =>
      value === null || value === undefined ? "n/a" : String(value),
    formatTimestamp: (value: string | null | undefined) => value ?? "n/a",
    guardedLive: {
      active_runtime_alert_count: 0,
      blockers: [],
      candidacy_status: "eligible",
      incident_events: [],
      kill_switch: {
        reason: "none",
        state: "released",
      },
      order_book: {
        open_orders: [],
      },
      ownership: {
        last_order_sync_at: null,
        owner_run_id: null,
        owner_session_id: null,
        state: "idle",
        symbol: null,
      },
      reconciliation: {
        findings: [],
        summary: "No reconciliation findings.",
        venue_snapshot: null,
      },
      session_handoff: {
        state: "idle",
      },
      session_restore: {
        state: "idle",
      },
    },
    guardedLiveReason: "",
    guardedLiveSummary: {
      blockerCount: 0,
      latestReconciliationAt: null,
    },
    recoverGuardedLiveRuntime: vi.fn(),
    releaseGuardedLiveKillSwitch: vi.fn(),
    remediateGuardedLiveIncident: vi.fn(),
    resumeGuardedLiveRun: vi.fn(),
    runGuardedLiveReconciliation: vi.fn(),
    setGuardedLiveReason: vi.fn(),
    ...overrides,
  };
}

describe("ControlRoomLiveControlPanel", () => {
  it("renders core guarded-live controls without provider recovery readbacks", () => {
    render(<ControlRoomLiveControlPanel model={buildModel()} />);

    expect(screen.getByText("Kill switch and reconciliation")).toBeInTheDocument();
    expect(screen.getByText("Run reconciliation")).toBeInTheDocument();
    expect(screen.getByText("Control guardrails")).toBeInTheDocument();
    expect(screen.getByText("Venue state and incidents")).toBeInTheDocument();
    expect(screen.queryByText("Recovered runtime")).not.toBeInTheDocument();
    expect(screen.queryByText("Recovered market channels")).not.toBeInTheDocument();
    expect(screen.queryByText("Provider recovery payload")).not.toBeInTheDocument();
  });
});
