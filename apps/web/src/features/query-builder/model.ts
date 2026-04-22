import {
  CSSProperties,
  FormEvent,
  KeyboardEvent,
  MouseEvent,
  PointerEvent,
  ReactNode,
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION,
  AKRA_TOUCH_FEEDBACK_EVENT_NAME,
  AkraTouchFeedbackDetail,
  AkraTouchFeedbackEnvelope,
  triggerAkraTouchFeedbackBridge,
} from "../../touchFeedback";
import { formatComparisonTooltipConflictSessionRelativeTime } from "../comparisonTooltipFormatters";
export { formatComparisonTooltipConflictSessionRelativeTime };
import {
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJob,
  exportRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  fetchJson,
  getRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  listRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs,
  pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
  resolveRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
  revokeRunSurfaceCollectionQueryBuilderServerReplayLinkAlias,
} from "../../controlRoomApi";
import {
  ALL_FILTER_VALUE,
  COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM,
  COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM,
  COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM,
  COMPARISON_FOCUS_DETAIL_SEARCH_PARAM,
  COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM,
  COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM,
  COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM,
  COMPARISON_FOCUS_SECTION_SEARCH_PARAM,
  COMPARISON_FOCUS_SOURCE_SEARCH_PARAM,
  COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES,
  MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS,
  REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_ALIAS_SEARCH_PARAM,
  REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM,
  REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM,
  REPLAY_INTENT_SCOPE_SEARCH_PARAM,
  REPLAY_INTENT_SEARCH_PARAM,
  REPLAY_INTENT_STEP_SEARCH_PARAM,
  REPLAY_INTENT_TEMPLATE_SEARCH_PARAM,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
  RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY,
} from "../../controlRoomDefinitions";
import type {
  BenchmarkArtifact,
  ComparisonScoreSection,
  ParameterSchema,
  ProvenanceArtifactLineDetailView,
  ProvenanceArtifactLineMicroView,
  Run,
  RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobDownloadPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryEntry,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobHistoryPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditExportJobPrunePayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditListPayload,
  RunSurfaceCollectionQueryBuilderReplayLinkServerAuditPrunePayload,
  RunSurfaceCollectionQueryContract,
  RunSurfaceCollectionQueryElementField,
  RunSurfaceCollectionQueryExpressionAuthoring,
  RunSurfaceCollectionQueryParameterDomainDescriptor,
  RunSurfaceCollectionQuerySchema,
} from "../../controlRoomDefinitions";

export function formatTimestamp(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

export function formatRelativeTimestampLabel(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) {
    return formatTimestamp(value);
  }
  const relative = formatComparisonTooltipConflictSessionRelativeTime(timestamp, new Date());
  return relative ? `${relative} · ${formatTimestamp(value)}` : formatTimestamp(value);
}

export function encodeComparisonScoreLinkToken(value: string) {
  return encodeURIComponent(value);
}

export function buildComparisonRunListLineSubFocusKey(key: string) {
  return `run-list-line:${encodeComparisonScoreLinkToken(key)}`;
}

export function buildComparisonRunListOrderPreviewSubFocusKey(orderId: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `order_preview:${encodeComparisonScoreLinkToken(orderId)}:${fieldKey}`,
  );
}

export function buildComparisonRunListDataSymbolSubFocusKey(symbol: string, fieldKey: string) {
  return buildComparisonRunListLineSubFocusKey(
    `data_symbol:${encodeComparisonScoreLinkToken(symbol)}:${fieldKey}`,
  );
}

export function buildComparisonProvenanceArtifactSummaryHoverKey(path: string, summaryKey: string) {
  return `provenance-artifact-summary:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(summaryKey)}`;
}

export function buildComparisonProvenanceArtifactSectionLineHoverKey(
  path: string,
  sectionKey: string,
  lineIndex: number,
) {
  return `provenance-artifact-section-line:${encodeComparisonScoreLinkToken(path)}:${encodeComparisonScoreLinkToken(
    sectionKey,
  )}:${lineIndex}`;
}

export const benchmarkArtifactSummaryLabels: Record<string, string> = {
  headline: "Headline",
  market_context: "Market read",
  portfolio_context: "Portfolio read",
  signal_context: "Signal read",
  rejection_context: "Rejections",
  exit_context: "Exit read",
  pair_context: "Pair read",
  strategy_name: "Strategy",
  run_id: "Run ID",
  exchange: "Exchange",
  stake_currency: "Stake",
  timeframe: "TF",
  timerange: "Timerange",
  generated_at: "Generated",
  backtest_start_at: "Backtest start",
  backtest_end_at: "Backtest end",
  pair_count: "Pairs",
  trade_count: "Trades",
  profit_total_pct: "Total return",
  profit_total_abs: "Total PnL",
  max_drawdown_pct: "Max DD",
  market_change_pct: "Market move",
  manifest_count: "Manifests",
  snapshot_count: "Snapshots",
  timeframe_detail: "TF detail",
  notes: "Notes",
  win_rate_pct: "Win rate",
  date: "Date",
  duration: "Duration",
  drawdown_start: "DD start",
  drawdown_end: "DD end",
  start_balance: "Start balance",
  end_balance: "End balance",
  high_balance: "High balance",
  low_balance: "Low balance",
  sharpe: "Sharpe",
  sortino: "Sortino",
  calmar: "Calmar",
  member_count: "Members",
  entry_preview: "Entries",
  market_change_export_count: "Market exports",
  wallet_export_count: "Wallet exports",
  signal_export_count: "Signal exports",
  rejected_export_count: "Rejected exports",
  exited_export_count: "Exited exports",
  strategy_source_count: "Strategy sources",
  strategy_param_count: "Strategy params",
  result_json_entry: "Result JSON",
  config_json_entry: "Config JSON",
  strategy: "Strategy",
  trading_mode: "Trading mode",
  margin_mode: "Margin mode",
  max_open_trades: "Max open trades",
  export: "Export",
  source_files: "Source files",
  parameter_files: "Parameter files",
  strategy_names: "Strategy names",
  parameter_keys: "Parameter keys",
  entry: "Entry",
  row_count: "Rows",
  total_row_count: "Total rows",
  frame_count: "Frames",
  column_count: "Columns",
  columns: "Column list",
  date_start: "Start",
  date_end: "End",
  export_count: "Exports",
  strategies: "Strategies",
  currencies: "Currencies",
  currency_count: "Currency count",
  entries: "Entries",
  unreadable_entries: "Unreadable",
  inspection_status: "Inspection",
  pair_change_preview: "Pair moves",
  best_pair: "Best pair",
  best_pair_change_pct: "Best pair move",
  worst_pair: "Worst pair",
  worst_pair_change_pct: "Worst pair move",
  positive_pair_count: "Positive pairs",
  negative_pair_count: "Negative pairs",
  start_value: "Start value",
  end_value: "End value",
  change_pct: "Change",
  total_quote_start: "Quote start",
  total_quote_end: "Quote end",
  total_quote_high: "Quote high",
  total_quote_low: "Quote low",
  currency_quote_preview: "Currency quote preview",
  latest_balance: "Latest balance",
  latest_quote_value: "Latest quote value",
  strategy_row_preview: "Strategy rows",
  pair_row_preview: "Pair rows",
  semantic_columns: "Semantic columns",
  enter_tag_counts: "Entry tag counts",
  reason_counts: "Reason counts",
  exit_reason_counts: "Exit reason counts",
};

export const benchmarkArtifactSectionLabels: Record<string, string> = {
  benchmark_story: "Benchmark narrative",
  zip_contents: "Zip contents",
  zip_config: "Embedded config",
  zip_strategy_bundle: "Strategy bundle",
  zip_market_change: "Market change export",
  zip_wallet_exports: "Wallet exports",
  zip_signal_exports: "Signal exports",
  zip_rejected_exports: "Rejected exports",
  zip_exited_exports: "Exited exports",
  metadata: "Metadata",
  strategy_comparison: "Strategy comparison",
  pair_metrics: "Pair metrics",
  pair_extremes: "Pair extremes",
  enter_tag_metrics: "Entry tags",
  exit_reason_metrics: "Exit reasons",
  mixed_tag_metrics: "Mixed tags",
  left_open_metrics: "Left open",
  periodic_breakdown: "Periodic breakdown",
  daily_profit: "Daily profit",
  wallet_stats: "Wallet stats",
};

export function formatBenchmarkArtifactSummaryLabel(key: string) {
  return benchmarkArtifactSummaryLabels[key] ?? key.replaceAll("_", " ");
}

export function formatBenchmarkArtifactSummaryValue(key: string, value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    if (key.endsWith("_pct")) {
      return `${value}%`;
    }
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export function formatBenchmarkArtifactSectionLabel(key: string) {
  return benchmarkArtifactSectionLabels[key] ?? key.replaceAll("_", " ");
}

export function formatBenchmarkArtifactInlineValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "n/a";
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatBenchmarkArtifactInlineValue(item)).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !key.startsWith("__"))
      .map(([key, nestedValue]) => {
        const formattedValue = formatBenchmarkArtifactSummaryValue(key, nestedValue);
        if (formattedValue === null) {
          return null;
        }
        return `${formatBenchmarkArtifactSummaryLabel(key)}: ${formattedValue}`;
      })
      .filter((entry): entry is string => entry !== null)
      .join(" · ");
  }
  return String(value);
}

export function formatBenchmarkArtifactSectionValue(value: unknown): string | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return null;
    }
    const preview = value.slice(0, 3).map((item) => formatBenchmarkArtifactInlineValue(item)).join(" | ");
    if (value.length > 3) {
      return `${preview} | +${value.length - 3} more`;
    }
    return preview;
  }
  if (typeof value === "object") {
    return formatBenchmarkArtifactInlineValue(value);
  }
  return String(value);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasEntryFromServerRecord(
  record: RunSurfaceCollectionQueryBuilderReplayLinkAliasRecordPayload,
): RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry {
  return {
    aliasId: record.alias_id,
    createdAt: record.created_at,
    createdByTabId: record.created_by_tab_id ?? "",
    createdByTabLabel: record.created_by_tab_label ?? "Server",
    expiresAt: record.expires_at,
    intent:
      normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(record.intent)
      ?? normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({})!,
    redactionPolicy: record.redaction_policy,
    resolutionSource: "server",
    revokedAt: record.revoked_at,
    revokedByTabId: record.revoked_by_tab_id,
    revokedByTabLabel: record.revoked_by_tab_label,
    signature: record.signature,
    templateKey: record.template_key,
    templateLabel: record.template_label,
  };
}

