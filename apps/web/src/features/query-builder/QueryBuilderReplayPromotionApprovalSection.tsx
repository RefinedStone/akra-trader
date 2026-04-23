import type {
  QueryBuilderReplayPromotionConflict,
  QueryBuilderReplayPromotionPreviewRow,
  QueryBuilderReplayPromotionSummary,
} from "./useQueryBuilderReplayPromotionApprovalFlow";

type QueryBuilderReplayPromotionApprovalSectionProps = {
  approval: {
    approvedSelections: QueryBuilderReplayPromotionPreviewRow[];
    approvalOpen: boolean;
    canReviewReplayFinalSummary: boolean;
    canReviewStagedReplayDraft: boolean;
    diffOnly: boolean;
    finalSummaryOpen: boolean;
    previewRows: QueryBuilderReplayPromotionPreviewRow[];
    stagedSelections: QueryBuilderReplayPromotionPreviewRow[];
    summary: QueryBuilderReplayPromotionSummary;
    visibleApprovalRows: QueryBuilderReplayPromotionPreviewRow[];
  };
  callbacks: {
    applyApprovedReplayDraft: () => void;
    closeReplayApprovalReview: () => void;
    closeReplayFinalSummary: () => void;
    openReplayApprovalReview: () => void;
    openReplayFinalSummary: () => void;
    setDiffOnly: (value: boolean) => void;
    toggleReplayApprovalDecision: (groupKey: string) => void;
    toggleReplayPromotionDecision: (groupKey: string) => void;
  };
  draft: {
    conflicts: QueryBuilderReplayPromotionConflict[];
  };
};

