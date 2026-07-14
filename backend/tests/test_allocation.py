import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models, schemas, allocation_logic
import datetime

# Create an in-memory SQLite engine for isolated testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_seat_allocation_basics(db_session):
    # 1. Create a seat
    seat = models.Seat(floor=1, zone="A", bay=1, seat_number="F1-A1-01", status="Available")
    db_session.add(seat)
    db_session.commit()

    # 2. Create an employee
    employee = models.Employee(
        name="John Doe",
        email="john.doe@ethara.ai",
        department="Engineering",
        role="Engineer",
        joining_date=datetime.date.today(),
        status="Awaiting Allocation"
    )
    db_session.add(employee)
    db_session.commit()

    # 3. Perform allocation
    alloc = allocation_logic.allocate_seat(db_session, employee.id, seat.id)
    
    # Assertions
    assert alloc.status == "Active"
    assert alloc.employee_id == employee.id
    assert alloc.seat_id == seat.id
    assert seat.status == "Occupied"
    assert employee.status == "Active"

def test_seat_allocation_fails_duplicate(db_session):
    seat = models.Seat(floor=1, zone="A", bay=1, seat_number="F1-A1-01", status="Available")
    employee1 = models.Employee(
        name="User One", email="one@ethara.ai", department="Sales", role="Rep", 
        joining_date=datetime.date.today(), status="Awaiting Allocation"
    )
    employee2 = models.Employee(
        name="User Two", email="two@ethara.ai", department="Sales", role="Rep", 
        joining_date=datetime.date.today(), status="Awaiting Allocation"
    )
    db_session.add_all([seat, employee1, employee2])
    db_session.commit()

    # Allocate to employee1
    allocation_logic.allocate_seat(db_session, employee1.id, seat.id)

    # Attempt to allocate same seat to employee2 (should fail)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        allocation_logic.allocate_seat(db_session, employee2.id, seat.id)
    assert exc_info.value.status_code == 400
    assert "is currently Occupied" in exc_info.value.detail

def test_auto_preferred_seat_logic(db_session):
    # Setup project
    project = models.Project(name="Project Ares")
    db_session.add(project)
    db_session.commit()

    # Create team member already sitting at F2-B1-05
    emp_seated = models.Employee(
        name="Seated Guy", email="seated@ethara.ai", department="Product", role="PM",
        joining_date=datetime.date.today(), status="Active", project_id=project.id
    )
    seat_occupied = models.Seat(floor=2, zone="B", bay=1, seat_number="F2-B1-05", status="Occupied")
    db_session.add_all([emp_seated, seat_occupied])
    db_session.commit()

    # Record active allocation
    alloc_active = models.SeatAllocation(
        employee_id=emp_seated.id, seat_id=seat_occupied.id, project_id=project.id, status="Active"
    )
    db_session.add(alloc_active)
    db_session.commit()

    # Create candidate seats (some in same floor/zone/bay, some other floor)
    seat_other_floor = models.Seat(floor=1, zone="A", bay=1, seat_number="F1-A1-01", status="Available")
    seat_same_bay = models.Seat(floor=2, zone="B", bay=1, seat_number="F2-B1-06", status="Available")
    seat_same_zone_diff_bay = models.Seat(floor=2, zone="B", bay=2, seat_number="F2-B2-01", status="Available")
    
    db_session.add_all([seat_other_floor, seat_same_bay, seat_same_zone_diff_bay])
    db_session.commit()

    # Create new joiner on the same project
    new_joiner = models.Employee(
        name="New Joiner", email="joiner@ethara.ai", department="Product", role="PM",
        joining_date=datetime.date.today(), status="Awaiting Allocation", project_id=project.id
    )
    db_session.add(new_joiner)
    db_session.commit()

    # Run auto-allocation (seat_id=None)
    alloc = allocation_logic.allocate_seat(db_session, new_joiner.id, seat_id=None)

    # New joiner should sit adjacent (same bay F2-B1-06)
    assert alloc.seat_id == seat_same_bay.id
    assert seat_same_bay.status == "Occupied"

def test_release_seat(db_session):
    seat = models.Seat(floor=3, zone="C", bay=2, seat_number="F3-C2-11", status="Occupied")
    employee = models.Employee(
        name="Tester", email="test@ethara.ai", department="HR", role="Recruiter",
        joining_date=datetime.date.today(), status="Active"
    )
    db_session.add_all([seat, employee])
    db_session.commit()

    alloc = models.SeatAllocation(
        employee_id=employee.id, seat_id=seat.id, status="Active"
    )
    db_session.add(alloc)
    db_session.commit()

    # Release it
    released_alloc = allocation_logic.release_seat(db_session, employee.id)

    assert released_alloc.status == "Released"
    assert released_alloc.released_at is not None
    assert seat.status == "Available"
    assert employee.status == "Awaiting Allocation"
