import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

/**
 * data: [{ metric, value }]  (value 0-100)
 */
export default function RadarChartView({ data, color = "#a855f7" }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="72%">
        <PolarGrid stroke="rgba(148,163,184,0.2)" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: "#cbd5e1", fontSize: 11 }} />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fill: "#64748b", fontSize: 10 }}
        />
        <Radar
          name="Score"
          dataKey="value"
          stroke={color}
          fill={color}
          fillOpacity={0.35}
        />
        <Tooltip
          contentStyle={{
            background: "#121a33",
            border: "1px solid rgba(148,163,184,0.2)",
            borderRadius: 12,
            color: "#e2e8f0",
          }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
