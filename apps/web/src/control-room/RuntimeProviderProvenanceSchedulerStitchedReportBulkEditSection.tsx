// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkEditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <div className="provider-provenance-governance-bar">
          <div className="provider-provenance-governance-summary">
            <strong>
              {selectedProviderProvenanceSchedulerStitchedReportViewIds.length} selected
            </strong>
            <span>
              {
                selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter(
                  (entry) => entry.status === "active",
                ).length
              }{" "}
              active ·{" "}
              {
                selectedProviderProvenanceSchedulerStitchedReportViewEntries.filter(
                  (entry) => entry.status === "deleted",
                ).length
              }{" "}
              deleted
            </span>
          </div>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              onClick={toggleAllProviderProvenanceSchedulerStitchedReportViewSelections}
              type="button"
            >
              {selectedProviderProvenanceSchedulerStitchedReportViewIds.length
                === providerProvenanceSchedulerStitchedReportViews.length
                ? "Clear all"
                : "Select all"}
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
                || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("delete");
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportViewBulkAction === "delete"
                ? "Previewing…"
                : "Preview delete"}
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
                || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("restore");
              }}
              type="button"
            >
              {providerProvenanceSchedulerStitchedReportViewBulkAction === "restore"
                ? "Previewing…"
                : "Preview restore"}
            </button>
          </div>
        </div>
      ) : null}
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Bulk stitched view edits</strong>
            <p>
              Preview metadata, scheduler slice filters, and export-limit changes across
              multiple saved stitched report views, then approve and apply the staged plan.
            </p>
          </div>
          <div className="filter-bar">
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Ops / "
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / v2"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="reviewed in shift handoff"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Category</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_category: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_category}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>All categories</option>
                <option value="scheduler_lag">scheduler lag</option>
                <option value="scheduler_failure">scheduler failure</option>
              </select>
            </label>
            <label>
              <span>Status</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_status: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_status}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value={ALL_FILTER_VALUE}>All statuses</option>
                <option value="active">active</option>
                <option value="resolved">resolved</option>
              </select>
            </label>
            <label>
              <span>Facet</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    scheduler_alert_narrative_facet:
                      event.target.value === "resolved_narratives"
                      || event.target.value === "post_resolution_recovery"
                      || event.target.value === "recurring_occurrences"
                      || event.target.value === "all_occurrences"
                        ? event.target.value
                        : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
                  }))
                }
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.scheduler_alert_narrative_facet}
              >
                <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
                <option value="all_occurrences">all occurrences</option>
                <option value="resolved_narratives">resolved narratives</option>
                <option value="post_resolution_recovery">post-resolution recovery</option>
                <option value="recurring_occurrences">recurring occurrences</option>
              </select>
            </label>
            <label>
              <span>Window days</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    window_days: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.window_days}
              />
            </label>
            <label>
              <span>Result limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    result_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.result_limit}
              />
            </label>
            <label>
              <span>Occurrence limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    occurrence_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.occurrence_limit}
              />
            </label>
            <label>
              <span>History limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    history_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.history_limit}
              />
            </label>
            <label>
              <span>Drill-down limit</span>
              <input
                inputMode="numeric"
                onChange={(event) =>
                  setProviderProvenanceSchedulerStitchedReportViewBulkDraft((current) => ({
                    ...current,
                    drilldown_history_limit: event.target.value,
                  }))
                }
                placeholder="keep"
                type="text"
                value={providerProvenanceSchedulerStitchedReportViewBulkDraft.drilldown_history_limit}
              />
            </label>
            <label>
              <span>Policy template</span>
              <select
                onChange={(event) => {
                  setProviderProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId(
                    event.target.value,
                  );
                }}
                value={providerProvenanceSchedulerStitchedReportViewGovernancePolicyTemplateId}
              >
                <option value="">Default staged policy</option>
                {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                  .filter(
                    (entry) =>
                      entry.status === "active"
                      && providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                        entry.item_type_scope,
                        "stitched_report_view",
                      ),
                  )
                  .map((entry) => (
                    <option key={entry.policy_template_id} value={entry.policy_template_id}>
                      {entry.name} · {formatWorkflowToken(entry.approval_lane)} ·{" "}
                      {formatWorkflowToken(entry.approval_priority)}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={
                    !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
                    || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
                  }
                  onClick={() => {
                    void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance(
                      "update",
                    );
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
                    ? "Previewing…"
                    : "Preview bulk edit"}
                </button>
              </div>
            </label>
          </div>
        </div>
      ) : null}
    </>
  );
}
