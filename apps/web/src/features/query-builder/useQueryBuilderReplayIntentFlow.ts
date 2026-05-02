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
import { useQueryBuilderReplayIntentGovernanceFlow } from "./useQueryBuilderReplayIntentGovernanceFlow";
import { useQueryBuilderReplayIntentServerAuditFlow } from "./useQueryBuilderReplayIntentServerAuditFlow";

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

  const {
    appendReplayIntentGovernanceAuditEntry,
    applyReplayIntentGovernanceSnapshot,
    currentReplayIntentGovernancePayloadValue,
    currentReplayIntentGovernanceSnapshot,
    dismissReplayIntentGovernanceConflict,
  } = useQueryBuilderReplayIntentGovernanceFlow({
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
  });

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
  const {
    createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
    downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
    exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords,
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
  } = useQueryBuilderReplayIntentServerAuditFlow({
    predicateRefReplayApplyHistoryTabIdentity,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditIncludeManual,
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
    setReplayIntentServerAuditExportJobTotal,
    setReplayIntentServerAuditExportJobs,
    setReplayIntentServerAuditItems,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
    setReplayIntentServerAuditTotal,
  });
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
