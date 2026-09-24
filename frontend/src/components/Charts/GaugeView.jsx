import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import { scoreColor } from "../../utils/format.js";

/**
 * Single-value gauge (0-100) rendered as a radial bar with a centred label.
 */
export default function GaugeView({ value = 0, label = "Score" }) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  const data = [{ name: label, value: clamped, fill: scoreColor(clamped) }];

  return (
    <div className="relative h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          innerRadius="68%"
          outerRadius="100%"
          data={data}
          startAngle={220}
          endAngle={-40}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background={{ fill: "rgba(148,163,184,0.12)" }} dataKey="value" cornerRadius={12} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{clamped.toFixed(1)}</span>
        <span className="text-xs text-slate-400">{label}</span>
      </div>
    </div>
  );
}
