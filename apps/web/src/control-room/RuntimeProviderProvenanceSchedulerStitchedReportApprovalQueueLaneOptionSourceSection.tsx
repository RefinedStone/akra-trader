// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueLaneOptionSourceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <option value={ALL_FILTER_VALUE}>All lanes</option>
      {Array.from(
        new Set(
          providerProvenanceSchedulerStitchedReportGovernancePlans.map((entry) => entry.approval_lane),
        ),
      )
        .sort()
        .map((lane) => (
          <option key={lane} value={lane}>
            {formatWorkflowToken(lane)}
          </option>
        ))}
    </>
  );
}
