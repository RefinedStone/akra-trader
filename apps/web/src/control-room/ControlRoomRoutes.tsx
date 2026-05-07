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
                    <p className="kicker">Strategy Catalog</p>
                    <h2>Runtime 구분</h2>
                  </div>
                  <button className="ghost-button" onClick={() => void loadAll()} type="button">
                    새로고침
                  </button>
                </div>

                <div className="strategy-columns">
                  <model.StrategyColumn
                    accent="amber"
                    strategies={strategyGroups.native}
                    title="Native"
                  />
                  <model.StrategyColumn
                    accent="ember"
                    strategies={strategyGroups.future}
                    title="Future LLM"
                  />
                </div>
              </section>
            ),
          },
          research: {
            launchPanel: (
              <section className="panel">
                <p className="kicker">Backtest</p>
                <h2>Run 실행</h2>
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
                <p className="kicker">Sandbox</p>
                <h2>Start sandbox worker</h2>
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
                <p className="kicker">Guarded Live</p>
                <h2>Live worker 시작</h2>
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
