from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, allocation_logic
import csv
import io

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.post(
    "/",
    response_model=schemas.SeatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a seat",
    description=(
        "Add a new seat to the office inventory. The `seat_number` must be globally unique "
        "and should follow the convention `F{floor}-{zone}-{bay}-{number}` (e.g., `F2-B-3-12`), "
        "though any unique string is accepted. New seats default to `Available` status."
    ),
    response_description="The newly created seat record.",
)
def create_seat(seat: schemas.SeatCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Seat).filter(models.Seat.seat_number == seat.seat_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Seat number already exists")

    db_seat = models.Seat(**seat.model_dump())
    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)
    return db_seat


@router.get(
    "/",
    response_model=List[schemas.SeatResponse],
    summary="List seats",
    description=(
        "Retrieve seats with optional filters. Use this endpoint to render the seat grid "
        "for a specific floor/zone/bay combination.\n\n"
        "**Filter parameters:**\n"
        "- `floor` — integer (1–5)\n"
        "- `zone` — letter (A, B, C, D)\n"
        "- `status` — `Available`, `Occupied`, or `Reserved`\n"
        "- `skip` / `limit` — pagination (default limit: 500 to support full floor views)"
    ),
    response_description="List of seat records matching the specified filters.",
)
def read_seats(
    floor: Optional[int] = None,
    zone: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    query = db.query(models.Seat)
    if floor is not None: query = query.filter(models.Seat.floor == floor)
    if zone:              query = query.filter(models.Seat.zone == zone)
    if status:            query = query.filter(models.Seat.status == status)
    return query.offset(skip).limit(limit).all()


@router.get(
    "/available",
    response_model=List[schemas.SeatResponse],
    summary="List all available seats",
    description="Returns every seat currently in `Available` status across all floors and zones.",
    response_description="All available (unoccupied, unreserved) seat records.",
)
def get_available_seats(db: Session = Depends(get_db)):
    return db.query(models.Seat).filter(models.Seat.status == "Available").all()


@router.post(
    "/allocate",
    response_model=schemas.SeatAllocationResponse,
    summary="Allocate a seat to an employee",
    description=(
        "Assign a desk to an employee. Supports two modes:\n\n"
        "1. **Manual allocation** — provide both `employee_id` and `seat_id` to assign a specific desk.\n"
        "2. **Auto allocation** — provide only `employee_id` (omit or null `seat_id`). "
        "The engine will find the best available seat near the employee's project teammates "
        "using the adjacency heuristic: *same bay → same zone → same floor → any available seat*.\n\n"
        "**Concurrency:** The allocation runs inside an atomic DB transaction with row-level "
        "locking to prevent double-booking under concurrent requests."
    ),
    response_description="The seat allocation record with employee and seat details embedded.",
)
def allocate_employee_seat(payload: schemas.SeatAllocationCreate, db: Session = Depends(get_db)):
    try:
        allocation = allocation_logic.allocate_seat(db, payload.employee_id, payload.seat_id)
        return allocation
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")


@router.post(
    "/release/{employee_id}",
    response_model=schemas.SeatAllocationResponse,
    summary="Release an employee's seat (Path parameter)",
    description=(
        "Release the active seat allocation for the given employee by ID in the path. "
        "The seat status is immediately set back to `Available`, "
        "and the employee's status is updated to `Awaiting Allocation`."
    ),
    response_description="The updated (released) allocation record.",
)
def release_employee_seat(employee_id: int, db: Session = Depends(get_db)):
    try:
        allocation = allocation_logic.release_seat(db, employee_id)
        return allocation
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Release failed: {str(e)}")


@router.post(
    "/release",
    response_model=schemas.SeatAllocationResponse,
    summary="Release an employee's seat (JSON body parameter)",
    description=(
        "Release the active seat allocation for the employee specified in the request body "
        "containing `employee_id`. The seat status is updated to `Available`."
    ),
    response_description="The updated (released) allocation record.",
)
def release_employee_seat_body(payload: schemas.SeatReleaseByBody, db: Session = Depends(get_db)):
    try:
        allocation = allocation_logic.release_seat(db, payload.employee_id)
        return allocation
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Release failed: {str(e)}")



@router.post(
    "/upload-csv",
    summary="Bulk import seats via CSV",
    description=(
        "Upload a CSV file to bulk-import seat records. Required column headers:\n\n"
        "| Column | Type | Description |\n"
        "|---|---|---|\n"
        "| `floor` | integer | Floor number (e.g., 1–5) |\n"
        "| `zone` | string | Zone letter (A, B, C, D) — auto-uppercased |\n"
        "| `bay` | integer | Bay number within the zone |\n"
        "| `seat_number` | string | Unique seat identifier |\n\n"
        "All imported seats default to `Available` status. "
        "Rows with duplicate `seat_number` values are skipped and reported in `errors`."
    ),
    response_description="Import summary with count and any per-row error messages.",
)
def upload_seats_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    count = 0
    errors = []

    for row_num, row in enumerate(reader, 1):
        try:
            floor_str   = row.get("floor")
            zone        = row.get("zone")
            bay_str     = row.get("bay")
            seat_number = row.get("seat_number")

            if not floor_str or not zone or not bay_str or not seat_number:
                errors.append(f"Row {row_num}: Missing required fields.")
                continue

            try:
                floor = int(floor_str)
                bay   = int(bay_str)
            except ValueError:
                errors.append(f"Row {row_num}: Floor and Bay must be integers.")
                continue

            if db.query(models.Seat).filter(models.Seat.seat_number == seat_number).first():
                errors.append(f"Row {row_num}: Seat '{seat_number}' already exists.")
                continue

            db.add(models.Seat(floor=floor, zone=zone.upper(), bay=bay, seat_number=seat_number, status="Available"))
            count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: Unexpected error — {str(e)}")

    db.commit()
    return {
        "message": f"Successfully imported {count} seat(s).",
        "imported": count,
        "errors": errors,
        "error_count": len(errors),
    }


@router.get(
    "/{seat_id}/occupant",
    response_model=Optional[schemas.EmployeeResponse],
    summary="Get seat occupant",
    description=(
        "Retrieve the employee currently occupying the specified seat. "
        "Returns `null` if the seat has no active allocation (e.g., it was seeded in bulk "
        "without a linked employee record)."
    ),
    response_description="The occupying employee record, or null if unoccupied.",
)
def get_seat_occupant_endpoint(seat_id: int, db: Session = Depends(get_db)):
    allocation = db.query(models.SeatAllocation).filter(
        models.SeatAllocation.seat_id == seat_id,
        models.SeatAllocation.status == "Active",
    ).first()
    if not allocation:
        return None
    return allocation.employee
