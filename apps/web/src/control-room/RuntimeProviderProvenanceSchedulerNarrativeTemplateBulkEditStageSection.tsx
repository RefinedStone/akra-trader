// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeTemplateBulkEditStageSection({
  model,
}: {
  model: any;
}) {
  const {
    ALL_FILTER_VALUE,
    KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
    providerProvenanceSchedulerNarrativeTemplateBulkAction,
    providerProvenanceSchedulerNarrativeTemplateBulkDraft,
    runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance,
    selectedProviderProvenanceSchedulerNarrativeTemplateIds,
    setProviderProvenanceSchedulerNarrativeTemplateBulkDraft,
  } = model;

  return (
    <div className="provider-provenance-governance-editor">
      <div className="market-data-provenance-history-head">
        <strong>Advanced bulk edits</strong>
        <p>Preview metadata or scheduler-lens patches, then approve and apply them with rollback planning.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name prefix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                name_prefix: event.target.value,
              }))
            }
            placeholder="Ops / "
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.name_prefix}
          />
        </label>
        <label>
          <span>Name suffix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                name_suffix: event.target.value,
              }))
            }
            placeholder=" / v2"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.name_suffix}
          />
        </label>
        <label>
          <span>Description append</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                description_append: event.target.value,
              }))
            }
            placeholder="reviewed in shift handoff"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.description_append}
          />
        </label>
        <label>
          <span>Category</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                scheduler_alert_category: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_category}
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
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                scheduler_alert_status: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_status}
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
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
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
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.scheduler_alert_narrative_facet}
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
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                window_days: event.target.value,
              }))
            }
            placeholder="keep"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.window_days}
          />
        </label>
        <label>
          <span>Result limit</span>
          <input
            inputMode="numeric"
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeTemplateBulkDraft((current) => ({
                ...current,
                result_limit: event.target.value,
              }))
            }
            placeholder="keep"
            type="text"
            value={providerProvenanceSchedulerNarrativeTemplateBulkDraft.result_limit}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeTemplateIds.length || providerProvenanceSchedulerNarrativeTemplateBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeTemplateBulkGovernance("update");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeTemplateBulkAction === "update"
                ? "Previewing…"
                : "Preview bulk edit"}
            </button>
          </div>
        </label>
      </div>
    </div>
  );
}
