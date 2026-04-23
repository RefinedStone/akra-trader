// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportBulkPreviewStateSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceSchedulerStitchedReportViewBulkAction === "update"
        ? "Previewing…"
        : "Preview bulk edit"}
    </>
  );
}
