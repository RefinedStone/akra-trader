export type ControlWorkspaceId = "overview" | "research" | "runtime" | "live";

export type ControlWorkspaceDescriptor = {
  id: ControlWorkspaceId;
  kicker: string;
  label: string;
  description: string;
  summary: string;
  sections: string[];
};

export const ControlWorkspaceDescriptor = undefined;

export type ControlStripMetric = {
  label: string;
  value: string;
  detail: string;
  tone?: "research" | "runtime" | "live" | "warning";
};

export const ControlStripMetric = undefined;

type ControlWorkspaceDescriptorInput = {
  alertCount: number;
  backtestsCount: number;
  blockerCount: number;
  instrumentsCount: number;
  killSwitchState: string;
  liveRunsCount: number;
  paperRunsCount: number;
  presetsCount: number;
  referencesCount: number;
  sandboxRunsCount: number;
  strategiesCount: number;
  totalTrackedRunCount: number;
};

const WORKSPACE_PATHS: Record<ControlWorkspaceId, string> = {
  overview: "/",
  research: "/research",
  runtime: "/runtime-ops",
  live: "/guarded-live",
};

export function buildControlWorkspaceDescriptors(
  input: ControlWorkspaceDescriptorInput,
): ControlWorkspaceDescriptor[] {
  return [
    {
      id: "overview",
      kicker: "운영 현황",
      label: "Overview",
      description:
        "전체 상태를 먼저 확인한 뒤 필요한 workspace로 이동합니다. 판단에 필요한 지표만 짧게 보여줍니다.",
      summary: `Run ${input.totalTrackedRunCount}개 · Strategy ${input.strategiesCount}개 · 활성 alert ${input.alertCount}개`,
      sections: ["운영 상태", "Workspace 이동", "Catalog 상태"],
    },
    {
      id: "research",
      kicker: "Backtest와 Preset",
      label: "Research",
      description:
        "실험 설계, Preset 관리, reference 검토, benchmark 비교를 운영 소음 없이 처리합니다.",
      summary: `Backtest ${input.backtestsCount}개 · Preset ${input.presetsCount}개 · reference ${input.referencesCount}개`,
      sections: ["Run 실행", "Scenario Preset", "외부 reference", "최근 Backtest"],
    },
    {
      id: "runtime",
      kicker: "Sandbox와 Paper",
      label: "Runtime Ops",
      description:
        "데이터 최신성, Sandbox/Paper 실행, 운영 alert를 한 workspace에서 확인합니다.",
      summary: `Sandbox ${input.sandboxRunsCount}개 · Paper ${input.paperRunsCount}개 · instrument ${input.instrumentsCount}개`,
      sections: [
        "Sandbox worker 시작",
        "Market data 상태",
        "Runtime alert와 audit",
        "Sandbox Run",
        "Paper Run",
      ],
    },
    {
      id: "live",
      kicker: "Guarded 실행",
      label: "Guarded Live",
      description:
        "Live ownership, reconciliation, recovery, 수동 주문 개입만 다룹니다. 실험성 작업은 분리합니다.",
      summary: `Kill switch ${input.killSwitchState} · blocker ${input.blockerCount}개 · Live Run ${input.liveRunsCount}개`,
      sections: ["Live worker 시작", "Kill switch와 reconciliation", "Guarded Live Run"],
    },
  ];
}

export function workspacePath(workspace: ControlWorkspaceId) {
  return WORKSPACE_PATHS[workspace];
}

export function workspaceFromPathname(pathname: string): ControlWorkspaceId {
  const normalized = pathname.replace(/\/+$/, "") || "/";
  if (normalized === "/research") {
    return "research";
  }
  if (normalized === "/runtime-ops") {
    return "runtime";
  }
  if (normalized === "/guarded-live") {
    return "live";
  }
  return "overview";
}

// Runtime placeholders for generated barrel compatibility.
export const ControlWorkspaceId = undefined;