export function getCollectionQueryStringArray(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

export function getCollectionQueryRecordArray(value: unknown) {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
    : [];
}

export function getRunSurfaceCollectionQuerySchemas(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQuerySchema[] {
  if (!contract) {
    return [];
  }
  return getCollectionQueryRecordArray(contract.schema_detail.collection_schemas).map((schema) => ({
    path: getCollectionQueryStringArray(schema.path),
    pathTemplate: getCollectionQueryStringArray(schema.path_template),
    label: typeof schema.label === "string" ? schema.label : "Collection",
    collectionKind: typeof schema.collection_kind === "string" ? schema.collection_kind : "collection",
    itemKind: typeof schema.item_kind === "string" ? schema.item_kind : "item",
    filterKeys: getCollectionQueryStringArray(schema.filter_keys),
    description: typeof schema.description === "string" ? schema.description : "",
    parameters: getCollectionQueryRecordArray(schema.parameters).map((parameter) => {
      const domainRecord =
        typeof parameter.domain === "object" && parameter.domain !== null
          ? (parameter.domain as Record<string, unknown>)
          : null;
      const enumSourceRecord =
        domainRecord && typeof domainRecord.enum_source === "object" && domainRecord.enum_source !== null
          ? (domainRecord.enum_source as Record<string, unknown>)
          : null;
      return {
        key: typeof parameter.key === "string" ? parameter.key : "",
        kind: typeof parameter.kind === "string" ? parameter.kind : "",
        description: typeof parameter.description === "string" ? parameter.description : "",
        examples: getCollectionQueryStringArray(parameter.examples),
        domain: domainRecord
          ? {
              key: typeof domainRecord.key === "string" ? domainRecord.key : null,
              source: typeof domainRecord.source === "string" ? domainRecord.source : null,
              values: getCollectionQueryStringArray(domainRecord.values),
              enumSource: enumSourceRecord
                ? {
                    kind: typeof enumSourceRecord.kind === "string" ? enumSourceRecord.kind : null,
                    surfaceKey:
                      typeof enumSourceRecord.surface_key === "string" ? enumSourceRecord.surface_key : null,
                    path: getCollectionQueryStringArray(enumSourceRecord.path),
                  }
                : null,
            }
          : null,
      };
    }),
    elementSchema: getCollectionQueryRecordArray(schema.element_schema).map((field) => ({
      key: typeof field.key === "string" ? field.key : "",
      queryExposed: field.query_exposed === true,
      valueType: typeof field.value_type === "string" ? field.value_type : "string",
      valuePath: getCollectionQueryStringArray(field.value_path),
      valueRoot: field.value_root === true,
      title: typeof field.title === "string" ? field.title : null,
      description: typeof field.description === "string" ? field.description : null,
      operators: getCollectionQueryRecordArray(field.operators).map((operator) => ({
        key: typeof operator.key === "string" ? operator.key : "",
        label: typeof operator.label === "string" ? operator.label : "",
        description: typeof operator.description === "string" ? operator.description : "",
        valueShape: typeof operator.value_shape === "string" ? operator.value_shape : "scalar",
      })),
    })),
  }));
}

export function getRunSurfaceCollectionQueryParameterDomains(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQueryParameterDomainDescriptor[] {
  if (!contract) {
    return [];
  }
  return getCollectionQueryRecordArray(contract.schema_detail.parameter_domains).map((parameterDomain) => {
    const domainRecord =
      typeof parameterDomain.domain === "object" && parameterDomain.domain !== null
        ? (parameterDomain.domain as Record<string, unknown>)
        : null;
    const enumSourceRecord =
      domainRecord && typeof domainRecord.enum_source === "object" && domainRecord.enum_source !== null
        ? (domainRecord.enum_source as Record<string, unknown>)
        : null;
    return {
      parameterKey: typeof parameterDomain.parameter_key === "string" ? parameterDomain.parameter_key : "",
      parameterKind: typeof parameterDomain.parameter_kind === "string" ? parameterDomain.parameter_kind : "",
      collectionLabel: typeof parameterDomain.collection_label === "string" ? parameterDomain.collection_label : "",
      collectionPath: getCollectionQueryStringArray(parameterDomain.collection_path),
      collectionPathTemplate: getCollectionQueryStringArray(parameterDomain.collection_path_template),
      surfaceKey: typeof parameterDomain.surface_key === "string" ? parameterDomain.surface_key : "",
      domain: domainRecord
        ? {
            key: typeof domainRecord.key === "string" ? domainRecord.key : null,
            source: typeof domainRecord.source === "string" ? domainRecord.source : null,
            values: getCollectionQueryStringArray(domainRecord.values),
            enumSource: enumSourceRecord
              ? {
                  kind: typeof enumSourceRecord.kind === "string" ? enumSourceRecord.kind : null,
                  surfaceKey:
                    typeof enumSourceRecord.surface_key === "string" ? enumSourceRecord.surface_key : null,
                  path: getCollectionQueryStringArray(enumSourceRecord.path),
                }
              : null,
          }
        : null,
    };
  });
}

export function getRunSurfaceCollectionQueryExpressionAuthoring(
  contract: RunSurfaceCollectionQueryContract | null | undefined,
): RunSurfaceCollectionQueryExpressionAuthoring {
  const authoringRecord =
    contract && typeof contract.schema_detail.expression_authoring === "object"
      ? (contract.schema_detail.expression_authoring as Record<string, unknown>)
      : null;
  const predicateRefsRecord =
    authoringRecord && typeof authoringRecord.predicate_refs === "object"
      ? (authoringRecord.predicate_refs as Record<string, unknown>)
      : null;
  const predicateTemplatesRecord =
    authoringRecord && typeof authoringRecord.predicate_templates === "object"
      ? (authoringRecord.predicate_templates as Record<string, unknown>)
      : null;
  const bindingReferenceShapeRecord =
    predicateTemplatesRecord && typeof predicateTemplatesRecord.binding_reference_shape === "object"
      ? (predicateTemplatesRecord.binding_reference_shape as Record<string, unknown>)
      : null;
  const collectionNodesRecord =
    authoringRecord && typeof authoringRecord.collection_nodes === "object"
      ? (authoringRecord.collection_nodes as Record<string, unknown>)
      : null;
  const collectionShapeRecord =
    collectionNodesRecord && typeof collectionNodesRecord.shape === "object"
      ? (collectionNodesRecord.shape as Record<string, unknown>)
      : null;
  return {
    predicateRefs: {
      registryField:
        predicateRefsRecord && typeof predicateRefsRecord.registry_field === "string"
          ? predicateRefsRecord.registry_field
          : "predicates",
      referenceField:
        predicateRefsRecord && typeof predicateRefsRecord.reference_field === "string"
          ? predicateRefsRecord.reference_field
          : "predicate_ref",
    },
    predicateTemplates: {
      registryField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.registry_field === "string"
          ? predicateTemplatesRecord.registry_field
          : "predicate_templates",
      templateField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.template_field === "string"
          ? predicateTemplatesRecord.template_field
          : "template",
      parametersField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.parameters_field === "string"
          ? predicateTemplatesRecord.parameters_field
          : "parameters",
      bindingsField:
        predicateTemplatesRecord && typeof predicateTemplatesRecord.bindings_field === "string"
          ? predicateTemplatesRecord.bindings_field
          : "bindings",
      bindingReferenceField:
        bindingReferenceShapeRecord && typeof bindingReferenceShapeRecord.binding === "string"
          ? "binding"
          : "binding",
    },
    collectionNodes: {
      field:
        collectionNodesRecord && typeof collectionNodesRecord.field === "string"
          ? collectionNodesRecord.field
          : "collection",
      pathField:
        collectionShapeRecord && typeof collectionShapeRecord.path === "string"
          ? "path"
          : "path",
      pathTemplateField:
        collectionShapeRecord && typeof collectionShapeRecord.path_template === "string"
          ? "path_template"
          : "path_template",
      bindingsField:
        collectionShapeRecord && typeof collectionShapeRecord.bindings === "object"
          ? "bindings"
          : "bindings",
      quantifierField:
        collectionShapeRecord && typeof collectionShapeRecord.quantifier === "string"
          ? "quantifier"
          : "quantifier",
    },
  };
}

export function getCollectionQuerySchemaId(schema: RunSurfaceCollectionQuerySchema) {
  return schema.pathTemplate.join(".");
}

export function resolveCollectionQueryPath(
  template: string[],
  parameterValues: Record<string, string>,
) {
  return template.map((segment) => {
    const match = segment.match(/^\{(.+)\}$/);
    if (!match) {
      return segment;
    }
    return parameterValues[match[1]] || segment;
  });
}

export function resolveCollectionQueryTemplateValues(
  template: string[],
  resolvedPath: string[],
) {
  if (template.length !== resolvedPath.length) {
    return null;
  }
  const values: Record<string, string> = {};
  for (let index = 0; index < template.length; index += 1) {
    const templateSegment = template[index];
    const resolvedSegment = resolvedPath[index];
    const match = templateSegment.match(/^\{(.+)\}$/);
    if (match) {
      values[match[1]] = resolvedSegment;
      continue;
    }
    if (templateSegment !== resolvedSegment) {
      return null;
    }
  }
  return values;
}

export function coerceCollectionQueryBuilderValue(rawValue: string, valueType: string) {
  if (valueType === "integer") {
    const parsed = Number.parseInt(rawValue, 10);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }
  if (valueType === "number") {
    const parsed = Number.parseFloat(rawValue);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }
  if (valueType.startsWith("list[")) {
    return rawValue
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return rawValue;
}

export function formatCollectionQueryBuilderValue(rawValue: unknown, valueType: string) {
  if (rawValue === null || rawValue === undefined) {
    return "";
  }
  if (valueType.startsWith("list[")) {
    if (Array.isArray(rawValue)) {
      return rawValue.map((value) => String(value)).join(", ");
    }
    return String(rawValue);
  }
  if (typeof rawValue === "string") {
    return rawValue;
  }
  if (typeof rawValue === "number" || typeof rawValue === "boolean") {
    return String(rawValue);
  }
  try {
    return JSON.stringify(rawValue);
  } catch {
    return String(rawValue);
  }
}

export type HydratedRunSurfaceCollectionQueryBuilderState = {
  contractKey: string;
  schemaId: string;
  parameterValues: Record<string, string>;
  parameterBindingKeys: Record<string, string>;
  quantifier: "any" | "all" | "none";
  fieldKey: string;
  operatorKey: string;
  builderValue: string;
  valueBindingKey: string;
  negated: boolean;
};

export type RunSurfaceCollectionQueryBuilderClauseState = {
  id: string;
  kind: "clause";
  clause: HydratedRunSurfaceCollectionQueryBuilderState;
};

export type RunSurfaceCollectionQueryBuilderPredicateRefState = {
  id: string;
  kind: "predicate_ref";
  predicateKey: string;
  bindings: Record<string, string>;
  negated: boolean;
};

export type RunSurfaceCollectionQueryBuilderGroupState = {
  id: string;
  kind: "group";
  logic: "and" | "or";
  negated: boolean;
  children: RunSurfaceCollectionQueryBuilderChildState[];
};

export type RunSurfaceCollectionQueryBuilderChildState =
  | RunSurfaceCollectionQueryBuilderClauseState
  | RunSurfaceCollectionQueryBuilderPredicateRefState
  | {
      id: string;
      kind: "group";
      logic: "and" | "or";
      negated: boolean;
      children: RunSurfaceCollectionQueryBuilderChildState[];
    };

export type RunSurfaceCollectionQueryBuilderPredicateState = {
  id: string;
  key: string;
  node: RunSurfaceCollectionQueryBuilderChildState;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState = {
  key: string;
  label: string;
  customLabel: string;
  groupName: string;
  helpNote: string;
  valueType: string;
  description: string | null;
  options: string[];
  defaultValue: string;
  bindingPreset: string;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState = {
  key: string;
  label: string;
  helpNote: string;
  collapsedByDefault: boolean;
  visibilityRule: "always" | "manual" | "binding_active" | "value_active";
  coordinationPolicy: "manual_source_priority" | "highest_source_priority" | "sticky_auto_selection" | "manual_resolution";
  presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState = {
  key: string;
  groupKey: string;
  bundleKey: string;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState = {
  key: string;
  label: string;
  helpNote: string;
  priority: number;
  autoSelectRule: "manual" | "always" | "binding_active" | "value_active";
  dependencies: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState[];
  parameterValues: Record<string, string>;
  parameterBindingPresets: Record<string, string>;
};

export type RunSurfaceCollectionQueryBuilderPredicateTemplateState = {
  id: string;
  key: string;
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
  parameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[];
  node: RunSurfaceCollectionQueryBuilderChildState;
};

export const RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT = 5;
export const RUN_SURFACE_COLLECTION_RUNTIME_MISSING = Symbol("run-surface-collection-runtime-missing");

export type RunSurfaceCollectionQueryRuntimePathToken = string | number;

export type RunSurfaceCollectionQueryRuntimeCollectionItem = {
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[];
  value: unknown;
};

export function formatRunSurfaceCollectionQueryRuntimePathSegment(segment: RunSurfaceCollectionQueryRuntimePathToken) {
  if (typeof segment === "number") {
    return `[${segment}]`;
  }
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(segment)
    ? `.${segment}`
    : `[${JSON.stringify(segment)}]`;
}

export function formatRunSurfaceCollectionQueryRuntimePath(
  rootLabel: string,
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[],
) {
  return `${rootLabel}${pathTokens.map(formatRunSurfaceCollectionQueryRuntimePathSegment).join("")}`;
}

export function normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
  value: unknown,
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[],
): RunSurfaceCollectionQueryRuntimeCollectionItem[] {
  if (value === null || value === undefined) {
    return [];
  }
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
      item,
      [...pathTokens, index],
    ));
  }
  if (value instanceof Set) {
    return Array.from(value).flatMap((item, index) => normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(
      item,
      [...pathTokens, index],
    ));
  }
  if (typeof value === "object") {
    return [{ pathTokens, value }];
  }
  return [{ pathTokens, value }];
}

export function resolveRunSurfaceCollectionQueryRuntimeCollectionItems(
  current: unknown,
  path: string[],
  pathTokens: RunSurfaceCollectionQueryRuntimePathToken[] = [],
): RunSurfaceCollectionQueryRuntimeCollectionItem[] {
  if (current === null || current === undefined) {
    return [];
  }
  if (!path.length) {
    return normalizeRunSurfaceCollectionQueryRuntimeCollectionItems(current, pathTokens);
  }
  const [segment, ...tail] = path;
  if (Array.isArray(current)) {
    return current.flatMap((item, index) =>
      resolveRunSurfaceCollectionQueryRuntimeCollectionItems(item, path, [...pathTokens, index]));
  }
  if (current instanceof Set) {
    return Array.from(current).flatMap((item, index) =>
      resolveRunSurfaceCollectionQueryRuntimeCollectionItems(item, path, [...pathTokens, index]));
  }
  if (typeof current !== "object") {
    return [];
  }
  const record = current as Record<string, unknown>;
  if (!(segment in record)) {
    return [];
  }
  return resolveRunSurfaceCollectionQueryRuntimeCollectionItems(
    record[segment],
    tail,
    [...pathTokens, segment],
  );
}

export function resolveRunSurfaceCollectionQueryRuntimeValuePath(
  current: unknown,
  path: string[],
): unknown | typeof RUN_SURFACE_COLLECTION_RUNTIME_MISSING {
  let value = current;
  const resolvedPath = path.length ? path : [];
  for (const segment of resolvedPath) {
    if (value === null || value === undefined) {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    if (Array.isArray(value)) {
      const parsedIndex = Number.parseInt(segment, 10);
      if (Number.isNaN(parsedIndex) || parsedIndex < 0 || parsedIndex >= value.length) {
        return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
      }
      value = value[parsedIndex];
      continue;
    }
    if (typeof value !== "object") {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    const record = value as Record<string, unknown>;
    if (!(segment in record)) {
      return RUN_SURFACE_COLLECTION_RUNTIME_MISSING;
    }
    value = record[segment];
  }
  return value;
}

export function normalizeRunSurfaceCollectionQueryRuntimeNumericValue(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number.parseFloat(value);
    return Number.isNaN(parsed) ? null : parsed;
  }
  return null;
}

export function normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(value: unknown) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value;
  }
  if (typeof value !== "string" && typeof value !== "number") {
    return null;
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function toRunSurfaceCollectionQueryRuntimeIterableValues(value: unknown) {
  if (Array.isArray(value)) {
    return value;
  }
  if (value instanceof Set) {
    return Array.from(value);
  }
  if (value === null || value === undefined) {
    return [];
  }
  if (typeof value === "string") {
    return Array.from(value);
  }
  return [value];
}

export function evaluateRunSurfaceCollectionQueryRuntimeCondition(
  candidateValue: unknown,
  operator: string,
  operand: unknown,
) {
  if (operator === "eq") {
    return candidateValue === operand;
  }
  if (operator === "prefix") {
    return typeof candidateValue === "string"
      && typeof operand === "string"
      && candidateValue.startsWith(operand);
  }
  if (operator === "contains_all") {
    const candidateValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(candidateValue));
    const operandValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(operand));
    return Array.from(operandValues).every((value) => candidateValues.has(value));
  }
  if (operator === "contains_any") {
    const candidateValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(candidateValue));
    const operandValues = new Set(toRunSurfaceCollectionQueryRuntimeIterableValues(operand));
    return Array.from(operandValues).some((value) => candidateValues.has(value));
  }
  if (operator === "include") {
    return toRunSurfaceCollectionQueryRuntimeIterableValues(operand).includes(candidateValue);
  }
  if (operator === "gt" || operator === "ge" || operator === "lt" || operator === "le") {
    const candidateDatetime = normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(candidateValue);
    const operandDatetime = normalizeRunSurfaceCollectionQueryRuntimeDatetimeValue(operand);
    if (candidateDatetime && operandDatetime) {
      if (operator === "gt") {
        return candidateDatetime > operandDatetime;
      }
      if (operator === "ge") {
        return candidateDatetime >= operandDatetime;
      }
      if (operator === "lt") {
        return candidateDatetime < operandDatetime;
      }
      return candidateDatetime <= operandDatetime;
    }
    const candidateNumber = normalizeRunSurfaceCollectionQueryRuntimeNumericValue(candidateValue);
    const operandNumber = normalizeRunSurfaceCollectionQueryRuntimeNumericValue(operand);
    if (candidateNumber === null || operandNumber === null) {
      return false;
    }
    if (operator === "gt") {
      return candidateNumber > operandNumber;
    }
    if (operator === "ge") {
      return candidateNumber >= operandNumber;
    }
    if (operator === "lt") {
      return candidateNumber < operandNumber;
    }
    return candidateNumber <= operandNumber;
  }
  return false;
}

export function evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome(
  quantifier: "any" | "all" | "none",
  candidateCount: number,
  matchedCount: number,
) {
  if (quantifier === "any") {
    return matchedCount > 0;
  }
  if (quantifier === "all") {
    return candidateCount > 0 && matchedCount === candidateCount;
  }
  return matchedCount === 0;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateSamples(params: {
  comparedValueLabel: string;
  comparedValueOperand: unknown;
  field: RunSurfaceCollectionQueryElementField | null;
  quantifier: "any" | "all" | "none";
  resolvedParameterValues: Record<string, string>;
  runs: Run[];
  schema: RunSurfaceCollectionQuerySchema | null;
  operatorKey: string;
}) {
  const {
    comparedValueLabel,
    comparedValueOperand,
    field,
    operatorKey,
    quantifier,
    resolvedParameterValues,
    runs,
    schema,
  } = params;
  if (!schema || !field || !runs.length) {
    return {
      allValues: [] as RunSurfaceCollectionQueryRuntimeCandidateSample[],
      runOutcomes: [] as RunSurfaceCollectionQueryRuntimeQuantifierOutcome[],
      sampleValues: [] as RunSurfaceCollectionQueryRuntimeCandidateSample[],
      sampleMatchCount: 0,
      sampleTotalCount: 0,
      sampleTruncated: false,
    };
  }
  const resolvedPath = resolveCollectionQueryPath(schema.pathTemplate, resolvedParameterValues);
  const accessorPath = field.valueRoot ? [] : (field.valuePath.length ? field.valuePath : [field.key]);
  const accessorLabel = field.valueRoot
    ? `${schema.itemKind} value`
    : `${schema.itemKind}.${accessorPath.join(".") || field.key}`;
  const allValues: RunSurfaceCollectionQueryRuntimeCandidateSample[] = [];
  const runOutcomes: RunSurfaceCollectionQueryRuntimeQuantifierOutcome[] = [];
  let sampleTotalCount = 0;
  let sampleMatchCount = 0;
  runs.forEach((run) => {
    const collectionItems = resolveRunSurfaceCollectionQueryRuntimeCollectionItems(run, resolvedPath);
    let runCandidateCount = 0;
    let runMatchedCount = 0;
    collectionItems.forEach((collectionItem) => {
      runCandidateCount += 1;
      sampleTotalCount += 1;
      const candidateValueRaw = field.valueRoot
        ? collectionItem.value
        : resolveRunSurfaceCollectionQueryRuntimeValuePath(collectionItem.value, accessorPath);
      const candidatePath = formatRunSurfaceCollectionQueryRuntimePath(
        `run:${run.config.run_id}`,
        collectionItem.pathTokens,
      );
      const result = candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
        ? false
        : evaluateRunSurfaceCollectionQueryRuntimeCondition(
            candidateValueRaw,
            operatorKey,
            comparedValueOperand,
          );
      if (result) {
        runMatchedCount += 1;
        sampleMatchCount += 1;
      }
      const candidateValue = candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
        ? `Missing ${accessorLabel}`
        : formatCollectionQueryBuilderValue(candidateValueRaw, field.valueType);
      const runContextArtifactHoverKeys = buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys({
        candidateValueRaw,
        resolvedParameterValues,
        resolvedPath,
        run,
      });
      const candidateReplayId = buildRunSurfaceCollectionQueryRuntimeCandidateReplayId({
        candidateValueRaw,
        resolvedParameterValues,
        resolvedPath,
      });
      const orderRecord =
        collectionItem.value && typeof collectionItem.value === "object" && !Array.isArray(collectionItem.value)
          ? (collectionItem.value as Record<string, unknown>)
          : null;
      const orderId = typeof orderRecord?.order_id === "string" ? orderRecord.order_id : null;
      const symbolKey =
        resolvedPath[0] === "provenance"
        && resolvedPath[1] === "market_data_by_symbol"
        && resolvedPath[3] === "issues"
          ? (resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "")
          : "";
      const runContext =
        resolvedPath[0] === "orders" && orderId
          ? {
              componentKey: "trade_count",
              label: `Order ${orderId}`,
              section: "metrics" as const,
              subFocusKey: buildComparisonRunListOrderPreviewSubFocusKey(orderId, "instrument"),
            }
          : symbolKey
            ? {
                componentKey: "provenance_richness",
                label: `Data lineage ${symbolKey}`,
                section: "context" as const,
                subFocusKey: buildComparisonRunListDataSymbolSubFocusKey(symbolKey, "issues"),
              }
            : null;
      allValues.push({
        candidatePath,
        candidateReplayId,
        candidateValue,
        detail: candidateValueRaw === RUN_SURFACE_COLLECTION_RUNTIME_MISSING
          ? `${candidatePath} has no ${accessorLabel} value in the current run payload.`
          : `${candidatePath} resolved ${accessorLabel} to ${candidateValue} and ${
            result ? "matched" : "did not match"
          } ${comparedValueLabel}.`,
        result,
        runId: run.config.run_id,
        runContextArtifactHoverKeys,
        runContextComponentKey: runContext?.componentKey ?? null,
        runContextLabel: runContext?.label ?? null,
        runContextSection: runContext?.section ?? null,
        runContextSubFocusKey: runContext?.subFocusKey ?? null,
      });
    });
    const quantifierResult = evaluateRunSurfaceCollectionQueryRuntimeQuantifierOutcome(
      quantifier,
      runCandidateCount,
      runMatchedCount,
    );
    runOutcomes.push({
      candidateCount: runCandidateCount,
      detail: runCandidateCount
        ? `${quantifier.toUpperCase()} resolved to ${quantifierResult ? "true" : "false"} from ${runMatchedCount}/${runCandidateCount} matching candidates in run ${run.config.run_id}.`
        : `${quantifier.toUpperCase()} resolved to ${quantifierResult ? "true" : "false"} because run ${run.config.run_id} had no concrete candidates on ${resolvedPath.join(".") || schema.label}.`,
      matchedCount: runMatchedCount,
      result: quantifierResult,
      runId: run.config.run_id,
    });
  });
  return {
    allValues,
    runOutcomes,
    sampleValues: allValues.slice(0, RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT),
    sampleMatchCount,
    sampleTotalCount,
    sampleTruncated: allValues.length > RUN_SURFACE_COLLECTION_RUNTIME_SAMPLE_LIMIT,
  };
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(
  sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
) {
  return `${sample.runId}:${sample.candidatePath}`;
}

export function normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants(symbolKey: string) {
  const trimmed = symbolKey.trim();
  if (!trimmed) {
    return [];
  }
  const bareSymbol = trimmed.includes(":")
    ? trimmed.split(":").slice(1).join(":")
    : trimmed;
  const rawVariants = new Set<string>([
    trimmed,
    trimmed.replace(":", " "),
    bareSymbol,
    bareSymbol.replace("/", "-"),
    bareSymbol.replace("/", " "),
    bareSymbol.replace("/", ""),
  ]);
  return Array.from(rawVariants)
    .map((value) => normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(value))
    .filter(Boolean);
}

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(value: unknown): string[] {
  const collected = new Set<string>();
  const isMetadataKey = (key: string) => key.startsWith("__");
  const visit = (candidate: unknown) => {
    if (candidate === null || candidate === undefined || candidate === "") {
      return;
    }
    if (typeof candidate === "string" || typeof candidate === "number" || typeof candidate === "boolean") {
      const normalized = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(String(candidate));
      if (normalized) {
        collected.add(normalized);
      }
      return;
    }
    if (Array.isArray(candidate)) {
      candidate.forEach((item) => visit(item));
      return;
    }
    if (typeof candidate === "object") {
      Object.entries(candidate as Record<string, unknown>).forEach(([key, nestedValue]) => {
        if (isMetadataKey(key)) {
          return;
        }
        const formattedKey = formatBenchmarkArtifactSummaryLabel(key);
        const normalizedKey = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(formattedKey);
        if (normalizedKey) {
          collected.add(normalizedKey);
        }
        if (
          typeof nestedValue === "string"
          || typeof nestedValue === "number"
          || typeof nestedValue === "boolean"
        ) {
          const joined = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
            `${formattedKey} ${nestedValue}`,
          );
          if (joined) {
            collected.add(joined);
          }
        }
        visit(nestedValue);
      });
    }
  };
  visit(value);
  return Array.from(collected);
}

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => (typeof entry === "string"
      ? normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry)
      : ""))
    .filter(Boolean);
}

export function normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(value: string | null | undefined) {
  if (!value) {
    return "";
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  return trimmed.includes(":")
    ? trimmed.split(":").slice(1).join(":").trim()
    : trimmed;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateReplayId(params: {
  candidateValueRaw: unknown;
  resolvedParameterValues: Record<string, string>;
  resolvedPath: string[];
}) {
  const { candidateValueRaw, resolvedParameterValues, resolvedPath } = params;
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
    || typeof candidateValueRaw !== "string"
  ) {
    return null;
  }
  const canonicalSymbol = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(
    resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "",
  );
  const canonicalValue = String(candidateValueRaw).trim();
  const normalizedValue = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
    canonicalValue,
  );
  if (!canonicalSymbol || !normalizedValue) {
    return null;
  }
  return JSON.stringify(["market_data_issue", canonicalSymbol, canonicalValue]);
}

export function collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => {
      if (!entry || typeof entry !== "object") {
        return null;
      }
      const record = entry as Record<string, unknown>;
      return {
        bindingKind:
          typeof record.binding_kind === "string" ? record.binding_kind : null,
        candidateId:
          typeof record.candidate_id === "string" ? record.candidate_id : null,
        runtimeCandidateId:
          typeof record.runtime_candidate_id === "string" ? record.runtime_candidate_id : null,
        candidatePathTemplate:
          typeof record.candidate_path_template === "string" ? record.candidate_path_template : null,
        candidateValue:
          typeof record.candidate_value === "string" ? record.candidate_value : null,
        symbolKey:
          typeof record.symbol_key === "string" ? record.symbol_key : null,
      };
    })
    .filter((entry): entry is {
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    } => entry !== null);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries(
  artifact: BenchmarkArtifact,
) {
  return Object.entries(artifact.summary)
    .map(([summaryKey, rawValue]) => {
      const metadataEntry = artifact.source_locations?.summary?.[summaryKey];
      const labelKey =
        typeof metadataEntry?.label_key === "string" && metadataEntry.label_key.trim()
          ? metadataEntry.label_key
          : summaryKey;
      const candidateBindings =
        collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(
          metadataEntry?.candidate_bindings,
        );
      const visibleText = formatBenchmarkArtifactSummaryValue(summaryKey, rawValue);
      if (!visibleText) {
        return null;
      }
      const searchableTexts = [
        ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(
          metadataEntry?.searchable_texts,
        ),
        normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
        normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
          formatBenchmarkArtifactSummaryLabel(labelKey),
        ),
        ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
      ].filter(Boolean);
      return {
        candidateBindings,
        hoverKey: buildComparisonProvenanceArtifactSummaryHoverKey(artifact.path, summaryKey),
        kind: "summary" as const,
        labelKey,
        searchableTexts: Array.from(new Set(searchableTexts)),
        visibleText,
      };
    })
    .filter((entry): entry is {
      candidateBindings: Array<{
        bindingKind: string | null;
        candidateId: string | null;
        runtimeCandidateId: string | null;
        candidatePathTemplate: string | null;
        candidateValue: string | null;
        symbolKey: string | null;
      }>;
      hoverKey: string;
      kind: "summary";
      labelKey: string;
      searchableTexts: string[];
      visibleText: string;
    } => entry !== null);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries(
  artifact: BenchmarkArtifact,
) {
  return Object.entries(artifact.sections ?? {})
    .flatMap(([sectionKey, sectionValue]) => {
      if (!sectionValue || typeof sectionValue !== "object" || Array.isArray(sectionValue)) {
        return [];
      }
      const metadataEntries = artifact.source_locations?.sections?.[sectionKey];
      if (Array.isArray(metadataEntries) && metadataEntries.length) {
        const structuredEntries = metadataEntries
          .map((metadataEntry, fallbackLineIndex) => {
            const lineKey =
              typeof metadataEntry?.line_key === "string" && metadataEntry.line_key.trim()
                ? metadataEntry.line_key
                : "";
            if (!lineKey) {
              return null;
            }
            const rawValue = (sectionValue as Record<string, unknown>)[lineKey];
            const inlineValue = formatBenchmarkArtifactSectionValue(rawValue);
            if (inlineValue === null) {
              return null;
            }
            const lineIndex =
              typeof metadataEntry?.line_index === "number"
                ? metadataEntry.line_index
                : fallbackLineIndex;
            const candidateBindings =
              collectRunSurfaceCollectionQueryRuntimeCandidateArtifactCandidateBindings(
                metadataEntry?.candidate_bindings,
              );
            const visibleText = `${formatBenchmarkArtifactSummaryLabel(lineKey)}: ${inlineValue}`;
            const searchableTexts = [
              ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMetadataMatchTexts(
                metadataEntry?.searchable_texts,
              ),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
                formatBenchmarkArtifactSectionLabel(sectionKey),
              ),
              normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
                formatBenchmarkArtifactSummaryLabel(lineKey),
              ),
              ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
            ].filter(Boolean);
            return {
              candidateBindings,
              hoverKey: buildComparisonProvenanceArtifactSectionLineHoverKey(
                artifact.path,
                sectionKey,
                lineIndex,
              ),
              kind: "section_line" as const,
              labelKey: lineKey,
              searchableTexts: Array.from(new Set(searchableTexts)),
              sectionKey,
              visibleText,
            };
          })
          .filter((entry): entry is {
            candidateBindings: Array<{
              bindingKind: string | null;
              candidateId: string | null;
              runtimeCandidateId: string | null;
              candidatePathTemplate: string | null;
              candidateValue: string | null;
              symbolKey: string | null;
            }>;
            hoverKey: string;
            kind: "section_line";
            labelKey: string;
            searchableTexts: string[];
            sectionKey: string;
            visibleText: string;
          } => entry !== null);
        if (structuredEntries.length) {
          return structuredEntries;
        }
      }
      const sectionEntries = Object.entries(sectionValue)
        .map(([lineKey, rawValue]) => {
          const inlineValue = formatBenchmarkArtifactSectionValue(rawValue);
          if (inlineValue === null) {
            return null;
          }
          const visibleText = `${formatBenchmarkArtifactSummaryLabel(lineKey)}: ${inlineValue}`;
          const searchableTexts = [
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(visibleText),
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
              formatBenchmarkArtifactSectionLabel(sectionKey),
            ),
            normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
              formatBenchmarkArtifactSummaryLabel(lineKey),
            ),
            ...collectRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchTexts(rawValue),
          ].filter(Boolean);
          return {
            candidateBindings: [] as Array<{
              bindingKind: string | null;
              candidateId: string | null;
              runtimeCandidateId: string | null;
              candidatePathTemplate: string | null;
              candidateValue: string | null;
              symbolKey: string | null;
            }>,
            kind: "section_line" as const,
            labelKey: lineKey,
            searchableTexts,
            sectionKey,
            visibleText,
          };
        })
        .filter((entry): entry is {
          candidateBindings: Array<{
            bindingKind: string | null;
            candidateId: string | null;
            runtimeCandidateId: string | null;
            candidatePathTemplate: string | null;
            candidateValue: string | null;
            symbolKey: string | null;
          }>;
          kind: "section_line";
          labelKey: string;
          searchableTexts: string[];
          sectionKey: string;
          visibleText: string;
        } => entry !== null);
      return sectionEntries.map((entry, lineIndex) => ({
        ...entry,
        hoverKey: buildComparisonProvenanceArtifactSectionLineHoverKey(
          artifact.path,
          sectionKey,
          lineIndex,
        ),
      }));
    });
}

