// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportAuditSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportAuditSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkEditSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkEditSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportRevisionReviewSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportRevisionReviewSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportSavedViewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Saved stitched report views</strong>
        <p>
          Store stitched multi-occurrence scheduler report slices as reusable saved views, then
          re-apply, copy, download, or share them without rebuilding the filter set by hand.
        </p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="Lag recovery stitched report"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewDraft.name}
          />
        </label>
        <label>
          <span>Description</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerStitchedReportViewDraft((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="saved stitched occurrence slice"
            type="text"
            value={providerProvenanceSchedulerStitchedReportViewDraft.description}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void saveCurrentProviderProvenanceSchedulerStitchedReportView();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerStitchedReportViewId
                ? "Save changes"
                : "Save stitched view"}
            </button>
            {editingProviderProvenanceSchedulerStitchedReportViewId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerStitchedReportViewDraft();
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
        </label>
      </div>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkEditSection model={model} />
      {providerProvenanceSchedulerStitchedReportViewsLoading ? (
        <p className="empty-state">Loading stitched report views…</p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViewsError ? (
        <p className="market-data-workflow-feedback">
          Stitched report views failed: {providerProvenanceSchedulerStitchedReportViewsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  aria-label="Select all stitched report views"
                  checked={
                    providerProvenanceSchedulerStitchedReportViews.length > 0
                    && selectedProviderProvenanceSchedulerStitchedReportViewIds.length
                      === providerProvenanceSchedulerStitchedReportViews.length
                  }
                  onChange={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
                  type="checkbox"
                />
              </th>
              <th>View</th>
              <th>Slice</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerStitchedReportViews.map((entry) => (
              <tr key={`provider-scheduler-stitched-view-${entry.view_id}`}>
                <td className="provider-provenance-selection-cell">
                  <input
                    aria-label={`Select stitched report view ${entry.name}`}
                    checked={selectedProviderProvenanceSchedulerStitchedReportViewIdSet.has(
                      entry.view_id,
                    )}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerStitchedReportViewSelection(entry.view_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>{entry.name}</strong>
                  <p className="run-lineage-symbol-copy">{entry.filter_summary}</p>
                  <p className="run-lineage-symbol-copy">
                    {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"} ·
                    updated {formatTimestamp(entry.updated_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                    {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                  </p>
                </td>
                <td>
                  <strong>{entry.occurrence_limit} occurrence(s)</strong>
                  <p className="run-lineage-symbol-copy">
                    History {entry.history_limit} · drill-down {entry.drilldown_history_limit}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Focus{" "}
                    {entry.query.focus_scope === "current_focus"
                      ? "current focus"
                      : "all focuses"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void applyProviderProvenanceSchedulerStitchedReportView(entry);
                      }}
                      type="button"
                    >
                      Apply
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void editProviderProvenanceSchedulerStitchedReportView(entry);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      disabled={entry.status !== "active"}
                      onClick={() => {
                        void deleteProviderProvenanceSchedulerStitchedReportViewEntry(entry);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerStitchedReportViewHistory(
                          entry.view_id,
                        );
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerStitchedReportViewId === entry.view_id
                        && selectedProviderProvenanceSchedulerStitchedReportViewHistory
                        ? "Hide versions"
                        : "Versions"}
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void copyProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                      }}
                      type="button"
                    >
                      Copy report
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void downloadProviderProvenanceSchedulerStitchedNarrativeCsvView(entry);
                      }}
                      type="button"
                    >
                      Download CSV
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void shareProviderProvenanceSchedulerStitchedNarrativeReportView(entry);
                      }}
                      type="button"
                    >
                      Share report
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No stitched scheduler report views saved yet.</p>
      )}
      <RuntimeProviderProvenanceSchedulerStitchedReportRevisionReviewSection model={model} />
      <RuntimeProviderProvenanceSchedulerStitchedReportAuditSection model={model} />
    </>
  );
}
