import { motion } from "framer-motion";

const STATUS_LABEL = {
  idle: "Idle",
  uploading: "Uploading dataset…",
  processing: "Running analysis…",
  done: "Complete",
  error: "Error",
};

export default function ProgressBar({ progress = 0, status = "idle" }) {
  if (status === "idle") return null;
  return (
    <div className="mt-4">
      <div className="mb-1 flex justify-between text-xs text-slate-400">
        <span>{STATUS_LABEL[status] || status}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-space-700">
        <motion.div
          className={`h-full rounded-full ${
            status === "error"
              ? "bg-red-500"
              : "bg-gradient-to-r from-accent-blue to-accent-purple"
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>
    </div>
  );
}
