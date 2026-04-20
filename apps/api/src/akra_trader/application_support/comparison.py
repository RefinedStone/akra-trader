COMPARISON_METRICS: tuple[tuple[str, str, str, bool], ...] = (
  ("total_return_pct", "Total return", "pct", True),
  ("max_drawdown_pct", "Max drawdown", "pct", False),
  ("win_rate_pct", "Win rate", "pct", True),
  ("trade_count", "Trades", "count", True),
)

COMPARISON_INTENT_DEFAULT = "benchmark_validation"

COMPARISON_INTENT_WEIGHTS: dict[str, dict[str, float]] = {
  "benchmark_validation": {
    "return": 0.8,
    "drawdown": 1.5,
    "win_rate": 0.7,
    "trade_count": 0.12,
    "semantic_kind_bonus": 1.2,
    "semantic_execution_bonus": 0.8,
    "semantic_source_bonus": 0.8,
    "semantic_parameter_contract_bonus": 0.4,
    "semantic_vocabulary_unit_bonus": 0.28,
    "provenance_richness_unit_bonus": 0.24,
    "native_reference_bonus": 8.0,
    "reference_bonus": 3.0,
    "status_bonus": 1.5,
    "benchmark_story_bonus": 1.5,
    "reference_floor": 1.0,
  },
  "execution_regression": {
    "return": 0.9,
    "drawdown": 1.9,
    "win_rate": 1.0,
    "trade_count": 0.4,
    "semantic_kind_bonus": 0.8,
    "semantic_execution_bonus": 0.6,
    "semantic_source_bonus": 0.4,
    "semantic_parameter_contract_bonus": 0.3,
    "semantic_vocabulary_unit_bonus": 0.18,
    "provenance_richness_unit_bonus": 0.2,
    "native_reference_bonus": 3.0,
    "reference_bonus": 1.0,
    "status_bonus": 3.0,
    "benchmark_story_bonus": 0.8,
    "reference_floor": 1.0,
  },
  "strategy_tuning": {
    "return": 2.0,
    "drawdown": 0.7,
    "win_rate": 1.3,
    "trade_count": 0.35,
    "semantic_kind_bonus": 1.0,
    "semantic_execution_bonus": 0.7,
    "semantic_source_bonus": 0.6,
    "semantic_parameter_contract_bonus": 0.5,
    "semantic_vocabulary_unit_bonus": 0.38,
    "provenance_richness_unit_bonus": 0.12,
    "native_reference_bonus": 1.5,
    "reference_bonus": 0.5,
    "status_bonus": 0.8,
    "benchmark_story_bonus": 0.4,
    "reference_floor": 0.5,
  },
}

COMPARISON_INTENT_COPY: dict[str, dict[str, str]] = {
  "benchmark_validation": {
    "title_prefix": "Benchmark validation",
    "summary_prefix": "Validation view",
    "partial_summary": (
      "Benchmark validation falls back to persisted reference provenance because direct metric "
      "deltas are partial."
    ),
    "lane_prefix": "Validation context",
    "activity_prefix": "Validation signal",
    "reference_prefix": "Benchmark evidence",
  },
  "execution_regression": {
    "title_prefix": "Execution regression",
    "summary_prefix": "Regression view",
    "partial_summary": (
      "Execution regression falls back to persisted reference provenance because direct execution "
      "deltas are partial."
    ),
    "lane_prefix": "Regression context",
    "activity_prefix": "Execution signal",
    "reference_prefix": "Reference baseline",
  },
  "strategy_tuning": {
    "title_prefix": "Strategy tuning",
    "summary_prefix": "Tuning view",
    "partial_summary": (
      "Strategy tuning falls back to benchmark provenance because direct optimization deltas are partial."
    ),
    "lane_prefix": "Tuning context",
    "activity_prefix": "Tuning signal",
    "reference_prefix": "Benchmark backdrop",
  },
}

COMPARISON_METRIC_COPY: dict[str, dict[str, dict[str, str]]] = {
  "benchmark_validation": {
    "total_return_pct": {
      "annotation": "Validation read: return drift versus the selected benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Validation read: downside drift versus the benchmark risk envelope.",
      "positive_delta": "deeper than benchmark",
      "negative_delta": "tighter than benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark drawdown delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Validation read: hit-rate drift versus the benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark hit-rate delta unavailable",
    },
    "trade_count": {
      "annotation": "Validation read: participation and pacing drift versus the benchmark.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark activity delta unavailable",
    },
  },
  "execution_regression": {
    "total_return_pct": {
      "annotation": "Regression read: return movement is treated as execution drift.",
      "positive_delta": "return lift",
      "negative_delta": "return regression",
      "baseline": "regression baseline",
      "missing": "return regression unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Regression read: higher drawdown is treated as risk regression.",
      "positive_delta": "extra drawdown",
      "negative_delta": "risk improvement",
      "baseline": "regression baseline",
      "missing": "drawdown regression unavailable",
    },
    "win_rate_pct": {
      "annotation": "Regression read: hit-rate movement is treated as execution drift.",
      "positive_delta": "hit-rate lift",
      "negative_delta": "hit-rate regression",
      "baseline": "regression baseline",
      "missing": "hit-rate regression unavailable",
    },
    "trade_count": {
      "annotation": "Regression read: trade-flow changes point to execution behavior drift.",
      "positive_delta": "extra activity",
      "negative_delta": "reduced activity",
      "baseline": "regression baseline",
      "missing": "activity regression unavailable",
    },
  },
  "strategy_tuning": {
    "total_return_pct": {
      "annotation": "Tuning read: return deltas show optimization edge versus the baseline.",
      "positive_delta": "tuning edge",
      "negative_delta": "tuning gap",
      "baseline": "tuning baseline",
      "missing": "tuning delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Tuning read: lower drawdown marks a cleaner optimization tradeoff.",
      "positive_delta": "drawdown penalty",
      "negative_delta": "drawdown improvement",
      "baseline": "tuning baseline",
      "missing": "drawdown tuning delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Tuning read: hit-rate deltas show signal-quality tradeoffs.",
      "positive_delta": "hit-rate edge",
      "negative_delta": "hit-rate gap",
      "baseline": "tuning baseline",
      "missing": "hit-rate tuning delta unavailable",
    },
    "trade_count": {
      "annotation": "Tuning read: trade-count changes expose activity tradeoffs in the variant.",
      "positive_delta": "activity expansion",
      "negative_delta": "activity reduction",
      "baseline": "tuning baseline",
      "missing": "activity tuning delta unavailable",
    },
  },
}
