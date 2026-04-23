// @ts-nocheck
export function RuntimeProviderProvenanceGovernanceCatalogHierarchyRowActionSection({
  step,
}: {
  step: any;
}) {
  return (
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
  );
}
