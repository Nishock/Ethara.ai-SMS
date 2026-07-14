import { useEffect, useState } from "react";
import { api } from "../api";
import type { Seat, Employee } from "../api";
import {
  Check, X, Monitor, UserPlus, Info,
  MapPin, User, ChevronRight, Layers
} from "lucide-react";

/* ── helpers ─────────────────────────────────────────── */
function SeatSkeleton() {
  return (
    <>
      {Array.from({ length: 20 }).map((_, i) => (
        <div key={i} className="skeleton h-[52px] w-full rounded-xl" />
      ))}
    </>
  );
}

function Avatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .slice(0, 2)
    .map(w => w[0])
    .join("")
    .toUpperCase();
  const colors = [
    "bg-purple-600", "bg-indigo-600", "bg-blue-600",
    "bg-violet-600", "bg-fuchsia-700",
  ];
  const bg = colors[name.charCodeAt(0) % colors.length];
  return (
    <div className={`h-9 w-9 rounded-full ${bg} flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-md`}>
      {initials}
    </div>
  );
}

/* ── status badge ────────────────────────────────────── */
function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "Available" ? "badge-available" :
    status === "Occupied"  ? "badge-occupied"  :
    "badge-reserved";
  const dot =
    status === "Available" ? "bg-emerald-400" :
    status === "Occupied"  ? "bg-purple-400"  :
    "bg-amber-400";
  return (
    <span className={`badge ${cls}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      {status}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════
   SeatMap
   ═══════════════════════════════════════════════════════ */
export default function SeatMap() {
  const [floor, setFloor] = useState<number>(1);
  const [zone,  setZone]  = useState<string>("A");
  const [bay,   setBay]   = useState<number>(1);

  const [seats,        setSeats]        = useState<Seat[]>([]);
  const [selectedSeat, setSelectedSeat] = useState<Seat | null>(null);

  const [pendingEmployees,  setPendingEmployees]  = useState<Employee[]>([]);
  const [isAllocating,      setIsAllocating]      = useState(false);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | "">("");

  const [loading,        setLoading]        = useState(false);
  const [occupant,       setOccupant]       = useState<Employee | null>(null);
  const [occupantLoading, setOccupantLoading] = useState(false);
  const [msg,   setMsg]   = useState("");
  const [error, setError] = useState("");

  /* ── data loaders ─────────────────────────────────── */
  const loadSeats = async () => {
    setLoading(true);
    try {
      const list = await api.getSeats(floor, zone);
      setSeats(list.filter(s => s.bay === bay));
      setError("");
    } catch { setError("Failed to load seats."); }
    finally  { setLoading(false); }
  };

  const loadPendingEmployees = async () => {
    try {
      const list = await api.getEmployees({ status: "Awaiting Allocation", limit: 200 });
      setPendingEmployees(list);
    } catch { /* silent */ }
  };

  useEffect(() => {
    loadSeats();
    setSelectedSeat(null);
    setIsAllocating(false);
    setMsg(""); setError("");
  }, [floor, zone, bay]);

  useEffect(() => { loadPendingEmployees(); }, []);

  useEffect(() => {
    if (selectedSeat?.status === "Occupied") {
      setOccupantLoading(true);
      setOccupant(null);
      api.getSeatOccupant(selectedSeat.id)
        .then(d => setOccupant(d))
        .catch(() => setError("Failed to fetch occupant."))
        .finally(() => setOccupantLoading(false));
    } else {
      setOccupant(null);
    }
  }, [selectedSeat]);

  /* ── handlers ─────────────────────────────────────── */
  const handleSeatClick = (seat: Seat) => {
    setSelectedSeat(seat);
    setIsAllocating(false);
    setMsg(""); setError("");
  };

  const handleAllocate = async () => {
    if (!selectedSeat || !selectedEmployeeId) return;
    setError(""); setMsg("");
    try {
      await api.allocateSeat(Number(selectedEmployeeId), selectedSeat.id);
      setMsg("✓ Seat allocated successfully!");
      await loadSeats(); await loadPendingEmployees();
      setSelectedSeat(null); setIsAllocating(false);
    } catch (e: any) { setError(e.message || "Allocation failed."); }
  };

  const handleRelease = async (empId: number) => {
    setError(""); setMsg("");
    try {
      await api.releaseSeat(empId);
      setMsg("✓ Seat released successfully!");
      await loadSeats(); await loadPendingEmployees();
      setSelectedSeat(null);
    } catch (e: any) { setError(e.message || "Release failed."); }
  };

  const handleAutoAllocate = async () => {
    if (pendingEmployees.length === 0) { setError("No employees awaiting allocation."); return; }
    setError(""); setMsg("");
    try {
      const emp = pendingEmployees[0];
      const alloc = await api.allocateSeat(emp.id);
      setMsg(`✓ Auto-allocated ${alloc.seat?.seat_number ?? "seat"} to ${emp.name}`);
      await loadSeats(); await loadPendingEmployees();
      setSelectedSeat(null);
    } catch (e: any) { setError(e.message || "Auto-allocation failed."); }
  };

  /* ── seat tile color class ───────────────────────── */
  const tileClass = (seat: Seat) => {
    const isSelected = selectedSeat?.id === seat.id;
    if (isSelected) return "seat-tile selected";
    if (seat.status === "Occupied")  return "seat-tile occupied pulse-active";
    if (seat.status === "Reserved")  return "seat-tile reserved";
    return "seat-tile available";
  };

  /* ─────────────────────────────────────────────────── */
  return (
    <div className="grid grid-cols-1 gap-7 lg:grid-cols-[280px_1fr_300px] animate-fadeIn">

      {/* ── LEFT: Navigator ────────────────────────── */}
      <div className="space-y-5">
        <div className="glass-card rounded-2xl p-6 space-y-6">
          <div className="flex items-center gap-2">
            <Layers size={16} className="text-purple-400" />
            <h3 className="text-base font-bold text-white">Floor Navigator</h3>
          </div>

          {/* Floor */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Floor</label>
            <div className="grid grid-cols-5 gap-1.5">
              {[1,2,3,4,5].map(f => (
                <button key={f} onClick={() => setFloor(f)}
                  className={`py-2.5 text-center rounded-xl text-xs font-bold transition-all ${
                    floor === f
                      ? "bg-purple-600 text-white shadow-lg shadow-purple-500/25"
                      : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
                  }`}
                >F{f}</button>
              ))}
            </div>
          </div>

          {/* Zone */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Zone</label>
            <div className="grid grid-cols-4 gap-1.5">
              {["A","B","C","D"].map(z => (
                <button key={z} onClick={() => setZone(z)}
                  className={`py-2.5 text-center rounded-xl text-xs font-bold transition-all ${
                    zone === z
                      ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/25"
                      : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
                  }`}
                >{z}</button>
              ))}
            </div>
          </div>

          {/* Bay */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Bay</label>
            <div className="grid grid-cols-5 gap-1.5">
              {[1,2,3,4,5].map(b => (
                <button key={b} onClick={() => setBay(b)}
                  className={`py-2.5 text-center rounded-xl text-xs font-bold transition-all ${
                    bay === b
                      ? "bg-violet-600 text-white shadow-lg shadow-violet-500/25"
                      : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
                  }`}
                >B{b}</button>
              ))}
            </div>
          </div>

          {/* divider glow */}
          <div className="divider-glow" />

          {/* Legend */}
          <div className="space-y-2.5">
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest">Seat Status</p>
            {[
              { label: "Available", cls: "badge-available" },
              { label: "Occupied",  cls: "badge-occupied"  },
              { label: "Reserved",  cls: "badge-reserved"  },
            ].map(({ label, cls }) => (
              <div key={label} className="flex items-center gap-2">
                <span className={`badge ${cls} text-[10px]`}>{label}</span>
              </div>
            ))}
          </div>

          {/* Pending count */}
          {pendingEmployees.length > 0 && (
            <div className="bg-amber-500/8 border border-amber-500/20 rounded-xl p-3 text-xs">
              <p className="text-amber-300 font-semibold">{pendingEmployees.length} pending allocation{pendingEmployees.length !== 1 ? "s" : ""}</p>
              <p className="text-slate-500 mt-0.5">Employees awaiting desk assignment</p>
            </div>
          )}

          {/* Auto-allocate */}
          <button
            onClick={handleAutoAllocate}
            className="btn-gradient w-full text-white py-3 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg"
          >
            <UserPlus size={15} />
            Auto-Allocate Next Joiner
          </button>
        </div>
      </div>

      {/* ── CENTRE: Seat Grid ──────────────────────── */}
      <div className="space-y-4">
        {/* breadcrumb header */}
        <div className="glass-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-5">
            <div>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium mb-1">
                <MapPin size={11} />
                <span>Floor {floor}</span>
                <ChevronRight size={11} />
                <span>Zone {zone}</span>
                <ChevronRight size={11} />
                <span>Bay {bay}</span>
              </div>
              <h3 className="text-base font-bold text-white">
                F{floor}-{zone}-B{bay} Seat Grid
              </h3>
            </div>
            <span className="text-[11px] text-slate-500 bg-slate-900 border border-slate-800 py-1.5 px-3 rounded-full font-semibold">
              {seats.length} seats
            </span>
          </div>

          {loading ? (
            <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 gap-2.5">
              <SeatSkeleton />
            </div>
          ) : error && !msg ? (
            <div className="py-16 text-center text-slate-500 text-sm">{error}</div>
          ) : seats.length === 0 ? (
            <div className="py-16 text-center">
              <Monitor size={40} className="mx-auto mb-3 text-slate-700" />
              <p className="text-slate-500 text-sm">No seats found for this location.</p>
            </div>
          ) : (
            <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 gap-2.5 max-h-[480px] overflow-y-auto pr-1">
              {seats.map(seat => (
                <button
                  key={seat.id}
                  onClick={() => handleSeatClick(seat)}
                  className={tileClass(seat)}
                  title={`${seat.seat_number} — ${seat.status}`}
                >
                  <Monitor size={11} className="mb-1 opacity-60" />
                  <span>{seat.seat_number.split("-")[2]}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* notifications */}
        {msg && (
          <div className="bg-emerald-500/8 border border-emerald-500/25 text-emerald-400 px-5 py-3.5 rounded-xl text-sm flex items-center gap-2.5 animate-slideUp font-medium">
            <Check size={16} className="shrink-0" />
            {msg}
          </div>
        )}
        {error && msg === "" && (
          <div className="bg-red-500/8 border border-red-500/25 text-red-400 px-5 py-3.5 rounded-xl text-sm flex items-center gap-2.5 animate-slideUp font-medium">
            <X size={16} className="shrink-0" />
            {error}
          </div>
        )}
      </div>

      {/* ── RIGHT: Seat Detail Panel ───────────────── */}
      <div>
        {selectedSeat ? (
          <div className="glass-card rounded-2xl p-6 space-y-5 animate-scaleIn">
            {/* header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Monitor size={15} className="text-purple-400" />
                Desk Details
              </h3>
              <button onClick={() => setSelectedSeat(null)}
                className="text-slate-500 hover:text-white hover:bg-slate-800 p-1.5 rounded-lg transition-all">
                <X size={15} />
              </button>
            </div>

            {/* meta */}
            <div className="space-y-4">
              <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Seat ID</p>
                <p className="text-xl font-extrabold text-white tracking-tight">{selectedSeat.seat_number}</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { lbl: "Floor", val: `Floor ${selectedSeat.floor}` },
                  { lbl: "Zone",  val: `Zone ${selectedSeat.zone}` },
                  { lbl: "Bay",   val: `Bay ${selectedSeat.bay}` },
                  { lbl: "Status", val: <StatusBadge status={selectedSeat.status} /> },
                ].map(({ lbl, val }) => (
                  <div key={lbl} className="bg-slate-900/50 rounded-xl p-3 border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">{lbl}</p>
                    <div className="text-sm font-semibold text-slate-200">{val}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Occupied panel */}
            {selectedSeat.status === "Occupied" && (
              <div className="space-y-3 pt-3 border-t border-slate-800/80">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                  <Info size={12} className="text-purple-400" /> Occupant
                </h4>
                {occupantLoading ? (
                  <div className="space-y-2">
                    <div className="skeleton h-12 w-full rounded-xl" />
                    <div className="skeleton h-8 w-full rounded-xl" />
                  </div>
                ) : occupant ? (
                  <div className="space-y-3">
                    <div className="flex flex-col gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800/60">
                      <div className="flex items-center gap-3">
                        <Avatar name={occupant.name} />
                        <div className="min-w-0 flex-1">
                          <p className="font-bold text-white text-sm truncate">{occupant.name}</p>
                          <p className="text-[11px] text-slate-400 truncate">{occupant.email}</p>
                          <p className="text-[11px] text-slate-300 font-medium mt-0.5">
                            {occupant.role} · {occupant.department}
                          </p>
                          {occupant.project && (
                            <p className="text-[10px] text-purple-400 font-semibold mt-1">
                              📂 {occupant.project.name}
                            </p>
                          )}
                        </div>
                      </div>
                      {occupant.allocation_date && (
                        <div className="pt-2 border-t border-slate-800/50 flex justify-between items-center text-[10px]">
                          <span className="text-slate-500 uppercase font-semibold">Allocated At</span>
                          <span className="text-slate-300 font-medium font-mono">
                            {new Date(occupant.allocation_date).toLocaleDateString(undefined, {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => handleRelease(occupant.id)}
                      className="w-full bg-red-500/8 hover:bg-red-500/15 text-red-400 border border-red-500/25 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all hover:border-red-500/40"
                    >
                      <X size={13} /> Release Allocation
                    </button>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic py-2">No occupant record found.</p>
                )}
              </div>
            )}

            {/* Available panel */}
            {selectedSeat.status === "Available" && (
              <div className="space-y-3 pt-3 border-t border-slate-800/80">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Assign Desk</h4>
                {isAllocating ? (
                  <div className="space-y-3">
                    <select
                      value={selectedEmployeeId}
                      onChange={e => setSelectedEmployeeId(e.target.value === "" ? "" : Number(e.target.value))}
                      className="w-full glass-input rounded-xl py-2.5 px-3 text-sm text-slate-200"
                    >
                      <option value="" className="bg-slate-950">Choose employee…</option>
                      {pendingEmployees.map(emp => (
                        <option key={emp.id} value={emp.id} className="bg-slate-950">
                          {emp.name} — {emp.department}
                        </option>
                      ))}
                    </select>
                    <div className="flex gap-2">
                      <button
                        onClick={handleAllocate} disabled={!selectedEmployeeId}
                        className="flex-1 btn-gradient text-white py-2.5 rounded-xl text-xs font-bold disabled:opacity-40 disabled:transform-none"
                      >
                        <Check size={13} className="inline mr-1" />Confirm
                      </button>
                      <button
                        onClick={() => setIsAllocating(false)}
                        className="px-4 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-bold border border-slate-800 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => { setIsAllocating(true); loadPendingEmployees(); }}
                    className="w-full bg-emerald-500/8 hover:bg-emerald-500/14 text-emerald-400 border border-emerald-500/25 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all hover:border-emerald-500/40"
                  >
                    <UserPlus size={13} /> Assign Employee to Desk
                  </button>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card rounded-2xl p-8 flex flex-col items-center justify-center text-center h-72 border border-dashed border-slate-800/60">
            <div className="h-14 w-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4">
              <Monitor size={26} className="text-slate-600" />
            </div>
            <p className="text-slate-400 text-sm font-semibold mb-1">No Desk Selected</p>
            <p className="text-slate-600 text-xs max-w-[200px]">Click any seat on the grid to view details or manage assignments.</p>
            <div className="mt-4 flex items-center gap-1.5 text-[11px] text-slate-600">
              <User size={11} />
              <span>{pendingEmployees.length} employees pending</span>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
