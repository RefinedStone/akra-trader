// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkWindowLimitControlSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
