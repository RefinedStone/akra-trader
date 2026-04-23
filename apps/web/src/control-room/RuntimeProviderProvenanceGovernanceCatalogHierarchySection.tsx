// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchySection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Catalog hierarchy steps</strong>
          <p>Edit reusable hierarchy steps, bulk-govern selected steps, and restore an older step snapshot without restoring the whole catalog.</p>
        </div>
        {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog ? (
          <>
            <div className="filter-bar">
              <label>
                <span>Selection</span>
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
                  onClick={toggleAllProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelections}
                  type="button"
                >
                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length
                    === selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
                    && selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length
                    ? "Clear all"
                    : "Select all"}
                </button>
              </label>
              <label>
                <span>Bulk name prefix</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      name_prefix: event.target.value,
                    }))
                  }
                  placeholder="Reviewed / "
                  type="text"
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_prefix}
                />
              </label>
              <label>
                <span>Bulk name suffix</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      name_suffix: event.target.value,
                    }))
                  }
                  placeholder=" / approved"
                  type="text"
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.name_suffix}
                />
              </label>
              <label>
                <span>Bulk description</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      description_append: event.target.value,
                    }))
                  }
                  placeholder="shared governance note"
                  type="text"
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.description_append}
                />
              </label>
              <label>
                <span>Bulk template link</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      template_id: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.template_id}
                >
                  <option value="">Keep current link</option>
                  {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                    <option key={entry.template_id} value={entry.template_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Clear link</span>
                <input
                  checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.clear_template_link}
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      clear_template_link: event.target.checked,
                    }))
                  }
                  type="checkbox"
                />
              </label>
              <label>
                <span>Action</span>
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("delete");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "delete"
                    ? "Deleting…"
                    : "Delete selected"}
                </button>
              </label>
              <label>
                <span>Action</span>
                <button
                  className="ghost-button"
                  disabled={!selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds.length}
                  onClick={() => {
                    void runProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction("update");
                  }}
                  type="button"
                >
                  {providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkAction === "update"
                    ? "Updating…"
                    : "Update selected"}
                </button>
              </label>
            </div>
            <div className="filter-bar">
              <label>
                <span>Bulk query patch</span>
                <textarea
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      query_patch: event.target.value,
                    }))
                  }
                  placeholder='{"scheduler_alert_status":"resolved"}'
                  rows={3}
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.query_patch}
                />
              </label>
              <label>
                <span>Bulk layout patch</span>
                <textarea
                  onChange={(event) =>
                    setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft((current) => ({
                      ...current,
                      layout_patch: event.target.value,
                    }))
                  }
                  placeholder='{"show_recent_exports":true}'
                  rows={3}
                  value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepBulkDraft.layout_patch}
                />
              </label>
            </div>
            {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th aria-label="Select step">Sel</th>
                    <th>Step</th>
                    <th>Patch</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.map((step, index) => (
                    <tr key={step.step_id ?? `${step.item_type}-${index}`}>
                      <td>
                        <input
                          checked={step.step_id ? selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet.has(step.step_id) : false}
                          disabled={!step.step_id}
                          onChange={() => {
                            if (step.step_id) {
                              toggleProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepSelection(step.step_id);
                            }
                          }}
                          type="checkbox"
                        />
                      </td>
                      <td>
                        <strong>{step.step_id ?? `step ${index + 1}`}</strong>
                        <p className="run-lineage-symbol-copy">
                          {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(step)}
                        </p>
                        {step.source_template_name || step.source_template_id ? (
                          <p className="run-lineage-symbol-copy">
                            Source template: {step.source_template_name ?? step.source_template_id}
                          </p>
                        ) : null}
                        <p className="run-lineage-symbol-copy">
                          {index + 1} of {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps.length}
                        </p>
                      </td>
                      <td>
                        <strong>{step.item_ids.length} target(s)</strong>
                        <p className="run-lineage-symbol-copy">
                          {step.item_ids.join(", ")}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {Object.keys(step.query_patch ?? {}).length
                            ? `query ${JSON.stringify(step.query_patch)}`
                            : "no query patch"}
                          {step.item_type === "registry"
                            ? ` · ${
                                Object.keys(step.layout_patch ?? {}).length
                                  ? `layout ${JSON.stringify(step.layout_patch)}`
                                  : "no layout patch"
                              }`
                            : ""}
                        </p>
                      </td>
                      <td>
                        <div className="market-data-provenance-history-actions">
                          <button
                            className="ghost-button"
                            disabled={!step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                            onClick={() => {
                              editProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep(step);
                            }}
                            type="button"
                          >
                            Edit
                          </button>
                          <button
                            className="ghost-button"
                            disabled={!step.step_id}
                            onClick={() => {
                              setSelectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId(
                                step.step_id ?? null,
                              );
                            }}
                            type="button"
                          >
                            Versions
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">No hierarchy steps are currently captured on this policy catalog.</p>
            )}
            <div className="market-data-provenance-shared-history">
              <div className="market-data-provenance-history-head">
                <strong>Hierarchy step editor</strong>
                <p>Edit one captured step directly. Empty JSON clears the current patch.</p>
              </div>
              {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
                <div className="filter-bar">
                  <label>
                    <span>Targets</span>
                    <input
                      onChange={(event) =>
                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                          ...current,
                          item_ids_text: event.target.value,
                        }))
                      }
                      placeholder="id_1, id_2"
                      type="text"
                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.item_ids_text}
                    />
                  </label>
                  <label>
                    <span>Name prefix</span>
                    <input
                      onChange={(event) =>
                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                          ...current,
                          name_prefix: event.target.value,
                        }))
                      }
                      placeholder="Reviewed / "
                      type="text"
                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_prefix}
                    />
                  </label>
                  <label>
                    <span>Name suffix</span>
                    <input
                      onChange={(event) =>
                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                          ...current,
                          name_suffix: event.target.value,
                        }))
                      }
                      placeholder=" / approved"
                      type="text"
                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.name_suffix}
                    />
                  </label>
                  <label>
                    <span>Description</span>
                    <input
                      onChange={(event) =>
                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                          ...current,
                          description_append: event.target.value,
                        }))
                      }
                      placeholder="shared governance note"
                      type="text"
                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.description_append}
                    />
                  </label>
                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
                    <>
                      <label>
                        <span>Template link</span>
                        <select
                          onChange={(event) =>
                            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                              ...current,
                              template_id: event.target.value,
                            }))
                          }
                          value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.template_id}
                        >
                          <option value="">No explicit template link</option>
                          {providerProvenanceSchedulerNarrativeTemplates.map((entry) => (
                            <option key={entry.template_id} value={entry.template_id}>
                              {entry.name}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label>
                        <span>Clear link</span>
                        <input
                          checked={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.clear_template_link}
                          onChange={(event) =>
                            setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                              ...current,
                              clear_template_link: event.target.checked,
                            }))
                          }
                          type="checkbox"
                        />
                      </label>
                    </>
                  ) : null}
                  <label>
                    <span>Action</span>
                    <button
                      className="ghost-button"
                      onClick={() => {
                        void saveProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep();
                      }}
                      type="button"
                    >
                      Save step
                    </button>
                  </label>
                  <label>
                    <span>Action</span>
                    <button
                      className="ghost-button"
                      onClick={resetProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft}
                      type="button"
                    >
                      Clear draft
                    </button>
                  </label>
                </div>
              ) : (
                <p className="empty-state">Select a hierarchy step row and choose Edit to stage it in the editor.</p>
              )}
              {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep ? (
                <div className="filter-bar">
                  <label>
                    <span>Query patch</span>
                    <textarea
                      onChange={(event) =>
                        setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                          ...current,
                          query_patch: event.target.value,
                        }))
                      }
                      placeholder='{"scheduler_alert_status":"resolved"}'
                      rows={4}
                      value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.query_patch}
                    />
                  </label>
                  {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep.item_type === "registry" ? (
                    <label>
                      <span>Layout patch</span>
                      <textarea
                        onChange={(event) =>
                          setProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft((current) => ({
                            ...current,
                            layout_patch: event.target.value,
                          }))
                        }
                        placeholder='{"show_recent_exports":true}'
                        rows={4}
                        value={providerProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft.layout_patch}
                      />
                    </label>
                  ) : null}
                </div>
              ) : null}
            </div>
            <div className="market-data-provenance-shared-history">
              <div className="market-data-provenance-history-head">
                <strong>Hierarchy step versions</strong>
                <p>Use the loaded catalog revision history to stage a prior step snapshot or restore that step only.</p>
              </div>
              {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.length ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Revision</th>
                      <th>Step</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions.map((entry) => (
                      <tr key={`${entry.revision.revision_id}:${entry.step.step_id ?? "step"}`}>
                        <td>
                          <strong>{entry.revision.revision_id}</strong>
                          <p className="run-lineage-symbol-copy">
                            {entry.revision.reason}
                          </p>
                          <p className="run-lineage-symbol-copy">
                            {formatTimestamp(entry.revision.recorded_at)}
                          </p>
                        </td>
                        <td>
                          <strong>{entry.step.step_id ?? "unknown step"}</strong>
                          <p className="run-lineage-symbol-copy">
                            {formatProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepSummary(entry.step)}
                          </p>
                          {entry.step.source_template_name || entry.step.source_template_id ? (
                            <p className="run-lineage-symbol-copy">
                              Source template: {entry.step.source_template_name ?? entry.step.source_template_id}
                            </p>
                          ) : null}
                          <p className="run-lineage-symbol-copy">
                            {entry.position} of {entry.total}
                          </p>
                        </td>
                        <td>
                          <div className="market-data-provenance-history-actions">
                            <button
                              className="ghost-button"
                              onClick={() => {
                                stageProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepDraft(entry.step);
                              }}
                              type="button"
                            >
                              Stage draft
                            </button>
                            <button
                              className="ghost-button"
                              disabled={!entry.step.step_id || selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog.status !== "active"}
                              onClick={() => {
                                void restoreProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersion(entry);
                              }}
                              type="button"
                            >
                              Restore step
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="empty-state">Select a hierarchy step and open Versions to inspect step snapshots across catalog revisions.</p>
              )}
            </div>
          </>
        ) : (
          <p className="empty-state">Select a policy catalog row and open Versions to inspect hierarchy steps.</p>
        )}
      </div>
    </>
  );
}
