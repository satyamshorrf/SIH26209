import { FileBarChart, Trash2, Snowflake, Boxes, Rocket, Route as RouteIcon, BrainCircuit } from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import ResultCard from "../components/ResultCard.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { useResults } from "../context/ResultsContext.jsx";
import { formatNumber, formatPercent } from "../utils/format.js";

const MODULES = [
  { key: "ice", label: "Ice Detection", icon: Snowflake },
  { key: "volume", label: "Ice Volume", icon: Boxes },
  { key: "landing", label: "Safe Landing", icon: Rocket },
  { key: "path", label: "Path Planning", icon: RouteIcon },
  { key: "confidence", label: "AI Confidence", icon: BrainCircuit },
];

function summarise(key, payload) {
  switch (key) {
    case "ice":
      return [
        ["Ice detected", formatNumber(payload.ice_detection_percent, 2) + "%"],
        ["Ice points", formatNumber(payload.detected_points, 0)],
        ["Mean probability", formatPercent(payload.mean_ice_probability)],
      ];
    case "volume":
      return [
        ["Volume", formatNumber(payload.estimated_ice_volume_million_m3, 2) + " M m³"],
        ["Mass", formatNumber(payload.estimated_mass_million_tonnes, 2) + " Mt"],
        ["PSR / DSPR", `${formatNumber(payload.psr_percent, 1)}% / ${formatNumber(payload.dspr_percent, 1)}%`],
      ];
    case "landing":
      return [
        ["Best safety", formatNumber(payload.best_site?.safety_percent, 1) + "%"],
        ["Safe zones", formatNumber(payload.safe_zones, 0)],
        ["Touchdown", `${formatNumber(payload.best_site?.latitude, 3)}°, ${formatNumber(payload.best_site?.longitude, 3)}°`],
      ];
    case "path":
      return [
        ["Algorithm", payload.algorithm],
        ["Distance", formatNumber(payload.distance_km, 2) + " km"],
        ["Waypoints", formatNumber(payload.num_waypoints, 0)],
      ];
    case "confidence":
      return [
        ["Accuracy", formatPercent(payload.metrics?.accuracy)],
        ["ROC-AUC", formatPercent(payload.metrics?.roc_auc)],
        ["Mission confidence", formatNumber(payload.metrics?.mission_confidence_percent, 1) + "%"],
      ];
    default:
      return [];
  }
}

export default function Results() {
  const { results, clearResults } = useResults();
  const hasAny = Object.keys(results).length > 0;

  return (
    <div>
      <PageHeader
        icon={FileBarChart}
        title="Consolidated Results"
        subtitle="Latest output from each analysis module in this session"
      />

      {!hasAny ? (
        <EmptyState
          icon={FileBarChart}
          title="No results recorded"
          message="Run any of the five modules and their latest results will be summarised here."
        />
      ) : (
        <>
          <div className="mb-4 flex justify-end">
            <button
              onClick={clearResults}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-600/60 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700/40"
            >
              <Trash2 className="h-4 w-4" />
              Clear results
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {MODULES.map(({ key, label, icon: Icon }) => {
              const entry = results[key];
              return (
                <ResultCard key={key} title={label} icon={Icon}>
                  {!entry ? (
                    <p className="text-sm text-slate-500">Not run yet.</p>
                  ) : (
                    <>
                      <ul className="space-y-1.5 text-sm text-slate-300">
                        {summarise(key, entry.payload).map(([k, v]) => (
                          <li key={k} className="flex justify-between gap-3">
                            <span className="text-slate-400">{k}</span>
                            <span className="font-medium text-white">{v}</span>
                          </li>
                        ))}
                      </ul>
                      <p className="mt-3 text-[11px] text-slate-500">
                        Updated {new Date(entry.savedAt).toLocaleString()}
                      </p>
                    </>
                  )}
                </ResultCard>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
