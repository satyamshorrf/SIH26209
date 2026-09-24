import { motion } from "framer-motion";

export default function PageHeader({ icon: Icon, title, subtitle }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-6 flex items-center gap-4"
    >
      {Icon && (
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-blue/30 to-accent-purple/30 ring-1 ring-slate-700/50">
          <Icon className="h-6 w-6 text-accent-blue" />
        </div>
      )}
      <div>
        <h2 className="text-xl font-bold text-white md:text-2xl">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
      </div>
    </motion.div>
  );
}
