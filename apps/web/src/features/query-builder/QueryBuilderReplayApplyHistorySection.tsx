import type {
  PredicateRefReplayApplyConflictDraftReview,
  PredicateRefReplayApplyConflictEntry,
  PredicateRefReplayApplyConflictPolicy,
  PredicateRefReplayApplyHistoryEntry,
  PredicateRefReplayApplyHistoryTabIdentity,
  PredicateRefReplayApplySyncAuditEntry,
  PredicateRefReplayApplySyncAuditFilter,
  PredicateRefReplayApplySyncMode,
} from "./model";

type ReplayConflictFocusedDecision = { conflictId: string; decisionKey: string } | null;
type SimulatedCoordinationGroup = { key: string; label: string };

type QueryBuilderReplayApplyHistorySectionProps = {
  callbacks: {
    activateReplayConflictSimulationReview: (review: PredicateRefReplayApplyConflictDraftReview) => void;
    focusReplayApplyConflictSimulationTrace: (groupKey: string, conflictId?: string | null) => void;
    resetPredicateRefReplayApplyConflictDraftSource: (conflictId: string) => void;
    resolvePredicateRefReplayApplyConflict: (
      conflict: PredicateRefReplayApplyConflictEntry,
      resolution: "local" | "remote" | "merged",
      mergedEntry?: PredicateRefReplayApplyHistoryEntry | null,
    ) => void;
    restorePredicateRefReplayApplyHistoryEntry: (entry: PredicateRefReplayApplyHistoryEntry) => void;
    setPredicateRefReplayApplyConflictDraftSource: (
      conflictId: string,
      decisionKey: string,
      source: "local" | "remote",
    ) => void;
    setPredicateRefReplayApplyConflictFocusedDecisionState: (conflictId: string, decisionKey: string) => void;
    setPredicateRefReplayApplyConflictPolicy: (value: PredicateRefReplayApplyConflictPolicy) => void;
    setPredicateRefReplayApplyConflictRowRef: (
      conflictId: string,
      decisionKey: string,
      node: HTMLDivElement | null,
    ) => void;
    setPredicateRefReplayApplySyncAuditFilter: (value: PredicateRefReplayApplySyncAuditFilter) => void;
    setPredicateRefReplayApplySyncMode: (value: PredicateRefReplayApplySyncMode) => void;
  };
  helpers: {
    formatRelativeTimestampLabel: (value?: string | null) => string;
  };
  review: {
    latestSelectedRefTemplateReplayApplyEntry: PredicateRefReplayApplyHistoryEntry | null;
    predicateRefReplayApplyConflictFocusedDecision: ReplayConflictFocusedDecision;
    predicateRefReplayApplyConflictPolicy: PredicateRefReplayApplyConflictPolicy;
    predicateRefReplayApplyConflictSimulationConflictId: string | null;
    predicateRefReplayApplyHistoryTabIdentity: PredicateRefReplayApplyHistoryTabIdentity;
    predicateRefReplayApplySyncAuditFilter: PredicateRefReplayApplySyncAuditFilter;
    predicateRefReplayApplySyncMode: PredicateRefReplayApplySyncMode;
    selectedRefTemplateReplayApplyConflictReviews: PredicateRefReplayApplyConflictDraftReview[];
    selectedRefTemplateReplayApplyConflicts: PredicateRefReplayApplyConflictEntry[];
    selectedRefTemplateReplayApplyHistory: PredicateRefReplayApplyHistoryEntry[];
    selectedRefTemplateReplayApplySyncAuditTrail: PredicateRefReplayApplySyncAuditEntry[];
    simulatedCoordinationGroups: SimulatedCoordinationGroup[];
    visibleSelectedRefTemplateReplayApplySyncAuditTrail: PredicateRefReplayApplySyncAuditEntry[];
  };
};

