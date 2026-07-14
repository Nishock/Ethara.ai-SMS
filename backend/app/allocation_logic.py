from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from fastapi import HTTPException, status
import datetime

def find_preferred_seat(db: Session, employee: models.Employee) -> models.Seat:
    """
    Finds the best seat for an employee based on their project/department peers.
    Rules:
    1. Prefer seats in the same floor, zone, and bay as other project team members.
    2. If no seats in the same bay, prefer the same floor and zone.
    3. If no seats in the same zone, look at other zones on the same floor.
    4. If no seats on the same floor, fallback to other floors.
    5. If employee has no project or team, look for any available seat starting from floor 1.
    """
    # 1. Look for team members (same project)
    team_seats = []
    if employee.project_id:
        team_seats = (
            db.query(models.Seat)
            .join(models.SeatAllocation, models.SeatAllocation.seat_id == models.Seat.id)
            .filter(
                models.SeatAllocation.project_id == employee.project_id,
                models.SeatAllocation.status == "Active"
            )
            .all()
        )

    # 2. If no project team seats, check department peers
    if not team_seats and employee.department:
        team_seats = (
            db.query(models.Seat)
            .join(models.SeatAllocation, models.SeatAllocation.seat_id == models.Seat.id)
            .join(models.Employee, models.SeatAllocation.employee_id == models.Employee.id)
            .filter(
                models.Employee.department == employee.department,
                models.SeatAllocation.status == "Active"
            )
            .all()
        )

    # 3. If we have peer seats, determine preferred floor/zone/bay
    if team_seats:
        # Determine the most common floor and zone
        floors = [s.floor for s in team_seats]
        zones = [s.zone for s in team_seats]
        bays = [s.bay for s in team_seats]

        pref_floor = max(set(floors), key=floors.count)
        pref_zone = max(set(zones), key=zones.count)
        pref_bay = max(set(bays), key=bays.count)

        # Step A: Same floor, same zone, same bay
        seat = db.query(models.Seat).filter(
            models.Seat.status == "Available",
            models.Seat.floor == pref_floor,
            models.Seat.zone == pref_zone,
            models.Seat.bay == pref_bay
        ).first()
        if seat:
            return seat

        # Step B: Same floor, same zone, any bay (adjacent in zone)
        seat = db.query(models.Seat).filter(
            models.Seat.status == "Available",
            models.Seat.floor == pref_floor,
            models.Seat.zone == pref_zone
        ).order_by(func.abs(models.Seat.bay - pref_bay)).first()
        if seat:
            return seat

        # Step C: Same floor, other zones (find closest zone)
        # Order zones by proximity (simple alphabetical sorting or defined map)
        zones_order = ["A", "B", "C", "D"]
        try:
            zone_idx = zones_order.index(pref_zone)
        except ValueError:
            zone_idx = 0
            
        seats_same_floor = db.query(models.Seat).filter(
            models.Seat.status == "Available",
            models.Seat.floor == pref_floor
        ).all()
        
        if seats_same_floor:
            # Sort by zone proximity
            def zone_distance(s):
                try:
                    s_idx = zones_order.index(s.zone)
                    return abs(s_idx - zone_idx)
                except ValueError:
                    return 999
            seats_same_floor.sort(key=zone_distance)
            return seats_same_floor[0]

        # Step D: Fallback to any available seat in the building, close to preferred floor
        all_avail = db.query(models.Seat).filter(models.Seat.status == "Available").all()
        if all_avail:
            all_avail.sort(key=lambda s: abs(s.floor - pref_floor))
            return all_avail[0]
            
    # 4. Fallback when there is no team/department footprint or no seats near them
    # Find any available seat, ordered from floor 1, zone A, bay 1, lowest seat number
    seat = db.query(models.Seat).filter(
        models.Seat.status == "Available"
    ).order_by(
        models.Seat.floor.asc(),
        models.Seat.zone.asc(),
        models.Seat.bay.asc(),
        models.Seat.seat_number.asc()
    ).first()

    return seat

def allocate_seat(db: Session, employee_id: int, seat_id: int = None) -> models.SeatAllocation:
    """
    Allocates a seat to an employee, handling locking and business logic constraints.
    - Ensures employee exists.
    - Ensures employee doesn't have an active seat.
    - If seat_id is specified:
        - Locks the seat.
        - Verifies it is Available.
    - If seat_id is NOT specified:
        - Automatically finds the best preferred seat.
        - Locks that seat.
    - Creates allocation, updates statuses.
    """
    # 1. Find employee
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_444_NOT_FOUND if hasattr(status, "HTTP_444_NOT_FOUND") else 404,
            detail="Employee not found"
        )

    # 2. Check if employee already has active seat
    active_alloc = db.query(models.SeatAllocation).filter(
        models.SeatAllocation.employee_id == employee_id,
        models.SeatAllocation.status == "Active"
    ).first()
    if active_alloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee already allocated to seat {active_alloc.seat.seat_number}"
        )

    # 3. Select seat with lock
    if seat_id:
        # User specified a seat - lock it for update
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id).with_for_update().first()
        if not seat:
            raise HTTPException(
                status_code=404,
                detail="Seat not found"
            )
        if seat.status != "Available":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seat {seat.seat_number} is currently {seat.status}"
            )
    else:
        # Find preferred seat
        seat_candidate = find_preferred_seat(db, employee)
        if not seat_candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available seats in the office"
            )
        # Lock the candidate seat for update
        seat = db.query(models.Seat).filter(models.Seat.id == seat_candidate.id).with_for_update().first()
        if seat.status != "Available":
            # Concurrency check: if someone else grabbed it between our check and our lock
            # We recursively call this to lock the next best seat
            return allocate_seat(db, employee_id, seat_id=None)

    # 4. Perform atomic update
    seat.status = "Occupied"
    employee.status = "Active"
    
    allocation = models.SeatAllocation(
        employee_id=employee.id,
        seat_id=seat.id,
        project_id=employee.project_id,
        allocated_at=datetime.datetime.now(),
        status="Active"
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    
    return allocation

def release_seat(db: Session, employee_id: int) -> models.SeatAllocation:
    """
    Releases an active seat allocation for an employee.
    Marks seat as Available, employee as Awaiting Allocation or Remote, and marks allocation as Released.
    """
    # 1. Find active allocation
    allocation = db.query(models.SeatAllocation).filter(
        models.SeatAllocation.employee_id == employee_id,
        models.SeatAllocation.status == "Active"
    ).with_for_update().first()
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active seat allocation found for this employee"
        )
        
    # 2. Lock and update seat and employee
    seat = db.query(models.Seat).filter(models.Seat.id == allocation.seat_id).with_for_update().first()
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).with_for_update().first()
    
    if seat:
        seat.status = "Available"
    if employee:
        employee.status = "Awaiting Allocation"
        
    allocation.released_at = datetime.datetime.now()
    allocation.status = "Released"
    
    db.commit()
    db.refresh(allocation)
    return allocation
