import { Loader2 } from "lucide-react";

export default function Loader({ label = "Loading…", className = "" }) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-3 py-10 text-slate-400 ${className}`}
    >
      <Loader2 className="h-8 w-8 animate-spin text-accent-blue" />
      <p className="text-sm">{label}</p>
    </div>
  );
}
