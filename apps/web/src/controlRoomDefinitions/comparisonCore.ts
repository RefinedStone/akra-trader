export const COMPARISON_RUN_ID_SEARCH_PARAM = "compare_run_id";
export const COMPARISON_INTENT_SEARCH_PARAM = "compare_intent";
export const COMPARISON_FOCUS_RUN_ID_SEARCH_PARAM = "compare_focus_run_id";
export const COMPARISON_FOCUS_SECTION_SEARCH_PARAM = "compare_focus_section";
export const COMPARISON_FOCUS_COMPONENT_SEARCH_PARAM = "compare_focus_component";
export const COMPARISON_FOCUS_SOURCE_SEARCH_PARAM = "compare_focus_source";
export const COMPARISON_FOCUS_ORIGIN_RUN_ID_SEARCH_PARAM = "compare_focus_origin_run_id";
export const COMPARISON_FOCUS_DETAIL_SEARCH_PARAM = "compare_focus_detail";
export const COMPARISON_FOCUS_EXPANDED_SEARCH_PARAM = "compare_focus_expanded";
export const COMPARISON_FOCUS_ARTIFACT_EXPANDED_SEARCH_PARAM = "compare_focus_artifact_expanded";
export const COMPARISON_FOCUS_ARTIFACT_LINE_EXPANDED_SEARCH_PARAM = "compare_focus_artifact_line_expanded";
export const COMPARISON_FOCUS_ARTIFACT_LINE_VIEW_SEARCH_PARAM = "compare_focus_artifact_line_view";
export const COMPARISON_FOCUS_ARTIFACT_LINE_MICRO_VIEW_SEARCH_PARAM = "compare_focus_artifact_line_micro_view";
export const COMPARISON_FOCUS_ARTIFACT_LINE_NOTE_PAGE_SEARCH_PARAM = "compare_focus_artifact_line_note_page";
export const COMPARISON_FOCUS_ARTIFACT_LINE_HOVER_SEARCH_PARAM = "compare_focus_artifact_line_hover";
export const COMPARISON_FOCUS_ARTIFACT_LINE_SCRUB_SEARCH_PARAM = "compare_focus_artifact_line_scrub";
export const COMPARISON_FOCUS_TOOLTIP_SEARCH_PARAM = "compare_focus_tooltip";
export const COMPARISON_FOCUS_ARTIFACT_HOVER_SEARCH_PARAM = "compare_focus_artifact_hover";
export const MAX_COMPARISON_RUNS = 4;

export type ComparisonIntent = "benchmark_validation" | "execution_regression" | "strategy_tuning";
export type ComparisonCueKind = "mode" | "baseline" | "best" | "insight";

export type ComparisonScoreSection = "metrics" | "semantics" | "context";
export type ProvenanceArtifactLineDetailView = "stats" | "context";
export type ProvenanceArtifactLineMicroView = "structure" | "signal" | "note";

export type ComparisonScoreLinkTarget = {
  narrativeRunId: string;
  section: ComparisonScoreSection;
  componentKey: string;
  source: ComparisonScoreLinkSource;
  originRunId: string | null;
  subFocusKey: string | null;
  detailExpanded: boolean | null;
  artifactDetailExpanded: boolean | null;
  artifactLineDetailExpanded: boolean | null;
  artifactLineDetailView: ProvenanceArtifactLineDetailView | null;
  artifactLineMicroView: ProvenanceArtifactLineMicroView | null;
  artifactLineNotePage: number | null;
  artifactLineDetailHoverKey: string | null;
  artifactLineDetailScrubStep: number | null;
  tooltipKey: string | null;
  artifactHoverKey: string | null;
};

export type ComparisonScoreLinkedRunRole = "baseline" | "target";

export type ComparisonScoreLinkSource =
  | "metric"
  | "drillback"
  | "overview"
  | "provenance"
  | "run_card"
  | "run_list";

export type ComparisonHistoryWriteMode = "push" | "replace" | "skip";

export type ComparisonScoreDrillBackOptions = {
  subFocusKey?: string | null;
  tooltipKey?: string | null;
  detailExpanded?: boolean | null;
  artifactDetailExpanded?: boolean | null;
  artifactLineDetailExpanded?: boolean | null;
  artifactLineDetailView?: ProvenanceArtifactLineDetailView | null;
  artifactLineMicroView?: ProvenanceArtifactLineMicroView | null;
  artifactLineNotePage?: number | null;
  artifactLineDetailHoverKey?: string | null;
  artifactLineDetailScrubStep?: number | null;
  artifactHoverKey?: string | null;
  historyMode?: ComparisonHistoryWriteMode;
};
