// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditEventTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>When</th>
          <th>Action</th>
          <th>Actor</th>
          <th>Detail</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryAudits.map((entry) => (
          <tr key={`provider-scheduler-stitched-governance-registry-audit-${entry.audit_id}`}>
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditWhenCellSection
              entry={entry}
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActionCellSection
              entry={entry}
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditActorCellSection
              entry={entry}
              model={model}
            />
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryAuditDetailCellSection
              entry={entry}
              model={model}
            />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
