# Ethara Seat Allocation & Project Mapping System – AI Prompt

The prompt should instruct the AI to produce a full-stack design and plan covering **architecture, data model, backend APIs, seat allocation logic, AI assistant, frontend UI, testing, deployment, and documentation**. Emphasize a **clean, scalable solution** with best practices, rather than a quick hack. For example:

- **Architecture & Stack:** Instruct the AI to propose a modular architecture. For instance: *“Design a scalable system architecture for Ethara’s seat allocation and project mapping system, including a React/Next.js frontend, a Python FastAPI backend with REST APIs, and a PostgreSQL database. Consider using a modular (or microservices) approach to separate concerns (employees, projects, seats, AI assistant). Use containerization (Docker) and deploy on cloud platforms like Railway or Vercel. Emphasize maintainability, fault isolation, and scalability.”*  

  Such an approach aligns with industry best practices: breaking the system into services improves scalability and ease of maintenance, and using an API gateway with microservices is common for enterprise applications. The backend can use FastAPI to define clear REST endpoints for each service, and the frontend can use React/Next.js with Tailwind CSS for rapid UI development.

- **Database & Data Model:** The AI should define a normalized relational schema. For example: *“Design a PostgreSQL schema with tables for `employees`, `projects`, `seats`, and `seat_allocations`. Each employee row includes fields like `id`, `name`, `email`, `department`, `role`, `joining_date`, `status`, and `project_id`. The `projects` table lists project names and managers. The `seats` table stores `floor`, `zone`, `bay`, `seat_number`, and `status`. The `seat_allocations` table links an `employee_id` to a `seat_id` and `project_id` with allocation dates and status. Enforce uniqueness: one active seat per employee and vice versa (e.g. with unique constraints and transactions).”*  

  The AI should ensure data integrity. For instance, it can cite locking/transaction strategies: using a database transaction with `SELECT ... FOR UPDATE SKIP LOCKED` ensures that two concurrent processes cannot claim the same seat. Unique indexes on `(floor, zone, bay, seat_number)` and on active allocations can prevent duplicate assignments. This follows common database design for scheduling/booking systems (analogous to airline check-in examples).

- **Backend APIs:** The prompt should enumerate required REST endpoints. For example: *“List the REST API endpoints: CRUD for employees (`POST /employees`, `GET /employees`, etc.), projects (`POST /projects`, `GET /projects`, etc.), seats (`POST /seats`, `GET /seats`, `GET /seats/available`), seat allocation (`POST /seats/allocate`, `POST /seats/release`), and dashboard endpoints (`GET /dashboard/summary`, `/dashboard/project-utilization`, `/dashboard/floor-utilization`). Describe the request/response format. Emphasize input validation and appropriate HTTP status codes.”*  

  FastAPI’s use of Pydantic models and automatic validation/schemas can be mentioned here. The AI should ensure that duplicate seat allocations are prevented by checking constraints in business logic and using transactions.

- **Seat Allocation Logic:** Instruct how to implement allocation rules. For example: *“Describe the algorithm to allocate a seat to a new joiner: check for available seats in the same floor/zone as the team, prefer adjacent seats, otherwise suggest alternatives. Use a transaction to update seat status from Available to Occupied. If no seat in preferred zone, query other zones and pick closest. After allocation or release, ensure released seats become Available again.”*  

  The AI should incorporate locking to avoid race conditions: for example, use `FOR UPDATE SKIP LOCKED` on seat selection queries to atomically reserve an available seat. It should also note the rule “one employee, one active seat” and “no duplicate seat numbers” as core constraints.

- **AI Assistant (Natural Language Queries):** The prompt must cover building a chat interface or endpoint. For example: *“Implement an AI-driven assistant endpoint (`POST /ai/query`) that takes a natural-language `query` (like ‘Where is my seat? My email is X’) and returns an answer. Use an LLM (OpenAI/Claude/Gemini) or a rule-based parser. Illustrate how to fetch relevant data (e.g. look up the employee by email then respond with their seat and project). Provide sample prompts or system messages. If using an LLM, show how to constrain its output format (e.g. JSON with `answer`). If not using an API, build a keyword-intent parser fallback: map “where is my seat” -> find seat by email, “who is on project X” -> query DB, etc.”*  

  This can reference known solutions: OfficeSpace’s Ossi is an AI assistant for desk queries, illustrating feasibility. One can prompt the LLM with context: *“Employee Amit (email amit@ethara.ai) has seat Floor 2 Zone B Bay 4 Seat B4-23 on Project Talos.”* as example responses. This section should emphasize testing the AI with various queries and ensuring factual answers.

