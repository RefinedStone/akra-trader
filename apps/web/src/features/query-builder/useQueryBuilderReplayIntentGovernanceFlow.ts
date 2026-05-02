import { useCallback, useEffect, useMemo } from "react";

import {
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
} from "../../controlRoomDefinitions";
import type { QueryBuilderReplayGovernanceSectionProps } from "./QueryBuilderReplayGovernanceSection";
import {
  areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId,
  buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
  getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts,
  limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue,
  loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue,
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
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource,
} from "./model";

export function useQueryBuilderReplayIntentGovernanceFlow(args: any) {
  const {
    currentRunSurfaceCollectionQueryBuilderReplayIntentLink,
    predicateRefReplayApplyHistoryTabIdentity,
    replayIntentGovernanceAuditTrail,
    replayIntentGovernanceConflicts,
    replayIntentGovernancePendingSourceRef,
    replayIntentGovernancePreviousStateRef,
    replayIntentGovernanceReviewedConflictKeys,
    replayIntentGovernanceSyncMode,
    replayIntentLinkAliases,
    replayIntentLinkAuditTrail,
    replayIntentRedactionPolicy,
    replayIntentRetentionPolicy,
    replayIntentShareMode,
    setReplayIntentGovernanceAuditTrail,
    setReplayIntentGovernanceConflicts,
    setReplayIntentGovernanceReviewedConflictKeys,
    setReplayIntentGovernanceStatus,
    setReplayIntentGovernanceSyncMode,
    setReplayIntentLinkAliases,
    setReplayIntentLinkAuditTrail,
    setReplayIntentRedactionPolicy,
    setReplayIntentRetentionPolicy,
    setReplayIntentShareMode,
    setReplayIntentShareStatus,
  } = args;
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
      setReplayIntentGovernanceAuditTrail((current: any) =>
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
      setReplayIntentGovernanceConflicts((current: any) =>
        current.filter((entry: any) => entry.conflictKey !== conflictKey),
      );
      if (options?.rememberResolution !== false) {
        setReplayIntentGovernanceReviewedConflictKeys((current: any) =>
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
        setReplayIntentGovernanceConflicts((current: any) =>
          current.filter((entry: any) => entry.conflictKey !== conflictKey),
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
        if (!replayIntentGovernanceConflicts.some((entry: any) => entry.conflictKey === conflictKey)) {
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
        setReplayIntentGovernanceConflicts((current: any) => {
          const nextByKey = new Map(
            current.map((entry: any) => [entry.conflictKey, entry] as const),
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
            (Array.from(nextByKey.values()) as any[]).sort((left: any, right: any) => right.detectedAt.localeCompare(left.detectedAt)),
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
      setReplayIntentGovernanceConflicts((current: any) =>
        current.filter((entry: any) => entry.conflictKey !== conflictKey),
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
        setReplayIntentLinkAliases((current: any) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, remoteAliases),
        );
        return;
      }
      if (event.key === RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY) {
        const remoteAuditTrail =
          loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(event.newValue);
        setReplayIntentLinkAuditTrail((current: any) =>
          mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(current, remoteAuditTrail),
        );
        return;
      }
      if (event.key === RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY) {
        const remoteGovernanceAuditTrail =
          loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(event.newValue);
        setReplayIntentGovernanceAuditTrail((current: any) =>
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
    setReplayIntentGovernanceConflicts((current: any) =>
      current.filter((entry: any) =>
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
    setReplayIntentLinkAliases((current: any) =>
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases(current, replayIntentRetentionPolicy),
    );
    setReplayIntentLinkAuditTrail((current: any) =>
      pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(current, replayIntentRetentionPolicy),
    );
    setReplayIntentGovernanceAuditTrail((current: any) =>
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


  return {
    appendReplayIntentGovernanceAuditEntry,
    applyReplayIntentGovernanceSnapshot,
    currentReplayIntentGovernancePayloadValue,
    currentReplayIntentGovernanceSnapshot,
    dismissReplayIntentGovernanceConflict,
  };
}
