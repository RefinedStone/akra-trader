import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkspaceShell } from "./WorkspaceShell";
import type { ControlWorkspaceDescriptor } from "./workspaces";

const workspaceDescriptors: ControlWorkspaceDescriptor[] = [
  {
    id: "overview",
    kicker: "퀀트 운용 개요",
    label: "대시보드",
    description: "운영 상태를 먼저 점검합니다.",
    summary: "실행 2개 · 전략 1개 · 활성 알림 0개",
    sections: ["운용 상태", "전략 현황", "위험 알림"],
  },
  {
    id: "research",
    kicker: "전략 검증",
    label: "백테스트",
    description: "전략 실행 결과를 검증합니다.",
    summary: "백테스트 2개 · 프리셋 1개",
    sections: ["백테스트 실행", "시나리오 프리셋", "최근 결과"],
  },
];

describe("WorkspaceShell", () => {
  it("renders operational context instead of static asset category chips", () => {
    const onNavigate = vi.fn();
    const onRefresh = vi.fn();

    render(
      <WorkspaceShell
        activeWorkspace="overview"
        activeWorkspaceDescriptor={workspaceDescriptors[0]}
        apiBase="/api"
        controlStripMetrics={[
          {
            label: "실행 상태",
            value: "2",
            detail: "전체 추적 실행",
            tone: "research",
          },
          {
            label: "차단 요인",
            value: "0",
            detail: "실전 보호 상태",
            tone: "warning",
          },
        ]}
        onNavigate={onNavigate}
        onRefresh={onRefresh}
        statusText="ready"
        workspaceDescriptors={workspaceDescriptors}
      >
        <div>workspace content</div>
      </WorkspaceShell>,
    );

    expect(screen.getByRole("heading", { name: "전략 검증부터 실전 보호까지 한 화면에서 판단합니다" })).toBeInTheDocument();
    expect(screen.getByLabelText("운영 핵심 지표")).toHaveTextContent("실행 상태");
    expect(screen.getByLabelText("현재 작업면 점검 항목")).toHaveTextContent("운용 상태");
    expect(screen.queryByText("Equity")).not.toBeInTheDocument();
    expect(screen.queryByText("Crypto")).not.toBeInTheDocument();
    expect(screen.queryByText("Backtest")).not.toBeInTheDocument();
    expect(screen.queryByText("Risk")).not.toBeInTheDocument();

    fireEvent.click(screen.getAllByRole("button", { name: /백테스트/ })[0]);
    expect(onNavigate).toHaveBeenCalledWith("research");
  });
});
