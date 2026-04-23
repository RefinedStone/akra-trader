// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection";
export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryReviewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched governance registry approval queue</strong>
          <p>
            Review staged governance plans for stitched-report governance registries
            without leaving the registry lifecycle workspace. This keeps queue-slice bundle
            approvals and rollback state next to the registry objects they mutate.
          </p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.total} registry plan(s)
          </strong>
          <span>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.pending_approval_count} pending approval · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.ready_to_apply_count} ready to apply · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary.completed_count} completed
          </span>
        </div>
        <div className="filter-bar">
          <label>
            <span>Queue state</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  queue_state:
                    event.target.value === "pending_approval"
                    || event.target.value === "ready_to_apply"
                    || event.target.value === "completed"
                      ? event.target.value
                      : ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.queue_state}
            >
              <option value={ALL_FILTER_VALUE}>All states</option>
              <option value="pending_approval">Pending approval</option>
              <option value="ready_to_apply">Ready to apply</option>
              <option value="completed">Completed</option>
            </select>
          </label>
          <label>
            <span>Lane</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  approval_lane: event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.approval_lane}
            >
              <option value={ALL_FILTER_VALUE}>All lanes</option>
              {Array.from(
                new Set(
                  providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.map(
                    (entry) => entry.approval_lane,
                  ),
                ),
              ).sort().map((lane) => (
                <option key={lane} value={lane}>
                  {formatWorkflowToken(lane)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Priority</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  approval_priority: event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.approval_priority}
            >
              <option value={ALL_FILTER_VALUE}>All priorities</option>
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>
          <label>
            <span>Policy template</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  policy_template_id:
                    event.target.value === ""
                      ? ""
                      : event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_template_id}
            >
              <option value={ALL_FILTER_VALUE}>All policy templates</option>
              <option value="">No policy template</option>
              {providerProvenanceSchedulerStitchedReportGovernancePolicyTemplates.map((entry) => (
                  <option key={entry.policy_template_id} value={entry.policy_template_id}>
                    {entry.name}
                  </option>
                ))}
            </select>
          </label>
          <label>
            <span>Policy catalog</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  policy_catalog_id:
                    event.target.value === ""
                      ? ""
                      : event.target.value || ALL_FILTER_VALUE,
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.policy_catalog_id}
            >
              <option value={ALL_FILTER_VALUE}>All policy catalogs</option>
              <option value="">No policy catalog</option>
              {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.map((entry) => (
                <option key={entry.catalog_id} value={entry.catalog_id}>
                  {entry.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Search</span>
            <input
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
              placeholder="plan, registry, policy"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.search}
            />
          </label>
          <label>
            <span>Sort</span>
            <select
              onChange={(event) =>
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter((current) => ({
                  ...current,
                  sort: normalizeProviderProvenanceSchedulerNarrativeGovernanceQueueSort(
                    event.target.value,
                  ),
                }))
              }
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueFilter.sort}
            >
              <option value={DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT}>
                Queue priority
              </option>
              <option value="updated_desc">Updated newest</option>
              <option value="updated_asc">Updated oldest</option>
              <option value="created_desc">Created newest</option>
              <option value="created_asc">Created oldest</option>
            </select>
          </label>
        </div>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading ? (
          <p className="empty-state">Loading stitched governance registry approval queue…</p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError ? (
          <p className="market-data-workflow-feedback">
            Stitched governance registry approval queue failed: {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansError}
          </p>
        ) : null}
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPlans.length ? (
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryQueueTableSection
            model={model}
          />
        ) : (
          !providerProvenanceSchedulerStitchedReportGovernanceRegistryPlansLoading
            ? <p className="empty-state">No stitched governance registry plans match the dedicated queue filters.</p>
            : null
        )}
      </div>
      <div className="market-data-provenance-shared-history">
        <div className="market-data-provenance-history-head">
          <strong>Stitched governance registry policy catalogs</strong>
          <p>
            Review only governance catalogs that can drive stitched-governance-registry
            approvals, then apply those defaults or jump into the shared catalog workspace
            when deeper hierarchy maintenance is needed.
          </p>
        </div>
        <div className="provider-provenance-governance-summary">
          <strong>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length} registry catalog(s)
          </strong>
          <span>
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "active").length} active · {" "}
            {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.filter((entry) => entry.status === "deleted").length} deleted
          </span>
        </div>
        <div className="filter-bar">
          <label>
            <span>Search</span>
            <input
              onChange={(event) => {
                setProviderProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch(
                  event.target.value,
                );
              }}
              placeholder="catalog, guidance, registry policy"
              type="text"
              value={providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch}
            />
          </label>
        </div>
        {providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs.length ? (
          <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryPolicyCatalogTableSection
            model={model}
          />
        ) : (
          <p className="empty-state">No stitched governance registry policy catalogs match the current search.</p>
        )}
      </div>
    </>
  );
}
