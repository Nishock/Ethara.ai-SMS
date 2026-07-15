# AI_PROMPTS.md — Ethara Workspace Intelligence

Comprehensive documentation of all AI prompts, system instructions, intent routing logic, and natural language query examples used in the Ethara Workspace Intelligence System.

---

## 📖 Overview

The AI assistant is the conversational interface to the Ethara Workspace Intelligence System. It accepts **free-form natural language** from any employee and resolves workspace queries in real time — without requiring knowledge of API endpoints or database structure.

**Architecture:**

```
User Question (natural language)
       ↓
POST /ai/query → backend/app/ai_assistant.py
       ↓
If GEMINI_API_KEY or OPENAI_API_KEY is set:
  → LLM parses the intent from the question
  → Returns a structured JSON intent object
  → Backend dispatches to the correct DB query
Else:
  → Local regex-based fallback parser handles the query directly
       ↓
Structured JSON response: { answer, intent, data }
       ↓
Frontend renders the human-readable answer in the chat UI
```

**Primary LLM:** Google Gemini 1.5 Flash
**Fallback LLM:** OpenAI GPT-4o Mini
**Offline Fallback:** Regex-based local parser (no API key required)

---

## 🔑 Environment Variables

> If **neither** key is set, the system automatically falls back to a built-in regex-based local parser which handles all 6 intent categories without any external API call.

---

## 🧠 The System Prompt Sent to the LLM

This is the exact prompt injected into every Gemini / OpenAI API call. Its purpose is **intent classification only** — the LLM outputs structured JSON, not the final answer. The final natural language answer is always generated from live PostgreSQL data.

```
You are an AI assistant for Ethara's Seat Allocation and Project Mapping system.
Analyze the user's natural language query and map it to one of the following JSON structures.

Intents:
1. Employee seat lookup: Use when user asks about a person, their seat, location, email, or desk.
   JSON format: {"intent": "employee_seat", "search_term": "name or email or employee code"}

2. Floor occupancy: Use when user asks about seats, availability, free spots, or statistics on a floor.
   JSON format: {"intent": "floor_occupancy", "floor": 2}

3. Project details: Use when user asks who is on a project, team details, or project manager.
   JSON format: {"intent": "project_info", "project_name": "name of project"}

4. Office summary: Use when user asks for overall dashboard stats, utilization, or total seats/employees.
   JSON format: {"intent": "office_summary"}

5. Neighbors: Use when user asks who sits near someone (e.g. "Who is sitting near Amit?").
   JSON format: {"intent": "neighbors", "search_term": "name or email"}

6. Allocate seat: Use when user asks to allocate a seat for a new joiner or employee.
   JSON format: {"intent": "allocate_joiner", "search_term": "name or email"}

7. Unknown: If the query does not match the above.
   JSON format: {"intent": "unknown"}

User query: "{query}"

Output ONLY raw valid JSON matching the format above. No explanation, no markdown.
```

---

## 🎯 Supported Intents & Example Prompts

### 1. `employee_seat` — Find Where an Employee Sits

Used when a user asks about a specific person's seat location, desk number, or floor assignment.

**Example Prompts:**

| Prompt                                       | What happens                                 |
| -------------------------------------------- | -------------------------------------------- |
| `"Where is my seat?"`                      | Finds the seat for the first active employee |
| `"Where is Amit sitting?"`                 | Searches for employee named Amit             |
| `"Where does rahul.sharma@ethara.io sit?"` | Looks up by email address                    |
| `"What is the seat for EMP-00123?"`        | Looks up by employee code                    |
| `"Find desk for John"`                     | Fuzzy name search                            |
| `"Which seat is allocated to Priya?"`      | Name-based seat lookup                       |

**Response includes:**

- Employee name, email, and code
- Assigned project
- Seat number (e.g., `F2-B3-42`)
- Floor, Zone, Bay
- If unallocated: current status (e.g., `Awaiting Allocation`)

**Example Response:**

```
Amit Kumar (Code: EMP-00042, Email: amit.kumar@ethara.io) is assigned to Project Indigo
and sits at Seat F2-B3-42 (Floor 2, Zone B, Bay 3).
```

---

### 2. `floor_occupancy` — Seat Availability on a Floor

Used when a user asks about how many seats are available, occupied, or free on a specific floor.

