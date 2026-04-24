import type {
  MarketDataIngestionJobRecord,
  MarketDataLineageHistoryRecord,
  OperatorLineageDrillEvidencePack,
  OperatorLineageEvidenceRetentionResult,
} from "../controlRoomDefinitions";
import { fetchJson } from "./base";

export async function listMarketDataLineageHistory(params: {
  symbol?: string;
  timeframe?: string;
  syncStatus?: string;
  validationClaim?: string;
  sort?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.syncStatus?.trim()) {
    searchParams.set("sync_status", params.syncStatus.trim());
  }
  if (params.validationClaim?.trim()) {
    searchParams.set("validation_claim", params.validationClaim.trim());
  }
  if (params.sort?.trim()) {
    searchParams.set("sort", params.sort.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<MarketDataLineageHistoryRecord[]>(`/market-data/lineage-history${suffix}`);
}

export async function listMarketDataIngestionJobs(params: {
  symbol?: string;
  timeframe?: string;
  operation?: string;
  status?: string;
  sort?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.symbol?.trim()) {
    searchParams.set("symbol", params.symbol.trim());
  }
  if (params.timeframe?.trim()) {
    searchParams.set("timeframe", params.timeframe.trim());
  }
  if (params.operation?.trim()) {
    searchParams.set("operation", params.operation.trim());
  }
  if (params.status?.trim()) {
    searchParams.set("status", params.status.trim());
  }
  if (params.sort?.trim()) {
    searchParams.set("sort", params.sort.trim());
  }
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";
  return fetchJson<MarketDataIngestionJobRecord[]>(`/market-data/ingestion-jobs${suffix}`);
}

export async function pruneMarketDataLineageEvidenceRetention(payload: {
  dry_run?: boolean;
  lineage_history_days?: number | null;
  lineage_issue_history_days?: number | null;
  ingestion_job_days?: number | null;
  ingestion_issue_job_days?: number | null;
  protected_history_ids?: string[];
  protected_job_ids?: string[];
} = {}) {
  return fetchJson<OperatorLineageEvidenceRetentionResult>(
    "/market-data/lineage-evidence/retention/prune",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function exportMarketDataLineageDrillEvidencePack(payload: {
  format?: "json" | "markdown" | string;
  scenario_key?: string | null;
  scenario_label?: string | null;
  incident_id?: string | null;
  operator_decision?: string;
  final_posture?: string;
  venue?: string | null;
  symbol?: string | null;
  timeframe?: string | null;
  sync_status?: string | null;
  validation_claim?: string | null;
  operation?: string | null;
  status?: string | null;
  source_run_id?: string | null;
  rerun_id?: string | null;
  dataset_identity?: string | null;
  sync_checkpoint_id?: string | null;
  rerun_boundary_id?: string | null;
  rerun_validation_category?: string | null;
  generated_by?: string;
  lineage_history_limit?: number;
  ingestion_job_limit?: number;
} = {}) {
  return fetchJson<OperatorLineageDrillEvidencePack>(
    "/market-data/lineage-evidence/drill-packs/export",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}
