export type ControlWorkspaceId = "overview" | "research" | "markets" | "runtime" | "live";

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
  sandboxRunsCount: number;
  strategiesCount: number;
  totalTrackedRunCount: number;
};

const WORKSPACE_PATHS: Record<ControlWorkspaceId, string> = {
  overview: "/",
  research: "/research",
  markets: "/markets",
  runtime: "/runtime-ops",
  live: "/guarded-live",
};

export function buildControlWorkspaceDescriptors(
  input: ControlWorkspaceDescriptorInput,
): ControlWorkspaceDescriptor[] {
  return [
    {
      id: "overview",
      kicker: "퀀트 운용 개요",
      label: "대시보드",
      description:
        "전략 실험, 시장 데이터, 실행 상태, 위험 알림을 먼저 훑어본 뒤 필요한 화면으로 이동합니다.",
      summary: `실행 ${input.totalTrackedRunCount}개 · 전략 ${input.strategiesCount}개 · 활성 알림 ${input.alertCount}개`,
      sections: ["운용 상태", "전략 현황", "위험 알림"],
    },
    {
      id: "research",
      kicker: "전략 검증",
      label: "백테스트",
      description:
        "주식·코인 전략의 설정, 시나리오, 실행 결과를 한곳에서 검증합니다.",
      summary: `백테스트 ${input.backtestsCount}개 · 시나리오 ${input.presetsCount}개 · 전략 ${input.strategiesCount}개`,
      sections: ["백테스트 실행", "시나리오", "전략", "최근 결과"],
    },
    {
      id: "markets",
      kicker: "시장 데이터",
      label: "시세·캔들",
      description:
        "거래소에서 수집한 가격봉과 종목별 수집 상태, 비어 있는 데이터를 차트로 확인합니다.",
      summary: `종목 ${input.instrumentsCount}개 · 가격봉 수집`,
      sections: ["가격봉 차트", "종목 전환", "수집 상태", "최근 가격봉"],
    },
    {
      id: "runtime",
      kicker: "모의 실행",
      label: "모의 실행",
      description:
        "실제 주문을 내기 전에 전략 실행, 데이터 최신성, 운용 알림을 함께 점검합니다.",
      summary: `테스트 실행 ${input.sandboxRunsCount}개 · 모의 주문 ${input.paperRunsCount}개 · 종목 ${input.instrumentsCount}개`,
      sections: [
        "테스트 실행",
        "시장 데이터 상태",
        "운용 알림과 기록",
        "테스트 실행 이력",
        "모의 주문 이력",
      ],
    },
    {
      id: "live",
      kicker: "실전 관리",
      label: "실전 관리",
      description:
        "실전 주문은 실행 주체, 거래소 확인, 상태 복원, 긴급 중지가 확인된 상태에서만 다룹니다.",
      summary: `긴급 중지 ${input.killSwitchState} · 차단 요인 ${input.blockerCount}개 · 실전 실행 ${input.liveRunsCount}개`,
      sections: ["실전 실행", "긴급 중지와 거래소 확인", "실전 이력"],
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
  if (normalized === "/markets") {
    return "markets";
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
