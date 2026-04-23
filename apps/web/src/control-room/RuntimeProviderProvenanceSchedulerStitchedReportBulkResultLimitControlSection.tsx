// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkResultLimitControlSection({ model }: { model: any }) {
  const {} = model;

  return (
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
  );
}
