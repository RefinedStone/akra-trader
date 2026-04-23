// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableRowSelectionSection({
  model,
  entry,
}: {
  model: any;
  entry: any;
}) {
  const {} = model;

  return (
    <td className="provider-provenance-selection-cell">
      <input
        aria-label={`Select stitched governance registry ${entry.name}`}
        checked={selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet.has(entry.registry_id)}
        onChange={() => {
          toggleProviderProvenanceSchedulerStitchedReportGovernanceRegistrySelection(
            entry.registry_id,
          );
        }}
        type="checkbox"
      />
    </td>
  );
}
