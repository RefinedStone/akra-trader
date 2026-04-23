// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSelectionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <th>
      <input
        aria-label="Select all stitched governance registries"
        checked={
          providerProvenanceSchedulerStitchedReportGovernanceRegistries.length > 0
          && selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds.length
          === providerProvenanceSchedulerStitchedReportGovernanceRegistries.length
        }
        onChange={toggleAllProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelections}
        type="checkbox"
      />
    </th>
  );
}
