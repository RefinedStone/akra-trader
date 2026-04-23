// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryBulkMetadataDescriptionStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
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
  );
}