export function scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch(params: {
  candidateValue: string;
  entry: {
    candidateBindings?: Array<{
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    }>;
    kind: "section_line" | "summary";
    labelKey: string;
    searchableTexts: string[];
    sectionKey?: string;
    visibleText: string;
  };
  symbolVariants: string[];
}) {
  const { candidateValue, entry, symbolVariants } = params;
  const normalizedCandidateValue =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(candidateValue);
  if (!normalizedCandidateValue) {
    return null;
  }
  const normalizedVisibleText =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry.visibleText);
  const issueMatchesVisibleText = normalizedVisibleText.includes(normalizedCandidateValue);
  const issueMatchesSearchableText = entry.searchableTexts.some((text) =>
    text.includes(normalizedCandidateValue)
  );
  if (!issueMatchesVisibleText && !issueMatchesSearchableText) {
    return null;
  }
  const symbolMatchesVisibleText =
    !symbolVariants.length
    || symbolVariants.some((variant) => normalizedVisibleText.includes(variant));
  const symbolMatchesSearchableText =
    !symbolVariants.length
    || entry.searchableTexts.some((text) =>
      symbolVariants.some((variant) => text.includes(variant))
    );
  if (!symbolMatchesVisibleText && !symbolMatchesSearchableText) {
    return null;
  }
  let score = 0;
  score += issueMatchesVisibleText ? 6 : 3;
  score += symbolMatchesVisibleText ? 4 : 2;
  if (entry.kind === "section_line") {
    score += 3;
  }
  const normalizedSectionKey = entry.sectionKey
    ? normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(entry.sectionKey)
    : "";
  const normalizedLabelKey = normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(
    entry.labelKey,
  );
  if (/issue|context|signal|market|pair/.test(normalizedSectionKey)) {
    score += 2;
  }
  if (/issue|pair|symbol|headline|context|label/.test(normalizedLabelKey)) {
    score += 1;
  }
  return score;
}

export function doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch(params: {
    binding: {
      bindingKind: string | null;
      candidateId: string | null;
      runtimeCandidateId: string | null;
      candidatePathTemplate: string | null;
      candidateValue: string | null;
      symbolKey: string | null;
    };
  candidateReplayId: string | null;
  candidateValue: string;
  resolvedPath: string[];
  symbolKey: string;
}) {
  const { binding, candidateReplayId, candidateValue, resolvedPath, symbolKey } = params;
  if (binding.bindingKind !== "market_data_issue") {
    return false;
  }
  if (binding.runtimeCandidateId && candidateReplayId) {
    return binding.runtimeCandidateId === candidateReplayId;
  }
  if (binding.candidateId && candidateReplayId) {
    return binding.candidateId === candidateReplayId;
  }
  if (binding.candidatePathTemplate !== "provenance.market_data_by_symbol.{symbol_key}.issues") {
    return false;
  }
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
  ) {
    return false;
  }
  const normalizedBindingSymbol =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(binding.symbolKey);
  const normalizedCandidateSymbol =
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactBindingSymbolKey(symbolKey || resolvedPath[2] || "");
  if (!normalizedBindingSymbol || !normalizedCandidateSymbol || normalizedBindingSymbol !== normalizedCandidateSymbol) {
    return false;
  }
  if (!binding.candidateValue) {
    return true;
  }
  return (
    normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(binding.candidateValue)
    === normalizeRunSurfaceCollectionQueryRuntimeCandidateArtifactMatchText(candidateValue)
  );
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateArtifactHoverKeys(params: {
  candidateValueRaw: unknown;
  resolvedParameterValues: Record<string, string>;
  resolvedPath: string[];
  run: Run;
}) {
  const { candidateValueRaw, resolvedParameterValues, resolvedPath, run } = params;
  if (
    resolvedPath[0] !== "provenance"
    || resolvedPath[1] !== "market_data_by_symbol"
    || resolvedPath[3] !== "issues"
    || typeof candidateValueRaw !== "string"
  ) {
    return [];
  }
  const candidateValue = candidateValueRaw.trim();
  if (!candidateValue) {
    return [];
  }
  const candidateReplayId = buildRunSurfaceCollectionQueryRuntimeCandidateReplayId({
    candidateValueRaw,
    resolvedParameterValues,
    resolvedPath,
  });
  const symbolKey = resolvedParameterValues.symbol_key?.trim() || resolvedPath[2] || "";
  const symbolVariants =
    buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSymbolVariants(symbolKey);
  const scoredMatches = run.provenance.benchmark_artifacts.flatMap((artifact) => {
    const artifactEntries = [
      ...buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSummaryMatchEntries(artifact),
      ...buildRunSurfaceCollectionQueryRuntimeCandidateArtifactSectionMatchEntries(artifact),
    ];
    const directValueMatches = artifactEntries.flatMap((entry) => {
      const hasExactBinding = (entry.candidateBindings ?? []).some((binding) =>
        doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch({
          binding,
          candidateReplayId,
          candidateValue,
          resolvedPath,
          symbolKey,
        }) && binding.candidateValue !== null
      );
      return hasExactBinding ? [entry.hoverKey] : [];
    });
    if (directValueMatches.length) {
      return Array.from(new Set(directValueMatches)).map((hoverKey) => ({
        hoverKey,
        score: Number.MAX_SAFE_INTEGER,
      }));
    }
    const directScopedEntries = artifactEntries.filter((entry) =>
      (entry.candidateBindings ?? []).some((binding) =>
        doesRunSurfaceCollectionQueryRuntimeCandidateArtifactDirectBindingMatch({
          binding,
          candidateReplayId,
          candidateValue,
          resolvedPath,
          symbolKey,
        })
      )
    );
    if (directScopedEntries.length) {
      return directScopedEntries.flatMap((entry) => {
        const score = scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch({
          candidateValue,
          entry,
          symbolVariants,
        });
        return score === null ? [{ hoverKey: entry.hoverKey, score: 1000 }] : [{ hoverKey: entry.hoverKey, score: 1000 + score }];
      });
    }
    return artifactEntries.flatMap((entry) => {
      const score = scoreRunSurfaceCollectionQueryRuntimeCandidateArtifactMatch({
        candidateValue,
        entry,
        symbolVariants,
      });
      return score === null ? [] : [{ hoverKey: entry.hoverKey, score }];
    });
  });
  if (!scoredMatches.length) {
    return [];
  }
  const bestScore = scoredMatches.reduce((maximum, entry) => Math.max(maximum, entry.score), 0);
  return Array.from(
    new Set(
      scoredMatches
        .filter((entry) => entry.score === bestScore)
        .map((entry) => entry.hoverKey),
    ),
  );
}

export function buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems(
  original: RunSurfaceCollectionQueryRuntimeCandidateTrace,
  preview: RunSurfaceCollectionQueryRuntimeCandidateTrace,
) {
  const originalByKey = new Map(
    original.allValues.map((sample) => [buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample), sample] as const),
  );
  const previewByKey = new Map(
    preview.allValues.map((sample) => [buildRunSurfaceCollectionQueryRuntimeCandidateSampleKey(sample), sample] as const),
  );
  const allKeys = Array.from(new Set([
    ...originalByKey.keys(),
    ...previewByKey.keys(),
  ])).sort((left, right) => left.localeCompare(right));
  return allKeys.reduce<RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem[]>((accumulator, key) => {
    const originalSample = originalByKey.get(key) ?? null;
    const previewSample = previewByKey.get(key) ?? null;
    if (
      originalSample
      && previewSample
      && originalSample.result === previewSample.result
      && originalSample.candidateValue === previewSample.candidateValue
    ) {
      return accumulator;
    }
    const runId = previewSample?.runId ?? originalSample?.runId ?? "run";
    const pathLabel = previewSample?.candidatePath ?? originalSample?.candidatePath ?? key;
    accumulator.push({
      detail:
        `${originalSample
          ? `${originalSample.candidateValue} (${originalSample.result ? "matched" : "not matched"})`
          : "missing"} -> ${previewSample
          ? `${previewSample.candidateValue} (${previewSample.result ? "matched" : "not matched"})`
          : "missing"}`,
      key,
      runId: `${runId} · ${pathLabel}`,
    });
    return accumulator;
  }, []);
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause(params: {
  bindingContextByKey?: Record<string, string> | null;
  clause: HydratedRunSurfaceCollectionQueryBuilderState;
  contracts: RunSurfaceCollectionQueryContract[];
  detailSuffix?: string | null;
  location: string;
  runs: Run[];
}) {
  const {
    bindingContextByKey = null,
    clause,
    contracts,
    detailSuffix = null,
    location,
    runs,
  } = params;
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  if (!activeContract || !activeSchema) {
    return null;
  }
  const field =
    activeSchema.elementSchema.find((candidate) => candidate.key === clause.fieldKey)
    ?? activeSchema.elementSchema[0]
    ?? null;
  const operator =
    field?.operators.find((candidate) => candidate.key === clause.operatorKey)
    ?? field?.operators[0]
    ?? null;
  if (!field || !operator) {
    return null;
  }
  const resolvedParameterValues = Object.fromEntries(
    activeSchema.parameters.map((parameter) => {
      const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim() ?? "";
      return [
        parameter.key,
        bindingKey
          ? (bindingContextByKey?.[bindingKey] ?? clause.parameterValues[parameter.key] ?? "")
          : (clause.parameterValues[parameter.key] ?? ""),
      ] as const;
    }),
  );
  const resolvedCandidatePath = resolveCollectionQueryPath(activeSchema.pathTemplate, resolvedParameterValues);
  const candidatePath = resolvedCandidatePath.length
    ? `${resolvedCandidatePath.join(".")}[*]`
    : `${clause.schemaId || "collection"}[*]`;
  const candidateAccessor = field.valueRoot
    ? `${activeSchema.itemKind} value`
    : `${activeSchema.itemKind}.${field.valuePath.join(".") || field.key}`;
  const comparedValueOperand = coerceCollectionQueryBuilderValue(
    clause.valueBindingKey
      ? (bindingContextByKey?.[clause.valueBindingKey] ?? clause.builderValue)
      : clause.builderValue,
    field.valueType,
  );
  const comparedValue = clause.valueBindingKey
    ? (
        formatCollectionQueryBuilderValue(comparedValueOperand, field.valueType)
        || `$${clause.valueBindingKey}`
      )
    : (clause.builderValue || "(blank)");
  const concreteRuntimeSamples = buildRunSurfaceCollectionQueryRuntimeCandidateSamples({
    comparedValueLabel: comparedValue,
    comparedValueOperand,
    field,
    operatorKey: clause.operatorKey,
    quantifier: clause.quantifier,
    resolvedParameterValues,
    runs,
    schema: activeSchema,
  });
  return {
    allValues: concreteRuntimeSamples.allValues,
    bindingContextByKey,
    candidateAccessor,
    candidatePath,
    comparedValue,
    detail:
      `${clause.quantifier.toUpperCase()} evaluates ${candidateAccessor} from ${candidatePath} `
      + `${operator.label ?? clause.operatorKey} ${comparedValue}. `
      + (
        concreteRuntimeSamples.sampleTotalCount
          ? `Concrete payload replay: ${concreteRuntimeSamples.sampleMatchCount}/${concreteRuntimeSamples.sampleTotalCount} candidate values matched across ${runs.length} run payloads. `
          : runs.length
            ? "Concrete payload replay found no candidate values across the current run payloads. "
            : "No run payloads are attached to replay concrete candidate values. "
      )
      + (detailSuffix ?? ""),
    editorClause: clause,
    location,
    quantifier: clause.quantifier,
    result: concreteRuntimeSamples.sampleMatchCount > 0,
    runOutcomes: concreteRuntimeSamples.runOutcomes,
    sampleMatchCount: concreteRuntimeSamples.sampleMatchCount,
    sampleTotalCount: concreteRuntimeSamples.sampleTotalCount,
    sampleTruncated: concreteRuntimeSamples.sampleTruncated,
    sampleValues: concreteRuntimeSamples.sampleValues,
  } satisfies RunSurfaceCollectionQueryRuntimeCandidateTrace;
}

export function buildRunSurfaceCollectionQueryRuntimeCandidateClauseReevaluationProjection(params: {
  candidateTrace: RunSurfaceCollectionQueryRuntimeCandidateTrace;
  contracts: RunSurfaceCollectionQueryContract[];
  drillthroughKey: string;
  editorClauseState: HydratedRunSurfaceCollectionQueryBuilderState | null;
  pinnedRuntimeCandidateClauseDiffItems: RunSurfaceCollectionQueryBuilderClauseDiffItem[];
  pinnedRuntimeCandidateClauseOriginKey: string | null;
  runtimeRuns: Run[];
}) {
  const {
    candidateTrace,
    contracts,
    drillthroughKey,
    editorClauseState,
    pinnedRuntimeCandidateClauseDiffItems,
    pinnedRuntimeCandidateClauseOriginKey,
    runtimeRuns,
  } = params;
  const tracePinnedFromClauseDraft = pinnedRuntimeCandidateClauseOriginKey === drillthroughKey;
  const traceClauseDiffItems =
    tracePinnedFromClauseDraft
      ? pinnedRuntimeCandidateClauseDiffItems
      : [];
  const traceReevaluationPreview =
    tracePinnedFromClauseDraft
    && traceClauseDiffItems.length
    && candidateTrace.editorClause
    && editorClauseState
      ? buildRunSurfaceCollectionQueryRuntimeCandidateTraceFromClause({
          bindingContextByKey: candidateTrace.bindingContextByKey,
          clause: editorClauseState,
          contracts,
          detailSuffix: "Draft preview replays the current clause editor state against the same runtime binding context.",
          location: `${candidateTrace.location}:draft_preview`,
          runs: runtimeRuns,
        })
      : null;
  const traceReevaluationPreviewDiffItems =
    traceReevaluationPreview
      ? buildRunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItems(
          candidateTrace,
          traceReevaluationPreview,
        )
      : [];
  return {
    tracePinnedFromClauseDraft,
    traceClauseDiffItems,
    traceReevaluationPreview,
    traceReevaluationPreviewDiffItems,
  };
}

export type PredicateRefReplayApplyHistoryRow = {
  changesCurrent: boolean;
  currentBundleLabel: string;
  currentStatus: string;
  groupKey: string;
  groupLabel: string;
  matchesSimulation: boolean;
  promotedBundleKey: string;
  promotedBundleLabel: string;
  simulatedBundleLabel: string;
  simulatedStatus: string;
};

export type PredicateRefReplayApplyHistoryEntry = {
  appliedAt: string;
  approvedCount: number;
  changedCurrentCount: number;
  id: string;
  matchesSimulationCount: number;
  rollbackSnapshot: {
    draftBindingsByParameterKey: Record<string, string | null>;
    groupSelectionsBySelectionKey: Record<string, string | null>;
  };
  rows: PredicateRefReplayApplyHistoryRow[];
  sourceTabId?: string | null;
  sourceTabLabel?: string | null;
  templateId: string;
  templateLabel: string;
  lastRestoredAt?: string | null;
  lastRestoredByTabId?: string | null;
  lastRestoredByTabLabel?: string | null;
};

export type PredicateRefReplayApplyHistoryTabIdentity = {
  label: string;
  tabId: string;
};

export type PredicateRefReplayApplySyncMode = "live" | "audit_only" | "mute_remote";
export type PredicateRefReplayApplySyncAuditFilter = "all" | "local" | "remote" | "apply" | "restore" | "conflict";
export type PredicateRefReplayApplyConflictPolicy = "prefer_local" | "prefer_remote" | "require_review";

export type PredicateRefReplayApplyConflictEntry = {
  conflictId: string;
  detectedAt: string;
  entryId: string;
  localEntry: PredicateRefReplayApplyHistoryEntry;
  remoteEntry: PredicateRefReplayApplyHistoryEntry;
  sourceTabId: string;
  sourceTabLabel: string;
  templateId: string;
  templateLabel: string;
};

export type PredicateRefReplayApplyConflictDiffItem = {
  decisionKey: string;
  editable: boolean;
  key: string;
  label: string;
  localValue: string;
  remoteValue: string;
  relatedGroupKey?: string | null;
  section: "summary" | "row" | "selection_snapshot" | "binding_snapshot";
};

export type PredicateRefReplayApplyConflictResolutionPreview = {
  effect: string;
  entry: PredicateRefReplayApplyHistoryEntry;
  matchesLocal: boolean;
  matchesRemote: boolean;
  resolution: "local" | "remote" | "merged";
  rowSummaries: string[];
  snapshotSummary: string;
  title: string;
};

export type PredicateRefReplayApplyConflictReview = {
  bindingSnapshotDiffs: PredicateRefReplayApplyConflictDiffItem[];
  conflict: PredicateRefReplayApplyConflictEntry;
  localPreview: PredicateRefReplayApplyConflictResolutionPreview;
  remotePreview: PredicateRefReplayApplyConflictResolutionPreview;
  rowDiffs: PredicateRefReplayApplyConflictDiffItem[];
  selectionSnapshotDiffs: PredicateRefReplayApplyConflictDiffItem[];
  summaryDiffs: PredicateRefReplayApplyConflictDiffItem[];
  totalDiffCount: number;
};

export type PredicateRefReplayApplyConflictDraftReview = PredicateRefReplayApplyConflictReview & {
  editableDiffCount: number;
  hasMixedSelection: boolean;
  hasRemoteSelection: boolean;
  mergedEntry: PredicateRefReplayApplyHistoryEntry;
  mergedPreview: PredicateRefReplayApplyConflictResolutionPreview;
  selectedRemoteCount: number;
  selectedSources: Record<string, "local" | "remote">;
};

export type PredicateRefReplayApplySyncAuditEntry = {
  at: string;
  auditId: string;
  detail: string;
  entryId: string;
  kind:
    | "local_apply"
    | "local_restore"
    | "remote_apply"
    | "remote_restore"
    | "conflict_detected"
    | "conflict_resolved";
  sourceTabId: string;
  sourceTabLabel: string;
  templateId: string;
  templateLabel: string;
};

export type PredicateRefReplayApplySyncAuditTrailState = {
  entries: PredicateRefReplayApplySyncAuditEntry[];
  tabId: string;
  version: number;
};

