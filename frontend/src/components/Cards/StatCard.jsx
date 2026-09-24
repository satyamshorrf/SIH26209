import { motion } from "framer-motion";

/**
 * Animated statistic card used on the dashboard and module result panels.
 */
export default function StatCard({
  icon: Icon,
  label,
  value,
  unit,
  accent = "blue",
  delay = 0,
}) {
  const accents = {
    blue: "from-accent-blue/25 to-accent-blue/5 text-accent-blue",
    purple: "from-accent-purple/25 to-accent-purple/5 text-accent-purple",
    cyan: "from-cyan-400/25 to-cyan-400/5 text-cyan-300",
    green: "from-emerald-400/25 to-emerald-400/5 text-emerald-300",
    orange: "from-orange-400/25 to-orange-400/5 text-orange-300",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      className="glass glass-hover rounded-2xl p-4"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            {label}
          </p>
          <p className="mt-2 text-2xl font-bold text-white">
            {value}
            {unit && <span className="ml-1 text-sm text-slate-400">{unit}</span>}
          </p>
        </div>
        {Icon && (
          <div
            className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${
              accents[accent] || accents.blue
            }`}
          >
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
