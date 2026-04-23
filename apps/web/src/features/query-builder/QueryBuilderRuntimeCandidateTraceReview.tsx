import type { Dispatch, SetStateAction } from "react";

import type { Run, RunSurfaceCollectionQueryContract } from "../../controlRoomDefinitions";
import {
  areHydratedRunSurfaceCollectionQueryBuilderStatesEqual,
  buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection,
  buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey,
  doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext,
} from "./model";
import type {
  HydratedRunSurfaceCollectionQueryBuilderState,
  RunSurfaceCollectionQueryBuilderClauseDiffItem,
  RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection,
  RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
  RunSurfaceCollectionQueryRuntimeCandidateSample,
  RunSurfaceCollectionQueryRuntimeCandidateTrace,
} from "./model";

type QueryBuilderRuntimeCandidateTraceReviewProps = {
  activeRuntimeCandidateRunContext: RunSurfaceCollectionQueryRuntimeCandidateContextSelection | null;
  candidateTrace: RunSurfaceCollectionQueryRuntimeCandidateTrace;
  contracts: RunSurfaceCollectionQueryContract[];
  editorClauseState: HydratedRunSurfaceCollectionQueryBuilderState | null;
  focusedRuntimeCandidateSampleKey: string | null;
  groupKey: string;
  mode: "focused_chain" | "active_replay";
  onFocusRuntimeCandidateClauseEditor: (
    clause: HydratedRunSurfaceCollectionQueryBuilderState | null,
    originTraceKey?: string | null,
    previewGroupKey?: string | null,
  ) => void;
  onFocusRuntimeCandidateRunContext?: ((
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
    options?: { artifactHoverKey?: string | null },
  ) => void) | null;
  persistedRuntimeCandidateArtifactSelection: RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection | null;
  pinnedRuntimeCandidateClauseDiffItems: RunSurfaceCollectionQueryBuilderClauseDiffItem[];
  pinnedRuntimeCandidateClauseOriginKey: string | null;
  runtimeCandidateTraceDrillthroughByKey: Record<string, boolean>;
  runtimeRuns?: Run[];
  scope: "focused_chain" | "active_replay";
  setFocusedRuntimeCandidateSampleKey: Dispatch<SetStateAction<string | null>>;
  setRuntimeCandidateTraceDrillthroughByKey: Dispatch<SetStateAction<Record<string, boolean>>>;
  stepIndex: number;
};

function buildRuntimeCandidateTraceDrillthroughKey(
  scope: "focused_chain" | "active_replay",
  stepIndex: number,
  trace: RunSurfaceCollectionQueryRuntimeCandidateTrace,
) {
  return `${scope}:${stepIndex}:${trace.location}:${trace.candidatePath}:${trace.candidateAccessor}`;
}

