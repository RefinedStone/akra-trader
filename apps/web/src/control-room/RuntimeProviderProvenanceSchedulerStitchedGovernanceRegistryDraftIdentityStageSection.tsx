// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftIdentityStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <label>
        <span>Name</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
              ...current,
              name: event.target.value,
            }))
          }
          placeholder="Lag stitched governance"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.name}
        />
      </label>
      <label>
        <span>Description</span>
        <input
          onChange={(event) =>
            setProviderProvenanceSchedulerStitchedReportGovernanceRegistryDraft((current) => ({
              ...current,
              description: event.target.value,
            }))
          }
          placeholder="Queue slice and default policy bundle"
          type="text"
          value={providerProvenanceSchedulerStitchedReportGovernanceRegistryDraft.description}
        />
      </label>
    </>
  );
}
