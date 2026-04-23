// @ts-nocheck
export function RuntimeProviderProvenanceGovernancePolicyCatalogSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Governance policy catalogs</strong>
          <p>Reuse named policy bundles, review catalog revisions, and bulk-govern shared queue defaults without editing each catalog one by one.</p>
        </div>
        {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length ? (
          <div className="filter-bar">
            <label>
              <span>Selection</span>
              <button
                className="ghost-button"
                onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogSelections}
                type="button"
              >
                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds.length
                  === providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs.length
                  ? "Clear all"
                  : "Select all"}
              </button>
              <p className="run-lineage-symbol-copy">
                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length} catalog(s) selected
              </p>
            </label>
            <label>
              <span>Name prefix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }))
                }
                placeholder="Shift "
                type="text"
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_prefix}
              />
            </label>
            <label>
              <span>Name suffix</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }))
                }
                placeholder=" / archived"
                type="text"
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.name_suffix}
              />
            </label>
            <label>
              <span>Description append</span>
              <input
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }))
                }
                placeholder="requires desk review"
                type="text"
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.description_append}
              />
            </label>
            <label>
              <span>Default template</span>
              <select
                onChange={(event) =>
                  setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft((current) => ({
                    ...current,
                    default_policy_template_id: event.target.value,
                  }))
                }
                value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkDraft.default_policy_template_id}
              >
                <option value="">Keep current default</option>
                {providerProvenanceSchedulerNarrativeGovernancePolicyTemplates
                  .filter((entry) => entry.status === "active")
                  .map((entry) => (
                    <option key={entry.policy_template_id} value={entry.policy_template_id}>
                      {entry.name}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              <span>Action</span>
              <div className="market-data-provenance-history-actions">
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("delete");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "delete"
                    ? "Deleting…"
                    : "Delete selected"}
                </button>
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("restore");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "restore"
                    ? "Restoring…"
                    : "Restore selected"}
                </button>
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries.length}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction("update");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogBulkAction === "update"
                    ? "Updating…"
                    : "Apply bulk edit"}
                </button>
              </div>
            </label>
          </div>
        ) : null}
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
        <div className="market-data-provenance-shared-history">
          <div className="market-data-provenance-history-head">
            <strong>Catalog revision history</strong>
            <p>Stage a previous linked-template snapshot or restore it as the active policy catalog.</p>
          </div>
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryLoading ? (
            <p className="empty-state">Loading policy catalog revisions…</p>
          ) : null}
          {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError ? (
            <p className="market-data-workflow-feedback">
              Policy catalog revision history failed: {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryError}
            </p>
          ) : null}
          {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Revision</th>
                  <th>Defaults</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory.history.map((entry) => (
                  <tr key={entry.revision_id}>
                    <td>
                      <strong>{entry.revision_id}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.name}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {entry.reason}
                      </p>
                    </td>
                    <td>
                      <strong>{entry.default_policy_template_name ?? "No default template"}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.policy_template_names.join(", ") || "No linked templates."}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.approval_lane)} / {formatWorkflowToken(entry.approval_priority)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchySummary(entry.hierarchy_steps)}
                      </p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          onClick={() => {
                            setEditingProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId(
                              entry.catalog_id,
                            );
                            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogDraft({
                              name: entry.name,
                              description: entry.description,
                              default_policy_template_id: entry.default_policy_template_id ?? "",
                            });
                            setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds(
                              entry.policy_template_ids,
                            );
                            setProviderProvenanceWorkspaceFeedback(
                              `Policy catalog revision ${entry.revision_id} staged in the editor.`,
                            );
                          }}
                          type="button"
                        >
                          Stage draft
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistoryRevision(
                              entry,
                            );
                          }}
                          type="button"
                        >
                          Restore revision
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-state">Select a policy catalog row and open Versions to inspect revisions.</p>
          )}
        </div>
      </div>
    </>
  );
}
