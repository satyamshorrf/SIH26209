import { Inbox } from "lucide-react";

export default function EmptyState({
  icon: Icon = Inbox,
  title = "No results yet",
  message = "Upload a dataset and run the analysis to see results here.",
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-700/50 bg-space-800/40 py-12 text-center">
      <Icon className="h-10 w-10 text-slate-500" />
      <p className="font-semibold text-slate-200">{title}</p>
      <p className="max-w-md text-sm text-slate-400">{message}</p>
    </div>
  );
}
