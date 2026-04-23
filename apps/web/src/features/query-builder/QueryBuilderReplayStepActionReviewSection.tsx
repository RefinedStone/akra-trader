import type { ComponentProps } from "react";

import type {
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState,
  RunSurfaceCollectionQueryRuntimeCandidateTrace,
} from "./model";
import { QueryBuilderRuntimeCandidateTraceReview } from "./QueryBuilderRuntimeCandidateTraceReview";

type RuntimeCandidateReviewContext = Omit<
  ComponentProps<typeof QueryBuilderRuntimeCandidateTraceReview>,
  "candidateTrace" | "groupKey" | "mode" | "scope" | "stepIndex"
>;

type ReviewFieldPick = {
  decisionKey: string;
  label: string;
  source: "local" | "remote";
};

type FocusedChainExplanation = {
  bindingSourceLocations: Array<{ detail: string; location: string }>;
  bundleRuleDetail: string;
  bundleRuleTitle: string;
  clauseSourceLocations: Array<{ detail: string; location: string }>;
  edgeLabels: string[];
  edgeRoleLabel: string | null;
  matchedPredicateBranches: Array<{ detail: string; location: string }>;
  parameterComparisons: Array<{ detail: string; location: string }>;
  parameterReasons: Array<{ detail: string; label: string }>;
  runtimeCandidateTraces: RunSurfaceCollectionQueryRuntimeCandidateTrace[];
  shortCircuitTraces: Array<{ detail: string; location: string }>;
  stateTransitionLabel: string | null;
  truthTableRows: Array<{ detail: string; expression: string; location: string; result: boolean }>;
  bundleRuleTitleDetail?: never;
  causalLabel: string;
};

type SimulationGroup = {
  key: string;
  label: string;
  presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
};

type SimulationReplayAction = {
  dependencyEdges: Array<{
    key: string;
    label: string;
  }>;
  detail: string;
  groupKey: string;
  groupLabel: string;
  type: "conflict_blocked" | "dependency_selection" | "direct_auto_selection" | "idle" | "manual_anchor";
};

type ActiveReplayStep = {
  key: string;
  resolvedSelectionsByGroupKey: Record<string, string>;
};

type QueryBuilderReplayStepActionReviewSectionProps = {
  callbacks: {
    focusConflictDecision: (conflictId: string, decisionKey: string) => void;
    getSortedTemplateGroupPresetBundles: (
      bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[],
    ) => RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
    toggleFieldPickSource: (decisionKey: string) => void;
  };
  review: {
    actionTypeFilter: "all" | "conflict_blocked" | "dependency_selection" | "direct_auto_selection" | "idle" | "manual_anchor";
    activeReviewConflictId: string | null;
    activeStep: ActiveReplayStep | null;
    activeStepIndex: number;
    edgeFilter: string;
    fieldPicksByGroupKey: Record<string, ReviewFieldPick[]>;
    filteredActions: SimulationReplayAction[];
    filteredEdge: {
      sourceBundleLabel: string;
      sourceGroupLabel: string;
      targetBundleLabel: string;
      targetGroupLabel: string;
    } | null;
    filteredGroup: { label: string } | null;
    focusedChainEntry: FocusedChainExplanation | null;
    focusedChainPosition: number;
    focusedChainStepIndexSet: Set<number>;
    focusedDecision: { conflictId: string; decisionKey: string } | null;
    primaryFocusGroupKey: string | null;
    replayGroupFilter: string;
    simulatedCoordinationGroups: SimulationGroup[];
  };
  runtimeCandidate: RuntimeCandidateReviewContext;
};

