// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection({ model }: { model: any }) {
  const {} = model;

  return providerProvenanceSchedulerStitchedReportGovernancePlans.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>Plan</th>
          <th>Preview</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerStitchedReportGovernancePlans.map((plan) => (
          <tr key={`provider-scheduler-stitched-governance-plan-${plan.plan_id}`}>
            <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueReviewStateSection
              model={model}
              plan={plan}
            />
            <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueMutationSection
              model={model}
              plan={plan}
            />
          </tr>
        ))}
      </tbody>
    </table>
  ) : !providerProvenanceSchedulerStitchedReportGovernancePlansLoading ? (
    <p className="empty-state">
      No stitched report governance plans match the dedicated queue filters.
    </p>
  ) : null;
}