export function QueryBuilderReplayPromotionApprovalSection({
  approval: {
    approvedSelections,
    approvalOpen,
    canReviewReplayFinalSummary,
    canReviewStagedReplayDraft,
    diffOnly,
    finalSummaryOpen,
    previewRows,
    stagedSelections,
    summary,
    visibleApprovalRows,
  },
  callbacks: {
    applyApprovedReplayDraft,
    closeReplayApprovalReview,
    closeReplayFinalSummary,
    openReplayApprovalReview,
    openReplayFinalSummary,
    setDiffOnly,
    toggleReplayApprovalDecision,
    toggleReplayPromotionDecision,
  },
  draft: {
    conflicts,
  },
}: QueryBuilderReplayPromotionApprovalSectionProps) {
  return (
    <>
      <div className="run-surface-query-builder-actions">
        <button
          className="ghost-button"
          disabled={!canReviewStagedReplayDraft}
          onClick={openReplayApprovalReview}
          type="button"
        >
          Review staged replay draft
        </button>
      </div>
      {previewRows.length ? (
        <p className="run-note">
          {`Staged promotion currently applies ${
            stagedSelections.map((entry) => `${entry.group.label} → ${entry.promotedBundle.label}`).join(", ")
            || "no groups"
          } from the current filtered replay edge set.`}
        </p>
      ) : null}
      {conflicts.length ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Promotion conflicts</strong>
            <span>{`${conflicts.length} blocked groups`}</span>
          </div>
          <p className="run-note">
            Promotion is blocked until each target group resolves to a single replay bundle.
          </p>
          <div className="run-surface-query-builder-trace-list">
            {conflicts.map((conflict) => (
              <div
                className="run-surface-query-builder-trace-step is-warning"
                key={`promotion-conflict:${conflict.groupLabel}`}
              >
                <strong>{conflict.groupLabel}</strong>
                <p>{conflict.bundleLabels.join(", ")}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {previewRows.length ? (
        <div className="run-surface-query-builder-trace-list">
          {previewRows.map((row) => {
            const isSelected = stagedSelections.some((entry) => entry.group.key === row.group.key);
            return (
              <div
                className={`run-surface-query-builder-trace-step is-${
                  row.matchesSimulation
                    ? "success"
                    : row.changesCurrent
                      ? "info"
                      : "muted"
                }`}
                key={`promotion-preview:${row.group.key}`}
              >
                <strong>{row.group.label}</strong>
                <p>
                  {`${row.currentStatus} · ${row.currentBundleLabel} → ${row.simulatedStatus} · ${row.simulatedBundleLabel} → draft ${row.promotedBundle.label}`}
                </p>
                <div className="run-surface-query-builder-actions">
                  <button
                    className={`ghost-button${isSelected ? " is-active" : ""}`}
                    onClick={() => toggleReplayPromotionDecision(row.group.key)}
                    type="button"
                  >
                    {isSelected ? "Staged for apply" : "Skipped"}
                  </button>
                </div>
                <div className="run-surface-query-builder-trace-chip-list">
                  <span className={`run-surface-query-builder-trace-chip${row.matchesSimulation ? " is-active" : ""}`}>
                    {row.matchesSimulation ? "Matches simulated bundle" : "Differs from simulated bundle"}
                  </span>
                  <span className={`run-surface-query-builder-trace-chip${row.changesCurrent ? " is-active" : ""}`}>
                    {row.changesCurrent ? "Changes current resolution" : "Keeps current resolution"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}
      {approvalOpen ? (
        <div className="run-surface-query-builder-trace-panel is-nested">
          <div className="run-surface-query-builder-card-head">
            <strong>Replay apply approval</strong>
            <span className="run-surface-query-builder-trace-status is-info">
              {`${approvedSelections.length}/${stagedSelections.length} approved`}
            </span>
          </div>
          <div className="run-surface-query-builder-actions">
            <button
              className="ghost-button"
              onClick={closeReplayApprovalReview}
              type="button"
            >
              Close review
            </button>
            <button
              className="ghost-button"
              disabled={!canReviewReplayFinalSummary}
              onClick={openReplayFinalSummary}
              type="button"
            >
              Review final summary
            </button>
          </div>
          <label className="run-surface-query-builder-checkbox">
            <input
              checked={diffOnly}
              onChange={(event) => setDiffOnly(event.target.checked)}
              type="checkbox"
            />
            <span>Diff-only confirmation</span>
          </label>
          <p className="run-note">
            Review the three-way comparison before apply:
            current live resolution, simulated policy outcome, and promoted replay draft.
          </p>
          {visibleApprovalRows.length ? (
            <div className="run-surface-query-builder-trace-list">
              {visibleApprovalRows.map((row) => {
                const isApproved = approvedSelections.some((entry) => entry.group.key === row.group.key);
                return (
                  <div
                    className={`run-surface-query-builder-trace-step is-${
                      row.matchesSimulation
                        ? "success"
                        : row.changesCurrent
                          ? "info"
                          : "muted"
                    }`}
                    key={`approval-preview:${row.group.key}`}
                  >
                    <strong>{row.group.label}</strong>
                    <div className="run-surface-query-builder-trace-chip-list">
                      <span className="run-surface-query-builder-trace-chip">
                        {`Current · ${row.currentStatus} · ${row.currentBundleLabel}`}
                      </span>
                      <span className="run-surface-query-builder-trace-chip">
                        {`Simulated · ${row.simulatedStatus} · ${row.simulatedBundleLabel}`}
                      </span>
                      <span className="run-surface-query-builder-trace-chip is-active">
                        {`Draft · ${row.promotedBundle.label}`}
                      </span>
                    </div>
                    <div className="run-surface-query-builder-actions">
                      <button
                        className={`ghost-button${isApproved ? " is-active" : ""}`}
                        onClick={() => toggleReplayApprovalDecision(row.group.key)}
                        type="button"
                      >
                        {isApproved ? "Approved" : "Rejected"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="run-surface-query-builder-trace-step is-muted">
              <strong>No approval rows</strong>
              <p>
                {diffOnly
                  ? "Diff-only confirmation is hiding rows that do not differ from the current or simulated state."
                  : "There are no staged replay rows available for approval."}
              </p>
            </div>
          )}
        </div>
      ) : null}
      {finalSummaryOpen ? (
        <div
          aria-modal="true"
          className="run-surface-query-builder-modal-backdrop"
          onClick={closeReplayFinalSummary}
          role="dialog"
        >
          <div
            className="run-surface-query-builder-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="run-surface-query-builder-card-head">
              <strong>Final replay apply summary</strong>
              <span>{`${summary.total} approved rows`}</span>
            </div>
            <p className="run-note">
              Confirm the exact replay draft changes before they become live manual overrides.
              This final summary always shows every approved row, even if diff-only confirmation hid some rows in review.
            </p>
            <div className="run-surface-query-builder-trace-chip-list">
              <span className="run-surface-query-builder-trace-chip is-active">
                {`${summary.changesCurrentCount} change current`}
              </span>
              <span className="run-surface-query-builder-trace-chip">
                {`${summary.matchesSimulationCount} match simulated`}
              </span>
              <span className="run-surface-query-builder-trace-chip">
                {`${Math.max(0, summary.total - summary.matchesSimulationCount)} diverge from simulated`}
              </span>
            </div>
            <div className="run-surface-query-builder-trace-list">
              {approvedSelections.map((row) => (
                <div
                  className={`run-surface-query-builder-trace-step is-${
                    row.matchesSimulation
                      ? "success"
                      : row.changesCurrent
                        ? "info"
                        : "muted"
                  }`}
                  key={`final-approval-preview:${row.group.key}`}
                >
                  <strong>{row.group.label}</strong>
                  <div className="run-surface-query-builder-trace-chip-list">
                    <span className="run-surface-query-builder-trace-chip">
                      {`Current · ${row.currentStatus} · ${row.currentBundleLabel}`}
                    </span>
                    <span className="run-surface-query-builder-trace-chip">
                      {`Simulated · ${row.simulatedStatus} · ${row.simulatedBundleLabel}`}
                    </span>
                    <span className="run-surface-query-builder-trace-chip is-active">
                      {`Draft · ${row.promotedBundle.label}`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="run-surface-query-builder-modal-actions">
              <button
                className="ghost-button"
                onClick={closeReplayFinalSummary}
                type="button"
              >
                Back to approval
              </button>
              <button
                className="ghost-button"
                disabled={!approvedSelections.length}
                onClick={applyApprovedReplayDraft}
                type="button"
              >
                Apply approved replay draft
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
