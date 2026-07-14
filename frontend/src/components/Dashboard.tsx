import { useEffect, useState, useCallback } from "react";
import { api } from "../api";
import type { DashboardSummary, ProjectUtilization, FloorUtilization } from "../api";
import {
  Users, LayoutGrid, MapPin, AlertCircle, TrendingUp,
  RefreshCw, Clock, Building2, CheckCircle2
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, Legend, Cell, RadialBarChart, RadialBar
} from "recharts";

/* ── helpers ─────────────────────────────────────────── */
function AnimatedNumber({ value, suffix = "" }: { value: number | undefined; suffix?: string }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    if (value === undefined) return;
    let start = 0;
    const end = value;
    if (start === end) { setDisplay(end); return; }
    const duration = 900;
    const step = (end - start) / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setDisplay(end); clearInterval(timer); }
      else { setDisplay(Math.floor(start)); }
    }, 16);
    return () => clearInterval(timer);
  }, [value]);
  return <>{display.toLocaleString()}{suffix}</>;
}



/* ── stat card ───────────────────────────────────────── */
interface StatCardProps {
  label: string;
  value?: number;
  suffix?: string;
  sub: string;
  icon: React.ReactNode;
  iconBg: string;
  cssVars: React.CSSProperties;
  progressPct?: number;
  progressColor: string;
}
function StatCard({ label, value, suffix, sub, icon, iconBg, cssVars, progressPct, progressColor }: StatCardProps) {
  return (
    <div className="glass-card stat-card rounded-2xl p-6" style={cssVars}>
      <div className="flex items-start justify-between mb-1">
        <div className="flex-1 min-w-0">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">{label}</p>
          <h3 className="mt-2 text-[2.1rem] font-extrabold tracking-tight text-white leading-none tabular-nums">
            {value !== undefined ? <AnimatedNumber value={value} suffix={suffix} /> : (
              <span className="skeleton inline-block w-24 h-9 rounded-lg" />
            )}
          </h3>
          <p className="mt-1.5 text-[11.5px] text-slate-500 font-medium">{sub}</p>
        </div>
        <div className={`rounded-xl ${iconBg} p-3 ml-3 shrink-0 shadow-md`}>{icon}</div>
      </div>
      {progressPct !== undefined && (
        <div className="progress-bar-track mt-3">
          <div
            className="progress-bar-fill"
            style={{ width: `${Math.min(progressPct, 100)}%`, background: progressColor }}
          />
        </div>
      )}
    </div>
  );
}


