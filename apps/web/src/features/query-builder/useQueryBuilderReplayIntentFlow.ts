import { useCallback, useEffect, useMemo } from "react";

import {
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
} from "../../controlRoomApi";
import {
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
} from "../../controlRoomDefinitions";
import type {
  RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
} from "../../controlRoomDefinitions";
import { formatRelativeTimestampLabel } from "../comparisonTooltipFormatters";
import type { QueryBuilderReplayGovernanceSectionProps } from "./QueryBuilderReplayGovernanceSection";
import {
  applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy,
  areRunSurfaceCollectionQueryBuilderReplayIntentsEqual,
  areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual,
  buildRunSurfaceCollectionQueryBuilderReplayIntentUrl,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken,
  buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue,
  encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl,
  formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue,
  getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys,
  isDefaultRunSurfaceCollectionQueryBuilderReplayIntent,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState,
  persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail,
  pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail,
  readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
} from "./model";
import type {
  PredicateRefReplayApplyHistoryTabIdentity,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
} from "./model";
import { useQueryBuilderReplayLinkState } from "./useQueryBuilderReplayLinkState";

type UseQueryBuilderReplayIntentFlowArgs = {
  bundleCoordinationSimulationReplayActionTypeFilter:
    RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayActionTypeFilter"];
  bundleCoordinationSimulationReplayEdgeFilter:
    RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayEdgeFilter"];
  bundleCoordinationSimulationReplayGroupFilter:
    RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayGroupFilter"];
  bundleCoordinationSimulationReplayIndex: number;
  bundleCoordinationSimulationScope: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayScope"];
  clauseReevaluationPreviewSelection: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["previewSelection"];
  predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  setBundleCoordinationSimulationReplayActionTypeFilter: (
    value: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayActionTypeFilter"],
  ) => void;
  setBundleCoordinationSimulationReplayEdgeFilter: (
    value: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayEdgeFilter"],
  ) => void;
  setBundleCoordinationSimulationReplayGroupFilter: (
    value: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayGroupFilter"],
  ) => void;
  setBundleCoordinationSimulationReplayIndex: (value: number) => void;
  setBundleCoordinationSimulationScope: (
    value: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayScope"],
  ) => void;
  setClauseReevaluationPreviewSelection: (
    value: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["previewSelection"],
  ) => void;
  setPredicateRefDraftKey: (value: string) => void;
};

type UseQueryBuilderReplayIntentFlowResult = {
  applyRunSurfaceCollectionQueryBuilderReplayIntent: (
    intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
  ) => void;
  currentRunSurfaceCollectionQueryBuilderReplayIntent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  lastHydratedReplayIntentTemplateIdRef: ReturnType<
    typeof useQueryBuilderReplayLinkState
  >["lastHydratedReplayIntentTemplateIdRef"];
  replayGovernanceSectionProps: QueryBuilderReplayGovernanceSectionProps;
  replayIntentUrlTemplateKey: string | null;
  setReplayIntentUrlTemplateKey: ReturnType<
    typeof useQueryBuilderReplayLinkState
  >["setReplayIntentUrlTemplateKey"];
};

function downloadTextPayload(content: string, contentType: string, filename: string) {
  if (typeof window === "undefined") {
    return;
  }
  const blob = new Blob([content], { type: contentType });
  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(objectUrl);
}

