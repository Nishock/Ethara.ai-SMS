from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "/",
    response_model=schemas.EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee",
    description=(
        "Register a new employee in the system. The employee is created with status "
        "`Awaiting Allocation` and will appear in the seat allocation queue. "
        "An optional `project_id` links the employee to a project team, which the "
        "allocation engine uses to group teammates near each other.\n\n"
        "**Validation:** Email must be unique across all employees."
    ),
    response_description="The newly created employee record.",
)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")

    if employee.project_id:
        proj = db.query(models.Project).filter(models.Project.id == employee.project_id).first()
        if not proj:
            raise HTTPException(status_code=400, detail="Project not found")

    data = employee.model_dump()
    # Auto-generate employee_code if not provided
    if not data.get("employee_code"):
        total = db.query(models.Employee).count()
        data["employee_code"] = f"EMP-{total + 1:05d}"

    new_emp = models.Employee(**data)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


@router.get(
    "/",
    response_model=List[schemas.EmployeeResponse],
    summary="List employees",
    description=(
        "Retrieve a paginated list of employees. Supports filtering by:\n"
        "- **name** — case-insensitive substring match\n"
        "- **email** — case-insensitive substring match\n"
        "- **employee_code** — exact or prefix match (e.g., `EMP-00042`)\n"
        "- **department** — exact department name\n"
        "- **project_id** — exact project assignment\n"
        "- **status** — `Active`, `Awaiting Allocation`, or `Inactive`\n\n"
        "Use `skip` and `limit` for pagination (default limit: 50)."
    ),
    response_description="List of employee records matching the filter criteria.",
)
def read_employees(
    name: Optional[str] = None,
    email: Optional[str] = None,
    employee_code: Optional[str] = None,
    department: Optional[str] = None,
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(models.Employee)
    if name:            query = query.filter(models.Employee.name.ilike(f"%{name}%"))
    if email:           query = query.filter(models.Employee.email.ilike(f"%{email}%"))
    if employee_code:   query = query.filter(models.Employee.employee_code.ilike(f"%{employee_code}%"))
    if department:      query = query.filter(models.Employee.department.ilike(f"%{department}%"))
    if project_id:      query = query.filter(models.Employee.project_id == project_id)
    if status:          query = query.filter(models.Employee.status == status)
    return query.offset(skip).limit(limit).all()


@router.get(
    "/{employee_id}",
    response_model=schemas.EmployeeResponse,
    summary="Get employee by ID",
    description="Retrieve a single employee record by their unique integer ID.",
    response_description="The employee record, including their project association if any.",
)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@router.put(
    "/{employee_id}",
    response_model=schemas.EmployeeResponse,
    summary="Update an employee",
    description=(
        "Partially or fully update an employee record. Only fields provided in the "
        "request body will be updated (PATCH semantics). "
        "Email uniqueness is enforced if the email field is changed."
    ),
    response_description="The updated employee record.",
)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != db_employee.email:
        existing = db.query(models.Employee).filter(models.Employee.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    if "project_id" in update_data and update_data["project_id"] is not None:
        proj = db.query(models.Project).filter(models.Project.id == update_data["project_id"]).first()
        if not proj:
            raise HTTPException(status_code=400, detail="Project not found")

    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
    description=(
        "Permanently delete an employee. If the employee has an active seat allocation, "
        "the seat is automatically released back to `Available` status before deletion."
    ),
    response_description="No content on success.",
)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Release active seat allocation if any
    active_alloc = db.query(models.SeatAllocation).filter(
        models.SeatAllocation.employee_id == employee_id,
        models.SeatAllocation.status == "Active",
    ).first()
    if active_alloc:
        seat = db.query(models.Seat).filter(models.Seat.id == active_alloc.seat_id).first()
        if seat:
            seat.status = "Available"
        active_alloc.status = "Released"
        active_alloc.released_at = datetime.now()

    db.delete(db_employee)
    db.commit()
    return None


@router.post(
    "/upload-csv",
    summary="Bulk import employees via CSV",
    description=(
        "Upload a CSV file to bulk-import employees. The file must include the following headers:\n\n"
        "| Column | Required | Description |\n"
        "|---|---|---|\n"
        "| `name` | ✅ | Full name |\n"
        "| `email` | ✅ | Unique email address |\n"
        "| `department` | ✅ | Department name |\n"
        "| `role` | ✅ | Job title / role |\n"
        "| `joining_date` | ✅ | Format: `YYYY-MM-DD` |\n"
        "| `project_name` | ❌ | If provided, auto-creates project if not found |\n\n"
        "Rows with validation errors are skipped and reported in the response `errors` array. "
        "Successfully imported rows are committed atomically."
    ),
    response_description="Import summary with count of successful imports and a list of row-level errors.",
)
def upload_employees_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    csv_file = io.StringIO(content)
    reader = csv.DictReader(csv_file)

    count = 0
    errors = []

    for row_num, row in enumerate(reader, 1):
        try:
            name             = row.get("name")
            email            = row.get("email")
            department       = row.get("department")
            role             = row.get("role")
            joining_date_str = row.get("joining_date")
            project_name     = row.get("project_name")

            if not name or not email or not department or not role or not joining_date_str:
                errors.append(f"Row {row_num}: Missing required fields.")
                continue

            if db.query(models.Employee).filter(models.Employee.email == email).first():
                errors.append(f"Row {row_num}: Email {email} already exists.")
                continue

            try:
                joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date format (use YYYY-MM-DD).")
                continue

            proj_id = None
            if project_name:
                proj = db.query(models.Project).filter(models.Project.name == project_name).first()
                if not proj:
                    proj = models.Project(name=project_name)
                    db.add(proj)
                    db.commit()
                    db.refresh(proj)
                proj_id = proj.id

            db.add(models.Employee(
                name=name, email=email, department=department, role=role,
                joining_date=joining_date, status="Awaiting Allocation", project_id=proj_id,
            ))
            count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: Unexpected error — {str(e)}")

    db.commit()
    return {
        "message": f"Successfully imported {count} employee(s).",
        "imported": count,
        "errors": errors,
        "error_count": len(errors),
    }