export function QueryBuilderRuntimeCandidateTraceReview({
  activeRuntimeCandidateRunContext,
  candidateTrace,
  contracts,
  editorClauseState,
  focusedRuntimeCandidateSampleKey,
  groupKey,
  mode,
  onFocusRuntimeCandidateClauseEditor,
  onFocusRuntimeCandidateRunContext,
  persistedRuntimeCandidateArtifactSelection,
  pinnedRuntimeCandidateClauseDiffItems,
  pinnedRuntimeCandidateClauseOriginKey,
  runtimeCandidateTraceDrillthroughByKey,
  runtimeRuns,
  scope,
  setFocusedRuntimeCandidateSampleKey,
  setRuntimeCandidateTraceDrillthroughByKey,
  stepIndex,
}: QueryBuilderRuntimeCandidateTraceReviewProps) {
  const doesRuntimeCandidateSampleMatchActiveContext = (
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  ) =>
    doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext(
      sample,
      activeRuntimeCandidateRunContext,
    );
  const doesRuntimeCandidateSampleMatchPersistedArtifactSelection = (
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  ) =>
    persistedRuntimeCandidateArtifactSelection?.sampleKeys.includes(
      buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
    ) ?? false;
  const doesRuntimeCandidateSampleMatchFocusedKey = (
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  ) =>
    focusedRuntimeCandidateSampleKey === buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample);
  const doesRuntimeCandidateTraceMatchEditorClause = (
    trace: RunSurfaceCollectionQueryRuntimeCandidateTrace,
  ) =>
    areHydratedRunSurfaceCollectionQueryBuilderStatesEqual(trace.editorClause, editorClauseState);
  const resolveRuntimeCandidateSampleArtifactHoverKey = (
    sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  ) => {
    if (
      activeRuntimeCandidateRunContext?.artifactHoverKey
      && sample.runContextArtifactHoverKeys.includes(activeRuntimeCandidateRunContext.artifactHoverKey)
    ) {
      return activeRuntimeCandidateRunContext.artifactHoverKey;
    }
    if (
      persistedRuntimeCandidateArtifactSelection?.artifactHoverKey
      && sample.runContextArtifactHoverKeys.includes(
        persistedRuntimeCandidateArtifactSelection.artifactHoverKey,
      )
    ) {
      return persistedRuntimeCandidateArtifactSelection.artifactHoverKey;
    }
    return sample.runContextArtifactHoverKeys[0] ?? null;
  };

  const drillthroughKey = buildRuntimeCandidateTraceDrillthroughKey(
    scope,
    stepIndex,
    candidateTrace,
  );
  const drillthroughOpen = runtimeCandidateTraceDrillthroughByKey[drillthroughKey] ?? false;
  const traceLinkedFromRunContext =
    Boolean(activeRuntimeCandidateRunContext)
    && candidateTrace.allValues.some(doesRuntimeCandidateSampleMatchActiveContext);
  const traceLinkedFromArtifactSelection =
    Boolean(persistedRuntimeCandidateArtifactSelection)
    && candidateTrace.allValues.some(doesRuntimeCandidateSampleMatchPersistedArtifactSelection);
  const traceLinkedFromClauseEditor = doesRuntimeCandidateTraceMatchEditorClause(candidateTrace);
  const traceFocusedSampleCount =
    focusedRuntimeCandidateSampleKey
      ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchFocusedKey).length
      : 0;
  const tracePinnedSampleCount =
    activeRuntimeCandidateRunContext
      ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchActiveContext).length
      : 0;
  const traceArtifactSelectionSampleCount =
    persistedRuntimeCandidateArtifactSelection
      ? candidateTrace.allValues.filter(doesRuntimeCandidateSampleMatchPersistedArtifactSelection).length
      : 0;
  const {
    traceClauseDiffItems,
    tracePinnedFromClauseDraft,
    traceReevaluationPreview,
    traceReevaluationPreviewDiffItems,
  } = buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection({
    candidateTrace,
    contracts,
    drillthroughKey,
    editorClauseState,
    pinnedRuntimeCandidateClauseDiffItems,
    pinnedRuntimeCandidateClauseOriginKey,
    runtimeRuns: runtimeRuns ?? [],
  });

  const orderedSamples = (
    mode === "focused_chain"
      ? (drillthroughOpen ? candidateTrace.allValues : candidateTrace.sampleValues)
      : (drillthroughOpen ? candidateTrace.allValues : candidateTrace.sampleValues.slice(0, 2))
  ).slice().sort((left, right) => {
    const leftFocused = doesRuntimeCandidateSampleMatchFocusedKey(left);
    const rightFocused = doesRuntimeCandidateSampleMatchFocusedKey(right);
    if (leftFocused !== rightFocused) {
      return leftFocused ? -1 : 1;
    }
    const leftArtifactSelected = doesRuntimeCandidateSampleMatchPersistedArtifactSelection(left);
    const rightArtifactSelected = doesRuntimeCandidateSampleMatchPersistedArtifactSelection(right);
    if (leftArtifactSelected !== rightArtifactSelected) {
      return leftArtifactSelected ? -1 : 1;
    }
    const leftPinned = doesRuntimeCandidateSampleMatchActiveContext(left);
    const rightPinned = doesRuntimeCandidateSampleMatchActiveContext(right);
    if (leftPinned === rightPinned) {
      return left.candidatePath.localeCompare(right.candidatePath);
    }
    return leftPinned ? -1 : 1;
  });

  return (
    <div
      className={`run-surface-query-builder-trace-step is-${candidateTrace.result ? "success" : "muted"} ${
        traceLinkedFromRunContext
        || traceLinkedFromArtifactSelection
        || traceLinkedFromClauseEditor
        || tracePinnedFromClauseDraft
          ? "is-linked"
          : ""
      }`.trim()}
      key={`${scope}:${groupKey}:${stepIndex}:${candidateTrace.location}:${candidateTrace.candidatePath}:${candidateTrace.candidateAccessor}`}
    >
      <strong>{candidateTrace.candidateAccessor}</strong>
      <p>{candidateTrace.detail}</p>
      <div className="run-surface-query-builder-trace-chip-list">
        {mode === "focused_chain" ? (
          <>
            <span className="run-surface-query-builder-trace-chip">
              {candidateTrace.candidatePath}
            </span>
            <span className="run-surface-query-builder-trace-chip">
              {candidateTrace.comparedValue}
            </span>
            <span className="run-surface-query-builder-trace-chip">
              {`${candidateTrace.quantifier.toUpperCase()} quantifier`}
            </span>
            <span className={`run-surface-query-builder-trace-chip${candidateTrace.result ? " is-active" : ""}`}>
              {candidateTrace.result ? "matched" : "not matched"}
            </span>
          </>
        ) : (
          <>
            <span className="run-surface-query-builder-trace-chip">
              {`${candidateTrace.quantifier.toUpperCase()} quantifier`}
            </span>
            <span className="run-surface-query-builder-trace-chip">
              {`${candidateTrace.sampleMatchCount}/${candidateTrace.sampleTotalCount} matched`}
            </span>
            {candidateTrace.runOutcomes.slice(0, 2).map((outcome) => (
              <span
                className={`run-surface-query-builder-trace-chip${outcome.result ? " is-active" : ""}`}
                key={`${scope}:${groupKey}:${stepIndex}:${candidateTrace.location}:${outcome.runId}`}
              >
                {`${outcome.runId} · ${outcome.result ? "true" : "false"}`}
              </span>
            ))}
            {candidateTrace.runOutcomes.length > 2 ? (
              <span className="run-surface-query-builder-trace-chip">
                {`+${candidateTrace.runOutcomes.length - 2} runs`}
              </span>
            ) : null}
          </>
        )}
        {traceLinkedFromRunContext ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            Linked from run context
          </span>
        ) : null}
        {traceLinkedFromArtifactSelection ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            Artifact replay selection
          </span>
        ) : null}
        {traceLinkedFromClauseEditor ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            Linked from clause editor
          </span>
        ) : null}
        {traceFocusedSampleCount ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            {`${traceFocusedSampleCount} focused candidates`}
          </span>
        ) : null}
        {tracePinnedFromClauseDraft ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            Pinned draft origin
          </span>
        ) : null}
        {tracePinnedSampleCount ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            {`${tracePinnedSampleCount} pinned candidates`}
          </span>
        ) : null}
        {traceArtifactSelectionSampleCount ? (
          <span className="run-surface-query-builder-trace-chip is-active">
            {`${traceArtifactSelectionSampleCount} artifact-selected`}
          </span>
        ) : null}
      </div>
      {candidateTrace.editorClause ? (
        <div className="run-surface-query-builder-actions">
          <button
            className="ghost-button"
            onClick={() =>
              onFocusRuntimeCandidateClauseEditor(
                candidateTrace.editorClause,
                drillthroughKey,
                groupKey,
              )}
            type="button"
          >
            Load clause into editor
          </button>
        </div>
      ) : null}
      {traceClauseDiffItems.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Clause draft diff</strong>
            <span>{traceClauseDiffItems.length}</span>
          </div>
          <div className="run-surface-query-builder-trace-list">
            {traceClauseDiffItems
              .slice(0, mode === "focused_chain" ? 6 : 6)
              .map((item) => (
                <div
                  className="run-surface-query-builder-trace-step is-warning"
                  key={`${scope}:${groupKey}:${stepIndex}:clause-diff:${drillthroughKey}:${item.key}`}
                >
                  <strong>{item.label}</strong>
                  <p>{item.detail}</p>
                </div>
              ))}
          </div>
        </div>
      ) : null}
      {traceReevaluationPreview ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Clause re-evaluation preview</strong>
            <span>{`${traceReevaluationPreview.sampleMatchCount}/${traceReevaluationPreview.sampleTotalCount} matched`}</span>
          </div>
          <div className="run-surface-query-builder-trace-chip-list">
            <span className="run-surface-query-builder-trace-chip is-active">
              {`${traceReevaluationPreview.runOutcomes.filter((outcome) => outcome.result).length}/${traceReevaluationPreview.runOutcomes.length} runs true`}
            </span>
            <span className="run-surface-query-builder-trace-chip">
              {`${traceReevaluationPreviewDiffItems.length} changed candidates`}
            </span>
          </div>
          {traceReevaluationPreviewDiffItems.length ? (
            <div className="run-surface-query-builder-trace-list">
              {traceReevaluationPreviewDiffItems
                .slice(0, mode === "focused_chain" ? 6 : 4)
                .map((item) => (
                  <div
                    className="run-surface-query-builder-trace-step is-info"
                    key={`${scope}:${groupKey}:${stepIndex}:reeval:${drillthroughKey}:${item.key}`}
                  >
                    <strong>{item.runId}</strong>
                    <p>{item.detail}</p>
                  </div>
                ))}
            </div>
          ) : (
            <p className="run-note">
              {mode === "focused_chain"
                ? "The current clause draft keeps the same concrete candidate outcomes for this trace."
                : "The current clause draft keeps the same concrete candidate outcomes for this replay step."}
            </p>
          )}
        </div>
      ) : null}
      {mode === "focused_chain" && candidateTrace.runOutcomes.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Quantifier outcomes</strong>
            <span>{`${candidateTrace.runOutcomes.filter((outcome) => outcome.result).length}/${candidateTrace.runOutcomes.length} runs true`}</span>
          </div>
          <div className="run-surface-query-builder-trace-list">
            {candidateTrace.runOutcomes.map((outcome) => (
              <div
                className={`run-surface-query-builder-trace-step is-${outcome.result ? "success" : "muted"}`}
                key={`${scope}:${groupKey}:${stepIndex}:quantifier:${candidateTrace.location}:${outcome.runId}`}
              >
                <strong>{outcome.runId}</strong>
                <p>{outcome.detail}</p>
                <div className="run-surface-query-builder-trace-chip-list">
                  <span className="run-surface-query-builder-trace-chip">
                    {`${outcome.matchedCount}/${outcome.candidateCount} matched`}
                  </span>
                  <span className={`run-surface-query-builder-trace-chip${outcome.result ? " is-active" : ""}`}>
                    {outcome.result ? "quantifier true" : "quantifier false"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {mode === "focused_chain" && candidateTrace.sampleTotalCount ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Concrete payload values</strong>
            <span>{`${candidateTrace.sampleMatchCount}/${candidateTrace.sampleTotalCount} matched`}</span>
          </div>
          <div className="run-surface-query-builder-trace-list">
            {orderedSamples.map((sample) => {
              const sampleLinkedFromRunContext = doesRuntimeCandidateSampleMatchActiveContext(sample);
              const sampleLinkedFromArtifactSelection =
                doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
              const sampleFocused = doesRuntimeCandidateSampleMatchFocusedKey(sample);
              return (
                <div
                  className={`run-surface-query-builder-trace-step is-${sample.result ? "success" : "muted"} ${
                    sampleLinkedFromRunContext
                    || sampleLinkedFromArtifactSelection
                    || sampleFocused
                      ? "is-linked"
                      : ""
                  }`.trim()}
                  key={`${scope}:${groupKey}:${stepIndex}:sample:${sample.runId}:${sample.candidatePath}`}
                >
                  <strong>{sample.candidatePath}</strong>
                  <p>{sample.detail}</p>
                  <div className="run-surface-query-builder-trace-chip-list">
                    <span className="run-surface-query-builder-trace-chip">
                      {sample.candidateValue}
                    </span>
                    <span className={`run-surface-query-builder-trace-chip${sample.result ? " is-active" : ""}`}>
                      {sample.result ? "matched" : "not matched"}
                    </span>
                    {sampleLinkedFromRunContext ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Linked from run context
                      </span>
                    ) : null}
                    {sampleLinkedFromArtifactSelection ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Artifact replay selection
                      </span>
                    ) : null}
                    {sampleFocused ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Focused candidate
                      </span>
                    ) : null}
                  </div>
                  {onFocusRuntimeCandidateRunContext && sample.runContextSection && sample.runContextComponentKey ? (
                    <div className="run-surface-query-builder-actions">
                      <button
                        className="ghost-button"
                        onClick={() => {
                          setFocusedRuntimeCandidateSampleKey(
                            buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
                          );
                          onFocusRuntimeCandidateRunContext(sample, {
                            artifactHoverKey: resolveRuntimeCandidateSampleArtifactHoverKey(sample),
                          });
                        }}
                        type="button"
                      >
                        {sample.runContextLabel
                          ? `Open ${sample.runContextLabel}`
                          : "Open run context"}
                      </button>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
          {candidateTrace.sampleTruncated ? (
            <div className="run-surface-query-builder-actions">
              <button
                className={`ghost-button${drillthroughOpen ? " is-active" : ""}`}
                onClick={() =>
                  setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                    ...current,
                    [drillthroughKey]: !drillthroughOpen,
                  }))}
                type="button"
              >
                {drillthroughOpen
                  ? `Collapse to ${candidateTrace.sampleValues.length} sample candidates`
                  : `Drill through all ${candidateTrace.sampleTotalCount} candidates`}
              </button>
            </div>
          ) : null}
        </div>
      ) : null}
      {mode === "active_replay" && orderedSamples.length ? (
        <div className="run-surface-query-builder-trace-chip-list">
          {orderedSamples.map((sample) => {
            const sampleLinkedFromRunContext = doesRuntimeCandidateSampleMatchActiveContext(sample);
            const sampleLinkedFromArtifactSelection =
              doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
            const sampleFocused = doesRuntimeCandidateSampleMatchFocusedKey(sample);
            return (
              <span
                className={`run-surface-query-builder-trace-chip${
                  sample.result
                  || sampleLinkedFromRunContext
                  || sampleLinkedFromArtifactSelection
                  || sampleFocused
                    ? " is-active"
                    : ""
                }`}
                key={`${scope}:${groupKey}:${stepIndex}:preview-sample:${sample.runId}:${sample.candidatePath}`}
              >
                {`${sample.candidatePath} · ${sample.candidateValue}${
                  sampleFocused
                    ? " · focused"
                    : sampleLinkedFromArtifactSelection
                      ? " · artifact-selected"
                      : sampleLinkedFromRunContext
                        ? " · linked"
                        : ""
                }`}
              </span>
            );
          })}
          {candidateTrace.sampleTruncated && !drillthroughOpen ? (
            <button
              className="ghost-button"
              onClick={() =>
                setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                  ...current,
                  [drillthroughKey]: true,
                }))}
              type="button"
            >
              {`Drill through ${candidateTrace.sampleTotalCount} candidates`}
            </button>
          ) : null}
          {candidateTrace.sampleTruncated && drillthroughOpen ? (
            <button
              className="ghost-button is-active"
              onClick={() =>
                setRuntimeCandidateTraceDrillthroughByKey((current) => ({
                  ...current,
                  [drillthroughKey]: false,
                }))}
              type="button"
            >
              Collapse drill-through
            </button>
          ) : null}
        </div>
      ) : null}
      {mode === "active_replay" && drillthroughOpen && orderedSamples.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Concrete payload drill-through</strong>
            <span>{orderedSamples.length}</span>
          </div>
          <div className="run-surface-query-builder-trace-list">
            {orderedSamples.map((sample) => {
              const sampleLinkedFromRunContext = doesRuntimeCandidateSampleMatchActiveContext(sample);
              const sampleLinkedFromArtifactSelection =
                doesRuntimeCandidateSampleMatchPersistedArtifactSelection(sample);
              const sampleFocused = doesRuntimeCandidateSampleMatchFocusedKey(sample);
              return (
                <div
                  className={`run-surface-query-builder-trace-step is-${sample.result ? "success" : "muted"} ${
                    sampleLinkedFromRunContext
                    || sampleLinkedFromArtifactSelection
                    || sampleFocused
                      ? "is-linked"
                      : ""
                  }`.trim()}
                  key={`${scope}:${groupKey}:${stepIndex}:detail-sample:${sample.runId}:${sample.candidatePath}`}
                >
                  <strong>{sample.candidatePath}</strong>
                  <p>{sample.detail}</p>
                  <div className="run-surface-query-builder-trace-chip-list">
                    <span className="run-surface-query-builder-trace-chip">
                      {sample.candidateValue}
                    </span>
                    <span className={`run-surface-query-builder-trace-chip${sample.result ? " is-active" : ""}`}>
                      {sample.result ? "matched" : "not matched"}
                    </span>
                    {sampleLinkedFromRunContext ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Linked from run context
                      </span>
                    ) : null}
                    {sampleLinkedFromArtifactSelection ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Artifact replay selection
                      </span>
                    ) : null}
                    {sampleFocused ? (
                      <span className="run-surface-query-builder-trace-chip is-active">
                        Focused candidate
                      </span>
                    ) : null}
                  </div>
                  {onFocusRuntimeCandidateRunContext && sample.runContextSection && sample.runContextComponentKey ? (
                    <div className="run-surface-query-builder-actions">
                      <button
                        className="ghost-button"
                        onClick={() => {
                          setFocusedRuntimeCandidateSampleKey(
                            buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample),
                          );
                          onFocusRuntimeCandidateRunContext(sample, {
                            artifactHoverKey: resolveRuntimeCandidateSampleArtifactHoverKey(sample),
                          });
                        }}
                        type="button"
                      >
                        {sample.runContextLabel
                          ? `Open ${sample.runContextLabel}`
                          : "Open run context"}
                      </button>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}
