import { useState } from "react";
import { api } from "../api";
import { Upload, Database, Check, X } from "lucide-react";

export default function AdminPanel() {
  const [empFile, setEmpFile] = useState<File | null>(null);
  const [seatFile, setSeatFile] = useState<File | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [seedLoading, setSeedLoading] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const handleEmpUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!empFile) return;
    setLoading(true);
    setMsg("");
    setError("");
    try {
      const res = await api.uploadEmployeesCSV(empFile);
      setMsg(res.message);
      if (res.errors && res.errors.length > 0) {
        setError(`Errors encountered in some rows:\n${res.errors.slice(0, 5).join("\n")}`);
      }
      setEmpFile(null);
    } catch (err: any) {
      setError(err.message || "Failed to upload employee CSV");
    } finally {
      setLoading(false);
    }
  };

  const handleSeatUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!seatFile) return;
    setLoading(true);
    setMsg("");
    setError("");
    try {
      const res = await api.uploadSeatsCSV(seatFile);
      setMsg(res.message);
      if (res.errors && res.errors.length > 0) {
        setError(`Errors encountered in some rows:\n${res.errors.slice(0, 5).join("\n")}`);
      }
      setSeatFile(null);
    } catch (err: any) {
      setError(err.message || "Failed to upload seat CSV");
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDatabase = async () => {
    if (!confirm("Are you sure you want to seed the database? This will generate 5,000 employees and 5,500 seats if not already seeded.")) return;
    setSeedLoading(true);
    setMsg("");
    setError("");
    try {
      const res = await fetch("http://localhost:8000/dashboard/seed", { method: "POST" });
      if (!res.ok) throw new Error("Database seeding failed");
      const data = await res.json();
      setMsg(data.message);
    } catch (err: any) {
      setError(err.message || "Database seeding failed.");
    } finally {
      setSeedLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-white">System Admin Control</h3>
      </div>

      {msg && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-4 rounded-xl text-sm flex items-center gap-2 whitespace-pre-line">
          <Check size={16} />
          {msg}
        </div>
      )}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl text-sm flex items-center gap-2 whitespace-pre-line">
          <X size={16} />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Bulk Employees Upload */}
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <h4 className="font-semibold text-white flex items-center gap-2">
            <Upload size={18} className="text-purple-400" /> Bulk Import Employees
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upload a CSV file containing employee records to import in bulk.
          </p>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-900 text-[11px] text-slate-400 space-y-1">
            <p className="font-semibold text-slate-300">Expected CSV Headers:</p>
            <p><code>name</code>, <code>email</code>, <code>department</code>, <code>role</code>, <code>joining_date</code>, <code>project_name</code></p>
            <p className="text-slate-500">Date Format: YYYY-MM-DD</p>
          </div>

          <form onSubmit={handleEmpUpload} className="space-y-4">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setEmpFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-900 file:text-slate-300 hover:file:bg-slate-800 cursor-pointer"
            />
            <button
              type="submit"
              disabled={loading || !empFile}
              className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-xl text-xs transition-all"
            >
              {loading ? "Importing..." : "Upload Employees CSV"}
            </button>
          </form>
        </div>

        {/* Bulk Seats Upload */}
        <div className="glass-card rounded-2xl p-6 space-y-4">
          <h4 className="font-semibold text-white flex items-center gap-2">
            <Upload size={18} className="text-purple-400" /> Bulk Import Seats
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upload a CSV file containing seats configurations to configure floor plans.
          </p>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-900 text-[11px] text-slate-400 space-y-1">
            <p className="font-semibold text-slate-300">Expected CSV Headers:</p>
            <p><code>floor</code>, <code>zone</code>, <code>bay</code>, <code>seat_number</code></p>
            <p className="text-slate-500">Floor & Bay must be integers. Zone: A, B, C, D</p>
          </div>

          <form onSubmit={handleSeatUpload} className="space-y-4">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSeatFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-900 file:text-slate-300 hover:file:bg-slate-800 cursor-pointer"
            />
            <button
              type="submit"
              disabled={loading || !seatFile}
              className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-xl text-xs transition-all"
            >
              {loading ? "Importing..." : "Upload Seats CSV"}
            </button>
          </form>
        </div>
      </div>

      {/* Database Seeding Controls */}
      <div className="glass-card rounded-2xl p-6 space-y-6">
        <div className="flex items-start gap-4">
          <div className="bg-purple-500/10 p-3 rounded-xl text-purple-400 shrink-0">
            <Database size={24} />
          </div>
          <div className="space-y-1">
            <h4 className="font-semibold text-white">Scale Seeding / Benchmark Data</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Populate the database with a scaling simulation (5,000 employees, 5,500 seats across 5 floors, and 4,000 active allocations).
              This action tests index query performances, dashboard chart aggregations, and layout load rates.
            </p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 items-center pt-2">
          <button
            onClick={handleSeedDatabase}
            disabled={seedLoading}
            className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white py-3 px-6 rounded-xl text-xs font-semibold shadow-lg shadow-purple-500/15 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
          >
            <Database size={16} />
            {seedLoading ? "Seeding Database..." : "Run Database Scale Seeding"}
          </button>
          
          <span className="text-[11px] text-slate-500 italic">
            This will take approximately 1-3 seconds using bulk save.
          </span>
        </div>
      </div>
    </div>
  );
}