export type PredicateRefReplayApplySyncGovernanceState = {
  auditFilter: PredicateRefReplayApplySyncAuditFilter;
  conflictPolicy: PredicateRefReplayApplyConflictPolicy;
  syncMode: PredicateRefReplayApplySyncMode;
  tabId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentState = {
  previewSelection: {
    diffItemKey: string | null;
    groupKey: string | null;
    traceKey: string | null;
  };
  replayActionTypeFilter: "all" | "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle";
  replayEdgeFilter: "all" | string;
  replayGroupFilter: "all" | string;
  replayIndex: number;
  replayScope: "all" | string;
  templateId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentStorageState = {
  intentsByTemplateId: Record<string, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayIntentBrowserState = {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  templateId: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkShareMode = "portable" | "indirect";

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry = {
  aliasId: string;
  createdAt: string;
  createdByTabId: string;
  createdByTabLabel: string;
  expiresAt: string | null;
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot;
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  resolutionSource: "local" | "server";
  revokedAt: string | null;
  revokedByTabId: string | null;
  revokedByTabLabel: string | null;
  signature: string | null;
  templateKey: string;
  templateLabel: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAliasState = {
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry = {
  action: "copy" | "share" | "revoke";
  aliasId: string | null;
  at: string;
  id: string;
  linkLength: number;
  mode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  sourceTabId: string;
  sourceTabLabel: string;
  status: "success" | "cancelled" | "failed";
  templateKey: string;
  templateLabel: string;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkAuditState = {
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode = "live" | "opt_out" | "review";

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey =
  | "shareMode"
  | "redactionPolicy"
  | "retentionPolicy"
  | "syncMode";

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry = {
  at: string;
  detail: string;
  diffKeys: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey[];
  fromState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
  id: string;
  kind:
    | "local_change"
    | "remote_sync"
    | "remote_ignored"
    | "conflict_detected"
    | "conflict_resolved_local"
    | "conflict_resolved_remote"
    | "cross_device_export"
    | "cross_device_import";
  remoteSourceTabId: string | null;
  remoteSourceTabLabel: string | null;
  sourceTabId: string;
  sourceTabLabel: string;
  toState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState = {
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[];
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  reviewedConflictKeys: string[];
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState = {
  redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  sourceTabId: string;
  sourceTabLabel: string;
  updatedAt: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload = {
  exportedAt: string;
  governance: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
  sourceTabId: string;
  sourceTabLabel: string;
  version: number;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceChangeSource = {
  detail?: string;
  kind: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry["kind"];
  remoteSourceTabId?: string | null;
  remoteSourceTabLabel?: string | null;
};

export type RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry = {
  conflictKey: string;
  detectedAt: string;
  localRedactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  localRetentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  localShareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  remoteRedactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
  remoteRetentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
  remoteShareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  sourceTabId: string;
  sourceTabLabel: string;
  updatedAt: string;
};

export type PredicateRefReplayApplyConflictState = {
  conflicts: PredicateRefReplayApplyConflictEntry[];
  tabId: string;
  version: number;
};

export type HydratedRunSurfaceCollectionQueryBuilderExpressionState = {
  mode: "single" | "grouped";
  draftClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
  groupLogic: "and" | "or";
  rootNegated: boolean;
  expressionChildren: RunSurfaceCollectionQueryBuilderChildState[];
  predicates: RunSurfaceCollectionQueryBuilderPredicateState[];
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[];
};

export type RunSurfaceCollectionQueryBuilderEditorTarget =
  | { kind: "draft" }
  | { kind: "expression_clause"; childId: string }
  | { kind: "predicate"; predicateId: string }
  | { kind: "template"; templateId: string };

export const RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID = "root";

export function buildRunSurfaceCollectionQueryBuilderEntityId(prefix: string) {
  return `${prefix}:${Math.random().toString(36).slice(2, 10)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-tab-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(tabId: string) {
  return `Tab ${tabId.replace(/[^a-z0-9]/gi, "").slice(0, 4).toUpperCase() || "REPL"}`;
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabIdentity(): PredicateRefReplayApplyHistoryTabIdentity {
  const fallbackTabId = buildRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabId();
  if (typeof window === "undefined") {
    return {
      tabId: fallbackTabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(fallbackTabId),
    };
  }
  try {
    const existingTabId =
      window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY)?.trim();
    const tabId = existingTabId || fallbackTabId;
    if (!existingTabId) {
      window.sessionStorage.setItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_TAB_ID_SESSION_KEY, tabId);
    }
    return {
      tabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(tabId),
    };
  } catch {
    return {
      tabId: fallbackTabId,
      label: formatRunSurfaceCollectionQueryBuilderReplayApplyHistoryTabLabel(fallbackTabId),
    };
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
  tabId: string,
): {
  auditFilter: PredicateRefReplayApplySyncAuditFilter;
  conflictPolicy: PredicateRefReplayApplyConflictPolicy;
  syncMode: PredicateRefReplayApplySyncMode;
} {
  if (typeof window === "undefined") {
    return {
      auditFilter: "all",
      conflictPolicy: "require_review",
      syncMode: "live",
    };
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY);
    if (!raw) {
      return {
        auditFilter: "all",
        conflictPolicy: "require_review",
        syncMode: "live",
      };
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplySyncGovernanceState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION
      || parsed.tabId !== tabId
    ) {
      return {
        auditFilter: "all",
        conflictPolicy: "require_review",
        syncMode: "live",
      };
    }
    return {
      auditFilter:
        parsed.auditFilter === "local"
        || parsed.auditFilter === "remote"
        || parsed.auditFilter === "apply"
        || parsed.auditFilter === "conflict"
        || parsed.auditFilter === "restore"
          ? parsed.auditFilter
          : "all",
      conflictPolicy:
        parsed.conflictPolicy === "prefer_local"
        || parsed.conflictPolicy === "prefer_remote"
          ? parsed.conflictPolicy
          : "require_review",
      syncMode:
        parsed.syncMode === "audit_only" || parsed.syncMode === "mute_remote"
          ? parsed.syncMode
          : "live",
    };
  } catch {
    return {
      auditFilter: "all",
      conflictPolicy: "require_review",
      syncMode: "live",
    };
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplySyncGovernanceState(
  tabId: string,
  state: {
    auditFilter: PredicateRefReplayApplySyncAuditFilter;
    conflictPolicy: PredicateRefReplayApplyConflictPolicy;
    syncMode: PredicateRefReplayApplySyncMode;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplySyncGovernanceState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_VERSION,
      tabId,
      auditFilter: state.auditFilter,
      conflictPolicy: state.conflictPolicy,
      syncMode: state.syncMode,
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_GOVERNANCE_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(
  parsed: Partial<RunSurfaceCollectionQueryBuilderReplayIntentSnapshot> | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null {
  if (!parsed) {
    return null;
  }
  return {
    previewSelection: {
      diffItemKey: typeof parsed.previewSelection?.diffItemKey === "string"
        ? parsed.previewSelection.diffItemKey
        : null,
      groupKey: typeof parsed.previewSelection?.groupKey === "string"
        ? parsed.previewSelection.groupKey
        : null,
      traceKey: typeof parsed.previewSelection?.traceKey === "string"
        ? parsed.previewSelection.traceKey
        : null,
    },
    replayActionTypeFilter:
      parsed.replayActionTypeFilter === "manual_anchor"
      || parsed.replayActionTypeFilter === "dependency_selection"
      || parsed.replayActionTypeFilter === "direct_auto_selection"
      || parsed.replayActionTypeFilter === "conflict_blocked"
      || parsed.replayActionTypeFilter === "idle"
        ? parsed.replayActionTypeFilter
        : "all",
    replayEdgeFilter:
      parsed.replayEdgeFilter === "all"
      || typeof parsed.replayEdgeFilter === "string"
        ? parsed.replayEdgeFilter
        : "all",
    replayGroupFilter:
      parsed.replayGroupFilter === "all"
      || typeof parsed.replayGroupFilter === "string"
        ? parsed.replayGroupFilter
        : "all",
    replayIndex:
      typeof parsed.replayIndex === "number" && Number.isFinite(parsed.replayIndex)
        ? Math.max(0, Math.floor(parsed.replayIndex))
        : 0,
    replayScope:
      parsed.replayScope === "all"
      || typeof parsed.replayScope === "string"
        ? parsed.replayScope
        : "all",
  };
}

export function areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(
  left: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
  right: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
) {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return JSON.stringify(left) === JSON.stringify(right);
}

export function readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(
  raw: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayIntentStorageState | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as
      | Partial<RunSurfaceCollectionQueryBuilderReplayIntentStorageState>
      | Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>
      | null;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return null;
    }
    const parsedStorageState = parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentStorageState>;
    if (
      parsedStorageState.version === RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION
      && parsedStorageState.intentsByTemplateId
      && typeof parsedStorageState.intentsByTemplateId === "object"
      && !Array.isArray(parsedStorageState.intentsByTemplateId)
    ) {
      const intentsByTemplateId = Object.entries(parsedStorageState.intentsByTemplateId).reduce<Record<string, RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>>(
        (acc, [templateId, candidate]) => {
          const normalized = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(
            candidate as Partial<RunSurfaceCollectionQueryBuilderReplayIntentSnapshot>,
          );
          if (normalized) {
            acc[templateId] = normalized;
          }
          return acc;
        },
        {},
      );
      return {
        intentsByTemplateId,
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    }
    if (
      parsed.version === 1
      && typeof (parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>).templateId === "string"
    ) {
      const legacy = parsed as Partial<RunSurfaceCollectionQueryBuilderReplayIntentState>;
      const normalized = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(legacy);
      if (!normalized) {
        return null;
      }
      return {
        intentsByTemplateId: {
          [legacy.templateId as string]: normalized,
        },
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    }
    return null;
  } catch {
    return null;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayIntent(
  templateId: string | null | undefined,
  rawOverride?: string | null,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null {
  if (!templateId) {
    return null;
  }
  const raw =
    typeof rawOverride === "string" || rawOverride === null
      ? rawOverride
      : (typeof window === "undefined"
        ? null
        : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY));
  const parsedState = readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(raw);
  if (!parsedState) {
    return null;
  }
  return parsedState.intentsByTemplateId[templateId] ?? null;
}

export function readRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(
  value: unknown,
): RunSurfaceCollectionQueryBuilderReplayIntentBrowserState | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const candidate = (value as Record<string, unknown>)[RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY];
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
    return null;
  }
  const parsed = candidate as Partial<RunSurfaceCollectionQueryBuilderReplayIntentBrowserState>;
  if (
    parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION
    || typeof parsed.templateId !== "string"
  ) {
    return null;
  }
  const normalizedIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(parsed.intent);
  if (!normalizedIntent) {
    return null;
  }
  return {
    intent: normalizedIntent,
    templateId: parsed.templateId,
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayIntentBrowserState(
  currentState: unknown,
  templateId: string,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
) {
  const nextState =
    currentState && typeof currentState === "object" && !Array.isArray(currentState)
      ? { ...(currentState as Record<string, unknown>) }
      : {};
  nextState[RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_BROWSER_STATE_KEY] = {
    intent,
    templateId,
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
  } satisfies RunSurfaceCollectionQueryBuilderReplayIntentBrowserState;
  return nextState;
}

export function isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null | undefined,
) {
  if (!intent) {
    return true;
  }
  return (
    intent.replayScope === "all"
    && intent.replayIndex === 0
    && intent.replayGroupFilter === "all"
    && intent.replayActionTypeFilter === "all"
    && intent.replayEdgeFilter === "all"
    && intent.previewSelection.groupKey === null
    && intent.previewSelection.traceKey === null
    && intent.previewSelection.diffItemKey === null
  );
}

export function encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
  templateKey: string,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
) {
  if (isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(intent)) {
    return null;
  }
  const payload: Record<string, string | number> = {
    t: templateKey,
  };
  if (intent.replayScope !== "all") {
    payload.s = intent.replayScope;
  }
  if (intent.replayIndex > 0) {
    payload.i = intent.replayIndex;
  }
  if (intent.replayGroupFilter !== "all") {
    payload.g = intent.replayGroupFilter;
  }
  if (intent.replayActionTypeFilter !== "all") {
    payload.a = intent.replayActionTypeFilter;
  }
  if (intent.replayEdgeFilter !== "all") {
    payload.e = intent.replayEdgeFilter;
  }
  if (intent.previewSelection.groupKey) {
    payload.pg = intent.previewSelection.groupKey;
  }
  if (intent.previewSelection.traceKey) {
    payload.pt = intent.previewSelection.traceKey;
  }
  if (intent.previewSelection.diffItemKey) {
    payload.pd = intent.previewSelection.diffItemKey;
  }
  try {
    const json = JSON.stringify(payload);
    if (typeof TextEncoder !== "undefined" && typeof btoa === "function") {
      const bytes = new TextEncoder().encode(json);
      let binary = "";
      bytes.forEach((byte) => {
        binary += String.fromCharCode(byte);
      });
      return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
    if (typeof btoa === "function") {
      return btoa(json).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
  } catch {
    return null;
  }
  return null;
}

export function decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(value: string | null | undefined): {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null;
  templateKey: string | null;
} | null {
  const compactValue = value?.trim() ?? "";
  if (!compactValue) {
    return null;
  }
  try {
    if (typeof atob !== "function") {
      return null;
    }
    const paddedValue = compactValue.replace(/-/g, "+").replace(/_/g, "/");
    const normalizedValue = `${paddedValue}${"===".slice((paddedValue.length + 3) % 4)}`;
    const binary = atob(normalizedValue);
    const json =
      typeof TextDecoder !== "undefined"
        ? new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0)))
        : binary;
    const parsed = JSON.parse(json) as Partial<Record<"t" | "s" | "i" | "g" | "a" | "e" | "pg" | "pt" | "pd", string | number>> | null;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed) || typeof parsed.t !== "string") {
      return null;
    }
    const replayActionTypeFilter =
      parsed.a === "all"
      || parsed.a === "manual_anchor"
      || parsed.a === "dependency_selection"
      || parsed.a === "direct_auto_selection"
      || parsed.a === "conflict_blocked"
      || parsed.a === "idle"
        ? parsed.a
        : undefined;
    return {
      intent: normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({
        previewSelection: {
          diffItemKey: typeof parsed.pd === "string" ? parsed.pd : null,
          groupKey: typeof parsed.pg === "string" ? parsed.pg : null,
          traceKey: typeof parsed.pt === "string" ? parsed.pt : null,
        },
        replayActionTypeFilter,
        replayEdgeFilter: typeof parsed.e === "string" ? parsed.e : undefined,
        replayGroupFilter: typeof parsed.g === "string" ? parsed.g : undefined,
        replayIndex: typeof parsed.i === "number" ? parsed.i : undefined,
        replayScope: typeof parsed.s === "string" ? parsed.s : undefined,
      }),
      templateKey: parsed.t.trim() || null,
    };
  } catch {
    return null;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayIntentFromUrl(): {
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null;
  templateKey: string | null;
} | null {
  if (typeof window === "undefined") {
    return null;
  }
  const params = new URL(window.location.href).searchParams;
  const aliasToken = parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
    params.get(REPLAY_INTENT_ALIAS_SEARCH_PARAM),
  );
  if (aliasToken?.aliasId) {
    const aliasEntry =
      loadRunSurfaceCollectionQueryBuilderReplayLinkAliases().find((entry) => entry.aliasId === aliasToken.aliasId)
      ?? null;
    if (aliasEntry && aliasEntry.resolutionSource !== "server" && !aliasEntry.revokedAt) {
      const recomputedSignature = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature(
        aliasEntry,
        loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret(),
      );
      const signatureMatches =
        aliasEntry.signature
          ? aliasToken.signature === aliasEntry.signature && aliasEntry.signature === recomputedSignature
          : !aliasToken.signature;
      if (signatureMatches) {
        return {
          intent: aliasEntry.intent,
          templateKey: aliasEntry.templateKey,
        };
      }
    }
  }
  const compactIntent = decodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
    params.get(REPLAY_INTENT_SEARCH_PARAM),
  );
  if (compactIntent) {
    return compactIntent;
  }
  const templateKey = params.get(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM)?.trim() ?? "";
  const hasReplayParam = [
    REPLAY_INTENT_TEMPLATE_SEARCH_PARAM,
    REPLAY_INTENT_SCOPE_SEARCH_PARAM,
    REPLAY_INTENT_STEP_SEARCH_PARAM,
    REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM,
    REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM,
  ].some((key) => params.has(key));
  if (!hasReplayParam) {
    return null;
  }
  const replayActionTypeFilterRaw = params.get(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM)?.trim() ?? "";
  const replayActionTypeFilter:
    RunSurfaceCollectionQueryBuilderReplayIntentSnapshot["replayActionTypeFilter"]
    | undefined =
      replayActionTypeFilterRaw === "all"
      || replayActionTypeFilterRaw === "manual_anchor"
      || replayActionTypeFilterRaw === "dependency_selection"
      || replayActionTypeFilterRaw === "direct_auto_selection"
      || replayActionTypeFilterRaw === "conflict_blocked"
      || replayActionTypeFilterRaw === "idle"
        ? replayActionTypeFilterRaw
        : undefined;
  const intent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot({
    previewSelection: {
      diffItemKey: params.get(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM)?.trim() ?? null,
      groupKey: params.get(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM)?.trim() ?? null,
      traceKey: params.get(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM)?.trim() ?? null,
    },
    replayActionTypeFilter,
    replayEdgeFilter: params.get(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM)?.trim() ?? undefined,
    replayGroupFilter: params.get(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM)?.trim() ?? undefined,
    replayIndex: (() => {
      const raw = params.get(REPLAY_INTENT_STEP_SEARCH_PARAM);
      if (raw === null) {
        return undefined;
      }
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : undefined;
    })(),
    replayScope: params.get(REPLAY_INTENT_SCOPE_SEARCH_PARAM)?.trim() ?? undefined,
  });
  return {
    intent,
    templateKey: templateKey || null,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayIntentUrl(
  templateKey: string | null | undefined,
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot | null,
  baseHref?: string,
  options?: {
    aliasId?: string | null;
    forceTemplateKey?: boolean;
  },
) {
  const url =
    typeof window !== "undefined"
      ? new URL(baseHref ?? window.location.href)
      : new URL(baseHref ?? "http://localhost/");
  const params = url.searchParams;
  params.delete(REPLAY_INTENT_ALIAS_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_SCOPE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_STEP_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM);
  params.delete(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM);
  if (options?.aliasId?.trim()) {
    params.set(REPLAY_INTENT_ALIAS_SEARCH_PARAM, options.aliasId.trim());
    const nextSearch = params.toString();
    return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
  }
  const normalizedIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(intent);
  const normalizedTemplateKey = templateKey?.trim() ?? "";
  const shouldEmitTemplateIntent =
    normalizedTemplateKey
    && normalizedIntent
    && (
      options?.forceTemplateKey
      || !isDefaultRunSurfaceCollectionQueryBuilderReplayIntent(normalizedIntent)
    );
  if (shouldEmitTemplateIntent) {
    const compactValue = encodeRunSurfaceCollectionQueryBuilderReplayIntentCompactValue(
      normalizedTemplateKey,
      normalizedIntent,
    );
    if (compactValue && !options?.forceTemplateKey) {
      params.set(REPLAY_INTENT_SEARCH_PARAM, compactValue);
    } else {
      params.set(REPLAY_INTENT_TEMPLATE_SEARCH_PARAM, normalizedTemplateKey);
      if (normalizedIntent.replayScope !== "all") {
        params.set(REPLAY_INTENT_SCOPE_SEARCH_PARAM, normalizedIntent.replayScope);
      }
      if (normalizedIntent.replayIndex > 0) {
        params.set(REPLAY_INTENT_STEP_SEARCH_PARAM, String(normalizedIntent.replayIndex));
      }
      if (normalizedIntent.replayGroupFilter !== "all") {
        params.set(REPLAY_INTENT_GROUP_FILTER_SEARCH_PARAM, normalizedIntent.replayGroupFilter);
      }
      if (normalizedIntent.replayActionTypeFilter !== "all") {
        params.set(REPLAY_INTENT_ACTION_FILTER_SEARCH_PARAM, normalizedIntent.replayActionTypeFilter);
      }
      if (normalizedIntent.replayEdgeFilter !== "all") {
        params.set(REPLAY_INTENT_EDGE_FILTER_SEARCH_PARAM, normalizedIntent.replayEdgeFilter);
      }
      if (normalizedIntent.previewSelection.groupKey) {
        params.set(REPLAY_INTENT_PREVIEW_GROUP_SEARCH_PARAM, normalizedIntent.previewSelection.groupKey);
      }
      if (normalizedIntent.previewSelection.traceKey) {
        params.set(REPLAY_INTENT_PREVIEW_TRACE_SEARCH_PARAM, normalizedIntent.previewSelection.traceKey);
      }
      if (normalizedIntent.previewSelection.diffItemKey) {
        params.set(REPLAY_INTENT_PREVIEW_DIFF_SEARCH_PARAM, normalizedIntent.previewSelection.diffItemKey);
      }
    }
  }
  const nextSearch = params.toString();
  return `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash}`;
}

export function applyRunSurfaceCollectionQueryBuilderReplayIntentRedactionPolicy(
  intent: RunSurfaceCollectionQueryBuilderReplayIntentSnapshot,
  policy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
): RunSurfaceCollectionQueryBuilderReplayIntentSnapshot {
  if (policy === "full") {
    return intent;
  }
  if (policy === "omit_preview") {
    return {
      ...intent,
      previewSelection: {
        diffItemKey: null,
        groupKey: null,
        traceKey: null,
      },
    };
  }
  return {
    previewSelection: {
      diffItemKey: null,
      groupKey: null,
      traceKey: null,
    },
    replayActionTypeFilter: intent.replayActionTypeFilter,
    replayEdgeFilter: "all",
    replayGroupFilter: intent.replayGroupFilter,
    replayIndex: 0,
    replayScope: intent.replayScope,
  };
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasId() {
  const randomSegment = Math.random().toString(36).slice(2, 10);
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID().replace(/-/g, "").slice(0, 10);
  }
  return `rl${randomSegment}`.slice(0, 10);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
  value: unknown,
): RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy {
  return value === "1d" || value === "7d" || value === "manual" ? value : "30d";
}

export function getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  switch (retentionPolicy) {
    case "1d":
      return 24 * 60 * 60 * 1000;
    case "7d":
      return 7 * 24 * 60 * 60 * 1000;
    case "30d":
      return 30 * 24 * 60 * 60 * 1000;
    case "manual":
    default:
      return null;
  }
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkExpiry(
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
  createdAt: string,
) {
  const duration = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (!duration) {
    return null;
  }
  const createdAtMs = Date.parse(createdAt);
  if (!Number.isFinite(createdAtMs)) {
    return null;
  }
  return new Date(createdAtMs + duration).toISOString();
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-secret-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret() {
  if (typeof window === "undefined") {
    return "replay-link-secret";
  }
  try {
    const existingSecret =
      window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY)?.trim();
    if (existingSecret) {
      return existingSecret;
    }
    const nextSecret = buildRunSurfaceCollectionQueryBuilderReplayLinkSigningSecret();
    window.localStorage.setItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_SIGNING_SECRET_STORAGE_KEY, nextSecret);
    return nextSecret;
  } catch {
    return "replay-link-secret";
  }
}

export function hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(input: string) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return (hash >>> 0).toString(36);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload(
  entry: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
    "aliasId" | "createdAt" | "expiresAt" | "intent" | "redactionPolicy" | "templateKey"
  >,
) {
  return JSON.stringify({
    a: entry.aliasId,
    c: entry.createdAt,
    e: entry.expiresAt,
    i: entry.intent,
    r: entry.redactionPolicy,
    t: entry.templateKey,
  });
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignature(
  entry: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry,
    "aliasId" | "createdAt" | "expiresAt" | "intent" | "redactionPolicy" | "templateKey"
  >,
  signingSecret: string,
) {
  const payload = `${signingSecret}:${buildRunSurfaceCollectionQueryBuilderReplayLinkAliasSignaturePayload(entry)}`;
  const primary = hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(payload);
  const secondary = hashRunSurfaceCollectionQueryBuilderReplayLinkSignatureSegment(
    payload.split("").reverse().join(""),
  );
  return `${primary}${secondary}`.slice(0, 18);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
  aliasId: string,
  signature: string | null | undefined,
) {
  return signature?.trim() ? `${aliasId}.${signature.trim()}` : aliasId;
}

export function parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
  value: string | null | undefined,
) {
  const token = value?.trim() ?? "";
  if (!token) {
    return null;
  }
  const lastSeparatorIndex = token.lastIndexOf(".");
  if (lastSeparatorIndex <= 0) {
    return {
      aliasId: token,
      signature: null,
    };
  }
  return {
    aliasId: token.slice(0, lastSeparatorIndex),
    signature: token.slice(lastSeparatorIndex + 1) || null,
  };
}

export function extractRunSurfaceCollectionQueryBuilderReplayLinkAliasTokenFromUrl() {
  if (typeof window === "undefined") {
    return null;
  }
  return parseRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
    new URL(window.location.href).searchParams.get(REPLAY_INTENT_ALIAS_SEARCH_PARAM),
  );
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-link-governance-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot(
  state: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  return {
    redactionPolicy: state.redactionPolicy,
    retentionPolicy: state.retentionPolicy,
    shareMode: state.shareMode,
    syncMode: state.syncMode,
  } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot;
}

export function getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
  fromState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
  toState: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  const diffKeys: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey[] = [];
  if (fromState.shareMode !== toState.shareMode) {
    diffKeys.push("shareMode");
  }
  if (fromState.redactionPolicy !== toState.redactionPolicy) {
    diffKeys.push("redactionPolicy");
  }
  if (fromState.retentionPolicy !== toState.retentionPolicy) {
    diffKeys.push("retentionPolicy");
  }
  if (fromState.syncMode !== toState.syncMode) {
    diffKeys.push("syncMode");
  }
  return diffKeys;
}

export function formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue(
  fieldKey: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditFieldKey,
  state: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSnapshot,
) {
  switch (fieldKey) {
    case "shareMode":
      return state.shareMode === "indirect" ? "Local alias link" : "Portable deep link";
    case "redactionPolicy":
      return state.redactionPolicy.replaceAll("_", " ");
    case "retentionPolicy":
      return state.retentionPolicy === "manual"
        ? "Keep until cleared"
        : state.retentionPolicy === "1d"
          ? "1 day"
          : state.retentionPolicy === "7d"
            ? "7 days"
            : "30 days";
    case "syncMode":
      return state.syncMode === "opt_out"
        ? "Ignore remote changes"
        : state.syncMode === "review"
          ? "Review remote changes"
          : "Live sync";
    default:
      return "n/a";
  }
}

export function encodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload(
  payload: RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload,
) {
  try {
    const json = JSON.stringify(payload);
    if (typeof TextEncoder !== "undefined" && typeof btoa === "function") {
      const bytes = new TextEncoder().encode(json);
      let binary = "";
      bytes.forEach((byte) => {
        binary += String.fromCharCode(byte);
      });
      return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
    if (typeof btoa === "function") {
      return btoa(json).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/u, "");
    }
  } catch {
    return null;
  }
  return null;
}

export function decodeRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload(
  value: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload | null {
  const compactValue = value?.trim() ?? "";
  if (!compactValue || typeof atob !== "function") {
    return null;
  }
  try {
    const paddedValue = compactValue.replace(/-/g, "+").replace(/_/g, "/");
    const normalizedValue = `${paddedValue}${"===".slice((paddedValue.length + 3) % 4)}`;
    const binary = atob(normalizedValue);
    const json =
      typeof TextDecoder !== "undefined"
        ? new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0)))
        : binary;
    const parsed = JSON.parse(json) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION
      || !parsed.governance
      || typeof parsed.sourceTabId !== "string"
      || typeof parsed.sourceTabLabel !== "string"
      || typeof parsed.exportedAt !== "string"
    ) {
      return null;
    }
    return {
      exportedAt: parsed.exportedAt,
      governance: {
        redactionPolicy:
          parsed.governance.redactionPolicy === "omit_preview"
          || parsed.governance.redactionPolicy === "summary_only"
            ? parsed.governance.redactionPolicy
            : "full",
        retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
          parsed.governance.retentionPolicy,
        ),
        shareMode: parsed.governance.shareMode === "indirect" ? "indirect" : "portable",
        syncMode:
          parsed.governance.syncMode === "opt_out" || parsed.governance.syncMode === "review"
            ? parsed.governance.syncMode
            : "live",
      },
      sourceTabId: parsed.sourceTabId,
      sourceTabLabel: parsed.sourceTabLabel,
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_PAYLOAD_VERSION,
    };
  } catch {
    return null;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAliases() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAliasesFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkAliasState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION
      || !Array.isArray(parsed.aliases)
    ) {
      return [];
    }
    return parsed.aliases.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry =>
      Boolean(
        entry
        && typeof entry.aliasId === "string"
        && typeof entry.createdAt === "string"
        && (typeof entry.expiresAt === "string" || entry.expiresAt === null || entry.expiresAt === undefined)
        && (typeof entry.signature === "string" || entry.signature === null || entry.signature === undefined)
        && typeof entry.templateKey === "string"
        && typeof entry.templateLabel === "string",
      ),
    ).map((entry): RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry => ({
      ...entry,
      expiresAt: typeof entry.expiresAt === "string" ? entry.expiresAt : null,
      resolutionSource: entry.resolutionSource === "server" ? "server" : "local",
      revokedAt: typeof entry.revokedAt === "string" ? entry.revokedAt : null,
      revokedByTabId: typeof entry.revokedByTabId === "string" ? entry.revokedByTabId : null,
      revokedByTabLabel: typeof entry.revokedByTabLabel === "string" ? entry.revokedByTabLabel : null,
      signature: typeof entry.signature === "string" ? entry.signature : null,
    })).filter((entry) =>
      !entry.expiresAt || Date.parse(entry.expiresAt) > Date.now(),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_KEY,
      JSON.stringify({
        aliases: aliases.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkAliasState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkAuditTrailFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkAuditState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry =>
      Boolean(
        entry
        && typeof entry.id === "string"
        && typeof entry.at === "string"
        && typeof entry.templateKey === "string"
        && typeof entry.templateLabel === "string",
      ),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_KEY,
      JSON.stringify({
        entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkAuditState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail() {
  return loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY),
  );
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrailFromStorageValue(
  raw: string | null | undefined,
) {
  if (typeof window === "undefined") {
    return [] as RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[];
  }
  try {
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries.filter((entry): entry is RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry =>
      Boolean(
        entry
        && typeof entry.id === "string"
        && typeof entry.at === "string"
        && typeof entry.kind === "string"
        && typeof entry.sourceTabId === "string"
        && typeof entry.sourceTabLabel === "string"
        && Array.isArray(entry.diffKeys),
      ),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_KEY,
      JSON.stringify({
        entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState() {
  const defaultState = {
    redactionPolicy: "full" as const,
    reviewedConflictKeys: [] as string[],
    retentionPolicy: "30d" as const,
    shareMode: "portable" as const,
    syncMode: "live" as const,
  };
  if (typeof window === "undefined") {
    return defaultState;
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY);
    if (!raw) {
      return defaultState;
    }
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState> | null;
    return {
      redactionPolicy:
        parsed?.redactionPolicy === "omit_preview" || parsed?.redactionPolicy === "summary_only"
          ? parsed.redactionPolicy
          : defaultState.redactionPolicy,
      reviewedConflictKeys: Array.isArray(parsed?.reviewedConflictKeys)
        ? parsed.reviewedConflictKeys
          .filter((value): value is string => typeof value === "string")
          .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS)
        : defaultState.reviewedConflictKeys,
      retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
        parsed?.retentionPolicy,
      ),
      shareMode:
        parsed?.shareMode === "indirect"
          ? "indirect"
          : defaultState.shareMode,
      syncMode:
        parsed?.syncMode === "opt_out" || parsed?.syncMode === "review"
          ? parsed.syncMode
          : defaultState.syncMode,
    } as const;
  } catch {
    return defaultState;
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceState(
  state: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    reviewedConflictKeys: string[];
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
    syncMode: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_KEY,
      JSON.stringify({
        ...state,
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SESSION_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceState),
    );
  } catch {
    return;
  }
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  current: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
) {
  const byId = new Map<string, RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry>();
  [...incoming, ...current].forEach((entry) => {
    const existing = byId.get(entry.aliasId);
    if (!existing || existing.createdAt < entry.createdAt) {
      byId.set(entry.aliasId, entry);
    }
  });
  return Array.from(byId.values())
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_ALIAS_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkAliases(
  aliases: RunSurfaceCollectionQueryBuilderReplayLinkAliasEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  const nowMs = Date.now();
  return aliases.filter((entry) => {
    if (entry.expiresAt && Date.parse(entry.expiresAt) <= nowMs) {
      return false;
    }
    if (cutoffMs === null) {
      return true;
    }
    const createdAtMs = Date.parse(entry.createdAt);
    if (!Number.isFinite(createdAtMs)) {
      return false;
    }
    return nowMs - createdAtMs <= cutoffMs;
  });
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  current: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
) {
  const seen = new Set<string>();
  return [...incoming, ...current]
    .filter((entry) => {
      if (seen.has(entry.id)) {
        return false;
      }
      seen.add(entry.id);
      return true;
    })
    .sort((left, right) => right.at.localeCompare(left.at))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_AUDIT_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkAuditEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (cutoffMs === null) {
    return entries;
  }
  const nowMs = Date.now();
  return entries.filter((entry) => {
    const entryMs = Date.parse(entry.at);
    return Number.isFinite(entryMs) && nowMs - entryMs <= cutoffMs;
  });
}

export function mergeRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  current: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
  incoming: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
) {
  const seen = new Set<string>();
  return [...incoming, ...current]
    .filter((entry) => {
      if (seen.has(entry.id)) {
        return false;
      }
      seen.add(entry.id);
      return true;
    })
    .sort((left, right) => right.at.localeCompare(left.at))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_AUDIT_ENTRIES);
}

export function pruneRunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditTrail(
  entries: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceAuditEntry[],
  retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
) {
  const cutoffMs = getRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicyDurationMs(retentionPolicy);
  if (cutoffMs === null) {
    return entries;
  }
  const nowMs = Date.now();
  return entries.filter((entry) => {
    const entryMs = Date.parse(entry.at);
    return Number.isFinite(entryMs) && nowMs - entryMs <= cutoffMs;
  });
}

export function persistRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(
  state: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
    sourceTabId: string;
    sourceTabLabel: string;
  },
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_KEY,
      JSON.stringify({
        ...state,
        updatedAt: new Date().toISOString(),
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
      } satisfies RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState),
    );
  } catch {
    return;
  }
}

export function limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceReviewedConflictKeys(keys: string[]) {
  const seen = new Set<string>();
  return keys.filter((key) => {
    if (!key || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  }).slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_REVIEWED_CONFLICT_KEYS);
}

export function buildRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictKey(
  state: Pick<
    RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState,
    "redactionPolicy" | "retentionPolicy" | "shareMode" | "sourceTabId" | "updatedAt"
  >,
) {
  return [
    state.sourceTabId,
    state.updatedAt,
    state.shareMode,
    state.redactionPolicy,
    state.retentionPolicy,
  ].join(":");
}

export function limitRunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflicts(
  conflicts: RunSurfaceCollectionQueryBuilderReplayLinkGovernanceConflictEntry[],
) {
  return conflicts.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_CONFLICT_ENTRIES);
}

export function areRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSelectionsEqual(
  left: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  },
  right: {
    redactionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy;
    retentionPolicy: RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy;
    shareMode: RunSurfaceCollectionQueryBuilderReplayLinkShareMode;
  },
) {
  return (
    left.redactionPolicy === right.redactionPolicy
    && left.retentionPolicy === right.retentionPolicy
    && left.shareMode === right.shareMode
  );
}

export function readRunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState(
  raw: string | null | undefined,
): RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION
      || typeof parsed.sourceTabId !== "string"
      || typeof parsed.sourceTabLabel !== "string"
      || typeof parsed.updatedAt !== "string"
    ) {
      return null;
    }
    return {
      redactionPolicy:
        parsed.redactionPolicy === "omit_preview" || parsed.redactionPolicy === "summary_only"
          ? parsed.redactionPolicy
          : "full",
      retentionPolicy: normalizeRunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy(
        parsed.retentionPolicy,
      ),
      shareMode: parsed.shareMode === "indirect" ? "indirect" : "portable",
      sourceTabId: parsed.sourceTabId,
      sourceTabLabel: parsed.sourceTabLabel,
      updatedAt: parsed.updatedAt,
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_LINK_GOVERNANCE_SYNC_STORAGE_VERSION,
    };
  } catch {
    return null;
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayIntent(
  state: Omit<RunSurfaceCollectionQueryBuilderReplayIntentState, "version">,
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const currentState =
      readRunSurfaceCollectionQueryBuilderReplayIntentStorageState(
        window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY),
      )
      ?? {
        intentsByTemplateId: {},
        version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
      };
    const nextIntent = normalizeRunSurfaceCollectionQueryBuilderReplayIntentSnapshot(state);
    if (!nextIntent) {
      return;
    }
    const currentIntent = currentState.intentsByTemplateId[state.templateId] ?? null;
    if (areRunSurfaceCollectionQueryBuilderReplayIntentsEqual(currentIntent, nextIntent)) {
      return;
    }
    const nextState: RunSurfaceCollectionQueryBuilderReplayIntentStorageState = {
      intentsByTemplateId: {
        ...currentState.intentsByTemplateId,
        [state.templateId]: nextIntent,
      },
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_VERSION,
    };
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_INTENT_STORAGE_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplySyncAuditId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-audit-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function buildRunSurfaceCollectionQueryBuilderReplayApplyConflictId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `replay-conflict-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function limitPredicateRefReplayApplySyncAuditEntries(entries: PredicateRefReplayApplySyncAuditEntry[]) {
  return entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_ENTRIES);
}

export function mergePredicateRefReplayApplySyncAuditEntries(
  currentEntries: PredicateRefReplayApplySyncAuditEntry[],
  incomingEntries: PredicateRefReplayApplySyncAuditEntry[],
) {
  const seen = new Set<string>();
  const merged = [...incomingEntries, ...currentEntries].filter((entry) => {
    const dedupeKey = `${entry.entryId}:${entry.kind}:${entry.at}:${entry.sourceTabId}`;
    if (seen.has(dedupeKey)) {
      return false;
    }
    seen.add(dedupeKey);
    return true;
  });
  return limitPredicateRefReplayApplySyncAuditEntries(merged);
}

export function limitPredicateRefReplayApplyConflictEntries(
  entries: PredicateRefReplayApplyConflictEntry[],
) {
  return entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICT_ENTRIES);
}

export function serializeComparablePredicateRefReplayApplyHistoryEntry(entry: PredicateRefReplayApplyHistoryEntry) {
  return JSON.stringify({
    appliedAt: entry.appliedAt,
    approvedCount: entry.approvedCount,
    changedCurrentCount: entry.changedCurrentCount,
    id: entry.id,
    lastRestoredAt: entry.lastRestoredAt ?? null,
    lastRestoredByTabId: entry.lastRestoredByTabId ?? null,
    matchesSimulationCount: entry.matchesSimulationCount,
    rollbackSnapshot: entry.rollbackSnapshot,
    rows: entry.rows,
    sourceTabId: entry.sourceTabId ?? null,
    templateId: entry.templateId,
    templateLabel: entry.templateLabel,
  });
}

export function arePredicateRefReplayApplyHistoryEntriesEquivalent(
  left: PredicateRefReplayApplyHistoryEntry,
  right: PredicateRefReplayApplyHistoryEntry,
) {
  return serializeComparablePredicateRefReplayApplyHistoryEntry(left)
    === serializeComparablePredicateRefReplayApplyHistoryEntry(right);
}

export function serializeComparablePredicateRefReplayApplyHistoryRow(row?: PredicateRefReplayApplyHistoryRow | null) {
  if (!row) {
    return "";
  }
  return JSON.stringify(row);
}

export function formatPredicateRefReplayApplyHistorySnapshotValue(value?: string | null) {
  if (value === null || value === undefined) {
    return "clear";
  }
  return value || '""';
}

export function formatPredicateRefReplayApplyHistorySelectionKeyLabel(selectionKey: string) {
  const parts = selectionKey.split(":").filter(Boolean);
  return parts.length ? parts[parts.length - 1] : selectionKey;
}

export function formatPredicateRefReplayApplyHistoryRowSummary(row?: PredicateRefReplayApplyHistoryRow | null) {
  if (!row) {
    return "No replay row in this version.";
  }
  return `${row.currentStatus} · ${row.currentBundleLabel} → ${row.promotedBundleLabel} · simulated ${row.simulatedStatus} · ${row.simulatedBundleLabel}`;
}

export function clonePredicateRefReplayApplyHistoryEntry(
  entry: PredicateRefReplayApplyHistoryEntry,
): PredicateRefReplayApplyHistoryEntry {
  return {
    ...entry,
    rollbackSnapshot: {
      draftBindingsByParameterKey: { ...entry.rollbackSnapshot.draftBindingsByParameterKey },
      groupSelectionsBySelectionKey: { ...entry.rollbackSnapshot.groupSelectionsBySelectionKey },
    },
    rows: entry.rows.map((row) => ({ ...row })),
  };
}

export function buildPredicateRefReplayApplyConflictResolutionPreview(
  conflict: PredicateRefReplayApplyConflictEntry,
  entry: PredicateRefReplayApplyHistoryEntry,
  resolution: "local" | "remote" | "merged",
  effect: string,
): PredicateRefReplayApplyConflictResolutionPreview {
  const rollbackGroupCount = Object.keys(entry.rollbackSnapshot.groupSelectionsBySelectionKey).length;
  const rollbackBindingCount = Object.keys(entry.rollbackSnapshot.draftBindingsByParameterKey).length;
  return {
    resolution,
    entry,
    title:
      resolution === "local"
        ? "Keep local version"
        : resolution === "remote"
          ? "Apply remote version"
          : "Apply reviewed merge",
    effect,
    snapshotSummary: `${rollbackGroupCount} rollback groups · ${rollbackBindingCount} rollback bindings`,
    rowSummaries: entry.rows.slice(0, 3).map(
      (row) => `${row.groupLabel}: ${row.currentBundleLabel} → ${row.promotedBundleLabel}`,
    ),
    matchesLocal: arePredicateRefReplayApplyHistoryEntriesEquivalent(entry, conflict.localEntry),
    matchesRemote: arePredicateRefReplayApplyHistoryEntriesEquivalent(entry, conflict.remoteEntry),
  };
}

export function buildPredicateRefReplayApplyConflictMergedEntry(
  conflict: PredicateRefReplayApplyConflictEntry,
  selectedSources: Record<string, "local" | "remote">,
) {
  const mergedEntry = clonePredicateRefReplayApplyHistoryEntry(conflict.localEntry);
  const getSelectedSource = (decisionKey: string) => selectedSources[decisionKey] ?? "local";
  const applyScalar = <K extends keyof PredicateRefReplayApplyHistoryEntry>(
    decisionKey: string,
    fieldKey: K,
  ) => {
    if (getSelectedSource(decisionKey) === "remote") {
      mergedEntry[fieldKey] = conflict.remoteEntry[fieldKey];
    }
  };
  applyScalar("summary:applied_at", "appliedAt");
  if (getSelectedSource("summary:source_tab") === "remote") {
    mergedEntry.sourceTabId = conflict.remoteEntry.sourceTabId ?? null;
    mergedEntry.sourceTabLabel = conflict.remoteEntry.sourceTabLabel ?? null;
  }
  if (getSelectedSource("summary:last_restored_at") === "remote") {
    mergedEntry.lastRestoredAt = conflict.remoteEntry.lastRestoredAt ?? null;
  }
  if (getSelectedSource("summary:last_restored_by") === "remote") {
    mergedEntry.lastRestoredByTabId = conflict.remoteEntry.lastRestoredByTabId ?? null;
    mergedEntry.lastRestoredByTabLabel = conflict.remoteEntry.lastRestoredByTabLabel ?? null;
  }

  const rowGroupKeys = Array.from(
    new Set([
      ...conflict.localEntry.rows.map((row) => row.groupKey),
      ...conflict.remoteEntry.rows.map((row) => row.groupKey),
    ]),
  );
  const mergedRows = rowGroupKeys.flatMap((groupKey) => {
    const source = getSelectedSource(`row:${groupKey}`);
    const sourceRow = (
      source === "remote"
        ? conflict.remoteEntry.rows.find((row) => row.groupKey === groupKey)
        : conflict.localEntry.rows.find((row) => row.groupKey === groupKey)
    ) ?? null;
    return sourceRow ? [{ ...sourceRow }] : [];
  });
  mergedEntry.rows = mergedRows.sort((left, right) => left.groupKey.localeCompare(right.groupKey));
  mergedEntry.approvedCount = mergedEntry.rows.length;
  mergedEntry.changedCurrentCount = mergedEntry.rows.filter((row) => row.changesCurrent).length;
  mergedEntry.matchesSimulationCount = mergedEntry.rows.filter((row) => row.matchesSimulation).length;

  const applySnapshotRecord = (
    decisionKey: string,
    snapshotKey: string,
    fieldKey: "groupSelectionsBySelectionKey" | "draftBindingsByParameterKey",
  ) => {
    const sourceRecord = (
      getSelectedSource(decisionKey) === "remote"
        ? conflict.remoteEntry.rollbackSnapshot[fieldKey]
        : conflict.localEntry.rollbackSnapshot[fieldKey]
    );
    if (Object.prototype.hasOwnProperty.call(sourceRecord, snapshotKey)) {
      mergedEntry.rollbackSnapshot[fieldKey][snapshotKey] = sourceRecord[snapshotKey] ?? null;
      return;
    }
    delete mergedEntry.rollbackSnapshot[fieldKey][snapshotKey];
  };
  Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
    ]),
  ).forEach((selectionKey) => {
    applySnapshotRecord(
      `selection_snapshot:${selectionKey}`,
      selectionKey,
      "groupSelectionsBySelectionKey",
    );
  });
  Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey),
    ]),
  ).forEach((parameterKey) => {
    applySnapshotRecord(
      `binding_snapshot:${parameterKey}`,
      parameterKey,
      "draftBindingsByParameterKey",
    );
  });
  return mergedEntry;
}

export function buildPredicateRefReplayApplyConflictReview(
  conflict: PredicateRefReplayApplyConflictEntry,
  localTabLabel: string,
  parameterGroupKeyByParameterKey: Record<string, string> = {},
): PredicateRefReplayApplyConflictReview {
  const summaryDiffs: PredicateRefReplayApplyConflictDiffItem[] = [];
  const pushSummaryDiff = (
    key: string,
    label: string,
    localValue: string,
    remoteValue: string,
    editable = false,
  ) => {
    if (localValue === remoteValue) {
      return;
    }
    summaryDiffs.push({
      decisionKey: `summary:${key}`,
      editable,
      key,
      label,
      localValue,
      remoteValue,
      section: "summary",
    });
  };
  pushSummaryDiff(
    "applied_at",
    "Applied at",
    formatRelativeTimestampLabel(conflict.localEntry.appliedAt),
    formatRelativeTimestampLabel(conflict.remoteEntry.appliedAt),
    true,
  );
  pushSummaryDiff(
    "approved_count",
    "Approved rows",
    String(conflict.localEntry.approvedCount),
    String(conflict.remoteEntry.approvedCount),
  );
  pushSummaryDiff(
    "changed_current_count",
    "Changed current",
    String(conflict.localEntry.changedCurrentCount),
    String(conflict.remoteEntry.changedCurrentCount),
  );
  pushSummaryDiff(
    "matches_simulation_count",
    "Matched simulated",
    String(conflict.localEntry.matchesSimulationCount),
    String(conflict.remoteEntry.matchesSimulationCount),
  );
  pushSummaryDiff(
    "source_tab",
    "Applied by",
    conflict.localEntry.sourceTabLabel ?? localTabLabel,
    conflict.remoteEntry.sourceTabLabel ?? conflict.sourceTabLabel,
    true,
  );
  pushSummaryDiff(
    "last_restored_at",
    "Last restored",
    formatRelativeTimestampLabel(conflict.localEntry.lastRestoredAt),
    formatRelativeTimestampLabel(conflict.remoteEntry.lastRestoredAt),
    true,
  );
  pushSummaryDiff(
    "last_restored_by",
    "Restored by",
    conflict.localEntry.lastRestoredByTabLabel ?? "Not restored",
    conflict.remoteEntry.lastRestoredByTabLabel ?? "Not restored",
    true,
  );

  const rowDiffs = Array.from(
    new Set([
      ...conflict.localEntry.rows.map((row) => row.groupKey),
      ...conflict.remoteEntry.rows.map((row) => row.groupKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((groupKey) => {
      const localRow = conflict.localEntry.rows.find((row) => row.groupKey === groupKey) ?? null;
      const remoteRow = conflict.remoteEntry.rows.find((row) => row.groupKey === groupKey) ?? null;
      if (serializeComparablePredicateRefReplayApplyHistoryRow(localRow) === serializeComparablePredicateRefReplayApplyHistoryRow(remoteRow)) {
        return [];
      }
      return [{
        decisionKey: `row:${groupKey}`,
        editable: true,
        key: groupKey,
        label: localRow?.groupLabel ?? remoteRow?.groupLabel ?? groupKey,
        localValue: formatPredicateRefReplayApplyHistoryRowSummary(localRow),
        remoteValue: formatPredicateRefReplayApplyHistoryRowSummary(remoteRow),
        relatedGroupKey: groupKey,
        section: "row",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const selectionSnapshotDiffs = Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((selectionKey) => {
      const localValue = conflict.localEntry.rollbackSnapshot.groupSelectionsBySelectionKey[selectionKey] ?? null;
      const remoteValue = conflict.remoteEntry.rollbackSnapshot.groupSelectionsBySelectionKey[selectionKey] ?? null;
      if (localValue === remoteValue) {
        return [];
      }
      const relatedGroupKey = selectionKey.split(":").filter(Boolean).pop() ?? null;
      return [{
        decisionKey: `selection_snapshot:${selectionKey}`,
        editable: true,
        key: selectionKey,
        label: formatPredicateRefReplayApplyHistorySelectionKeyLabel(selectionKey),
        localValue: formatPredicateRefReplayApplyHistorySnapshotValue(localValue),
        remoteValue: formatPredicateRefReplayApplyHistorySnapshotValue(remoteValue),
        relatedGroupKey,
        section: "selection_snapshot",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const bindingSnapshotDiffs = Array.from(
    new Set([
      ...Object.keys(conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey),
      ...Object.keys(conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey),
    ]),
  )
    .sort((left, right) => left.localeCompare(right))
    .flatMap((parameterKey) => {
      const localValue = conflict.localEntry.rollbackSnapshot.draftBindingsByParameterKey[parameterKey] ?? null;
      const remoteValue = conflict.remoteEntry.rollbackSnapshot.draftBindingsByParameterKey[parameterKey] ?? null;
      if (localValue === remoteValue) {
        return [];
      }
      return [{
        decisionKey: `binding_snapshot:${parameterKey}`,
        editable: true,
        key: parameterKey,
        label: parameterKey,
        localValue: formatPredicateRefReplayApplyHistorySnapshotValue(localValue),
        remoteValue: formatPredicateRefReplayApplyHistorySnapshotValue(remoteValue),
        relatedGroupKey: parameterGroupKeyByParameterKey[parameterKey] ?? null,
        section: "binding_snapshot",
      } satisfies PredicateRefReplayApplyConflictDiffItem];
    });

  const totalDiffCount = summaryDiffs.length
    + rowDiffs.length
    + selectionSnapshotDiffs.length
    + bindingSnapshotDiffs.length;
  return {
    conflict,
    summaryDiffs,
    rowDiffs,
    selectionSnapshotDiffs,
    bindingSnapshotDiffs,
    totalDiffCount,
    localPreview: buildPredicateRefReplayApplyConflictResolutionPreview(
      conflict,
      conflict.localEntry,
      "local",
      `Keeps the currently active entry in this tab and ignores ${totalDiffCount} remote field-level differences.`,
    ),
    remotePreview: buildPredicateRefReplayApplyConflictResolutionPreview(
      conflict,
      conflict.remoteEntry,
      "remote",
      `Replaces the active entry with ${conflict.sourceTabLabel}'s version across ${totalDiffCount} differing fields in this tab.`,
    ),
  };
}

export function normalizePredicateRefReplayApplySyncAuditEntry(value: unknown): PredicateRefReplayApplySyncAuditEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.auditId !== "string"
    || typeof record.at !== "string"
    || typeof record.detail !== "string"
    || typeof record.entryId !== "string"
    || typeof record.kind !== "string"
    || typeof record.sourceTabId !== "string"
    || typeof record.sourceTabLabel !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
  ) {
    return null;
  }
  if (
    ![
      "local_apply",
      "local_restore",
      "remote_apply",
      "remote_restore",
      "conflict_detected",
      "conflict_resolved",
    ].includes(record.kind)
  ) {
    return null;
  }
  return {
    at: record.at,
    auditId: record.auditId,
    detail: record.detail,
    entryId: record.entryId,
    kind: record.kind,
    sourceTabId: record.sourceTabId,
    sourceTabLabel: record.sourceTabLabel,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
  } as PredicateRefReplayApplySyncAuditEntry;
}

export function normalizePredicateRefReplayApplyConflictEntry(value: unknown): PredicateRefReplayApplyConflictEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.conflictId !== "string"
    || typeof record.detectedAt !== "string"
    || typeof record.entryId !== "string"
    || typeof record.sourceTabId !== "string"
    || typeof record.sourceTabLabel !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
  ) {
    return null;
  }
  const localEntry = normalizePredicateRefReplayApplyHistoryEntry(record.localEntry);
  const remoteEntry = normalizePredicateRefReplayApplyHistoryEntry(record.remoteEntry);
  if (!localEntry || !remoteEntry) {
    return null;
  }
  return {
    conflictId: record.conflictId,
    detectedAt: record.detectedAt,
    entryId: record.entryId,
    localEntry,
    remoteEntry,
    sourceTabId: record.sourceTabId,
    sourceTabLabel: record.sourceTabLabel,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
  };
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
  tabId: string,
): PredicateRefReplayApplySyncAuditEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplySyncAuditTrailState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION
      || typeof parsed.tabId !== "string"
      || parsed.tabId !== tabId
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return limitPredicateRefReplayApplySyncAuditEntries(
      parsed.entries
        .map((entry) => normalizePredicateRefReplayApplySyncAuditEntry(entry))
        .filter((entry): entry is PredicateRefReplayApplySyncAuditEntry => entry !== null),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplySyncAuditTrail(
  tabId: string,
  entries: PredicateRefReplayApplySyncAuditEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplySyncAuditTrailState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_VERSION,
      tabId,
      entries: limitPredicateRefReplayApplySyncAuditEntries(entries),
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_SYNC_AUDIT_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
  tabId: string,
): PredicateRefReplayApplyConflictEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.sessionStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<PredicateRefReplayApplyConflictState> | null;
    if (
      !parsed
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION
      || typeof parsed.tabId !== "string"
      || parsed.tabId !== tabId
      || !Array.isArray(parsed.conflicts)
    ) {
      return [];
    }
    return limitPredicateRefReplayApplyConflictEntries(
      parsed.conflicts
        .map((entry) => normalizePredicateRefReplayApplyConflictEntry(entry))
        .filter((entry): entry is PredicateRefReplayApplyConflictEntry => entry !== null),
    );
  } catch {
    return [];
  }
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplyConflicts(
  tabId: string,
  conflicts: PredicateRefReplayApplyConflictEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    const nextState: PredicateRefReplayApplyConflictState = {
      version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_VERSION,
      tabId,
      conflicts: limitPredicateRefReplayApplyConflictEntries(conflicts),
    };
    window.sessionStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_CONFLICTS_SESSION_KEY,
      JSON.stringify(nextState),
    );
  } catch {
    return;
  }
}

export function normalizeReplayApplySnapshotRecord(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).flatMap(([key, entryValue]) =>
      typeof key === "string" && (typeof entryValue === "string" || entryValue === null)
        ? [[key, entryValue] as const]
        : [],
    ),
  );
}

export function normalizePredicateRefReplayApplyHistoryEntry(value: unknown): PredicateRefReplayApplyHistoryEntry | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.id !== "string"
    || typeof record.appliedAt !== "string"
    || typeof record.templateId !== "string"
    || typeof record.templateLabel !== "string"
    || typeof record.approvedCount !== "number"
    || typeof record.changedCurrentCount !== "number"
    || typeof record.matchesSimulationCount !== "number"
    || !Array.isArray(record.rows)
  ) {
    return null;
  }
  const rows = record.rows.flatMap((rowValue) => {
    if (!rowValue || typeof rowValue !== "object" || Array.isArray(rowValue)) {
      return [];
    }
    const rowRecord = rowValue as Record<string, unknown>;
    if (
      typeof rowRecord.groupKey !== "string"
      || typeof rowRecord.groupLabel !== "string"
      || typeof rowRecord.currentBundleLabel !== "string"
      || typeof rowRecord.currentStatus !== "string"
      || typeof rowRecord.simulatedBundleLabel !== "string"
      || typeof rowRecord.simulatedStatus !== "string"
      || typeof rowRecord.promotedBundleKey !== "string"
      || typeof rowRecord.promotedBundleLabel !== "string"
      || typeof rowRecord.matchesSimulation !== "boolean"
      || typeof rowRecord.changesCurrent !== "boolean"
    ) {
      return [];
    }
    return [{
      changesCurrent: rowRecord.changesCurrent,
      currentBundleLabel: rowRecord.currentBundleLabel,
      currentStatus: rowRecord.currentStatus,
      groupKey: rowRecord.groupKey,
      groupLabel: rowRecord.groupLabel,
      matchesSimulation: rowRecord.matchesSimulation,
      promotedBundleKey: rowRecord.promotedBundleKey,
      promotedBundleLabel: rowRecord.promotedBundleLabel,
      simulatedBundleLabel: rowRecord.simulatedBundleLabel,
      simulatedStatus: rowRecord.simulatedStatus,
    } satisfies PredicateRefReplayApplyHistoryRow];
  });
  if (!rows.length) {
    return null;
  }
  const rollbackSnapshot =
    record.rollbackSnapshot && typeof record.rollbackSnapshot === "object" && !Array.isArray(record.rollbackSnapshot)
      ? (record.rollbackSnapshot as Record<string, unknown>)
      : {};
  return {
    appliedAt: record.appliedAt,
    approvedCount: record.approvedCount,
    changedCurrentCount: record.changedCurrentCount,
    id: record.id,
    matchesSimulationCount: record.matchesSimulationCount,
    rollbackSnapshot: {
      draftBindingsByParameterKey: normalizeReplayApplySnapshotRecord(rollbackSnapshot.draftBindingsByParameterKey),
      groupSelectionsBySelectionKey: normalizeReplayApplySnapshotRecord(rollbackSnapshot.groupSelectionsBySelectionKey),
    },
    rows,
    sourceTabId:
      typeof record.sourceTabId === "string" || record.sourceTabId === null
        ? record.sourceTabId
        : null,
    sourceTabLabel:
      typeof record.sourceTabLabel === "string" || record.sourceTabLabel === null
        ? record.sourceTabLabel
        : null,
    templateId: record.templateId,
    templateLabel: record.templateLabel,
    lastRestoredAt:
      typeof record.lastRestoredAt === "string" || record.lastRestoredAt === null
        ? record.lastRestoredAt
        : null,
    lastRestoredByTabId:
      typeof record.lastRestoredByTabId === "string" || record.lastRestoredByTabId === null
        ? record.lastRestoredByTabId
        : null,
    lastRestoredByTabLabel:
      typeof record.lastRestoredByTabLabel === "string" || record.lastRestoredByTabLabel === null
        ? record.lastRestoredByTabLabel
        : null,
  };
}

export function parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue(raw: string | null) {
  if (!raw) {
    return [] as PredicateRefReplayApplyHistoryEntry[];
  }
  try {
    const parsed = JSON.parse(raw);
    if (
      !parsed
      || typeof parsed !== "object"
      || Array.isArray(parsed)
      || parsed.version !== RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION
      || !Array.isArray(parsed.entries)
    ) {
      return [];
    }
    return parsed.entries
      .map((entry: unknown) => normalizePredicateRefReplayApplyHistoryEntry(entry))
      .filter((entry: PredicateRefReplayApplyHistoryEntry | null): entry is PredicateRefReplayApplyHistoryEntry => Boolean(entry))
      .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES);
  } catch {
    return [];
  }
}

export function loadRunSurfaceCollectionQueryBuilderReplayApplyHistory() {
  if (typeof window === "undefined") {
    return [] as PredicateRefReplayApplyHistoryEntry[];
  }
  return parseRunSurfaceCollectionQueryBuilderReplayApplyHistoryValue(
    window.localStorage.getItem(RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY),
  );
}

export function serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(
  entries: PredicateRefReplayApplyHistoryEntry[],
) {
  return JSON.stringify({
    version: RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_VERSION,
    entries: entries.slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES),
  });
}

export function persistRunSurfaceCollectionQueryBuilderReplayApplyHistory(
  entries: PredicateRefReplayApplyHistoryEntry[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_STORAGE_KEY,
      serializeRunSurfaceCollectionQueryBuilderReplayApplyHistory(entries),
    );
  } catch {
    return;
  }
}

export function mergePredicateRefReplayApplyHistoryEntries(
  currentEntries: PredicateRefReplayApplyHistoryEntry[],
  incomingEntries: PredicateRefReplayApplyHistoryEntry[],
) {
  const entryById = new Map(
    currentEntries.map((entry) => [entry.id, entry] as const),
  );
  incomingEntries.forEach((incomingEntry) => {
    const currentEntry = entryById.get(incomingEntry.id);
    if (!currentEntry) {
      entryById.set(incomingEntry.id, incomingEntry);
      return;
    }
    const currentRestoredAt = currentEntry.lastRestoredAt ? Date.parse(currentEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
    const incomingRestoredAt = incomingEntry.lastRestoredAt ? Date.parse(incomingEntry.lastRestoredAt) : Number.NEGATIVE_INFINITY;
    if (incomingRestoredAt > currentRestoredAt) {
      entryById.set(incomingEntry.id, incomingEntry);
      return;
    }
    if (incomingRestoredAt < currentRestoredAt) {
      entryById.set(incomingEntry.id, currentEntry);
      return;
    }
    const currentAppliedAt = Date.parse(currentEntry.appliedAt);
    const incomingAppliedAt = Date.parse(incomingEntry.appliedAt);
    entryById.set(
      incomingEntry.id,
      incomingAppliedAt >= currentAppliedAt ? incomingEntry : currentEntry,
    );
  });
  return Array.from(entryById.values())
    .sort((left, right) => Date.parse(right.appliedAt) - Date.parse(left.appliedAt))
    .slice(0, MAX_RUN_SURFACE_QUERY_BUILDER_REPLAY_HISTORY_ENTRIES);
}

export function isRunSurfaceCollectionQueryBindingReferenceValue(value: string) {
  return value.startsWith("$") && value.length > 1;
}

export function toRunSurfaceCollectionQueryBindingReferenceValue(bindingKey: string) {
  return bindingKey ? `$${bindingKey}` : "";
}

export function fromRunSurfaceCollectionQueryBindingReferenceValue(value: string) {
  return isRunSurfaceCollectionQueryBindingReferenceValue(value) ? value.slice(1) : "";
}

export function mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
  inferredParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  existingParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[] = [],
) {
  const inferredParameterMap = new Map(
    inferredParameters.map((parameter) => [parameter.key, parameter] as const),
  );
  const existingParameterMap = new Map(
    existingParameters.map((parameter) => [parameter.key, parameter] as const),
  );
  const orderedKeys = [
    ...existingParameters
      .map((parameter) => parameter.key)
      .filter((key) => inferredParameterMap.has(key)),
    ...inferredParameters
      .map((parameter) => parameter.key)
      .filter((key) => !existingParameterMap.has(key)),
  ];
  return orderedKeys.flatMap((key) => {
    const parameter = inferredParameterMap.get(key);
    if (!parameter) {
      return [];
    }
    const existing = existingParameterMap.get(key);
    return [
      existing
        ? {
            ...parameter,
            customLabel: existing.customLabel,
            groupName: existing.groupName,
            helpNote: existing.helpNote,
            defaultValue: existing.defaultValue,
            bindingPreset: existing.bindingPreset,
          }
        : parameter,
    ];
  });
}

export function normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(groupName: string) {
  const trimmedGroupName = groupName.trim();
  if (!trimmedGroupName) {
    return "__ungrouped__";
  }
  const normalizedKey = trimmedGroupName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalizedKey || "__ungrouped__";
}

export function mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  existingGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
) {
  const existingGroupMap = new Map(existingGroups.map((group) => [group.key, group] as const));
  const derivedGroups = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState>();
  parameters.forEach((parameter) => {
    const trimmedGroupName = parameter.groupName.trim();
    const groupKey = normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(trimmedGroupName);
    if (derivedGroups.has(groupKey)) {
      return;
    }
    const existingGroup = existingGroupMap.get(groupKey);
    derivedGroups.set(groupKey, {
      key: groupKey,
      label: existingGroup?.label || trimmedGroupName || "Ungrouped parameters",
      helpNote: existingGroup?.helpNote ?? "",
      collapsedByDefault: existingGroup?.collapsedByDefault ?? false,
      visibilityRule: existingGroup?.visibilityRule ?? "always",
      coordinationPolicy: existingGroup?.coordinationPolicy ?? "manual_source_priority",
      presetBundles: existingGroup?.presetBundles ?? [],
    });
  });
  return Array.from(derivedGroups.values());
}

export function groupRunSurfaceCollectionQueryBuilderTemplateParameters(
  parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[],
  groupMetadata: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
) {
  const mergedGroups = mergeRunSurfaceCollectionQueryBuilderTemplateGroups(parameters, groupMetadata);
  const mergedGroupMap = new Map(mergedGroups.map((group) => [group.key, group] as const));
  const groups = new Map<
    string,
    {
      key: string;
      label: string;
      helpNote: string;
      collapsedByDefault: boolean;
      visibilityRule: "always" | "manual" | "binding_active" | "value_active";
      coordinationPolicy: "manual_source_priority" | "highest_source_priority" | "sticky_auto_selection" | "manual_resolution";
      presetBundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[];
      parameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
    }
  >();
  parameters.forEach((parameter) => {
    const normalizedLabel = parameter.groupName.trim();
    const key = normalizeRunSurfaceCollectionQueryBuilderTemplateGroupKey(normalizedLabel);
    const group = mergedGroupMap.get(key);
    const label = group?.label || normalizedLabel || "Ungrouped parameters";
    const existing = groups.get(key);
    if (existing) {
      existing.parameters.push(parameter);
      return;
    }
    groups.set(key, {
      key,
      label,
      helpNote: group?.helpNote ?? "",
      collapsedByDefault: group?.collapsedByDefault ?? false,
      visibilityRule: group?.visibilityRule ?? "always",
      coordinationPolicy: group?.coordinationPolicy ?? "manual_source_priority",
      presetBundles: group?.presetBundles ?? [],
      parameters: [parameter],
    });
  });
  return Array.from(groups.values());
}

export function sortRunSurfaceCollectionQueryBuilderTemplateGroupPresetBundles(
  bundles: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState[],
) {
  return [...bundles].sort((left, right) => {
    if (right.priority !== left.priority) {
      return right.priority - left.priority;
    }
    const labelComparison = left.label.localeCompare(right.label);
    if (labelComparison !== 0) {
      return labelComparison;
    }
    return left.key.localeCompare(right.key);
  });
}

export function formatRunSurfaceCollectionQueryBuilderCoordinationPolicyLabel(
  policy: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"],
) {
  if (policy === "manual_source_priority") {
    return "prefer manual source";
  }
  if (policy === "highest_source_priority") {
    return "highest source priority";
  }
  if (policy === "sticky_auto_selection") {
    return "keep current auto choice";
  }
  return "manual resolution";
}

export function cloneRunSurfaceCollectionQueryBuilderChildState(
  child: RunSurfaceCollectionQueryBuilderChildState,
): RunSurfaceCollectionQueryBuilderChildState {
  if (child.kind === "clause") {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: {
        ...child.clause,
        parameterValues: { ...child.clause.parameterValues },
        parameterBindingKeys: { ...child.clause.parameterBindingKeys },
        valueBindingKey: child.clause.valueBindingKey,
      },
    };
  }
  if (child.kind === "predicate_ref") {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: child.predicateKey,
      bindings: { ...child.bindings },
      negated: child.negated,
    };
  }
  return {
    id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
    kind: "group",
    logic: child.logic,
    negated: child.negated,
    children: child.children.map((nestedChild) => cloneRunSurfaceCollectionQueryBuilderChildState(nestedChild)),
  };
}

