// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueRowSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueRowSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Plan</th>
          <th>Preview</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.map((plan) => (
          <tr key={`provider-scheduler-stitched-governance-registry-plan-${plan.plan_id}`}>
            <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueRowSection
              model={model}
              plan={plan}
            />
          </tr>
        ))}
      </tbody>
    </table>
  );
}
