import { motion } from "framer-motion";

/**
 * Generic panel wrapper for a section of module results.
 */
export default function ResultCard({ title, icon: Icon, action, children, className = "" }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`glass rounded-2xl p-4 md:p-5 ${className}`}
    >
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="h-5 w-5 text-accent-blue" />}
            {title && (
              <h3 className="text-sm font-semibold text-white md:text-base">
                {title}
              </h3>
            )}
          </div>
          {action}
        </div>
      )}
      {children}
    </motion.section>
  );
}
