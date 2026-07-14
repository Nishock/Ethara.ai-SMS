from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    manager_name = Column(String, nullable=True)
    status = Column(String, default="Active", nullable=False)  # Active, Completed, On Hold

    employees = relationship("Employee", back_populates="project")
    allocations = relationship("SeatAllocation", back_populates="project")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=True)  # e.g. EMP-00001
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    joining_date = Column(Date, nullable=False)
    status = Column(String, default="Awaiting Allocation", nullable=False)
    # Status: Active | Awaiting Allocation | Inactive
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    project = relationship("Project", back_populates="employees")
    allocations = relationship("SeatAllocation", back_populates="employee")

    @property
    def allocation_date(self):
        active = [a for a in self.allocations if a.status == "Active"]
        return active[0].allocated_at if active else None

    @property
    def seat_number(self):
        active = [a for a in self.allocations if a.status == "Active"]
        return active[0].seat.seat_number if active and active[0].seat else None



class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    floor = Column(Integer, index=True, nullable=False)
    zone = Column(String, index=True, nullable=False)
    bay = Column(Integer, index=True, nullable=False)
    seat_number = Column(String, unique=True, index=True, nullable=False)  # e.g. F1-A1-01
    status = Column(String, default="Available", nullable=False)
    # Status: Available | Occupied | Reserved | Maintenance

    allocations = relationship("SeatAllocation", back_populates="seat")


class SeatAllocation(Base):
    __tablename__ = "seat_allocations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    allocated_at = Column(DateTime, default=func.now(), nullable=False)
    released_at = Column(DateTime, nullable=True)
    status = Column(String, default="Active", nullable=False)  # Active | Released

    employee = relationship("Employee", back_populates="allocations")
    seat = relationship("Seat", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")


# Partial Unique Indexes: one active seat per employee, one active employee per seat
Index(
    "idx_active_employee_allocation",
    SeatAllocation.employee_id,
    unique=True,
    sqlite_where=(SeatAllocation.status == 'Active'),
    postgresql_where=(SeatAllocation.status == 'Active'),
)

Index(
    "idx_active_seat_allocation",
    SeatAllocation.seat_id,
    unique=True,
    sqlite_where=(SeatAllocation.status == 'Active'),
    postgresql_where=(SeatAllocation.status == 'Active'),
)
