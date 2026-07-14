from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


# ─── Project Schemas ──────────────────────────────────────────────────────────
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = "Active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int

    class Config:
        from_attributes = True


# ─── Employee Schemas ─────────────────────────────────────────────────────────
class EmployeeBase(BaseModel):
    employee_code: Optional[str] = None     # e.g. EMP-00001 (auto-generated if omitted)
    name: str
    email: EmailStr
    department: str
    role: str
    joining_date: date
    status: Optional[str] = "Awaiting Allocation"
    project_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = None
    joining_date: Optional[date] = None
    status: Optional[str] = None
    project_id: Optional[int] = None

class EmployeeResponse(EmployeeBase):
    id: int
    project: Optional[ProjectResponse] = None
    allocation_date: Optional[datetime] = None
    seat_number: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Seat Schemas ─────────────────────────────────────────────────────────────
class SeatBase(BaseModel):
    floor: int
    zone: str
    bay: int
    seat_number: str
    status: Optional[str] = "Available"     # Available | Occupied | Reserved | Maintenance

class SeatCreate(SeatBase):
    pass

class SeatResponse(SeatBase):
    id: int

    class Config:
        from_attributes = True


# ─── Seat Allocation Schemas ──────────────────────────────────────────────────
class SeatAllocationBase(BaseModel):
    employee_id: int
    seat_id: int
    project_id: Optional[int] = None
    allocated_at: datetime
    released_at: Optional[datetime] = None
    status: str

class SeatAllocationCreate(BaseModel):
    employee_id: int
    seat_id: Optional[int] = None           # None → auto-allocation heuristic

class SeatReleaseByBody(BaseModel):
    employee_id: int                        # Body-based release (alias route)

class SeatAllocationResponse(SeatAllocationBase):
    id: int
    employee: Optional[EmployeeResponse] = None
    seat: Optional[SeatResponse] = None

    class Config:
        from_attributes = True


# ─── Dashboard Schemas ────────────────────────────────────────────────────────
class DashboardSummary(BaseModel):
    total_employees: int
    total_seats: int
    occupied_seats: int
    available_seats: int
    reserved_seats: int
    maintenance_seats: int
    utilization_rate: float
    pending_allocations: int

class ProjectUtilization(BaseModel):
    project_id: Optional[int]
    project_name: str
    total_members: int
    allocated_seats: int
    utilization_rate: float

class FloorUtilization(BaseModel):
    floor: int
    total_seats: int
    occupied_seats: int
    available_seats: int
    reserved_seats: int
    maintenance_seats: int
    utilization_rate: float


# ─── AI Query Schemas ─────────────────────────────────────────────────────────
class AIQueryRequest(BaseModel):
    query: str

class AIQueryResponse(BaseModel):
    answer: str
    intent: Optional[str] = None
    data: Optional[dict] = None
