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
        summary: "거래소 확인 결과가 없습니다.",
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

    expect(screen.getByText("중지 스위치와 거래소 확인")).toBeInTheDocument();
    expect(screen.getAllByText("거래소 확인").length).toBeGreaterThan(0);
    expect(screen.getByText("실전 안전장치")).toBeInTheDocument();
    expect(screen.getByText("거래소 상태와 사고")).toBeInTheDocument();
    expect(screen.getByText("실전 가능")).toBeInTheDocument();
    expect(screen.getAllByText("해제됨").length).toBeGreaterThan(0);
    expect(screen.getAllByText("대기 중").length).toBeGreaterThan(0);
    expect(screen.queryByText("eligible")).not.toBeInTheDocument();
    expect(screen.queryByText("released")).not.toBeInTheDocument();
    expect(screen.queryByText("Recovered runtime")).not.toBeInTheDocument();
    expect(screen.queryByText("Recovered market channels")).not.toBeInTheDocument();
    expect(screen.queryByText("Provider recovery payload")).not.toBeInTheDocument();
  });
});
