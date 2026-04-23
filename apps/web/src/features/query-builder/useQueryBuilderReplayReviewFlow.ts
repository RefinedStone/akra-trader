import {
  useCallback,
  useEffect,
  useMemo,
  type Dispatch,
  type MutableRefObject,
  type SetStateAction,
} from "react";

import {
  buildPredicateRefReplayApplyConflictMergedEntry,
  buildPredicateRefReplayApplyConflictResolutionPreview,
  buildPredicateRefReplayApplyConflictReview,
  buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId,
  mergePredicateRefReplayApplyHistoryEntries,
  mergePredicateRefReplayApplySyncAuditEntries,
} from "./model";
import type {
  PredicateRefReplayApplyConflictDraftReview,
  PredicateRefReplayApplyConflictEntry,
  PredicateRefReplayApplyHistoryEntry,
  PredicateRefReplayApplyHistoryTabIdentity,
  PredicateRefReplayApplySyncAuditEntry,
  PredicateRefReplayApplySyncAuditFilter,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";

type ReplayConflictFocusedDecision = { conflictId: string; decisionKey: string } | null;

type UseQueryBuilderReplayReviewFlowArgs = {
  predicateRefReplayApplyConflictDraftSourcesById: Record<string, Record<string, "local" | "remote">>;
  predicateRefReplayApplyConflictFocusedDecision: ReplayConflictFocusedDecision;
  predicateRefReplayApplyConflictSimulationConflictId: string | null;
  predicateRefReplayApplyConflicts: PredicateRefReplayApplyConflictEntry[];
  predicateRefReplayApplyHistory: PredicateRefReplayApplyHistoryEntry[];
  predicateRefReplayApplyHistoryRef: MutableRefObject<PredicateRefReplayApplyHistoryEntry[]>;
  predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
  predicateRefReplayApplySyncAuditFilter: PredicateRefReplayApplySyncAuditFilter;
  predicateRefReplayApplySyncAuditTrail: PredicateRefReplayApplySyncAuditEntry[];
  predicateRefReplayApplyConflictRowRefs: MutableRefObject<Record<string, HTMLDivElement | null>>;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  selectedRefTemplateParameterGroups: Array<
    RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState & {
      parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
    }
  >;
  setPredicateRefReplayApplyConflictDraftSourcesById: Dispatch<
    SetStateAction<Record<string, Record<string, "local" | "remote">>>
  >;
  setPredicateRefReplayApplyConflictFocusedDecision: Dispatch<SetStateAction<ReplayConflictFocusedDecision>>;
  setPredicateRefReplayApplyConflicts: Dispatch<SetStateAction<PredicateRefReplayApplyConflictEntry[]>>;
  setPredicateRefReplayApplyHistory: Dispatch<SetStateAction<PredicateRefReplayApplyHistoryEntry[]>>;
  setPredicateRefReplayApplySyncAuditTrail: Dispatch<SetStateAction<PredicateRefReplayApplySyncAuditEntry[]>>;
};

export function useQueryBuilderReplayReviewFlow({
  predicateRefReplayApplyConflictDraftSourcesById,
  predicateRefReplayApplyConflictFocusedDecision,
  predicateRefReplayApplyConflictSimulationConflictId,
  predicateRefReplayApplyConflicts,
  predicateRefReplayApplyHistory,
  predicateRefReplayApplyHistoryRef,
  predicateRefReplayApplyHistoryTabIdentity,
  predicateRefReplayApplySyncAuditFilter,
  predicateRefReplayApplySyncAuditTrail,
  predicateRefReplayApplyConflictRowRefs,
  selectedRefTemplate,
  selectedRefTemplateParameterGroups,
  setPredicateRefReplayApplyConflictDraftSourcesById,
  setPredicateRefReplayApplyConflictFocusedDecision,
  setPredicateRefReplayApplyConflicts,
  setPredicateRefReplayApplyHistory,
  setPredicateRefReplayApplySyncAuditTrail,
}: UseQueryBuilderReplayReviewFlowArgs) {
  const selectedRefTemplateReplayApplyHistory = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplyHistory.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : []
    ),
    [predicateRefReplayApplyHistory, selectedRefTemplate],
  );
  const latestSelectedRefTemplateReplayApplyEntry = useMemo(
    () => selectedRefTemplateReplayApplyHistory[0] ?? null,
    [selectedRefTemplateReplayApplyHistory],
  );
  const selectedRefTemplateReplayApplySyncAuditTrail = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplySyncAuditTrail.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : predicateRefReplayApplySyncAuditTrail
    ),
    [predicateRefReplayApplySyncAuditTrail, selectedRefTemplate],
  );
  const visibleSelectedRefTemplateReplayApplySyncAuditTrail = useMemo(
    () => selectedRefTemplateReplayApplySyncAuditTrail.filter((entry) => {
      if (predicateRefReplayApplySyncAuditFilter === "local") {
        return entry.sourceTabId === predicateRefReplayApplyHistoryTabIdentity.tabId;
      }
      if (predicateRefReplayApplySyncAuditFilter === "remote") {
        return entry.sourceTabId !== predicateRefReplayApplyHistoryTabIdentity.tabId;
      }
      if (predicateRefReplayApplySyncAuditFilter === "apply") {
        return entry.kind.endsWith("_apply");
      }
      if (predicateRefReplayApplySyncAuditFilter === "restore") {
        return entry.kind.endsWith("_restore");
      }
      if (predicateRefReplayApplySyncAuditFilter === "conflict") {
        return entry.kind.includes("conflict");
      }
      return true;
    }),
    [
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      predicateRefReplayApplySyncAuditFilter,
      selectedRefTemplateReplayApplySyncAuditTrail,
    ],
  );
  const selectedRefTemplateReplayApplyConflicts = useMemo(
    () => (
      selectedRefTemplate
        ? predicateRefReplayApplyConflicts.filter((entry) => entry.templateId === selectedRefTemplate.id)
        : predicateRefReplayApplyConflicts
    ),
    [predicateRefReplayApplyConflicts, selectedRefTemplate],
  );
  const selectedRefTemplateReplayApplyConflictReviews = useMemo<PredicateRefReplayApplyConflictDraftReview[]>(
    () => {
      const parameterGroupKeyByParameterKey = Object.fromEntries(
        selectedRefTemplateParameterGroups.flatMap((group) =>
          group.parameters.map((parameter) => [parameter.key, group.key] as const)),
      );
      return selectedRefTemplateReplayApplyConflicts.map((conflict) => {
        const review = buildPredicateRefReplayApplyConflictReview(
          conflict,
          predicateRefReplayApplyHistoryTabIdentity.label,
          parameterGroupKeyByParameterKey,
        );
        const editableItems = [
          ...review.summaryDiffs,
          ...review.rowDiffs,
          ...review.selectionSnapshotDiffs,
          ...review.bindingSnapshotDiffs,
        ].filter((item) => item.editable);
        const storedDraftSources = predicateRefReplayApplyConflictDraftSourcesById[conflict.conflictId] ?? {};
        const selectedSources = Object.fromEntries(
          editableItems.map((item) => [item.decisionKey, storedDraftSources[item.decisionKey] ?? "local"]),
        ) as Record<string, "local" | "remote">;
        const mergedEntry = buildPredicateRefReplayApplyConflictMergedEntry(conflict, selectedSources);
        const selectedRemoteCount = Object.values(selectedSources).filter((source) => source === "remote").length;
        const hasRemoteSelection = selectedRemoteCount > 0;
        const hasMixedSelection = hasRemoteSelection && selectedRemoteCount < editableItems.length;
        const mergedPreview = buildPredicateRefReplayApplyConflictResolutionPreview(
          conflict,
          mergedEntry,
          "merged",
          hasRemoteSelection
            ? hasMixedSelection
              ? `Applies a partial reviewed merge with ${selectedRemoteCount} remote field selections and ${editableItems.length - selectedRemoteCount} local field selections.`
              : `Applies the fully reviewed remote version across all ${editableItems.length} editable field differences.`
            : "Keeps the local version because no remote field selections are currently staged.",
        );
        return {
          ...review,
          editableDiffCount: editableItems.length,
          hasMixedSelection,
          hasRemoteSelection,
          mergedEntry,
          mergedPreview,
          selectedRemoteCount,
          selectedSources,
        };
      });
    },
    [
      predicateRefReplayApplyConflictDraftSourcesById,
      predicateRefReplayApplyHistoryTabIdentity.label,
      selectedRefTemplateParameterGroups,
      selectedRefTemplateReplayApplyConflicts,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationReview = useMemo(
    () => (
      predicateRefReplayApplyConflictSimulationConflictId
        ? selectedRefTemplateReplayApplyConflictReviews.find(
            (review) => review.conflict.conflictId === predicateRefReplayApplyConflictSimulationConflictId,
          ) ?? null
        : null
    ),
    [
      predicateRefReplayApplyConflictSimulationConflictId,
      selectedRefTemplateReplayApplyConflictReviews,
    ],
  );
  const appendPredicateRefReplayApplySyncAuditEntry = useCallback(
    (entry: PredicateRefReplayApplySyncAuditEntry) => {
      setPredicateRefReplayApplySyncAuditTrail((current) =>
        mergePredicateRefReplayApplySyncAuditEntries(current, [entry]),
      );
    },
    [setPredicateRefReplayApplySyncAuditTrail],
  );
  const setPredicateRefReplayApplyConflictDraftSource = useCallback(
    (
      conflictId: string,
      decisionKey: string,
      source: "local" | "remote",
    ) => {
      setPredicateRefReplayApplyConflictDraftSourcesById((current) => ({
        ...current,
        [conflictId]: {
          ...(current[conflictId] ?? {}),
          [decisionKey]: source,
        },
      }));
    },
    [setPredicateRefReplayApplyConflictDraftSourcesById],
  );
  const setPredicateRefReplayApplyConflictFocusedDecisionState = useCallback(
    (conflictId: string, decisionKey: string) => {
      setPredicateRefReplayApplyConflictFocusedDecision({ conflictId, decisionKey });
    },
    [setPredicateRefReplayApplyConflictFocusedDecision],
  );
  const resetPredicateRefReplayApplyConflictDraftSource = useCallback((conflictId: string) => {
    setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
      if (!current[conflictId]) {
        return current;
      }
      const next = { ...current };
      delete next[conflictId];
      return next;
    });
  }, [setPredicateRefReplayApplyConflictDraftSourcesById]);
  const setPredicateRefReplayApplyConflictRowRef = useCallback(
    (conflictId: string, decisionKey: string, node: HTMLDivElement | null) => {
      predicateRefReplayApplyConflictRowRefs.current[`${conflictId}:${decisionKey}`] = node;
    },
    [predicateRefReplayApplyConflictRowRefs],
  );
  const focusPredicateRefReplayApplyConflictDecision = useCallback(
    (conflictId: string, decisionKey: string) => {
      setPredicateRefReplayApplyConflictFocusedDecisionState(conflictId, decisionKey);
      const refKey = `${conflictId}:${decisionKey}`;
      requestAnimationFrame(() => {
        const node = predicateRefReplayApplyConflictRowRefs.current[refKey];
        if (!node) {
          return;
        }
        node.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
        node.focus({
          preventScroll: true,
        });
      });
    },
    [
      predicateRefReplayApplyConflictRowRefs,
      setPredicateRefReplayApplyConflictFocusedDecisionState,
    ],
  );
  const togglePredicateRefReplayApplyConflictSimulationFieldPickSource = useCallback(
    (decisionKey: string) => {
      if (!activePredicateRefReplayApplyConflictSimulationReview) {
        return;
      }
      setPredicateRefReplayApplyConflictFocusedDecisionState(
        activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
        decisionKey,
      );
      const currentSource =
        activePredicateRefReplayApplyConflictSimulationReview.selectedSources[decisionKey] ?? "local";
      setPredicateRefReplayApplyConflictDraftSource(
        activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId,
        decisionKey,
        currentSource === "remote" ? "local" : "remote",
      );
    },
    [
      activePredicateRefReplayApplyConflictSimulationReview,
      setPredicateRefReplayApplyConflictDraftSource,
      setPredicateRefReplayApplyConflictFocusedDecisionState,
    ],
  );
  const resolvePredicateRefReplayApplyConflict = useCallback(
    (
      conflict: PredicateRefReplayApplyConflictEntry,
      resolution: "local" | "remote" | "merged",
      mergedEntry?: PredicateRefReplayApplyHistoryEntry | null,
    ) => {
      if (resolution !== "local") {
        const nextEntry = resolution === "remote" ? conflict.remoteEntry : mergedEntry ?? conflict.localEntry;
        setPredicateRefReplayApplyHistory((current) => {
          const next = mergePredicateRefReplayApplyHistoryEntries(
            current.filter((entry) => entry.id !== conflict.entryId),
            [nextEntry],
          );
          predicateRefReplayApplyHistoryRef.current = next;
          return next;
        });
      }
      setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
        if (!current[conflict.conflictId]) {
          return current;
        }
        const next = { ...current };
        delete next[conflict.conflictId];
        return next;
      });
      setPredicateRefReplayApplyConflicts((current) =>
        current.filter((entry) => entry.conflictId !== conflict.conflictId),
      );
      appendPredicateRefReplayApplySyncAuditEntry({
        at: new Date().toISOString(),
        auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
        detail:
          resolution === "remote"
            ? `${predicateRefReplayApplyHistoryTabIdentity.label} accepted the remote replay history override from ${conflict.sourceTabLabel}.`
            : resolution === "merged"
              ? `${predicateRefReplayApplyHistoryTabIdentity.label} applied a reviewed replay history merge against ${conflict.sourceTabLabel}.`
              : `${predicateRefReplayApplyHistoryTabIdentity.label} kept the local replay history version over ${conflict.sourceTabLabel}.`,
        entryId: conflict.entryId,
        kind: "conflict_resolved",
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        templateId: conflict.templateId,
        templateLabel: conflict.templateLabel,
      });
    },
    [
      appendPredicateRefReplayApplySyncAuditEntry,
      predicateRefReplayApplyHistoryRef,
      predicateRefReplayApplyHistoryTabIdentity.label,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
      setPredicateRefReplayApplyConflictDraftSourcesById,
      setPredicateRefReplayApplyConflicts,
      setPredicateRefReplayApplyHistory,
    ],
  );

  useEffect(() => {
    setPredicateRefReplayApplyConflictDraftSourcesById((current) => {
      const activeConflictIds = new Set(predicateRefReplayApplyConflicts.map((entry) => entry.conflictId));
      let changed = false;
      const next = Object.fromEntries(
        Object.entries(current).filter(([conflictId]) => {
          const keep = activeConflictIds.has(conflictId);
          if (!keep) {
            changed = true;
          }
          return keep;
        }),
      );
      return changed ? next : current;
    });
  }, [predicateRefReplayApplyConflicts, setPredicateRefReplayApplyConflictDraftSourcesById]);

  useEffect(() => {
    if (!predicateRefReplayApplyConflictFocusedDecision) {
      return;
    }
    const stillExists = selectedRefTemplateReplayApplyConflictReviews.some((review) =>
      review.conflict.conflictId === predicateRefReplayApplyConflictFocusedDecision.conflictId
      && [
        ...review.summaryDiffs,
        ...review.rowDiffs,
        ...review.selectionSnapshotDiffs,
        ...review.bindingSnapshotDiffs,
      ].some((item) => item.decisionKey === predicateRefReplayApplyConflictFocusedDecision.decisionKey));
    if (!stillExists) {
      setPredicateRefReplayApplyConflictFocusedDecision(null);
    }
  }, [
    predicateRefReplayApplyConflictFocusedDecision,
    selectedRefTemplateReplayApplyConflictReviews,
    setPredicateRefReplayApplyConflictFocusedDecision,
  ]);

  return {
    activePredicateRefReplayApplyConflictSimulationReview,
    appendPredicateRefReplayApplySyncAuditEntry,
    focusPredicateRefReplayApplyConflictDecision,
    latestSelectedRefTemplateReplayApplyEntry,
    resetPredicateRefReplayApplyConflictDraftSource,
    resolvePredicateRefReplayApplyConflict,
    selectedRefTemplateReplayApplyConflictReviews,
    selectedRefTemplateReplayApplyConflicts,
    selectedRefTemplateReplayApplyHistory,
    selectedRefTemplateReplayApplySyncAuditTrail,
    setPredicateRefReplayApplyConflictDraftSource,
    setPredicateRefReplayApplyConflictFocusedDecisionState,
    setPredicateRefReplayApplyConflictRowRef,
    togglePredicateRefReplayApplyConflictSimulationFieldPickSource,
    visibleSelectedRefTemplateReplayApplySyncAuditTrail,
  };
}
