import { useEffect, useState } from "react";
import { api } from "../api";
import type { Employee, Project } from "../api";
import { Search, UserPlus, MapPin, X, Check, Building, Trash2 } from "lucide-react";

export default function EmployeeDirectory() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  
  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  
  // Pagination
  const [skip, setSkip] = useState(0);
  const limit = 20;
  
  // Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEmp, setNewEmp] = useState({
    employee_code: "",
    name: "",
    email: "",
    department: "Engineering",
    role: "Software Engineer",
    joining_date: new Date().toISOString().split("T")[0],
    project_id: "" as number | "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const isEmpCode = searchTerm.trim().toLowerCase().startsWith("emp-");
      const [empList, projList] = await Promise.all([
        api.getEmployees({
          name: isEmpCode ? undefined : (searchTerm || undefined),
          employee_code: isEmpCode ? searchTerm.trim() : undefined,
          status: statusFilter || undefined,
          project_id: projectFilter || undefined,
          limit,
          skip
        }),
        api.getProjects()
      ]);
      setEmployees(empList);
      setProjects(projList);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load directory data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchTerm, statusFilter, projectFilter, skip]);

  const handleAddEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    try {
      const payload = {
        ...newEmp,
        project_id: newEmp.project_id === "" ? undefined : Number(newEmp.project_id)
      };
      await api.createEmployee(payload);
      setSuccessMsg(`Successfully created employee ${newEmp.name}!`);
      setShowAddForm(false);
      setNewEmp({
        employee_code: "",
        name: "",
        email: "",
        department: "Engineering",
        role: "Software Engineer",
        joining_date: new Date().toISOString().split("T")[0],
        project_id: "",
      });
      setSkip(0); // Reset pagination
      loadData();
    } catch (err: any) {
      setError(err.message || "Failed to create employee");
    }
  };

  const handleAutoAllocate = async (empId: number) => {
    setError("");
    setSuccessMsg("");
    try {
      const alloc = await api.allocateSeat(empId);
      setSuccessMsg(`Allocated Seat ${alloc.seat?.seat_number || "successfully"} to employee.`);
      loadData();
    } catch (err: any) {
      setError(err.message || "Auto-allocation failed.");
    }
  };

  const handleRelease = async (empId: number) => {
    setError("");
    setSuccessMsg("");
    try {
      await api.releaseSeat(empId);
      setSuccessMsg("Released seat allocation.");
      loadData();
    } catch (err: any) {
      setError(err.message || "Release failed.");
    }
  };

  const handleDelete = async (empId: number) => {
    if (!confirm("Are you sure you want to delete this employee?")) return;
    setError("");
    setSuccessMsg("");
    try {
      await api.deleteEmployee(empId);
      setSuccessMsg("Employee deleted.");
      loadData();
    } catch (err: any) {
      setError(err.message || "Deletion failed.");
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top bar controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-xl font-bold text-white">Employee Directory</h3>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-lg shadow-purple-500/10 transition-all self-start"
        >
          <UserPlus size={16} />
          Add Employee
        </button>
      </div>

      {/* Success/Error Notifications */}
      {successMsg && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <Check size={16} />
          {successMsg}
        </div>
      )}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <X size={16} />
          {error}
        </div>
      )}

      {/* Filter panel */}
      <div className="glass-card rounded-2xl p-6 grid grid-cols-1 gap-4 sm:grid-cols-4">
        {/* Search */}
        <div className="relative col-span-1 sm:col-span-2">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
            <Search size={16} />
          </span>
          <input
            type="text"
            placeholder="Search by name, email, or code (e.g. EMP-00001)..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setSkip(0); }}
            className="w-full pl-9 pr-4 py-2.5 glass-input rounded-xl text-sm text-slate-200"
          />
        </div>

        {/* Project Filter */}
        <div>
          <select
            value={projectFilter}
            onChange={(e) => { setProjectFilter(e.target.value === "" ? "" : Number(e.target.value)); setSkip(0); }}
            className="w-full px-3 py-2.5 glass-input rounded-xl text-sm text-slate-300"
          >
            <option value="" className="bg-slate-950">All Projects</option>
            {projects.map((proj) => (
              <option key={proj.id} value={proj.id} className="bg-slate-950">{proj.name}</option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setSkip(0); }}
            className="w-full px-3 py-2.5 glass-input rounded-xl text-sm text-slate-300"
          >
            <option value="" className="bg-slate-950">All Statuses</option>
            <option value="Active" className="bg-slate-950">Active Seated</option>
            <option value="Awaiting Allocation" className="bg-slate-950">Awaiting Allocation</option>
            <option value="Remote" className="bg-slate-950">Remote</option>
          </select>
        </div>
      </div>

      {/* Directory Table */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/40 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-4 px-6">Code</th>
                <th className="py-4 px-6">Name</th>
                <th className="py-4 px-6">Role & Department</th>
                <th className="py-4 px-6">Project</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500">
                    <div className="h-6 w-6 animate-spin rounded-full border-t-2 border-purple-500 mx-auto"></div>
                  </td>
                </tr>
              ) : employees.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500">
                    No employees found matching filters.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-900/20 transition-colors">
                    <td className="py-4 px-6">
                      <span className="font-mono text-xs text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                        {emp.employee_code || `EMP-${emp.id}`}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className="font-semibold text-white">{emp.name}</div>
                      <div className="text-xs text-slate-400">{emp.email}</div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="text-slate-200">{emp.role}</div>
                      <div className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                        <Building size={12} /> {emp.department}
                      </div>
                    </td>
                    <td className="py-4 px-6 text-slate-300">
                      {emp.project ? (
                        <span className="text-purple-400 font-medium">{emp.project.name}</span>
                      ) : (
                        <span className="text-slate-500 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-semibold ${
                        emp.status === "Active" 
                          ? "bg-purple-500/10 text-purple-400 border border-purple-500/20" 
                          : emp.status === "Awaiting Allocation"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-slate-500/10 text-slate-400 border border-slate-700"
                      }`}>
                        {emp.status === "Active" ? "Seated" : emp.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      {emp.status === "Awaiting Allocation" && (
                        <button
                          onClick={() => handleAutoAllocate(emp.id)}
                          className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all inline-flex items-center gap-1"
                        >
                          <MapPin size={12} /> Auto-Allocate
                        </button>
                      )}
                      {emp.status === "Active" && (
                        <button
                          onClick={() => handleRelease(emp.id)}
                          className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all inline-flex items-center gap-1"
                        >
                          Release Seat
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(emp.id)}
                        className="text-slate-500 hover:text-red-400 p-1.5 rounded transition-all inline-flex align-middle"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-900/10">
          <button
            onClick={() => setSkip(Math.max(0, skip - limit))}
            disabled={skip === 0}
            className="px-3.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-semibold text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition-all"
          >
            Previous
          </button>
          <span className="text-xs text-slate-400">
            Showing records {skip + 1} - {skip + employees.length}
          </span>
          <button
            onClick={() => setSkip(skip + limit)}
            disabled={employees.length < limit}
            className="px-3.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-semibold text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition-all"
          >
            Next
          </button>
        </div>
      </div>

      {/* Add Employee Modal Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="glass-card rounded-2xl max-w-md w-full p-6 space-y-4 border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h4 className="text-lg font-bold text-white">Add New Employee</h4>
              <button onClick={() => setShowAddForm(false)} className="text-slate-400 hover:text-white">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAddEmployee} className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Employee Code (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. EMP-00042"
                    value={newEmp.employee_code}
                    onChange={(e) => setNewEmp({ ...newEmp, employee_code: e.target.value })}
                    className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. John Doe"
                    value={newEmp.name}
                    onChange={(e) => setNewEmp({ ...newEmp, name: e.target.value })}
                    className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="e.g. john@ethara.ai"
                  value={newEmp.email}
                  onChange={(e) => setNewEmp({ ...newEmp, email: e.target.value })}
                  className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Department</label>
                  <select
                    value={newEmp.department}
                    onChange={(e) => setNewEmp({ ...newEmp, department: e.target.value })}
                    className="w-full glass-input rounded-xl py-2 px-3 text-slate-300"
                  >
                    <option value="Engineering" className="bg-slate-950">Engineering</option>
                    <option value="Product" className="bg-slate-950">Product</option>
                    <option value="Design" className="bg-slate-950">Design</option>
                    <option value="Marketing" className="bg-slate-950">Marketing</option>
                    <option value="Sales" className="bg-slate-950">Sales</option>
                    <option value="HR" className="bg-slate-950">HR</option>
                    <option value="Finance" className="bg-slate-950">Finance</option>
                    <option value="Operations" className="bg-slate-950">Operations</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Role</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Frontend Dev"
                    value={newEmp.role}
                    onChange={(e) => setNewEmp({ ...newEmp, role: e.target.value })}
                    className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Joining Date</label>
                <input
                  type="date"
                  required
                  value={newEmp.joining_date}
                  onChange={(e) => setNewEmp({ ...newEmp, joining_date: e.target.value })}
                  className="w-full glass-input rounded-xl py-2 px-3 text-slate-300"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Assigned Project (Optional)</label>
                <select
                  value={newEmp.project_id}
                  onChange={(e) => setNewEmp({ ...newEmp, project_id: e.target.value === "" ? "" : Number(e.target.value) })}
                  className="w-full glass-input rounded-xl py-2 px-3 text-slate-300"
                >
                  <option value="" className="bg-slate-950">Unassigned</option>
                  {projects.map((proj) => (
                    <option key={proj.id} value={proj.id} className="bg-slate-950">{proj.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-3 border-t border-slate-800">
                <button
                  type="submit"
                  className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2 px-4 rounded-xl transition-all"
                >
                  Save Employee
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold py-2 px-4 rounded-xl transition-all"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
