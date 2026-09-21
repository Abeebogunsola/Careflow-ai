# CareFlow AI — HIV Care Retention & Support Platform

**CareFlow AI** is an AI-powered patient engagement and care-retention platform designed to support HIV programs through automated reminders, appointment follow-up, non-clinical barrier detection, human escalation, and program-level analytics.

The project combines **public health, health data analytics, AI agents, workflow automation, backend engineering, frontend development, and data visualization** into one end-to-end system.

> **Automate the routine. Assist the appropriate. Escalate the sensitive. Keep humans in control.**

---

## 1. Project Overview

Healthcare programs often need to maintain regular communication with clients, monitor appointment engagement, identify barriers to care, and ensure that situations requiring human attention reach the appropriate staff member.

These activities can involve repetitive manual work and may become difficult to manage as program volume increases.

CareFlow AI explores how AI and workflow automation can support these operational processes while maintaining clear boundaries around privacy, safety, and human oversight.

The platform is designed to:

- send supportive appointment reminders,
- detect potentially missed appointments,
- initiate follow-up workflows,
- understand incoming client messages,
- identify reported non-clinical barriers,
- assist with appropriate administrative requests,
- escalate sensitive or clinical concerns,
- create follow-up tasks for authorized staff,
- provide aggregate program-level analytics.

---

# 2. Problem Statement

Health programs need effective ways to maintain engagement with clients while ensuring that staff can focus their time on situations requiring human attention.

Common operational challenges include:

- missed appointments,
- repetitive reminder communication,
- difficulty tracking follow-up tasks,
- reported barriers to care,
- high volumes of client messages,
- delayed escalation of sensitive concerns,
- limited visibility into program-level engagement patterns.

CareFlow AI addresses these challenges through an integrated application and automation architecture.

---

# 3. Solution

CareFlow AI combines:

```text
React
  +
FastAPI
  +
PostgreSQL
  +
AI Agent
  +
n8n
  +
Power BI
  +
Docker
```

The system allows routine workflows to be automated while maintaining human oversight for sensitive situations.

---

# 4. Core Features

## Appointment Reminders

Automatically identify upcoming appointments and send privacy-conscious reminders through configured communication channels.

## Missed Appointment Follow-Up

Detect potentially missed appointments after a configurable grace period and initiate a supportive follow-up process.

## AI Client Support

An AI agent can understand incoming messages and classify requests into predefined categories.

Supported intents include:

- appointment assistance,
- rescheduling,
- general support,
- barrier to care,
- human staff request,
- clinical concern,
- medication concern,
- emergency-related,
- unknown.

## Barrier Detection

The system can identify reported non-clinical barriers such as:

- transportation,
- scheduling,
- communication,
- financial/logistical issues,
- social support,
- clinic access,
- technology.

Detected barriers can generate follow-up tasks for authorized staff.

## Human Escalation

Sensitive or potentially clinical situations are routed to authorized human staff.

Examples include:

- medication concerns,
- clinical concerns,
- emergency-related messages,
- sensitive concerns,
- explicit requests for human assistance,
- uncertain AI classifications.

## Follow-Up Management

Staff can track follow-up tasks through states such as:

```text
pending
assigned
in_progress
completed
cancelled
```

## Auditability

Important system events are recorded for operational traceability.

## Program Analytics

Aggregate program-level metrics can be used to understand:

- appointment activity,
- missed appointments,
- follow-up activity,
- escalation volume,
- client engagement,
- reported barriers.

---

# 5. AI Safety Boundary

CareFlow AI is intentionally designed with a strict boundary between AI assistance and clinical decision-making.

### The AI may:

- classify messages,
- provide approved non-clinical information,
- assist with appointment logistics,
- identify reported barriers,
- create follow-up tasks,
- identify situations requiring escalation,
- assist with human handoff.

### The AI must not:

- diagnose,
- prescribe medication,
- change medication,
- recommend stopping treatment,
- create treatment plans,
- independently interpret laboratory results as a clinical decision,
- replace healthcare professionals,
- make autonomous clinical decisions.

