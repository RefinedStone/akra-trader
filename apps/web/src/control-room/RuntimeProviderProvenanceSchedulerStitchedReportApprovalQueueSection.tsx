// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection({ model }: { model: any }) {
  return (
    <div className="market-data-provenance-shared-history">
      <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection model={model} />
      {providerProvenanceSchedulerStitchedReportGovernancePlans.length ? (
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
                <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection
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
      ) : null}
    </div>
  );
}