export function parseRunSurfaceCollectionQueryBuilderClauseState(
  rawNode: unknown,
  contracts: RunSurfaceCollectionQueryContract[],
): HydratedRunSurfaceCollectionQueryBuilderState | null {
  try {
    if (!rawNode || typeof rawNode !== "object" || Array.isArray(rawNode)) {
      return null;
    }
    const record = rawNode as Record<string, unknown>;
    const collectionRecord =
      record.collection && typeof record.collection === "object" && !Array.isArray(record.collection)
        ? (record.collection as Record<string, unknown>)
        : null;
    const conditionRecords = Array.isArray(record.conditions)
      ? record.conditions.filter(
          (condition): condition is Record<string, unknown> =>
            Boolean(condition) && typeof condition === "object" && !Array.isArray(condition),
        )
      : [];
    const childRecords = Array.isArray(record.children)
      ? record.children.filter((child) => Boolean(child))
      : [];
    if (!collectionRecord || conditionRecords.length !== 1 || childRecords.length) {
      return null;
    }
    const resolvedPath = getCollectionQueryStringArray(collectionRecord.path);
    const rawPathTemplate = getCollectionQueryStringArray(collectionRecord.path_template);
    const rawBindings =
      collectionRecord.bindings && typeof collectionRecord.bindings === "object" && !Array.isArray(collectionRecord.bindings)
        ? (collectionRecord.bindings as Record<string, unknown>)
        : null;
    const quantifier =
      collectionRecord.quantifier === "all"
      || collectionRecord.quantifier === "none"
      || collectionRecord.quantifier === "any"
        ? collectionRecord.quantifier
        : "any";
    const condition = conditionRecords[0];
    const fieldKey = typeof condition.key === "string" ? condition.key : "";
    const operatorKey = typeof condition.operator === "string" ? condition.operator : "";
    if ((!resolvedPath.length && !rawPathTemplate.length) || !fieldKey || !operatorKey) {
      return null;
    }
    for (const contract of contracts) {
      const schemas = getRunSurfaceCollectionQuerySchemas(contract);
      for (const schema of schemas) {
        const parameterValues = rawPathTemplate.length
          ? (
              getCollectionQuerySchemaId(schema) === rawPathTemplate.join(".")
                ? schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
                    const rawBindingValue = rawBindings?.[parameter.key];
                    if (rawBindingValue && typeof rawBindingValue === "object" && !Array.isArray(rawBindingValue)) {
                      return accumulator;
                    }
                    if (typeof rawBindingValue === "string") {
                      accumulator[parameter.key] = rawBindingValue;
                      return accumulator;
                    }
                    const optionValues = parameter.domain?.values.length
                      ? parameter.domain.values
                      : parameter.examples;
                    if (optionValues[0]) {
                      accumulator[parameter.key] = optionValues[0];
                    }
                    return accumulator;
                  }, {})
                : null
            )
          : resolveCollectionQueryTemplateValues(schema.pathTemplate, resolvedPath);
        if (!parameterValues) {
          continue;
        }
        const field = schema.elementSchema.find((candidate) => candidate.key === fieldKey);
        if (!field) {
          continue;
        }
        const operator = field.operators.find((candidate) => candidate.key === operatorKey);
        if (!operator) {
          continue;
        }
        const parameterBindingKeys = schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
          const rawBindingValue = rawBindings?.[parameter.key];
          if (
            rawBindingValue
            && typeof rawBindingValue === "object"
            && !Array.isArray(rawBindingValue)
            && typeof (rawBindingValue as Record<string, unknown>).binding === "string"
          ) {
            accumulator[parameter.key] = (rawBindingValue as Record<string, string>).binding;
          }
          return accumulator;
        }, {});
        const valueBindingKey =
          condition.value
          && typeof condition.value === "object"
          && !Array.isArray(condition.value)
          && typeof (condition.value as Record<string, unknown>).binding === "string"
            ? (condition.value as Record<string, string>).binding
            : "";
        return {
          contractKey: contract.contract_key,
          schemaId: getCollectionQuerySchemaId(schema),
          parameterValues,
          parameterBindingKeys,
          quantifier,
          fieldKey,
          operatorKey,
          builderValue: valueBindingKey ? "" : formatCollectionQueryBuilderValue(condition.value, field.valueType),
          valueBindingKey,
          negated: record.negated === true,
        };
      }
    }
  } catch {
    return null;
  }
  return null;
}

