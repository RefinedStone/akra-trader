// @ts-nocheck
import { ControlRoomLiveControlPanel } from "./ControlRoomLiveControlPanel";
import { ControlRoomMarketDataPanel } from "./ControlRoomMarketDataPanel";
import { ControlRoomOverviewPanel } from "./ControlRoomOverviewPanel";
import { MarketCandlestickChartPanel } from "./MarketCandlestickChartPanel";
import { RuntimeOperatorPanel } from "./RuntimeOperatorPanel";

export function ControlRoomRoutes({ model }: { model: any }) {
  const {
    WorkspaceRouteContent,
    WorkspaceShell,
    activeWorkspace,
    activeWorkspaceDescriptor,
    apiBase,
    backtestForm,
    beginPresetEdit,
    controlStripMetrics,
    editingPresetId,
    expandedPresetRevisionIds,
    handleBacktestSubmit,
    handleLiveSubmit,
    handlePresetSubmit,
    handleSandboxSubmit,
    liveForm,
    loadAll,
    navigateToWorkspace,
    presetForm,
    presets,
    runHistoryWorkspacePanels,
    runSurfaceCapabilities,
    sandboxForm,
    setBacktestForm,
    setLiveForm,
    setPresetForm,
    setSandboxForm,
    statusText,
    strategies,
    strategyGroups,
    workspaceDescriptors,
  } = model;

  const nativeStrategies = strategies.filter((strategy: any) => strategy.runtime === "native");

  return (
    <WorkspaceShell
      activeWorkspace={activeWorkspace}
      activeWorkspaceDescriptor={activeWorkspaceDescriptor}
      apiBase={apiBase}
      controlStripMetrics={controlStripMetrics}
      onNavigate={navigateToWorkspace}
      onRefresh={() => void loadAll()}
      statusText={statusText}
      workspaceDescriptors={workspaceDescriptors}
    >
      <WorkspaceRouteContent
        activeWorkspace={activeWorkspace}
        routes={{
          overview: {
            briefingPanel: (
              <ControlRoomOverviewPanel
                controlStripMetrics={controlStripMetrics}
                onNavigate={navigateToWorkspace}
                statusText={statusText}
                workspaceDescriptors={workspaceDescriptors}
              />
            ),
            catalogPanel: (
              <section className="panel panel-wide">
                <div className="section-heading">
                  <div>
                    <p className="kicker">전략 운영 카탈로그</p>
                    <h2>실행 가능한 전략</h2>
                  </div>
                  <button className="ghost-button" onClick={() => void loadAll()} type="button">
                    새로고침
                  </button>
                </div>

                <div className="strategy-columns">
                  <model.StrategyColumn
                    accent="amber"
                    strategies={strategyGroups.native}
                    title="운용 전략"
                  />
                  <model.StrategyColumn
                    accent="ember"
                    strategies={strategyGroups.future}
                    title="준비 중인 전략"
                  />
                </div>
              </section>
            ),
          },
          research: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">전략 검증</p>
                <h2>백테스트 실행</h2>
                <model.RunForm
                  form={backtestForm}
                  onSubmit={handleBacktestSubmit}
                  presets={presets}
                  setForm={setBacktestForm}
                  showDateRange
                  strategies={strategies}
                />
              </section>
            ),
            presetPanel: (
              <section className="panel panel-wide">
                <p className="kicker">실험 운영</p>
                <h2>시나리오 Preset</h2>
                <model.PresetCatalogPanel
                  editingPresetId={editingPresetId}
                  expandedPresetRevisionIds={expandedPresetRevisionIds}
                  form={presetForm}
                  onEditPreset={beginPresetEdit}
                  onLifecycleAction={model.applyPresetLifecycleAction}
                  onResetEditor={model.resetPresetEditor}
                  onRestoreRevision={model.restorePresetRevision}
                  onSubmit={handlePresetSubmit}
                  onToggleRevisions={model.togglePresetRevisions}
                  presets={presets}
                  runSurfaceCapabilities={runSurfaceCapabilities}
                  setForm={setPresetForm}
                  strategies={strategies}
                />
              </section>
            ),
            ...runHistoryWorkspacePanels.research,
          },
          markets: {
            chartPanel: <MarketCandlestickChartPanel />,
          },
          runtime: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">모의 운용</p>
                <h2>샌드박스 실행</h2>
                <model.RunForm
                  form={sandboxForm}
                  onSubmit={handleSandboxSubmit}
                  presets={presets}
                  setForm={setSandboxForm}
                  strategies={nativeStrategies}
                />
              </section>
            ),
            marketDataPanel: <ControlRoomMarketDataPanel model={model} />,
            operatorPanel: <RuntimeOperatorPanel model={model} />,
            ...runHistoryWorkspacePanels.runtime,
          },
          live: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">실전 보호 운용</p>
                <h2>가드 라이브 시작</h2>
                <model.RunForm
                  form={liveForm}
                  onSubmit={handleLiveSubmit}
                  presets={presets}
                  setForm={setLiveForm}
                  strategies={nativeStrategies}
                />
              </section>
            ),
            controlPanel: <ControlRoomLiveControlPanel model={model} />,
            ...runHistoryWorkspacePanels.live,
          },
        }}
      />
    </WorkspaceShell>
  );
}
