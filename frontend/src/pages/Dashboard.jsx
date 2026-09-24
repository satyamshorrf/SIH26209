import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  Snowflake,
  Camera,
  Percent,
  ShieldCheck,
  BrainCircuit,
  PieChart as PieIcon,
  BarChart3,
  Radar as RadarIcon,
} from "lucide-react";
import PageHeader from "../components/common/PageHeader.jsx";
import StatCard from "../components/Cards/StatCard.jsx";
import ChartCard from "../components/ChartCard.jsx";
import PieChartView from "../components/Charts/PieChartView.jsx";
import BarChartView from "../components/Charts/BarChartView.jsx";
import RadarChartView from "../components/Charts/RadarChartView.jsx";
import GaugeView from "../components/Charts/GaugeView.jsx";
import Loader from "../components/common/Loader.jsx";
import { DashboardAPI } from "../services/api.js";
import { formatNumber } from "../utils/format.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    DashboardAPI.get()
      .then(setData)
      .catch((e) => setError(e?.message || "Failed to load dashboard"));
  }, []);

  if (error) {
    return (
      <div>
        <PageHeader icon={LayoutDashboard} title="Mission Dashboard" />
        <p className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {error}. Ensure the backend is running on port 8000.
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div>
        <PageHeader icon={LayoutDashboard} title="Mission Dashboard" />
        <Loader label="Loading mission telemetry…" />
      </div>
    );
  }

  const cards = data.cards || {};
  const landing = data.landing_summary || {};
  const volume = data.volume_summary || {};
  const conf = data.confidence_metrics || {};

  const zoneData = [
    { name: "Safe", value: landing.safe_zones || 0 },
    { name: "Risk", value: landing.risk_zones || 0 },
    { name: "Unsafe", value: landing.unsafe_zones || 0 },
  ];

  const radarData = [
    { metric: "Accuracy", value: (conf.accuracy || 0) * 100 },
    { metric: "Precision", value: (conf.precision || 0) * 100 },
    { metric: "Recall", value: (conf.recall || 0) * 100 },
    { metric: "F1", value: (conf.f1_score || 0) * 100 },
    { metric: "ROC-AUC", value: (conf.roc_auc || 0) * 100 },
  ];

  const compositionData = [
    { name: "PSR", value: volume.psr_percent || 0 },
    { name: "DSPR", value: volume.dspr_percent || 0 },
    { name: "Detected Ice", value: cards.detected_ice_percent || 0 },
  ];

  return (
    <div>
      <PageHeader
        icon={LayoutDashboard}
        title="Mission Dashboard"
        subtitle="Live overview from the bundled Chandrayaan-2 south-polar sample survey"
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard
          icon={Snowflake}
          label="DFSAR Points"
          value={formatNumber(cards.dfsar_points, 0)}
          accent="blue"
          delay={0}
        />
        <StatCard
          icon={Camera}
          label="OHRC Samples"
          value={formatNumber(cards.ohrc_points, 0)}
          accent="cyan"
          delay={0.05}
        />
        <StatCard
          icon={Percent}
          label="Detected Ice"
          value={formatNumber(cards.detected_ice_percent, 2)}
          unit="%"
          accent="purple"
          delay={0.1}
        />
        <StatCard
          icon={ShieldCheck}
          label="Landing Safety"
          value={formatNumber(cards.landing_safety_score, 1)}
          unit="%"
          accent="green"
          delay={0.15}
        />
        <StatCard
          icon={BrainCircuit}
          label="Mission Confidence"
          value={formatNumber(cards.mission_confidence, 1)}
          unit="%"
          accent="orange"
          delay={0.2}
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartCard title="Landing Zone Distribution" icon={PieIcon}>
          <PieChartView
            data={zoneData}
            colors={["#22c55e", "#eab308", "#ef4444"]}
          />
        </ChartCard>
        <ChartCard title="Region Composition (%)" icon={BarChart3}>
          <BarChartView data={compositionData} colorful />
        </ChartCard>
        <ChartCard title="Model Performance" icon={RadarIcon}>
          <RadarChartView data={radarData} />
        </ChartCard>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartCard title="Mission Confidence Gauge" height={220}>
          <GaugeView
            value={cards.mission_confidence || 0}
            label="Confidence %"
          />
        </ChartCard>
        <div className="glass rounded-2xl p-5 lg:col-span-2">
          <h3 className="mb-3 text-sm font-semibold text-white">
            Mission Briefing
          </h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li>
              • Estimated subsurface ice volume:{" "}
              <span className="font-semibold text-accent-blue">
                {formatNumber(volume.total_volume_million_m3, 2)} million m³
              </span>{" "}
              ({formatNumber(volume.total_mass_million_tonnes, 2)} Mt).
            </li>
            <li>
              • Permanently shadowed regions cover{" "}
              <span className="font-semibold text-accent-purple">
                {formatNumber(volume.psr_percent, 1)}%
              </span>{" "}
              of the survey; doubly-shadowed traps{" "}
              {formatNumber(volume.dspr_percent, 1)}%.
            </li>
            <li>
              • {formatNumber(landing.safe_zones, 0)} safe landing candidates of{" "}
              {formatNumber(landing.total_candidates, 0)} evaluated.
            </li>
            <li>
              • Classifier ROC-AUC{" "}
              <span className="font-semibold text-emerald-300">
                {formatNumber((conf.roc_auc || 0) * 100, 1)}%
              </span>{" "}
              with mission confidence{" "}
              {formatNumber(cards.mission_confidence, 1)}%.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
