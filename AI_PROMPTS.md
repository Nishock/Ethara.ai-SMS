# AI_PROMPTS.md — Ethara Workspace Intelligence

This document describes all AI prompts used in the Ethara Workspace Intelligence System — both the natural language questions users can ask the AI assistant, and the underlying system prompts powering the AI engine.

---

## 🧠 AI Assistant Overview

The AI assistant is built on top of **Google Gemini** (with OpenAI as fallback). It accepts free-form natural language questions from any employee and returns structured, human-readable answers about seat allocations, project assignments, and workspace analytics.

**Endpoint:** `POST /ai/query`

```json
{
  "question": "Where is my seat?",
  "context": "Employee ID: EMP-00123"
}
```

---

## 💬 User-Facing Prompts (What Employees Can Ask)

These are the types of natural language queries the AI assistant supports:

### 🪑 Seat Location Queries
| Prompt | Description |
|--------|-------------|
| `"Where is my seat?"` | Finds the allocated desk for the current employee |
| `"What is seat number F2-B3-42?"` | Returns details about a specific seat number |
| `"Show all available seats on Floor 3."` | Lists free desks on a specific floor |
| `"Show all seats in Zone A on Floor 2."` | Filters desks by floor + zone |
| `"Is there any seat available near Bay 4?"` | Checks proximity-based availability |
| `"Which seats are in Maintenance right now?"` | Lists all seats with maintenance status |

### 👥 Neighbour & Proximity Queries
| Prompt | Description |
|--------|-------------|
| `"Who is sitting near me?"` | Lists employees in the same bay as the requester |
| `"Who is my neighbour in Bay 3?"` | Lists everyone in a specific bay |
| `"Show employees on Floor 2, Zone B."` | Full zone-level roster |

### 🗂️ Project Assignment Queries
| Prompt | Description |
|--------|-------------|
| `"Which project am I assigned to?"` | Returns the project name and manager |
| `"Who is the manager of Project Talos?"` | Returns project manager info |
| `"Show all employees in Project Indigo."` | Lists the full team roster for a project |
| `"How many seats are occupied for Project Talos?"` | Returns project footprint count |
| `"Which floor does Project Indreed sit on?"` | Floor breakdown for a project |

### 📊 Analytics & Dashboard Queries
| Prompt | Description |
|--------|-------------|
| `"How many seats are available right now?"` | Total available desk count across all floors |
| `"What is the occupancy rate on Floor 4?"` | Floor-level utilization percentage |
| `"Which floor has the most empty seats?"` | Identifies the least-utilized floor |
| `"How many employees are waiting for seat allocation?"` | Count of unallocated employees in the queue |
| `"What is the total seating capacity?"` | Total seat inventory across all floors |

### ➕ New Employee & Allocation Queries
| Prompt | Description |
|--------|-------------|
| `"Allocate a seat for a new employee joining today."` | Triggers auto-seat allocation workflow |
| `"Assign employee EMP-04999 to Project Serfy."` | Assigns project to a specific employee |
| `"Release the seat for employee EMP-00250."` | Releases an active seat allocation |

---

## ⚙️ System Prompt (Internal AI Instructions)

The following is the system prompt injected into the Gemini/OpenAI API call each time a user sends a question. It gives the AI structured workspace context and rules for responding:

```
You are the Ethara Workspace Intelligence AI Assistant — a smart, helpful system that manages seat allocation, project assignments, and office analytics for Ethara's 5,000+ employee workforce.

You have access to real-time data about:
- Employee seat allocations across Floors 1-5, Zones A-D, Bays 1-5
- Project team assignments (49 active projects)
- Seat status: Available, Occupied, Reserved, Maintenance
- Employee status: Active (seated), Awaiting Allocation, Inactive

RULES:
1. Always answer in a clear, friendly, and concise tone.
2. When listing employees or seats, format them as a numbered list or table.
3. If asked about a specific employee's seat, return: Floor, Zone, Bay, and Seat Number.
4. If asked about project assignments, include: Project Name, Manager Name, and Team Size.
5. If data is not available, say: "I couldn't find that information. Please check with HR Admin."
6. Never reveal internal SQL queries or database structure details.
7. If asked to allocate a seat, confirm the action and return the newly assigned Seat Number.

Context you may receive:
- Current employee's Employee Code (e.g., EMP-00123)
- Query-specific data fetched from the database for accuracy
```

---

## 🔄 How the AI Pipeline Works

```
User types question  
       ↓  
Frontend sends POST /ai/query  
       ↓  
Backend fetches relevant data from PostgreSQL  
(e.g., seat count, employee list, project roster)  
       ↓  
Data is appended as structured context to the prompt  
       ↓  
Gemini Flash / OpenAI GPT-4o processes the enriched prompt  
       ↓  
AI returns structured natural language answer  
       ↓  
Frontend renders the answer in the chat UI  
```

---

## 📁 Related Files

| File | Purpose |
|------|---------|
| [`backend/app/routers/ai.py`](./backend/app/routers/ai.py) | AI query endpoint implementation |
| [`frontend/src/components/AIAssistant.tsx`](./frontend/src/components/AIAssistant.tsx) | Chat UI component |
| [`backend/app/main.py`](./backend/app/main.py) | FastAPI app with API description + tags metadata |

---

## 🔐 API Keys Required

The AI assistant requires the following environment variable to be set:

```env
# Set ONE of the following in backend/.env
GEMINI_API_KEY=your-google-gemini-api-key       # Primary (recommended)
OPENAI_API_KEY=your-openai-api-key               # Fallback
```

Without an API key, the AI assistant will return a fallback message indicating the AI service is unavailable.