export function buildRunSurfaceCollectionQueryBuilderDefaultClauseState(
  contracts: RunSurfaceCollectionQueryContract[],
  preferredContractKey?: string | null,
): HydratedRunSurfaceCollectionQueryBuilderState | null {
  const activeContract =
    contracts.find((contract) => contract.contract_key === preferredContractKey) ?? contracts[0] ?? null;
  if (!activeContract) {
    return null;
  }
  const schema = getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  if (!schema) {
    return null;
  }
  const parameterValues = schema.parameters.reduce<Record<string, string>>((accumulator, parameter) => {
    const optionValues = parameter.domain?.values.length ? parameter.domain.values : parameter.examples;
    if (optionValues[0]) {
      accumulator[parameter.key] = optionValues[0];
    }
    return accumulator;
  }, {});
  const field = schema.elementSchema[0] ?? null;
  const operator = field?.operators[0] ?? null;
  if (!field || !operator) {
    return null;
  }
  return {
    contractKey: activeContract.contract_key,
    schemaId: getCollectionQuerySchemaId(schema),
    parameterValues,
    parameterBindingKeys: {},
    quantifier: "any",
    fieldKey: field.key,
    operatorKey: operator.key,
    builderValue: "",
    valueBindingKey: "",
    negated: false,
  };
}

