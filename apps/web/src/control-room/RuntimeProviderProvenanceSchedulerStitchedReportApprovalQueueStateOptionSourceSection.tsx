// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueStateOptionSourceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <option value={ALL_FILTER_VALUE}>All states</option>
      <option value="pending_approval">Pending approval</option>
      <option value="ready_to_apply">Ready to apply</option>
      <option value="completed">Completed</option>
    </>
  );
}
