// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSearchSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <label>
      <span>Search</span>
      <input
        onChange={(event) => {
          setProviderProvenanceSchedulerStitchedReportGovernanceRegistrySearch(
            event.target.value,
          );
        }}
        placeholder="registry, queue, policy"
        type="text"
        value={providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch}
      />
    </label>
  );
}