**Example Prompts:**

| Prompt                                       | What happens                               |
| -------------------------------------------- | ------------------------------------------ |
| `"Show all available seats on Floor 3."`   | Returns availability breakdown for Floor 3 |
| `"How many free seats are on Floor 2?"`    | Available count for Floor 2                |
| `"What is the occupancy rate on Floor 4?"` | Returns utilization %                      |
| `"Are there any empty seats on Floor 1?"`  | Floor 1 availability check                 |
| `"How many seats are vacant on floor 5?"`  | Floor 5 vacancy count                      |

**Response includes:**

- Total seats on the floor
- Available / Occupied / Reserved / Maintenance counts
- Occupancy percentage

**Example Response:**

```
On Floor 3, there are 187 available seats, 862 occupied seats (82.1% utilization),
45 reserved, and 6 under maintenance.
```

---

### 3. `project_info` — Project Team & Seat Footprint

Used when a user asks about a specific project — team size, manager, who is seated, or who is waiting.

**Example Prompts:**

| Prompt                                                | What happens                          |
| ----------------------------------------------------- | ------------------------------------- |
| `"Who is on Project Talos?"`                        | Lists all employees assigned to Talos |
| `"How many seats are occupied for Project Indigo?"` | Counts active allocations for Indigo  |
| `"Who is the manager of Project Serfy?"`            | Returns project manager name          |
| `"Show all employees in Project Indreed."`          | Full roster for Indreed               |
| `"How many people are on team Kaary?"`              | Team headcount for Kaary              |
| `"Which project has the most employees?"`           | Top project by headcount              |

**Response includes:**

- Project name and manager
- Total team size
- Number of seated employees (with seat numbers)
- Number of employees awaiting allocation

**Example Response:**

```
Project 'Talos' (Manager: Deepa Rao) has 98 members.
Seated: 87 (Anita Sharma (Seat F3-A2-14), Rajesh Nair (Seat F3-A2-15), ...)
Unseated/Remote: 11.
```

---

### 4. `office_summary` — Entire Workspace KPI Dashboard

Used when a user asks for a high-level overview of the entire office's occupancy and allocation status.

**Example Prompts:**

| Prompt                                                 | What happens                   |
| ------------------------------------------------------ | ------------------------------ |
| `"Give me an office summary."`                       | Full workspace statistics      |
| `"What are the total seat stats?"`                   | All seat status counts         |
| `"Show workspace utilization metrics."`              | Occupancy rate and KPIs        |
| `"How many employees are awaiting seat allocation?"` | Pending allocation queue count |
| `"What is the total seating capacity?"`              | Total inventory count          |
| `"How many inactive employees are there?"`           | Inactive employee count        |

**Response includes:**

- Total seats (all floors)
- Occupied / Available / Reserved / Maintenance counts
- Overall utilization %
- Total employee count
- Awaiting allocation count

**Example Response:**

```
Office Occupancy Summary:
- Total Seats: 5,500
- Occupied: 4,000 (72.7% utilization)
- Available: 1,350
- Reserved: 100
- Maintenance: 50
- Total Employees: 5,000
- Awaiting Assignment: 1,000
```

---

### 5. `neighbors` — Who Sits Near an Employee

Used when a user wants to find who is sitting adjacent to someone — same bay, zone, or floor.

**Example Prompts:**

| Prompt                                      | What happens                                         |
| ------------------------------------------- | ---------------------------------------------------- |
| `"Who is sitting near me?"`               | Lists teammates in same bay as first active employee |
| `"Who sits near Priya?"`                  | Finds Priya's seat → lists bay neighbours           |
| `"Who is next to Amit?"`                  | Adjacency search around Amit's desk                  |
| `"Who are the neighbors of EMP-00042?"`   | Code-based neighbor lookup                           |
| `"Show teammates around rahul@ethara.io"` | Email-based neighbor lookup                          |

**Proximity search order:**

1. Same bay (highest priority — direct desk neighbors)
2. Same zone (if no bay neighbors found)
3. Same floor (fallback)

**Example Response:**

```
Sitting near Amit Kumar in Bay 3 (Floor 2, Zone B):
Priya Singh (Seat F2-B3-41), Ravi Menon (Seat F2-B3-43), Kavya Nair (Seat F2-B3-44).
```

---