export function buildRunSurfaceCollectionQueryBuilderNodeFromClause(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  if (!activeContract || !activeSchema) {
    return null;
  }
  const field =
    activeSchema.elementSchema.find((candidate) => candidate.key === clause.fieldKey)
    ?? activeSchema.elementSchema[0]
    ?? null;
  const operator =
    field?.operators.find((candidate) => candidate.key === clause.operatorKey)
    ?? field?.operators[0]
    ?? null;
  if (!field || !operator) {
    return null;
  }
  const hasTemplateBindings = Object.values(clause.parameterBindingKeys).some(Boolean);
  const collectionNode = hasTemplateBindings
    ? {
        path_template: activeSchema.pathTemplate,
        bindings: activeSchema.parameters.reduce<Record<string, unknown>>((accumulator, parameter) => {
          const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim();
          if (bindingKey) {
            accumulator[parameter.key] = { binding: bindingKey };
            return accumulator;
          }
          const literalValue = clause.parameterValues[parameter.key];
          if (literalValue) {
            accumulator[parameter.key] = literalValue;
          }
          return accumulator;
        }, {}),
        quantifier: clause.quantifier,
      }
    : {
        path: resolveCollectionQueryPath(activeSchema.pathTemplate, clause.parameterValues),
        quantifier: clause.quantifier,
      };
  return {
    ...(clause.negated ? { negated: true } : {}),
    collection: collectionNode,
    conditions: [
      {
        key: field.key,
        operator: operator.key,
        value: clause.valueBindingKey
          ? { binding: clause.valueBindingKey }
          : coerceCollectionQueryBuilderValue(clause.builderValue, field.valueType),
      },
    ],
  };
}

export function formatRunSurfaceCollectionQueryBuilderClauseSummary(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  const field = activeSchema?.elementSchema.find((candidate) => candidate.key === clause.fieldKey) ?? null;
  const operator = field?.operators.find((candidate) => candidate.key === clause.operatorKey) ?? null;
  const path = activeSchema
    ? (
        Object.values(clause.parameterBindingKeys).some(Boolean)
          ? `${activeSchema.pathTemplate.join(".")} (bound)`
          : resolveCollectionQueryPath(activeSchema.pathTemplate, clause.parameterValues).join(".")
      )
    : clause.schemaId;
  const qualifier = clause.negated ? "not " : "";
  const valueSuffix = clause.valueBindingKey ? ` · value via $${clause.valueBindingKey}` : "";
  return `${qualifier}${clause.quantifier} ${field?.title ?? field?.key ?? clause.fieldKey} ${operator?.label ?? operator?.key ?? clause.operatorKey} @ ${path}${valueSuffix}`;
}

export function areRunSurfaceCollectionQueryBuilderRecordValuesEqual(
  left: Record<string, string>,
  right: Record<string, string>,
) {
  const leftEntries = Object.entries(left).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
  const rightEntries = Object.entries(right).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
  if (leftEntries.length !== rightEntries.length) {
    return false;
  }
  return leftEntries.every(([leftKey, leftValue], index) => {
    const [rightKey, rightValue] = rightEntries[index] ?? [];
    return leftKey === rightKey && leftValue === rightValue;
  });
}

export function areHydratedRunSurfaceCollectionQueryBuilderStatesEqual(
  left: HydratedRunSurfaceCollectionQueryBuilderState | null,
  right: HydratedRunSurfaceCollectionQueryBuilderState | null,
) {
  if (!left || !right) {
    return false;
  }
  return (
    left.contractKey === right.contractKey
    && left.schemaId === right.schemaId
    && left.quantifier === right.quantifier
    && left.fieldKey === right.fieldKey
    && left.operatorKey === right.operatorKey
    && left.builderValue === right.builderValue
    && left.valueBindingKey === right.valueBindingKey
    && left.negated === right.negated
    && areRunSurfaceCollectionQueryBuilderRecordValuesEqual(left.parameterValues, right.parameterValues)
    && areRunSurfaceCollectionQueryBuilderRecordValuesEqual(left.parameterBindingKeys, right.parameterBindingKeys)
  );
}

export function doesRunSurfaceCollectionQueryRuntimeCandidateSampleMatchContext(
  sample: RunSurfaceCollectionQueryRuntimeCandidateSample,
  selection: RunSurfaceCollectionQueryRuntimeCandidateContextSelection | null,
) {
  if (!selection || sample.runId !== selection.runId) {
    return false;
  }
  if (selection.artifactHoverKey) {
    return sample.runContextArtifactHoverKeys.includes(selection.artifactHoverKey);
  }
  if (selection.subFocusKey) {
    return sample.runContextSubFocusKey === selection.subFocusKey;
  }
  if (selection.componentKey) {
    return (
      sample.runContextComponentKey === selection.componentKey
      && sample.runContextSection === selection.section
    );
  }
  return false;
}

export function isSameRunSurfaceCollectionQueryRuntimeCandidateSelectionSurface(
  left: Pick<
    RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
    "componentKey" | "runId" | "section" | "subFocusKey"
  > | null,
  right: Pick<
    RunSurfaceCollectionQueryRuntimeCandidateContextSelection,
    "componentKey" | "runId" | "section" | "subFocusKey"
  > | null,
) {
  if (!left || !right) {
    return false;
  }
  return (
    left.runId === right.runId
    && left.section === right.section
    && left.componentKey === right.componentKey
    && left.subFocusKey === right.subFocusKey
  );
}

export function formatRunSurfaceCollectionQueryBuilderClauseParameterSource(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  parameterKey: string,
) {
  const bindingKey = clause.parameterBindingKeys[parameterKey]?.trim() ?? "";
  if (bindingKey) {
    return `$${bindingKey}`;
  }
  return clause.parameterValues[parameterKey] || "(blank)";
}

export function formatRunSurfaceCollectionQueryBuilderClauseValueSource(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
) {
  return clause.valueBindingKey.trim()
    ? `$${clause.valueBindingKey.trim()}`
    : (clause.builderValue || "(blank)");
}

export function buildRunSurfaceCollectionQueryBuilderClauseDiffItems(
  original: HydratedRunSurfaceCollectionQueryBuilderState | null,
  draft: HydratedRunSurfaceCollectionQueryBuilderState | null,
): RunSurfaceCollectionQueryBuilderClauseDiffItem[] {
  if (!original || !draft) {
    return [];
  }
  const items: RunSurfaceCollectionQueryBuilderClauseDiffItem[] = [];
  if (original.contractKey !== draft.contractKey) {
    items.push({
      detail: `${original.contractKey} -> ${draft.contractKey}`,
      key: "contract",
      label: "Contract",
    });
  }
  if (original.schemaId !== draft.schemaId) {
    items.push({
      detail: `${original.schemaId} -> ${draft.schemaId}`,
      key: "schema",
      label: "Collection",
    });
  }
  if (original.quantifier !== draft.quantifier) {
    items.push({
      detail: `${original.quantifier.toUpperCase()} -> ${draft.quantifier.toUpperCase()}`,
      key: "quantifier",
      label: "Quantifier",
    });
  }
  if (original.fieldKey !== draft.fieldKey) {
    items.push({
      detail: `${original.fieldKey} -> ${draft.fieldKey}`,
      key: "field",
      label: "Field",
    });
  }
  if (original.operatorKey !== draft.operatorKey) {
    items.push({
      detail: `${original.operatorKey} -> ${draft.operatorKey}`,
      key: "operator",
      label: "Operator",
    });
  }
  if (original.negated !== draft.negated) {
    items.push({
      detail: `${original.negated ? "negated" : "plain"} -> ${draft.negated ? "negated" : "plain"}`,
      key: "negated",
      label: "Negation",
    });
  }
  const originalValue = formatRunSurfaceCollectionQueryBuilderClauseValueSource(original);
  const draftValue = formatRunSurfaceCollectionQueryBuilderClauseValueSource(draft);
  if (originalValue !== draftValue) {
    items.push({
      detail: `${originalValue} -> ${draftValue}`,
      key: "value",
      label: "Value",
    });
  }
  const parameterKeys = Array.from(
    new Set([
      ...Object.keys(original.parameterValues),
      ...Object.keys(draft.parameterValues),
      ...Object.keys(original.parameterBindingKeys),
      ...Object.keys(draft.parameterBindingKeys),
    ]),
  ).sort((left, right) => left.localeCompare(right));
  parameterKeys.forEach((parameterKey) => {
    const originalSource = formatRunSurfaceCollectionQueryBuilderClauseParameterSource(original, parameterKey);
    const draftSource = formatRunSurfaceCollectionQueryBuilderClauseParameterSource(draft, parameterKey);
    if (originalSource === draftSource) {
      return;
    }
    items.push({
      detail: `${originalSource} -> ${draftSource}`,
      key: `parameter:${parameterKey}`,
      label: `Path ${parameterKey}`,
    });
  });
  return items;
}

export function formatRunSurfaceCollectionQueryBuilderChildSummary(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  if (child.kind === "clause") {
    return formatRunSurfaceCollectionQueryBuilderClauseSummary(child.clause, contracts);
  }
  if (child.kind === "predicate_ref") {
    const bindingSummary = Object.keys(child.bindings).length
      ? ` · ${Object.entries(child.bindings)
          .map(([key, value]) => `${key}=${value}`)
          .join(", ")}`
      : "";
    return `${child.negated ? "not " : ""}predicate ${child.predicateKey}${bindingSummary}`;
  }
  const counts = countRunSurfaceCollectionQueryBuilderChildren(child.children);
  return `${child.negated ? "not " : ""}${child.logic.toUpperCase()} subgroup · ${counts.clauses} clause${counts.clauses === 1 ? "" : "s"} · ${counts.predicateRefs} predicate ref${counts.predicateRefs === 1 ? "" : "s"} · ${counts.groups} nested group${counts.groups === 1 ? "" : "s"}`;
}

export function parseRunSurfaceCollectionQueryBuilderChildState(
  rawNode: unknown,
  contracts: RunSurfaceCollectionQueryContract[],
): RunSurfaceCollectionQueryBuilderChildState | null {
  if (!rawNode || typeof rawNode !== "object" || Array.isArray(rawNode)) {
    return null;
  }
  const childRecord = rawNode as Record<string, unknown>;
  if (typeof childRecord.predicate_ref === "string" && childRecord.predicate_ref) {
    const rawBindings =
      childRecord.bindings && typeof childRecord.bindings === "object" && !Array.isArray(childRecord.bindings)
        ? (childRecord.bindings as Record<string, unknown>)
        : null;
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: childRecord.predicate_ref,
      bindings: rawBindings
        ? Object.fromEntries(
            Object.entries(rawBindings).flatMap(([key, value]) => {
              if (typeof value === "string") {
                return [[key, value]];
              }
              if (
                value
                && typeof value === "object"
                && !Array.isArray(value)
                && typeof (value as Record<string, unknown>).binding === "string"
              ) {
                return [[key, toRunSurfaceCollectionQueryBindingReferenceValue((value as Record<string, string>).binding)]];
              }
              return [];
            }),
          )
        : {},
      negated: childRecord.negated === true,
    };
  }
  const clause = parseRunSurfaceCollectionQueryBuilderClauseState(childRecord, contracts);
  if (clause) {
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause,
    };
  }
  const rawChildren = Array.isArray(childRecord.children) ? childRecord.children : [];
  const children = rawChildren.reduce<RunSurfaceCollectionQueryBuilderChildState[]>(
    (accumulator, rawChild) => {
      const parsedChild = parseRunSurfaceCollectionQueryBuilderChildState(rawChild, contracts);
      if (parsedChild) {
        accumulator.push(parsedChild);
      }
      return accumulator;
    },
    [],
  );
  if (!children.length) {
    return null;
  }
  return {
    id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
    kind: "group",
    logic: childRecord.logic === "or" || childRecord.logic === "and" ? childRecord.logic : "and",
    negated: childRecord.negated === true,
    children,
  };
}

export function buildRunSurfaceCollectionQueryBuilderNodeFromChild(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
  expressionAuthoring: RunSurfaceCollectionQueryExpressionAuthoring,
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[],
): Record<string, unknown> | null {
  if (child.kind === "predicate_ref") {
    const node: Record<string, unknown> = child.negated
      ? { [expressionAuthoring.predicateRefs.referenceField]: child.predicateKey, negated: true }
      : { [expressionAuthoring.predicateRefs.referenceField]: child.predicateKey };
    const referencedTemplate = predicateTemplates.find((template) => template.key === child.predicateKey) ?? null;
    if (referencedTemplate && Object.keys(child.bindings).length) {
      node[expressionAuthoring.predicateTemplates.bindingsField] = Object.fromEntries(
        referencedTemplate.parameters.flatMap((parameter) => {
          const value = child.bindings[parameter.key];
          if (!value) {
            return [];
          }
          return [[
            parameter.key,
            isRunSurfaceCollectionQueryBindingReferenceValue(value)
              ? { [expressionAuthoring.predicateTemplates.bindingReferenceField]: fromRunSurfaceCollectionQueryBindingReferenceValue(value) }
              : coerceCollectionQueryBuilderValue(value, parameter.valueType),
          ]];
        }),
      );
    }
    return node;
  }
  if (child.kind === "clause") {
    return buildRunSurfaceCollectionQueryBuilderNodeFromClause(child.clause, contracts);
  }
  const childNodes = child.children.reduce<Record<string, unknown>[]>((accumulator, nestedChild) => {
    const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
      nestedChild,
      contracts,
      expressionAuthoring,
      predicateTemplates,
    );
    if (node) {
      accumulator.push(node);
    }
    return accumulator;
  }, []);
  if (!childNodes.length) {
    return null;
  }
  return {
    ...(child.negated ? { negated: true } : {}),
    logic: child.logic,
    children: childNodes,
  };
}

