// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerWorkspaceAsyncStateSection } from "./RuntimeProviderProvenanceSchedulerWorkspaceAsyncStateSection";
import { RuntimeProviderProvenanceSchedulerWorkspaceSurfaceSection } from "./RuntimeProviderProvenanceSchedulerWorkspaceSurfaceSection";

export function RuntimeProviderProvenanceSchedulerWorkspaceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerWorkspaceAsyncStateSection model={model} />
      <RuntimeProviderProvenanceSchedulerWorkspaceSurfaceSection model={model} />
    </>
  );
}
