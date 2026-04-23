// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogRegistryTableSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsLoading ? (
        <p className="empty-state">Loading governance policy catalogs…</p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError ? (
        <p className="market-data-workflow-feedback">
          Governance policy catalog load failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th aria-label="Select catalog">Sel</th>
              <th>Catalog</th>
              <th>Defaults</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.map((catalog) => (
              <tr key={catalog.catalog_id}>
                <td>
                  <input
                    checked={selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet.has(catalog.catalog_id)}
                    onChange={() => {
                      toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelection(catalog.catalog_id);
                    }}
                    type="checkbox"
                  />
                </td>
                <td>
                  <strong>{catalog.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {catalog.description || "No description."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {catalog.policy_template_names.join(", ") || "No linked templates."}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(catalog.status)} · {catalog.revision_count} revision(s) · updated {formatTimestamp(catalog.updated_at)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(catalog.hierarchy_steps)}
                  </p>
                </td>
                <td>
                  <strong>{catalog.default_policy_template_name ?? "No default template"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(catalog.item_type_scope)} · {formatWorkflowToken(catalog.action_scope)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(catalog.approval_lane)} · {formatWorkflowToken(catalog.approval_priority)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {catalog.created_by_tab_label ?? catalog.created_by_tab_id ?? "unknown tab"}
                  </p>
                </td>
                <td>
                  <div className="market-data-provenance-history-actions">
                    <button
                      className="ghost-button"
                      disabled={catalog.status !== "active"}
                      onClick={() => {
                        applyProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                      }}
                      type="button"
                    >
                      Apply catalog
                    </button>
                    <button
                      className="ghost-button"
                      disabled={catalog.status !== "active"}
                      onClick={() => {
                        void captureProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyForCatalog(catalog);
                      }}
                      type="button"
                    >
                      Capture hierarchy
                    </button>
                    <button
                      className="ghost-button"
                      disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
                      onClick={() => {
                        void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(catalog);
                      }}
                      type="button"
                    >
                      Stage queue
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void removeProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog(catalog);
                      }}
                      type="button"
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory(
                          catalog.catalog_id,
                        );
                      }}
                      type="button"
                    >
                      {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId === catalog.catalog_id
                        && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory
                        ? "Hide versions"
                        : "Versions"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No governance policy catalogs saved yet.</p>
      )}
    </>
  );
}
