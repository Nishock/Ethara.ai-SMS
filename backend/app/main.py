from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .database import engine, Base
from .routers import employees, projects, seats, dashboard, ai

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# ─── API Description ──────────────────────────────────────────────────────────
DESCRIPTION = """
## Ethara Workspace Intelligence API

A **production-ready** REST API for intelligent office workspace management — built with FastAPI + SQLAlchemy.

---

### 🚀 Core Features

| Feature | Details |
|---|---|
| **Seat Allocation Engine** | Auto-allocates desks by team adjacency heuristics (same floor → zone → bay) |
| **Concurrency Control** | Atomic transactions with row-level locking to prevent double-booking |
| **AI Query Interface** | Natural language workspace queries powered by Gemini/OpenAI |
| **Bulk Import** | CSV uploads for employees and seats with validation & error reporting |
| **Analytics Dashboard** | Real-time floor utilization, project footprints, occupancy rates |

---

### 🗂️ API Sections

- **`/employees`** — CRUD + CSV bulk import for employee records
- **`/projects`** — Project team management and membership
- **`/seats`** — Seat inventory, allocation, release, and CSV import
- **`/dashboard`** — Aggregated analytics: floor utilization, project footprint, summary stats
- **`/ai`** — Natural language workspace query engine

---

### 📋 Seat Status Values

| Status | Meaning |
|---|---|
| `Available` | Desk is free and ready to be assigned |
| `Occupied` | A current active employee is seated |
| `Reserved` | Desk is held and cannot be auto-allocated |

### 👤 Employee Status Values

| Status | Meaning |
|---|---|
| `Active` | Employee has an active seat allocation |
| `Awaiting Allocation` | Newly onboarded, no desk yet assigned |
| `Inactive` | Left the company / no longer active |

---

### ⚙️ Authentication
This development API does not require authentication. Production deployments should add **OAuth2 / JWT** bearer token middleware.

### 🔗 Useful Links
- [Frontend UI](http://localhost:5173) — React SPA
- [ReDoc Documentation](http://localhost:8000/redoc) — Alternative docs view
"""

