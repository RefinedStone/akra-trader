// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueResetApplySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <label>
        <span>Policy template</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              policy_template_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_template_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy templates</option>
          <option value="">No policy template</option>
          {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
            .filter((entry) =>
              providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType(
                entry.item_type_scope,
                "stitched_report_view",
              ),
            )
            .map((entry) => (
              <option key={entry.policy_template_id} value={entry.policy_template_id}>
                {entry.name}
              </option>
            ))}
        </select>
      </label>
      <label>
        <span>Policy catalog</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              policy_catalog_id:
                event.target.value === ""
                  ? ""
                  : event.target.value || ALL_FILTER_VALUE,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.policy_catalog_id}
        >
          <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
          <option value="">No policy catalog</option>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((entry) => (
            <option key={entry.catalog_id} value={entry.catalog_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Sort</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
              ...current,
              sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                event.target.value,
              ),
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.sort}
        >
          <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
            Queue priority
          </option>
          <option value="updated_desc">Updated newest</option>
          <option value="updated_asc">Updated oldest</option>
          <option value="created_desc">Created newest</option>
          <option value="created_asc">Created oldest</option>
        </select>
      </label>
    </>
  );
}
