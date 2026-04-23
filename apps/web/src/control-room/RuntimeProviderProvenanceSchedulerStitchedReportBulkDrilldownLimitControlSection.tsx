// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkDrilldownLimitControlSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
