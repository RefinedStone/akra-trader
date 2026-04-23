import type { MutableRefObject } from "react";

import type {
  HydratedRunSurfaceCollectionQueryBuilderState,
  RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem,
} from "./model";

type ReviewFieldPick = {
  decisionKey: string;
  label: string;
  source: "local" | "remote";
};

type SimulationReplayAttribution = {
  chain: Array<{
    causalLabel: string;
    edgeRoleLabel: string | null;
    stateTransitionLabel: string | null;
    stepIndex: number;
    stepLabel: string;
  }>;
  chainSummary: string;
};

type ClauseReevaluationProjectionTrace = {
  candidateAccessor: string;
  candidatePath: string;
  changedCandidateCount: number;
  diffItems: RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem[];
  editorClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
  focusableDiffSampleKeysByItemKey: Record<string, string | null>;
  groupKey: string;
  drillthroughKey: string;
  key: string;
  matchedCandidateLabel: string;
  matchedRunLabel: string;
  primarySampleKey: string | null;
  stepIndex: number;
  stepLabel: string;
};

type ClauseReevaluationProjection = {
  changedCandidateCount: number;
  previewTraceCount: number;
  projectedTraces: ClauseReevaluationProjectionTrace[];
  tracesWithChangesCount: number;
};

type SimulationGroupBundleDiff = {
  attributedReplayDetail: string | null;
  attributedReplayStepIndex: number;
  attributedReplayStepLabel: string;
  attributedReplayType: string | null;
  clauseReevaluationProjection: ClauseReevaluationProjection | null;
  currentBundleLabel: string;
  currentStatus: string;
  groupKey: string;
  groupLabel: string;
  simulatedBundleLabel: string;
  simulatedStatus: string;
};

type QueryBuilderSimulationDiffReviewSectionProps = {
  callbacks: {
    focusConflictDecision: (conflictId: string, decisionKey: string) => void;
    focusRuntimeCandidateClauseEditor: (
      clause: HydratedRunSurfaceCollectionQueryBuilderState | null,
      originTraceKey?: string | null,
      previewGroupKey?: string | null,
    ) => void;
    focusRuntimeCandidateReplayTrace: (params: {
      diffItemKey?: string | null;
      groupKey?: string | null;
      sampleKey?: string | null;
      stepIndex: number;
      traceKey: string;
    }) => void;
    setClauseReevaluationPreviewSelection: (value: {
      diffItemKey: string | null;
      groupKey: string | null;
      traceKey: string | null;
    }) => void;
    setReplayIndex: (value: number) => void;
    toggleFieldPickSource: (decisionKey: string) => void;
  };
  clausePreview: {
    diffItemRefs: MutableRefObject<Map<string, HTMLDivElement>>;
    selection: {
      diffItemKey: string | null;
      groupKey: string | null;
      traceKey: string | null;
    };
    traceRefs: MutableRefObject<Map<string, HTMLDivElement>>;
  };
  review: {
    activeReviewConflictId: string | null;
    activeStepIndex: number;
    attributionByGroupKey: Record<string, SimulationReplayAttribution | undefined>;
    diffs: SimulationGroupBundleDiff[];
    fieldPicksByGroupKey: Record<string, ReviewFieldPick[]>;
    focusedDecision: { conflictId: string; decisionKey: string } | null;
    primaryFocusGroupKey: string | null;
  };
};

