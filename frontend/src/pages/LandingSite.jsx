import { useEffect } from "react";
import { Rocket, ShieldCheck, MapPin, Table2, PieChart as PieIcon } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import DatasetUploader from "../components/DatasetUploader.jsx";
import RunButton from "../components/common/RunButton.jsx";
import SampleLoader from "../components/common/SampleLoader.jsx";
import ProgressBar from "../components/common/ProgressBar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ChartCard from "../components/ChartCard.jsx";
import PieChartView from "../components/Charts/PieChartView.jsx";
import ImageViewer from "../components/ImageViewer.jsx";
import DownloadButton from "../components/DownloadButton.jsx";
import DataTable from "../components/common/DataTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import LunarMap from "../components/MapViewer/LunarMap.jsx";
import { useModuleProcessor } from "../hooks/useModuleProcessor.js";
import { useResults } from "../context/ResultsContext.jsx";
import { LandingAPI } from "../services/api.js";
import { formatNumber } from "../utils/format.js";

export default function LandingSite() {
  const proc = useModuleProcessor(LandingAPI);
  const { saveResult } = useResults();

  useEffect(() => {
    if (proc.result) saveResult("landing", proc.result);
  }, [proc.result, saveResult]);

  const r = proc.result;
  const best = r?.best_site;

  const points = (r?.preview || [])
    .filter((row) => row.Latitude !== undefined && row.Longitude !== undefined)
    .map((row) => ({ lat: row.Latitude, lon: row.Longitude, value: row.LSI }));

  return (
    <div>
      <PageHeader
        icon={Rocket}
        title="Module 3 · Safe Landing Site"
        subtitle="Multi-criteria suitability from slope, roughness, craters, boulders & illumination"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ResultCard title="Upload & Process">
          <DatasetUploader
            file={proc.file}
            onFile={proc.setFile}
            label="Terrain / DEM CSV"
          />
          <div className="mt-3">
            <SampleLoader onLoaded={proc.setFile} />
          </div>
          <RunButton
            onRun={() => proc.run()}
            onReset={proc.reset}
            isBusy={proc.isBusy}
            disabled={!proc.file}
            label="Analyse Landing Sites"
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
              icon={Rocket}
              title="No landing analysis yet"
              message="Upload a dataset (or load the sample) and run the analysis."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard
                  icon={ShieldCheck}
                  label="Best Safety"
                  value={formatNumber(best?.safety_percent, 1)}
                  unit="%"
                  accent="green"
                />
                <StatCard
                  icon={Rocket}
                  label="Safe Zones"
                  value={formatNumber(r.safe_zones, 0)}
                  accent="blue"
                />
                <StatCard
                  icon={Rocket}
                  label="Risk Zones"
                  value={formatNumber(r.risk_zones, 0)}
                  accent="orange"
                />
                <StatCard
                  icon={Rocket}
                  label="Unsafe Zones"
                  value={formatNumber(r.unsafe_zones, 0)}
                  accent="purple"
                />
              </div>

              {best && (
                <ResultCard title="Recommended Touchdown" icon={MapPin}>
                  <div className="grid grid-cols-2 gap-3 text-sm text-slate-300 md:grid-cols-4">
                    <div>
                      <p className="text-xs text-slate-400">Latitude</p>
                      <p className="font-semibold text-white">
                        {formatNumber(best.latitude, 4)}°
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Longitude</p>
                      <p className="font-semibold text-white">
                        {formatNumber(best.longitude, 4)}°
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Slope</p>
                      <p className="font-semibold text-white">
                        {formatNumber(best.slope, 2)}°
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Zone</p>
                      <p className="font-semibold text-emerald-300">{best.zone}</p>
                    </div>
                  </div>
                </ResultCard>
              )}

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ChartCard title="Zone Distribution" icon={PieIcon}>
                  <PieChartView
                    data={r.charts?.zone_distribution || []}
                    colors={["#22c55e", "#eab308", "#ef4444"]}
                  />
                </ChartCard>
                <ResultCard title="Suitability Map">
                  <ImageViewer
                    filename={r.artifacts?.landing_map_png}
                    alt="Landing suitability map"
                  />
                  <div className="mt-3">
                    <DownloadButton
                      filename={r.artifacts?.landing_csv}
                      label="Landing Sites CSV"
                    />
                  </div>
                </ResultCard>
              </div>

              {points.length > 0 && (
                <ResultCard title="Interactive Lunar Viewer" icon={MapPin}>
                  <LunarMap points={points} />
                </ResultCard>
              )}

              <ResultCard title="Candidate Preview" icon={Table2}>
                <DataTable rows={r.preview} />
              </ResultCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
