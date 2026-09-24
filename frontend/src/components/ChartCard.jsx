import { motion } from "framer-motion";

/**
 * Titled panel wrapper for charts with a consistent fixed height area.
 */
export default function ChartCard({ title, icon: Icon, height = 280, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="glass rounded-2xl p-4"
    >
      {title && (
        <div className="mb-3 flex items-center gap-2">
          {Icon && <Icon className="h-4 w-4 text-accent-purple" />}
          <h3 className="text-sm font-semibold text-white">{title}</h3>
        </div>
      )}
      <div style={{ height }}>{children}</div>
    </motion.div>
  );
}
