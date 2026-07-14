import { useEffect, useState } from "react";
import { api } from "../api";
import type { Project, Employee } from "../api";
import { Folder, Users, User, MapPin, X, Check, FolderPlus } from "lucide-react";

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProj, setSelectedProj] = useState<Project | null>(null);
  const [teamMembers, setTeamMembers] = useState<Employee[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  
  const [newProj, setNewProj] = useState({
    name: "",
    manager_name: ""
  });

  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const loadProjects = async () => {
    setLoading(true);
    try {
      const list = await api.getProjects();
      setProjects(list);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load projects.");
    } finally {
      setLoading(false);
    }
  };

  const loadProjectDetails = async (project: Project) => {
    setSelectedProj(project);
    setDetailLoading(true);
    try {
      const list = await api.getEmployees({ project_id: project.id, limit: 1000 });
      setTeamMembers(list);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    try {
      const p = await api.createProject(newProj);
      setSuccessMsg(`Project '${p.name}' created successfully!`);
      setShowAddForm(false);
      setNewProj({ name: "", manager_name: "" });
      loadProjects();
    } catch (err: any) {
      setError(err.message || "Failed to create project");
    }
  };

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-3 animate-fadeIn">
      {/* Project list panel */}
      <div className="lg:col-span-1 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Project Teams</h3>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-purple-600/10 hover:bg-purple-600/20 text-purple-400 border border-purple-500/20 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <FolderPlus size={14} /> Add Project
          </button>
        </div>

        {successMsg && (
          <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-3 rounded-xl text-xs flex items-center gap-2">
            <Check size={14} />
            {successMsg}
          </div>
        )}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs flex items-center gap-2">
            <X size={14} />
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-t-2 border-purple-500"></div>
          </div>
        ) : (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {projects.map((proj) => (
              <button
                key={proj.id}
                onClick={() => loadProjectDetails(proj)}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-150 flex items-center justify-between ${
                  selectedProj?.id === proj.id
                    ? "bg-purple-600/15 border-purple-500 text-white"
                    : "bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-900 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${selectedProj?.id === proj.id ? "bg-purple-500/20 text-purple-300" : "bg-slate-800 text-slate-400"}`}>
                    <Folder size={18} />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{proj.name}</p>
                    <p className="text-xs text-slate-400">Manager: {proj.manager_name || "Unassigned"}</p>
                  </div>
                </div>
                <Users size={16} className="text-slate-500" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Team Details / Members */}
      <div className="lg:col-span-2">
        {selectedProj ? (
          <div className="glass-card rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{selectedProj.name}</h3>
                <p className="text-sm text-slate-400 mt-1">
                  Manager: <span className="font-semibold text-slate-300">{selectedProj.manager_name || "None"}</span>
                </p>
              </div>
              <span className="text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 py-1.5 px-3 rounded-full">
                {teamMembers.length} Team Members
              </span>
            </div>

            {detailLoading ? (
              <div className="flex h-48 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-t-2 border-purple-500"></div>
              </div>
            ) : teamMembers.length === 0 ? (
              <p className="text-sm text-slate-500 italic py-8 text-center">No employees assigned to this project.</p>
            ) : (
              <div className="space-y-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Member list</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {teamMembers.map((member) => (
                    <div key={member.id} className="bg-slate-950/60 border border-slate-900 rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
                          <User size={14} />
                        </div>
                        <div>
                          <p className="font-bold text-white text-sm">{member.name}</p>
                          <p className="text-[10px] text-slate-400">{member.role}</p>
                        </div>
                      </div>
                      
                      {member.status === "Active" ? (
                        <div className="flex items-center gap-1.5 text-xs text-purple-400 bg-purple-500/5 px-2.5 py-1 rounded-lg border border-purple-500/10">
                          <MapPin size={12} />
                          <span>Seated</span>
                        </div>
                      ) : (
                        <div className="text-xs text-amber-400 bg-amber-500/5 px-2.5 py-1 rounded-lg border border-amber-500/10">
                          Pending Seat
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card rounded-2xl p-6 text-center text-slate-500 h-[300px] flex flex-col items-center justify-center">
            <Folder size={48} className="mb-2 opacity-35" />
            <p className="text-sm font-medium">Select a project from the panel to view manager details and team members desk allocations.</p>
          </div>
        )}
      </div>

      {/* Add Project Modal Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="glass-card rounded-2xl max-w-md w-full p-6 space-y-4 border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h4 className="text-lg font-bold text-white">Create New Project</h4>
              <button onClick={() => setShowAddForm(false)} className="text-slate-400 hover:text-white">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Project Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Project Apollo"
                  value={newProj.name}
                  onChange={(e) => setNewProj({ ...newProj, name: e.target.value })}
                  className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Manager Name</label>
                <input
                  type="text"
                  placeholder="e.g. Sarah Jenkins"
                  value={newProj.manager_name}
                  onChange={(e) => setNewProj({ ...newProj, manager_name: e.target.value })}
                  className="w-full glass-input rounded-xl py-2 px-3 text-slate-200"
                />
              </div>

              <div className="flex gap-3 pt-3 border-t border-slate-800">
                <button
                  type="submit"
                  className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2 px-4 rounded-xl transition-all"
                >
                  Create
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
