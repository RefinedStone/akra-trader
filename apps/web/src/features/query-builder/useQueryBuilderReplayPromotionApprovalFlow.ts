import { useCallback, useEffect, useMemo, type Dispatch, type SetStateAction } from "react";

import { MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES } from "../../controlRoomDefinitions";
import { buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId } from "./model";
import type {
  PredicateRefReplayApplyHistoryEntry,
  PredicateRefReplayApplyHistoryTabIdentity,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";

type PromotionGroup = {
  key: string;
  label: string;
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
  presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
};

type ReplayActionEdge = {
  key: string;
  targetBundleKey: string;
  targetGroupKey: string;
};

type ReplayAction = {
  dependencyEdges: ReplayActionEdge[];
};

type CoordinatedGroupBundleState = {
  policyTraceByGroupKey: Record<string, { statusLabel: string } | null | undefined>;
  resolvedSelectionsByGroupKey: Record<string, string>;
};

export type QueryBuilderReplayPromotionConflict = {
  bundleLabels: string[];
  groupLabel: string;
};

export type QueryBuilderReplayPromotionPreviewRow = {
  changesCurrent: boolean;
  currentBundleLabel: string;
  currentStatus: string;
  group: PromotionGroup;
  matchesSimulation: boolean;
  promotedBundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState;
  simulatedBundleLabel: string;
  simulatedStatus: string;
};

export type QueryBuilderReplayPromotionSummary = {
  changesCurrentCount: number;
  matchesSimulationCount: number;
  total: number;
};

type UseQueryBuilderReplayPromotionApprovalFlowArgs = {
  activeSimulatedPredicateRefSolverReplayFilteredActions: ReplayAction[];
  activeSimulatedPredicateRefSolverReplayIndex: number;
  appendPredicateRefReplayApplySyncAuditEntry: (entry: {
    at: string;
    auditId: string;
    detail: string;
    entryId: string;
    kind: "local_apply";
    sourceTabId: string;
    sourceTabLabel: string;
    templateId: string;
    templateLabel: string;
  }) => void;
  applyPredicateRefGroupPresetBundles: (
    templateId: string,
    selections: Array<{
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState | null;
      group: PromotionGroup;
    }>,
  ) => void;
  bundleCoordinationSimulationApprovalDecisionsByGroupKey: Record<string, boolean>;
  bundleCoordinationSimulationApprovalDiffOnly: boolean;
  bundleCoordinationSimulationApprovalOpen: boolean;
  bundleCoordinationSimulationPolicy: string;
  bundleCoordinationSimulationPromotionDecisionsByGroupKey: Record<string, boolean>;
  bundleCoordinationSimulationReplayActionTypeFilter: string;
  bundleCoordinationSimulationReplayEdgeFilter: string;
  bundleCoordinationSimulationReplayGroupFilter: string;
  bundleCoordinationSimulationScope: string;
  coordinatedPredicateRefGroupBundleState: CoordinatedGroupBundleState;
  getSortedTemplateGroupPresetBundles: (
    bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[],
  ) => RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
  predicateRefDraftBindings: Record<string, string>;
  predicateRefGroupBundleSelections: Record<string, string>;
  predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  setBundleCoordinationSimulationApprovalDecisionsByGroupKey: Dispatch<SetStateAction<Record<string, boolean>>>;
  setBundleCoordinationSimulationApprovalOpen: Dispatch<SetStateAction<boolean>>;
  setBundleCoordinationSimulationFinalSummaryOpen: Dispatch<SetStateAction<boolean>>;
  setBundleCoordinationSimulationPromotionDecisionsByGroupKey: Dispatch<SetStateAction<Record<string, boolean>>>;
  setPredicateRefReplayApplyHistory: Dispatch<SetStateAction<PredicateRefReplayApplyHistoryEntry[]>>;
  simulatedCoordinationGroups: PromotionGroup[];
  simulatedPredicateRefGroupBundleState: CoordinatedGroupBundleState | null;
};

export function useQueryBuilderReplayPromotionApprovalFlow({
  activeSimulatedPredicateRefSolverReplayFilteredActions,
  activeSimulatedPredicateRefSolverReplayIndex,
  appendPredicateRefReplayApplySyncAuditEntry,
  applyPredicateRefGroupPresetBundles,
  bundleCoordinationSimulationApprovalDecisionsByGroupKey,
  bundleCoordinationSimulationApprovalDiffOnly,
  bundleCoordinationSimulationApprovalOpen,
  bundleCoordinationSimulationPolicy,
  bundleCoordinationSimulationPromotionDecisionsByGroupKey,
  bundleCoordinationSimulationReplayActionTypeFilter,
  bundleCoordinationSimulationReplayEdgeFilter,
  bundleCoordinationSimulationReplayGroupFilter,
  bundleCoordinationSimulationScope,
  coordinatedPredicateRefGroupBundleState,
  getSortedTemplateGroupPresetBundles,
  predicateRefDraftBindings,
  predicateRefGroupBundleSelections,
  predicateRefReplayApplyHistoryTabIdentity,
  selectedRefTemplate,
  setBundleCoordinationSimulationApprovalDecisionsByGroupKey,
  setBundleCoordinationSimulationApprovalOpen,
  setBundleCoordinationSimulationFinalSummaryOpen,
  setBundleCoordinationSimulationPromotionDecisionsByGroupKey,
  setPredicateRefReplayApplyHistory,
  simulatedCoordinationGroups,
  simulatedPredicateRefGroupBundleState,
}: UseQueryBuilderReplayPromotionApprovalFlowArgs) {
  const simulatedPredicateRefReplayPromotionDraft = useMemo(() => {
    const targetSelections = new Map<string, {
      bundlesByKey: Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState>;
      group: PromotionGroup;
    }>();
    activeSimulatedPredicateRefSolverReplayFilteredActions.forEach((action) => {
      action.dependencyEdges.forEach((edge) => {
        if (
          bundleCoordinationSimulationReplayEdgeFilter !== "all"
          && edge.key !== bundleCoordinationSimulationReplayEdgeFilter
        ) {
          return;
        }
        const group = simulatedCoordinationGroups.find((candidate) => candidate.key === edge.targetGroupKey);
        if (!group) {
          return;
        }
        const bundle =
          getSortedTemplateGroupPresetBundles(group.presetBundles).find(
            (candidate) => candidate.key === edge.targetBundleKey,
          ) ?? null;
        if (!bundle) {
          return;
        }
        const existing = targetSelections.get(group.key);
        if (existing) {
          existing.bundlesByKey.set(bundle.key, bundle);
          return;
        }
        targetSelections.set(group.key, {
          bundlesByKey: new Map([[bundle.key, bundle]]),
          group,
        });
      });
    });
    const promotableSelections: Array<{
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState;
      group: PromotionGroup;
    }> = [];
    const conflicts: QueryBuilderReplayPromotionConflict[] = [];
    targetSelections.forEach(({ bundlesByKey, group }) => {
      const bundles = Array.from(bundlesByKey.values());
      if (bundles.length === 1) {
        promotableSelections.push({
          bundle: bundles[0],
          group,
        });
        return;
      }
      conflicts.push({
        bundleLabels: bundles.map((bundle) => bundle.label),
        groupLabel: group.label,
      });
    });
    return {
      conflicts,
      promotableSelections,
    };
  }, [
    activeSimulatedPredicateRefSolverReplayFilteredActions,
    bundleCoordinationSimulationReplayEdgeFilter,
    getSortedTemplateGroupPresetBundles,
    simulatedCoordinationGroups,
  ]);
  const simulatedPredicateRefReplayPromotionPreviewRows = useMemo<QueryBuilderReplayPromotionPreviewRow[]>(
    () => simulatedPredicateRefReplayPromotionDraft.promotableSelections.map(({ bundle, group }) => {
      const currentBundleKey =
        coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey[group.key] ?? "";
      const simulatedBundleKey =
        simulatedPredicateRefGroupBundleState?.resolvedSelectionsByGroupKey[group.key] ?? "";
      const currentBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((candidate) => candidate.key === currentBundleKey)
        ?? null;
      const simulatedBundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find((candidate) => candidate.key === simulatedBundleKey)
        ?? null;
      const currentStatus =
        coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey[group.key]?.statusLabel ?? "Idle";
      const simulatedStatus =
        simulatedPredicateRefGroupBundleState?.policyTraceByGroupKey[group.key]?.statusLabel ?? "Idle";
      return {
        changesCurrent: currentBundle?.key !== bundle.key,
        currentBundleLabel: currentBundle?.label ?? "No bundle",
        currentStatus,
        group,
        matchesSimulation: simulatedBundle?.key === bundle.key,
        promotedBundle: bundle,
        simulatedBundleLabel: simulatedBundle?.label ?? "No bundle",
        simulatedStatus,
      };
    }),
    [
      coordinatedPredicateRefGroupBundleState.policyTraceByGroupKey,
      coordinatedPredicateRefGroupBundleState.resolvedSelectionsByGroupKey,
      getSortedTemplateGroupPresetBundles,
      simulatedPredicateRefGroupBundleState,
      simulatedPredicateRefReplayPromotionDraft.promotableSelections,
    ],
  );
  const stagedSimulatedPredicateRefReplayPromotionSelections = useMemo(
    () => simulatedPredicateRefReplayPromotionPreviewRows.filter((row) =>
      bundleCoordinationSimulationPromotionDecisionsByGroupKey[row.group.key] ?? true,
    ),
    [
      bundleCoordinationSimulationPromotionDecisionsByGroupKey,
      simulatedPredicateRefReplayPromotionPreviewRows,
    ],
  );
  const visibleSimulatedPredicateRefReplayApprovalRows = useMemo(
    () => (
      bundleCoordinationSimulationApprovalDiffOnly
        ? stagedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
            row.changesCurrent || !row.matchesSimulation,
          )
        : stagedSimulatedPredicateRefReplayPromotionSelections
    ),
    [
      bundleCoordinationSimulationApprovalDiffOnly,
      stagedSimulatedPredicateRefReplayPromotionSelections,
    ],
  );
  const approvedSimulatedPredicateRefReplayPromotionSelections = useMemo(
    () => stagedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
      bundleCoordinationSimulationApprovalDecisionsByGroupKey[row.group.key] ?? true,
    ),
    [
      bundleCoordinationSimulationApprovalDecisionsByGroupKey,
      stagedSimulatedPredicateRefReplayPromotionSelections,
    ],
  );
  const approvedSimulatedPredicateRefReplayPromotionSummary = useMemo<QueryBuilderReplayPromotionSummary>(
    () => ({
      changesCurrentCount: approvedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
        row.changesCurrent,
      ).length,
      matchesSimulationCount: approvedSimulatedPredicateRefReplayPromotionSelections.filter((row) =>
        row.matchesSimulation,
      ).length,
      total: approvedSimulatedPredicateRefReplayPromotionSelections.length,
    }),
    [approvedSimulatedPredicateRefReplayPromotionSelections],
  );
  const canReviewStagedReplayDraft = Boolean(
    stagedSimulatedPredicateRefReplayPromotionSelections.length
    && !simulatedPredicateRefReplayPromotionDraft.conflicts.length,
  );
  const canReviewReplayFinalSummary = Boolean(
    selectedRefTemplate && approvedSimulatedPredicateRefReplayPromotionSelections.length,
  );

  const openReplayApprovalReview = useCallback(() => {
    if (!stagedSimulatedPredicateRefReplayPromotionSelections.length) {
      return;
    }
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey(
      Object.fromEntries(
        stagedSimulatedPredicateRefReplayPromotionSelections.map((row) => [row.group.key, true]),
      ),
    );
    setBundleCoordinationSimulationFinalSummaryOpen(false);
    setBundleCoordinationSimulationApprovalOpen(true);
  }, [
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey,
    setBundleCoordinationSimulationApprovalOpen,
    setBundleCoordinationSimulationFinalSummaryOpen,
    stagedSimulatedPredicateRefReplayPromotionSelections,
  ]);
  const closeReplayApprovalReview = useCallback(
    () => setBundleCoordinationSimulationApprovalOpen(false),
    [setBundleCoordinationSimulationApprovalOpen],
  );
  const openReplayFinalSummary = useCallback(() => {
    if (!selectedRefTemplate || !approvedSimulatedPredicateRefReplayPromotionSelections.length) {
      return;
    }
    setBundleCoordinationSimulationFinalSummaryOpen(true);
  }, [
    approvedSimulatedPredicateRefReplayPromotionSelections.length,
    selectedRefTemplate,
    setBundleCoordinationSimulationFinalSummaryOpen,
  ]);
  const closeReplayFinalSummary = useCallback(
    () => setBundleCoordinationSimulationFinalSummaryOpen(false),
    [setBundleCoordinationSimulationFinalSummaryOpen],
  );
  const toggleReplayPromotionDecision = useCallback((groupKey: string) => {
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey((current) => ({
      ...current,
      [groupKey]: !(current[groupKey] ?? true),
    }));
  }, [setBundleCoordinationSimulationPromotionDecisionsByGroupKey]);
  const toggleReplayApprovalDecision = useCallback((groupKey: string) => {
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey((current) => ({
      ...current,
      [groupKey]: !(current[groupKey] ?? true),
    }));
  }, [setBundleCoordinationSimulationApprovalDecisionsByGroupKey]);
  const applyApprovedReplayDraft = useCallback(() => {
    if (!selectedRefTemplate || !approvedSimulatedPredicateRefReplayPromotionSelections.length) {
      return;
    }
    const appliedAt = new Date().toISOString();
    const historyEntry: PredicateRefReplayApplyHistoryEntry = {
      appliedAt,
      approvedCount: approvedSimulatedPredicateRefReplayPromotionSummary.total,
      changedCurrentCount: approvedSimulatedPredicateRefReplayPromotionSummary.changesCurrentCount,
      id: `replay-apply:${selectedRefTemplate.id}:${appliedAt}`,
      matchesSimulationCount: approvedSimulatedPredicateRefReplayPromotionSummary.matchesSimulationCount,
      rollbackSnapshot: {
        draftBindingsByParameterKey: Object.fromEntries(
          approvedSimulatedPredicateRefReplayPromotionSelections.flatMap((row) =>
            row.group.parameters.map((parameter) => [
              parameter.key,
              predicateRefDraftBindings[parameter.key] ?? null,
            ] as const),
          ),
        ),
        groupSelectionsBySelectionKey: Object.fromEntries(
          approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => {
            const selectionKey = `${selectedRefTemplate.id}:${row.group.key}`;
            return [
              selectionKey,
              predicateRefGroupBundleSelections[selectionKey] ?? null,
            ] as const;
          }),
        ),
      },
      rows: approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => ({
        changesCurrent: row.changesCurrent,
        currentBundleLabel: row.currentBundleLabel,
        currentStatus: row.currentStatus,
        groupKey: row.group.key,
        groupLabel: row.group.label,
        matchesSimulation: row.matchesSimulation,
        promotedBundleKey: row.promotedBundle.key,
        promotedBundleLabel: row.promotedBundle.label,
        simulatedBundleLabel: row.simulatedBundleLabel,
        simulatedStatus: row.simulatedStatus,
      })),
      sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
      sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
      templateId: selectedRefTemplate.id,
      templateLabel: selectedRefTemplate.key,
    };
    setPredicateRefReplayApplyHistory((current) => [
      historyEntry,
      ...current,
    ].slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES));
    appendPredicateRefReplayApplySyncAuditEntry({
      at: appliedAt,
      auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
      detail: `${predicateRefReplayApplyHistoryTabIdentity.label} applied ${historyEntry.approvedCount} approved replay rows.`,
      entryId: historyEntry.id,
      kind: "local_apply",
      sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
      sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
      templateId: historyEntry.templateId,
      templateLabel: historyEntry.templateLabel,
    });
    applyPredicateRefGroupPresetBundles(
      selectedRefTemplate.id,
      approvedSimulatedPredicateRefReplayPromotionSelections.map((row) => ({
        bundle: row.promotedBundle,
        group: row.group,
      })),
    );
    setBundleCoordinationSimulationFinalSummaryOpen(false);
    setBundleCoordinationSimulationApprovalOpen(false);
  }, [
    appendPredicateRefReplayApplySyncAuditEntry,
    applyPredicateRefGroupPresetBundles,
    approvedSimulatedPredicateRefReplayPromotionSelections,
    approvedSimulatedPredicateRefReplayPromotionSummary.changesCurrentCount,
    approvedSimulatedPredicateRefReplayPromotionSummary.matchesSimulationCount,
    approvedSimulatedPredicateRefReplayPromotionSummary.total,
    predicateRefDraftBindings,
    predicateRefGroupBundleSelections,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    selectedRefTemplate,
    setBundleCoordinationSimulationApprovalOpen,
    setBundleCoordinationSimulationFinalSummaryOpen,
    setPredicateRefReplayApplyHistory,
  ]);

  useEffect(() => {
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey({});
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey({});
    setBundleCoordinationSimulationApprovalOpen(false);
  }, [
    activeSimulatedPredicateRefSolverReplayIndex,
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationScope,
    selectedRefTemplate?.id,
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey,
    setBundleCoordinationSimulationApprovalOpen,
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey,
  ]);

  useEffect(() => {
    if (
      !bundleCoordinationSimulationApprovalOpen
      || !selectedRefTemplate
      || !approvedSimulatedPredicateRefReplayPromotionSelections.length
    ) {
      setBundleCoordinationSimulationFinalSummaryOpen(false);
    }
  }, [
    approvedSimulatedPredicateRefReplayPromotionSelections,
    bundleCoordinationSimulationApprovalOpen,
    selectedRefTemplate,
    setBundleCoordinationSimulationFinalSummaryOpen,
  ]);

  return {
    applyApprovedReplayDraft,
    approvedSimulatedPredicateRefReplayPromotionSelections,
    approvedSimulatedPredicateRefReplayPromotionSummary,
    canReviewReplayFinalSummary,
    canReviewStagedReplayDraft,
    closeReplayApprovalReview,
    closeReplayFinalSummary,
    openReplayApprovalReview,
    openReplayFinalSummary,
    simulatedPredicateRefReplayPromotionDraft,
    simulatedPredicateRefReplayPromotionPreviewRows,
    stagedSimulatedPredicateRefReplayPromotionSelections,
    toggleReplayApprovalDecision,
    toggleReplayPromotionDecision,
    visibleSimulatedPredicateRefReplayApprovalRows,
  };
}
