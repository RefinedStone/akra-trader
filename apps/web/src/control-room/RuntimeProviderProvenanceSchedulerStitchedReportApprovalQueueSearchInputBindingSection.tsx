// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputBindingSection({
  model,
  children,
}: {
  model: any;
  children: any;
}) {
  const {} = model;

  const onChange = (event: any) =>
    setProviderProvenanceSchedulerStitchedReportGovernanceQueueFilter((current) => ({
      ...current,
      search: event.target.value,
    }));

  return children({
    onChange,
    value: providerProvenanceSchedulerStitchedReportGovernanceQueueFilter.search,
  });
}
