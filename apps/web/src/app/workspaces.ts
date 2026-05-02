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
      kicker: "Mission control",
      label: "Overview",
      description:
        "Start here to assess control posture, then move into the lane that needs action. This surface stays intentionally short and decision-oriented.",
      summary: `${input.totalTrackedRunCount} tracked runs · ${input.strategiesCount} strategies · ${input.alertCount} active alerts`,
      sections: ["Control posture", "Workspace routing", "Catalog health"],
    },
    {
      id: "research",
      kicker: "Backtests and presets",
      label: "Research",
      description:
        "Use this lane for experiment design, preset management, reference review, and benchmark comparison without runtime noise.",
      summary: `${input.backtestsCount} backtests · ${input.presetsCount} presets · ${input.referencesCount} references`,
      sections: ["Launch a run", "Scenario presets", "Third-party references", "Recent backtests"],
    },
    {
      id: "runtime",
      kicker: "Sandbox and paper",
      label: "Runtime Ops",
      description:
        "Monitor data freshness, sandbox and paper execution, and operator incident pressure in one operational workspace.",
      summary: `${input.sandboxRunsCount} sandbox · ${input.paperRunsCount} paper · ${input.instrumentsCount} instruments`,
      sections: [
        "Start sandbox worker",
        "Market data status",
        "Runtime alerts and audit",
        "Sandbox runs",
        "Paper runs",
      ],
    },
    {
      id: "live",
      kicker: "Guarded execution",
      label: "Guarded Live",
      description:
        "Reserve this workspace for live ownership, reconciliation, recovery, and manual order intervention. Nothing exploratory belongs here.",
      summary: `Kill switch ${input.killSwitchState} · ${input.blockerCount} blockers · ${input.liveRunsCount} live runs`,
      sections: ["Start live worker", "Kill switch and reconciliation", "Guarded live runs"],
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
