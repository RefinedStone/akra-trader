// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewStateSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewStateSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkApprovalTriggerSection({ model }: { model: any }) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      disabled={
        !selectedProviderProvenanceSchedulerStitchedReportViewIds.length
        || providerProvenanceSchedulerStitchedReportViewBulkAction !== null
      }
      onClick={() => {
        void runProviderProvenanceSchedulerStitchedReportViewBulkGovernance("update");
      }}
      type="button"
    >
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewStateSection model={model} />
    </button>
  );
}
