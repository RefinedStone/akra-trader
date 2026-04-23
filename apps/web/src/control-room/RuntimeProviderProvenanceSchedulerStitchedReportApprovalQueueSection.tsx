// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSection({ model }: { model: any }) {
  const {} = model;

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
            <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueActionSection model={model} />
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
