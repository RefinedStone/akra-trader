// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterTextInputSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Actor tab</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
              ...current,
              actor_tab_id: event.target.value,
            }))
          }
          placeholder="tab_ops"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.actor_tab_id}
        />
      </label>
      <label>
        <span>Search</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
              ...current,
              search: event.target.value,
            }))
          }
          placeholder="lag reviewed"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.search}
        />
      </label>
    </>
  );
}
