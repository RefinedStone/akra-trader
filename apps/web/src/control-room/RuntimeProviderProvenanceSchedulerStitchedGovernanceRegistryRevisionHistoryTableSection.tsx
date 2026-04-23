// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionHistoryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Recorded</th>
          <th>Snapshot</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryHistory.history.map((entry) => (
          <tr key={`provider-scheduler-stitched-governance-registry-revision-${entry.revision_id}`}>
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionRecordedCellSection
              entry={entry}
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionSnapshotCellSection
              entry={entry}
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryRevisionActionCellSection
              entry={entry}
              model={model}
            />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