export function countRunSurfaceCollectionQueryBuilderChildren(children: RunSurfaceCollectionQueryBuilderChildState[]) {
  return children.reduce(
    (accumulator, child) => {
      if (child.kind === "clause") {
        accumulator.clauses += 1;
        return accumulator;
      }
      if (child.kind === "predicate_ref") {
        accumulator.predicateRefs += 1;
        return accumulator;
      }
      accumulator.groups += 1;
      const nestedCounts = countRunSurfaceCollectionQueryBuilderChildren(child.children);
      accumulator.clauses += nestedCounts.clauses;
      accumulator.predicateRefs += nestedCounts.predicateRefs;
      accumulator.groups += nestedCounts.groups;
      return accumulator;
    },
    { clauses: 0, predicateRefs: 0, groups: 0 },
  );
}

export function findRunSurfaceCollectionQueryBuilderGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
): RunSurfaceCollectionQueryBuilderGroupState | null {
  for (const child of children) {
    if (child.kind !== "group") {
      continue;
    }
    if (child.id === groupId) {
      return child;
    }
    const nested = findRunSurfaceCollectionQueryBuilderGroup(child.children, groupId);
    if (nested) {
      return nested;
    }
  }
  return null;
}

export function addRunSurfaceCollectionQueryBuilderChildToGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
  childToAdd: RunSurfaceCollectionQueryBuilderChildState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind !== "group") {
      return child;
    }
    if (child.id === groupId) {
      return {
        ...child,
        children: [...child.children, childToAdd],
      };
    }
    return {
      ...child,
      children: addRunSurfaceCollectionQueryBuilderChildToGroup(child.children, groupId, childToAdd),
    };
  });
}

export function updateRunSurfaceCollectionQueryBuilderGroup(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  groupId: string,
  updater: (group: RunSurfaceCollectionQueryBuilderGroupState) => RunSurfaceCollectionQueryBuilderGroupState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind !== "group") {
      return child;
    }
    if (child.id === groupId) {
      return updater(child);
    }
    return {
      ...child,
      children: updateRunSurfaceCollectionQueryBuilderGroup(child.children, groupId, updater),
    };
  });
}

export function updateRunSurfaceCollectionQueryBuilderClause(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  childId: string,
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind === "clause" && child.id === childId) {
      return {
        ...child,
        clause,
      };
    }
    if (child.kind === "group") {
      return {
        ...child,
        children: updateRunSurfaceCollectionQueryBuilderClause(child.children, childId, clause),
      };
    }
    return child;
  });
}

export function removeRunSurfaceCollectionQueryBuilderChild(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  childId: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.reduce<RunSurfaceCollectionQueryBuilderChildState[]>((accumulator, child) => {
    if (child.id === childId) {
      return accumulator;
    }
    if (child.kind === "group") {
      accumulator.push({
        ...child,
        children: removeRunSurfaceCollectionQueryBuilderChild(child.children, childId),
      });
      return accumulator;
    }
    accumulator.push(child);
    return accumulator;
  }, []);
}

export function replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  previousKey: string,
  nextKey: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.map((child) => {
    if (child.kind === "predicate_ref") {
      return child.predicateKey === previousKey
        ? {
            ...child,
            predicateKey: nextKey,
          }
        : child;
    }
    if (child.kind === "group") {
      return {
        ...child,
        children: replaceRunSurfaceCollectionQueryBuilderPredicateRefs(child.children, previousKey, nextKey),
      };
    }
    return child;
  });
}

export function removeRunSurfaceCollectionQueryBuilderPredicateRefs(
  children: RunSurfaceCollectionQueryBuilderChildState[],
  predicateKey: string,
): RunSurfaceCollectionQueryBuilderChildState[] {
  return children.reduce<RunSurfaceCollectionQueryBuilderChildState[]>((accumulator, child) => {
    if (child.kind === "predicate_ref") {
      if (child.predicateKey !== predicateKey) {
        accumulator.push(child);
      }
      return accumulator;
    }
    if (child.kind === "group") {
      accumulator.push({
        ...child,
        children: removeRunSurfaceCollectionQueryBuilderPredicateRefs(child.children, predicateKey),
      });
      return accumulator;
    }
    accumulator.push(child);
    return accumulator;
  }, []);
}

export function collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause(
  clause: HydratedRunSurfaceCollectionQueryBuilderState,
  contracts: RunSurfaceCollectionQueryContract[],
) {
  const activeContract =
    contracts.find((contract) => contract.contract_key === clause.contractKey) ?? contracts[0] ?? null;
  const activeSchema =
    getRunSurfaceCollectionQuerySchemas(activeContract).find(
      (schema) => getCollectionQuerySchemaId(schema) === clause.schemaId,
    ) ?? getRunSurfaceCollectionQuerySchemas(activeContract)[0] ?? null;
  const activeField =
    activeSchema?.elementSchema.find((field) => field.key === clause.fieldKey)
    ?? activeSchema?.elementSchema[0]
    ?? null;
  const parameterMap = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState>();
  activeSchema?.parameters.forEach((parameter) => {
    const bindingKey = clause.parameterBindingKeys[parameter.key]?.trim();
    if (!bindingKey) {
      return;
    }
    parameterMap.set(bindingKey, {
      key: bindingKey,
      label: `${parameter.key} path binding`,
      customLabel: "",
      groupName: "",
      helpNote: "",
      valueType: "string",
      description: parameter.description || `Collection path binding for ${activeSchema.label}.`,
      options: parameter.domain?.values.length ? parameter.domain.values : parameter.examples,
      defaultValue: "",
      bindingPreset: "",
    });
  });
  if (clause.valueBindingKey.trim()) {
    parameterMap.set(clause.valueBindingKey.trim(), {
      key: clause.valueBindingKey.trim(),
      label: `${activeField?.title ?? activeField?.key ?? clause.fieldKey} value binding`,
      customLabel: "",
      groupName: "",
      helpNote: "",
      valueType: activeField?.valueType ?? "string",
      description: activeField?.description ?? "Bound condition value.",
      options: [],
      defaultValue: "",
      bindingPreset: "",
    });
  }
  return parameterMap;
}

export function collectRunSurfaceCollectionQueryBuilderTemplateParameters(
  child: RunSurfaceCollectionQueryBuilderChildState,
  contracts: RunSurfaceCollectionQueryContract[],
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[] = [],
) {
  const parameterMap = new Map<string, RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState>();
  const collect = (node: RunSurfaceCollectionQueryBuilderChildState) => {
    if (node.kind === "clause") {
      collectRunSurfaceCollectionQueryBuilderTemplateParametersFromClause(node.clause, contracts).forEach(
        (parameter, key) => {
          if (!parameterMap.has(key)) {
            parameterMap.set(key, parameter);
          }
        },
      );
      return;
    }
    if (node.kind === "predicate_ref") {
      const referencedTemplate =
        predicateTemplates.find((template) => template.key === node.predicateKey) ?? null;
      Object.entries(node.bindings).forEach(([parameterKey, rawValue]) => {
        const bindingKey = fromRunSurfaceCollectionQueryBindingReferenceValue(rawValue);
        if (!bindingKey || parameterMap.has(bindingKey)) {
          return;
        }
        const referencedParameter =
          referencedTemplate?.parameters.find((parameter) => parameter.key === parameterKey) ?? null;
        parameterMap.set(bindingKey, {
          key: bindingKey,
          label: referencedParameter?.label ?? `${parameterKey} nested binding`,
          customLabel: "",
          groupName: referencedParameter?.groupName ?? "",
          helpNote: referencedParameter?.helpNote ?? "",
          valueType: referencedParameter?.valueType ?? "string",
          description:
            referencedParameter?.description
            ?? `Nested template binding from ${node.predicateKey}.${parameterKey}.`,
          options: referencedParameter?.options ?? [],
          defaultValue: "",
          bindingPreset: "",
        });
      });
      return;
    }
    if (node.kind === "group") {
      node.children.forEach((nestedChild) => collect(nestedChild));
    }
  };
  collect(child);
  return Array.from(parameterMap.values());
}

export function parseRunSurfaceCollectionQueryBuilderExpressionState(
  rawExpression: string | null | undefined,
  contracts: RunSurfaceCollectionQueryContract[],
): HydratedRunSurfaceCollectionQueryBuilderExpressionState | null {
  const trimmedExpression = rawExpression?.trim();
  if (!trimmedExpression) {
    return null;
  }
  try {
    const parsed = JSON.parse(trimmedExpression) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return null;
    }
    const record = parsed as Record<string, unknown>;
    const predicateRegistry =
      typeof record.predicates === "object" && record.predicates !== null && !Array.isArray(record.predicates)
        ? (record.predicates as Record<string, unknown>)
        : {};
    const predicateTemplateRegistry =
      typeof record.predicate_templates === "object" && record.predicate_templates !== null && !Array.isArray(record.predicate_templates)
        ? (record.predicate_templates as Record<string, unknown>)
        : {};
    const rootNode =
      "root" in record
        ? record.root
        : parsed;
    const singleClause = parseRunSurfaceCollectionQueryBuilderClauseState(rootNode, contracts);
    const predicates = Object.entries(predicateRegistry).flatMap(([predicateKey, node]) => {
      const predicateNode = parseRunSurfaceCollectionQueryBuilderChildState(node, contracts);
      if (!predicateNode) {
        return [];
      }
      return [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
          key: predicateKey,
          node: predicateNode,
        } satisfies RunSurfaceCollectionQueryBuilderPredicateState,
      ];
    });
    const predicateTemplates = Object.entries(predicateTemplateRegistry).flatMap(([templateKey, rawTemplate]) => {
      if (!rawTemplate || typeof rawTemplate !== "object" || Array.isArray(rawTemplate)) {
        return [];
      }
      const templateRecord = rawTemplate as Record<string, unknown>;
      const templateNode = parseRunSurfaceCollectionQueryBuilderChildState(templateRecord.template, contracts);
      if (!templateNode) {
        return [];
      }
      const rawParameters = templateRecord.parameters;
      const parameterKeys = Array.isArray(rawParameters)
        ? rawParameters.filter((parameter): parameter is string => typeof parameter === "string" && Boolean(parameter))
        : (
            rawParameters && typeof rawParameters === "object" && !Array.isArray(rawParameters)
              ? Object.keys(rawParameters)
              : []
          );
      const inferredParameters = collectRunSurfaceCollectionQueryBuilderTemplateParameters(templateNode, contracts);
      const inferredParameterMap = new Map(
        inferredParameters.map((parameter) => [parameter.key, parameter] as const),
      );
      const parsedParameters = parameterKeys.map((parameterKey) => {
        const inferredParameter = inferredParameterMap.get(parameterKey);
        const rawParameter =
          rawParameters && typeof rawParameters === "object" && !Array.isArray(rawParameters)
            ? (rawParameters as Record<string, unknown>)[parameterKey]
            : null;
        const rawDefault =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
            ? (rawParameter as Record<string, unknown>).default
            : undefined;
        const rawCustomLabel =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).label === "string"
            ? ((rawParameter as Record<string, string>).label)
            : "";
        const rawBindingPreset =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).binding_preset === "string"
            ? ((rawParameter as Record<string, string>).binding_preset)
            : "";
        const rawGroupName =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).group === "string"
            ? ((rawParameter as Record<string, string>).group)
            : "";
        const rawHelpNote =
          rawParameter && typeof rawParameter === "object" && !Array.isArray(rawParameter)
          && typeof (rawParameter as Record<string, unknown>).help_note === "string"
            ? ((rawParameter as Record<string, string>).help_note)
            : "";
        const valueType = inferredParameter?.valueType ?? "string";
        return inferredParameter
          ? {
              ...inferredParameter,
              customLabel: rawCustomLabel || inferredParameter.customLabel,
              groupName: rawGroupName || inferredParameter.groupName,
              helpNote: rawHelpNote || inferredParameter.helpNote,
              defaultValue:
                rawDefault === undefined
                  ? inferredParameter.defaultValue
                  : formatCollectionQueryBuilderValue(rawDefault, valueType),
              bindingPreset: rawBindingPreset || inferredParameter.bindingPreset,
            }
          : {
              key: parameterKey,
              label: parameterKey,
              customLabel: rawCustomLabel,
              groupName: rawGroupName,
              helpNote: rawHelpNote,
              valueType,
              description: null,
              options: [],
              defaultValue:
                rawDefault === undefined
                  ? ""
                  : formatCollectionQueryBuilderValue(rawDefault, valueType),
              bindingPreset: rawBindingPreset,
            };
      });
      const rawParameterGroups = templateRecord.parameter_groups;
      const parsedParameterGroups = (
        rawParameterGroups && typeof rawParameterGroups === "object" && !Array.isArray(rawParameterGroups)
          ? Object.entries(rawParameterGroups)
          : []
      ).flatMap(([groupKey, rawGroup]) => {
        if (!rawGroup || typeof rawGroup !== "object" || Array.isArray(rawGroup)) {
          return [];
        }
        const groupRecord = rawGroup as Record<string, unknown>;
        const rawPresetBundles =
          groupRecord.preset_bundles && typeof groupRecord.preset_bundles === "object" && !Array.isArray(groupRecord.preset_bundles)
            ? Object.entries(groupRecord.preset_bundles as Record<string, unknown>)
            : [];
        return [{
          key: groupKey,
          label:
            typeof groupRecord.label === "string" && groupRecord.label.trim()
              ? groupRecord.label.trim()
              : (groupKey === "__ungrouped__" ? "Ungrouped parameters" : groupKey),
          helpNote:
            typeof groupRecord.help_note === "string"
              ? groupRecord.help_note
              : "",
          collapsedByDefault: Boolean(groupRecord.collapsed),
          visibilityRule:
            groupRecord.visibility_rule === "manual"
            || groupRecord.visibility_rule === "binding_active"
            || groupRecord.visibility_rule === "value_active"
              ? groupRecord.visibility_rule
              : "always",
          coordinationPolicy:
            groupRecord.coordination_policy === "highest_source_priority"
            || groupRecord.coordination_policy === "sticky_auto_selection"
            || groupRecord.coordination_policy === "manual_resolution"
              ? groupRecord.coordination_policy
              : "manual_source_priority",
          presetBundles: rawPresetBundles.flatMap(([bundleKey, rawBundle]) => {
            if (!rawBundle || typeof rawBundle !== "object" || Array.isArray(rawBundle)) {
              return [];
            }
            const bundleRecord = rawBundle as Record<string, unknown>;
            const rawValues =
              bundleRecord.values && typeof bundleRecord.values === "object" && !Array.isArray(bundleRecord.values)
                ? (bundleRecord.values as Record<string, unknown>)
                : {};
            const rawBindings =
              bundleRecord.binding_presets && typeof bundleRecord.binding_presets === "object" && !Array.isArray(bundleRecord.binding_presets)
                ? (bundleRecord.binding_presets as Record<string, unknown>)
                : {};
            const rawDependencies =
              bundleRecord.depends_on && typeof bundleRecord.depends_on === "object" && !Array.isArray(bundleRecord.depends_on)
                ? Object.entries(bundleRecord.depends_on as Record<string, unknown>)
                : [];
            return [{
              key: bundleKey,
              label:
                typeof bundleRecord.label === "string" && bundleRecord.label.trim()
                  ? bundleRecord.label.trim()
                  : bundleKey,
              helpNote:
                typeof bundleRecord.help_note === "string"
                  ? bundleRecord.help_note
                  : "",
              priority:
                typeof bundleRecord.priority === "number" && Number.isFinite(bundleRecord.priority)
                  ? bundleRecord.priority
                  : 0,
              autoSelectRule:
                bundleRecord.auto_select_rule === "always"
                || bundleRecord.auto_select_rule === "binding_active"
                || bundleRecord.auto_select_rule === "value_active"
                  ? bundleRecord.auto_select_rule
                  : "manual",
              dependencies: rawDependencies.flatMap(([dependencyKey, rawDependency]) => {
                if (!rawDependency || typeof rawDependency !== "object" || Array.isArray(rawDependency)) {
                  return [];
                }
                const dependencyRecord = rawDependency as Record<string, unknown>;
                const groupKey =
                  typeof dependencyRecord.group_key === "string"
                    ? dependencyRecord.group_key.trim()
                    : "";
                const targetBundleKey =
                  typeof dependencyRecord.bundle_key === "string"
                    ? dependencyRecord.bundle_key.trim()
                    : "";
                if (!groupKey || !targetBundleKey) {
                  return [];
                }
                return [{
                  key: dependencyKey,
                  groupKey,
                  bundleKey: targetBundleKey,
                } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleDependencyState];
              }),
              parameterValues: Object.fromEntries(
                Object.entries(rawValues).flatMap(([parameterKey, rawValue]) =>
                  rawValue === undefined || rawValue === null
                    ? []
                    : [[parameterKey, formatCollectionQueryBuilderValue(rawValue, "string")]],
                ),
              ),
              parameterBindingPresets: Object.fromEntries(
                Object.entries(rawBindings).flatMap(([parameterKey, rawValue]) =>
                  typeof rawValue === "string" && rawValue.trim()
                    ? [[parameterKey, rawValue.trim()]]
                    : [],
                ),
              ),
            } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupPresetBundleState];
          }),
        } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState];
      });
      return [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("template"),
          key: templateKey,
          parameters: parsedParameters,
          parameterGroups: mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
            parsedParameters,
            parsedParameterGroups,
          ),
          node: templateNode,
        } satisfies RunSurfaceCollectionQueryBuilderPredicateTemplateState,
      ];
    });
    if (singleClause && !predicates.length && !predicateTemplates.length) {
      return {
        mode: "single",
        draftClause: singleClause,
        groupLogic: "and",
        rootNegated: false,
        expressionChildren: [],
        predicates: [],
        predicateTemplates: [],
      };
    }
    if (!rootNode || typeof rootNode !== "object" || Array.isArray(rootNode)) {
      return null;
    }
    const rootRecord = rootNode as Record<string, unknown>;
    const childNodes = Array.isArray(rootRecord.children) ? rootRecord.children : [];
    let expressionChildren = childNodes.reduce<RunSurfaceCollectionQueryBuilderChildState[]>(
      (accumulator, rawChild) => {
        const parsedChild = parseRunSurfaceCollectionQueryBuilderChildState(rawChild, contracts);
        if (parsedChild) {
          accumulator.push(parsedChild);
        }
        return accumulator;
      },
      [],
    );
    const rootLogic =
      rootRecord.logic === "or" || rootRecord.logic === "and"
        ? rootRecord.logic
        : "and";
    if (!expressionChildren.length && singleClause) {
      expressionChildren = [
        {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
          kind: "clause",
          clause: singleClause,
        },
      ];
    }
    if (!expressionChildren.length) {
      return null;
    }
    const firstClause = expressionChildren.find(
      (child): child is RunSurfaceCollectionQueryBuilderClauseState => child.kind === "clause",
    );
    return {
      mode: "grouped",
      draftClause: firstClause?.clause ?? buildRunSurfaceCollectionQueryBuilderDefaultClauseState(contracts),
      groupLogic: rootLogic,
      rootNegated: rootRecord.negated === true,
      expressionChildren,
      predicates,
      predicateTemplates,
    };
  } catch {
    return null;
  }
}

export type RunSurfaceCollectionQueryBuilderApplyPayload = {
  expression: string;
  expressionLabel: string;
  resolvedPath: string[];
  quantifier: "any" | "all" | "none";
  fieldKey: string;
  operatorKey: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidateSample = {
  candidatePath: string;
  candidateReplayId: string | null;
  candidateValue: string;
  detail: string;
  result: boolean;
  runId: string;
  runContextArtifactHoverKeys: string[];
  runContextComponentKey: string | null;
  runContextLabel: string | null;
  runContextSection: ComparisonScoreSection | null;
  runContextSubFocusKey: string | null;
};

export type RunSurfaceCollectionQueryRuntimeCandidateContextSelection = {
  artifactHoverKey: string | null;
  componentKey: string | null;
  runId: string;
  section: ComparisonScoreSection | null;
  subFocusKey: string | null;
};

export type RunSurfaceCollectionQueryRuntimeCandidateArtifactSelection = {
  artifactHoverKey: string;
  componentKey: string | null;
  runId: string;
  sampleKeys: string[];
  section: ComparisonScoreSection | null;
  subFocusKey: string | null;
};

export type RunSurfaceCollectionQueryBuilderClauseDiffItem = {
  detail: string;
  key: string;
  label: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidatePreviewDiffItem = {
  detail: string;
  key: string;
  runId: string;
};

export type RunSurfaceCollectionQueryRuntimeQuantifierOutcome = {
  candidateCount: number;
  detail: string;
  matchedCount: number;
  result: boolean;
  runId: string;
};

export type RunSurfaceCollectionQueryRuntimeCandidateTrace = {
  allValues: RunSurfaceCollectionQueryRuntimeCandidateSample[];
  bindingContextByKey?: Record<string, string> | null;
  candidateAccessor: string;
  candidatePath: string;
  comparedValue: string;
  detail: string;
  editorClause: HydratedRunSurfaceCollectionQueryBuilderState | null;
  location: string;
  quantifier: "any" | "all" | "none";
  result: boolean;
  runOutcomes: RunSurfaceCollectionQueryRuntimeQuantifierOutcome[];
  sampleMatchCount: number;
  sampleTotalCount: number;
  sampleTruncated: boolean;
  sampleValues: RunSurfaceCollectionQueryRuntimeCandidateSample[];
};
