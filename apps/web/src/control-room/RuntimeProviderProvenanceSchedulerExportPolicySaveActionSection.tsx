// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerExportPolicySaveActionSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <button
      className="ghost-button"
      onClick={() => {
        void updateSharedProviderProvenanceSchedulerExportPolicy(
          selectedProviderProvenanceSchedulerExportEntry,
        );
      }}
      type="button"
    >
      Save policy
    </button>
  );
}
