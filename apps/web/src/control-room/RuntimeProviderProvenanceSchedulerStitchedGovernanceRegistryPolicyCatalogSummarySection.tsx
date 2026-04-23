// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogSummarySection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <div className="provider-provenance-governance-summary">
      <strong>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length} registry catalog(s)
      </strong>
      <span>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
      </span>
    </div>
  );
}