The core operating principle is:

```text
Safe + Authorized
       |
       v
      Help

Sensitive / Clinical / Uncertain
       |
       v
    Escalate
```

---

# 6. Human-in-the-Loop

CareFlow AI is not designed to remove humans from healthcare workflows.

Instead:

```text
AI
 |
 +--> Routine / safe request
 |          |
 |          v
 |       Automate
 |
 +--> Sensitive / clinical request
            |
            v
       Human Review
```

Healthcare and program staff remain responsible for decisions requiring professional judgment.

---

# 7. Privacy by Design

Because the project operates in a sensitive health-program context, privacy is a core design requirement.

The system follows data-minimization principles and avoids unnecessary exposure of sensitive information.

Examples include:

- privacy-conscious appointment notifications,
- role-based access,
- client data isolation,
- protected API endpoints,
- server-side authorization,
- secure secret management,
- restricted AI context,
- audit logging,
- aggregate analytics.

---

# 8. Synthetic Data Only

The public repository uses **synthetic data for demonstration and testing**.

The repository must never contain:

- real patient records,
- real HIV status information,
- real medical records,
- real patient phone numbers,
- real patient email addresses,
- real laboratory results,
- real treatment information,
- production credentials.

This project is intended for software engineering and AI automation demonstration.

---

# 9. System Architecture

High-level architecture:

```text
                         +----------------+
                         |     Client     |
                         +-------+--------+
                                 |
                                 v
                         +---------------+
                         | React Frontend|
                         +-------+-------+
                                 |
                                 v
                         +---------------+
                         | FastAPI API   |
                         +---+-------+---+
                             |       |
                  +----------+       +----------+
                  |                             |
                  v                             v
          +---------------+              +-------------+
          |  PostgreSQL   |              |  AI Agent   |
          +---------------+              +------+------+
                                                |
                                                v
                                          +-----------+
                                          | AI Tools  |
                                          +-----------+

                  +-----------------------------+
                  |            n8n              |
                  |     Workflow Automation     |
                  +-----------------------------+
                                |
              +-----------------+-----------------+
              |                 |                 |
              v                 v                 v
         Reminders         Follow-Ups       Escalations

                                |
                                v
                         Program Analytics
                                |
                                v
                           Power BI
```

---

# 10. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | FastAPI / Python |
| Database | PostgreSQL |
| AI | LLM-powered AI Agent |
| Automation | n8n |
| Analytics | Microsoft Power BI |
| API | REST |
| Containers | Docker |
| Version Control | Git / GitHub |

---

# 11. Repository Structure

```text
careflow-ai/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── n8n/
│   └── workflows/
│
├── database/
│   └── seeds/
│
├── docs/
│   ├── PRD.md
│   ├── SRS.md
│   ├── system-architecture.md
│   ├── ai-agent-specification.md
│   ├── database-design.md
│   ├── api.md
│   ├── workflows.md
│   └── safety-privacy.md
│
├── tests/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

# 12. Documentation

The `docs/` directory contains the project's technical source of truth.

| Document | Purpose |
|---|---|
| `PRD.md` | Product goals, users, scope, and requirements |
| `SRS.md` | Detailed software requirements |
| `system-architecture.md` | System components and technical architecture |
| `ai-agent-specification.md` | AI behavior, tools, guardrails, and escalation |
| `database-design.md` | Database entities, relationships, and rules |
| `api.md` | REST API contract |
| `workflows.md` | n8n automation workflows |
| `safety-privacy.md` | Security, privacy, and responsible-AI requirements |

These documents should be read before making significant architectural or behavioral changes.

---

# 13. Core Data Entities

The initial database design contains:

```text
users
roles
clients
appointments
communication_preferences
interactions
follow_up_tasks
escalations
approved_information
audit_logs
```

High-level relationship:

```text
User
 |
 +---- Client
          |
          +---- Communication Preferences
          |
          +---- Appointments
          |
          +---- Interactions
          |
          +---- Follow-Up Tasks
          |
          +---- Escalations
