const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (typeof window !== "undefined" && window.location.hostname === "localhost" ? "http://localhost:8000" : "");


export interface Project {
  id: number;
  name: string;
  manager_name?: string;
}

export interface Employee {
  id: number;
  employee_code?: string;
  name: string;
  email: string;
  department: string;
  role: string;
  joining_date: string;
  status: string;
  project_id?: number;
  project?: Project;
  allocation_date?: string;
  seat_number?: string;
}

export interface Seat {
  id: number;
  floor: number;
  zone: string;
  bay: number;
  seat_number: string;
  status: string;
}

export interface SeatAllocation {
  id: number;
  employee_id: number;
  seat_id: number;
  project_id?: number;
  allocated_at: string;
  released_at?: string;
  status: string;
  employee?: Employee;
  seat?: Seat;
}

export interface DashboardSummary {
  total_employees: number;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats: number;
  maintenance_seats?: number;
  utilization_rate: number;
  pending_allocations: number;
}

export interface ProjectUtilization {
  project_id: number | null;
  project_name: string;
  total_members: number;
  allocated_seats: number;
  utilization_rate: number;
}

export interface FloorUtilization {
  floor: number;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats?: number;
  maintenance_seats?: number;
  utilization_rate: number;
}

export interface AIQueryResponse {
  answer: string;
  intent?: string;
  data?: any;
}

export const api = {
  // Employees
  async getEmployees(params?: { name?: string; status?: string; project_id?: number; employee_code?: string; limit?: number; skip?: number }): Promise<Employee[]> {
    const query = new URLSearchParams();
    if (params?.name) query.append("name", params.name);
    if (params?.status) query.append("status", params.status);
    if (params?.project_id) query.append("project_id", params.project_id.toString());
    if (params?.employee_code) query.append("employee_code", params.employee_code);
    if (params?.limit) query.append("limit", params.limit.toString());
    if (params?.skip) query.append("skip", params.skip.toString());
    
    const res = await fetch(`${API_BASE_URL}/employees/?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch employees");
    return res.json();
  },


  async createEmployee(data: Partial<Employee>): Promise<Employee> {
    const res = await fetch(`${API_BASE_URL}/employees/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to create employee");
    }
    return res.json();
  },

  async deleteEmployee(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/employees/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete employee");
  },

  async uploadEmployeesCSV(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/employees/upload-csv`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload CSV");
    return res.json();
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE_URL}/projects/`);
    if (!res.ok) throw new Error("Failed to fetch projects");
    return res.json();
  },

  async createProject(data: Partial<Project>): Promise<Project> {
    const res = await fetch(`${API_BASE_URL}/projects/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to create project");
    }
    return res.json();
  },

  async getProjectEmployees(projectId: number): Promise<Employee[]> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/employees`);
    if (!res.ok) throw new Error("Failed to fetch project employees");
    return res.json();
  },


  // Seats
  async getSeats(floor?: number, zone?: string, status?: string): Promise<Seat[]> {
    const query = new URLSearchParams();
    if (floor !== undefined) query.append("floor", floor.toString());
    if (zone) query.append("zone", zone);
    if (status) query.append("status", status);
    
    const res = await fetch(`${API_BASE_URL}/seats/?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch seats");
    return res.json();
  },

  async uploadSeatsCSV(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/seats/upload-csv`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload CSV");
    return res.json();
  },

  // Allocations
  async allocateSeat(employeeId: number, seatId?: number): Promise<SeatAllocation> {
    const body: Record<string, number> = { employee_id: employeeId };
    if (seatId !== undefined) body.seat_id = seatId;
    const res = await fetch(`${API_BASE_URL}/seats/allocate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Seat allocation failed");
    }
    return res.json();
  },


  async releaseSeat(employeeId: number): Promise<SeatAllocation> {
    const res = await fetch(`${API_BASE_URL}/seats/release/${employeeId}`, {
      method: "POST",
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Seat release failed");
    }
    return res.json();
  },

  async getSeatOccupant(seatId: number): Promise<Employee | null> {
    const res = await fetch(`${API_BASE_URL}/seats/${seatId}/occupant`);
    if (!res.ok) throw new Error("Failed to fetch seat occupant");
    return res.json();
  },

  // Dashboard
  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE_URL}/dashboard/summary`);
    if (!res.ok) throw new Error("Failed to fetch summary");
    return res.json();
  },

  async getProjectUtilization(): Promise<ProjectUtilization[]> {
    const res = await fetch(`${API_BASE_URL}/dashboard/project-utilization`);
    if (!res.ok) throw new Error("Failed to fetch project utilization");
    return res.json();
  },

  async getFloorUtilization(): Promise<FloorUtilization[]> {
    const res = await fetch(`${API_BASE_URL}/dashboard/floor-utilization`);
    if (!res.ok) throw new Error("Failed to fetch floor utilization");
    return res.json();
  },

  // AI Assistant
  async queryAI(query: string): Promise<AIQueryResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error("AI query failed");
    return res.json();
  },
};