/* ── custom tooltip ──────────────────────────────────── */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card rounded-xl px-4 py-3 text-xs shadow-xl min-w-[130px]">
      <p className="text-slate-300 font-semibold mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.fill || p.color }} className="font-medium">{p.name}</span>
          <span className="text-white font-bold tabular-nums">{p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

const CHART_COLORS = ["#8b5cf6", "#6366f1", "#c084fc", "#ec4899", "#f59e0b"];

/* ═══════════════════════════════════════════════════════
   Dashboard
   ═══════════════════════════════════════════════════════ */
export default function Dashboard() {
  const [summary,  setSummary]  = useState<DashboardSummary | null>(null);
  const [projects, setProjects] = useState<ProjectUtilization[]>([]);
  const [floors,   setFloors]   = useState<FloorUtilization[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [refreshing, setRefreshing]   = useState(false);

  const fetchData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    try {
      const [sumData, projData, floorData] = await Promise.all([
        api.getDashboardSummary(),
        api.getProjectUtilization(),
        api.getFloorUtilization(),
      ]);
      setSummary(sumData);
      setProjects(projData);
      setFloors(floorData);
      setLastRefresh(new Date());
      setError("");
    } catch {
      setError("Failed to load dashboard data. Ensure the backend is running.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  /* ── loading skeleton ─────────────────────────────── */
  if (loading) {
    return (
      <div className="space-y-8 animate-fadeIn">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="glass-card rounded-2xl p-6 space-y-3">
              <div className="skeleton h-3 w-24" />
              <div className="skeleton h-9 w-16" />
              <div className="skeleton h-2 w-full mt-3" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="glass-card rounded-2xl p-6">
            <div className="skeleton h-5 w-40 mb-6" />
            <div className="skeleton h-72 w-full" />
          </div>
          <div className="glass-card rounded-2xl p-6">
            <div className="skeleton h-5 w-48 mb-6" />
            <div className="skeleton h-72 w-full" />
          </div>
        </div>
      </div>
    );
  }

  /* ── error ────────────────────────────────────────── */
  if (error) {
    return (
      <div className="glass-card my-8 flex items-center gap-4 rounded-2xl p-6 border border-red-500/20 bg-red-500/5">
        <AlertCircle size={28} className="text-red-400 shrink-0" />
        <div>
          <p className="font-semibold text-red-300 text-sm">{error}</p>
          <button onClick={() => fetchData()} className="mt-2 text-xs text-purple-400 hover:text-purple-300 underline font-medium">
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const utilPct = summary?.utilization_rate ?? 0;

  /* radial gauge data */
  const gaugeData = [{ name: "Utilization", value: utilPct, fill: "#8b5cf6" }];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* ── Header row ─────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Workspace Overview</h2>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Real-time seat allocation &amp; project analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-500">
              <Clock size={11} className="text-slate-600" />
              {lastRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </span>
          )}
          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-slate-700 transition-all disabled:opacity-50"
          >
            <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {/* ── KPI Stat Cards (5 cards) ───────────────── */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard
          label="Total Employees"
          value={summary?.total_employees}
          sub={`${(summary?.total_employees ?? 0) - (summary?.pending_allocations ?? 0)} active`}
          icon={<Users size={21} className="text-blue-300" />}
          iconBg="bg-blue-500/15"
          cssVars={{ "--card-accent": "linear-gradient(90deg,#3b82f6,#60a5fa)", "--card-glow": "rgba(59,130,246,0.12)", "--card-border-hover": "rgba(59,130,246,0.35)", "--card-shadow": "rgba(59,130,246,0.30)" } as React.CSSProperties}
          progressColor="linear-gradient(90deg,#3b82f6,#60a5fa)"
          progressPct={summary ? (((summary.total_employees - summary.pending_allocations) / summary.total_employees) * 100) : 0}
        />
        <StatCard
          label="Seat Utilization"
          value={summary?.utilization_rate}
          suffix="%"
          sub={`${summary?.occupied_seats ?? 0} of ${summary?.total_seats ?? 0} filled`}
          icon={<TrendingUp size={21} className="text-purple-300" />}
          iconBg="bg-purple-500/15"
          cssVars={{ "--card-accent": "linear-gradient(90deg,#8b5cf6,#a78bfa)", "--card-glow": "rgba(139,92,246,0.14)", "--card-border-hover": "rgba(139,92,246,0.40)", "--card-shadow": "rgba(139,92,246,0.35)" } as React.CSSProperties}
          progressColor="linear-gradient(90deg,#8b5cf6,#a78bfa)"
          progressPct={utilPct}
        />
        <StatCard
          label="Available Seats"
          value={summary?.available_seats}
          sub="Ready for allocation"
          icon={<CheckCircle2 size={21} className="text-emerald-300" />}
          iconBg="bg-emerald-500/15"
          cssVars={{ "--card-accent": "linear-gradient(90deg,#10b981,#34d399)", "--card-glow": "rgba(16,185,129,0.10)", "--card-border-hover": "rgba(16,185,129,0.32)", "--card-shadow": "rgba(16,185,129,0.28)" } as React.CSSProperties}
          progressColor="linear-gradient(90deg,#10b981,#34d399)"
          progressPct={summary ? (summary.available_seats / summary.total_seats) * 100 : 0}
        />
        <StatCard
          label="Reserved Seats"
          value={summary?.reserved_seats}
          sub="Locked / held back"
          icon={<Building2 size={21} className="text-amber-300" />}
          iconBg="bg-amber-500/15"
          cssVars={{ "--card-accent": "linear-gradient(90deg,#f59e0b,#fbbf24)", "--card-glow": "rgba(245,158,11,0.10)", "--card-border-hover": "rgba(245,158,11,0.32)", "--card-shadow": "rgba(245,158,11,0.28)" } as React.CSSProperties}
          progressColor="linear-gradient(90deg,#f59e0b,#fbbf24)"
          progressPct={summary ? (summary.reserved_seats / summary.total_seats) * 100 : 0}
        />
        <StatCard
          label="Pending Desk"
          value={summary?.pending_allocations}
          sub="Awaiting seat assignment"
          icon={<MapPin size={21} className="text-rose-300" />}
          iconBg="bg-rose-500/15"
          cssVars={{ "--card-accent": "linear-gradient(90deg,#f43f5e,#fb7185)", "--card-glow": "rgba(244,63,94,0.10)", "--card-border-hover": "rgba(244,63,94,0.32)", "--card-shadow": "rgba(244,63,94,0.28)" } as React.CSSProperties}
          progressColor="linear-gradient(90deg,#f43f5e,#fb7185)"
          progressPct={summary ? (summary.pending_allocations / summary.total_employees) * 100 : 0}
        />
      </div>


      {/* ── Charts Row ─────────────────────────────── */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Utilization Gauge */}
        <div className="glass-card rounded-2xl p-6 flex flex-col items-center justify-center">
          <h4 className="text-base font-semibold text-white mb-4 self-start flex items-center gap-2">
            <LayoutGrid size={16} className="text-purple-400" />
            Occupancy Rate
          </h4>
          <div className="relative flex items-center justify-center">
            <ResponsiveContainer width={200} height={200}>
              <RadialBarChart
                cx="50%" cy="50%"
                innerRadius="65%" outerRadius="85%"
                startAngle={220} endAngle={-40}
                data={gaugeData}
              >
                <RadialBar
                  dataKey="value"
                  cornerRadius={8}
                  background={{ fill: "rgba(255,255,255,0.04)" }}
                />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-4xl font-extrabold text-white tabular-nums">{utilPct}%</span>
              <span className="text-[11px] text-slate-400 font-medium mt-1">Utilized</span>
            </div>
          </div>
          {/* mini stats row */}
          <div className="grid grid-cols-2 gap-3 w-full mt-4">
            {[
              { label: "Occupied", val: summary?.occupied_seats, color: "text-purple-400" },
              { label: "Available", val: summary?.available_seats, color: "text-emerald-400" },
            ].map(({ label, val, color }) => (
              <div key={label} className="bg-slate-900/50 rounded-xl p-3 text-center border border-slate-800/50">
                <p className={`text-lg font-bold tabular-nums ${color}`}>{val?.toLocaleString()}</p>
                <p className="text-[10px] text-slate-500 font-medium mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Floor Occupancy Stacked Bar */}
        <div className="glass-card rounded-2xl p-6 lg:col-span-2">
          <h4 className="text-base font-semibold text-white mb-5 flex items-center gap-2">
            <Building2 size={16} className="text-indigo-400" />
            Floor-wise Occupancy
          </h4>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={floors} margin={{ top: 8, right: 8, left: -24, bottom: 0 }} barCategoryGap="30%">
                <XAxis
                  dataKey="floor"
                  tickFormatter={v => `Floor ${v}`}
                  tick={{ fill: "#64748b", fontSize: 11, fontWeight: 600 }}
                  axisLine={false} tickLine={false}
                />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  wrapperStyle={{ fontSize: 11, color: "#94a3b8", paddingTop: 12 }}
                  iconType="circle" iconSize={8}
                />
                <Bar dataKey="occupied_seats"  name="Occupied"  stackId="a" fill="#8b5cf6" radius={[0,0,0,0]} />
                <Bar dataKey="available_seats" name="Available" stackId="a" fill="#10b981" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Project Footprint Horizontal Bar ──────── */}
      <div className="glass-card rounded-2xl p-6">
        <h4 className="text-base font-semibold text-white mb-5 flex items-center gap-2">
          <TrendingUp size={16} className="text-pink-400" />
          Project Seat Footprint
          <span className="ml-auto text-[11px] text-slate-500 font-normal">Top 5 projects by seated members</span>
        </h4>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={projects.slice(0, 5)} layout="vertical"
              margin={{ top: 4, right: 16, left: 8, bottom: 0 }} barCategoryGap="25%"
            >
              <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis
                type="category" dataKey="project_name"
                tick={{ fill: "#94a3b8", fontSize: 11, fontWeight: 600 }}
                width={130} axisLine={false} tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="allocated_seats" name="Seated Members" radius={[0, 6, 6, 0]}>
                {projects.slice(0, 5).map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
