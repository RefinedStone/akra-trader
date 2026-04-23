// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditFilterSelectSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Registry</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
              ...current,
              registry_id: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.registry_id}
        >
          <option value="">All registries</option>
          {providerProvenanceSchedulerStitchedReportGovernanceRegistries.map((entry) => (
            <option key={entry.registry_id} value={entry.registry_id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Action</span>
        <select
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter((current) => ({
              ...current,
              action: event.target.value,
            }))
          }
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryAuditFilter.action}
        >
          <option value={ALL_FILTER_VALUE}>All actions</option>
          <option value="created">Created</option>
          <option value="updated">Updated</option>
          <option value="deleted">Deleted</option>
          <option value="restored">Restored</option>
        </select>
      </label>
    </>
  );
}
