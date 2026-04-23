// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitControlsSection({ model }: { model: any }) {
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
    </>
  );
}
