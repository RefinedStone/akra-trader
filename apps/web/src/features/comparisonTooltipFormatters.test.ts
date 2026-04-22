import { describe, expect, it } from "vitest";

import {
  formatComparisonTooltipConflictSessionMetadata,
  formatComparisonTooltipConflictSessionSummary,
  formatComparisonTooltipConflictSessionSummarySession,
  formatComparisonTooltipPresetConflictGroupSummary,
  formatComparisonTooltipPresetImportFeedback,
  formatComparisonTooltipTuningDelta,
  formatComparisonTooltipTuningValue,
  formatRelativeTimestampLabel,
  hashComparisonTooltipConflictSessionRaw,
  parseComparisonTooltipConflictSessionUpdatedAt,
} from "./comparisonTooltipFormatters";

describe("comparisonTooltipFormatters", () => {
  it("formats tuning values and deltas consistently", () => {
    expect(formatComparisonTooltipTuningValue(2)).toBe("2");
    expect(formatComparisonTooltipTuningValue(2.5)).toBe("2.5");
    expect(formatComparisonTooltipTuningDelta(1, 1)).toEqual({
      direction: "same",
      label: "match",
    });
    expect(formatComparisonTooltipTuningDelta(1, 2.5)).toEqual({
      direction: "higher",
      label: "higher +1.5",
    });
  });

  it("summarizes preset conflict groups and import feedback", () => {
    expect(
      formatComparisonTooltipPresetConflictGroupSummary([
        {
          changed: true,
          delta_direction: "higher",
          delta_label: "higher +1",
          existing_value: 1,
          group_key: "timing",
          group_label: "Timing",
          group_order: 0,
          incoming_value: 2,
          key: "metric_hover_open_ms",
          label: "Hover open",
        },
        {
          changed: false,
          delta_direction: "same",
          delta_label: "match",
          existing_value: 1,
          group_key: "timing",
          group_label: "Timing",
          group_order: 0,
          incoming_value: 1,
          key: "metric_hover_close_ms",
          label: "Hover close",
        },
      ]),
    ).toBe("1 changed · 1 higher · 1 match");

    expect(
      formatComparisonTooltipPresetImportFeedback({
        conflicted: true,
        final_preset_name: "Momentum v2",
        imported_preset_name: "Momentum",
        policy: "rename",
        renamed: true,
        overwritten: false,
      }),
    ).toBe('Imported preset "Momentum" as "Momentum v2" because that name already existed.');
  });

  it("formats session labels and metadata from shared helpers", () => {
    expect(
      formatComparisonTooltipConflictSessionSummary({
        group_key: "baseline",
        includes_current: false,
        preset_name: "Preset A",
        session_count: 2,
        sessions: [],
      }),
    ).toBe("Preset A (2 saved sessions)");
    expect(
      formatComparisonTooltipConflictSessionSummarySession(
        {
          hash: "abc123",
          includes_current: false,
          metadata: [],
          session_key: "Preset A:abc123",
          updated_at: null,
        },
        1,
        3,
      ),
    ).toBe("Saved session 2");
    expect(
      formatComparisonTooltipConflictSessionMetadata(
        {
          collapsed_unchanged_groups: { timing: true },
          show_unchanged_conflict_rows: false,
          updated_at: null,
        },
        "abcdef123",
        Date.UTC(2026, 0, 1),
      ),
    ).toEqual([
      "updated time unavailable",
      "unchanged rows hidden",
      "1 collapsed group",
      "ID abcdef12",
    ]);
  });

  it("keeps timestamp parsing and hashing deterministic", () => {
    expect(formatRelativeTimestampLabel(undefined)).toBe("n/a");
    expect(parseComparisonTooltipConflictSessionUpdatedAt("invalid")).toBe(0);
    expect(hashComparisonTooltipConflictSessionRaw("Preset A:raw-payload")).toBe(
      hashComparisonTooltipConflictSessionRaw("Preset A:raw-payload"),
    );
    expect(hashComparisonTooltipConflictSessionRaw("Preset A:raw-payload")).not.toBe(
      hashComparisonTooltipConflictSessionRaw("Preset B:raw-payload"),
    );
  });
});