export function useQueryBuilderReplayIntentFlow({
  bundleCoordinationSimulationReplayActionTypeFilter,
  bundleCoordinationSimulationReplayEdgeFilter,
  bundleCoordinationSimulationReplayGroupFilter,
  bundleCoordinationSimulationReplayIndex,
  bundleCoordinationSimulationScope,
  clauseReevaluationPreviewSelection,
  predicateRefReplayApplyHistoryTabIdentity,
  selectedRefTemplate,
  setBundleCoordinationSimulationReplayActionTypeFilter,
  setBundleCoordinationSimulationReplayEdgeFilter,
  setBundleCoordinationSimulationReplayGroupFilter,
  setBundleCoordinationSimulationReplayIndex,
  setBundleCoordinationSimulationScope,
  setClauseReevaluationPreviewSelection,
  setPredicateRefDraftKey,
}: UseQueryBuilderReplayIntentFlowArgs): UseQueryBuilderReplayIntentFlowResult {
  const {
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
  } = useQueryBuilderReplayLinkState();

  const currentRunSurfaceCollectionQueryBuilderReplayIntent =
    useMemo<RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>(
      () => ({
        previewSelection: clauseReevaluationPreviewSelection,
        replayActionTypeFilter: bundleCoordinationSimulationReplayActionTypeFilter,
        replayEdgeFilter: bundleCoordinationSimulationReplayEdgeFilter,
        replayGroupFilter: bundleCoordinationSimulationReplayGroupFilter,
        replayIndex: bundleCoordinationSimulationReplayIndex,
        replayScope: bundleCoordinationSimulationScope,
      }),
      [
        bundleCoordinationSimulationReplayActionTypeFilter,
        bundleCoordinationSimulationReplayEdgeFilter,
        bundleCoordinationSimulationReplayGroupFilter,
        bundleCoordinationSimulationReplayIndex,
        bundleCoordinationSimulationScope,
        clauseReevaluationPreviewSelection,
      ],
    );
  const currentRunSurfaceCollectionQueryBuilderReplayIntentCompactValue = useMemo(
    () => (
      selectedRefTemplate?.key
        ? encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
            selectedRefTemplate.key,
            currentRunSurfaceCollectionQueryBuilderReplayIntent,
          )
        : null
    ),
    [currentRunSurfaceCollectionQueryBuilderReplayIntent, selectedRefTemplate?.key],
  );
  const redactedRunSurfaceCollectionQueryBuilderReplayIntent = useMemo(
    () => applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy(
      currentRunSurfaceCollectionQueryBuilderReplayIntent,
      replayIntentRedactionPolicy,
    ),
    [
      currentRunSurfaceCollectionQueryBuilderReplayIntent,
      replayIntentRedactionPolicy,
    ],
  );
  const redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue = useMemo(
    () => (
      selectedRefTemplate?.key
        ? encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
            selectedRefTemplate.key,
            redactedRunSurfaceCollectionQueryBuilderReplayIntent,
          )
        : null
    ),
    [redactedRunSurfaceCollectionQueryBuilderReplayIntent, selectedRefTemplate?.key],
  );
  const currentRunSurfaceCollectionQueryBuilderReplayIntentLink = useMemo(() => {
    if (typeof window === "undefined") {
      return "";
    }
    return new URL(
      buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
        selectedRefTemplate?.key ?? replayIntentUrlTemplateKey,
        currentRunSurfaceCollectionQueryBuilderReplayIntent,
        window.location.href,
      ),
      window.location.origin,
    ).toString();
  }, [
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    replayIntentUrlTemplateKey,
    selectedRefTemplate?.key,
  ]);
  const visibleReplayIntentLinkAuditTrail = useMemo(
    () => (
      selectedRefTemplate?.key
        ? replayIntentLinkAuditTrail.filter((entry) => entry.templateKey === selectedRefTemplate.key)
        : replayIntentLinkAuditTrail
    ),
    [replayIntentLinkAuditTrail, selectedRefTemplate?.key],
  );
  const visibleReplayIntentLinkAliases = useMemo(
    () => (
      selectedRefTemplate?.key
        ? replayIntentLinkAliases.filter((entry) => entry.templateKey === selectedRefTemplate.key)
        : replayIntentLinkAliases
    ),
    [replayIntentLinkAliases, selectedRefTemplate?.key],
  );

  useEffect(() => {
    if (!selectedRefTemplate?.key) {
      return;
    }
    setReplayIntentServerAuditTemplateFilter((current) =>
      current.trim() ? current : selectedRefTemplate.key,
    );
  }, [selectedRefTemplate?.key, setReplayIntentServerAuditTemplateFilter]);

  const currentReplayIntentGovernanceSnapshot = useMemo(
    () => buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot({
      redactionPolicy: replayIntentRedactionPolicy,
      retentionPolicy: replayIntentRetentionPolicy,
      shareMode: replayIntentShareMode,
      syncMode: replayIntentGovernanceSyncMode,
    }),
    [
      replayIntentGovernanceSyncMode,
      replayIntentRedactionPolicy,
      replayIntentRetentionPolicy,
      replayIntentShareMode,
    ],
  );
  const currentReplayIntentGovernancePayloadValue = useMemo(
    () => encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload({
      exportedAt: new Date().toISOString(),
      governance: currentReplayIntentGovernanceSnapshot,
      sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
      sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
    }),
    [
      currentReplayIntentGovernanceSnapshot,
      predicateRefReplayApplyHistoryTabIdentity.label,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
    ],
  );
  const appendReplayIntentGovernanceAuditEntry = useCallback(
    (
      entry: Omit<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry, "id">,
    ) => {
      setReplayIntentGovernanceAuditTrail((current) =>
        mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(current, [{
          ...entry,
          id: buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId(),
        }]),
      );
    },
    [setReplayIntentGovernanceAuditTrail],
  );
  const applyReplayIntentGovernanceSnapshot = useCallback(
    (
      nextState: QueryBuilderReplayGovernanceSectionProps["governance"]["currentReplayIntentGovernanceSnapshot"],
      source: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
    ) => {
      replayIntentGovernancePendingSourceRef.current = source;
      setReplayIntentShareMode(nextState.shareMode);
      setReplayIntentRedactionPolicy(nextState.redactionPolicy);
      setReplayIntentRetentionPolicy(nextState.retentionPolicy);
      setReplayIntentGovernanceSyncMode(nextState.syncMode);
    },
    [
      replayIntentGovernancePendingSourceRef,
      setReplayIntentGovernanceSyncMode,
      setReplayIntentRedactionPolicy,
      setReplayIntentRetentionPolicy,
      setReplayIntentShareMode,
    ],
  );
  const dismissReplayIntentGovernanceConflict = useCallback(
    (conflictKey: string, options?: { rememberResolution?: boolean }) => {
      setReplayIntentGovernanceConflicts((current) =>
        current.filter((entry) => entry.conflictKey !== conflictKey),
      );
      if (options?.rememberResolution !== false) {
        setReplayIntentGovernanceReviewedConflictKeys((current) =>
          limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys([
            conflictKey,
            ...current,
          ]),
        );
      }
    },
    [
      setReplayIntentGovernanceConflicts,
      setReplayIntentGovernanceReviewedConflictKeys,
    ],
  );
  const handleIncomingReplayIntentGovernanceSyncState = useCallback(
    (
      remoteGovernance: ReturnType<
        typeof readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState
      > | null,
      options?: { source?: "bootstrap" | "storage" },
    ) => {
      if (!remoteGovernance || remoteGovernance.sourceTabId === predicateRefReplayApplyHistoryTabIdentity.tabId) {
        return;
      }
      const conflictKey = buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey(remoteGovernance);
      const remoteGovernanceSnapshot = buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot({
        redactionPolicy: remoteGovernance.redactionPolicy,
        retentionPolicy: remoteGovernance.retentionPolicy,
        shareMode: remoteGovernance.shareMode,
        syncMode: replayIntentGovernanceSyncMode,
      });
      if (areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual(
        {
          redactionPolicy: replayIntentRedactionPolicy,
          retentionPolicy: replayIntentRetentionPolicy,
          shareMode: replayIntentShareMode,
        },
        remoteGovernance,
      )) {
        setReplayIntentGovernanceConflicts((current) =>
          current.filter((entry) => entry.conflictKey !== conflictKey),
        );
        return;
      }
      if (replayIntentGovernanceSyncMode === "opt_out") {
        appendReplayIntentGovernanceAuditEntry({
          at: new Date().toISOString(),
          detail: `${remoteGovernance.sourceTabLabel} changed replay link governance, but this tab ignored the remote update.`,
          diffKeys: getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
            currentReplayIntentGovernanceSnapshot,
            remoteGovernanceSnapshot,
          ),
          fromState: currentReplayIntentGovernanceSnapshot,
          kind: "remote_ignored",
          remoteSourceTabId: remoteGovernance.sourceTabId,
          remoteSourceTabLabel: remoteGovernance.sourceTabLabel,
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          toState: remoteGovernanceSnapshot,
        });
        setReplayIntentShareStatus({
          message: `${remoteGovernance.sourceTabLabel} changed replay link governance, but this tab is set to ignore remote sync.`,
          tone: "muted",
        });
        return;
      }
      if (replayIntentGovernanceSyncMode === "review") {
        if (replayIntentGovernanceReviewedConflictKeys.includes(conflictKey)) {
          return;
        }
        if (!replayIntentGovernanceConflicts.some((entry) => entry.conflictKey === conflictKey)) {
          appendReplayIntentGovernanceAuditEntry({
            at: new Date().toISOString(),
            detail: `${remoteGovernance.sourceTabLabel} changed replay link governance and queued a review in this tab.`,
            diffKeys: getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
              currentReplayIntentGovernanceSnapshot,
              remoteGovernanceSnapshot,
            ),
            fromState: currentReplayIntentGovernanceSnapshot,
            kind: "conflict_detected",
            remoteSourceTabId: remoteGovernance.sourceTabId,
            remoteSourceTabLabel: remoteGovernance.sourceTabLabel,
            sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
            sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
            toState: remoteGovernanceSnapshot,
          });
        }
        setReplayIntentGovernanceConflicts((current) => {
          const nextByKey = new Map(
            current.map((entry) => [entry.conflictKey, entry] as const),
          );
          nextByKey.set(conflictKey, {
            conflictKey,
            detectedAt: new Date().toISOString(),
            localRedactionPolicy: replayIntentRedactionPolicy,
            localRetentionPolicy: replayIntentRetentionPolicy,
            localShareMode: replayIntentShareMode,
            remoteRedactionPolicy: remoteGovernance.redactionPolicy,
            remoteRetentionPolicy: remoteGovernance.retentionPolicy,
            remoteShareMode: remoteGovernance.shareMode,
            sourceTabId: remoteGovernance.sourceTabId,
            sourceTabLabel: remoteGovernance.sourceTabLabel,
            updatedAt: remoteGovernance.updatedAt,
          });
          return limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts(
            Array.from(nextByKey.values()).sort((left, right) => right.detectedAt.localeCompare(left.detectedAt)),
          );
        });
        setReplayIntentShareStatus({
          message:
            options?.source === "bootstrap"
              ? `${remoteGovernance.sourceTabLabel} has a pending replay link governance change waiting for review in this tab.`
              : `${remoteGovernance.sourceTabLabel} updated replay link governance. Review the pending change before applying it here.`,
          tone: "muted",
        });
        return;
      }
      setReplayIntentGovernanceConflicts((current) =>
        current.filter((entry) => entry.conflictKey !== conflictKey),
      );
      applyReplayIntentGovernanceSnapshot(remoteGovernanceSnapshot, {
        detail: `${remoteGovernance.sourceTabLabel} synced replay link governance into this tab.`,
        kind: "remote_sync",
        remoteSourceTabId: remoteGovernance.sourceTabId,
        remoteSourceTabLabel: remoteGovernance.sourceTabLabel,
      });
      setReplayIntentShareStatus({
        message: `${remoteGovernance.sourceTabLabel} synced replay link governance to ${remoteGovernance.shareMode} / ${remoteGovernance.redactionPolicy.replaceAll("_", " ")}.`,
        tone: "muted",
      });
    },
    [
      appendReplayIntentGovernanceAuditEntry,
      applyReplayIntentGovernanceSnapshot,
      currentReplayIntentGovernanceSnapshot,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      predicateRefReplayApplyHistoryTabIdentity.label,
      replayIntentGovernanceConflicts,
      replayIntentGovernanceReviewedConflictKeys,
      replayIntentGovernanceSyncMode,
      replayIntentRedactionPolicy,
      replayIntentRetentionPolicy,
      replayIntentShareMode,
      setReplayIntentGovernanceConflicts,
      setReplayIntentShareStatus,
    ],
  );

  useEffect(() => {
    setReplayIntentShareStatus(null);
  }, [currentRunSurfaceCollectionQueryBuilderReplayIntentLink, setReplayIntentShareStatus]);
  useEffect(() => {
    const previous = replayIntentGovernancePreviousStateRef.current;
    const next = currentReplayIntentGovernanceSnapshot;
    const diffKeys = getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(previous, next);
    if (!diffKeys.length) {
      return;
    }
    const source = replayIntentGovernancePendingSourceRef.current;
    replayIntentGovernancePendingSourceRef.current = null;
    appendReplayIntentGovernanceAuditEntry({
      at: new Date().toISOString(),
      detail:
        source?.detail
        ?? `${predicateRefReplayApplyHistoryTabIdentity.label} updated replay link governance in this tab.`,
      diffKeys,
      fromState: previous,
      kind: source?.kind ?? "local_change",
      remoteSourceTabId: source?.remoteSourceTabId ?? null,
      remoteSourceTabLabel: source?.remoteSourceTabLabel ?? null,
      sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
      sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
      toState: next,
    });
    replayIntentGovernancePreviousStateRef.current = next;
  }, [
    appendReplayIntentGovernanceAuditEntry,
    currentReplayIntentGovernanceSnapshot,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentGovernancePendingSourceRef,
    replayIntentGovernancePreviousStateRef,
  ]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState({
      redactionPolicy: replayIntentRedactionPolicy,
      reviewedConflictKeys: replayIntentGovernanceReviewedConflictKeys,
      retentionPolicy: replayIntentRetentionPolicy,
      shareMode: replayIntentShareMode,
      syncMode: replayIntentGovernanceSyncMode,
    });
  }, [
    replayIntentGovernanceReviewedConflictKeys,
    replayIntentGovernanceSyncMode,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentShareMode,
  ]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState({
      redactionPolicy: replayIntentRedactionPolicy,
      retentionPolicy: replayIntentRetentionPolicy,
      shareMode: replayIntentShareMode,
      sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
      sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
    });
  }, [
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentShareMode,
  ]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
        replayIntentLinkAuditTrail,
        replayIntentRetentionPolicy,
      ),
    );
  }, [replayIntentLinkAuditTrail, replayIntentRetentionPolicy]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
      pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
        replayIntentGovernanceAuditTrail,
        replayIntentRetentionPolicy,
      ),
    );
  }, [replayIntentGovernanceAuditTrail, replayIntentRetentionPolicy]);
  useEffect(() => {
    persistRunSurfaceCollectionQueryBuilderReplayLinkAliases(
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases(
        replayIntentLinkAliases,
        replayIntentRetentionPolicy,
      ),
    );
  }, [replayIntentLinkAliases, replayIntentRetentionPolicy]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const handleStorage = (event: StorageEvent) => {
      if (event.key === RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY) {
        const remoteAliases =
          loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue(event.newValue);
        setReplayIntentLinkAliases((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, remoteAliases),
        );
        return;
      }
      if (event.key === RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY) {
        const remoteAuditTrail =
          loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(event.newValue);
        setReplayIntentLinkAuditTrail((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(current, remoteAuditTrail),
        );
        return;
      }
      if (event.key === RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY) {
        const remoteGovernanceAuditTrail =
          loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(event.newValue);
        setReplayIntentGovernanceAuditTrail((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(current, remoteGovernanceAuditTrail),
        );
        return;
      }
      if (event.key !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY) {
        return;
      }
      handleIncomingReplayIntentGovernanceSyncState(
        readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(event.newValue),
        { source: "storage" },
      );
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [
    handleIncomingReplayIntentGovernanceSyncState,
    setReplayIntentGovernanceAuditTrail,
    setReplayIntentLinkAliases,
    setReplayIntentLinkAuditTrail,
  ]);
  useEffect(() => {
    if (replayIntentGovernanceSyncMode !== "review" && replayIntentGovernanceConflicts.length) {
      setReplayIntentGovernanceConflicts([]);
    }
  }, [
    replayIntentGovernanceConflicts.length,
    replayIntentGovernanceSyncMode,
    setReplayIntentGovernanceConflicts,
  ]);
  useEffect(() => {
    setReplayIntentGovernanceConflicts((current) =>
      current.filter((entry) =>
        !replayIntentGovernanceReviewedConflictKeys.includes(entry.conflictKey)
        && !areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual(
          {
            redactionPolicy: replayIntentRedactionPolicy,
            retentionPolicy: replayIntentRetentionPolicy,
            shareMode: replayIntentShareMode,
          },
          {
            redactionPolicy: entry.remoteRedactionPolicy,
            retentionPolicy: entry.remoteRetentionPolicy,
            shareMode: entry.remoteShareMode,
          },
        ),
      ),
    );
  }, [
    replayIntentGovernanceReviewedConflictKeys,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentShareMode,
    setReplayIntentGovernanceConflicts,
  ]);
  useEffect(() => {
    setReplayIntentLinkAliases((current) =>
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, replayIntentRetentionPolicy),
    );
    setReplayIntentLinkAuditTrail((current) =>
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(current, replayIntentRetentionPolicy),
    );
    setReplayIntentGovernanceAuditTrail((current) =>
      pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(current, replayIntentRetentionPolicy),
    );
  }, [
    replayIntentRetentionPolicy,
    setReplayIntentGovernanceAuditTrail,
    setReplayIntentLinkAliases,
    setReplayIntentLinkAuditTrail,
  ]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    handleIncomingReplayIntentGovernanceSyncState(
      readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(
        window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY),
      ),
      { source: "bootstrap" },
    );
  }, [handleIncomingReplayIntentGovernanceSyncState]);

  const applyRunSurfaceCollectionQueryBuilderReplayIntent = useCallback(
    (intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null) => {
      if (!intent) {
        setBundleCoordinationSimulationScope("all");
        setBundleCoordinationSimulationReplayIndex(0);
        setBundleCoordinationSimulationReplayGroupFilter("all");
        setBundleCoordinationSimulationReplayActionTypeFilter("all");
        setBundleCoordinationSimulationReplayEdgeFilter("all");
        setClauseReevaluationPreviewSelection({
          diffItemKey: null,
          groupKey: null,
          traceKey: null,
        });
        return;
      }
      setBundleCoordinationSimulationScope(intent.replayScope);
      setBundleCoordinationSimulationReplayIndex(intent.replayIndex);
      setBundleCoordinationSimulationReplayGroupFilter(intent.replayGroupFilter);
      setBundleCoordinationSimulationReplayActionTypeFilter(intent.replayActionTypeFilter);
      setBundleCoordinationSimulationReplayEdgeFilter(intent.replayEdgeFilter);
      setClauseReevaluationPreviewSelection(intent.previewSelection);
    },
    [
      setBundleCoordinationSimulationReplayActionTypeFilter,
      setBundleCoordinationSimulationReplayEdgeFilter,
      setBundleCoordinationSimulationReplayGroupFilter,
      setBundleCoordinationSimulationReplayIndex,
      setBundleCoordinationSimulationScope,
      setClauseReevaluationPreviewSelection,
    ],
  );
  useEffect(() => {
    const parsedAliasToken = extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl();
    const aliasToken = parsedAliasToken
      ? buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
          parsedAliasToken.aliasId,
          parsedAliasToken.signature,
        )
      : null;
    if (!aliasToken || !parsedAliasToken) {
      lastResolvedServerReplayLinkAliasTokenRef.current = null;
      return;
    }
    const localAliasEntry =
      replayIntentLinkAliases.find((entry) => entry.aliasId === parsedAliasToken.aliasId) ?? null;
    if (localAliasEntry?.resolutionSource !== "server" && localAliasEntry && !localAliasEntry.revokedAt) {
      lastResolvedServerReplayLinkAliasTokenRef.current = null;
      return;
    }
    if (lastResolvedServerReplayLinkAliasTokenRef.current === aliasToken) {
      if (
        localAliasEntry?.resolutionSource === "server"
        && !localAliasEntry.revokedAt
        && selectedRefTemplate?.key === localAliasEntry.templateKey
        && !areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
          localAliasEntry.intent,
          currentRunSurfaceCollectionQueryBuilderReplayIntent,
        )
      ) {
        applyRunSurfaceCollectionQueryBuilderReplayIntent(localAliasEntry.intent);
      }
      return;
    }
    let cancelled = false;
    void resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias(aliasToken)
      .then((record) => {
        if (cancelled) {
          return;
        }
        const aliasEntry = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord(record);
        lastResolvedServerReplayLinkAliasTokenRef.current = aliasToken;
        setReplayIntentLinkAliases((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, [aliasEntry]),
        );
        setReplayIntentUrlTemplateKey(aliasEntry.templateKey);
        if (selectedRefTemplate?.key === aliasEntry.templateKey) {
          applyRunSurfaceCollectionQueryBuilderReplayIntent(aliasEntry.intent);
          return;
        }
        setPredicateRefDraftKey(aliasEntry.templateKey);
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        lastResolvedServerReplayLinkAliasTokenRef.current = aliasToken;
        setReplayIntentShareStatus({
          message: "Replay alias is unavailable, expired, or has been revoked on the server.",
          tone: "error",
        });
      });
    return () => {
      cancelled = true;
    };
  }, [
    applyRunSurfaceCollectionQueryBuilderReplayIntent,
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    lastResolvedServerReplayLinkAliasTokenRef,
    replayIntentLinkAliases,
    selectedRefTemplate?.key,
    setPredicateRefDraftKey,
    setReplayIntentLinkAliases,
    setReplayIntentShareStatus,
    setReplayIntentUrlTemplateKey,
  ]);
  const appendReplayIntentLinkAuditEntry = useCallback(
    (entry: Omit<RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry, "id">) => {
      setReplayIntentLinkAuditTrail((current) => [
        {
          ...entry,
          id: buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId(),
        },
        ...current,
      ].slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES));
    },
    [setReplayIntentLinkAuditTrail],
  );
  const buildRunSurfaceCollectionQueryBuilderReplayIntentShareDescriptor = useCallback(async () => {
    if (!selectedRefTemplate?.key) {
      return null;
    }
    const redactedIntent = redactedRunSurfaceCollectionQueryBuilderReplayIntent;
    let aliasId: string | null = null;
    let aliasToken: string | null = null;
    let resolutionSource: "local" | "server" | null = null;
    let nextUrl = buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
      selectedRefTemplate.key,
      redactedIntent,
      typeof window !== "undefined" ? window.location.href : undefined,
      {
        forceTemplateKey: isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(redactedIntent),
      },
    );
    if (replayIntentShareMode === "indirect") {
      try {
        const serverRecord = await createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias({
          intent: redactedIntent,
          redactionPolicy: replayIntentRedactionPolicy,
          retentionPolicy: replayIntentRetentionPolicy,
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          templateKey: selectedRefTemplate.key,
          templateLabel: selectedRefTemplate.key,
        });
        const serverAliasEntry =
          buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord(serverRecord);
        aliasId = serverAliasEntry.aliasId;
        aliasToken = serverRecord.alias_token;
        resolutionSource = "server";
        setReplayIntentLinkAliases((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, [serverAliasEntry]),
        );
      } catch {
        aliasId = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId();
        const createdAt = new Date().toISOString();
        const expiresAt = buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry(
          replayIntentRetentionPolicy,
          createdAt,
        );
        const nextAliasEntry: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry = {
          aliasId,
          createdAt,
          createdByTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          createdByTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          expiresAt,
          intent: redactedIntent,
          redactionPolicy: replayIntentRedactionPolicy,
          resolutionSource: "local",
          revokedAt: null,
          revokedByTabId: null,
          revokedByTabLabel: null,
          signature: null,
          templateKey: selectedRefTemplate.key,
          templateLabel: selectedRefTemplate.key,
        };
        nextAliasEntry.signature = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature(
          nextAliasEntry,
          loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret(),
        );
        aliasToken = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
          aliasId,
          nextAliasEntry.signature,
        );
        resolutionSource = "local";
        setReplayIntentLinkAliases((current) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(
            current,
            [nextAliasEntry],
          ),
        );
      }
      nextUrl = buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
        selectedRefTemplate.key,
        redactedIntent,
        typeof window !== "undefined" ? window.location.href : undefined,
        {
          aliasId: aliasToken,
        },
      );
    }
    return {
      aliasId,
      aliasToken,
      compactLength: redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue?.length ?? 0,
      redactedIntent,
      resolutionSource,
      url: typeof window !== "undefined"
        ? new URL(nextUrl, window.location.origin).toString()
        : nextUrl,
    };
  }, [
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    redactedRunSurfaceCollectionQueryBuilderReplayIntent,
    redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue?.length,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentShareMode,
    selectedRefTemplate?.key,
    setReplayIntentLinkAliases,
  ]);
  const copyRunSurfaceCollectionQueryBuilderReplayIntentLink = useCallback(async () => {
    const descriptor = await buildRunSurfaceCollectionQueryBuilderReplayIntentShareDescriptor();
    if (!descriptor || !selectedRefTemplate?.key) {
      setReplayIntentShareStatus({
        message: "Replay deep link is unavailable for the current template state.",
        tone: "error",
      });
      return;
    }
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(descriptor.url);
        setReplayIntentShareStatus({
          message:
            replayIntentShareMode === "indirect"
              ? `Copied ${descriptor.resolutionSource === "server" ? "server alias" : "local alias"} link.`
              : "Copied replay deep link.",
          tone: "success",
        });
        appendReplayIntentLinkAuditEntry({
          action: "copy",
          aliasId: descriptor.aliasId,
          at: new Date().toISOString(),
          linkLength: descriptor.url.length,
          mode: replayIntentShareMode,
          redactionPolicy: replayIntentRedactionPolicy,
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          status: "success",
          templateKey: selectedRefTemplate.key,
          templateLabel: selectedRefTemplate.key,
        });
        return;
      }
      throw new Error("clipboard unavailable");
    } catch {
      setReplayIntentShareStatus({
        message: "Clipboard access is unavailable in this browser.",
        tone: "error",
      });
      appendReplayIntentLinkAuditEntry({
        action: "copy",
        aliasId: descriptor.aliasId,
        at: new Date().toISOString(),
        linkLength: descriptor.url.length,
        mode: replayIntentShareMode,
        redactionPolicy: replayIntentRedactionPolicy,
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        status: "failed",
        templateKey: selectedRefTemplate.key,
        templateLabel: selectedRefTemplate.key,
      });
    }
  }, [
    appendReplayIntentLinkAuditEntry,
    buildRunSurfaceCollectionQueryBuilderReplayIntentShareDescriptor,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentRedactionPolicy,
    replayIntentShareMode,
    selectedRefTemplate?.key,
    setReplayIntentShareStatus,
  ]);
  const shareRunSurfaceCollectionQueryBuilderReplayIntentLink = useCallback(async () => {
    const descriptor = await buildRunSurfaceCollectionQueryBuilderReplayIntentShareDescriptor();
    if (!descriptor || !selectedRefTemplate?.key) {
      setReplayIntentShareStatus({
        message: "Replay deep link is unavailable for the current template state.",
        tone: "error",
      });
      return;
    }
    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share({
          title: selectedRefTemplate.key
            ? `${selectedRefTemplate.key} replay deep link`
            : "Replay deep link",
          url: descriptor.url,
        });
        setReplayIntentShareStatus({
          message:
            replayIntentShareMode === "indirect"
              ? `Shared ${descriptor.resolutionSource === "server" ? "server alias" : "local alias"} link.`
              : "Shared replay deep link.",
          tone: "success",
        });
        appendReplayIntentLinkAuditEntry({
          action: "share",
          aliasId: descriptor.aliasId,
          at: new Date().toISOString(),
          linkLength: descriptor.url.length,
          mode: replayIntentShareMode,
          redactionPolicy: replayIntentRedactionPolicy,
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          status: "success",
          templateKey: selectedRefTemplate.key,
          templateLabel: selectedRefTemplate.key,
        });
        return;
      }
      throw new Error("share unavailable");
    } catch {
      setReplayIntentShareStatus({
        message: "Share is unavailable or was cancelled.",
        tone: "muted",
      });
      appendReplayIntentLinkAuditEntry({
        action: "share",
        aliasId: descriptor.aliasId,
        at: new Date().toISOString(),
        linkLength: descriptor.url.length,
        mode: replayIntentShareMode,
        redactionPolicy: replayIntentRedactionPolicy,
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        status: "cancelled",
        templateKey: selectedRefTemplate.key,
        templateLabel: selectedRefTemplate.key,
      });
    }
  }, [
    appendReplayIntentLinkAuditEntry,
    buildRunSurfaceCollectionQueryBuilderReplayIntentShareDescriptor,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentRedactionPolicy,
    replayIntentShareMode,
    selectedRefTemplate?.key,
    setReplayIntentShareStatus,
  ]);
  const revokeRunSurfaceCollectionQueryBuilderReplayIntentAlias = useCallback(async (
    aliasEntry: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
  ) => {
    const aliasToken = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
      aliasEntry.aliasId,
      aliasEntry.signature,
    );
    try {
      const revokedRecord = await revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias(aliasToken, {
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
      });
      const revokedEntry = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord(revokedRecord);
      setReplayIntentLinkAliases((current) =>
        mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, [revokedEntry]),
      );
      appendReplayIntentLinkAuditEntry({
        action: "revoke",
        aliasId: aliasEntry.aliasId,
        at: new Date().toISOString(),
        linkLength: aliasToken.length,
        mode: "indirect",
        redactionPolicy: aliasEntry.redactionPolicy,
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        status: "success",
        templateKey: aliasEntry.templateKey,
        templateLabel: aliasEntry.templateLabel,
      });
      setReplayIntentShareStatus({
        message: `Revoked replay alias ${aliasEntry.aliasId.slice(0, 8)} on the server.`,
        tone: "success",
      });
    } catch {
      appendReplayIntentLinkAuditEntry({
        action: "revoke",
        aliasId: aliasEntry.aliasId,
        at: new Date().toISOString(),
        linkLength: aliasToken.length,
        mode: "indirect",
        redactionPolicy: aliasEntry.redactionPolicy,
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        status: "failed",
        templateKey: aliasEntry.templateKey,
        templateLabel: aliasEntry.templateLabel,
      });
      setReplayIntentShareStatus({
        message: "Replay alias revocation failed.",
        tone: "error",
      });
    }
  }, [
    appendReplayIntentLinkAuditEntry,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    setReplayIntentLinkAliases,
    setReplayIntentShareStatus,
  ]);
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits = useCallback(async (
    options?: { adminToken?: string; silent?: boolean },
  ) => {
    const adminToken = (options?.adminToken ?? replayIntentServerAuditReadToken.trim())
      || replayIntentServerAuditWriteToken.trim();
    const normalizedLimit = Number.parseInt(replayIntentServerAuditLimit, 10);
    setReplayIntentServerAuditLoading(true);
    if (!options?.silent) {
      setReplayIntentServerAuditStatus(null);
    }
    try {
      const payload = await listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        limit: Number.isFinite(normalizedLimit) ? normalizedLimit : 25,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditItems(payload.items);
      setReplayIntentServerAuditTotal(payload.total);
      if (!options?.silent) {
        setReplayIntentServerAuditStatus({
          message: `Loaded ${payload.items.length} server replay alias audit record${payload.items.length === 1 ? "" : "s"}.`,
          tone: payload.items.length ? "success" : "muted",
        });
      }
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditItems,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
    setReplayIntentServerAuditTotal,
  ]);
  const pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords = useCallback(async (
    pruneMode: "expired" | "matched",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditLoading(true);
    setReplayIntentServerAuditStatus(null);
    try {
      const payload = await pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        includeManual: replayIntentServerAuditIncludeManual,
        pruneMode,
        recordedBefore: replayIntentServerAuditRecordedBefore,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditStatus({
        message:
          pruneMode === "expired"
            ? `Pruned ${payload.deleted_count} expired server replay alias audit record${payload.deleted_count === 1 ? "" : "s"}.`
            : `Pruned ${payload.deleted_count} matched server replay alias audit record${payload.deleted_count === 1 ? "" : "s"}.`,
        tone: payload.deleted_count ? "success" : "muted",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to prune server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditIncludeManual,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
  ]);
  const exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords = useCallback(async (
    exportFormat: "json" | "csv",
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditLoading(true);
    setReplayIntentServerAuditStatus(null);
    try {
      const payload = await exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        exportFormat,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      downloadTextPayload(payload.content, payload.content_type, payload.filename);
      setReplayIntentServerAuditStatus({
        message: `Exported ${payload.record_count} server replay alias audit record${payload.record_count === 1 ? "" : "s"} as ${payload.format.toUpperCase()}.`,
        tone: payload.record_count ? "success" : "muted",
      });
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to export server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
  ]);
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs = useCallback(async (
    options?: { adminToken?: string; silent?: boolean },
  ) => {
    const adminToken = (options?.adminToken ?? replayIntentServerAuditReadToken.trim())
      || replayIntentServerAuditWriteToken.trim();
    const normalizedLimit = Number.parseInt(replayIntentServerAuditLimit, 10);
    setReplayIntentServerAuditExportJobLoading(true);
    if (!options?.silent) {
      setReplayIntentServerAuditExportJobStatus(null);
    }
    try {
      const payload = await listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        exportFormat: "all",
        limit: Number.isFinite(normalizedLimit) ? normalizedLimit : 25,
        requestedByTabId: replayIntentServerAuditSourceTabFilter,
        search: replayIntentServerAuditSearch,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobs(payload.items);
      setReplayIntentServerAuditExportJobTotal(payload.total);
      if (!options?.silent) {
        setReplayIntentServerAuditExportJobStatus({
          message: `Loaded ${payload.items.length} server export job${payload.items.length === 1 ? "" : "s"}.`,
          tone: payload.items.length ? "success" : "muted",
        });
      }
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay audit export jobs.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
    setReplayIntentServerAuditExportJobTotal,
    setReplayIntentServerAuditExportJobs,
  ]);
  const createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord = useCallback(async (
    exportFormat: "json" | "csv",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        exportFormat,
        requestedByTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        requestedByTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobStatus({
        message: `Created ${payload.export_format.toUpperCase()} export job ${payload.job_id.slice(0, 8)} for ${payload.record_count} server audit record${payload.record_count === 1 ? "" : "s"}.`,
        tone: payload.record_count ? "success" : "muted",
      });
      setReplayIntentServerAuditExportJobHistory(null);
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to create server replay audit export job.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord = useCallback(async (
    jobId: string,
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob({
        adminToken,
        jobId,
      });
      downloadTextPayload(payload.content, payload.content_type, payload.filename);
      setReplayIntentServerAuditExportJobStatus({
        message: `Downloaded export job ${payload.job_id.slice(0, 8)} as ${payload.export_format.toUpperCase()}.`,
        tone: "success",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to download server replay audit export job.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory = useCallback(async (
    jobId: string,
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory({
        adminToken,
        jobId,
      });
      setReplayIntentServerAuditExportJobHistory(payload);
      setReplayIntentServerAuditExportJobStatus({
        message: `Loaded ${payload.history.length} export job audit event${payload.history.length === 1 ? "" : "s"} for ${payload.job.filename}.`,
        tone: payload.history.length ? "success" : "muted",
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay audit export job history.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    replayIntentServerAuditReadToken,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords = useCallback(async (
    pruneMode: "expired" | "matched",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        createdBefore: replayIntentServerAuditRecordedBefore,
        exportFormat: "all",
        pruneMode,
        requestedByTabId: replayIntentServerAuditSourceTabFilter,
        search: replayIntentServerAuditSearch,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobHistory(null);
      setReplayIntentServerAuditExportJobStatus({
        message:
          pruneMode === "expired"
            ? `Pruned ${payload.deleted_job_count} expired export job${payload.deleted_job_count === 1 ? "" : "s"}, ${payload.deleted_artifact_count} retained artifact${payload.deleted_artifact_count === 1 ? "" : "s"}, and ${payload.deleted_history_count} history record${payload.deleted_history_count === 1 ? "" : "s"}.`
            : `Pruned ${payload.deleted_job_count} matched export job${payload.deleted_job_count === 1 ? "" : "s"}, ${payload.deleted_artifact_count} retained artifact${payload.deleted_artifact_count === 1 ? "" : "s"}, and ${payload.deleted_history_count} history record${payload.deleted_history_count === 1 ? "" : "s"}.`,
        tone: payload.deleted_job_count || payload.deleted_artifact_count || payload.deleted_history_count ? "success" : "muted",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to prune server replay audit export jobs.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const copyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload = useCallback(async () => {
    if (!currentReplayIntentGovernancePayloadValue) {
      setReplayIntentGovernanceStatus({
        message: "Replay link governance payload is unavailable in this browser.",
        tone: "error",
      });
      return;
    }
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(currentReplayIntentGovernancePayloadValue);
        appendReplayIntentGovernanceAuditEntry({
          at: new Date().toISOString(),
          detail: `${predicateRefReplayApplyHistoryTabIdentity.label} copied a cross-device replay link governance payload.`,
          diffKeys: [],
          fromState: currentReplayIntentGovernanceSnapshot,
          kind: "cross_device_export",
          remoteSourceTabId: null,
          remoteSourceTabLabel: null,
          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
          toState: currentReplayIntentGovernanceSnapshot,
        });
        setReplayIntentGovernanceStatus({
          message: "Copied cross-device governance payload.",
          tone: "success",
        });
        return;
      }
      throw new Error("clipboard unavailable");
    } catch {
      setReplayIntentGovernanceStatus({
        message: "Clipboard access is unavailable for governance payload copy.",
        tone: "error",
      });
    }
  }, [
    appendReplayIntentGovernanceAuditEntry,
    currentReplayIntentGovernancePayloadValue,
    currentReplayIntentGovernanceSnapshot,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    setReplayIntentGovernanceStatus,
  ]);
  const applyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload = useCallback(() => {
    const payload = decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload(
      replayIntentGovernancePayloadDraft,
    );
    if (!payload) {
      setReplayIntentGovernanceStatus({
        message: "Governance payload is invalid or expired.",
        tone: "error",
      });
      return;
    }
    const diffKeys = getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
      currentReplayIntentGovernanceSnapshot,
      payload.governance,
    );
    if (!diffKeys.length) {
      setReplayIntentGovernanceStatus({
        message: "Imported governance payload already matches this tab.",
        tone: "muted",
      });
      return;
    }
    applyReplayIntentGovernanceSnapshot(payload.governance, {
      detail: `Applied a cross-device replay link governance payload exported by ${payload.sourceTabLabel}.`,
      kind: "cross_device_import",
      remoteSourceTabId: payload.sourceTabId,
      remoteSourceTabLabel: payload.sourceTabLabel,
    });
    setReplayIntentGovernancePayloadDraft("");
    setReplayIntentGovernanceStatus({
      message: `Applied governance payload from ${payload.sourceTabLabel}.`,
      tone: "success",
    });
  }, [
    applyReplayIntentGovernanceSnapshot,
    currentReplayIntentGovernanceSnapshot,
    replayIntentGovernancePayloadDraft,
    setReplayIntentGovernancePayloadDraft,
    setReplayIntentGovernanceStatus,
  ]);

  const replayGovernanceSectionProps: QueryBuilderReplayGovernanceSectionProps = {
    callbacks: {
      appendReplayIntentGovernanceAuditEntry,
      applyReplayIntentGovernanceSnapshot,
      applyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
      copyRunSurfaceCollectionQueryBuilderReplayIntentLink,
      copyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
      createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
      dismissReplayIntentGovernanceConflict,
      downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
      exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
      loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
      loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
      loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
      pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords,
      pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
      revokeRunSurfaceCollectionQueryBuilderReplayIntentAlias,
      setReplayIntentGovernanceAuditTrail,
      setReplayIntentGovernancePayloadDraft,
      setReplayIntentGovernanceStatus,
      setReplayIntentGovernanceSyncMode,
      setReplayIntentLinkAliases,
      setReplayIntentLinkAuditTrail,
      setReplayIntentRedactionPolicy,
      setReplayIntentRetentionPolicy,
      setReplayIntentServerAuditActionFilter,
      setReplayIntentServerAuditAliasFilter,
      setReplayIntentServerAuditIncludeManual,
      setReplayIntentServerAuditLimit,
      setReplayIntentServerAuditReadToken,
      setReplayIntentServerAuditRecordedBefore,
      setReplayIntentServerAuditRetentionFilter,
      setReplayIntentServerAuditSearch,
      setReplayIntentServerAuditSourceTabFilter,
      setReplayIntentServerAuditTemplateFilter,
      setReplayIntentServerAuditWriteToken,
      setReplayIntentShareMode,
      setReplayIntentShareStatus,
      shareRunSurfaceCollectionQueryBuilderReplayIntentLink,
    },
    governance: {
      currentReplayIntentGovernancePayloadValue,
      currentReplayIntentGovernanceSnapshot,
      predicateRefReplayApplyHistoryTabIdentity,
      redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue,
      replayIntentGovernanceAuditTrail,
      replayIntentGovernanceConflicts,
      replayIntentGovernancePayloadDraft,
      replayIntentGovernanceStatus,
      replayIntentGovernanceSyncMode,
      replayIntentRedactionPolicy,
      replayIntentRetentionPolicy,
      replayIntentShareMode,
      replayIntentShareStatus,
      visibleReplayIntentLinkAliases,
      visibleReplayIntentLinkAuditTrail,
    },
    helpers: {
      buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken,
      formatRelativeTimestampLabel,
      formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue,
      getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys,
    },
    serverAudit: {
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
    },
  };

  return {
    applyRunSurfaceCollectionQueryBuilderReplayIntent,
    currentRunSurfaceCollectionQueryBuilderReplayIntent,
    lastHydratedReplayIntentTemplateIdRef,
    replayGovernanceSectionProps,
    replayIntentUrlTemplateKey,
    setReplayIntentUrlTemplateKey,
  };
}
