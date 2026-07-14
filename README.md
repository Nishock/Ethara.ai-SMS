# 🚀 Ethara Workspace Intelligence System

A **production-ready, AI-powered office seat allocation and workspace management system** for Ethara's 5,000+ employee workforce.

![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20Neon-336791)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)

---

## 🔗 Live Links

| Resource | URL |
|----------|-----|
| 🌐 **Frontend App** | [https://ethara-ai-sms-wef9.vercel.app](https://ethara-ai-sms-wef9.vercel.app) |
| ⚙️ **Backend API** | [https://ethara-ai-sms.onrender.com](https://ethara-ai-sms.onrender.com) |
| 📄 **Swagger API Docs** | [https://ethara-ai-sms.onrender.com/docs](https://ethara-ai-sms.onrender.com/docs) |
| 📚 **ReDoc API Docs** | [https://ethara-ai-sms.onrender.com/redoc](https://ethara-ai-sms.onrender.com/redoc) |
| 🐙 **GitHub Repository** | [https://github.com/Nishock/Ethara.ai-SMS](https://github.com/Nishock/Ethara.ai-SMS) |

---

## ✨ Features

### 👤 Employee Management
- Create, view, update, and deactivate employees
- Auto-generates unique employee codes (`EMP-XXXXX`)
- Track department, role, joining date, and project assignment
- Status transitions: `Awaiting Allocation` → `Active` → `Inactive`
- **Bulk CSV import** with validation and duplicate detection

### 🪑 Seat Allocation Engine
- **Auto-allocation** with adjacency heuristics — teams sit together (same floor → zone → bay → first available)
- **Manual allocation** to a specific seat number
- **Seat release** with full history preserved
- Seat statuses: `Available`, `Occupied`, `Reserved`, `Maintenance`
- **Bulk CSV import** for seat layouts

### 🗂️ Project Mapping
- 49+ active projects with manager assignments
- Project-based team grouping and floor mapping
- Project seat footprint analytics

### 📊 Analytics Dashboard
- Real-time floor utilization charts (Floors 1–5)
- Project seat footprint breakdown
- Summary KPIs: total employees, active seats, available seats, utilization %

### 🤖 AI Assistant
- Natural language queries powered by **Google Gemini**
- Ask questions like: *"Where is my seat?"*, *"Show all seats on Floor 3"*, *"Who is sitting near me?"*
- Enriched with real-time database context for accuracy

---

## 🏗️ Architecture

```
ethara-workspace-intelligence/
├── frontend/              # React + TypeScript + Vite (UI)
│   ├── src/
│   │   ├── components/    # Dashboard, EmployeeDirectory, SeatMap, AIAssistant, etc.
│   │   └── api.ts         # Typed API client
│   └── vite.config.ts
│
├── backend/               # Python FastAPI (REST API)
│   ├── app/
│   │   ├── main.py        # FastAPI app + custom docs + CORS
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── schemas.py     # Pydantic request/response schemas
│   │   ├── database.py    # DB engine + session management
│   │   └── routers/       # employees, projects, seats, dashboard, ai
│   ├── seed.py            # Bulk seed script (5,000 employees, 5,500 seats)
│   └── requirements.txt
│
├── api/                   # Vercel serverless entry point
│   ├── index.py
│   └── requirements.txt
│
├── vercel.json            # Vercel routing + build config
├── docker-compose.yml     # Local Docker setup
├── README.md
└── AI_PROMPTS.md
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use the hosted Neon connection)

### 1. Clone the Repository
```bash
git clone https://github.com/Nishock/Ethara.ai-SMS.git
cd Ethara.ai-SMS
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `backend/.env`:
```env
DATABASE_URL=postgresql://neondb_owner:...@ep-...neon.tech/neondb?sslmode=require
GEMINI_API_KEY=your-gemini-api-key      # Optional: for AI assistant
```

### 4. Start the Backend
```bash
cd backend
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

### 5. Seed the Database
```bash
cd backend
.venv\Scripts\python seed.py
```

### 6. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 7. Open in Browser
- **Frontend:** http://localhost:5173
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc Docs:** http://localhost:8000/redoc

---

## 🐳 Docker Compose (Recommended for Local Full Stack)

```bash
docker-compose up --build
```

This starts:
- `backend` on port `8000`
- `frontend` on port `5173`
- `postgres` on port `5432`

---

## 🗄️ Database Schema

| Table | Key Fields |
|-------|-----------|
| `employees` | `id`, `employee_code`, `name`, `email`, `department`, `role`, `status`, `project_id` |
| `projects` | `id`, `name`, `description`, `manager_name`, `status` |
| `seats` | `id`, `floor`, `zone`, `bay`, `seat_number`, `status` |
| `seat_allocations` | `id`, `employee_id`, `seat_id`, `project_id`, `allocated_at`, `released_at`, `status` |

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/employees/` | List employees with filters |
| `POST` | `/employees/` | Create new employee |
| `PUT` | `/employees/{id}` | Update employee |
| `DELETE` | `/employees/{id}` | Deactivate employee |
| `POST` | `/employees/import/csv` | Bulk CSV import |
| `GET` | `/projects/` | List all projects |
| `POST` | `/projects/` | Create project |
| `GET` | `/seats/` | List seats with filters |
| `POST` | `/seats/allocate` | Allocate seat (auto or manual) |
| `POST` | `/seats/{id}/release` | Release seat |
| `GET` | `/seats/{id}/occupant` | Get current occupant |
| `POST` | `/seats/import/csv` | Bulk seat CSV import |
| `GET` | `/dashboard/stats` | Summary KPIs |
| `GET` | `/dashboard/floor-utilization` | Floor occupancy breakdown |
| `GET` | `/dashboard/project-footprint` | Project seat counts |
| `POST` | `/dashboard/seed` | Seed database with test data |
| `POST` | `/ai/query` | Natural language AI query |

Full interactive documentation: **[Swagger UI](https://ethara-ai-sms.onrender.com/docs)** or **[ReDoc](https://ethara-ai-sms.onrender.com/redoc)**

---

## 🌐 Deployment on Vercel

### Required Environment Variables in Vercel:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon PostgreSQL connection string |
| `GEMINI_API_KEY` | Your Google Gemini API key (for AI assistant) |

### Live Deployments:
| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | [https://ethara-ai-sms-wef9.vercel.app](https://ethara-ai-sms-wef9.vercel.app) |
| Backend API | Render | [https://ethara-ai-sms.onrender.com](https://ethara-ai-sms.onrender.com) |
| Swagger UI | Render | [https://ethara-ai-sms.onrender.com/docs](https://ethara-ai-sms.onrender.com/docs) |
| ReDoc UI | Render | [https://ethara-ai-sms.onrender.com/redoc](https://ethara-ai-sms.onrender.com/redoc) |

### Build Configuration:
Vercel automatically reads `vercel.json` in the repository root, which:
1. Builds the **React frontend** from `frontend/` using Vite
2. Deploys the **FastAPI backend** as Python serverless functions from `api/`
3. Routes `/api/*`, `/employees/*`, `/seats/*`, etc. → backend
4. Routes everything else → frontend static files

---

## 🤖 AI Assistant

The AI assistant supports natural language workspace queries. See [AI_PROMPTS.md](./AI_PROMPTS.md) for the full list of supported prompts and system prompt configuration.

**Example queries:**
- *"Where is my seat?"*
- *"Show all available seats on Floor 3."*
- *"How many employees are in Project Talos?"*
- *"Who is sitting near me?"*
- *"Allocate a seat for a new employee joining today."*

---

## 🔧 Debugging Notes

See [`submission_package.md`](./submission_package.md) for detailed debugging and resolution notes on:
- Python version conflicts (3.14 preview vs 3.11 stable)
- `EBADPLATFORM` npm build errors on Linux CI
- SQLite concurrency → PostgreSQL migration
- Duplicate key constraint errors on re-seeding

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.

---

## 👨‍💻 Built For

Ethara Engineering Team — Workspace Intelligence Assignment, July 2026.
