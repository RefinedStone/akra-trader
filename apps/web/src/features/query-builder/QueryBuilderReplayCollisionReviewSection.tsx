import type { ComponentProps } from "react";

import type { RunSurfaceCollectionQueryRuntimeCandidateTrace } from "./model";
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
  causalLabel: string;
  clauseSourceLocations: Array<{ detail: string; location: string }>;
  detail: string;
  edgeLabels: string[];
  edgeRoleLabel: string | null;
  kind: "dependency_edge" | "group_action" | "selection_change";
  matchedPredicateBranches: Array<{ detail: string; location: string }>;
  parameterComparisons: Array<{ detail: string; location: string }>;
  parameterReasons: Array<{ detail: string; label: string }>;
  runtimeCandidateTraces: RunSurfaceCollectionQueryRuntimeCandidateTrace[];
  shortCircuitTraces: Array<{ detail: string; location: string }>;
  stateTransitionLabel: string | null;
  stepIndex: number;
  stepLabel: string;
  truthTableRows: Array<{ detail: string; expression: string; location: string; result: boolean }>;
  type: string | null;
};

type QueryBuilderReplayCollisionReviewSectionProps = {
  callbacks: {
    clearReviewOverride: () => void;
    focusConflictDecision: (conflictId: string, decisionKey: string) => void;
    setReplayIndex: (value: number) => void;
    toggleFieldPickSource: (decisionKey: string) => void;
  };
  review: {
    activeReview: {
      conflict: {
        conflictId: string;
        sourceTabLabel: string;
        templateLabel: string;
      };
      hasMixedSelection: boolean;
      hasRemoteSelection: boolean;
      selectedRemoteCount: number;
    } | null;
    activeStepIndex: number;
    focusedChainExplanations: FocusedChainExplanation[];
    focusedDecision: { conflictId: string; decisionKey: string } | null;
    focusedGroupKey: string | null;
    focusedItemLabel: string | null;
    globalFieldPicks: ReviewFieldPick[];
    groupKeys: string[];
    groupLabelsByKey: Record<string, string>;
  };
  runtimeCandidate: RuntimeCandidateReviewContext;
};

