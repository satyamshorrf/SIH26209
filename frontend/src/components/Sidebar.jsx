import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Snowflake,
  Boxes,
  Rocket,
  Route as RouteIcon,
  BrainCircuit,
  FileBarChart,
  Settings as SettingsIcon,
  Moon,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/ice-detection", label: "Ice Detection", icon: Snowflake },
  { to: "/ice-volume", label: "Ice Volume", icon: Boxes },
  { to: "/landing-site", label: "Safe Landing Site", icon: Rocket },
  { to: "/path-planning", label: "Path Planning", icon: RouteIcon },
  { to: "/ai-confidence", label: "AI Confidence", icon: BrainCircuit },
  { to: "/results", label: "Results", icon: FileBarChart },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function Sidebar({ collapsed }) {
  return (
    <aside
      className={`glass sticky top-0 hidden h-screen shrink-0 flex-col border-r border-slate-700/40 p-3 transition-all duration-300 md:flex ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      <div className="mb-6 flex items-center gap-3 px-2 py-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple shadow-lg">
          <Moon className="h-6 w-6 text-white" />
        </div>
        {!collapsed && (
          <div className="leading-tight">
            <p className="text-sm font-semibold text-white">Lunar AI</p>
            <p className="text-xs text-slate-400">Ice Detection System</p>
          </div>
        )}
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-accent-blue/20 text-white ring-1 ring-accent-blue/40"
                  : "text-slate-400 hover:bg-slate-700/30 hover:text-white"
              }`
            }
            title={collapsed ? label : undefined}
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="mt-4 rounded-xl border border-slate-700/40 bg-space-700/40 p-3 text-xs text-slate-400">
          <p className="font-semibold text-slate-200">Smart India Hackathon 2026</p>
          <p>PS ID: SIH26209</p>
          <p className="mt-1">Chandrayaan-2 DFSAR / OHRC</p>
        </div>
      )}
    </aside>
  );
}
