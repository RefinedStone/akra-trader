// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportPolicyCatalogDerivedStateSection({
  catalog,
  children,
}: {
  catalog: any;
  children: any;
}) {
  const useDefaultsDisabled = catalog.status !== "active";
  const stageQueueDisabled = useDefaultsDisabled || !catalog.hierarchy_steps.length;

  return children({
    useDefaultsDisabled,
    stageQueueDisabled,
  });
}