TAGS_METADATA = [
    {
        "name": "Employees",
        "description": (
            "Manage employee records — create, read, update, and delete. "
            "Supports bulk CSV import with project mapping and duplicate detection. "
            "Employee status transitions from `Awaiting Allocation` → `Active` upon seat assignment."
        ),
    },
    {
        "name": "Projects",
        "description": (
            "Manage project teams. Each employee can belong to one project. "
            "The allocation engine uses project membership to group team members on the same floor/zone/bay."
        ),
    },
    {
        "name": "Seats",
        "description": (
            "Full seat inventory management. Allocate seats (auto or manual), release them, "
            "and bulk-import seat layouts via CSV. "
            "Auto-allocation applies a **priority heuristic**: "
            "same bay → same zone → same floor → any available seat."
        ),
    },
    {
        "name": "Dashboard",
        "description": (
            "Aggregated analytics endpoints powering the frontend dashboard. "
            "Returns real-time floor occupancy, project seat footprints, and workspace summary KPIs. "
            "Also exposes the **database seed** endpoint for bulk test data."
        ),
    },
    {
        "name": "AI",
        "description": (
            "Natural language workspace query engine. "
            "Submit plain-English questions like *'Where is Amit sitting?'* or "
            "*'How many available seats are on Floor 3?'* and receive structured answers."
        ),
    },
]

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ethara Workspace Intelligence API",
    description=DESCRIPTION,
    version="1.0.0",
    summary="Office seat allocation, project mapping, and AI-powered workspace analytics.",
    contact={
        "name": "Ethara Engineering",
        "url": "http://localhost:5173",
        "email": "engineering@ethara.io",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=TAGS_METADATA,
    # Disable default Swagger so we serve our custom one at /docs
    docs_url=None,
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(seats.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


# ─── Custom Dark Swagger UI ────────────────────────────────────────────────────
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Ethara API · Swagger UI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    /* ── Reset & base ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: #08080f;
      color: #e2e8f0;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }

    /* ── Custom header banner ── */
    #swagger-ui-header {
      background: linear-gradient(135deg, #12102a 0%, #0f0a20 40%, #0a0f25 100%);
      border-bottom: 1px solid rgba(139,92,246,0.20);
      padding: 24px 32px;
      display: flex;
      align-items: center;
      gap: 20px;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 4px 32px -8px rgba(0,0,0,0.6);
    }
    #swagger-ui-header .logo {
      width: 44px; height: 44px;
      background: linear-gradient(135deg, #7c3aed, #6366f1);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      box-shadow: 0 0 20px rgba(139,92,246,0.40);
      flex-shrink: 0;
    }
    #swagger-ui-header .title { flex: 1; }
    #swagger-ui-header .title h1 {
      font-size: 20px; font-weight: 800; color: #fff; letter-spacing: -0.02em;
    }
    #swagger-ui-header .title h1 span {
      background: linear-gradient(90deg, #c4b5fd, #a5b4fc);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    #swagger-ui-header .title p {
      font-size: 12px; color: #94a3b8; margin-top: 2px; font-weight: 500;
    }
    #swagger-ui-header .pills {
      display: flex; gap: 8px; align-items: center;
    }
    #swagger-ui-header .pill {
      padding: 4px 12px; border-radius: 100px; font-size: 11px; font-weight: 600;
      letter-spacing: 0.03em; border: 1px solid;
    }
    .pill-green  { background:rgba(16,185,129,0.12); color:#34d399; border-color:rgba(16,185,129,0.30); }
    .pill-purple { background:rgba(139,92,246,0.12); color:#a78bfa; border-color:rgba(139,92,246,0.30); }
    .pill-indigo { background:rgba(99,102,241,0.12); color:#818cf8; border-color:rgba(99,102,241,0.30); }
    .pill-links  { display:flex; gap:12px; align-items:center; }
    .pill-links a {
      font-size:12px; font-weight:600; color:#8b5cf6;
      text-decoration:none; border-bottom:1px solid transparent;
      transition:all .2s; padding-bottom:1px;
    }
    .pill-links a:hover { color:#c4b5fd; border-bottom-color:rgba(196,181,253,0.4); }

    /* ── Swagger UI wrapper ── */
    #swagger-ui {
      background: transparent;
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px 60px;
    }

    /* ── Hide Swagger default header ── */
    .swagger-ui .topbar { display: none !important; }
    .swagger-ui .information-container { display: none !important; }
    .swagger-ui .scheme-container { display: none !important; }

    /* ── Base text & backgrounds ── */
    .swagger-ui, .swagger-ui * {
      color: #cbd5e1;
      font-family: 'Inter', system-ui, sans-serif !important;
    }
    .swagger-ui .wrapper { background: transparent; box-shadow: none; }
    .swagger-ui .opblock-tag-section { background: transparent; }
    .swagger-ui .opblock { background: transparent; }

    /* ── Tag section headers ── */
    .swagger-ui .opblock-tag {
      background: rgba(18, 18, 30, 0.85) !important;
      border: 1px solid rgba(255,255,255,0.07) !important;
      border-radius: 14px !important;
      padding: 14px 20px !important;
      margin: 10px 0 6px !important;
      backdrop-filter: blur(16px);
      box-shadow: 0 2px 16px -4px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
      transition: all .2s;
    }
    .swagger-ui .opblock-tag:hover {
      border-color: rgba(139,92,246,0.22) !important;
      box-shadow: 0 4px 24px -6px rgba(139,92,246,0.20), inset 0 1px 0 rgba(255,255,255,0.06);
    }
    .swagger-ui .opblock-tag h3 {
      color: #f1f5f9 !important;
      font-size: 15px !important;
      font-weight: 700 !important;
      letter-spacing: -0.01em;
    }
    .swagger-ui .opblock-tag .opblock-tag-description p {
      color: #94a3b8 !important;
      font-size: 13px !important;
      line-height: 1.6 !important;
    }
    .swagger-ui .opblock-tag-section > .no-margin { padding-left: 0 !important; }

    /* ── Operation blocks ── */
    .swagger-ui .opblock {
      border-radius: 12px !important;
      margin: 6px 0 !important;
      border: 1px solid rgba(255,255,255,0.07) !important;
      background: rgba(14, 14, 25, 0.70) !important;
      backdrop-filter: blur(12px);
      box-shadow: 0 2px 12px -4px rgba(0,0,0,0.35);
      overflow: hidden;
      transition: all .2s !important;
    }
    .swagger-ui .opblock:hover {
      border-color: rgba(255,255,255,0.12) !important;
      transform: translateX(2px);
    }
    .swagger-ui .opblock .opblock-summary {
      background: transparent !important;
      border: none !important;
    }
    .swagger-ui .opblock .opblock-summary-method {
      border-radius: 8px !important;
      font-weight: 700 !important;
      font-size: 11px !important;
      letter-spacing: 0.06em !important;
      min-width: 70px !important;
      text-align: center;
      padding: 6px 10px !important;
    }
    .swagger-ui .opblock .opblock-summary-path {
      color: #e2e8f0 !important;
      font-size: 14px !important;
      font-weight: 600 !important;
      letter-spacing: 0.01em;
    }
    .swagger-ui .opblock .opblock-summary-description {
      color: #64748b !important;
      font-size: 12px !important;
      font-style: italic;
    }

    /* ── HTTP method color bands ── */
    .swagger-ui .opblock.opblock-get { border-left: 3px solid #10b981 !important; }
    .swagger-ui .opblock.opblock-post { border-left: 3px solid #6366f1 !important; }
    .swagger-ui .opblock.opblock-put { border-left: 3px solid #f59e0b !important; }
    .swagger-ui .opblock.opblock-delete { border-left: 3px solid #f43f5e !important; }
    .swagger-ui .opblock.opblock-patch { border-left: 3px solid #8b5cf6 !important; }

    /* Method badge colors */
    .swagger-ui .opblock.opblock-get .opblock-summary-method { background: rgba(16,185,129,0.18) !important; color: #34d399 !important; }
    .swagger-ui .opblock.opblock-post .opblock-summary-method { background: rgba(99,102,241,0.18) !important; color: #a5b4fc !important; }
    .swagger-ui .opblock.opblock-put .opblock-summary-method { background: rgba(245,158,11,0.18) !important; color: #fbbf24 !important; }
    .swagger-ui .opblock.opblock-delete .opblock-summary-method { background: rgba(244,63,94,0.18) !important; color: #fb7185 !important; }

    /* ── Expanded body ── */
    .swagger-ui .opblock-body { background: transparent !important; }
    .swagger-ui .opblock-description-wrapper {
      background: rgba(8, 8, 20, 0.50) !important;
      border-top: 1px solid rgba(255,255,255,0.06) !important;
      padding: 16px 20px !important;
      margin: 0 !important;
    }
    .swagger-ui .opblock-description-wrapper p,
    .swagger-ui .markdown-text p,
    .swagger-ui .renderedMarkdown p {
      color: #94a3b8 !important;
      font-size: 13px !important;
      line-height: 1.7 !important;
    }
    .swagger-ui .renderedMarkdown code,
    .swagger-ui .opblock-description-wrapper code {
      background: rgba(139,92,246,0.12) !important;
      color: #c4b5fd !important;
      padding: 1px 6px !important;
      border-radius: 5px !important;
      font-size: 12px !important;
    }
    /* Tables inside markdown */
    .swagger-ui .renderedMarkdown table {
      border-collapse: collapse !important;
      width: 100% !important;
      font-size: 12px !important;
      border-radius: 8px !important;
      overflow: hidden !important;
    }
    .swagger-ui .renderedMarkdown th {
      background: rgba(139,92,246,0.14) !important;
      color: #c4b5fd !important;
      padding: 8px 14px !important;
      font-weight: 700 !important;
      text-align: left !important;
    }
    .swagger-ui .renderedMarkdown td {
      padding: 7px 14px !important;
      border-top: 1px solid rgba(255,255,255,0.05) !important;
      color: #94a3b8 !important;
    }
    .swagger-ui .renderedMarkdown tr:nth-child(even) td {
      background: rgba(255,255,255,0.02) !important;
    }

    /* ── Parameters / request body ── */
    .swagger-ui .opblock .opblock-section-header,
    .swagger-ui .opblock.opblock-get .opblock-section-header,
    .swagger-ui .opblock.opblock-post .opblock-section-header,
    .swagger-ui .opblock.opblock-put .opblock-section-header,
    .swagger-ui .opblock.opblock-delete .opblock-section-header,
    .swagger-ui .opblock.opblock-patch .opblock-section-header {
      background: rgba(18, 18, 30, 0.90) !important;
      border-top: 1px solid rgba(255,255,255,0.06) !important;
      border-bottom: 1px solid rgba(255,255,255,0.06) !important;
      box-shadow: none !important;
      padding: 10px 20px !important;
    }
    .swagger-ui .opblock .opblock-section-header h4,
    .swagger-ui .opblock .opblock-section-header h4 span {
      color: #c4b5fd !important;
      font-weight: 700 !important;
      font-size: 13px !important;
    }
    .swagger-ui .parameters-container,
    .swagger-ui .request-body-container {
      background: rgba(8, 8, 20, 0.50) !important;
    }
    .swagger-ui table.headers td, .swagger-ui table thead th {
      color: #94a3b8 !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      border-bottom: 1px solid rgba(255,255,255,0.08) !important;
      padding: 8px 12px !important;
    }
    .swagger-ui table tbody tr td {
      color: #cbd5e1 !important;
      border-bottom: 1px solid rgba(255,255,255,0.04) !important;
      padding: 8px 12px !important;
    }
    .swagger-ui .parameter__name { color: #a78bfa !important; font-weight: 700 !important; }
    .swagger-ui .parameter__type { color: #64748b !important; font-size: 11px !important; }
    .swagger-ui .parameter__deprecated { color: #f43f5e !important; }
    .swagger-ui .parameter__in {
      background: rgba(99,102,241,0.10) !important;
      color: #818cf8 !important;
      border-radius: 4px !important;
      padding: 1px 6px !important;
      font-size: 10px !important;
      font-weight: 700 !important;
    }

    /* ── Models section ── */
    .swagger-ui section.models {
      background: rgba(14,14,25,0.70) !important;
      border: 1px solid rgba(255,255,255,0.07) !important;
      border-radius: 14px !important;
      margin-top: 32px !important;
    }
    .swagger-ui section.models h4 {
      color: #e2e8f0 !important;
      font-weight: 700 !important;
    }
    .swagger-ui .model-container {
      background: rgba(8,8,20,0.50) !important;
      border-radius: 8px !important;
    }
    .swagger-ui .model { color: #94a3b8 !important; font-size: 12px !important; }
    .swagger-ui .prop-type { color: #a78bfa !important; font-weight: 600 !important; }
    .swagger-ui .prop-format { color: #64748b !important; font-size: 11px !important; }

    /* ── Try it out button ── */
    .swagger-ui .try-out__btn {
      background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
      color: #fff !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      padding: 6px 16px !important;
      cursor: pointer;
      transition: all .2s !important;
      box-shadow: 0 4px 12px rgba(139,92,246,0.30);
    }
    .swagger-ui .try-out__btn:hover {
      box-shadow: 0 6px 20px rgba(139,92,246,0.45) !important;
      transform: translateY(-1px);
    }

    /* ── Execute button ── */
    .swagger-ui .btn.execute {
      background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
      color: #fff !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 700 !important;
      font-size: 13px !important;
      padding: 10px 24px !important;
      box-shadow: 0 4px 16px rgba(139,92,246,0.35);
      transition: all .2s !important;
    }
    .swagger-ui .btn.execute:hover {
      box-shadow: 0 8px 28px rgba(139,92,246,0.5) !important;
      transform: translateY(-1px);
    }
    .swagger-ui .btn.btn-clear {
      border: 1px solid rgba(255,255,255,0.12) !important;
      color: #94a3b8 !important;
      background: rgba(255,255,255,0.04) !important;
      border-radius: 8px !important;
    }
    .swagger-ui .btn.btn-clear:hover {
      background: rgba(255,255,255,0.08) !important;
      color: #cbd5e1 !important;
    }

    /* ── Inputs in Try-it-out ── */
    .swagger-ui input[type=text],
    .swagger-ui input[type=email],
    .swagger-ui input[type=file],
    .swagger-ui textarea,
    .swagger-ui select {
      background: rgba(8,8,20,0.70) !important;
      border: 1px solid rgba(255,255,255,0.12) !important;
      color: #e2e8f0 !important;
      border-radius: 8px !important;
      padding: 8px 12px !important;
      font-size: 13px !important;
      font-family: 'Inter', monospace !important;
    }
    .swagger-ui input:focus, .swagger-ui textarea:focus {
      border-color: rgba(139,92,246,0.55) !important;
      box-shadow: 0 0 0 3px rgba(139,92,246,0.14) !important;
      outline: none !important;
    }
    .swagger-ui .body-param textarea {
      background: rgba(5,5,15,0.80) !important;
      border: 1px solid rgba(139,92,246,0.20) !important;
      border-radius: 10px !important;
      font-size: 12px !important;
      font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }

    /* ── Responses ── */
    .swagger-ui .responses-wrapper {
      background: rgba(8,8,20,0.50) !important;
    }
    .swagger-ui .response-col_status { color: #a78bfa !important; font-weight: 700 !important; }
    .swagger-ui .response-col_description { color: #94a3b8 !important; font-size: 13px !important; }
    .swagger-ui .tabheader {
      border-bottom: 1px solid rgba(255,255,255,0.08) !important;
      background: transparent !important;
      padding: 0 !important;
    }
    .swagger-ui .tabheader .tab-btn {
      color: #94a3b8 !important;
      font-weight: 600 !important;
      font-size: 11px !important;
      background: transparent !important;
      border: none !important;
      padding: 6px 12px !important;
    }
    .swagger-ui .tabheader .tab-btn.active {
      color: #c4b5fd !important;
      border-bottom: 2px solid #8b5cf6 !important;
    }
    .swagger-ui .response-control-media-type {
      background: rgba(8,8,20,0.80) !important;
      color: #cbd5e1 !important;
      border: 1px solid rgba(255,255,255,0.12) !important;
      border-radius: 6px !important;
      padding: 2px 6px !important;
      font-size: 11px !important;
    }
    .swagger-ui .microlight {
      background: rgba(5,5,15,0.75) !important;
      border: 1px solid rgba(255,255,255,0.06) !important;
      border-radius: 8px !important;
      padding: 12px 16px !important;
      font-size: 12px !important;
      font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
      color: #a78bfa !important;
      line-height: 1.7;
    }
    .swagger-ui .highlight-code pre {
      background: rgba(5,5,15,0.80) !important;
      border-radius: 8px !important;
      padding: 16px !important;
      color: #c4b5fd !important;
      font-size: 12px !important;
    }

    /* ── Copy btn ── */
    .swagger-ui .copy-to-clipboard {
      background: rgba(139,92,246,0.12) !important;
      border: 1px solid rgba(139,92,246,0.25) !important;
      border-radius: 6px !important;
    }

    /* ── Auth button ── */
    .swagger-ui .btn.authorize {
      background: rgba(99,102,241,0.12) !important;
      border: 1px solid rgba(99,102,241,0.30) !important;
      color: #818cf8 !important;
      border-radius: 8px !important;
      font-weight: 700 !important;
    }
    .swagger-ui .btn.authorize:hover {
      background: rgba(99,102,241,0.22) !important;
    }
    .swagger-ui .authorization__btn { color: #818cf8 !important; }

    /* ── Required badge ── */
    .swagger-ui .required { color: #f43f5e !important; font-size: 11px !important; font-weight: 700 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.20); border-radius: 100px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.45); }

    /* ── Filter input ── */
    .swagger-ui .operation-filter-input {
      background: rgba(18,18,30,0.90) !important;
      border: 1px solid rgba(139,92,246,0.22) !important;
      border-radius: 10px !important;
      color: #e2e8f0 !important;
      padding: 10px 16px !important;
      font-size: 13px !important;
      width: 100% !important;
      margin-bottom: 16px !important;
    }

    /* ── Arrow icons ── */
    .swagger-ui .expand-methods svg, .swagger-ui .expand-operation svg { fill: #8b5cf6 !important; }
    .swagger-ui .arrow { fill: #8b5cf6 !important; }
    .swagger-ui .model-toggle { color: #8b5cf6 !important; }

    /* ── Loading ── */
    .swagger-ui .loading-container .loading::after { background: #8b5cf6 !important; }
  </style>
</head>
<body>
  <!-- Custom branded header -->
  <div id="swagger-ui-header">
    <div class="logo">🚀</div>
    <div class="title">
      <h1>Ethara <span>Workspace</span> API</h1>
      <p>Seat Allocation · Project Mapping · AI-Powered Analytics</p>
    </div>
    <div class="pills">
      <span class="pill pill-green">● Online</span>
      <span class="pill pill-purple">v1.0.0</span>
      <span class="pill pill-indigo">OAS 3.1</span>
    </div>
    <div class="pill-links">
      <a href="http://localhost:5173" target="_blank">← Frontend</a>
      <a href="/redoc" target="_blank">ReDoc</a>
      <a href="/openapi.json" target="_blank">JSON Schema</a>
    </div>
  </div>

  <div id="swagger-ui"></div>

  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/openapi.json",
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      docExpansion: "none",
      operationsSorter: "alpha",
      tagsSorter: "alpha",
      defaultModelsExpandDepth: 1,
      tryItOutEnabled: true,
      persistAuthorization: true,
      displayRequestDuration: true,
      filter: true,
      syntaxHighlight: { activate: true, theme: "monokai" }
    });
  </script>
</body>
</html>""", status_code=200)


# ─── Health ────────────────────────────────────────────────────────────────────
@app.get(
    "/",
    tags=["Health"],
    summary="API Health Check",
    description="Returns the current API status and links to documentation.",
    response_description="API status and documentation links.",
)
def read_root():
    return {
        "status": "online",
        "version": "1.0.0",
        "message": "Ethara Workspace Intelligence API is running.",
        "docs": {"swagger": "/docs", "redoc": "/redoc", "openapi_json": "/openapi.json"},
        "frontend": "http://localhost:5173",
    }
