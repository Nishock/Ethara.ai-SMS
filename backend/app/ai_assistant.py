import os
import re
from sqlalchemy.orm import Session
from . import models, allocation_logic
from typing import Dict, Any

# Regular expression patterns for local fallback parser
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
FLOOR_PATTERN = re.compile(r'(?:floor|f)\s*(\d+)', re.IGNORECASE)
PROJECT_PATTERN = re.compile(r'(?:project|team)\s*([a-zA-Z0-9_\s-]+)', re.IGNORECASE)

def parse_and_respond_local(query: str, db: Session) -> Dict[str, Any]:
    """
    Fallback regex-based natural language parser when no LLM API key is present.
    Also handles custom query routing for advanced intents.
    """
    query_lower = query.lower()

    # 1. Seat Allocation query (e.g., "Allocate a seat for Amit")
    if "allocate" in query_lower or "assign" in query_lower:
        # Find first employee with status "Awaiting Allocation"
        email_match = EMAIL_PATTERN.search(query)
        emp = None
        if email_match:
            emp = db.query(models.Employee).filter(models.Employee.email.ilike(email_match.group(0))).first()
        else:
            # Look for a name in the query after "for"
            for_match = re.search(r'(?:for|to)\s+([a-zA-Z\s]+)', query_lower)
            if for_match:
                name_str = for_match.group(1).strip()
                emp = db.query(models.Employee).filter(
                    models.Employee.name.ilike(f"%{name_str}%"),
                    models.Employee.status == "Awaiting Allocation"
                ).first()

        if not emp:
            # Fallback: get any employee waiting for allocation
            emp = db.query(models.Employee).filter(models.Employee.status == "Awaiting Allocation").first()

        if emp:
            try:
                alloc = allocation_logic.allocate_seat(db, emp.id)
                seat = alloc.seat
                return {
                    "answer": f"Successfully allocated seat **{seat.seat_number}** (Floor {seat.floor}, Zone {seat.zone}, Bay {seat.bay}) for **{emp.name}** ({emp.email}) near their project team using proximity heuristics.",
                    "intent": "allocate_joiner",
                    "data": {
                        "success": True,
                        "employee_name": emp.name,
                        "employee_email": emp.email,
                        "seat_number": seat.seat_number,
                        "floor": seat.floor,
                        "zone": seat.zone,
                    }
                }
            except Exception as e:
                return {
                    "answer": f"Could not allocate seat for {emp.name}: {str(e)}",
                    "intent": "allocate_joiner",
                    "data": {"success": False}
                }
        else:
            return {
                "answer": "I couldn't find any employees currently awaiting seat allocation in the database.",
                "intent": "allocate_joiner",
                "data": {"success": False}
            }

    # 2. Neighbors query (e.g., "Who sits near Amit?", "Who is sitting near me?")
    if "near" in query_lower or "neighbor" in query_lower or "next to" in query_lower:
        email_match = EMAIL_PATTERN.search(query)
        emp = None
        if email_match:
            emp = db.query(models.Employee).filter(models.Employee.email.ilike(email_match.group(0))).first()
        else:
            # Extract name words, ignore keywords
            words = [w for w in query.split() if w.lower() not in [
                "who", "is", "sitting", "near", "next", "to", "neighbor", "neighbors", "me", "my", "the", "on"
            ]]
            for word in words:
                if len(word) > 2:
                    emp = db.query(models.Employee).filter(models.Employee.name.ilike(f"%{word}%")).first()
                    if emp:
                        break
        
        # Default to first seated employee if querying "near me" and no target found
        if not emp:
            emp = db.query(models.Employee).filter(models.Employee.status == "Active").first()

        if emp:
            active_alloc = db.query(models.SeatAllocation).filter(
                models.SeatAllocation.employee_id == emp.id,
                models.SeatAllocation.status == "Active"
            ).first()
            
            if active_alloc:
                seat = active_alloc.seat
                # Query occupied seats on same floor, zone, bay (excluding own seat)
                nearby_allocs = db.query(models.SeatAllocation).join(models.Seat).filter(
                    models.SeatAllocation.status == "Active",
                    models.Seat.floor == seat.floor,
                    models.Seat.zone == seat.zone,
                    models.Seat.bay == seat.bay,
                    models.SeatAllocation.employee_id != emp.id
                ).limit(5).all()

                if nearby_allocs:
                    names = [f"{a.employee.name} (Seat {a.seat.seat_number})" for a in nearby_allocs]
                    answer = f"Sitting near **{emp.name}** in Bay {seat.bay} (Floor {seat.floor}, Zone {seat.zone}): " + ", ".join(names) + "."
                else:
                    # Try wider zone range
                    nearby_zone = db.query(models.SeatAllocation).join(models.Seat).filter(
                        models.SeatAllocation.status == "Active",
                        models.Seat.floor == seat.floor,
                        models.Seat.zone == seat.zone,
                        models.SeatAllocation.employee_id != emp.id
                    ).limit(5).all()
                    if nearby_zone:
                        names = [f"{a.employee.name} (Seat {a.seat.seat_number})" for a in nearby_zone]
                        answer = f"No one is directly in the same bay, but nearby in Zone {seat.zone}: " + ", ".join(names) + "."
                    else:
                        answer = f"No active employees are currently seated near {emp.name} in Floor {seat.floor}, Zone {seat.zone}."

                return {
                    "answer": answer,
                    "intent": "neighbors",
                    "data": {
                        "employee_name": emp.name,
                        "seat_number": seat.seat_number,
                        "neighbors": [a.employee.name for a in nearby_allocs]
                    }
                }
            else:
                return {
                    "answer": f"{emp.name} does not have an active seat allocation, so I can't locate nearby teammates.",
                    "intent": "neighbors",
                    "data": None
                }

    # 3. Floor occupancy / availability query
    floor_match = FLOOR_PATTERN.search(query_lower)
    if floor_match and any(x in query_lower for x in ["available", "free", "vacant", "how many", "empty", "seats"]):
        floor_num = int(floor_match.group(1))
        total = db.query(models.Seat).filter(models.Seat.floor == floor_num).count()
        available = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Available").count()
        occupied = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Occupied").count()
        reserved = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Reserved").count()
        maintenance = db.query(models.Seat).filter(models.Seat.floor == floor_num, models.Seat.status == "Maintenance").count()
        
        if total == 0:
            return {
                "answer": f"I couldn't find any seats configured on Floor {floor_num}.",
                "intent": "floor_occupancy",
                "data": {"floor": floor_num, "total": 0}
            }
            
        utilization = (occupied / total) * 100 if total > 0 else 0
        return {
            "answer": f"On Floor {floor_num}, there are {available} available seats, {occupied} occupied seats ({utilization:.1f}% utilization), {reserved} reserved, and {maintenance} under maintenance.",
            "intent": "floor_occupancy",
            "data": {"floor": floor_num, "total": total, "available": available, "occupied": occupied, "utilization": utilization}
        }

    # 4. Employee seat lookup by email, code, or name
    email_match = EMAIL_PATTERN.search(query)
    employee = None
    if email_match:
        email = email_match.group(0)
        employee = db.query(models.Employee).filter(models.Employee.email.ilike(email)).first()
    elif "emp-" in query_lower:
        code_match = re.search(r'(emp-\d+)', query_lower)
        if code_match:
            code = code_match.group(1).upper()
            employee = db.query(models.Employee).filter(models.Employee.employee_code == code).first()
    else:
        name_match = re.search(r'(?:where is|seat of|where does)\s+([a-zA-Z\s]+?)(?:\s+sit|\s+sitting|\s*|\?|$)', query_lower)
        if name_match:
            name_str = name_match.group(1).strip()
            employee = db.query(models.Employee).filter(models.Employee.name.ilike(f"%{name_str}%")).first()
        else:
            for word in query.split():
                if len(word) > 2 and word.lower() not in ["where", "seat", "floor", "zone", "project", "is", "my", "the", "on", "who", "sitting"]:
                    employee = db.query(models.Employee).filter(models.Employee.name.ilike(f"%{word}%")).first()
                    if employee:
                        break

    if employee:
        active_alloc = db.query(models.SeatAllocation).filter(
            models.SeatAllocation.employee_id == employee.id,
            models.SeatAllocation.status == "Active"
        ).first()
        
        project_name = employee.project.name if employee.project else "No assigned project"
        
        if active_alloc:
            seat = active_alloc.seat
            return {
                "answer": f"{employee.name} (Code: {employee.employee_code or 'N/A'}, Email: {employee.email}) is assigned to **{project_name}** and sits at **Seat {seat.seat_number}** (Floor {seat.floor}, Zone {seat.zone}, Bay {seat.bay}).",
                "intent": "employee_seat",
                "data": {
                    "employee_name": employee.name,
                    "employee_email": employee.email,
                    "employee_code": employee.employee_code,
                    "project": project_name,
                    "seat_number": seat.seat_number,
                    "floor": seat.floor,
                    "zone": seat.zone,
                    "bay": seat.bay
                }
            }
        else:
            return {
                "answer": f"{employee.name} (Code: {employee.employee_code or 'N/A'}, Email: {employee.email}) is assigned to **{project_name}** but does not have an active seat allocation (Status: {employee.status}).",
                "intent": "employee_seat",
                "data": {
                    "employee_name": employee.name,
                    "employee_email": employee.email,
                    "employee_code": employee.employee_code,
                    "project": project_name,
                    "seat_number": None,
                    "status": employee.status
                }
            }

    # 5. Project details listing / occupancy
    project_match = PROJECT_PATTERN.search(query_lower)
    if project_match or "project" in query_lower:
        proj_name = ""
        if project_match:
            proj_name = project_match.group(1).strip()
        else:
            words = query.split()
            for word in words:
                if word.lower() not in ["project", "who", "is", "on", "team", "members", "the", "in", "what", "how", "many"]:
                    proj_name = word
                    break
                    
        project = db.query(models.Project).filter(models.Project.name.ilike(f"%{proj_name}%")).first()
        if project:
            employees = db.query(models.Employee).filter(models.Employee.project_id == project.id).all()
            allocated = []
            unallocated = []
            for emp in employees:
                alloc = db.query(models.SeatAllocation).filter(
                    models.SeatAllocation.employee_id == emp.id,
                    models.SeatAllocation.status == "Active"
                ).first()
                if alloc:
                    allocated.append(f"{emp.name} (Seat {alloc.seat.seat_number})")
                else:
                    unallocated.append(emp.name)
            
            allocated_str = ", ".join(allocated) if allocated else "None"
            unallocated_str = ", ".join(unallocated) if unallocated else "None"
            
            answer = f"Project '{project.name}' (Manager: {project.manager_name or 'N/A'}) has {len(employees)} members. "
            answer += f"Seated: {len(allocated)} ({allocated_str}) | Unseated/Remote: {len(unallocated)}."
            
            return {
                "answer": answer,
                "intent": "project_info",
                "data": {
                    "project_name": project.name,
                    "manager": project.manager_name,
                    "total_members": len(employees),
                    "seated_count": len(allocated),
                    "unseated_count": len(unallocated)
                }
            }

    # 6. Office dashboard / general summary query
    if any(x in query_lower for x in ["summary", "stats", "metrics", "total", "occupancy", "utilization"]):
        total_seats = db.query(models.Seat).count()
        occupied_seats = db.query(models.Seat).filter(models.Seat.status == "Occupied").count()
        available_seats = db.query(models.Seat).filter(models.Seat.status == "Available").count()
        reserved_seats = db.query(models.Seat).filter(models.Seat.status == "Reserved").count()
        maintenance_seats = db.query(models.Seat).filter(models.Seat.status == "Maintenance").count()
        total_employees = db.query(models.Employee).count()
        pending = db.query(models.Employee).filter(models.Employee.status == "Awaiting Allocation").count()
        
        utilization = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
        
        return {
            "answer": f"Office Occupancy Summary:\n- Total Seats: {total_seats}\n- Occupied: {occupied_seats} ({utilization:.1f}% utilization)\n- Available: {available_seats}\n- Reserved: {reserved_seats}\n- Maintenance: {maintenance_seats}\n- Total Employees: {total_employees}\n- Awaiting Assignment: {pending}",
            "intent": "office_summary",
            "data": {
                "total_seats": total_seats,
                "occupied_seats": occupied_seats,
                "available_seats": available_seats,
                "reserved_seats": reserved_seats,
                "maintenance_seats": maintenance_seats,
                "total_employees": total_employees,
                "pending_allocations": pending,
                "utilization": utilization
            }
        }

    # 7. Default generic response
    return {
        "answer": "I'm not sure how to answer that. You can ask me questions like: 'Where is Amit sitting?', 'Who sits near Amit?', 'Allocate a seat for Amit', 'How many available seats are on Floor 3?', or 'Give me an office summary'.",
        "intent": "unknown",
        "data": None
    }