export function QueryBuilderReplayStepActionReviewSection({
  callbacks: {
    focusConflictDecision,
    getSortedTemplateGroupPresetBundles,
    toggleFieldPickSource,
  },
  review: {
    actionTypeFilter,
    activeReviewConflictId,
    activeStep,
    activeStepIndex,
    edgeFilter,
    fieldPicksByGroupKey,
    filteredActions,
    filteredEdge,
    filteredGroup,
    focusedChainEntry,
    focusedChainPosition,
    focusedChainStepIndexSet,
    focusedDecision,
    primaryFocusGroupKey,
    replayGroupFilter,
    simulatedCoordinationGroups,
  },
  runtimeCandidate,
}: QueryBuilderReplayStepActionReviewSectionProps) {
  if (!activeStep) {
    return null;
  }

  const isFocusedReplayStep = focusedChainStepIndexSet.has(activeStepIndex);

  return (
    <>
      <div className="run-surface-query-builder-trace-chip-list">
        {simulatedCoordinationGroups.map((group) => {
          const resolvedBundleKey = activeStep.resolvedSelectionsByGroupKey[group.key] ?? "";
          const resolvedBundle =
            getSortedTemplateGroupPresetBundles(group.presetBundles).find(
              (bundle) => bundle.key === resolvedBundleKey,
            ) ?? null;
          return (
            <span
              className={`run-surface-query-builder-trace-chip${
                primaryFocusGroupKey === group.key
                || replayGroupFilter === "all"
                || replayGroupFilter === group.key
                  ? " is-active"
                  : " is-muted"
              }`}
              key={`solver-replay:${group.key}`}
            >
              {`${group.label}: ${resolvedBundle?.label ?? "unresolved"}${
                fieldPicksByGroupKey[group.key]?.length
                  ? ` · ${fieldPicksByGroupKey[group.key].length} reviewed picks`
                  : ""
              }`}
            </span>
          );
        })}
      </div>
      {filteredEdge ? (
        <div className="run-surface-query-builder-trace-chip-list">
          <span className="run-surface-query-builder-trace-chip is-active">
            {`Source: ${filteredEdge.sourceGroupLabel} → ${filteredEdge.sourceBundleLabel}`}
          </span>
          <span className="run-surface-query-builder-trace-chip is-active">
            {`Target: ${filteredEdge.targetGroupLabel} → ${filteredEdge.targetBundleLabel}`}
          </span>
        </div>
      ) : null}
      <div className="run-surface-query-builder-trace-list">
        {filteredActions.length ? (
          filteredActions.map((action) => (
            <div
              className={`run-surface-query-builder-trace-step is-${
                isFocusedReplayStep && primaryFocusGroupKey === action.groupKey
                  ? "success"
                  : action.type === "conflict_blocked"
                    ? "warning"
                    : action.type === "idle"
                      ? "muted"
                      : "success"
              }`}
              key={`${activeStep.key}:${action.groupKey}:${action.type}`}
            >
              <strong>{`${action.groupLabel} · ${action.type.replaceAll("_", " ")}`}</strong>
              <p>{action.detail}</p>
              {isFocusedReplayStep ? (
                <div className="run-surface-query-builder-trace-chip-list">
                  <span className="run-surface-query-builder-trace-chip is-active">
                    {`Causal chain step ${focusedChainPosition + 1}/${Math.max(1, focusedChainStepIndexSet.size)}`}
                  </span>
                  {focusedChainEntry?.causalLabel ? (
                    <span className="run-surface-query-builder-trace-chip is-active">
                      {focusedChainEntry.causalLabel}
                    </span>
                  ) : null}
                  {focusedChainEntry?.stateTransitionLabel ? (
                    <span className="run-surface-query-builder-trace-chip">
                      {focusedChainEntry.stateTransitionLabel}
                    </span>
                  ) : null}
                  {focusedChainEntry?.edgeRoleLabel ? (
                    <span className="run-surface-query-builder-trace-chip">
                      {focusedChainEntry.edgeRoleLabel}
                    </span>
                  ) : null}
                </div>
              ) : null}
              {focusedChainEntry && isFocusedReplayStep ? (
                <div className="run-surface-query-builder-trace-panel is-nested">
                  <div className="run-surface-query-builder-card-head">
                    <strong>Bundle rule explanation</strong>
                    <span>{focusedChainEntry.bundleRuleTitle}</span>
                  </div>
                  <p className="run-note">
                    {focusedChainEntry.bundleRuleDetail}
                  </p>
                  {focusedChainEntry.parameterReasons.length ? (
                    <div className="run-surface-query-builder-trace-list">
                      {focusedChainEntry.parameterReasons.slice(0, 3).map((reason) => (
                        <div
                          className="run-surface-query-builder-trace-step is-info"
                          key={`${activeStep.key}:${action.groupKey}:causal-reason:${reason.label}`}
                        >
                          <strong>{reason.label}</strong>
                          <p>{reason.detail}</p>
                        </div>
                      ))}
                    </div>
                  ) : null}
                  {focusedChainEntry.clauseSourceLocations.length
                  || focusedChainEntry.bindingSourceLocations.length ? (
                    <div className="run-surface-query-builder-trace-panel is-nested">
                      <div className="run-surface-query-builder-card-head">
                        <strong>Explanation provenance</strong>
                        <span>Active replay step</span>
                      </div>
                      {focusedChainEntry.clauseSourceLocations.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.clauseSourceLocations.slice(0, 2).map((sourceLocation) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`${activeStep.key}:${action.groupKey}:causal-clause:${sourceLocation.location}`}
                            >
                              <strong>{sourceLocation.location}</strong>
                              <p>{sourceLocation.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                      {focusedChainEntry.bindingSourceLocations.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.bindingSourceLocations.slice(0, 3).map((sourceLocation) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`${activeStep.key}:${action.groupKey}:causal-binding:${sourceLocation.location}`}
                            >
                              <strong>{sourceLocation.location}</strong>
                              <p>{sourceLocation.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                  {focusedChainEntry.runtimeCandidateTraces.length
                  || focusedChainEntry.truthTableRows.length
                  || focusedChainEntry.shortCircuitTraces.length
                  || focusedChainEntry.matchedPredicateBranches.length
                  || focusedChainEntry.parameterComparisons.length ? (
                    <div className="run-surface-query-builder-trace-panel is-nested">
                      <div className="run-surface-query-builder-card-head">
                        <strong>Evaluation-level provenance</strong>
                        <span>Active replay step</span>
                      </div>
                      {focusedChainEntry.runtimeCandidateTraces.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.runtimeCandidateTraces.slice(0, 3).map((candidateTrace) => (
                            <QueryBuilderRuntimeCandidateTraceReview
                              {...runtimeCandidate}
                              candidateTrace={candidateTrace}
                              groupKey={action.groupKey}
                              key={`${activeStep.key}:${action.groupKey}:causal-candidate:${candidateTrace.location}:${candidateTrace.candidatePath}:${candidateTrace.candidateAccessor}`}
                              mode="active_replay"
                              scope="active_replay"
                              stepIndex={activeStepIndex}
                            />
                          ))}
                        </div>
                      ) : null}
                      {focusedChainEntry.truthTableRows.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.truthTableRows.slice(0, 3).map((row) => (
                            <div
                              className={`run-surface-query-builder-trace-step is-${row.result ? "success" : "muted"}`}
                              key={`${activeStep.key}:${action.groupKey}:causal-truth:${row.location}:${row.expression}`}
                            >
                              <strong>{row.expression}</strong>
                              <p>{row.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                      {focusedChainEntry.shortCircuitTraces.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.shortCircuitTraces.slice(0, 2).map((trace) => (
                            <div
                              className="run-surface-query-builder-trace-step is-warning"
                              key={`${activeStep.key}:${action.groupKey}:causal-short-circuit:${trace.location}:${trace.detail}`}
                            >
                              <strong>{trace.location}</strong>
                              <p>{trace.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                      {focusedChainEntry.matchedPredicateBranches.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.matchedPredicateBranches.slice(0, 2).map((match) => (
                            <div
                              className="run-surface-query-builder-trace-step is-success"
                              key={`${activeStep.key}:${action.groupKey}:causal-branch:${match.location}:${match.detail}`}
                            >
                              <strong>{match.location}</strong>
                              <p>{match.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                      {focusedChainEntry.parameterComparisons.length ? (
                        <div className="run-surface-query-builder-trace-list">
                          {focusedChainEntry.parameterComparisons.slice(0, 3).map((comparison) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`${activeStep.key}:${action.groupKey}:causal-comparison:${comparison.location}:${comparison.detail}`}
                            >
                              <strong>{comparison.location}</strong>
                              <p>{comparison.detail}</p>
                            </div>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              ) : null}
              {action.dependencyEdges.length ? (
                <div className="run-surface-query-builder-trace-chip-list">
                  {action.dependencyEdges.map((edge) => (
                    <span
                      className={`run-surface-query-builder-trace-chip${
                        edgeFilter === "all" || edgeFilter === edge.key
                          ? " is-active"
                          : ""
                      }`}
                      key={`${activeStep.key}:${action.groupKey}:${edge.key}`}
                    >
                      {edge.label}
                    </span>
                  ))}
                </div>
              ) : null}
              {focusedChainEntry?.edgeLabels.length && isFocusedReplayStep ? (
                <div className="run-surface-query-builder-trace-chip-list">
                  {focusedChainEntry.edgeLabels.map((edgeLabel) => (
                    <span
                      className="run-surface-query-builder-trace-chip"
                      key={`${activeStep.key}:${action.groupKey}:causal-edge:${edgeLabel}`}
                    >
                      {edgeLabel}
                    </span>
                  ))}
                </div>
              ) : null}
              {fieldPicksByGroupKey[action.groupKey]?.length ? (
                <div className="run-surface-query-builder-trace-chip-list">
                  {fieldPicksByGroupKey[action.groupKey].slice(0, 4).map((pick) => (
                    <span
                      className="run-surface-query-builder-trace-chip-list"
                      key={`${activeStep.key}:${action.groupKey}:review-pick:${pick.decisionKey}`}
                    >
                      <button
                        className={`run-surface-query-builder-trace-chip${
                          pick.source === "remote" ? " is-active" : ""
                        }`}
                        onClick={() => toggleFieldPickSource(pick.decisionKey)}
                        type="button"
                      >
                        {`${pick.label} · ${pick.source === "remote" ? "remote" : "local"}`}
                      </button>
                      <button
                        className={`run-surface-query-builder-trace-chip${
                          focusedDecision?.conflictId === activeReviewConflictId
                          && focusedDecision?.decisionKey === pick.decisionKey
                            ? " is-active"
                            : ""
                        }`}
                        onClick={() => {
                          if (!activeReviewConflictId) {
                            return;
                          }
                          focusConflictDecision(activeReviewConflictId, pick.decisionKey);
                        }}
                        type="button"
                      >
                        Review field
                      </button>
                    </span>
                  ))}
                  {fieldPicksByGroupKey[action.groupKey].length > 4 ? (
                    <span className="run-surface-query-builder-trace-chip">
                      {`+${fieldPicksByGroupKey[action.groupKey].length - 4} more reviewed picks`}
                    </span>
                  ) : null}
                </div>
              ) : null}
            </div>
          ))
        ) : (
          <div className="run-surface-query-builder-trace-step is-muted">
            <strong>No matching actions</strong>
            <p>
              {filteredGroup
                ? (
                    actionTypeFilter !== "all"
                      ? (
                          edgeFilter !== "all"
                            ? `This replay step did not produce any ${actionTypeFilter.replaceAll("_", " ")} actions for ${filteredGroup.label} on the selected dependency edge.`
                            : `This replay step did not produce any ${actionTypeFilter.replaceAll("_", " ")} actions for ${filteredGroup.label}.`
                        )
                      : (
                          edgeFilter !== "all"
                            ? `This replay step did not produce any coordination actions for ${filteredGroup.label} on the selected dependency edge.`
                            : `This replay step did not produce any coordination actions for ${filteredGroup.label}.`
                        )
                  )
                : (
                    actionTypeFilter !== "all"
                      ? (
                          edgeFilter !== "all"
                            ? `This replay step did not produce any ${actionTypeFilter.replaceAll("_", " ")} actions on the selected dependency edge.`
                            : `This replay step did not produce any ${actionTypeFilter.replaceAll("_", " ")} actions.`
                        )
                      : (
                          edgeFilter !== "all"
                            ? "This replay step did not produce any actions on the selected dependency edge."
                            : "This replay step did not produce any new coordination actions."
                        )
                  )}
            </p>
          </div>
        )}
      </div>
    </>
  );
}