export function QueryBuilderReplayApplyHistorySection({
  callbacks: {
    activateReplayConflictSimulationReview,
    focusReplayApplyConflictSimulationTrace,
    resetPredicateRefReplayApplyConflictDraftSource,
    resolvePredicateRefReplayApplyConflict,
    restorePredicateRefReplayApplyHistoryEntry,
    setPredicateRefReplayApplyConflictDraftSource,
    setPredicateRefReplayApplyConflictFocusedDecisionState,
    setPredicateRefReplayApplyConflictPolicy,
    setPredicateRefReplayApplyConflictRowRef,
    setPredicateRefReplayApplySyncAuditFilter,
    setPredicateRefReplayApplySyncMode,
  },
  helpers: {
    formatRelativeTimestampLabel,
  },
  review: {
    latestSelectedRefTemplateReplayApplyEntry,
    predicateRefReplayApplyConflictFocusedDecision,
    predicateRefReplayApplyConflictPolicy,
    predicateRefReplayApplyConflictSimulationConflictId,
    predicateRefReplayApplyHistoryTabIdentity,
    predicateRefReplayApplySyncAuditFilter,
    predicateRefReplayApplySyncMode,
    selectedRefTemplateReplayApplyConflictReviews,
    selectedRefTemplateReplayApplyConflicts,
    selectedRefTemplateReplayApplyHistory,
    selectedRefTemplateReplayApplySyncAuditTrail,
    simulatedCoordinationGroups,
    visibleSelectedRefTemplateReplayApplySyncAuditTrail,
  },
}: QueryBuilderReplayApplyHistorySectionProps) {
  return (
    <div className="run-surface-query-builder-trace-panel is-nested">
      <div className="run-surface-query-builder-card-head">
        <strong>Replay apply history</strong>
        <span>{`${selectedRefTemplateReplayApplyHistory.length} entries`}</span>
      </div>
      <div className="run-surface-query-builder-inline-grid">
        <label className="run-surface-query-builder-control">
          <span>Remote sync mode</span>
          <select
            value={predicateRefReplayApplySyncMode}
            onChange={(event) =>
              setPredicateRefReplayApplySyncMode(
                event.target.value as PredicateRefReplayApplySyncMode,
              )}
          >
            <option value="live">Live merge</option>
            <option value="audit_only">Audit only</option>
            <option value="mute_remote">Mute remote</option>
          </select>
          <small>
            {predicateRefReplayApplySyncMode === "live"
              ? "Apply and restore events from other tabs merge into this tab."
              : predicateRefReplayApplySyncMode === "audit_only"
                ? "Remote tab events are logged but do not change this tab history."
                : "Remote tab replay history updates are ignored in this tab."}
          </small>
        </label>
        <label className="run-surface-query-builder-control">
          <span>Conflict policy</span>
          <select
            value={predicateRefReplayApplyConflictPolicy}
            onChange={(event) =>
              setPredicateRefReplayApplyConflictPolicy(
                event.target.value as PredicateRefReplayApplyConflictPolicy,
              )}
          >
            <option value="require_review">Require review</option>
            <option value="prefer_local">Prefer local</option>
            <option value="prefer_remote">Prefer remote</option>
          </select>
          <small>
            {predicateRefReplayApplyConflictPolicy === "require_review"
              ? "Override collisions stay pending until you explicitly resolve them."
              : predicateRefReplayApplyConflictPolicy === "prefer_local"
                ? "Conflicting remote overrides are logged but local history wins."
                : "Conflicting remote overrides replace local history automatically."}
          </small>
        </label>
        <label className="run-surface-query-builder-control">
          <span>Audit filter</span>
          <select
            value={predicateRefReplayApplySyncAuditFilter}
            onChange={(event) =>
              setPredicateRefReplayApplySyncAuditFilter(
                event.target.value as PredicateRefReplayApplySyncAuditFilter,
              )}
          >
            <option value="all">All audit events</option>
            <option value="local">Local only</option>
            <option value="remote">Remote only</option>
            <option value="apply">Apply only</option>
            <option value="restore">Restore only</option>
            <option value="conflict">Conflict only</option>
          </select>
          <small>
            {visibleSelectedRefTemplateReplayApplySyncAuditTrail.length
              ? `${visibleSelectedRefTemplateReplayApplySyncAuditTrail.length} audit events match the current filter.`
              : "No audit events match the current filter."}
          </small>
        </label>
      </div>
      <div className="run-surface-query-builder-trace-chip-list">
        <span className="run-surface-query-builder-trace-chip is-active">
          {`Current tab · ${predicateRefReplayApplyHistoryTabIdentity.label}`}
        </span>
        <span className="run-surface-query-builder-trace-chip">
          {selectedRefTemplateReplayApplySyncAuditTrail.length
            ? `${selectedRefTemplateReplayApplySyncAuditTrail.length} sync audit events`
            : "No sync audit events yet"}
        </span>
      </div>
      <p className="run-note">
        Each confirmed replay apply stores a rollback snapshot of the affected manual bundle
        selections and draft bindings for this template.
      </p>
      {selectedRefTemplateReplayApplyConflicts.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Pending override collisions</strong>
            <span>{`${selectedRefTemplateReplayApplyConflicts.length} pending`}</span>
          </div>
          <p className="run-note">
            Remote replay history updates collided with a local override for the same entry id.
            Resolve each collision to decide which version stays active in this tab.
          </p>
          <div className="run-surface-query-builder-trace-list">
            {selectedRefTemplateReplayApplyConflictReviews.map((review) => (
              <div
                className="run-surface-query-builder-trace-step is-warning"
                key={review.conflict.conflictId}
              >
                <strong>{review.conflict.templateLabel}</strong>
                <p>
                  {`Detected ${formatRelativeTimestampLabel(review.conflict.detectedAt)} from ${review.conflict.sourceTabLabel}.`}
                </p>
                <div className="run-surface-query-builder-trace-chip-list">
                  <span className="run-surface-query-builder-trace-chip">
                    {`Local · ${review.conflict.localEntry.approvedCount} rows · ${review.conflict.localEntry.sourceTabLabel ?? predicateRefReplayApplyHistoryTabIdentity.label}`}
                  </span>
                  <span className="run-surface-query-builder-trace-chip is-active">
                    {`Remote · ${review.conflict.remoteEntry.approvedCount} rows · ${review.conflict.sourceTabLabel}`}
                  </span>
                  <span className="run-surface-query-builder-trace-chip">
                    {`${review.totalDiffCount} differing fields`}
                  </span>
                </div>
                <div className="run-surface-query-builder-trace-chip-list">
                  {review.conflict.remoteEntry.rows.map((row) => (
                    <span className="run-surface-query-builder-trace-chip" key={`${review.conflict.conflictId}:${row.groupKey}`}>
                      {`${row.groupLabel}: ${row.promotedBundleLabel}`}
                    </span>
                  ))}
                </div>
                <div className="run-surface-query-builder-trace-panel is-nested">
                  <div className="run-surface-query-builder-card-head">
                    <strong>Field-level diff</strong>
                    <span>{`${review.totalDiffCount} changed fields`}</span>
                  </div>
                  <div className="run-surface-query-builder-trace-chip-list">
                    {review.summaryDiffs.length ? (
                      <span className="run-surface-query-builder-trace-chip">
                        {`${review.summaryDiffs.length} summary`}
                      </span>
                    ) : null}
                    {review.rowDiffs.length ? (
                      <span className="run-surface-query-builder-trace-chip">
                        {`${review.rowDiffs.length} replay rows`}
                      </span>
                    ) : null}
                    {review.selectionSnapshotDiffs.length ? (
                      <span className="run-surface-query-builder-trace-chip">
                        {`${review.selectionSnapshotDiffs.length} rollback groups`}
                      </span>
                    ) : null}
                    {review.bindingSnapshotDiffs.length ? (
                      <span className="run-surface-query-builder-trace-chip">
                        {`${review.bindingSnapshotDiffs.length} draft bindings`}
                      </span>
                    ) : null}
                  </div>
                  {[
                    { key: "summary", label: "Summary fields", items: review.summaryDiffs },
                    { key: "rows", label: "Replay rows", items: review.rowDiffs },
                    { key: "selection", label: "Rollback groups", items: review.selectionSnapshotDiffs },
                    { key: "binding", label: "Draft bindings", items: review.bindingSnapshotDiffs },
                  ].map((section) =>
                    section.items.length ? (
                      <div className="run-surface-query-builder-trace-panel is-nested" key={`${review.conflict.conflictId}:${section.key}`}>
                        <div className="run-surface-query-builder-card-head">
                          <strong>{section.label}</strong>
                          <span>{`${section.items.length} changed`}</span>
                        </div>
                        <div className="run-surface-query-builder-trace-list">
                          {section.items.map((item) => {
                            const selectedSource = item.editable
                              ? review.selectedSources[item.decisionKey] ?? "local"
                              : null;
                            const canTrace =
                              item.relatedGroupKey
                              && simulatedCoordinationGroups.some((group) => group.key === item.relatedGroupKey);
                            const isFocusedDecision =
                              predicateRefReplayApplyConflictFocusedDecision?.conflictId === review.conflict.conflictId
                              && predicateRefReplayApplyConflictFocusedDecision?.decisionKey === item.decisionKey;
                            return (
                              <div
                                className={`run-surface-query-builder-trace-step is-${
                                  item.editable
                                    ? selectedSource === "remote"
                                      ? "warning"
                                      : "info"
                                    : "muted"
                                }`}
                                ref={(node) =>
                                  setPredicateRefReplayApplyConflictRowRef(
                                    review.conflict.conflictId,
                                    item.decisionKey,
                                    node,
                                  )}
                                key={`${review.conflict.conflictId}:${section.key}:${item.key}`}
                                onClick={() =>
                                  setPredicateRefReplayApplyConflictFocusedDecisionState(
                                    review.conflict.conflictId,
                                    item.decisionKey,
                                  )}
                                onFocusCapture={() =>
                                  setPredicateRefReplayApplyConflictFocusedDecisionState(
                                    review.conflict.conflictId,
                                    item.decisionKey,
                                  )}
                                tabIndex={-1}
                              >
                                <strong>{item.label}</strong>
                                <div className="run-surface-query-builder-trace-chip-list">
                                  <span className={`run-surface-query-builder-trace-chip${selectedSource === "local" ? " is-active" : ""}`}>
                                    {`Local · ${item.localValue}`}
                                  </span>
                                  <span className={`run-surface-query-builder-trace-chip${selectedSource === "remote" ? " is-active" : ""}`}>
                                    {`Remote · ${item.remoteValue}`}
                                  </span>
                                  {!item.editable ? (
                                    <span className="run-surface-query-builder-trace-chip">
                                      Derived
                                    </span>
                                  ) : null}
                                  {isFocusedDecision ? (
                                    <span className="run-surface-query-builder-trace-chip is-active">
                                      Linked from replay
                                    </span>
                                  ) : null}
                                </div>
                                <div className="run-surface-query-builder-actions">
                                  {item.editable ? (
                                    <>
                                      <button
                                        className={`ghost-button${selectedSource === "local" ? " is-active" : ""}`}
                                        onClick={() => {
                                          setPredicateRefReplayApplyConflictFocusedDecisionState(
                                            review.conflict.conflictId,
                                            item.decisionKey,
                                          );
                                          setPredicateRefReplayApplyConflictDraftSource(
                                            review.conflict.conflictId,
                                            item.decisionKey,
                                            "local",
                                          );
                                        }}
                                        type="button"
                                      >
                                        Keep local field
                                      </button>
                                      <button
                                        className={`ghost-button${selectedSource === "remote" ? " is-active" : ""}`}
                                        onClick={() => {
                                          setPredicateRefReplayApplyConflictFocusedDecisionState(
                                            review.conflict.conflictId,
                                            item.decisionKey,
                                          );
                                          setPredicateRefReplayApplyConflictDraftSource(
                                            review.conflict.conflictId,
                                            item.decisionKey,
                                            "remote",
                                          );
                                        }}
                                        type="button"
                                      >
                                        Accept remote field
                                      </button>
                                    </>
                                  ) : null}
                                  {canTrace ? (
                                    <button
                                      className="ghost-button"
                                      onClick={() =>
                                        focusReplayApplyConflictSimulationTrace(
                                          item.relatedGroupKey ?? "",
                                          review.conflict.conflictId,
                                        )}
                                      type="button"
                                    >
                                      Trace in simulation
                                    </button>
                                  ) : null}
                                </div>
                                {!item.editable && section.key === "summary" ? (
                                  <p className="run-note">
                                    Derived summary counts follow the replay row selection that survives resolution.
                                  </p>
                                ) : null}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ) : null,
                  )}
                </div>
                <div className="run-surface-query-builder-trace-panel is-nested">
                  <div className="run-surface-query-builder-card-head">
                    <strong>What-if review</strong>
                    <span>Local, merged, and remote outcome</span>
                  </div>
                  <div className="run-surface-query-builder-trace-chip-list">
                    <span className="run-surface-query-builder-trace-chip">
                      {`${review.editableDiffCount} editable fields`}
                    </span>
                    <span className={`run-surface-query-builder-trace-chip${review.hasRemoteSelection ? " is-active" : ""}`}>
                      {`${review.selectedRemoteCount} remote selections`}
                    </span>
                    <span className={`run-surface-query-builder-trace-chip${review.hasMixedSelection ? " is-active" : ""}`}>
                      {review.hasMixedSelection ? "Partial merge staged" : "No partial merge staged"}
                    </span>
                  </div>
                  <div className="run-surface-query-builder-trace-list">
                    {[review.localPreview, review.mergedPreview, review.remotePreview].map((preview) => (
                      <div
                        className={`run-surface-query-builder-trace-step is-${
                          preview.resolution === "local" ? "info" : "warning"
                        }`}
                        key={`${review.conflict.conflictId}:${preview.resolution}`}
                      >
                        <strong>{preview.title}</strong>
                        <p>{preview.effect}</p>
                        <div className="run-surface-query-builder-trace-chip-list">
                          <span className="run-surface-query-builder-trace-chip">
                            {`${preview.entry.approvedCount} approved rows`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${preview.entry.changedCurrentCount} changed current`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {`${preview.entry.matchesSimulationCount} matched simulated`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {preview.snapshotSummary}
                          </span>
                          {preview.matchesLocal ? (
                            <span className="run-surface-query-builder-trace-chip">
                              Matches local
                            </span>
                          ) : null}
                          {preview.matchesRemote ? (
                            <span className="run-surface-query-builder-trace-chip">
                              Matches remote
                            </span>
                          ) : null}
                        </div>
                        <div className="run-surface-query-builder-trace-chip-list">
                          {preview.rowSummaries.length ? (
                            preview.rowSummaries.map((summary, index) => (
                              <span
                                className="run-surface-query-builder-trace-chip"
                                key={`${review.conflict.conflictId}:${preview.resolution}:row:${index}`}
                              >
                                {summary}
                              </span>
                            ))
                          ) : (
                            <span className="run-surface-query-builder-trace-chip">
                              No replay rows recorded
                            </span>
                          )}
                        </div>
                        <div className="run-surface-query-builder-actions">
                          {preview.resolution === "merged" ? (
                            <>
                              <button
                                className={`ghost-button${
                                  predicateRefReplayApplyConflictSimulationConflictId === review.conflict.conflictId
                                    ? " is-active"
                                    : ""
                                }`}
                                onClick={() => activateReplayConflictSimulationReview(review)}
                                type="button"
                              >
                                {predicateRefReplayApplyConflictSimulationConflictId === review.conflict.conflictId
                                  ? "Simulation override active"
                                  : "Run reviewed merge in simulation"}
                              </button>
                              <button
                                className="ghost-button"
                                disabled={!review.hasRemoteSelection}
                                onClick={() =>
                                  resolvePredicateRefReplayApplyConflict(
                                    review.conflict,
                                    "merged",
                                    review.mergedEntry,
                                  )}
                                type="button"
                              >
                                Apply reviewed merge
                              </button>
                              <button
                                className="ghost-button"
                                disabled={!review.hasRemoteSelection}
                                onClick={() =>
                                  resetPredicateRefReplayApplyConflictDraftSource(
                                    review.conflict.conflictId,
                                  )}
                                type="button"
                              >
                                Reset merge draft
                              </button>
                            </>
                          ) : (
                            <button
                              className="ghost-button"
                              onClick={() =>
                                resolvePredicateRefReplayApplyConflict(
                                  review.conflict,
                                  preview.resolution,
                                )}
                              type="button"
                            >
                              {preview.title}
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {selectedRefTemplateReplayApplySyncAuditTrail.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Sync audit trail</strong>
            <span>{`Session scoped · ${predicateRefReplayApplyHistoryTabIdentity.label}`}</span>
          </div>
          {visibleSelectedRefTemplateReplayApplySyncAuditTrail.length ? (
            <div className="run-surface-query-builder-trace-list">
              {visibleSelectedRefTemplateReplayApplySyncAuditTrail.map((auditEntry) => (
                <div
                  className={`run-surface-query-builder-trace-step is-${
                    auditEntry.kind.includes("restore") ? "warning" : "info"
                  }`}
                  key={auditEntry.auditId}
                >
                  <strong>{auditEntry.templateLabel}</strong>
                  <p>{auditEntry.detail}</p>
                  <div className="run-surface-query-builder-trace-chip-list">
                    <span className="run-surface-query-builder-trace-chip is-active">
                      {auditEntry.kind.replaceAll("_", " ")}
                    </span>
                    <span className="run-surface-query-builder-trace-chip">
                      {auditEntry.sourceTabLabel}
                    </span>
                    <span className="run-surface-query-builder-trace-chip">
                      {formatRelativeTimestampLabel(auditEntry.at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="run-surface-query-builder-trace-step is-muted">
              <strong>No matching sync audit events</strong>
              <p>
                {predicateRefReplayApplySyncMode === "mute_remote"
                  ? "Remote sync is muted in this tab, so only local audit events can appear."
                  : "Change the audit filter to inspect a different replay history sync slice."}
              </p>
            </div>
          )}
        </div>
      ) : null}
      {latestSelectedRefTemplateReplayApplyEntry ? (
        <div className="run-surface-query-builder-actions">
          <button
            className="ghost-button"
            onClick={() =>
              restorePredicateRefReplayApplyHistoryEntry(
                latestSelectedRefTemplateReplayApplyEntry,
              )}
            type="button"
          >
            Roll back latest replay apply
          </button>
        </div>
      ) : null}
      <div className="run-surface-query-builder-trace-list">
        {selectedRefTemplateReplayApplyHistory.map((entry) => (
          <div
            className={`run-surface-query-builder-trace-step is-${
              entry.lastRestoredAt ? "muted" : "info"
            }`}
            key={entry.id}
          >
            <strong>{entry.templateLabel}</strong>
            <p>
              {`${entry.approvedCount} approved rows · ${entry.changedCurrentCount} changed current · ${entry.matchesSimulationCount} matched simulated · ${formatRelativeTimestampLabel(entry.appliedAt)}`}
            </p>
            <div className="run-surface-query-builder-trace-chip-list">
              {entry.sourceTabLabel ? (
                <span className="run-surface-query-builder-trace-chip is-active">
                  {`Applied by ${entry.sourceTabLabel}`}
                </span>
              ) : null}
              {entry.lastRestoredByTabLabel ? (
                <span className="run-surface-query-builder-trace-chip">
                  {`Restored by ${entry.lastRestoredByTabLabel}`}
                </span>
              ) : null}
            </div>
            <div className="run-surface-query-builder-trace-chip-list">
              {entry.rows.map((row) => (
                <span
                  className={`run-surface-query-builder-trace-chip${
                    row.matchesSimulation ? " is-active" : ""
                  }`}
                  key={`${entry.id}:${row.groupKey}`}
                >
                  {`${row.groupLabel}: ${row.currentBundleLabel} → ${row.promotedBundleLabel}`}
                </span>
              ))}
            </div>
            <div className="run-surface-query-builder-actions">
              <button
                className="ghost-button"
                onClick={() => restorePredicateRefReplayApplyHistoryEntry(entry)}
                type="button"
              >
                Restore snapshot
              </button>
            </div>
            <p className="run-note">
              {entry.lastRestoredAt
                ? `Last restored ${formatRelativeTimestampLabel(entry.lastRestoredAt)}${entry.lastRestoredByTabLabel ? ` by ${entry.lastRestoredByTabLabel}` : ""}.`
                : "Snapshot available for rollback."}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
