// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkFilterStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
    </>
  );
}