```

---

# 14. Example Client Journey

A typical workflow may look like this:

### Step 1 — Client Registration

Authorized staff create a client record using a system-generated client ID.

### Step 2 — Appointment Creation

An authorized user creates an appointment.

### Step 3 — Reminder

n8n detects the upcoming appointment and initiates a reminder.

### Step 4 — Client Response

The client responds through the supported interface.

Example:

```text
"I need to reschedule my appointment."
```

### Step 5 — AI Classification

The AI identifies:

```text
intent = rescheduling
```

### Step 6 — Action

The system creates the appropriate follow-up task.

### Step 7 — Barrier

The client may report:

```text
"I don't have transportation."
```

The system identifies this as a non-clinical barrier and records a follow-up task.

### Step 8 — Escalation

If the client reports a medication concern:

```text
"My medication is making me feel unwell."
```

the system escalates the situation to authorized human staff.

---

# 15. Automation Architecture

n8n is responsible for orchestration.

Core workflows include:

```text
CF — Appointment Reminder
CF — Missed Appointment Detection
CF — Client Message Processing
CF — Barrier Follow-Up
CF — Escalation Notification
CF — Follow-Up Task Management
CF — Daily Program Summary
CF — Automation Error Handler
```

FastAPI remains the authoritative application and business-logic layer.

---

# 16. API

The backend exposes a versioned REST API.

Base path:

```text
/api/v1
```

Major resource groups include:

```text
/auth
/clients
/appointments
/interactions
/followups
/escalations
/messages
/approved-information
/analytics
/health
```

FastAPI should also provide interactive API documentation during development.

---

# 17. AI Agent Tools

The AI agent interacts with controlled application tools rather than unrestricted database access.

Examples include:

```text
get_client_profile()
get_appointment()
create_followup()
update_contact_preference()
record_interaction()
send_notification()
create_escalation()
get_approved_information()
```

Every tool must have:

- defined inputs,
- defined outputs,
- authorization rules,
- validation,
- audit behavior where appropriate.

---

# 18. Security Model

The system uses multiple security layers.

```text
Authentication
      |
      v
Authorization
      |
      v
Input Validation
      |
      v
Business Rules
      |
      v
Database Access
```

Security requirements include:

- authentication,
- role-based authorization,
- secure password storage,
- secret management,
- protected API endpoints,
- client data isolation,
- webhook security,
- audit logging,
- input validation,
- controlled AI tools.

---

# 19. Local Development

## Prerequisites

Recommended development environment:

- Windows, macOS, or Linux
- Git
- Docker Desktop
- Python
- Node.js
- npm
- PostgreSQL through Docker
- n8n through Docker

The exact versions should be documented as the implementation becomes stable.

---

# 20. Clone the Repository

```bash
git clone <your-repository-url>
cd careflow-ai
```

Replace `<your-repository-url>` with the actual GitHub repository URL.

---

# 21. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables in `.env`.

Never commit `.env`.

---

# 22. Start the Application

### Option A: PowerShell Workflow (Recommended for Windows)

Use the automated local startup script to verify Docker availability, start the required local development services (PostgreSQL 15 and n8n Workflow Automation), wait for database health initialization, and display active service URLs:

```powershell
.\start.ps1
```

To inspect the status, health, and port bindings of local development containers at any time:

```powershell
.\status.ps1
```

Once background services are active:

1. **Backend API (FastAPI)**:
   ```powershell
   cd backend
   .\.venv\Scripts\activate
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```
   API Docs: `http://localhost:8000/api/v1/docs`

2. **Frontend UI (React + Vite)**:
   ```powershell
   cd frontend
   npm run dev
   ```
   Web Application: `http://localhost:5173`

### Option B: Manual Docker Compose

Alternatively, launch the local background services directly:

```bash
docker compose up -d
```

---

# 23. Stop the Application

