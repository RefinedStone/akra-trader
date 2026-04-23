// @ts-nocheck
import { RuntimeProviderProvenanceApprovalQueuePlansTableViewSection } from "./RuntimeProviderProvenanceApprovalQueuePlansTableViewSection";

export function RuntimeProviderProvenanceApprovalQueuePlansTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (providerProvenanceSchedulerNarrativeGovernancePlansLoading) {
    return <p className="empty-state">Loading governance plans…</p>;
  }

  if (providerProvenanceSchedulerNarrativeGovernancePlansError) {
    return (
      <p className="market-data-workflow-feedback">
        Governance plan registry load failed: {providerProvenanceSchedulerNarrativeGovernancePlansError}
      </p>
    );
  }

  return filteredProviderProvenanceSchedulerNarrativeGovernancePlans.length ? (
    <RuntimeProviderProvenanceApprovalQueuePlansTableViewSection model={model} />
  ) : (
    <p className="empty-state">No scheduler governance plans match the current approval queue filters.</p>
  );
}
