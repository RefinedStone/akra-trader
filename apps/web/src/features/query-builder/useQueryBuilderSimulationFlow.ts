import { useCallback, useEffect, useMemo, type Dispatch, type SetStateAction } from "react";
import type {
  PredicateRefReplayApplyConflictDiffItem,
  PredicateRefReplayApplyConflictDraftReview,
  PredicateRefReplayApplyHistoryEntry,
  PredicateRefReplayApplyHistoryTabIdentity,
  PredicateRefReplayApplySyncAuditEntry,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";
import {
  buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId,
  formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel,
  fromRunSurfaceCollectionQueryBindingReferenceValue,
  groupRunSurfaceCollectionQueryBuilderTemplateParameters,
  isRunSurfaceCollectionQueryBindingReferenceValue,
  sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles,
  toRunSurfaceCollectionQueryBindingReferenceValue,
} from "./model";
import { computeCoordinatedPredicateRefGroupBundleStateResult } from "./useQueryBuilderSimulationFlowCompute";

type PredicateTemplateParameterGroups = ReturnType<typeof groupRunSurfaceCollectionQueryBuilderTemplateParameters>;
type CoordinationPolicy = RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"];
type SimulationReplayActionType =
  | "manual_anchor"
  | "dependency_selection"
  | "direct_auto_selection"
  | "conflict_blocked"
  | "idle";
type ClauseReevaluationPreviewSelection = {
  diffItemKey: string | null;
  groupKey: string | null;
  traceKey: string | null;
};

type UseQueryBuilderSimulationFlowArgs = {
  activePredicateRefReplayApplyConflictSimulationReview: PredicateRefReplayApplyConflictDraftReview | null;
  appendPredicateRefReplayApplySyncAuditEntry: (entry: PredicateRefReplayApplySyncAuditEntry) => void;
  bundleCoordinationSimulationPolicy: CoordinationPolicy | "current";
  bundleCoordinationSimulationReplayActionTypeFilter: "all" | SimulationReplayActionType;
  bundleCoordinationSimulationReplayEdgeFilter: string;
  bundleCoordinationSimulationReplayGroupFilter: string;
  bundleCoordinationSimulationReplayIndex: number;
  bundleCoordinationSimulationScope: string;
  clauseReevaluationPreviewSelection: ClauseReevaluationPreviewSelection;
  predicateRefDraftBindings: Record<string, string>;
  predicateRefGroupAutoBundleSelections: Record<string, string>;
  predicateRefGroupBundleSelections: Record<string, string>;
  predicateRefReplayApplyConflictFocusedDecision: { conflictId: string; decisionKey: string } | null;
  predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  selectedRefTemplateParameterGroups: PredicateTemplateParameterGroups;
  setBundleCoordinationSimulationPolicy: (value: CoordinationPolicy | "current") => void;
  setBundleCoordinationSimulationReplayActionTypeFilter: (value: "all" | SimulationReplayActionType) => void;
  setBundleCoordinationSimulationReplayEdgeFilter: (value: string) => void;
  setBundleCoordinationSimulationReplayGroupFilter: (value: string) => void;
  setBundleCoordinationSimulationReplayIndex: (value: number) => void;
  setBundleCoordinationSimulationScope: (value: string) => void;
  setClauseReevaluationPreviewSelection: (value: ClauseReevaluationPreviewSelection) => void;
  setPredicateRefDraftBindings: Dispatch<SetStateAction<Record<string, string>>>;
  setPredicateRefGroupBundleSelections: Dispatch<SetStateAction<Record<string, string>>>;
  setPredicateRefReplayApplyHistory: Dispatch<SetStateAction<PredicateRefReplayApplyHistoryEntry[]>>;
  setTemplateGroupExpansionByKey: Dispatch<SetStateAction<Record<string, boolean>>>;
  templateGroupExpansionByKey: Record<string, boolean>;
};

export function useQueryBuilderSimulationFlow({
  activePredicateRefReplayApplyConflictSimulationReview,
  appendPredicateRefReplayApplySyncAuditEntry,
  bundleCoordinationSimulationPolicy,
  bundleCoordinationSimulationReplayActionTypeFilter,
  bundleCoordinationSimulationReplayEdgeFilter,
  bundleCoordinationSimulationReplayGroupFilter,
  bundleCoordinationSimulationReplayIndex,
  bundleCoordinationSimulationScope,
  clauseReevaluationPreviewSelection,
  predicateRefDraftBindings,
  predicateRefGroupAutoBundleSelections,
  predicateRefGroupBundleSelections,
  predicateRefReplayApplyConflictFocusedDecision,
  predicateRefReplayApplyHistoryTabIdentity,
  selectedRefTemplate,
  selectedRefTemplateParameterGroups,
  setBundleCoordinationSimulationPolicy,
  setBundleCoordinationSimulationReplayActionTypeFilter,
  setBundleCoordinationSimulationReplayEdgeFilter,
  setBundleCoordinationSimulationReplayGroupFilter,
  setBundleCoordinationSimulationReplayIndex,
  setBundleCoordinationSimulationScope,
  setClauseReevaluationPreviewSelection,
  setPredicateRefDraftBindings,
  setPredicateRefGroupBundleSelections,
  setPredicateRefReplayApplyHistory,
  setTemplateGroupExpansionByKey,
  templateGroupExpansionByKey,
}: UseQueryBuilderSimulationFlowArgs) {
  const simulatedCoordinationGroups = useMemo<ReturnType<typeof groupRunSurfaceCollectionQueryBuilderTemplateParameters>>(
    () => selectedRefTemplateParameterGroups.filter((group) => group.presetBundles.length),
    [selectedRefTemplateParameterGroups],
  );
  useEffect(() => {
    if (!simulatedCoordinationGroups.length) {
      setBundleCoordinationSimulationScope("all");
      setBundleCoordinationSimulationPolicy("current");
      return;
    }
    if (
      bundleCoordinationSimulationScope !== "all"
      && !simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationScope)
    ) {
      setBundleCoordinationSimulationScope("all");
    }
  }, [
    bundleCoordinationSimulationScope,
    simulatedCoordinationGroups,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayIndex(0);
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    predicateRefDraftBindings,
    predicateRefGroupBundleSelections,
    predicateRefGroupAutoBundleSelections,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayActionTypeFilter("all");
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    setBundleCoordinationSimulationReplayEdgeFilter("all");
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    selectedRefTemplate?.id,
  ]);
  useEffect(() => {
    if (!simulatedCoordinationGroups.length) {
      setBundleCoordinationSimulationReplayGroupFilter("all");
      return;
    }
    if (
      bundleCoordinationSimulationReplayGroupFilter !== "all"
      && !simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationReplayGroupFilter)
    ) {
      setBundleCoordinationSimulationReplayGroupFilter("all");
    }
  }, [
    bundleCoordinationSimulationReplayGroupFilter,
    simulatedCoordinationGroups,
  ]);
  const getSortedTemplateGroupPresetBundles = useCallback(
    (bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[]) =>
      sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles(bundles),
    [],
  );
  const activePredicateRefReplayApplyConflictSimulationBundleOverrides = useMemo(() => {
    if (!selectedRefTemplate || !activePredicateRefReplayApplyConflictSimulationReview) {
      return {
        bindingOverridesByParameterKey: {} as Record<string, string | null>,
        groupLabelsByKey: {} as Record<string, string>,
        selectionOverridesBySelectionKey: {} as Record<string, string | null>,
      };
    }
    const selectionOverridesBySelectionKey: Record<string, string | null> = {};
    const bindingOverridesByParameterKey: Record<string, string | null> = {};
    const groupLabelsByKey: Record<string, string> = {};
    activePredicateRefReplayApplyConflictSimulationReview.mergedEntry.rows.forEach((row) => {
      const group = selectedRefTemplateParameterGroups.find((candidate) => candidate.key === row.groupKey) ?? null;
      if (!group) {
        return;
      }
      groupLabelsByKey[group.key] = group.label;
      selectionOverridesBySelectionKey[`${selectedRefTemplate.id}:${group.key}`] = row.promotedBundleKey;
      group.parameters.forEach((parameter) => {
        bindingOverridesByParameterKey[parameter.key] = null;
      });
      const bundle =
        getSortedTemplateGroupPresetBundles(group.presetBundles).find(
          (candidate) => candidate.key === row.promotedBundleKey,
        ) ?? null;
      if (!bundle) {
        return;
      }
      group.parameters.forEach((parameter) => {
        const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
        if (bindingPreset) {
          bindingOverridesByParameterKey[parameter.key] =
            toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
          return;
        }
        const parameterValue = bundle.parameterValues[parameter.key];
        if (parameterValue?.trim()) {
          bindingOverridesByParameterKey[parameter.key] = parameterValue;
        }
      });
    });
    return {
      bindingOverridesByParameterKey,
      groupLabelsByKey,
      selectionOverridesBySelectionKey,
    };
  }, [
    activePredicateRefReplayApplyConflictSimulationReview,
    getSortedTemplateGroupPresetBundles,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  ]);
  const activePredicateRefReplayApplyConflictSimulationGroupKeys = useMemo(
    () => Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.groupLabelsByKey),
    [activePredicateRefReplayApplyConflictSimulationBundleOverrides.groupLabelsByKey],
  );
  const activePredicateRefReplayApplyConflictSimulationDiffItems = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationReview
        ? [
            ...activePredicateRefReplayApplyConflictSimulationReview.summaryDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.rowDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.selectionSnapshotDiffs,
            ...activePredicateRefReplayApplyConflictSimulationReview.bindingSnapshotDiffs,
          ]
        : []
    ),
    [activePredicateRefReplayApplyConflictSimulationReview],
  );
  const activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey = useMemo(
    () => Object.fromEntries(
      activePredicateRefReplayApplyConflictSimulationDiffItems.map((item) => [item.decisionKey, item] as const),
    ),
    [activePredicateRefReplayApplyConflictSimulationDiffItems],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedItem = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationReview
      && predicateRefReplayApplyConflictFocusedDecision?.conflictId
        === activePredicateRefReplayApplyConflictSimulationReview.conflict.conflictId
        ? (
            activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey[
              predicateRefReplayApplyConflictFocusedDecision.decisionKey
            ] ?? null
          )
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey,
      activePredicateRefReplayApplyConflictSimulationReview,
      predicateRefReplayApplyConflictFocusedDecision,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFieldPicks = useMemo(() => {
    if (!activePredicateRefReplayApplyConflictSimulationReview) {
      return {
        byGroupKey: {} as Record<string, Array<{
          decisionKey: string;
          key: string;
          label: string;
          section: PredicateRefReplayApplyConflictDiffItem["section"];
          source: "local" | "remote";
        }>>,
        global: [] as Array<{
          decisionKey: string;
          key: string;
          label: string;
          section: PredicateRefReplayApplyConflictDiffItem["section"];
          source: "local" | "remote";
        }>,
      };
    }
    const parameterGroupKeyByParameterKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) =>
        group.parameters.map((parameter) => [parameter.key, group.key] as const)),
    );
    const allItems = [
      ...activePredicateRefReplayApplyConflictSimulationReview.summaryDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.rowDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.selectionSnapshotDiffs,
      ...activePredicateRefReplayApplyConflictSimulationReview.bindingSnapshotDiffs,
    ].filter((item) => item.editable);
    const byGroupKey: Record<string, Array<{
      decisionKey: string;
      key: string;
      label: string;
      section: PredicateRefReplayApplyConflictDiffItem["section"];
      source: "local" | "remote";
    }>> = {};
    const global: Array<{
      decisionKey: string;
      key: string;
      label: string;
      section: PredicateRefReplayApplyConflictDiffItem["section"];
      source: "local" | "remote";
    }> = [];
    allItems.forEach((item) => {
      const source = activePredicateRefReplayApplyConflictSimulationReview.selectedSources[item.decisionKey] ?? "local";
      const relatedGroupKey = item.relatedGroupKey ?? parameterGroupKeyByParameterKey[item.key] ?? null;
      const annotation = {
        decisionKey: item.decisionKey,
        key: item.key,
        label: item.label,
        section: item.section,
        source,
      };
      if (relatedGroupKey) {
        byGroupKey[relatedGroupKey] = [...(byGroupKey[relatedGroupKey] ?? []), annotation];
        return;
      }
      global.push(annotation);
    });
    return {
      byGroupKey,
      global,
    };
  }, [
    activePredicateRefReplayApplyConflictSimulationReview,
    selectedRefTemplateParameterGroups,
  ]);
  const activePredicateRefReplayApplyConflictSimulationFocusedGroupKey = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedItem?.relatedGroupKey
      && simulatedCoordinationGroups.some(
        (group) => group.key === activePredicateRefReplayApplyConflictSimulationFocusedItem.relatedGroupKey,
      )
        ? activePredicateRefReplayApplyConflictSimulationFocusedItem.relatedGroupKey
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedItem,
      simulatedCoordinationGroups,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
      ?? clauseReevaluationPreviewSelection.groupKey
      ?? (
        bundleCoordinationSimulationReplayGroupFilter !== "all"
          ? bundleCoordinationSimulationReplayGroupFilter
          : null
      )
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      bundleCoordinationSimulationReplayGroupFilter,
      clauseReevaluationPreviewSelection.groupKey,
    ],
  );
  const doesTemplateGroupMatchVisibilityRule = useCallback(
    (
      group: {
        visibilityRule: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["visibilityRule"];
        coordinationPolicy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"];
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bindings: Record<string, string>,
    ) => {
      if (group.visibilityRule === "always") {
        return true;
      }
      if (group.visibilityRule === "manual") {
        return false;
      }
      if (group.visibilityRule === "binding_active") {
        return group.parameters.some((parameter) => {
          const currentValue = bindings[parameter.key]?.trim() ?? "";
          return Boolean(fromRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
            || Boolean(parameter.bindingPreset.trim());
        });
      }
      return group.parameters.some((parameter) => {
        const currentValue = bindings[parameter.key]?.trim() ?? "";
        return Boolean(currentValue && !isRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
          || Boolean(parameter.defaultValue.trim());
      });
    },
    [],
  );
  const doesTemplateGroupBundleMatchAutoSelectRule = useCallback(
    (
      group: {
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
      bindings: Record<string, string>,
    ) => {
      if (bundle.autoSelectRule === "manual") {
        return false;
      }
      if (bundle.autoSelectRule === "always") {
        return true;
      }
      if (bundle.autoSelectRule === "binding_active") {
        return group.parameters.some((parameter) => {
          const currentValue = bindings[parameter.key]?.trim() ?? "";
          return Boolean(fromRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
            || Boolean(parameter.bindingPreset.trim())
            || Boolean(bundle.parameterBindingPresets[parameter.key]?.trim());
        });
      }
      return group.parameters.some((parameter) => {
        const currentValue = bindings[parameter.key]?.trim() ?? "";
        return Boolean(currentValue && !isRunSurfaceCollectionQueryBindingReferenceValue(currentValue))
          || Boolean(parameter.defaultValue.trim())
          || Boolean(bundle.parameterValues[parameter.key]?.trim());
      });
    },
    [],
  );
  const isTemplateGroupExpanded = useCallback(
    (viewKey: string, collapsedByDefault: boolean) => (
      templateGroupExpansionByKey[viewKey] ?? !collapsedByDefault
    ),
    [templateGroupExpansionByKey],
  );
  const toggleTemplateGroupExpanded = useCallback((viewKey: string, collapsedByDefault: boolean) => {
    setTemplateGroupExpansionByKey((current) => ({
      ...current,
      [viewKey]: !(current[viewKey] ?? !collapsedByDefault),
    }));
  }, []);
  const applyPredicateRefGroupPresetBundle = useCallback(
    (
      templateId: string,
      group: {
        key: string;
        parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
      },
      bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState | null,
    ) => {
      const selectionKey = `${templateId}:${group.key}`;
      setPredicateRefGroupBundleSelections((current) => ({
        ...current,
        [selectionKey]: bundle?.key ?? "",
      }));
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        group.parameters.forEach((parameter) => {
          delete next[parameter.key];
        });
        if (!bundle) {
          return next;
        }
        group.parameters.forEach((parameter) => {
          const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
          if (bindingPreset) {
            next[parameter.key] = toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
            return;
          }
          const parameterValue = bundle.parameterValues[parameter.key];
          if (parameterValue?.trim()) {
            next[parameter.key] = parameterValue;
          }
        });
        return next;
      });
    },
    [],
  );
  const applyPredicateRefGroupPresetBundles = useCallback(
    (
      templateId: string,
      selections: Array<{
        group: {
          key: string;
          parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
        };
        bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState | null;
      }>,
    ) => {
      if (!selections.length) {
        return;
      }
      setPredicateRefGroupBundleSelections((current) => {
        const next = { ...current };
        selections.forEach(({ group, bundle }) => {
          next[`${templateId}:${group.key}`] = bundle?.key ?? "";
        });
        return next;
      });
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        selections.forEach(({ group, bundle }) => {
          group.parameters.forEach((parameter) => {
            delete next[parameter.key];
          });
          if (!bundle) {
            return;
          }
          group.parameters.forEach((parameter) => {
            const bindingPreset = bundle.parameterBindingPresets[parameter.key]?.trim();
            if (bindingPreset) {
              next[parameter.key] = toRunSurfaceCollectionQueryBindingReferenceValue(bindingPreset);
              return;
            }
            const parameterValue = bundle.parameterValues[parameter.key];
            if (parameterValue?.trim()) {
              next[parameter.key] = parameterValue;
            }
          });
        });
        return next;
      });
    },
    [],
  );
  const restorePredicateRefReplayApplyHistoryEntry = useCallback(
    (entry: PredicateRefReplayApplyHistoryEntry) => {
      setPredicateRefGroupBundleSelections((current) => {
        const next = { ...current };
        Object.entries(entry.rollbackSnapshot.groupSelectionsBySelectionKey).forEach(([selectionKey, bundleKey]) => {
          if (bundleKey?.trim()) {
            next[selectionKey] = bundleKey;
            return;
          }
          delete next[selectionKey];
        });
        return next;
      });
      setPredicateRefDraftBindings((current) => {
        const next = { ...current };
        Object.entries(entry.rollbackSnapshot.draftBindingsByParameterKey).forEach(([parameterKey, value]) => {
          if (value?.trim()) {
            next[parameterKey] = value;
            return;
          }
          delete next[parameterKey];
        });
        return next;
      });
      setPredicateRefReplayApplyHistory((current) =>
        current.map((item) =>
          item.id === entry.id
            ? {
                ...item,
                lastRestoredAt: new Date().toISOString(),
                lastRestoredByTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
                lastRestoredByTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
              }
            : item,
        ),
      );
      appendPredicateRefReplayApplySyncAuditEntry({
        at: new Date().toISOString(),
        auditId: buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId(),
        detail: `${predicateRefReplayApplyHistoryTabIdentity.label} restored the replay snapshot for ${entry.templateLabel}.`,
        entryId: entry.id,
        kind: "local_restore",
        sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        templateId: entry.templateId,
        templateLabel: entry.templateLabel,
      });
    },
    [
      appendPredicateRefReplayApplySyncAuditEntry,
      predicateRefReplayApplyHistoryTabIdentity.label,
      predicateRefReplayApplyHistoryTabIdentity.tabId,
    ],
  );
  const computeCoordinatedPredicateRefGroupBundleState = useCallback((
    overrides: {
      draftBindingOverridesByParameterKey?: Record<string, string | null>;
      manualSelectionOverridesBySelectionKey?: Record<string, string | null>;
      policyOverridesByGroupKey?: Record<
        string,
        RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"]
      >;
    } = {},
  ) => computeCoordinatedPredicateRefGroupBundleStateResult({
    doesTemplateGroupBundleMatchAutoSelectRule,
    getSortedTemplateGroupPresetBundles,
    overrides,
    predicateRefDraftBindings,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  }), [
    doesTemplateGroupBundleMatchAutoSelectRule,
    getSortedTemplateGroupPresetBundles,
    predicateRefDraftBindings,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    selectedRefTemplate,
    selectedRefTemplateParameterGroups,
  ]);
  const coordinatedPredicateRefGroupBundleState = useMemo(
    () => computeCoordinatedPredicateRefGroupBundleState(),
    [computeCoordinatedPredicateRefGroupBundleState],
  );
  const bundleCoordinationSimulationPolicyOverrides = useMemo(() => {
    if (
      bundleCoordinationSimulationPolicy === "current"
      || !simulatedCoordinationGroups.length
    ) {
      return {};
    }
    if (bundleCoordinationSimulationScope === "all") {
      return Object.fromEntries(
        simulatedCoordinationGroups.map((group) => [group.key, bundleCoordinationSimulationPolicy]),
      );
    }
    return simulatedCoordinationGroups.some((group) => group.key === bundleCoordinationSimulationScope)
      ? { [bundleCoordinationSimulationScope]: bundleCoordinationSimulationPolicy }
      : {};
  }, [
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationScope,
    simulatedCoordinationGroups,
  ]);
  const hasActivePredicateRefReplayApplyConflictSimulationOverride = useMemo(
    () => Boolean(
      activePredicateRefReplayApplyConflictSimulationReview
      && (
        Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey).length
        || Object.keys(activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey).length
      )
    ),
    [
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
      activePredicateRefReplayApplyConflictSimulationReview,
    ],
  );
  const simulatedPredicateRefGroupBundleState = useMemo(
    () => (
      Object.keys(bundleCoordinationSimulationPolicyOverrides).length
      || hasActivePredicateRefReplayApplyConflictSimulationOverride
        ? computeCoordinatedPredicateRefGroupBundleState({
            draftBindingOverridesByParameterKey:
              activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
            manualSelectionOverridesBySelectionKey:
              activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
            policyOverridesByGroupKey: bundleCoordinationSimulationPolicyOverrides,
          })
        : null
    ),
    [
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.bindingOverridesByParameterKey,
      activePredicateRefReplayApplyConflictSimulationBundleOverrides.selectionOverridesBySelectionKey,
      bundleCoordinationSimulationPolicyOverrides,
      computeCoordinatedPredicateRefGroupBundleState,
      hasActivePredicateRefReplayApplyConflictSimulationOverride,
    ],
  );
  const simulatedPredicateRefSolverReplay = simulatedPredicateRefGroupBundleState?.solverReplay ?? [];
  const activeSimulatedPredicateRefSolverReplayIndex = simulatedPredicateRefSolverReplay.length
    ? Math.min(bundleCoordinationSimulationReplayIndex, simulatedPredicateRefSolverReplay.length - 1)
    : 0;
  const activeSimulatedPredicateRefSolverReplayStep = simulatedPredicateRefSolverReplay.length
    ? simulatedPredicateRefSolverReplay[activeSimulatedPredicateRefSolverReplayIndex]
    : null;
  const availableSimulatedPredicateRefSolverReplayActionTypes = useMemo(
    () => Array.from(
      new Set(
        simulatedPredicateRefSolverReplay.flatMap((step) => step.actions.map((action) => action.type)),
      ),
    ),
    [simulatedPredicateRefSolverReplay],
  );
  const availableSimulatedPredicateRefSolverReplayEdges = useMemo(
    () => Object.values(
      simulatedPredicateRefSolverReplay.reduce<Record<string, {
        key: string;
        label: string;
        sourceGroupKey: string;
        sourceGroupLabel: string;
        sourceBundleKey: string;
        sourceBundleLabel: string;
        targetGroupKey: string;
        targetGroupLabel: string;
        targetBundleKey: string;
        targetBundleLabel: string;
      }>>((accumulator, step) => {
        step.actions.forEach((action) => {
          action.dependencyEdges.forEach((edge) => {
            accumulator[edge.key] = edge;
          });
        });
        return accumulator;
      }, {}),
    ),
    [simulatedPredicateRefSolverReplay],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredActions = useMemo(
    () => (
      activeSimulatedPredicateRefSolverReplayStep
        ? (
            activeSimulatedPredicateRefSolverReplayStep.actions.filter((action) => {
              if (
                bundleCoordinationSimulationReplayGroupFilter !== "all"
                && action.groupKey !== bundleCoordinationSimulationReplayGroupFilter
              ) {
                return false;
              }
              if (
                bundleCoordinationSimulationReplayActionTypeFilter !== "all"
                && action.type !== bundleCoordinationSimulationReplayActionTypeFilter
              ) {
                return false;
              }
              if (
                bundleCoordinationSimulationReplayEdgeFilter !== "all"
                && !action.dependencyEdges.some((edge) => edge.key === bundleCoordinationSimulationReplayEdgeFilter)
              ) {
                return false;
              }
              return true;
            })
          )
        : []
    ),
    [
      bundleCoordinationSimulationReplayActionTypeFilter,
      bundleCoordinationSimulationReplayEdgeFilter,
      activeSimulatedPredicateRefSolverReplayStep,
      bundleCoordinationSimulationReplayGroupFilter,
    ],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredGroup = useMemo(
    () => (
      bundleCoordinationSimulationReplayGroupFilter === "all"
        ? null
        : simulatedCoordinationGroups.find((group) => group.key === bundleCoordinationSimulationReplayGroupFilter)
          ?? null
    ),
    [
      bundleCoordinationSimulationReplayGroupFilter,
      simulatedCoordinationGroups,
    ],
  );
  const activeSimulatedPredicateRefSolverReplayFilteredEdge = useMemo(
    () => (
      bundleCoordinationSimulationReplayEdgeFilter === "all"
        ? null
        : availableSimulatedPredicateRefSolverReplayEdges.find((edge) => edge.key === bundleCoordinationSimulationReplayEdgeFilter)
          ?? null
    ),
    [
      availableSimulatedPredicateRefSolverReplayEdges,
      bundleCoordinationSimulationReplayEdgeFilter,
    ],
  );
  const simulatedPredicateRefSolverReplayAttributionByGroupKey = useMemo(
    () => Object.fromEntries(
      simulatedCoordinationGroups.map((group) => {
        const selectedRefTemplateKey = selectedRefTemplate?.key ?? "template";
        const findGroupBundle = (groupKey: string, bundleKey: string) => {
          const targetGroup = simulatedCoordinationGroups.find((candidate) => candidate.key === groupKey);
          return targetGroup?.presetBundles.find((bundle) => bundle.key === bundleKey) ?? null;
        };
        const formatResolvedBundleLabel = (bundleKey: string) => {
          if (!bundleKey) {
            return "Unresolved";
          }
          return (
            getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) => bundle.key === bundleKey)?.label
            ?? bundleKey
          );
        };
        const buildEdgeRoleLabel = (
          edges: Array<{
            key: string;
            label: string;
            sourceGroupKey: string;
            targetGroupKey: string;
          }>,
        ) => {
          const hasSourceEdge = edges.some((edge) => edge.sourceGroupKey === group.key);
          const hasTargetEdge = edges.some((edge) => edge.targetGroupKey === group.key);
          if (hasSourceEdge && hasTargetEdge) {
            return "Bridge edge";
          }
          if (hasSourceEdge) {
            return "Outbound dependency edge";
          }
          if (hasTargetEdge) {
            return "Inbound dependency edge";
          }
          return "Related dependency edge";
        };
        const buildDependencySourceLocation = (
          edge: {
            sourceGroupKey: string;
            sourceBundleKey: string;
            targetGroupKey: string;
            targetBundleKey: string;
          },
        ) => {
          const sourceBundle = findGroupBundle(edge.sourceGroupKey, edge.sourceBundleKey);
          const dependencyIndex = sourceBundle?.dependencies.findIndex(
            (dependency) =>
              dependency.groupKey === edge.targetGroupKey && dependency.bundleKey === edge.targetBundleKey,
          ) ?? -1;
          return dependencyIndex >= 0
            ? `${selectedRefTemplateKey}.parameter_groups.${edge.sourceGroupKey}.preset_bundles.${edge.sourceBundleKey}.dependencies[${dependencyIndex}]`
            : `${selectedRefTemplateKey}.parameter_groups.${edge.sourceGroupKey}.preset_bundles.${edge.sourceBundleKey}.dependencies`;
        };
        let previousBundleKey = "";
        const chain: Array<{
          causalLabel: string;
          detail: string;
          edgeLabels: string[];
          edgeSourceLocations: string[];
          edgeRoleLabel: string | null;
          kind: "selection_change" | "group_action" | "dependency_edge";
          stateTransitionLabel: string | null;
          stepIndex: number;
          stepLabel: string;
          type: string | null;
        }> = [];
        for (let stepIndex = 0; stepIndex < simulatedPredicateRefSolverReplay.length; stepIndex += 1) {
          const step = simulatedPredicateRefSolverReplay[stepIndex];
          const resolvedBundleKey = step.resolvedSelectionsByGroupKey[group.key] ?? "";
          const matchingActions = step.actions.filter((action) =>
            action.groupKey === group.key
            || action.dependencyEdges.some((edge) =>
              edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key));
          const directAction = matchingActions.find((action) => action.groupKey === group.key);
          const edgeAction = matchingActions.find((action) =>
            action.dependencyEdges.some((edge) =>
              edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key));
          const relatedEdges = (directAction ?? edgeAction)?.dependencyEdges.filter((edge) =>
            edge.sourceGroupKey === group.key || edge.targetGroupKey === group.key) ?? [];
          const edgeRoleLabel = relatedEdges.length ? buildEdgeRoleLabel(relatedEdges) : null;
          const selectionChanged = resolvedBundleKey !== previousBundleKey;
          if (selectionChanged) {
            const previousBundleLabel = formatResolvedBundleLabel(previousBundleKey);
            const nextBundleLabel = formatResolvedBundleLabel(resolvedBundleKey);
            chain.push({
              causalLabel: "State transition",
              detail: resolvedBundleKey
                ? `${group.label} switched from ${previousBundleLabel} to ${nextBundleLabel} during ${step.title.toLowerCase()}.`
                : `${group.label} became unresolved during ${step.title.toLowerCase()}.`,
              edgeLabels: relatedEdges.map((edge) => edge.label),
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "selection_change",
              stateTransitionLabel: `${previousBundleLabel} -> ${nextBundleLabel}`,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: directAction?.type ?? edgeAction?.type ?? null,
            });
          } else if (directAction) {
            chain.push({
              causalLabel: edgeRoleLabel ? `${edgeRoleLabel} action` : "Group action",
              detail: directAction.detail,
              edgeLabels: relatedEdges.map((edge) => edge.label),
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "group_action",
              stateTransitionLabel: null,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: directAction.type,
            });
          } else if (edgeAction) {
            const edgeLabels = relatedEdges.map((edge) => edge.label);
            chain.push({
              causalLabel: edgeRoleLabel ?? "Dependency edge",
              detail: edgeLabels.length
                ? `${group.label} participates in ${edgeLabels.join(", ")} during ${step.title.toLowerCase()}.`
                : edgeAction.detail,
              edgeLabels,
              edgeSourceLocations: relatedEdges.map((edge) => buildDependencySourceLocation(edge)),
              edgeRoleLabel,
              kind: "dependency_edge",
              stateTransitionLabel: null,
              stepIndex,
              stepLabel: `Replay step ${stepIndex + 1}`,
              type: edgeAction.type,
            });
          }
          previousBundleKey = resolvedBundleKey;
        }
        const firstAttribution = chain[0] ?? null;
        return [group.key, {
          chain,
          chainSummary:
            chain.length > 1
              ? `${chain.length} replay steps · ${chain[0]?.causalLabel ?? chain[0]?.stepLabel ?? "Replay"} → ${chain[chain.length - 1]?.causalLabel ?? chain[chain.length - 1]?.stepLabel ?? "Replay"}`
              : chain.length === 1
                ? `1 replay step · ${chain[0]?.causalLabel ?? chain[0]?.stepLabel ?? "Replay"}`
                : "No replay attribution",
          detail: firstAttribution?.detail ?? null,
          stepIndex: firstAttribution?.stepIndex ?? -1,
          stepLabel: firstAttribution?.stepLabel ?? "No replay attribution",
          type: firstAttribution?.type ?? null,
        }] as const;
      }),
    ),
    [
      getSortedTemplateGroupPresetBundles,
      selectedRefTemplate,
      simulatedCoordinationGroups,
      simulatedPredicateRefSolverReplay,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChain = useMemo(
    () => (
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
        ? (
            simulatedPredicateRefSolverReplayAttributionByGroupKey[
              activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
            ]?.chain ?? []
          )
        : []
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      simulatedPredicateRefSolverReplayAttributionByGroupKey,
    ],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet = useMemo(
    () => new Set(
      activePredicateRefReplayApplyConflictSimulationFocusedChain.map((entry) => entry.stepIndex),
    ),
    [activePredicateRefReplayApplyConflictSimulationFocusedChain],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedChainPosition = useMemo(
    () => activePredicateRefReplayApplyConflictSimulationFocusedChain.findIndex(
      (entry) => entry.stepIndex === activeSimulatedPredicateRefSolverReplayIndex,
    ),
    [
      activePredicateRefReplayApplyConflictSimulationFocusedChain,
      activeSimulatedPredicateRefSolverReplayIndex,
    ],
  );
  const selectedRefTemplateParameterGroupByKey = useMemo(
    () => Object.fromEntries(
      selectedRefTemplateParameterGroups.map((group) => [group.key, group] as const),
    ),
    [selectedRefTemplateParameterGroups],
  );
  const activePredicateRefReplayApplyConflictSimulationFocusedParameter = useMemo(
    () => {
      if (
        !activePredicateRefReplayApplyConflictSimulationFocusedItem
        || activePredicateRefReplayApplyConflictSimulationFocusedItem.section !== "binding_snapshot"
      ) {
        return null;
      }
      const parameterGroup =
        activePredicateRefReplayApplyConflictSimulationFocusedGroupKey
          ? selectedRefTemplateParameterGroupByKey[activePredicateRefReplayApplyConflictSimulationFocusedGroupKey] ?? null
          : null;
      return parameterGroup?.parameters.find(
        (parameter) => parameter.key === activePredicateRefReplayApplyConflictSimulationFocusedItem.key,
      ) ?? null;
    },
    [
      activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
      activePredicateRefReplayApplyConflictSimulationFocusedItem,
      selectedRefTemplateParameterGroupByKey,
    ],
  );

  return {
    activePredicateRefReplayApplyConflictSimulationBundleOverrides,
    activePredicateRefReplayApplyConflictSimulationDiffItemByDecisionKey,
    activePredicateRefReplayApplyConflictSimulationDiffItems,
    activePredicateRefReplayApplyConflictSimulationFieldPicks,
    activePredicateRefReplayApplyConflictSimulationFocusedChain,
    activePredicateRefReplayApplyConflictSimulationFocusedChainPosition,
    activePredicateRefReplayApplyConflictSimulationFocusedChainStepIndexSet,
    activePredicateRefReplayApplyConflictSimulationFocusedGroupKey,
    activePredicateRefReplayApplyConflictSimulationFocusedItem,
    activePredicateRefReplayApplyConflictSimulationFocusedParameter,
    activePredicateRefReplayApplyConflictSimulationGroupKeys,
    activePredicateRefReplayApplyConflictSimulationPrimaryFocusGroupKey,
    activeSimulatedPredicateRefSolverReplayFilteredActions,
    activeSimulatedPredicateRefSolverReplayFilteredEdge,
    activeSimulatedPredicateRefSolverReplayFilteredGroup,
    activeSimulatedPredicateRefSolverReplayIndex,
    activeSimulatedPredicateRefSolverReplayStep,
    applyPredicateRefGroupPresetBundle,
    applyPredicateRefGroupPresetBundles,
    availableSimulatedPredicateRefSolverReplayActionTypes,
    availableSimulatedPredicateRefSolverReplayEdges,
    bundleCoordinationSimulationPolicyOverrides,
    coordinatedPredicateRefGroupBundleState,
    doesTemplateGroupBundleMatchAutoSelectRule,
    doesTemplateGroupMatchVisibilityRule,
    getSortedTemplateGroupPresetBundles,
    hasActivePredicateRefReplayApplyConflictSimulationOverride,
    isTemplateGroupExpanded,
    restorePredicateRefReplayApplyHistoryEntry,
    selectedRefTemplateParameterGroupByKey,
    simulatedCoordinationGroups,
    simulatedPredicateRefGroupBundleState,
    simulatedPredicateRefSolverReplay,
    simulatedPredicateRefSolverReplayAttributionByGroupKey,
    toggleTemplateGroupExpanded,
  };
}