export function QueryBuilderSimulationDiffReviewSection({
  callbacks: {
    focusConflictDecision,
    focusRuntimeCandidateClauseEditor,
    focusRuntimeCandidateReplayTrace,
    setClauseReevaluationPreviewSelection,
    setReplayIndex,
    toggleFieldPickSource,
  },
  clausePreview: {
    diffItemRefs,
    selection,
    traceRefs,
  },
  review: {
    activeReviewConflictId,
    activeStepIndex,
    attributionByGroupKey,
    diffs,
    fieldPicksByGroupKey,
    focusedDecision,
    primaryFocusGroupKey,
  },
}: QueryBuilderSimulationDiffReviewSectionProps) {
  if (!diffs.length) {
    return (
      <p className="run-note">
        This policy would not change the currently resolved bundle choices for the simulated scope.
      </p>
    );
  }

  return (
    <div className="run-surface-query-builder-trace-list">
      {diffs.map((diff) => (
        <div
          className={`run-surface-query-builder-trace-step is-${
            primaryFocusGroupKey === diff.groupKey ? "success" : "info"
          }`}
          key={`simulation-diff:${diff.groupKey}`}
        >
          <strong>{diff.groupLabel}</strong>
          <p>
            {`${diff.currentStatus} · ${diff.currentBundleLabel} → ${diff.simulatedStatus} · ${diff.simulatedBundleLabel}`}
          </p>
          {diff.attributedReplayStepIndex >= 0 ? (
            <div className="run-surface-query-builder-trace-chip-list">
              <span className={`run-surface-query-builder-trace-chip${
                focusedDecision?.conflictId === activeReviewConflictId
                && primaryFocusGroupKey === diff.groupKey
                  ? " is-active"
                  : ""
              }`}>
                {diff.attributedReplayStepLabel}
              </span>
              {diff.attributedReplayType ? (
                <span className="run-surface-query-builder-trace-chip">
                  {diff.attributedReplayType.replaceAll("_", " ")}
                </span>
              ) : null}
              <span className="run-surface-query-builder-trace-chip">
                {attributionByGroupKey[diff.groupKey]?.chain[0]?.causalLabel ?? "Replay attribution"}
              </span>
              {attributionByGroupKey[diff.groupKey]?.chain[0]?.stateTransitionLabel ? (
                <span className="run-surface-query-builder-trace-chip">
                  {attributionByGroupKey[diff.groupKey]?.chain[0]?.stateTransitionLabel}
                </span>
              ) : null}
              {attributionByGroupKey[diff.groupKey]?.chain[0]?.edgeRoleLabel ? (
                <span className="run-surface-query-builder-trace-chip">
                  {attributionByGroupKey[diff.groupKey]?.chain[0]?.edgeRoleLabel}
                </span>
              ) : null}
              <span className="run-surface-query-builder-trace-chip">
                {attributionByGroupKey[diff.groupKey]?.chainSummary ?? "No replay attribution"}
              </span>
            </div>
          ) : null}
          {diff.attributedReplayDetail ? (
            <p className="run-note">{diff.attributedReplayDetail}</p>
          ) : null}
          {attributionByGroupKey[diff.groupKey]?.chain.length ? (
            <div className="run-surface-query-builder-trace-chip-list">
              {attributionByGroupKey[diff.groupKey]?.chain.slice(0, 4).map((entry, index) => (
                <button
                  className={`run-surface-query-builder-trace-chip${
                    entry.stepIndex === activeStepIndex ? " is-active" : ""
                  }`}
                  key={`simulation-diff-chain:${diff.groupKey}:${entry.stepIndex}:${index}`}
                  onClick={() => setReplayIndex(entry.stepIndex)}
                  type="button"
                >
                  {`${entry.stepLabel} · ${entry.causalLabel}`}
                </button>
              ))}
              {attributionByGroupKey[diff.groupKey]?.chain.length
              && attributionByGroupKey[diff.groupKey]!.chain.length > 4 ? (
                <span className="run-surface-query-builder-trace-chip">
                  {`+${attributionByGroupKey[diff.groupKey]!.chain.length - 4} more chain steps`}
                </span>
              ) : null}
            </div>
          ) : null}
          {diff.clauseReevaluationProjection ? (
            <div className="run-surface-query-builder-trace-panel is-nested">
              <div className="run-surface-query-builder-card-head">
                <strong>Clause re-evaluation preview</strong>
                <span>{`${diff.clauseReevaluationProjection.previewTraceCount} traces`}</span>
              </div>
              <div className="run-surface-query-builder-trace-chip-list">
                <span className="run-surface-query-builder-trace-chip is-active">
                  {`${diff.clauseReevaluationProjection.tracesWithChangesCount}/${diff.clauseReevaluationProjection.previewTraceCount} traces changed`}
                </span>
                <span className="run-surface-query-builder-trace-chip">
                  {`${diff.clauseReevaluationProjection.changedCandidateCount} changed candidates`}
                </span>
                <span className="run-surface-query-builder-trace-chip is-active">
                  Linked from clause draft
                </span>
              </div>
              <div className="run-surface-query-builder-trace-list">
                {diff.clauseReevaluationProjection.projectedTraces.slice(0, 3).map((trace) => (
                  <div
                    className={`run-surface-query-builder-trace-step is-info${
                      selection.traceKey === trace.drillthroughKey ? " is-linked" : ""
                    }`}
                    key={`simulation-diff-preview:${diff.groupKey}:${trace.key}`}
                    ref={(node) => {
                      if (node) {
                        traceRefs.current.set(trace.drillthroughKey, node);
                        return;
                      }
                      traceRefs.current.delete(trace.drillthroughKey);
                    }}
                  >
                    <strong>{`${trace.stepLabel} · ${trace.candidateAccessor}`}</strong>
                    <p>{trace.candidatePath}</p>
                    <div className="run-surface-query-builder-trace-chip-list">
                      <button
                        className={`run-surface-query-builder-trace-chip${
                          trace.stepIndex === activeStepIndex ? " is-active" : ""
                        }`}
                        onClick={() => setReplayIndex(trace.stepIndex)}
                        type="button"
                      >
                        {trace.stepLabel}
                      </button>
                      <span className="run-surface-query-builder-trace-chip">
                        {trace.matchedCandidateLabel}
                      </span>
                      <span className="run-surface-query-builder-trace-chip">
                        {trace.matchedRunLabel}
                      </span>
                      <span className={`run-surface-query-builder-trace-chip${
                        trace.changedCandidateCount ? " is-active" : ""
                      }`}>
                        {`${trace.changedCandidateCount} changed candidates`}
                      </span>
                      {selection.traceKey === trace.drillthroughKey ? (
                        <span className="run-surface-query-builder-trace-chip is-active">
                          Linked preview trace
                        </span>
                      ) : null}
                    </div>
                    <div className="run-surface-query-builder-actions">
                      <button
                        className="ghost-button"
                        onClick={() =>
                          focusRuntimeCandidateReplayTrace({
                            diffItemKey: null,
                            groupKey: trace.groupKey,
                            sampleKey: trace.primarySampleKey,
                            stepIndex: trace.stepIndex,
                            traceKey: trace.drillthroughKey,
                          })}
                        type="button"
                      >
                        Focus candidate drill-through
                      </button>
                      {trace.editorClause ? (
                        <button
                          className="ghost-button"
                          onClick={() => {
                            setClauseReevaluationPreviewSelection({
                              diffItemKey: null,
                              groupKey: trace.groupKey,
                              traceKey: trace.drillthroughKey,
                            });
                            focusRuntimeCandidateClauseEditor(
                              trace.editorClause,
                              trace.drillthroughKey,
                              trace.groupKey,
                            );
                          }}
                          type="button"
                        >
                          Load clause into editor
                        </button>
                      ) : null}
                    </div>
                    {trace.diffItems.length ? (
                      <div className="run-surface-query-builder-trace-list">
                        {trace.diffItems.slice(0, 3).map((item) => (
                          <div
                            className={`run-surface-query-builder-trace-step is-info${
                              selection.traceKey === trace.drillthroughKey
                              && selection.diffItemKey === item.key
                                ? " is-linked"
                                : ""
                            }`}
                            key={`simulation-diff-preview-item:${diff.groupKey}:${trace.key}:${item.key}`}
                            ref={(node) => {
                              const refKey = `${trace.drillthroughKey}:${item.key}`;
                              if (node) {
                                diffItemRefs.current.set(refKey, node);
                                return;
                              }
                              diffItemRefs.current.delete(refKey);
                            }}
                          >
                            <strong>{item.runId}</strong>
                            <p>{item.detail}</p>
                            {selection.traceKey === trace.drillthroughKey
                            && selection.diffItemKey === item.key ? (
                              <div className="run-surface-query-builder-trace-chip-list">
                                <span className="run-surface-query-builder-trace-chip is-active">
                                  Linked preview diff
                                </span>
                              </div>
                            ) : null}
                            <div className="run-surface-query-builder-actions">
                              {trace.focusableDiffSampleKeysByItemKey[item.key] ? (
                                <button
                                  className="ghost-button"
                                  onClick={() =>
                                    focusRuntimeCandidateReplayTrace({
                                      diffItemKey: item.key,
                                      groupKey: trace.groupKey,
                                      sampleKey: trace.focusableDiffSampleKeysByItemKey[item.key],
                                      stepIndex: trace.stepIndex,
                                      traceKey: trace.drillthroughKey,
                                    })}
                                  type="button"
                                >
                                  Focus candidate
                                </button>
                              ) : null}
                              {trace.editorClause ? (
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setClauseReevaluationPreviewSelection({
                                      diffItemKey: item.key,
                                      groupKey: trace.groupKey,
                                      traceKey: trace.drillthroughKey,
                                    });
                                    focusRuntimeCandidateClauseEditor(
                                      trace.editorClause,
                                      trace.drillthroughKey,
                                      trace.groupKey,
                                    );
                                  }}
                                  type="button"
                                >
                                  Focus clause editor
                                </button>
                              ) : null}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="run-note">
                        The current clause draft keeps the same concrete candidate outcomes for this replay trace.
                      </p>
                    )}
                  </div>
                ))}
              </div>
              {diff.clauseReevaluationProjection.projectedTraces.length > 3 ? (
                <p className="run-note">
                  {`+${diff.clauseReevaluationProjection.projectedTraces.length - 3} more projected traces`}
                </p>
              ) : null}
            </div>
          ) : null}
          {fieldPicksByGroupKey[diff.groupKey]?.length ? (
            <div className="run-surface-query-builder-trace-chip-list">
              {fieldPicksByGroupKey[diff.groupKey].slice(0, 4).map((pick) => (
                <span
                  className="run-surface-query-builder-trace-chip-list"
                  key={`simulation-diff-pick:${diff.groupKey}:${pick.decisionKey}`}
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
              {fieldPicksByGroupKey[diff.groupKey].length > 4 ? (
                <span className="run-surface-query-builder-trace-chip">
                  {`+${fieldPicksByGroupKey[diff.groupKey].length - 4} more reviewed picks`}
                </span>
              ) : null}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