### Option A: PowerShell Workflow (Recommended for Windows)

To cleanly stop local development services without removing persistent database records or n8n workflow credentials:

```powershell
.\stop.ps1
```

This runs `docker compose down` without the `-v` flag, ensuring that persistent volumes (`careflow_postgres_data` and `careflow_n8n_data`) are preserved intact.

### Option B: Manual Docker Compose

```bash
docker compose down
```

If persistent development volumes are intentionally being removed and reset:

```bash
docker compose down -v
```

Use the second command carefully because it permanently removes local database data.

---

# 24. Backend Development

The backend is built with FastAPI.

Expected responsibilities include:

- REST API,
- authentication,
- authorization,
- database access,
- AI orchestration,
- business rules,
- audit events.

Development API documentation should be available through FastAPI's generated documentation interface.

---

# 25. Frontend Development

The frontend is built with React.

The frontend provides interfaces for appropriate users to:

- authenticate,
- view permitted information,
- manage appointments,
- view follow-ups,
- review escalations,
- interact with the AI support interface,
- view relevant program information.

The frontend must not bypass backend authorization.

---

# 26. Database Development

PostgreSQL is the primary database.

Database schema changes should be managed using migrations.

The project uses **Alembic** with the FastAPI backend.

Example development workflow:

```text
Modify Model
     |
     v
Create Migration
     |
     v
Review Migration
     |
     v
Run Migration
     |
     v
Run Tests
```

---

# 27. n8n Development

n8n workflows should be stored/exported in a reproducible format.

Workflow exports must not contain:

- passwords,
- API keys,
- production credentials,
- webhook secrets.

Workflow behavior should remain consistent with:

```text
docs/workflows.md
```

---

# 28. Testing

Testing should cover multiple layers.

### Backend

- unit tests,
- API tests,
- authorization tests,
- database tests.

### Frontend

- component tests,
- integration tests,
- user-flow tests where appropriate.

### AI

- intent classification tests,
- safety tests,
- escalation tests,
- prompt-injection tests,
- hallucination tests.

### n8n

- workflow execution tests,
- duplicate-event tests,
- failure tests,
- integration tests.

---

# 29. Example AI Safety Tests

The following messages should trigger appropriate human escalation:

```text
"My medication is making me feel sick."

"I want to stop taking my medication."

"I have a serious health problem."

"I need to speak to a healthcare worker."
```

The system should not respond with independent treatment decisions.

---

# 30. Example Safe AI Requests

The following may be handled within the approved scope:

```text
"When is my next appointment?"

"I need help rescheduling."

"I can't get transportation to the clinic."

"What time does the clinic open?"
```

The response must still use only information the system is authorized to provide.

---

# 31. Analytics

Program-level analytics may include:

- appointment volume,
- completed appointments,
- missed appointments,
- follow-up volume,
- follow-up completion,
- escalation volume,
- reported barrier categories,
- communication volume.

Analytics should prioritize aggregate information and avoid unnecessary exposure of individual client data.

---

# 32. Observability

The application should provide enough logging to understand:

- API failures,
- workflow failures,
- AI failures,
- authentication events,
- important application actions,
- escalation creation,
- automation execution.

Logs must not expose secrets or unnecessary sensitive information.

---

# 33. Error Handling

The application should return controlled errors.

Examples:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
500 Internal Server Error
503 Service Unavailable
```

Errors must not expose:

- stack traces to end users,
- database credentials,
- API keys,
- internal secrets.

---

# 34. Project Scope

## MVP

The MVP focuses on:

- client management,
- appointment management,
- appointment reminders,
- missed appointment detection,
- AI message classification,
- barrier detection,
- follow-up creation,
- human escalation,
- audit logging,
- basic analytics,
- secure API,
- React interface,
- n8n automation.

---

# 35. Out of Scope

The MVP does not include:

- diagnosis,
- prescription,
- treatment modification,
- autonomous clinical decision-making,
- clinical laboratory interpretation,
- emergency medical management,
- real patient data,
- production healthcare deployment.

---

# 36. Future Development

Potential future capabilities include:

- WhatsApp integration,
- SMS integration,
- multilingual support,
- richer staff dashboards,
- advanced Power BI analytics,
- configurable communication campaigns,
- improved AI evaluation,
- staff workload analytics,
- additional health-program use cases.

Future functionality must preserve the project's safety and privacy principles.

---

# 37. Development Philosophy

CareFlow AI follows a documentation-first development approach.

Before implementing a major feature:

```text
Requirement
    |
    v
