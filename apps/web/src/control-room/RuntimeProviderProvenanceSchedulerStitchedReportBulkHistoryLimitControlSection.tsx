// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkHistoryLimitControlSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
