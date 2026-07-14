import random
import datetime
from sqlalchemy.orm import Session
from . import models


# ─── Required project names per assignment spec ────────────────────────────────
REQUIRED_PROJECT_NAMES = [
    "Indigo", "Indreed", "Mydreed", "Preed", "Serfy",
    "Oreed", "Bedegreed", "Opreed", "Serry", "Kaary", "Mered",
]

# Additional projects to reach a realistic 50-project portfolio
EXTRA_PROJECT_NAMES = [
    "Apollo", "Artemis", "Athena", "Atlas", "Ares",
    "Chronos", "Calypso", "Cybele", "Ceres", "Chaos",
    "Demeter", "Dionysus", "Daedalus", "Diana", "Draco",
    "Eros", "Erebus", "Echo", "Electra", "Elpis",
    "Fortuna", "Fenrir", "Freya", "Flora", "Faunus",
    "Gaia", "Griffin", "Helios", "Hermes", "Hera",
    "Hyperion", "Hephaestus", "Hercules", "Icarus", "Iris",
    "Janus", "Jupiter", "Jason",
]

MANAGERS = [
    "Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince",
    "Evan Wright", "Fiona Gallagher", "George Clark", "Hannah Abbott",
    "Ivy Chen", "Jack Morrison",
]

DEPARTMENTS = ["Engineering", "Product", "Design", "Marketing", "Sales", "HR", "Finance", "Operations"]
ROLES = {
    "Engineering": ["Software Engineer", "Frontend Engineer", "Backend Engineer", "QA Engineer",
                    "DevOps Engineer", "Engineering Lead", "Staff Engineer"],
    "Product": ["Product Manager", "Associate PM", "Product Owner", "Product Director"],
    "Design": ["UI/UX Designer", "Product Designer", "Visual Designer", "Design Lead"],
    "Marketing": ["Marketing Specialist", "SEO Analyst", "Growth Marketer", "Content Strategist"],
    "Sales": ["Account Executive", "Business Development", "Sales Manager"],
    "HR": ["HR Generalist", "Recruiter", "HR Manager", "HR Business Partner"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Controller", "CFO"],
    "Operations": ["Operations Specialist", "Operations Manager", "COO"],
}

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph",
    "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Aisha", "Rahul", "Priya",
    "Amit", "Neha", "Arjun", "Deepa", "Ravi", "Sunita", "Mohammed",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Kumar", "Sharma", "Patel",
    "Singh", "Nair", "Rao", "Shah", "Mehta", "Gupta", "Verma",
]