def query_assistant(query: str, db: Session) -> Dict[str, Any]:
    """
    Main interface for AI workspace queries.
    Attempts to call Gemini or OpenAI APIs if configured, otherwise falls back.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not gemini_key and not openai_key:
        return parse_and_respond_local(query, db)

    prompt = f"""
    You are an AI assistant for Ethara's Seat Allocation and Project Mapping system.
    Analyze the user's natural language query and map it to one of the following JSON structures.

    Intents:
    1. Employee seat lookup: Use when user asks about a person, their seat, location, email, or desk.
       JSON format: {{"intent": "employee_seat", "search_term": "name or email or employee code"}}
       
    2. Floor occupancy: Use when user asks about seats, availability, free spots, or statistics on a floor.
       JSON format: {{"intent": "floor_occupancy", "floor": 2}}
       
    3. Project details: Use when user asks who is on a project, team details, or project manager.
       JSON format: {{"intent": "project_info", "project_name": "name of project"}}
       
    4. Office summary: Use when user asks for overall dashboard stats, utilization, or total seats/employees.
       JSON format: {{"intent": "office_summary"}}
       
    5. Neighbors: Use when user asks who sits near someone (e.g. "Who is sitting near Amit?").
       JSON format: {{"intent": "neighbors", "search_term": "name or email"}}

    6. Allocate seat: Use when user asks to allocate a seat for a new joiner or employee (e.g. "Allocate a seat for Amit").
       JSON format: {{"intent": "allocate_joiner", "search_term": "name or email"}}

    7. Unknown: If the query does not match the above.
       JSON format: {{"intent": "unknown"}}

    User query: "{query}"

    Output ONLY raw valid JSON matching the format above. No explanation, no markdown.
    """

    try:
        import json
        if gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            text = response.text.strip()
        else:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            text = completion.choices[0].message.content.strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        parsed = json.loads(text)
        intent = parsed.get("intent")
        
        # Dispatch to DB queries based on LLM structured output
        if intent == "employee_seat":
            search_term = parsed.get("search_term", "")
            return parse_and_respond_local(f"where is my seat {search_term}", db)
                
        elif intent == "floor_occupancy":
            floor_num = parsed.get("floor")
            if floor_num is not None:
                return parse_and_respond_local(f"available seats on floor {floor_num}", db)
                
        elif intent == "project_info":
            proj_name = parsed.get("project_name", "")
            return parse_and_respond_local(f"who is on project {proj_name}", db)
            
        elif intent == "office_summary":
            return parse_and_respond_local("office summary dashboard", db)

        elif intent == "neighbors":
            search_term = parsed.get("search_term", "")
            return parse_and_respond_local(f"who is sitting near {search_term}", db)

        elif intent == "allocate_joiner":
            search_term = parsed.get("search_term", "")
            return parse_and_respond_local(f"allocate seat for {search_term}", db)

    except Exception as e:
        print(f"AI Assistant LLM routing error, using local fallback: {e}")
        
    return parse_and_respond_local(query, db)
