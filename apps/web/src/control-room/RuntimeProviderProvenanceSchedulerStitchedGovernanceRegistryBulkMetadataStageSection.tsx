// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataStageSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <label>
        <span>Name prefix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              name_prefix: event.target.value,
            }))
          }
          placeholder="Ops / "
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_prefix}
        />
      </label>
      <label>
        <span>Name suffix</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              name_suffix: event.target.value,
            }))
          }
          placeholder=" / reviewed"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.name_suffix}
        />
      </label>
      <label>
        <span>Description append</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft((current) => ({
              ...current,
              description_append: event.target.value,
            }))
          }
          placeholder="shift-reviewed"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryBulkDraft.description_append}
        />
      </label>
    </>
  );
}
