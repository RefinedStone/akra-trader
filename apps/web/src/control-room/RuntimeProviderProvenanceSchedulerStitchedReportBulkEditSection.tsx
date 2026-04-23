// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkFilterStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkFilterStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitPolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitPolicyStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportBulkSelectionSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportBulkSelectionSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportBulkEditSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerStitchedReportBulkSelectionSection model={model} />
      {providerProvenanceSchedulerStitchedReportViews.length ? (
        <div className="provider-provenance-governance-editor">
          <div className="market-data-provenance-history-head">
            <strong>Bulk stitched view edits</strong>
            <p>
              Preview metadata, scheduler slice filters, and export-limit changes across
              multiple saved stitched report views, then approve and apply the staged plan.
            </p>
          </div>
          <div className="filter-bar">
            <RuntimeProviderProvenanceSchedulerStitchedReportBulkFilterStageSection model={model} />
            <RuntimeProviderProvenanceSchedulerStitchedReportBulkLimitPolicyStageSection model={model} />
          </div>
        </div>
      ) : null}
    </>
  );
}
