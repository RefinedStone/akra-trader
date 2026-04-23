// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitPolicyStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
              void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("update");
            }}
            type="button"
          >
            {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
              ? "Previewing…"
              : "Preview bulk edit"}
          </button>
        </div>
      </label>
    </>
  );
}
