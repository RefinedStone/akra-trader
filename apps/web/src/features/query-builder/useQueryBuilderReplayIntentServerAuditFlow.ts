import { useCallback } from "react";

import {
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
} from "../../controlRoomApi";

function downloadTextPayload(content: string, contentType: string, filename: string) {
  if (typeof window === "undefined") {
    return;
  }
  const blob = new Blob([content], { type: contentType });
  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(objectUrl);
}

export function useQueryBuilderReplayIntentServerAuditFlow(args: any) {
  const {
    predicateRefReplayApplyHistoryTabIdentity,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditIncludeManual,
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
    setReplayIntentServerAuditExportJobTotal,
    setReplayIntentServerAuditExportJobs,
    setReplayIntentServerAuditItems,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
    setReplayIntentServerAuditTotal,
  } = args;
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits = useCallback(async (
    options?: { adminToken?: string; silent?: boolean },
  ) => {
    const adminToken = (options?.adminToken ?? replayIntentServerAuditReadToken.trim())
      || replayIntentServerAuditWriteToken.trim();
    const normalizedLimit = Number.parseInt(replayIntentServerAuditLimit, 10);
    setReplayIntentServerAuditLoading(true);
    if (!options?.silent) {
      setReplayIntentServerAuditStatus(null);
    }
    try {
      const payload = await listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        limit: Number.isFinite(normalizedLimit) ? normalizedLimit : 25,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditItems(payload.items);
      setReplayIntentServerAuditTotal(payload.total);
      if (!options?.silent) {
        setReplayIntentServerAuditStatus({
          message: `Loaded ${payload.items.length} server replay alias audit record${payload.items.length === 1 ? "" : "s"}.`,
          tone: payload.items.length ? "success" : "muted",
        });
      }
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditItems,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
    setReplayIntentServerAuditTotal,
  ]);
  const pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords = useCallback(async (
    pruneMode: "expired" | "matched",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditLoading(true);
    setReplayIntentServerAuditStatus(null);
    try {
      const payload = await pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        includeManual: replayIntentServerAuditIncludeManual,
        pruneMode,
        recordedBefore: replayIntentServerAuditRecordedBefore,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditStatus({
        message:
          pruneMode === "expired"
            ? `Pruned ${payload.deleted_count} expired server replay alias audit record${payload.deleted_count === 1 ? "" : "s"}.`
            : `Pruned ${payload.deleted_count} matched server replay alias audit record${payload.deleted_count === 1 ? "" : "s"}.`,
        tone: payload.deleted_count ? "success" : "muted",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to prune server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditIncludeManual,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
  ]);
  const exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords = useCallback(async (
    exportFormat: "json" | "csv",
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditLoading(true);
    setReplayIntentServerAuditStatus(null);
    try {
      const payload = await exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        exportFormat,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      downloadTextPayload(payload.content, payload.content_type, payload.filename);
      setReplayIntentServerAuditStatus({
        message: `Exported ${payload.record_count} server replay alias audit record${payload.record_count === 1 ? "" : "s"} as ${payload.format.toUpperCase()}.`,
        tone: payload.record_count ? "success" : "muted",
      });
    } catch (error) {
      setReplayIntentServerAuditStatus({
        message: error instanceof Error ? error.message : "Failed to export server replay alias audits.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditLoading(false);
    }
  }, [
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditLoading,
    setReplayIntentServerAuditStatus,
  ]);
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs = useCallback(async (
    options?: { adminToken?: string; silent?: boolean },
  ) => {
    const adminToken = (options?.adminToken ?? replayIntentServerAuditReadToken.trim())
      || replayIntentServerAuditWriteToken.trim();
    const normalizedLimit = Number.parseInt(replayIntentServerAuditLimit, 10);
    setReplayIntentServerAuditExportJobLoading(true);
    if (!options?.silent) {
      setReplayIntentServerAuditExportJobStatus(null);
    }
    try {
      const payload = await listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        exportFormat: "all",
        limit: Number.isFinite(normalizedLimit) ? normalizedLimit : 25,
        requestedByTabId: replayIntentServerAuditSourceTabFilter,
        search: replayIntentServerAuditSearch,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobs(payload.items);
      setReplayIntentServerAuditExportJobTotal(payload.total);
      if (!options?.silent) {
        setReplayIntentServerAuditExportJobStatus({
          message: `Loaded ${payload.items.length} server export job${payload.items.length === 1 ? "" : "s"}.`,
          tone: payload.items.length ? "success" : "muted",
        });
      }
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay audit export jobs.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    replayIntentServerAuditLimit,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
    setReplayIntentServerAuditExportJobTotal,
    setReplayIntentServerAuditExportJobs,
  ]);
  const createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord = useCallback(async (
    exportFormat: "json" | "csv",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob({
        adminToken,
        action: replayIntentServerAuditActionFilter,
        aliasId: replayIntentServerAuditAliasFilter,
        exportFormat,
        requestedByTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
        requestedByTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
        retentionPolicy: replayIntentServerAuditRetentionFilter,
        search: replayIntentServerAuditSearch,
        sourceTabId: replayIntentServerAuditSourceTabFilter,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobStatus({
        message: `Created ${payload.export_format.toUpperCase()} export job ${payload.job_id.slice(0, 8)} for ${payload.record_count} server audit record${payload.record_count === 1 ? "" : "s"}.`,
        tone: payload.record_count ? "success" : "muted",
      });
      setReplayIntentServerAuditExportJobHistory(null);
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to create server replay audit export job.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    predicateRefReplayApplyHistoryTabIdentity.label,
    predicateRefReplayApplyHistoryTabIdentity.tabId,
    replayIntentServerAuditActionFilter,
    replayIntentServerAuditAliasFilter,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord = useCallback(async (
    jobId: string,
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob({
        adminToken,
        jobId,
      });
      downloadTextPayload(payload.content, payload.content_type, payload.filename);
      setReplayIntentServerAuditExportJobStatus({
        message: `Downloaded export job ${payload.job_id.slice(0, 8)} as ${payload.export_format.toUpperCase()}.`,
        tone: "success",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to download server replay audit export job.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory = useCallback(async (
    jobId: string,
  ) => {
    const adminToken = replayIntentServerAuditReadToken.trim() || replayIntentServerAuditWriteToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory({
        adminToken,
        jobId,
      });
      setReplayIntentServerAuditExportJobHistory(payload);
      setReplayIntentServerAuditExportJobStatus({
        message: `Loaded ${payload.history.length} export job audit event${payload.history.length === 1 ? "" : "s"} for ${payload.job.filename}.`,
        tone: payload.history.length ? "success" : "muted",
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to load server replay audit export job history.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    replayIntentServerAuditReadToken,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);
  const pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords = useCallback(async (
    pruneMode: "expired" | "matched",
  ) => {
    const adminToken = replayIntentServerAuditWriteToken.trim() || replayIntentServerAuditReadToken.trim();
    setReplayIntentServerAuditExportJobLoading(true);
    setReplayIntentServerAuditExportJobStatus(null);
    try {
      const payload = await pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        createdBefore: replayIntentServerAuditRecordedBefore,
        exportFormat: "all",
        pruneMode,
        requestedByTabId: replayIntentServerAuditSourceTabFilter,
        search: replayIntentServerAuditSearch,
        templateKey: replayIntentServerAuditTemplateFilter,
      });
      setReplayIntentServerAuditExportJobHistory(null);
      setReplayIntentServerAuditExportJobStatus({
        message:
          pruneMode === "expired"
            ? `Pruned ${payload.deleted_job_count} expired export job${payload.deleted_job_count === 1 ? "" : "s"}, ${payload.deleted_artifact_count} retained artifact${payload.deleted_artifact_count === 1 ? "" : "s"}, and ${payload.deleted_history_count} history record${payload.deleted_history_count === 1 ? "" : "s"}.`
            : `Pruned ${payload.deleted_job_count} matched export job${payload.deleted_job_count === 1 ? "" : "s"}, ${payload.deleted_artifact_count} retained artifact${payload.deleted_artifact_count === 1 ? "" : "s"}, and ${payload.deleted_history_count} history record${payload.deleted_history_count === 1 ? "" : "s"}.`,
        tone: payload.deleted_job_count || payload.deleted_artifact_count || payload.deleted_history_count ? "success" : "muted",
      });
      await loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs({
        adminToken,
        silent: true,
      });
    } catch (error) {
      setReplayIntentServerAuditExportJobStatus({
        message: error instanceof Error ? error.message : "Failed to prune server replay audit export jobs.",
        tone: "error",
      });
    } finally {
      setReplayIntentServerAuditExportJobLoading(false);
    }
  }, [
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    replayIntentServerAuditReadToken,
    replayIntentServerAuditRecordedBefore,
    replayIntentServerAuditSearch,
    replayIntentServerAuditSourceTabFilter,
    replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditWriteToken,
    setReplayIntentServerAuditExportJobHistory,
    setReplayIntentServerAuditExportJobLoading,
    setReplayIntentServerAuditExportJobStatus,
  ]);

  return {
    createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
    downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
    exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
    loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords,
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords,
  };
}
