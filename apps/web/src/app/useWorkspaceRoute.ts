import { useCallback, useEffect, useState } from "react";
import { ControlWorkspaceId, workspaceFromPathname, workspacePath } from "./workspaces";

function readWorkspaceFromLocation() {
  if (typeof window === "undefined") {
    return "overview" as ControlWorkspaceId;
  }
  return workspaceFromPathname(window.location.pathname);
}

export function useWorkspaceRoute() {
  const [activeWorkspace, setActiveWorkspace] = useState<ControlWorkspaceId>(readWorkspaceFromLocation);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const handlePopState = () => {
      setActiveWorkspace(readWorkspaceFromLocation());
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const navigateToWorkspace = useCallback((workspace: ControlWorkspaceId) => {
    if (typeof window === "undefined") {
      setActiveWorkspace(workspace);
      return;
    }
    const nextPath = workspacePath(workspace);
    if (window.location.pathname !== nextPath) {
      window.history.pushState(window.history.state, "", `${nextPath}${window.location.search}${window.location.hash}`);
    }
    setActiveWorkspace(workspace);
  }, []);

  return {
    activeWorkspace,
    navigateToWorkspace,
  };
}
