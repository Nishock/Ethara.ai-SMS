# Ethara Workspace Intelligence System — Submission Package

This document compile all required deliverables for the submission checklist of the Ethara Seat Allocation & AI Assistant Assignment.

---

## 🔗 Live Links & Repository

- **GitHub Repository:** [https://github.com/Nishock/Ethara.ai-SMS.git](https://github.com/Nishock/Ethara.ai-SMS.git)
- **Live Deployment Link:** *[Your Vercel Deployment URL, e.g., https://ethara-ai-sms-wef9.vercel.app]*
- **Live API Swagger Documentation:** *[Your Vercel API URL + /docs, e.g., https://ethara-ai-sms-wef9.vercel.app/docs]*

---

## 🗄️ Database Schema & Models
The application utilizes a relational PostgreSQL database structure configured via SQLAlchemy (`backend/app/models.py`):

1. **Employee:**
   - `id` (Integer, Primary Key)
   - `employee_code` (String, Unique, Index) — Auto-generated e.g. `EMP-00001`
   - `name` (String, Index)
   - `email` (String, Unique, Index)
   - `department` (String, Index)
   - `role` (String)
   - `joining_date` (Date)
   - `status` (String) — `Active` (Seated), `Awaiting Allocation`, or `Inactive`
   - `project_id` (Integer, Foreign Key)

2. **Project:**
   - `id` (Integer, Primary Key)
   - `name` (String, Unique, Index)
   - `description` (String)
   - `manager_name` (String)
   - `status` (String) — `Active`, `Completed`, or `On Hold`

3. **Seat:**
   - `id` (Integer, Primary Key)
   - `floor` (Integer, Index) — Floors 1-5
   - `zone` (String, Index) — Zones A-D
   - `bay` (Integer, Index) — Bays 1-5
   - `seat_number` (String, Unique, Index) — e.g. `F2-B3-42`
   - `status` (String) — `Available`, `Occupied`, `Reserved`, or `Maintenance`

4. **SeatAllocation:**
   - `id` (Integer, Primary Key)
   - `employee_id` (Integer, Foreign key, Index)
   - `seat_id` (Integer, Foreign key, Index)
   - `project_id` (Integer, Foreign key)
   - `allocated_at` (DateTime, Default: Now)
   - `released_at` (DateTime, Optional)
   - `status` (String) — `Active` or `Released`

*Note: Database unique index rules are set up with partial indexes to ensure that only one employee sits at an active seat, and only one seat is assigned to an active employee at any given time (historic records are kept in `seat_allocations` with `Released` status).*

---

## 📊 Sample Seed Data Counts
The live Neon PostgreSQL cloud database has been successfully seeded with the following benchmark metrics:
- **Employees:** 5,000 records (including first/last names, roles, departments, and project associations).
  - *Seated Employees:* 4,000 active allocations.
  - *Awaiting Allocation (Queue):* 1,000 employees.
- **Seats:** 5,500 desk seats across 5 floors (55 seats per bay, 5 bays per zone, 4 zones per floor).
  - *Available Seats:* 1,350 desks.
  - *Reserved Seats:* 100 desks.
  - *Maintenance Seats:* 50 desks.
- **Projects:** 49 projects (including all 11 required: `Indigo`, `Indreed`, `Mydreed`, `Preed`, `Serfy`, `Oreed`, `Bedegreed`, `Opreed`, `Serry`, `Kaary`, `Mered`).

---

## 🛠️ Debugging & Resolution Notes

### 1. `EBADPLATFORM` Node Dependency Error
- **Issue:** The frontend `package-lock.json` was generated on a Windows development system. This locked down the Windows binding for the new bundler `@rolldown/binding-win32-x64-msvc`. When Vercel (running Linux) attempted to install packages, npm errored out due to the OS platform mismatch.
- **Fix:** Added the `--force` flag inside the root delegation build script in `package.json`: `"build": "npm --prefix frontend install --force && npm --prefix frontend run build"`. This forces npm to bypass platform constraints and fetch the correct Linux binary wheels dynamically.

### 2. Python 3.14 Version Instabilities on Deployments
- **Issue:** Web services like Render build using the newest Python interpreter version (3.14.x preview). Some key binary extensions like `pydantic-core` do not have compiled wheels for Python 3.14 yet, causing compilation errors during dependency installs.
- **Fix:** Created a `.python-version` file specifying `3.11.9` in the repository root and backend folder, forcing the build server to use the stable Python 3.11 branch where pre-compiled wheels install instantly.

### 3. SQLite Concurrency Locking & 422 Errors
- **Issue:** Simultaneous allocation requests triggered a lock conflict on the default SQLite database file. Also, optional keys like `seat_id` caused FastAPI validation (HTTP 422) when omitted from JSON payloads.
- **Fix:** Refactored SQLAlchemy schemas to mark `seat_id: Optional[int] = None` and set up transaction level `SELECT FOR UPDATE` locks during searches. Replaced local SQLite database configurations with a fully concurrent cloud PostgreSQL hosted on Neon.

---

## 🚀 Deployment Notes
- **Frontend Stack:** React, Vite, TypeScript, Tailwind CSS, Lucide icons, served statically on Vercel.
- **Backend Stack:** Python, FastAPI, SQLAlchemy ORM, Uvicorn server, running as a Vercel Serverless/Render service.
- **Database:** Neon PostgreSQL hosting, configured using the environment variable `DATABASE_URL`.
