import { useMemo, useRef, useState } from "react";

import type {
  RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload,
} from "../../controlRoomDefinitions";
import {
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys,
  loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState,
} from "./model";
import type {
  RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode,
  RunSurfaceCollectionQueryBuilderReplayLinkShareMode,
} from "./model";

type StatusMessage = {
  message: string;
  tone: "error" | "muted" | "success";
} | null;

export function useQueryBuilderReplayLinkState() {
  const lastHydratedReplayIntentTemplateIdRef = useRef<string | null>(null);
  const [replayIntentUrlTemplateKey, setReplayIntentUrlTemplateKey] = useState<string | null>(
    () => loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl()?.templateKey ?? null,
  );
  const initialReplayLinkGovernanceState = useMemo(
    () => loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState(),
    [],
  );
  const [replayIntentShareMode, setReplayIntentShareMode] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkShareMode>(initialReplayLinkGovernanceState.shareMode);
  const [replayIntentRedactionPolicy, setReplayIntentRedactionPolicy] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy>(initialReplayLinkGovernanceState.redactionPolicy);
  const [replayIntentRetentionPolicy, setReplayIntentRetentionPolicy] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy>(initialReplayLinkGovernanceState.retentionPolicy);
  const [replayIntentGovernanceSyncMode, setReplayIntentGovernanceSyncMode] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode>(initialReplayLinkGovernanceState.syncMode);
  const [replayIntentGovernanceConflicts, setReplayIntentGovernanceConflicts] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry[]>([]);
  const [replayIntentGovernanceReviewedConflictKeys, setReplayIntentGovernanceReviewedConflictKeys] =
    useState<string[]>(
      limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys(
        initialReplayLinkGovernanceState.reviewedConflictKeys,
      ),
    );
  const [replayIntentGovernanceAuditTrail, setReplayIntentGovernanceAuditTrail] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[]>(() =>
      loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(),
    );
  const [replayIntentGovernancePayloadDraft, setReplayIntentGovernancePayloadDraft] = useState("");
  const [replayIntentGovernanceStatus, setReplayIntentGovernanceStatus] = useState<StatusMessage>(null);
  const [replayIntentShareStatus, setReplayIntentShareStatus] = useState<StatusMessage>(null);
  const [replayIntentServerAuditReadToken, setReplayIntentServerAuditReadToken] = useState("");
  const [replayIntentServerAuditWriteToken, setReplayIntentServerAuditWriteToken] = useState("");
  const [replayIntentServerAuditTemplateFilter, setReplayIntentServerAuditTemplateFilter] = useState("");
  const [replayIntentServerAuditAliasFilter, setReplayIntentServerAuditAliasFilter] = useState("");
  const [replayIntentServerAuditActionFilter, setReplayIntentServerAuditActionFilter] =
    useState<"all" | "created" | "resolved" | "revoked">("all");
  const [replayIntentServerAuditRetentionFilter, setReplayIntentServerAuditRetentionFilter] =
    useState<"all" | RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy>("all");
  const [replayIntentServerAuditSourceTabFilter, setReplayIntentServerAuditSourceTabFilter] = useState("");
  const [replayIntentServerAuditSearch, setReplayIntentServerAuditSearch] = useState("");
  const [replayIntentServerAuditLimit, setReplayIntentServerAuditLimit] = useState("25");
  const [replayIntentServerAuditRecordedBefore, setReplayIntentServerAuditRecordedBefore] = useState("");
  const [replayIntentServerAuditIncludeManual, setReplayIntentServerAuditIncludeManual] = useState(false);
  const [replayIntentServerAuditItems, setReplayIntentServerAuditItems] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry[]>([]);
  const [replayIntentServerAuditTotal, setReplayIntentServerAuditTotal] = useState(0);
  const [replayIntentServerAuditStatus, setReplayIntentServerAuditStatus] = useState<StatusMessage>(null);
  const [replayIntentServerAuditLoading, setReplayIntentServerAuditLoading] = useState(false);
  const [replayIntentServerAuditExportJobs, setReplayIntentServerAuditExportJobs] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry[]>([]);
  const [replayIntentServerAuditExportJobTotal, setReplayIntentServerAuditExportJobTotal] = useState(0);
  const [replayIntentServerAuditExportJobStatus, setReplayIntentServerAuditExportJobStatus] =
    useState<StatusMessage>(null);
  const [replayIntentServerAuditExportJobLoading, setReplayIntentServerAuditExportJobLoading] = useState(false);
  const [replayIntentServerAuditExportJobHistory, setReplayIntentServerAuditExportJobHistory] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload | null>(null);
  const [replayIntentLinkAuditTrail, setReplayIntentLinkAuditTrail] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[]>(() =>
      loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(),
    );
  const [replayIntentLinkAliases, setReplayIntentLinkAliases] =
    useState<RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[]>(() =>
      loadRunSurfaceCollectionQueryBuilderReplayLinkAliases(),
    );
  const replayIntentGovernancePreviousStateRef = useRef<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot>({
    redactionPolicy: initialReplayLinkGovernanceState.redactionPolicy,
    retentionPolicy: initialReplayLinkGovernanceState.retentionPolicy,
    shareMode: initialReplayLinkGovernanceState.shareMode,
    syncMode: initialReplayLinkGovernanceState.syncMode,
  });
  const replayIntentGovernancePendingSourceRef =
    useRef<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource | null>(null);
  const lastResolvedServerReplayLinkAliasTokenRef = useRef<string | null>(null);

  return {
    initialReplayLinkGovernanceState,
    lastHydratedReplayIntentTemplateIdRef,
    lastResolvedServerReplayLinkAliasTokenRef,
    replayIntentGovernanceAuditTrail,
    replayIntentGovernanceConflicts,
    replayIntentGovernancePayloadDraft,
    replayIntentGovernancePendingSourceRef,
    replayIntentGovernancePreviousStateRef,
    replayIntentGovernanceReviewedConflictKeys,
    replayIntentGovernanceStatus,
    replayIntentGovernanceSyncMode,
    replayIntentLinkAliases,
    replayIntentLinkAuditTrail,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditExportJobHistory,
    replayIntentServerAuditExportJobLoading,
    replayIntentServerAuditExportJobStatus,
    replayIntentServerAuditExportJobTotal,
    replayIntentServerAuditExportJobs,
    replayIntentServerAuditIncludeManual,
    replayIntentServerAuditItems,
    replayIntentServerAuditLimit,
    replayIntentServerAuditLoading,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditStatus,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditTotal,
    replayIntentServerAuditWriteToken,
    replayIntentShareMode,
    replayIntentShareStatus,
    replayIntentUrlTemplateKey,
    setReplayIntentGovernanceAuditTrail,
    setReplayIntentGovernanceConflicts,
    setReplayIntentGovernancePayloadDraft,
    setReplayIntentGovernanceReviewedConflictKeys,
    setReplayIntentGovernanceStatus,
    setReplayIntentGovernanceSyncMode,
    setReplayIntentLinkAliases,
    setReplayIntentLinkAuditTrail,
    setReplayIntentRedactionPolicy,
    setReplayIntentRetentionPolicy,
    setReplayIntentServerAuditActionFilter,
    setReplayIntentServerAuditAliasFilter,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
    setReplayIntentServerAuditExportJobTotal,
    setReplayIntentServerAuditExportJobs,
    setReplayIntentServerAuditIncludeManual,
    setReplayIntentServerAuditItems,
    setReplayIntentServerAuditLimit,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditReadToken,
    setReplayIntentServerAuditRecordedBefore,
    setReplayIntentServerAuditRetentionFilter,
    setReplayIntentServerAuditSearch,
    setReplayIntentServerAuditSourceTabFilter,
    setReplayIntentServerAuditStatus,
    setReplayIntentServerAuditTemplateFilter,
    setReplayIntentServerAuditTotal,
    setReplayIntentServerAuditWriteToken,
    setReplayIntentShareMode,
    setReplayIntentShareStatus,
    setReplayIntentUrlTemplateKey,
  };
}
