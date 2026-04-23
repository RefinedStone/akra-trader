// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div className="market-data-provenance-shared-history">
      <div className="market-data-provenance-history-head">
        <strong>Stitched report policy catalogs</strong>
        <p>
          Review only governance catalogs that can drive stitched report view approval
          defaults, then apply those defaults or jump into the shared catalog workspace.
        </p>
      </div>
      <div className="provider-provenance-governance-summary">
        <strong>
          {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length} stitched catalog(s)
        </strong>
        <span>
          {
            providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter(
              (entry) => entry.status === "active",
            ).length
          }{" "}
          active ·{" "}
          {
            providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.filter(
              (entry) => entry.status === "deleted",
            ).length
          }{" "}
          deleted
        </span>
      </div>
      <div className="filter-bar">
        <label>
          <span>Search</span>
          <input
            onChange={(event) => {
              setProviderProvenanceSchedulerStitchedReportGovernanceCatalogSearch(
                event.target.value,
              );
            }}
            placeholder="catalog, guidance, policy"
            type="text"
            value={providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch}
          />
        </label>
      </div>
      {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Catalog</th>
              <th>Defaults</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs.map((catalog) => (
              <tr key={`provider-scheduler-stitched-governance-catalog-${catalog.catalog_id}`}>
                <td>
                  <strong>{catalog.name}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(catalog.status)} · {catalog.policy_template_ids.length} linked template(s)
                  </p>
                  <p className="run-lineage-symbol-copy">
                    Scope {formatWorkflowToken(catalog.item_type_scope)} ·{" "}
                    {formatWorkflowToken(catalog.action_scope)}
                  </p>
                  <p className="run-lineage-symbol-copy">
                    {catalog.description || "No stitched report catalog description recorded."}
                  </p>
                </td>
                <td>
                  <strong>{catalog.default_policy_template_name ?? "No default policy template"}</strong>
                  <p className="run-lineage-symbol-copy">
                    {formatWorkflowToken(catalog.approval_lane)} ·{" "}
                    {formatWorkflowToken(catalog.approval_priority)}
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
                        applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(
                          catalog,
                        );
                      }}
                      type="button"
                    >
                      Use defaults
                    </button>
                    <button
                      className="ghost-button"
                      disabled={catalog.status !== "active" || !catalog.hierarchy_steps.length}
                      onClick={() => {
                        applyProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalog(
                          catalog,
                        );
                        void stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchy(
                          catalog,
                        );
                      }}
                      type="button"
                    >
                      Stage queue
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        openProviderProvenanceSchedulerStitchedReportGovernancePolicyCatalogInSharedSurface(
                          catalog,
                        );
                      }}
                      type="button"
                    >
                      Open shared catalog
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No stitched report policy catalogs match the current search.</p>
      )}
    </div>
  );
}
