import { Play, Loader2, RotateCcw } from "lucide-react";

export default function RunButton({ onRun, onReset, isBusy, disabled, label = "Run Analysis" }) {
  return (
    <div className="mt-4 flex items-center gap-3">
      <button
        onClick={onRun}
        disabled={disabled || isBusy}
        className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-accent-blue to-accent-purple px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isBusy ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Play className="h-4 w-4" />
        )}
        {isBusy ? "Processing…" : label}
      </button>
      {onReset && (
        <button
          onClick={onReset}
          disabled={isBusy}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-600/60 px-3 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-slate-700/40 disabled:opacity-50"
          title="Reset"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
