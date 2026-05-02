import type {
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";
import {
  formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel,
  fromRunSurfaceCollectionQueryBindingReferenceValue,
  isRunSurfaceCollectionQueryBindingReferenceValue,
} from "./model";

type PredicateTemplateParameterGroups = ReturnType<
  typeof import("./model").groupRunSurfaceCollectionQueryBuilderTemplateParameters
>;
type CoordinationPolicy = RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"];

type ComputeCoordinatedPredicateRefGroupBundleStateArgs = {
  doesTemplateGroupBundleMatchAutoSelectRule: (
    group: { parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[] },
    bundle: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
    bindings: Record<string, string>,
  ) => boolean;
  getSortedTemplateGroupPresetBundles: (
    bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[],
  ) => RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
  overrides?: {
    draftBindingOverridesByParameterKey?: Record<string, string | null>;
    manualSelectionOverridesBySelectionKey?: Record<string, string | null>;
    policyOverridesByGroupKey?: Record<string, CoordinationPolicy>;
  };
  predicateRefDraftBindings: Record<string, string>;
  predicateRefGroupAutoBundleSelections: Record<string, string>;
  predicateRefGroupBundleSelections: Record<string, string>;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  selectedRefTemplateParameterGroups: PredicateTemplateParameterGroups;
};

export function computeCoordinatedPredicateRefGroupBundleStateResult({
  doesTemplateGroupBundleMatchAutoSelectRule,
  getSortedTemplateGroupPresetBundles,
  overrides = {},
  predicateRefDraftBindings,
  predicateRefGroupAutoBundleSelections,
  predicateRefGroupBundleSelections,
  selectedRefTemplate,
  selectedRefTemplateParameterGroups,
}: ComputeCoordinatedPredicateRefGroupBundleStateArgs) {
    const policyOverridesByGroupKey = overrides.policyOverridesByGroupKey ?? {};
    type AggregatedDependencyRequest = {
      bundleKey: string;
      bundleLabel: string;
      targetPriority: number;
      hasManualSource: boolean;
      maxSourcePriority: number;
      sourceLabels: string[];
    };
    type PolicyTraceStep = {
      key: string;
      title: string;
      detail: string;
      tone: "info" | "success" | "warning" | "muted";
    };
    type PolicyTrace = {
      summary: string;
      statusLabel: string;
      tone: PolicyTraceStep["tone"];
      steps: PolicyTraceStep[];
    };
    type GlobalPolicyTrace = PolicyTrace & {
      counts: {
        groupCount: number;
        manualCount: number;
        autoCount: number;
        blockedCount: number;
        conflictCount: number;
        dependencyRequestCount: number;
        unmetDependencyCount: number;
      };
    };
    type SolverReplayAction = {
      dependencyEdges: Array<{
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
      }>;
      groupKey: string;
      groupLabel: string;
      type: "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle";
      detail: string;
    };
    type SolverReplayStep = {
      key: string;
      title: string;
      summary: string;
      actions: SolverReplayAction[];
      resolvedSelectionsByGroupKey: Record<string, string>;
      autoSelectionsByGroupKey: Record<string, string>;
    };
    if (!selectedRefTemplate) {
      return {
        autoSelectionsBySelectionKey: {} as Record<string, string>,
        resolvedSelectionsByGroupKey: {} as Record<string, string>,
        dependencyRequestsByGroupKey: {} as Record<string, Array<{
          bundleKey: string;
          sourceGroupKey: string;
          sourceGroupLabel: string;
          sourceBundleKey: string;
          sourceBundleLabel: string;
          sourcePriority: number;
          manualSource: boolean;
        }>>,
        unmetDependenciesByGroupKey: {} as Record<string, Array<{
          key: string;
          groupKey: string;
          groupLabel: string;
          bundleKey: string;
          bundleLabel: string;
        }>>,
        conflictRequestsByGroupKey: {} as Record<string, Array<{
          bundleKey: string;
          bundleLabel: string;
          targetPriority: number;
          hasManualSource: boolean;
          maxSourcePriority: number;
          sourceLabels: string[];
        }>>,
        policyTraceByGroupKey: {} as Record<string, PolicyTrace>,
        globalPolicyTrace: {
          summary: "No predicate template is selected.",
          statusLabel: "Idle",
          tone: "muted" as const,
          steps: [],
          counts: {
            groupCount: 0,
            manualCount: 0,
            autoCount: 0,
            blockedCount: 0,
            conflictCount: 0,
            dependencyRequestCount: 0,
            unmetDependencyCount: 0,
          },
        } as GlobalPolicyTrace,
        solverReplay: [] as SolverReplayStep[],
      };
    }
    type DependencyRequest = {
      bundleKey: string;
      bundleLabel: string;
      targetPriority: number;
      sourceGroupKey: string;
      sourceGroupLabel: string;
      sourceBundleKey: string;
      sourceBundleLabel: string;
      sourcePriority: number;
      manualSource: boolean;
    };
    const groupMap = new Map(
      selectedRefTemplateParameterGroups.map((group) => [group.key, group] as const),
    );
    const effectiveDraftBindings = { ...predicateRefDraftBindings };
    Object.entries(overrides.draftBindingOverridesByParameterKey ?? {}).forEach(([parameterKey, value]) => {
      if (value?.trim()) {
        effectiveDraftBindings[parameterKey] = value;
        return;
      }
      delete effectiveDraftBindings[parameterKey];
    });
    const effectiveManualSelectionsBySelectionKey = { ...predicateRefGroupBundleSelections };
    Object.entries(overrides.manualSelectionOverridesBySelectionKey ?? {}).forEach(([selectionKey, bundleKey]) => {
      if (bundleKey?.trim()) {
        effectiveManualSelectionsBySelectionKey[selectionKey] = bundleKey;
        return;
      }
      delete effectiveManualSelectionsBySelectionKey[selectionKey];
    });
    const getGroupBundle = (
      groupKey: string,
      bundleKey: string,
    ) =>
      getSortedTemplateGroupPresetBundles(groupMap.get(groupKey)?.presetBundles ?? []).find(
        (bundle) => bundle.key === bundleKey,
      ) ?? null;
    const getCoordinationPolicy = (
      group: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
    ) => policyOverridesByGroupKey[group.key] ?? group.coordinationPolicy;
    const buildDependencyEdges = (
      requests: DependencyRequest[],
      targetGroupKey: string,
    ) => Object.values(
      requests.reduce<Record<string, SolverReplayAction["dependencyEdges"][number]>>((accumulator, request) => {
        const targetGroup = groupMap.get(targetGroupKey);
        const edgeKey = `${request.sourceGroupKey}:${request.sourceBundleKey}->${targetGroupKey}:${request.bundleKey}`;
        if (accumulator[edgeKey]) {
          return accumulator;
        }
        accumulator[edgeKey] = {
          key: edgeKey,
          label: `${request.sourceGroupLabel} → ${request.sourceBundleLabel} => ${targetGroup?.label ?? targetGroupKey} → ${request.bundleLabel}`,
          sourceGroupKey: request.sourceGroupKey,
          sourceGroupLabel: request.sourceGroupLabel,
          sourceBundleKey: request.sourceBundleKey,
          sourceBundleLabel: request.sourceBundleLabel,
          targetGroupKey,
          targetGroupLabel: targetGroup?.label ?? targetGroupKey,
          targetBundleKey: request.bundleKey,
          targetBundleLabel: request.bundleLabel,
        };
        return accumulator;
      }, {}),
    );
    const buildDependencyRequests = (
      resolvedSelectionsByGroupKey: Record<string, string>,
      includePredictedAutoCandidates = false,
    ) => {
      const requestsByGroupKey: Record<string, DependencyRequest[]> = {};
      const appendRequestsFromBundle = (
        sourceGroupKey: string,
        sourceBundleKey: string,
        manualSource: boolean,
      ) => {
        const sourceGroup = groupMap.get(sourceGroupKey);
        const sourceBundle = getGroupBundle(sourceGroupKey, sourceBundleKey);
        if (!sourceGroup || !sourceBundle) {
          return;
        }
        sourceBundle.dependencies.forEach((dependency) => {
          const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
          if (!targetBundle) {
            return;
          }
          requestsByGroupKey[dependency.groupKey] = [
            ...(requestsByGroupKey[dependency.groupKey] ?? []),
            {
              bundleKey: dependency.bundleKey,
              bundleLabel: targetBundle.label,
              targetPriority: targetBundle.priority,
              sourceGroupKey,
              sourceGroupLabel: sourceGroup.label,
              sourceBundleKey,
              sourceBundleLabel: sourceBundle.label,
              sourcePriority: sourceBundle.priority,
              manualSource,
            },
          ];
        });
      };
      Object.entries(resolvedSelectionsByGroupKey).forEach(([sourceGroupKey, sourceBundleKey]) => {
        appendRequestsFromBundle(
          sourceGroupKey,
          sourceBundleKey,
          Boolean(effectiveManualSelectionsBySelectionKey[`${selectedRefTemplate.id}:${sourceGroupKey}`]),
        );
      });
      if (includePredictedAutoCandidates) {
        selectedRefTemplateParameterGroups.forEach((group) => {
          if (resolvedSelectionsByGroupKey[group.key]) {
            return;
          }
          const predictedAutoBundle = getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) =>
            doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings),
          );
          if (!predictedAutoBundle) {
            return;
          }
          appendRequestsFromBundle(group.key, predictedAutoBundle.key, false);
        });
      }
      return requestsByGroupKey;
    };
    const aggregateDependencyRequests = (requests: DependencyRequest[]) =>
      Object.values(
        requests.reduce<Record<string, AggregatedDependencyRequest>>((accumulator, request) => {
          const existing = accumulator[request.bundleKey];
          const sourceLabel = `${request.sourceGroupLabel} → ${request.sourceBundleLabel}`;
          if (existing) {
            existing.hasManualSource = existing.hasManualSource || request.manualSource;
            existing.maxSourcePriority = Math.max(existing.maxSourcePriority, request.sourcePriority);
            if (!existing.sourceLabels.includes(sourceLabel)) {
              existing.sourceLabels.push(sourceLabel);
            }
            return accumulator;
          }
          accumulator[request.bundleKey] = {
            bundleKey: request.bundleKey,
            bundleLabel: request.bundleLabel,
            targetPriority: request.targetPriority,
            hasManualSource: request.manualSource,
            maxSourcePriority: request.sourcePriority,
            sourceLabels: [sourceLabel],
          };
          return accumulator;
        }, {}),
      );
    const sortAggregatedDependencyRequests = (
      summaries: AggregatedDependencyRequest[],
      policy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"],
      stickyBundleKey: string,
    ) => [...summaries].sort((left, right) => {
      if (policy === "sticky_auto_selection") {
        if (left.bundleKey === stickyBundleKey || right.bundleKey === stickyBundleKey) {
          return Number(right.bundleKey === stickyBundleKey) - Number(left.bundleKey === stickyBundleKey);
        }
      }
      if (policy === "manual_source_priority") {
        if (Number(right.hasManualSource) !== Number(left.hasManualSource)) {
          return Number(right.hasManualSource) - Number(left.hasManualSource);
        }
      }
      if (right.maxSourcePriority !== left.maxSourcePriority) {
        return right.maxSourcePriority - left.maxSourcePriority;
      }
      if (right.targetPriority !== left.targetPriority) {
        return right.targetPriority - left.targetPriority;
      }
      return left.bundleLabel.localeCompare(right.bundleLabel);
    });
    const manualSelectionsByGroupKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) => {
        const selectionKey = `${selectedRefTemplate.id}:${group.key}`;
        const manualBundleKey = effectiveManualSelectionsBySelectionKey[selectionKey] ?? "";
        return getGroupBundle(group.key, manualBundleKey)
          ? [[group.key, manualBundleKey]]
          : [];
      }),
    );
    const resolvedSelectionsByGroupKey = { ...manualSelectionsByGroupKey };
    const autoSelectionsByGroupKey: Record<string, string> = {};
    const solverReplay: SolverReplayStep[] = [{
      key: "seed",
      title: "Manual seed",
      summary: Object.keys(manualSelectionsByGroupKey).length
        ? `Seeded the solver with ${Object.keys(manualSelectionsByGroupKey).length} manual bundle selection${Object.keys(manualSelectionsByGroupKey).length === 1 ? "" : "s"}.`
        : "No manual bundle anchors were present when the solver started.",
      actions: selectedRefTemplateParameterGroups.flatMap((group) => {
        const manualBundleKey = manualSelectionsByGroupKey[group.key];
        const manualBundle = manualBundleKey ? getGroupBundle(group.key, manualBundleKey) : null;
        return manualBundle
          ? [{
              dependencyEdges: [],
              groupKey: group.key,
              groupLabel: group.label,
              type: "manual_anchor" as const,
              detail: `${manualBundle.label} is pinned manually before coordination begins.`,
            }]
          : [];
      }),
      resolvedSelectionsByGroupKey: { ...resolvedSelectionsByGroupKey },
      autoSelectionsByGroupKey: {},
    }];
    let iterationIndex = 0;
    let changed = true;
    while (changed) {
      changed = false;
      const dependencyRequestsByGroupKey = buildDependencyRequests(resolvedSelectionsByGroupKey, true);
      const iterationActions: SolverReplayAction[] = [];
      selectedRefTemplateParameterGroups.forEach((group) => {
        if (resolvedSelectionsByGroupKey[group.key]) {
          return;
        }
        const coordinationPolicy = getCoordinationPolicy(group);
        const dependencyRequests = dependencyRequestsByGroupKey[group.key] ?? [];
        const aggregatedDependencyRequests = aggregateDependencyRequests(dependencyRequests);
        const stickyBundleKey = predicateRefGroupAutoBundleSelections[`${selectedRefTemplate.id}:${group.key}`] ?? "";
        const sortedDependencyRequests = sortAggregatedDependencyRequests(
          aggregatedDependencyRequests,
          coordinationPolicy,
          stickyBundleKey,
        );
        if (sortedDependencyRequests.length > 1 && coordinationPolicy === "manual_resolution") {
          iterationActions.push({
            dependencyEdges: buildDependencyEdges(dependencyRequests, group.key),
            groupKey: group.key,
            groupLabel: group.label,
            type: "conflict_blocked",
            detail: `${sortedDependencyRequests.map((request) => request.bundleLabel).join(", ")} conflict under manual resolution, so this group stays unresolved.`,
          });
          return;
        }
        const dependencyDrivenBundle = sortedDependencyRequests[0] ?? null;
        if (dependencyDrivenBundle) {
          resolvedSelectionsByGroupKey[group.key] = dependencyDrivenBundle.bundleKey;
          autoSelectionsByGroupKey[group.key] = dependencyDrivenBundle.bundleKey;
          iterationActions.push({
            dependencyEdges: buildDependencyEdges(
              dependencyRequests.filter((request) => request.bundleKey === dependencyDrivenBundle.bundleKey),
              group.key,
            ),
            groupKey: group.key,
            groupLabel: group.label,
            type: "dependency_selection",
            detail: `${dependencyDrivenBundle.bundleLabel} won from ${dependencyDrivenBundle.sourceLabels.join(", ")} under ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
          });
          changed = true;
          return;
        }
        const directAutoBundle = getSortedTemplateGroupPresetBundles(group.presetBundles).find((bundle) =>
          doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings)
          && bundle.dependencies.every((dependency) =>
            resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey,
          ),
        );
        if (directAutoBundle) {
          resolvedSelectionsByGroupKey[group.key] = directAutoBundle.key;
          autoSelectionsByGroupKey[group.key] = directAutoBundle.key;
          const directAutoDependencyEdges = directAutoBundle.dependencies.flatMap((dependency) => {
            const sourceBundleKey = resolvedSelectionsByGroupKey[dependency.groupKey];
            const sourceGroup = groupMap.get(dependency.groupKey);
            const sourceBundle = getGroupBundle(dependency.groupKey, sourceBundleKey);
            if (!sourceGroup || !sourceBundle) {
              return [];
            }
            return [{
              key: `${dependency.groupKey}:${sourceBundleKey}->${group.key}:${directAutoBundle.key}`,
              label: `${sourceGroup.label} → ${sourceBundle.label} => ${group.label} → ${directAutoBundle.label}`,
              sourceGroupKey: dependency.groupKey,
              sourceGroupLabel: sourceGroup.label,
              sourceBundleKey,
              sourceBundleLabel: sourceBundle.label,
              targetGroupKey: group.key,
              targetGroupLabel: group.label,
              targetBundleKey: directAutoBundle.key,
              targetBundleLabel: directAutoBundle.label,
            }];
          });
          iterationActions.push({
            dependencyEdges: directAutoDependencyEdges,
            groupKey: group.key,
            groupLabel: group.label,
            type: "direct_auto_selection",
            detail: `${directAutoBundle.label} matched ${directAutoBundle.autoSelectRule.replaceAll("_", " ")} and all dependencies were already satisfied.`,
          });
          changed = true;
          return;
        }
        if (dependencyRequestsByGroupKey[group.key]?.length || aggregatedDependencyRequests.length) {
          return;
        }
        iterationActions.push({
          dependencyEdges: [],
          groupKey: group.key,
          groupLabel: group.label,
          type: "idle",
          detail: "No dependency request or valid auto-select candidate changed this group in this pass.",
        });
      });
      solverReplay.push({
        key: `iteration:${iterationIndex}`,
        title: `Iteration ${iterationIndex + 1}`,
        summary: iterationActions.length
          ? `${iterationActions.filter((action) => action.type !== "idle").length || iterationActions.length} coordination event${(iterationActions.filter((action) => action.type !== "idle").length || iterationActions.length) === 1 ? "" : "s"} recorded in this pass.`
          : "No further changes were produced in this pass.",
        actions: iterationActions,
        resolvedSelectionsByGroupKey: { ...resolvedSelectionsByGroupKey },
        autoSelectionsByGroupKey: { ...autoSelectionsByGroupKey },
      });
      iterationIndex += 1;
    }
    const dependencyRequestsByGroupKey = buildDependencyRequests(resolvedSelectionsByGroupKey);
    const conflictRequestsByGroupKey = Object.fromEntries(
      selectedRefTemplateParameterGroups.flatMap((group) => {
        const coordinationPolicy = getCoordinationPolicy(group);
        const aggregatedDependencyRequests = aggregateDependencyRequests(
          dependencyRequestsByGroupKey[group.key] ?? [],
        );
        return aggregatedDependencyRequests.length > 1
          ? [[group.key, sortAggregatedDependencyRequests(
              aggregatedDependencyRequests,
              coordinationPolicy,
              predicateRefGroupAutoBundleSelections[`${selectedRefTemplate.id}:${group.key}`] ?? "",
            )]]
          : [];
      }),
    );
    const unmetDependenciesByGroupKey = Object.fromEntries(
      Object.entries(resolvedSelectionsByGroupKey).flatMap(([groupKey, bundleKey]) => {
        const bundle = getGroupBundle(groupKey, bundleKey);
        if (!bundle) {
          return [];
        }
        const unmetDependencies = bundle.dependencies.flatMap((dependency) => {
          if (resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey) {
            return [];
          }
          const targetGroup = groupMap.get(dependency.groupKey);
          const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
          return [{
            key: dependency.key,
            groupKey: dependency.groupKey,
            groupLabel: targetGroup?.label ?? dependency.groupKey,
            bundleKey: dependency.bundleKey,
            bundleLabel: targetBundle?.label ?? dependency.bundleKey,
          }];
        });
        return unmetDependencies.length
          ? [[groupKey, unmetDependencies]]
          : [];
      }),
    );
    const policyTraceEntries: Array<[string, PolicyTrace]> = [];
    const globalManualGroups: string[] = [];
    const globalDependencyGroups: string[] = [];
    const globalAutoGroups: string[] = [];
    const globalBlockedGroups: string[] = [];
    const globalConflictGroups: string[] = [];
    const globalIdleGroups: string[] = [];
    selectedRefTemplateParameterGroups.forEach((group) => {
        const selectionKey = `${selectedRefTemplate.id}:${group.key}`;
        const coordinationPolicy = getCoordinationPolicy(group);
        const manualBundleKey = manualSelectionsByGroupKey[group.key] ?? "";
        const manualBundle = getGroupBundle(group.key, manualBundleKey);
        const resolvedBundleKey = resolvedSelectionsByGroupKey[group.key] ?? "";
        const resolvedBundle = getGroupBundle(group.key, resolvedBundleKey);
        const stickyBundleKey = predicateRefGroupAutoBundleSelections[selectionKey] ?? "";
        const dependencyRequests = dependencyRequestsByGroupKey[group.key] ?? [];
        const aggregatedDependencyRequests = sortAggregatedDependencyRequests(
          aggregateDependencyRequests(dependencyRequests),
          coordinationPolicy,
          stickyBundleKey,
        );
        const matchingAutoBundles = getSortedTemplateGroupPresetBundles(group.presetBundles).flatMap((bundle) => {
          if (!doesTemplateGroupBundleMatchAutoSelectRule(group, bundle, effectiveDraftBindings)) {
            return [];
          }
          const unmetDependencies = bundle.dependencies.flatMap((dependency) => {
            if (resolvedSelectionsByGroupKey[dependency.groupKey] === dependency.bundleKey) {
              return [];
            }
            const targetGroup = groupMap.get(dependency.groupKey);
            const targetBundle = getGroupBundle(dependency.groupKey, dependency.bundleKey);
            return [
              `${targetGroup?.label ?? dependency.groupKey} → ${targetBundle?.label ?? dependency.bundleKey}`,
            ];
          });
          return [{
            bundle,
            unmetDependencies,
          }];
        });
        const selectedByDependency = Boolean(
          resolvedBundleKey && aggregatedDependencyRequests.some((request) => request.bundleKey === resolvedBundleKey),
        );
        const selectedAutoBundleEntry =
          matchingAutoBundles.find(({ bundle }) => bundle.key === resolvedBundleKey)
          ?? null;
        const blockedAutoBundles = matchingAutoBundles.filter(
          ({ unmetDependencies }) => unmetDependencies.length > 0,
        );
        const unmetDependencies = unmetDependenciesByGroupKey[group.key] ?? [];
        let statusLabel = "Idle";
        let tone: PolicyTrace["tone"] = "muted";
        let summary = "No coordinated bundle is active for this group right now.";
        if (manualBundle) {
          statusLabel = "Manual";
          tone = "success";
          summary = `${manualBundle.label} is pinned manually and overrides auto coordination for this group.`;
        } else if (resolvedBundle && selectedByDependency) {
          statusLabel = "Resolved";
          tone = "success";
          summary = `${resolvedBundle.label} was selected from incoming dependency requests.`;
        } else if (resolvedBundle && selectedAutoBundleEntry) {
          statusLabel = "Auto";
          tone = "success";
          summary = `${resolvedBundle.label} auto-selected via ${selectedAutoBundleEntry.bundle.autoSelectRule.replaceAll("_", " ")}.`;
        } else if (
          aggregatedDependencyRequests.length > 1
          && coordinationPolicy === "manual_resolution"
        ) {
          statusLabel = "Blocked";
          tone = "warning";
          summary = "Conflicting dependency requests require manual resolution before this group can choose a bundle.";
        } else if (blockedAutoBundles.length) {
          statusLabel = "Blocked";
          tone = "warning";
          summary = "Auto-select candidates are currently blocked by unresolved dependencies.";
        } else if (aggregatedDependencyRequests.length) {
          statusLabel = "Pending";
          tone = "info";
          summary = "Dependency requests are present, but this group is still waiting for a coordinated decision.";
        }
        const policyDetailParts = [
          `Uses ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
        ];
        if (coordinationPolicy === "sticky_auto_selection" && stickyBundleKey) {
          const stickyBundle = getGroupBundle(group.key, stickyBundleKey);
          if (stickyBundle) {
            policyDetailParts.push(`Current sticky preference is ${stickyBundle.label}.`);
          }
        }
        const steps: PolicyTraceStep[] = [{
          key: `${group.key}:policy`,
          title: "Coordination policy",
          detail: policyDetailParts.join(" "),
          tone: "info",
        }];
        if (manualBundle) {
          steps.push({
            key: `${group.key}:manual`,
            title: "Manual override",
            detail: `${manualBundle.label} is manually selected, so dependency and auto-selection rules are treated as advisory until you clear the override.`,
            tone: "success",
          });
        }
        if (aggregatedDependencyRequests.length) {
          steps.push({
            key: `${group.key}:requests`,
            title: aggregatedDependencyRequests.length > 1
              ? "Incoming dependency requests"
              : "Incoming dependency request",
            detail: aggregatedDependencyRequests
              .map((request) => {
                const detailParts = [
                  `from ${request.sourceLabels.join(", ")}`,
                  `target P${request.targetPriority}`,
                  `source P${request.maxSourcePriority}`,
                ];
                if (request.hasManualSource) {
                  detailParts.push("includes manual source");
                }
                return `${request.bundleLabel} (${detailParts.join(" · ")})`;
              })
              .join("; "),
            tone: aggregatedDependencyRequests.length > 1 ? "warning" : "info",
          });
        }
        if (aggregatedDependencyRequests.length > 1) {
          if (coordinationPolicy === "manual_resolution" && !manualBundle && !resolvedBundle) {
            steps.push({
              key: `${group.key}:conflict`,
              title: "Conflict resolution",
              detail: "Multiple bundles were requested for this group, and the current policy requires an explicit manual choice before coordination can continue.",
              tone: "warning",
            });
          } else if (resolvedBundle) {
            steps.push({
              key: `${group.key}:conflict`,
              title: "Conflict resolution",
              detail: `${resolvedBundle.label} won the conflict under ${formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(coordinationPolicy)}.`,
              tone: "success",
            });
          }
        } else if (!manualBundle && resolvedBundle && selectedByDependency && aggregatedDependencyRequests[0]) {
          steps.push({
            key: `${group.key}:dependency-selection`,
            title: "Dependency-driven selection",
            detail: `${resolvedBundle.label} satisfied the active request from ${aggregatedDependencyRequests[0].sourceLabels.join(", ")}.`,
            tone: "success",
          });
        }
        if (!manualBundle && resolvedBundle && selectedAutoBundleEntry && !selectedByDependency) {
          steps.push({
            key: `${group.key}:auto-selection`,
            title: "Direct auto-selection",
            detail: `${resolvedBundle.label} matched ${selectedAutoBundleEntry.bundle.autoSelectRule.replaceAll("_", " ")} with priority P${selectedAutoBundleEntry.bundle.priority}.`,
            tone: "success",
          });
        }
        if (blockedAutoBundles.length) {
          steps.push({
            key: `${group.key}:blocked-auto`,
            title: "Blocked auto candidates",
            detail: blockedAutoBundles
              .map(
                ({ bundle, unmetDependencies: bundleUnmetDependencies }) =>
                  `${bundle.label} (${bundle.autoSelectRule.replaceAll("_", " ")}) is waiting on ${bundleUnmetDependencies.join(", ")}`,
              )
              .join("; "),
            tone: "warning",
          });
        }
        if (unmetDependencies.length) {
          steps.push({
            key: `${group.key}:unmet`,
            title: "Unmet dependencies",
            detail: `Waiting on ${unmetDependencies
              .map((dependency) => `${dependency.groupLabel} → ${dependency.bundleLabel}`)
              .join(", ")}.`,
            tone: "warning",
          });
        }
        if (tone === "muted" && steps.length === 1) {
          steps.push({
            key: `${group.key}:idle`,
            title: "Idle state",
            detail: "No incoming dependency requests or matching auto-select rules are currently activating this group.",
            tone: "muted",
          });
        }
        if (manualBundle) {
          globalManualGroups.push(group.label);
        } else if (resolvedBundle && selectedByDependency) {
          globalDependencyGroups.push(`${group.label} → ${resolvedBundle.label}`);
        } else if (resolvedBundle && selectedAutoBundleEntry) {
          globalAutoGroups.push(`${group.label} → ${resolvedBundle.label}`);
        } else if (tone === "warning") {
          globalBlockedGroups.push(group.label);
        } else if (tone === "muted") {
          globalIdleGroups.push(group.label);
        }
        if (aggregatedDependencyRequests.length > 1) {
          globalConflictGroups.push(group.label);
        }
        policyTraceEntries.push([group.key, {
          summary,
          statusLabel,
          tone,
          steps,
        }]);
      });
    const policyTraceByGroupKey = Object.fromEntries(policyTraceEntries);
    const globalPolicyTraceSteps: PolicyTraceStep[] = [];
    if (globalManualGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:manual",
        title: "Manual anchors",
        detail: `${globalManualGroups.join(", ")} currently pin their bundle choices manually, anchoring the coordination graph.`,
        tone: "success",
      });
    }
    if (globalDependencyGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:dependencies",
        title: "Dependency-driven chain",
        detail: globalDependencyGroups.join("; "),
        tone: "info",
      });
    }
    if (globalAutoGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:auto",
        title: "Direct auto selections",
        detail: globalAutoGroups.join("; "),
        tone: "success",
      });
    }
    if (globalConflictGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:conflicts",
        title: "Conflict hotspots",
        detail: `${globalConflictGroups.join(", ")} received competing bundle requests during coordination.`,
        tone: "warning",
      });
    }
    if (globalBlockedGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:blocked",
        title: "Blocked groups",
        detail: `${globalBlockedGroups.join(", ")} are blocked by unresolved dependencies or manual-resolution requirements.`,
        tone: "warning",
      });
    }
    if (globalIdleGroups.length) {
      globalPolicyTraceSteps.push({
        key: "global:idle",
        title: "Idle groups",
        detail: `${globalIdleGroups.join(", ")} are not currently activated by dependency or auto-selection rules.`,
        tone: "muted",
      });
    }
    const globalPolicyTrace: GlobalPolicyTrace = {
      summary: globalBlockedGroups.length
        ? `Coordination currently has ${globalBlockedGroups.length} blocked group${globalBlockedGroups.length === 1 ? "" : "s"} across ${selectedRefTemplateParameterGroups.length} template group${selectedRefTemplateParameterGroups.length === 1 ? "" : "s"}.`
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? `Coordination resolved ${Object.keys(resolvedSelectionsByGroupKey).length} group bundle${Object.keys(resolvedSelectionsByGroupKey).length === 1 ? "" : "s"} across the current dependency graph.`
          : "No coordination activity is currently running across this template graph.",
      statusLabel: globalBlockedGroups.length
        ? "Blocked"
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? "Active"
          : "Idle",
      tone: globalBlockedGroups.length
        ? "warning"
        : globalDependencyGroups.length || globalAutoGroups.length || globalManualGroups.length
          ? "info"
          : "muted",
      steps: globalPolicyTraceSteps,
      counts: {
        groupCount: selectedRefTemplateParameterGroups.length,
        manualCount: globalManualGroups.length,
        autoCount: globalDependencyGroups.length + globalAutoGroups.length,
        blockedCount: globalBlockedGroups.length,
        conflictCount: globalConflictGroups.length,
        dependencyRequestCount: Object.values(dependencyRequestsByGroupKey).reduce(
          (total, requests) => total + requests.length,
          0,
        ),
        unmetDependencyCount: Object.values(unmetDependenciesByGroupKey).reduce(
          (total, dependencies) => total + dependencies.length,
          0,
        ),
      },
    };
    return {
      autoSelectionsBySelectionKey: Object.fromEntries(
        Object.entries(autoSelectionsByGroupKey).map(([groupKey, bundleKey]) => [
          `${selectedRefTemplate.id}:${groupKey}`,
          bundleKey,
        ]),
      ),
      resolvedSelectionsByGroupKey,
      dependencyRequestsByGroupKey,
      unmetDependenciesByGroupKey,
      conflictRequestsByGroupKey,
      policyTraceByGroupKey,
      globalPolicyTrace,
      solverReplay,
    };
}