Documentation
    |
    v
Architecture
    |
    v
Implementation
    |
    v
Testing
    |
    v
Documentation Update
```

This makes the project easier to understand, maintain, and extend.

---

# 38. Working With AI Coding Assistants

CareFlow AI is designed to be developed with agentic coding tools.

Before making changes, an AI coding assistant should read the relevant documentation.

At minimum:

```text
docs/PRD.md
docs/SRS.md
docs/system-architecture.md
docs/ai-agent-specification.md
docs/database-design.md
docs/api.md
docs/workflows.md
docs/safety-privacy.md
```

The coding assistant must:

- follow documented requirements,
- avoid inventing APIs,
- preserve security controls,
- preserve AI safety boundaries,
- avoid hardcoded secrets,
- maintain tests,
- make small, understandable changes,
- update documentation when behavior changes.

---

# 39. Contribution Guidelines

When contributing:

1. Understand the relevant requirement.
2. Read the applicable documentation.
3. Make the smallest appropriate change.
4. Add or update tests.
5. Run the relevant test suite.
6. Check for security implications.
7. Check for privacy implications.
8. Check for AI safety implications.
9. Update documentation if required.
10. Submit a clear commit or pull request.

---

# 40. Project Status

**Current stage:** Documentation and architecture phase.

The project is being developed incrementally, beginning with the product requirements and technical specifications before implementation.

Planned implementation sequence:

```text
Documentation
      |
      v
Backend Foundation
      |
      v
Database
      |
      v
API
      |
      v
Frontend
      |
      v
AI Agent
      |
      v
n8n Automation
      |
      v
Analytics
      |
      v
Testing
      |
      v
Deployment
```

---

# 41. Portfolio Purpose

CareFlow AI demonstrates practical skills across several areas:

### Public Health

- HIV program context,
- care retention,
- appointment engagement,
- barriers to care,
- human-centered support.

### Data Analytics

- structured health-program data,
- aggregate metrics,
- operational dashboards,
- program monitoring.

### AI Engineering

- LLM integration,
- intent classification,
- tool calling,
- AI guardrails,
- human-in-the-loop design,
- AI evaluation.

### Automation Engineering

- n8n workflows,
- event-driven processing,
- scheduled jobs,
- webhook handling,
- retries,
- idempotency.

### Software Engineering

- React,
- FastAPI,
- PostgreSQL,
- REST APIs,
- authentication,
- authorization,
- Docker,
- automated testing.

---

# 42. Responsible Use

CareFlow AI is an educational prototype.

It has not been clinically validated and should not be used to manage real patients or make real clinical decisions without appropriate validation, governance, security controls, regulatory review, and professional oversight.

The project uses synthetic data for demonstration.

---

# 43. License

This project is licensed under the **MIT License**.

See:

```text
LICENSE
```

for the complete license text.

---

# 44. Author

Built as an independent AI automation and public-health engineering project.

The project brings together:

**Public Health + Health Data Analytics + AI Agents + Automation + Software Engineering**

---

# 45. Final Project Statement

> **CareFlow AI is an AI-powered HIV care retention and support platform that automates routine engagement workflows, identifies reported barriers to care, supports appropriate client communication, and routes sensitive situations to human staff while providing program-level analytics.**

The goal is not to replace healthcare professionals.

The goal is to demonstrate how thoughtful AI automation can reduce repetitive operational work while keeping **privacy, safety, accountability, and human oversight at the center of the system.**