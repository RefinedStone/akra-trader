// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkOccurrenceLimitControlSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
