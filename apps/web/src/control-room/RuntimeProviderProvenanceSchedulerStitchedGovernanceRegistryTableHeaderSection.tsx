// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <thead>
      <tr>
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryTableHeaderSelectionSection
          model={model}
        />
        <th>Registry</th>
        <th>Queue slice</th>
        <th>Action</th>
      </tr>
    </thead>
  );
}