### 6. `allocate_joiner` — Allocate a Seat for a New Employee

Used when HR/Admin wants to assign a desk to a newly joined employee using the smart proximity heuristic engine.

**Example Prompts:**

| Prompt                                                  | What happens                                                            |
| ------------------------------------------------------- | ----------------------------------------------------------------------- |
| `"Allocate a seat for a new employee joining today."` | Picks first employee in`Awaiting Allocation` queue and auto-allocates |
| `"Assign a desk to Anjali."`                          | Finds Anjali in the queue and allocates                                 |
| `"Give amit.new@ethara.io a seat."`                   | Email-based allocation trigger                                          |
| `"Seat the next employee in the queue."`              | Takes first unallocated employee                                        |
| `"Allocate seat for EMP-05000."`                      | Code-based allocation trigger                                           |

**Allocation heuristic (from `allocation_logic.py`):**

1. Same bay as their project team → highest priority
2. Same zone as their project team
3. Same floor as their project team
4. Any available seat (fallback)

**Example Response:**

```
Successfully allocated seat F3-A2-18 (Floor 3, Zone A, Bay 2) for Anjali Verma
(anjali.verma@ethara.io) near their project team using proximity heuristics.
```

---

## 🔄 Intent Routing Flow (Technical Detail)

```
User Query: "Who is sitting near Rahul?"
       ↓
LLM (Gemini) outputs:
  { "intent": "neighbors", "search_term": "Rahul" }
       ↓
Backend dispatches to local parser:
  parse_and_respond_local("who is sitting near Rahul", db)
       ↓
1. DB query: Find employee named "Rahul" where status = Active
2. Find active SeatAllocation for that employee → get seat.floor, zone, bay
3. Query all SeatAllocations where floor=X, zone=Y, bay=Z (limit 5)
4. Build human-readable answer with names and seat numbers
       ↓
Response: { "answer": "...", "intent": "neighbors", "data": {...} }
```

---

## 📡 API Usage

**Endpoint:** `POST /ai/query`

**Request:**

```json
{
  "query": "Where is Amit sitting?"
}
```

**Response:**

```json
{
  "answer": "Amit Kumar (Code: EMP-00042, Email: amit.kumar@ethara.io) is assigned to Project Indigo and sits at Seat F2-B3-42 (Floor 2, Zone B, Bay 3).",
  "intent": "employee_seat",
  "data": {
    "employee_name": "Amit Kumar",
    "employee_email": "amit.kumar@ethara.io",
    "employee_code": "EMP-00042",
    "project": "Indigo",
    "seat_number": "F2-B3-42",
    "floor": 2,
    "zone": "B",
    "bay": 3
  }
}
```

**Test it live:** [https://ethara-ai-sms.onrender.com/docs#/AI%20Assistant/post_ai_query_ai_query_post](https://ethara-ai-sms.onrender.com/docs)

---

## 🛡️ Error Handling

| Scenario              | Behaviour                                           |
| --------------------- | --------------------------------------------------- |
| No API key configured | Falls back to local regex parser automatically      |
| LLM API call fails    | Falls back to local regex parser (exception caught) |
| Employee not found    | Returns helpful guidance message                    |
| No seats available    | Returns clear status with count = 0                 |
| Unknown query         | Returns example prompts to guide the user           |

**Unknown Intent Response:**

```
I'm not sure how to answer that. You can ask me questions like:
'Where is Amit sitting?', 'Who sits near Amit?', 'Allocate a seat for Amit',
'How many available seats are on Floor 3?', or 'Give me an office summary'.
```

---

## 📁 Source Files

| File                                                                                    | Role                                                       |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [`backend/app/ai_assistant.py`](./backend/app/ai_assistant.py)                         | Core AI logic: LLM routing + local fallback parser         |
| [`backend/app/routers/ai.py`](./backend/app/routers/ai.py)                             | FastAPI route:`POST /ai/query`                           |
| [`backend/app/allocation_logic.py`](./backend/app/allocation_logic.py)                 | Proximity heuristic seat allocation engine                 |
| [`frontend/src/components/AIAssistant.tsx`](./frontend/src/components/AIAssistant.tsx) | Chat UI component                                          |
| [`backend/app/schemas.py`](./backend/app/schemas.py)                                   | `AIQueryRequest` and `AIQueryResponse` Pydantic models |
