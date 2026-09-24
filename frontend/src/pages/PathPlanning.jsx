import { useEffect, useState } from "react";
import { Route as RouteIcon, Ruler, Clock, MapPin, Table2 } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import DatasetUploader from "../components/DatasetUploader.jsx";
import RunButton from "../components/common/RunButton.jsx";
import SampleLoader from "../components/common/SampleLoader.jsx";
import ProgressBar from "../components/common/ProgressBar.jsx";
import ResultCard from "../components/ResultCard.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ImageViewer from "../components/ImageViewer.jsx";
import DownloadButton from "../components/DownloadButton.jsx";
import DataTable from "../components/common/DataTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import LunarMap from "../components/MapViewer/LunarMap.jsx";
import { useModuleProcessor } from "../hooks/useModuleProcessor.js";
import { useResults } from "../context/ResultsContext.jsx";
import { PathAPI } from "../services/api.js";
import { formatNumber } from "../utils/format.js";

export default function PathPlanning() {
  const proc = useModuleProcessor(PathAPI);
  const { saveResult } = useResults();
  const [algorithm, setAlgorithm] = useState("astar");
  const [gridSize, setGridSize] = useState(40);

  useEffect(() => {
    if (proc.result) saveResult("path", proc.result);
  }, [proc.result, saveResult]);

  const r = proc.result;
  const path = (r?.waypoints || []).map((w) => ({ lat: w.lat, lon: w.lon }));

  return (
    <div>
      <PageHeader
        icon={RouteIcon}
        title="Module 4 · Rover Path Planning"
        subtitle="A* / Dijkstra over a hazard-weighted grid with solar & terrain constraints"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ResultCard title="Upload & Process">
          <DatasetUploader
            file={proc.file}
            onFile={proc.setFile}
            label="Terrain CSV"
          />
          <div className="mt-4">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">
              Algorithm
            </label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="w-full rounded-lg border border-slate-700/60 bg-space-700/50 px-3 py-2 text-sm text-white outline-none focus:border-accent-blue"
            >
              <option value="astar">A* (heuristic search)</option>
              <option value="dijkstra">Dijkstra (uniform cost)</option>
            </select>
          </div>
          <div className="mt-4">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">
              Grid size ({gridSize}×{gridSize})
            </label>
            <input
              type="range"
              min={20}
              max={80}
              step={5}
              value={gridSize}
              onChange={(e) => setGridSize(Number(e.target.value))}
              className="w-full accent-[#4f8cff]"
            />
          </div>
          <div className="mt-3">
            <SampleLoader onLoaded={proc.setFile} />
          </div>
          <RunButton
            onRun={() => proc.run(algorithm, gridSize)}
            onReset={proc.reset}
            isBusy={proc.isBusy}
            disabled={!proc.file}
            label="Plan Route"
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
              icon={RouteIcon}
              title="No route planned yet"
              message="Upload a dataset (or load the sample) and plan a rover route."
            />
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <StatCard
                  icon={Ruler}
                  label="Distance"
                  value={formatNumber(r.distance_km, 2)}
                  unit="km"
                  accent="blue"
                />
                <StatCard
                  icon={Clock}
                  label="Travel Time"
                  value={formatNumber(r.travel_time_hours, 1)}
                  unit="h"
                  accent="purple"
                />
                <StatCard
                  icon={MapPin}
                  label="Waypoints"
                  value={formatNumber(r.num_waypoints, 0)}
                  accent="cyan"
                />
                <StatCard
                  icon={RouteIcon}
                  label="Path Cost"
                  value={formatNumber(r.path_cost, 2)}
                  accent="orange"
                />
              </div>

              <ResultCard title={r.algorithm} icon={RouteIcon}>
                <p className="text-sm text-slate-300">
                  Start: {formatNumber(r.start?.lat, 3)}°,{" "}
                  {formatNumber(r.start?.lon, 3)}° → Target:{" "}
                  {formatNumber(r.goal?.lat, 3)}°, {formatNumber(r.goal?.lon, 3)}°
                </p>
              </ResultCard>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ResultCard title="Route Map">
                  <ImageViewer
                    filename={r.artifacts?.route_map_png}
                    alt="Rover route map"
                  />
                  <div className="mt-3">
                    <DownloadButton
                      filename={r.artifacts?.route_csv}
                      label="Route CSV"
                    />
                  </div>
                </ResultCard>
                <ResultCard title="Interactive Route Viewer" icon={MapPin}>
                  <LunarMap path={path} />
                </ResultCard>
              </div>

              <ResultCard title="Waypoints" icon={Table2}>
                <DataTable rows={r.waypoints} maxRows={12} />
              </ResultCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
