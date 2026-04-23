// @ts-nocheck
import { RuntimeProviderProvenanceFocusedPersistedExportHistorySection } from "./RuntimeProviderProvenanceFocusedPersistedExportHistorySection";
import { RuntimeProviderProvenanceFocusedReadbackSection } from "./RuntimeProviderProvenanceFocusedReadbackSection";
import { RuntimeProviderProvenanceFocusedSharedExportRegistrySection } from "./RuntimeProviderProvenanceFocusedSharedExportRegistrySection";
import { RuntimeProviderProvenanceWorkspaceSection } from "./RuntimeProviderProvenanceWorkspaceSection";

export function RuntimeProviderProvenanceFocusedExportSection({ model }: { model: any }) {
  const {} = model;

  return (
    <div>
      <h3>Provider provenance export</h3>
      <div className="run-filter-workbench market-data-provenance-workbench">
        <div className="run-filter-workbench-head">
          <div className="market-data-provenance-copy">
            <strong>Filtered provider readback incidents</strong>
            <p>
              Export the incidents whose selected market context came back from a provider-native
              field path. Filters stay local to this browser, while copied exports also land in
              the shared registry.
            </p>
          </div>
          <div className="run-filter-workbench-actions">
            <button
              className="ghost-button"
              onClick={() => {
                void copyFocusedMarketWorkflowExport();
              }}
              type="button"
            >
              Copy filtered export
            </button>
            <button
              className="ghost-button"
              onClick={resetMarketDataProvenanceExportFilter}
              type="button"
            >
              Reset filters
            </button>
            {marketDataProvenanceExportHistory.length ? (
              <button
                className="ghost-button"
                onClick={clearMarketDataProvenanceExportHistory}
                type="button"
              >
                Clear history
              </button>
            ) : null}
          </div>
        </div>
        <RuntimeProviderProvenanceFocusedReadbackSection model={model} />
        <RuntimeProviderProvenanceFocusedPersistedExportHistorySection model={model} />
        <RuntimeProviderProvenanceFocusedSharedExportRegistrySection model={model} />
        <RuntimeProviderProvenanceWorkspaceSection model={model} />
      </div>
    </div>
  );
}
