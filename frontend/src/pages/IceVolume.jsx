import { useEffect, useState } from "react";
import { Boxes, Layers, Mountain, Table2, PieChart as PieIcon } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import DatasetUploader from "../components/DatasetUploader.jsx";
import RunButton from "../components/common/RunButton.jsx";
import SampleLoader from "../components/common/SampleLoader.jsx";
import ProgressBar from "../components/common/ProgressBar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ChartCard from "../components/ChartCard.jsx";
import PieChartView from "../components/Charts/PieChartView.jsx";
import DownloadButton from "../components/DownloadButton.jsx";
import DataTable from "../components/common/DataTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import ImageViewer from "../components/ImageViewer.jsx";
import { useModuleProcessor } from "../hooks/useModuleProcessor.js";
import { useResults } from "../context/ResultsContext.jsx";
import { VolumeAPI } from "../services/api.js";
import { formatNumber } from "../utils/format.js";

export default function IceVolume() {
  const proc = useModuleProcessor(VolumeAPI);
  const { saveResult } = useResults();
  const [depth, setDepth] = useState(5);

  useEffect(() => {
    if (proc.result) saveResult("volume", proc.result);
  }, [proc.result, saveResult]);

  const r = proc.result;

  return (
    <div>
      <PageHeader
        icon={Boxes}
        title="Module 2 · Ice Volume Estimation"
        subtitle="PSR / DSPR mapping and Volume = Area × Depth × Ice Fraction"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ResultCard title="Upload & Process">
          <DatasetUploader
            file={proc.file}
            onFile={proc.setFile}
            label="Dataset CSV"
          />
          <div className="mt-4">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">
              Sensing depth (m)
            </label>
            <input
              type="number"
              min={1}
              max={20}
              step={0.5}
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-700/60 bg-space-700/50 px-3 py-2 text-sm text-white outline-none focus:border-accent-blue"
            />
          </div>
          <div className="mt-3">
            <SampleLoader onLoaded={proc.setFile} />
          </div>
          <RunButton
            onRun={() => proc.run(depth)}
            onReset={proc.reset}
            isBusy={proc.isBusy}
            disabled={!proc.file}
            label="Estimate Volume"
          />
          <ProgressBar progress={proc.progress} status={proc.status} />
          {proc.error && (
            <p className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-300">
              {proc.error}
            </p>
          )}
        </ResultCard>

        <div className="lg:col-span-2">
          {!r ? (
            <EmptyState
              icon={Boxes}
              title="No volume estimate yet"
              message="Upload a dataset (or load the sample) and run the estimation."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard
                  icon={Boxes}
                  label="Ice Volume"
                  value={formatNumber(r.estimated_ice_volume_million_m3, 2)}
                  unit="M m³"
                  accent="blue"
                />
                <StatCard
                  icon={Mountain}
                  label="Ice Mass"
                  value={formatNumber(r.estimated_mass_million_tonnes, 2)}
                  unit="Mt"
                  accent="purple"
                />
                <StatCard
                  icon={Layers}
                  label="PSR Coverage"
                  value={formatNumber(r.psr_percent, 1)}
                  unit="%"
                  accent="cyan"
                />
                <StatCard
                  icon={Layers}
                  label="DSPR Coverage"
                  value={formatNumber(r.dspr_percent, 1)}
                  unit="%"
                  accent="green"
                />
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ChartCard title="Shadowed Region Distribution" icon={PieIcon}>
                  <PieChartView data={r.charts?.region_distribution || []} />
                </ChartCard>
                <ResultCard title="Region Chart & Downloads">
                  <ImageViewer
                    filename={r.artifacts?.region_chart_png}
                    alt="Region distribution chart"
                  />
                  <div className="mt-4">
                    <DownloadButton
                      filename={r.artifacts?.volume_csv}
                      label="Volume CSV"
                    />
                  </div>
                </ResultCard>
              </div>

              <ResultCard title="Per-cell Volume Preview" icon={Table2}>
                <DataTable rows={r.preview} />
              </ResultCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
