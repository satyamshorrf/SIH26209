import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { CHART_COLORS } from "../../utils/format.js";

/**
 * data: [{ name, value }]
 */
export default function BarChartView({ data, dataKey = "value", color = "#4f8cff", colorful = false }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 8, right: 12, left: -8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.12)" />
        <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip
          cursor={{ fill: "rgba(79,140,255,0.08)" }}
          contentStyle={{
            background: "#121a33",
            border: "1px solid rgba(148,163,184,0.2)",
            borderRadius: 12,
            color: "#e2e8f0",
          }}
        />
        <Bar dataKey={dataKey} radius={[6, 6, 0, 0]} fill={color}>
          {colorful &&
            data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
