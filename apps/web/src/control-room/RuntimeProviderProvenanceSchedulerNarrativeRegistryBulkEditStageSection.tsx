// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerNarrativeRegistryBulkEditStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-editor">
      <div className="market-data-provenance-history-head">
        <strong>Advanced bulk edits</strong>
        <p>Preview metadata, query, template-link, or board-layout patches, then approve and apply them with rollback planning.</p>
      </div>
      <div className="filter-bar">
        <label>
          <span>Name prefix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                name_prefix: event.target.value,
              }))
            }
            placeholder="Ops / "
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.name_prefix}
          />
        </label>
        <label>
          <span>Name suffix</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                name_suffix: event.target.value,
              }))
            }
            placeholder=" / board"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.name_suffix}
          />
        </label>
        <label>
          <span>Description append</span>
          <input
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                description_append: event.target.value,
              }))
            }
            placeholder="shared governance update"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.description_append}
          />
        </label>
        <label>
          <span>Category</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                scheduler_alert_category: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_category}
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
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                scheduler_alert_status: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_status}
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
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
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
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.scheduler_alert_narrative_facet}
          >
            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
            <option value="all_occurrences">all occurrences</option>
            <option value="resolved_narratives">resolved narratives</option>
            <option value="post_resolution_recovery">post-resolution recovery</option>
            <option value="recurring_occurrences">recurring occurrences</option>
          </select>
        </label>
        <label>
          <span>Template link</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                template_id: event.target.value,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.template_id}
          >
            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
            <option value={CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE}>Clear link</option>
            {providerProvenanceSchedulerNarrativeTemplates
              .filter((entry) => entry.status === "active")
              .map((entry) => (
                <option key={entry.template_id} value={entry.template_id}>
                  {entry.name}
                </option>
              ))}
          </select>
        </label>
        <label>
          <span>Rollups</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                show_rollups:
                  event.target.value === "enable" || event.target.value === "disable"
                    ? event.target.value
                    : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_rollups}
          >
            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
            <option value="enable">Enable</option>
            <option value="disable">Disable</option>
          </select>
        </label>
        <label>
          <span>Time series</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                show_time_series:
                  event.target.value === "enable" || event.target.value === "disable"
                    ? event.target.value
                    : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_time_series}
          >
            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
            <option value="enable">Enable</option>
            <option value="disable">Disable</option>
          </select>
        </label>
        <label>
          <span>Recent exports</span>
          <select
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                show_recent_exports:
                  event.target.value === "enable" || event.target.value === "disable"
                    ? event.target.value
                    : KEEP_CURRENT_BULK_GOVERNANCE_VALUE,
              }))
            }
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.show_recent_exports}
          >
            <option value={KEEP_CURRENT_BULK_GOVERNANCE_VALUE}>Keep current</option>
            <option value="enable">Enable</option>
            <option value="disable">Disable</option>
          </select>
        </label>
        <label>
          <span>Window days</span>
          <input
            inputMode="numeric"
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                window_days: event.target.value,
              }))
            }
            placeholder="keep"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.window_days}
          />
        </label>
        <label>
          <span>Result limit</span>
          <input
            inputMode="numeric"
            onChange={(event) =>
              setProviderProvenanceSchedulerNarrativeRegistryBulkDraft((current) => ({
                ...current,
                result_limit: event.target.value,
              }))
            }
            placeholder="keep"
            type="text"
            value={providerProvenanceSchedulerNarrativeRegistryBulkDraft.result_limit}
          />
        </label>
        <label>
          <span>Action</span>
          <div className="market-data-provenance-history-actions">
            <button
              className="ghost-button"
              disabled={!selectedProviderProvenanceSchedulerNarrativeRegistryIds.length || providerProvenanceSchedulerNarrativeRegistryBulkAction !== null}
              onClick={() => {
                void runProviderProvenanceSchedulerNarrativeRegistryBulkGovernance("update");
              }}
              type="button"
            >
              {providerProvenanceSchedulerNarrativeRegistryBulkAction === "update"
                ? "Previewing…"
                : "Preview bulk edit"}
            </button>
          </div>
        </label>
      </div>
    </div>
  );
}
