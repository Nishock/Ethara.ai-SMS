# AI Prompts log - Ethara Seat Allocation & Project Mapping System

This document outlines the detailed prompt flows, technical design decisions, and verification steps implemented throughout the development cycle.

---

## 1. Prompt Flow Checklist

### Prompt 1 — System Architecture
- **Prompt:** *"Design a scalable system architecture for Ethara’s seat allocation and project mapping system, including a React/Vite/TypeScript frontend, a Python FastAPI backend, and a database model. Emphasize containerization, atomic transactional allocations, and high-performance search queries for 5,000+ employees."*
- **AI Response:** Suggested a clean client-server architecture with Docker containerization. Emphasized using index rules for floor, zone, and project, along with SQLAlchemy ORM for handling transactions.

### Prompt 2 — Database Design & Schema
- **Prompt:** *"Draft a SQLAlchemy models file in Python with employees, projects, seats, and seat allocations. Emphasize constraints: one employee can have only one active seat, and one seat can have only one active employee. Include columns for employee_code, manager_name, department, role, status, joining_date, and created/updated timestamps."*
- **What AI Generated Correctly:** Produced tables with standard properties and foreign key relationships.
- **What AI Generated Incorrectly:** Standard SQL unique constraints on columns like `employee_id` and `seat_id` inside `seat_allocations` would prevent historic records or releasing seats (since a released seat must allow a new occupant).
- **Manual Fix:** Hand-crafted partial unique indexes using `sqlite_where` and `postgresql_where` filtering by `status == 'Active'` to enforce the uniqueness constraint only for current allocations.

### Prompt 3 — Backend API Development
- **Prompt:** *"Write FastAPI router modules for Employees, Projects, Seats, Dashboard analytics, and AI queries. Implement full CRUD endpoints, CSV bulk uploads, and response schemas conforming to OpenAPI specs. Support queries by employee_code, status, and project."*
- **Outcome:** Generated robust endpoints with Pydantic validation. Handled file parses for CSV imports, and automatically populated `employee_code` values (e.g. `EMP-00042`) when omitted.

### Prompt 4 — Seat Allocation Algorithm & Adjacency Heuristics
- **Prompt:** *"Implement the seat allocation function in Python. The algorithm must locate teammates in the same project, search for adjacent seats in the same bay, fall back to same zone, then same floor, and finally any floor. Enforce a row-level SELECT FOR UPDATE database lock during searches to prevent race conditions."*
- **Outcome:** Successfully implemented the multi-tiered proximity heuristic. Fallback options also look up department peers if no project teammates are currently seated.

### Prompt 5 — AI Assistant Engine
- **Prompt:** *"Create an AI assistant query router in Python. If GEMINI_API_KEY is configured, call Gemini to parse the user's natural language query and extract structured intent JSON. If not, use regular expression pattern match fallbacks to support queries like 'Where is Amit sitting?', 'Who sits near Amit?', 'Allocate a seat for Emily', or 'How many available seats are on Floor 3?'."*
- **Outcome:** Built a unified interface that routes to structured DB queries, executing read/write capabilities (like allocating seats) seamlessly via text commands.

### Prompt 6 — Frontend UI Implementation
- **Prompt:** *"Build a high-performance React frontend using Tailwind CSS for styling. Include an interactive Seat Map Grid, Dashboard summary cards, Project Footprint charts, Employee Directory, Admin Panel, and a floating AI Chatbot. Apply custom glassmorphism card styles, radial gradients, and micro-animations."*
- **Outcome:** Designed a dark-theme workspace with harmonized color gradients, responsive layout panels, and loading skeletons.

### Prompt 7 — Testing & Test Suites
- **Prompt:** *"Create a python test suite using pytest to verify seat allocation, manual override, release rules, double-booking preventions, and project proximity fallbacks. Mock the database session using a temporary SQLite database."*
- **Outcome:** Created a complete test suite verifying edge cases, priority hierarchies, and index rules.

### Prompt 8 — Debugging & Concurrency Checks
- **Prompt:** *"We are encountering a 422 validation error when calling auto-allocation with an undefined seat_id. Solve this and ensure JSON serialization strips undefined keys correctly in frontend API calls."*
- **Manual Fix:** Changed Pydantic schemas to mark `seat_id: Optional[int] = None` and updated the frontend `api.ts` fetch call to construct the payload dynamically.

### Prompt 9 — Deployment & Seeding
- **Prompt:** *"Generate a seed database helper in Python populating 5,000 employees, 5,500 seats, and 4,000 active allocations. Ensure the script runs in under 3 seconds using bulk inserts."*
- **Outcome:** Successfully written using SQLAlchemy's `bulk_save_objects` and committed atomically.

### Prompt 10 — Refactoring & Polish
- **Prompt:** *"Refactor the FastAPI Swagger UI at /docs to match the dark purple glassmorphism aesthetic of the React frontend. Include branded tags, HTTP method color bands, and inline markdown tables."*
- **Outcome:** Served a customized Swagger page featuring status pills, dark layout cards, and custom CSS styling.

---

## 2. Verification Summary

1. **Adjacency & Allocation Rules:** Verified that allocating an employee search queries project teammates first, placing them in the same floor/zone/bay.
2. **Double Booking:** Attempting to assign an occupied seat raises a validation exception and is blocked by DB unique indexes.
3. **Database Speed:** Seeding 5,000 employees and 5,500 seats completes in under 2 seconds.