export function QueryBuilderReplayCollisionReviewSection({
  callbacks: {
    clearReviewOverride,
    focusConflictDecision,
    setReplayIndex,
    toggleFieldPickSource,
  },
  review: {
    activeReview,
    activeStepIndex,
    focusedChainExplanations,
    focusedDecision,
    focusedGroupKey,
    focusedItemLabel,
    globalFieldPicks,
    groupKeys,
    groupLabelsByKey,
  },
  runtimeCandidate,
}: QueryBuilderReplayCollisionReviewSectionProps) {
  if (!activeReview) {
    return null;
  }

  return (
    <div className="run-surface-query-builder-trace-panel is-nested">
      <div className="run-surface-query-builder-card-head">
        <strong>Collision review override</strong>
        <span>{activeReview.conflict.templateLabel}</span>
      </div>
      <div className="run-surface-query-builder-trace-chip-list">
        <span className="run-surface-query-builder-trace-chip is-active">
          {`${activeReview.selectedRemoteCount} remote field picks`}
        </span>
        <span className="run-surface-query-builder-trace-chip">
          {`${groupKeys.length} override groups`}
        </span>
        <span className="run-surface-query-builder-trace-chip">
          {activeReview.hasMixedSelection
            ? "Partial merge replay"
            : activeReview.hasRemoteSelection
              ? "Full remote replay"
              : "Local replay baseline"}
        </span>
      </div>
      <p className="run-note">
        {`Simulation is currently replaying the reviewed collision draft for ${activeReview.conflict.sourceTabLabel} across ${groupKeys
          .map((groupKey) => groupLabelsByKey[groupKey] ?? groupKey)
          .join(", ") || "no groups"}.`}
      </p>
      {globalFieldPicks.length ? (
        <div className="run-surface-query-builder-trace-chip-list">
          {globalFieldPicks.slice(0, 4).map((pick) => (
            <span className="run-surface-query-builder-trace-chip-list" key={`collision-override-global-pick:${pick.decisionKey}`}>
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
                  focusedDecision?.conflictId === activeReview.conflict.conflictId
                  && focusedDecision?.decisionKey === pick.decisionKey
                    ? " is-active"
                    : ""
                }`}
                onClick={() => focusConflictDecision(activeReview.conflict.conflictId, pick.decisionKey)}
                type="button"
              >
                Review field
              </button>
            </span>
          ))}
          {globalFieldPicks.length > 4 ? (
            <span className="run-surface-query-builder-trace-chip">
              {`+${globalFieldPicks.length - 4} more reviewed picks`}
            </span>
          ) : null}
        </div>
      ) : null}
      {focusedItemLabel && focusedChainExplanations.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Reviewed field causal chain</strong>
            <span>{focusedChainExplanations.length === 1
              ? "1 replay step"
              : `${focusedChainExplanations.length} replay steps`}</span>
          </div>
          <p className="run-note">
            {`${focusedItemLabel} propagates through ${focusedGroupKey ?? "the replay graph"} across the steps below.`}
          </p>
          <div className="run-surface-query-builder-trace-chip-list">
            {focusedChainExplanations.map((entry, index) => (
              <button
                className={`run-surface-query-builder-trace-chip${
                  entry.stepIndex === activeStepIndex ? " is-active" : ""
                }`}
                key={`focused-causal-chain:${entry.stepIndex}:${index}`}
                onClick={() => setReplayIndex(entry.stepIndex)}
                type="button"
              >
                {`${entry.stepLabel}${entry.type ? ` · ${entry.type.replaceAll("_", " ")}` : ""}`}
              </button>
            ))}
          </div>
          <div className="run-surface-query-builder-trace-list">
            {focusedChainExplanations.map((entry, index) => (
              <div
                className={`run-surface-query-builder-trace-step is-${
                  entry.stepIndex === activeStepIndex
                    ? "success"
                    : entry.kind === "dependency_edge"
                      ? "info"
                      : entry.kind === "selection_change"
                        ? "warning"
                        : "info"
                }`}
                key={`focused-causal-step:${entry.stepIndex}:${index}`}
              >
                <strong>{`${entry.stepLabel}${entry.type ? ` · ${entry.type.replaceAll("_", " ")}` : ""}`}</strong>
                <div className="run-surface-query-builder-trace-chip-list">
                  <span className="run-surface-query-builder-trace-chip is-active">
                    {entry.causalLabel}
                  </span>
                  {entry.stateTransitionLabel ? (
                    <span className="run-surface-query-builder-trace-chip">
                      {entry.stateTransitionLabel}
                    </span>
                  ) : null}
                  {entry.edgeRoleLabel ? (
                    <span className="run-surface-query-builder-trace-chip">
                      {entry.edgeRoleLabel}
                    </span>
                  ) : null}
                </div>
                <p>{entry.detail}</p>
                <div className="run-surface-query-builder-trace-panel is-nested">
                  <div className="run-surface-query-builder-card-head">
                    <strong>Bundle rule explanation</strong>
                    <span>{entry.bundleRuleTitle}</span>
                  </div>
                  <p className="run-note">{entry.bundleRuleDetail}</p>
                </div>
                {entry.edgeLabels.length ? (
                  <div className="run-surface-query-builder-trace-chip-list">
                    {entry.edgeLabels.map((edgeLabel) => (
                      <span
                        className="run-surface-query-builder-trace-chip"
                        key={`focused-causal-edge:${entry.stepIndex}:${edgeLabel}`}
                      >
                        {edgeLabel}
                      </span>
                    ))}
                  </div>
                ) : null}
                {entry.parameterReasons.length ? (
                  <div className="run-surface-query-builder-trace-panel is-nested">
                    <div className="run-surface-query-builder-card-head">
                      <strong>Parameter-level predicate reasons</strong>
                      <span>{entry.parameterReasons.length}</span>
                    </div>
                    <div className="run-surface-query-builder-trace-list">
                      {entry.parameterReasons.map((reason) => (
                        <div
                          className="run-surface-query-builder-trace-step is-info"
                          key={`focused-causal-reason:${entry.stepIndex}:${reason.label}`}
                        >
                          <strong>{reason.label}</strong>
                          <p>{reason.detail}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
                {entry.clauseSourceLocations.length || entry.bindingSourceLocations.length ? (
                  <div className="run-surface-query-builder-trace-panel is-nested">
                    <div className="run-surface-query-builder-card-head">
                      <strong>Explanation provenance</strong>
                      <span>{`${entry.clauseSourceLocations.length + entry.bindingSourceLocations.length} locations`}</span>
                    </div>
                    {entry.clauseSourceLocations.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Template clause locations</strong>
                          <span>{entry.clauseSourceLocations.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.clauseSourceLocations.map((sourceLocation) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`focused-causal-clause:${entry.stepIndex}:${sourceLocation.location}`}
                            >
                              <strong>{sourceLocation.location}</strong>
                              <p>{sourceLocation.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {entry.bindingSourceLocations.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Binding source locations</strong>
                          <span>{entry.bindingSourceLocations.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.bindingSourceLocations.map((sourceLocation) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`focused-causal-binding:${entry.stepIndex}:${sourceLocation.location}`}
                            >
                              <strong>{sourceLocation.location}</strong>
                              <p>{sourceLocation.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
                {entry.matchedPredicateBranches.length
                || entry.parameterComparisons.length
                || entry.runtimeCandidateTraces.length
                || entry.shortCircuitTraces.length
                || entry.truthTableRows.length ? (
                  <div className="run-surface-query-builder-trace-panel is-nested">
                    <div className="run-surface-query-builder-card-head">
                      <strong>Evaluation-level provenance</strong>
                      <span>{`${entry.matchedPredicateBranches.length + entry.parameterComparisons.length} matches`}</span>
                    </div>
                    {entry.runtimeCandidateTraces.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Runtime candidate traces</strong>
                          <span>{entry.runtimeCandidateTraces.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.runtimeCandidateTraces.map((candidateTrace) => (
                            <QueryBuilderRuntimeCandidateTraceReview
                              {...runtimeCandidate}
                              candidateTrace={candidateTrace}
                              groupKey={focusedGroupKey ?? ""}
                              key={`focused-causal-candidate:${entry.stepIndex}:${candidateTrace.location}:${candidateTrace.candidatePath}:${candidateTrace.candidateAccessor}`}
                              mode="focused_chain"
                              scope="focused_chain"
                              stepIndex={entry.stepIndex}
                            />
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {entry.truthTableRows.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Step truth table</strong>
                          <span>{entry.truthTableRows.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.truthTableRows.map((row) => (
                            <div
                              className={`run-surface-query-builder-trace-step is-${row.result ? "success" : "muted"}`}
                              key={`focused-causal-truth:${entry.stepIndex}:${row.location}:${row.expression}`}
                            >
                              <strong>{row.expression}</strong>
                              <p>{row.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {entry.shortCircuitTraces.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Short-circuit notes</strong>
                          <span>{entry.shortCircuitTraces.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.shortCircuitTraces.map((trace) => (
                            <div
                              className="run-surface-query-builder-trace-step is-warning"
                              key={`focused-causal-short-circuit:${entry.stepIndex}:${trace.location}:${trace.detail}`}
                            >
                              <strong>{trace.location}</strong>
                              <p>{trace.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {entry.matchedPredicateBranches.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Matched predicate branches</strong>
                          <span>{entry.matchedPredicateBranches.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.matchedPredicateBranches.map((match) => (
                            <div
                              className="run-surface-query-builder-trace-step is-success"
                              key={`focused-causal-branch:${entry.stepIndex}:${match.location}:${match.detail}`}
                            >
                              <strong>{match.location}</strong>
                              <p>{match.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {entry.parameterComparisons.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested">
                        <div className="run-surface-query-builder-card-head">
                          <strong>Parameter comparisons</strong>
                          <span>{entry.parameterComparisons.length}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {entry.parameterComparisons.map((comparison) => (
                            <div
                              className="run-surface-query-builder-trace-step is-info"
                              key={`focused-causal-comparison:${entry.stepIndex}:${comparison.location}:${comparison.detail}`}
                            >
                              <strong>{comparison.location}</strong>
                              <p>{comparison.detail}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
                <div className="run-surface-query-builder-actions">
                  <button
                    className="ghost-button"
                    onClick={() => setReplayIndex(entry.stepIndex)}
                    type="button"
                  >
                    Focus replay step
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      <div className="run-surface-query-builder-actions">
        <button
          className="ghost-button"
          onClick={clearReviewOverride}
          type="button"
        >
          Clear review override
        </button>
      </div>
    </div>
  );
}