def run_seed(db: Session) -> str:
    if db.query(models.Seat).count() > 0:
        return "Database already has seats configuration. Seeding skipped."

    # ── 1. Create Projects ────────────────────────────────────────────────────
    all_project_names = REQUIRED_PROJECT_NAMES + EXTRA_PROJECT_NAMES
    db_projects = []
    for name in all_project_names:
        proj = models.Project(
            name=f"Project {name}",
            description=f"Ethara workspace project — {name} team.",
            manager_name=random.choice(MANAGERS),
            status="Active",
        )
        db.add(proj)
        db_projects.append(proj)
    db.commit()
    for p in db_projects:
        db.refresh(p)

    # ── 2. Create Seats (5 floors × 4 zones × 5 bays × 55 seats = 5,500) ────
    db_seats = []
    floors = [1, 2, 3, 4, 5]
    zones  = ["A", "B", "C", "D"]
    bays   = [1, 2, 3, 4, 5]
    seats_per_bay = 55

    for f in floors:
        for z in zones:
            for b in bays:
                for s_num in range(1, seats_per_bay + 1):
                    seat_str = f"F{f}-{z}{b}-{s_num:02d}"
                    db_seats.append(models.Seat(
                        floor=f, zone=z, bay=b,
                        seat_number=seat_str,
                        status="Available",
                    ))

    db.bulk_save_objects(db_seats)
    db.commit()

    all_seats: list[models.Seat] = db.query(models.Seat).order_by(models.Seat.id).all()

    # ── 3. Mark 100 seats as Reserved and 50 as Maintenance ──────────────────
    reserved_seats = all_seats[:100]
    maintenance_seats = all_seats[100:150]
    for seat in reserved_seats:
        seat.status = "Reserved"
    for seat in maintenance_seats:
        seat.status = "Maintenance"
    db.commit()

    # Remaining available seats (for allocation)
    available_seats = all_seats[150:]   # 5,350 available

    # ── 4. Create 5,000 Employees ─────────────────────────────────────────────
    db_employees = []
    start_date = datetime.date(2024, 1, 1)

    for i in range(1, 5001):
        fn   = random.choice(FIRST_NAMES)
        ln   = random.choice(LAST_NAMES)
        dept = random.choice(DEPARTMENTS)
        role = random.choice(ROLES[dept])
        days_ago     = random.randint(0, 730)
        joining_date = start_date + datetime.timedelta(days=days_ago)
        proj_id      = random.choice(db_projects).id if random.random() < 0.85 else None

        db_employees.append(models.Employee(
            employee_code=f"EMP-{i:05d}",
            name=f"{fn} {ln}",
            email=f"{fn.lower()}.{ln.lower()}.{i}@ethara.ai",
            department=dept,
            role=role,
            joining_date=joining_date,
            status="Awaiting Allocation",
            project_id=proj_id,
        ))

    db.bulk_save_objects(db_employees)
    db.commit()

    all_employees: list[models.Employee] = db.query(models.Employee).order_by(models.Employee.id).all()

    # ── 5. Allocate ~4,000 employees with team adjacency ─────────────────────
    allocated_count = 0
    available_pool = list(available_seats)   # copy to pop from

    # Group employees by project
    project_employee_map: dict[int, list[models.Employee]] = {}
    no_project_employees: list[models.Employee] = []
    for emp in all_employees:
        if emp.project_id:
            project_employee_map.setdefault(emp.project_id, []).append(emp)
        else:
            no_project_employees.append(emp)

    db_allocations = []

    # Allocate project teams floor by floor (adjacency)
    for proj_id, emps in project_employee_map.items():
        proj_idx     = (proj_id - db_projects[0].id) % len(db_projects)
        target_floor = (proj_idx // 10) + 1
        floor_pool   = [s for s in available_pool if s.floor == target_floor]
        if not floor_pool:
            floor_pool = available_pool  # fallback to any floor

        for emp in emps:
            if allocated_count >= 4000:
                break
            if not floor_pool:
                break
            seat = floor_pool.pop(0)
            available_pool.remove(seat)
            seat.status = "Occupied"
            emp.status  = "Active"
            db_allocations.append(models.SeatAllocation(
                employee_id=emp.id,
                seat_id=seat.id,
                project_id=emp.project_id,
                allocated_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365)),
                status="Active",
            ))
            allocated_count += 1
        if allocated_count >= 4000:
            break

    # Allocate no-project employees
    for emp in no_project_employees:
        if allocated_count >= 4000:
            break
        if not available_pool:
            break
        seat = available_pool.pop(0)
        seat.status = "Occupied"
        emp.status  = "Active"
        db_allocations.append(models.SeatAllocation(
            employee_id=emp.id,
            seat_id=seat.id,
            project_id=None,
            allocated_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365)),
            status="Active",
        ))
        allocated_count += 1

    db.bulk_save_objects(db_allocations)
    db.commit()

    # Count final state
    available_final  = db.query(models.Seat).filter(models.Seat.status == "Available").count()
    reserved_final   = db.query(models.Seat).filter(models.Seat.status == "Reserved").count()
    maintenance_final= db.query(models.Seat).filter(models.Seat.status == "Maintenance").count()
    pending_final    = db.query(models.Employee).filter(models.Employee.status == "Awaiting Allocation").count()

    return (
        f"Seeding complete — "
        f"{len(db_projects)} projects | "
        f"{len(db_seats)} seats ({available_final} available, {reserved_final} reserved, {maintenance_final} maintenance) | "
        f"{len(db_employees)} employees ({allocated_count} seated, {pending_final} awaiting allocation)"
    )