- **Frontend & UI:** The prompt should specify a user-friendly interface. For example: *“Design a responsive React/Next.js frontend using Tailwind CSS. Include pages or components for: employee lookup (by name/ID/email), project view (list team members, their seats), seat map view (visual floor plans or lists filtered by floor/zone), and admin forms (upload CSV, allocate seat). Add search bars and filters for employees, projects, floor, zone, and seat status. Build a Dashboard page with summary cards (total employees, total seats, counts of occupied/available/reserved) and charts for project-wise and floor-wise utilization.”*  

  Tailwind is recommended for rapid, consistent UI development. If floor plans are needed, mention using an interactive map or grid (optional). The AI should ensure clean component structure, e.g. use reusable components for tables, cards, modals. It should also mention handling API calls (fetching from the FastAPI backend).

- **Search & Filtering:** The prompt should remind to implement search endpoints and UI. For example: *“Implement search/filter functionality on the frontend and backend. For instance, `GET /employees?name=Amit&project=Talos` should return matching employees. Use database indexes on searchable fields (`name`, `email`, `project_id`, `floor`, `zone`, `status`) for fast lookup.”* 

  This ensures users can query the system by name, ID, email, project, floor, zone, and status as required.

- **Dashboard & Metrics:** The prompt should have AI build summary endpoints and visuals. For example: *“Create dashboard APIs that return aggregate counts: total seats, occupied, available, reserved; employee count; project-wise and floor-wise occupancy statistics; new joiners awaiting allocation. Then, in the frontend, display these as summary cards and charts (e.g., bar or pie charts).”*  

  Use chart libraries (e.g. Chart.js or Recharts) to plot the data. This aligns with common practice in office space analytics (though we need no specific citation, the concept of workplace analytics is widespread). The prompt can suggest that the charts update dynamically after each allocation or release.

- **Testing & Validation:** The prompt should include testing. For example: *“Include unit tests for each backend endpoint (using pytest) and integration tests for allocation logic. Verify business rules (no duplicate seats, correct status transitions). Provide sample seed data (5,000 employees, 5,500 seats, etc.) to test scalability. Write front-end tests (Jest or Cypress) for UI components and user flows.”*  

  Testing strategies ensure correctness. Although not cited, this is implied by “validated correctness” in instructions.

- **Deployment:** The prompt must cover deployment instructions. For example: *“Describe how to containerize the app (Docker for backend and possibly frontend). Provide a Docker Compose or Dockerfiles. Suggest hosting: e.g., deploying FastAPI on Railway/Render with a connected PostgreSQL, and the React/Next.js app on Vercel or Netlify. Include environment variables management and a CI/CD pipeline (GitHub Actions) to run tests and auto-deploy on push.”*  

  This matches the allowed deployment platforms (Railway, Render, Vercel, etc.). Emphasize that the live frontend and backend URLs should be produced, along with a README.

- **Documentation & AI Prompts:** Finally, the prompt should tell the AI to generate required documentation. For example: *“Generate a README with project overview, tech stack, setup instructions, and API documentation (Swagger or Postman). Outline the schema (database diagram) and sample seed data. Also produce an `AI_PROMPTS.md` file listing all AI prompts used in the process (for planning, DB design, backend, frontend, AI assistant, debugging, deployment). For each prompt, note what was correct/incorrect and what was manually fixed.”*  

  This ensures compliance with the submission checklist and AI tool usage requirements.

Throughout the prompt, stress **clean code structure and maintainability**. For instance: *“Write clean, modular code with proper separation of concerns. Use a layered architecture (e.g., routers, services, repositories) for the backend, and organized components/hooks in the frontend. Document code and use linting/formatting.”* 

By combining these instructions into a single comprehensive prompt, the AI assistant will generate an end-to-end plan and code for the seat allocation system that fulfills all requirements and follows best practices for scalability and maintainability. Each section can be tested and refined iteratively, ensuring the final solution is robust, cleanly designed, and fully documented. 

**Sources:** Best practices for system architecture and design; concurrency control in seat booking; AI-driven workspace assistants; rapid UI development with Tailwind CSS.