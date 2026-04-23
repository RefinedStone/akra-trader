// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogRowSection({
  model,
  catalog,
}: {
  model: any;
  catalog: any;
}) {
  const {} = model;

  return (
    <>
      <td>
        <strong>{catalog.name}</strong>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
        </p>
        <p className="run-lineage-symbol-copy">
          Scope {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
        </p>
        <p className="run-lineage-symbol-copy">
          {catalog.description || "No stitched governance registry catalog description recorded."}
        </p>
      </td>
      <td>
        <strong>
          {catalog.default_policy_template_name ?? "No default policy template"}
        </strong>
        <p className="run-lineage-symbol-copy">
          {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
        </p>
        <p className="run-lineage-symbol-copy">
          {catalog.hierarchy_steps.length} hierarchy step(s)
        </p>
        {catalog.guidance ? (
          <p className="run-lineage-symbol-copy">{catalog.guidance}</p>
        ) : null}
      </td>
      <td>
        <div className="market-data-provenance-history-actions">
          <button
            className="ghost-button"
            disabled={catalog.status !== "active"}
            onClick={() => {
              applyProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalog(catalog);
            }}
            type="button"
          >
            Use defaults
          </button>
          <button
            className="ghost-button"
            onClick={() => {
              openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(catalog);
            }}
            type="button"
          >
            Open shared catalog
          </button>
        </div>
      </td>
    </>
  );
}
