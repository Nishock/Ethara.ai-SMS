import { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard";
import SeatMap from "./components/SeatMap";
import EmployeeDirectory from "./components/EmployeeDirectory";
import ProjectList from "./components/ProjectList";
import AdminPanel from "./components/AdminPanel";
import AIAssistant from "./components/AIAssistant";
import {
  LayoutDashboard, Map, Users, FolderKanban, ShieldCheck,
  Sparkles, Activity, Clock, Wifi
} from "lucide-react";

const TABS = [
  { id: "dashboard", label: "Dashboard",       icon: LayoutDashboard, badge: null },
  { id: "map",       label: "Seat Map",         icon: Map,             badge: null },
  { id: "directory", label: "Employees",        icon: Users,           badge: null },
  { id: "projects",  label: "Projects",         icon: FolderKanban,   badge: null },
  { id: "admin",     label: "Admin",            icon: ShieldCheck,    badge: null },
] as const;

type TabId = typeof TABS[number]["id"];

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [time, setTime]           = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fmtTime = (d: Date) =>
    d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const fmtDate = (d: Date) =>
    d.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });

  return (
    <div className="min-h-screen flex flex-col relative" style={{ backgroundColor: "var(--color-bg-primary)" }}>
      {/* ── Ambient background blobs ─────────────────────────────── */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden z-0">
        <div className="absolute top-[-120px] left-[10%] w-[520px] h-[520px] bg-purple-700/8 rounded-full blur-[130px]" />
        <div className="absolute top-[40%] right-[5%] w-[400px] h-[400px] bg-indigo-700/7 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 left-[35%] w-[500px] h-[300px] bg-violet-800/5 rounded-full blur-[120px]" />
      </div>

      {/* ── Top Header ───────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 glass-card border-b border-white/5 backdrop-blur-xl">
        {/* Gradient accent line */}
        <div className="h-[2px] bg-gradient-to-r from-purple-600 via-indigo-500 to-violet-600" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-[68px] flex items-center justify-between gap-4">
          {/* Logo / Brand */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="relative">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
                <Sparkles size={19} className="text-white" />
              </div>
              {/* Live indicator dot */}
              <span className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full bg-emerald-400 border-2 border-slate-950 animate-live" />
            </div>
            <div>
              <h1 className="font-extrabold text-white text-[15px] leading-none tracking-tight">
                Ethara <span className="gradient-text font-semibold">Workspace</span>
              </h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-0.5 font-semibold">
                Seat &amp; Project Intelligence
              </p>
            </div>
          </div>

          {/* Centre — system status pills */}
          <div className="hidden lg:flex items-center gap-2">
            <span className="badge badge-live gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-live" />
              API Online
            </span>
            <span className="badge" style={{ background: "rgba(99,102,241,0.1)", color: "#818cf8", border: "1px solid rgba(99,102,241,0.25)" }}>
              <Wifi size={10} />
              Real-time
            </span>
            <span className="badge" style={{ background: "rgba(255,255,255,0.05)", color: "#94a3b8", border: "1px solid rgba(255,255,255,0.08)" }}>
              <Activity size={10} />
              v1.0.0
            </span>
          </div>

          {/* Right — clock */}
          <div className="hidden md:flex items-center gap-3 text-xs bg-slate-900/50 border border-slate-800/60 rounded-xl px-4 py-2">
            <Clock size={13} className="text-purple-400 shrink-0" />
            <span className="font-mono tabular-nums text-slate-200 font-semibold tracking-wide">
              {fmtTime(time)}
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400 font-medium">{fmtDate(time)}</span>
          </div>
        </div>
      </header>

      {/* ── Main layout ──────────────────────────────────────────── */}
      <main className="relative z-10 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 flex-1 py-7 space-y-7">
        {/* Navigation Tabs */}
        <nav className="flex overflow-x-auto scrollbar-none gap-1 border-b border-slate-900/80">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              id={`tab-${id}`}
              onClick={() => setActiveTab(id)}
              className={`nav-tab ${activeTab === id ? "active" : ""}`}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div className="min-h-[560px]">
          {activeTab === "dashboard" && <Dashboard />}
          {activeTab === "map"       && <SeatMap />}
          {activeTab === "directory" && <EmployeeDirectory />}
          {activeTab === "projects"  && <ProjectList />}
          {activeTab === "admin"     && <AdminPanel />}
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-slate-900/80 py-4 px-6 mt-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-600 font-medium">
          <span>© 2026 Ethara Workspace Intelligence · Built with FastAPI + React</span>
          <div className="flex items-center gap-4">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer"
              className="hover:text-purple-400 transition-colors">API Docs</a>
            <a href="http://localhost:8000/redoc" target="_blank" rel="noopener noreferrer"
              className="hover:text-purple-400 transition-colors">ReDoc</a>
            <span className="text-slate-700">v1.0.0</span>
          </div>
        </div>
      </footer>

      {/* ── Floating AI Assistant ─────────────────────────────────── */}
      <AIAssistant />
    </div>
  );
}
