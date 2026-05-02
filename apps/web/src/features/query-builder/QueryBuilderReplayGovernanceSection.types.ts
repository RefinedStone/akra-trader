import type {
  PredicateRefReplayApplyHistoryTabIdentity,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkShareMode,
} from "./model";
import type {
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload,
} from "../../controlRoomDefinitions";

type QueryBuilderStatusTone = "error" | "muted" | "success";

export type QueryBuilderReplayGovernanceSectionProps = {
  governance: {
    currentReplayIntentGovernancePayloadValue: string | null;
    currentReplayIntentGovernanceSnapshot: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
    predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
    redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue: string | null;
    replayIntentGovernanceAuditTrail: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[];
    replayIntentGovernanceConflicts: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry[];
    replayIntentGovernancePayloadDraft: string;
    replayIntentGovernanceStatus: { message: string; tone: QueryBuilderStatusTone } | null;
    replayIntentGovernanceSyncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
    replayIntentRedactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    replayIntentRetentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    replayIntentShareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
    replayIntentShareStatus: { message: string; tone: QueryBuilderStatusTone } | null;
    visibleReplayIntentLinkAliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[];
    visibleReplayIntentLinkAuditTrail: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[];
  };
  serverAudit: {
    replayIntentServerAuditActionFilter: "all" | "created" | "resolved" | "revoked";
    replayIntentServerAuditAliasFilter: string;
    replayIntentServerAuditExportJobHistory: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload | null;
    replayIntentServerAuditExportJobLoading: boolean;
    replayIntentServerAuditExportJobStatus: { message: string; tone: QueryBuilderStatusTone } | null;
    replayIntentServerAuditExportJobTotal: number;
    replayIntentServerAuditExportJobs: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry[];
    replayIntentServerAuditIncludeManual: boolean;
    replayIntentServerAuditItems: RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry[];
    replayIntentServerAuditLimit: string;
    replayIntentServerAuditLoading: boolean;
    replayIntentServerAuditReadToken: string;
    replayIntentServerAuditRecordedBefore: string;
    replayIntentServerAuditRetentionFilter: "all" | RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    replayIntentServerAuditSearch: string;
    replayIntentServerAuditSourceTabFilter: string;
    replayIntentServerAuditStatus: { message: string; tone: QueryBuilderStatusTone } | null;
    replayIntentServerAuditTemplateFilter: string;
    replayIntentServerAuditTotal: number;
    replayIntentServerAuditWriteToken: string;
  };
  callbacks: {
    appendReplayIntentGovernanceAuditEntry: (
      entry: Omit<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, "id">,
    ) => void;
    applyReplayIntentGovernanceSnapshot: (
      snapshot: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
      options: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
    ) => void;
    applyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload: () => void;
    copyRunSurfaceCollectionQueryBuilderReplayIntentLink: () => void | Promise<void>;
    copyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload: () => void | Promise<void>;
    createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord: (format: "json" | "csv") => void | Promise<void>;
    dismissReplayIntentGovernanceConflict: (conflictKey: string) => void;
    downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord: (jobId: string) => void | Promise<void>;
    exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords: (format: "json" | "csv") => void | Promise<void>;
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory: (jobId: string) => void | Promise<void>;
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs: () => void | Promise<void>;
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits: () => void | Promise<void>;
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords: (mode: "expired" | "matched") => void | Promise<void>;
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords: (mode: "expired" | "matched") => void | Promise<void>;
    revokeRunSurfaceCollectionQueryBuilderReplayIntentAlias: (entry: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry) => void | Promise<void>;
    setReplayIntentGovernanceAuditTrail: (entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[]) => void;
    setReplayIntentGovernancePayloadDraft: (value: string) => void;
    setReplayIntentGovernanceStatus: (value: { message: string; tone: QueryBuilderStatusTone } | null) => void;
    setReplayIntentGovernanceSyncMode: (value: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode) => void;
    setReplayIntentLinkAliases: (entries: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[]) => void;
    setReplayIntentLinkAuditTrail: (entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[]) => void;
    setReplayIntentRedactionPolicy: (value: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy) => void;
    setReplayIntentRetentionPolicy: (value: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy) => void;
    setReplayIntentServerAuditActionFilter: (value: "all" | "created" | "resolved" | "revoked") => void;
    setReplayIntentServerAuditAliasFilter: (value: string) => void;
    setReplayIntentServerAuditIncludeManual: (value: boolean) => void;
    setReplayIntentServerAuditLimit: (value: string) => void;
    setReplayIntentServerAuditReadToken: (value: string) => void;
    setReplayIntentServerAuditRecordedBefore: (value: string) => void;
    setReplayIntentServerAuditRetentionFilter: (value: "all" | RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy) => void;
    setReplayIntentServerAuditSearch: (value: string) => void;
    setReplayIntentServerAuditSourceTabFilter: (value: string) => void;
    setReplayIntentServerAuditTemplateFilter: (value: string) => void;
    setReplayIntentServerAuditWriteToken: (value: string) => void;
    setReplayIntentShareMode: (value: RunSurfaceCollectionQueryBuilderReplayLinkShareMode) => void;
    setReplayIntentShareStatus: (value: { message: string; tone: QueryBuilderStatusTone } | null) => void;
    shareRunSurfaceCollectionQueryBuilderReplayIntentLink: () => void | Promise<void>;
  };
  helpers: {
    buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken: (aliasId: string, signature: string) => string;
    formatRelativeTimestampLabel: (value?: string | null) => string;
    formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue: (
      fieldKey: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey,
      state: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
    ) => string;
    getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys: (
      fromState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
      toState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
    ) => RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey[];
  };
};

// Runtime placeholders for generated barrel compatibility.
export const QueryBuilderReplayGovernanceSectionProps = undefined;
