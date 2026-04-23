// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportsRegistryRowActionSection } from "./RuntimeProviderProvenanceSchedulerExportsRegistryRowActionSection";
import { RuntimeProviderProvenanceSchedulerExportsRegistryRowDetailSection } from "./RuntimeProviderProvenanceSchedulerExportsRegistryRowDetailSection";

export function RuntimeProviderProvenanceSchedulerExportsRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return providerProvenanceSchedulerExportsLoading ? (
    <p className="empty-state">Loading shared scheduler export registry…</p>
  ) : providerProvenanceSchedulerExportsError ? (
    <p className="market-data-workflow-feedback">
      Shared scheduler export registry failed: {providerProvenanceSchedulerExportsError}
    </p>
  ) : providerProvenanceSchedulerExports.length ? (
    <table className="data-table">
      <thead>
        <tr>
          <th>Exported</th>
          <th>Status</th>
          <th>Delivery</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {providerProvenanceSchedulerExports.map((entry) => (
          <tr key={`provider-scheduler-export-${entry.job_id}`}>
            <RuntimeProviderProvenanceSchedulerExportsRegistryRowDetailSection entry={entry} />
            <RuntimeProviderProvenanceSchedulerExportsRegistryRowActionSection entry={entry} />
          </tr>
        ))}
      </tbody>
    </table>
  ) : (
    <p className="empty-state">No shared scheduler exports have been recorded yet.</p>
  );
}
