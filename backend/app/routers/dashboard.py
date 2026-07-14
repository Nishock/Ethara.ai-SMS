from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, seed_helper

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=schemas.DashboardSummary,
    summary="Workspace summary KPIs",
    description=(
        "Returns a single aggregated snapshot of the current workspace state. "
        "Used by the frontend dashboard to populate the five KPI stat cards.\n\n"
        "**Metrics returned:**\n"
        "- `total_employees` — all registered employees\n"
        "- `total_seats` — all seats in the inventory\n"
        "- `occupied_seats` — seats with status `Occupied`\n"
        "- `available_seats` — seats with status `Available`\n"
        "- `reserved_seats` — seats with status `Reserved`\n"
        "- `utilization_rate` — `(occupied / total) × 100`, rounded to 2 decimal places\n"
        "- `pending_allocations` — employees with status `Awaiting Allocation`"
    ),
    response_description="Aggregated workspace KPIs.",
)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_employees  = db.query(models.Employee).count()
    total_seats      = db.query(models.Seat).count()
    occupied_seats   = db.query(models.Seat).filter(models.Seat.status == "Occupied").count()
    available_seats  = db.query(models.Seat).filter(models.Seat.status == "Available").count()
    reserved_seats   = db.query(models.Seat).filter(models.Seat.status == "Reserved").count()
    maintenance_seats= db.query(models.Seat).filter(models.Seat.status == "Maintenance").count()
    pending          = db.query(models.Employee).filter(models.Employee.status == "Awaiting Allocation").count()

    utilization_rate = (occupied_seats / total_seats * 100) if total_seats > 0 else 0.0

    return {
        "total_employees":   total_employees,
        "total_seats":       total_seats,
        "occupied_seats":    occupied_seats,
        "available_seats":   available_seats,
        "reserved_seats":    reserved_seats,
        "maintenance_seats": maintenance_seats,
        "utilization_rate":  round(utilization_rate, 2),
        "pending_allocations": pending,
    }


@router.get(
    "/project-utilization",
    response_model=List[schemas.ProjectUtilization],
    summary="Project seat utilization",
    description=(
        "Returns seat allocation statistics broken down by project. "
        "Sorted by `total_members` descending so the largest projects appear first. "
        "Includes a special `No Project` group for employees not assigned to any project.\n\n"
        "Used by the frontend to render the **Project Seat Footprint** horizontal bar chart."
    ),
    response_description="List of per-project utilization records, sorted by team size descending.",
)
def get_project_utilization(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    results = []

    no_proj_members   = db.query(models.Employee).filter(models.Employee.project_id == None).count()
    no_proj_allocated = db.query(models.SeatAllocation).filter(
        models.SeatAllocation.project_id == None,
        models.SeatAllocation.status == "Active",
    ).count()

    if no_proj_members > 0:
        results.append({
            "project_id":      None,
            "project_name":    "No Project",
            "total_members":   no_proj_members,
            "allocated_seats": no_proj_allocated,
            "utilization_rate": round((no_proj_allocated / no_proj_members * 100), 2) if no_proj_members > 0 else 0.0,
        })

    for proj in projects:
        total_members   = db.query(models.Employee).filter(models.Employee.project_id == proj.id).count()
        allocated_seats = db.query(models.SeatAllocation).filter(
            models.SeatAllocation.project_id == proj.id,
            models.SeatAllocation.status == "Active",
        ).count()

        results.append({
            "project_id":      proj.id,
            "project_name":    proj.name,
            "total_members":   total_members,
            "allocated_seats": allocated_seats,
            "utilization_rate": round((allocated_seats / total_members * 100) if total_members > 0 else 0.0, 2),
        })

    results.sort(key=lambda x: x["total_members"], reverse=True)
    return results


@router.get(
    "/floor-utilization",
    response_model=List[schemas.FloorUtilization],
    summary="Floor-wise seat utilization",
    description=(
        "Returns seat occupancy metrics grouped by floor number, sorted ascending by floor. "
        "Used by the frontend to render the **Floor-wise Occupancy** stacked bar chart.\n\n"
        "Each entry includes `total_seats`, `occupied_seats`, `available_seats`, and "
        "a computed `utilization_rate` percentage."
    ),
    response_description="List of per-floor utilization records, sorted by floor number ascending.",
)
def get_floor_utilization(db: Session = Depends(get_db)):
    floors = db.query(models.Seat.floor).distinct().all()
    results = []

    for f in floors:
        floor_num      = f[0]
        total_seats    = db.query(models.Seat).filter(models.Seat.floor == floor_num).count()
        occupied_seats = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Occupied").count()
        available_seats = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Available").count()
        reserved_seats = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Reserved").count()
        maintenance_seats = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Maintenance").count()

        results.append({
            "floor":           floor_num,
            "total_seats":     total_seats,
            "occupied_seats":  occupied_seats,
            "available_seats": available_seats,
            "reserved_seats":  reserved_seats,
            "maintenance_seats": maintenance_seats,
            "utilization_rate": round((occupied_seats / total_seats * 100) if total_seats > 0 else 0.0, 2),
        })

    results.sort(key=lambda x: x["floor"])
    return results



@router.post(
    "/seed",
    summary="Seed database with benchmark data",
    description=(
        "Populate the database with a large-scale benchmark dataset for testing and demonstration:\n\n"
        "- **5,000 employees** across multiple departments and projects\n"
        "- **5,500 seats** across 5 floors, 4 zones, 5 bays\n"
        "- **4,000 active seat allocations** with team adjacency grouping\n\n"
        "⚠️ This endpoint is **idempotent** — running it multiple times will not create duplicates "
        "(existing employees and seats are skipped). "
        "Useful for demonstrating the system under realistic load."
    ),
    response_description="Success message confirming the seeding operation.",
)
def seed_database_endpoint(db: Session = Depends(get_db)):
    try:
        msg = seed_helper.run_seed(db)
        return {"message": msg, "status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}",
        )
