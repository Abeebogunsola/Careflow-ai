# CareFlow AI — System Architecture

**Product:** CareFlow AI  
**Document:** System Architecture  
**Version:** 1.0  
**Status:** Draft  
**Architecture Style:** Modular, API-driven, event-driven  
**Primary Goal:** Reliable AI-assisted patient engagement with human oversight

---

# 1. Architecture Overview

CareFlow AI is designed as a modular system in which each major component has a clearly defined responsibility.

The system consists of:

- React frontend
- FastAPI backend
- PostgreSQL database
- AI support agent
- n8n automation engine
- Notification/messaging layer
- Power BI analytics layer
- Authentication and authorization layer

The architecture follows a key principle:

> **The AI agent should make decisions within a controlled application environment, while the backend remains the source of truth for data, permissions, and business rules.**

The AI should never have unrestricted access to the database or system.

---

# 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       CLIENT         │
                         │                      │
                         │ Web / Messaging UI   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │                      │
                         │ Dashboard / Client   │
                         │ Interaction / Staff  │
                         └──────────┬───────────┘
                                    │
                              REST / HTTPS
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Backend    │
                         │                      │
                         │ API / Auth / Rules   │
                         │ Validation / Tools   │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └─────────────┐
                    ▼                                  ▼
          ┌──────────────────┐               ┌──────────────────┐
          │   PostgreSQL     │               │   AI Agent       │
          │                  │               │                  │
          │ Clients          │               │ Intent           │
          │ Appointments     │               │ Classification   │
          │ Interactions     │               │ Support          │
          │ Tasks            │               │ Escalation       │
          │ Escalations      │               │ Tool Calling     │
          └──────────────────┘               └────────┬─────────┘
                                                       │
                                                Controlled Tools
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │      FastAPI     │
                                              │      Services    │
                                              └──────────────────┘

                         ┌──────────────────────┐
                         │        n8n           │
                         │                      │
                         │ Scheduled Jobs       │
                         │ Reminders            │
                         │ Missed Appointments  │
                         │ Follow-ups           │
                         │ Notifications        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Messaging /          │
                         │ Notification Service │
                         └──────────────────────┘


                         ┌──────────────────────┐
                         │       Power BI       │
                         │                      │
                         │ Program Analytics    │
                         │ Operational Metrics  │
                         └──────────▲───────────┘
                                    │
                                    │ Aggregate Data
                                    │
                         ┌──────────┴───────────┐
                         │ Analytics Data Layer │
                         └──────────────────────┘
```

---

# 3. Architecture Principles

CareFlow AI shall follow these architectural principles.

## 3.1 Backend as Source of Truth

The FastAPI backend is responsible for:

- Business rules
- Data validation
- Authentication
- Authorization
- Database access
- API contracts
- Security enforcement

The AI agent does not override backend rules.

---

## 3.2 AI as a Controlled Component

The AI agent is an application component, not the owner of the system.

The AI may request an action through approved tools.

Example:

```text
AI Agent
   |
   | create_followup()
   v
FastAPI
   |
   | validate permission
   | validate data
   | apply business rules
   v
PostgreSQL
```

The AI should never directly execute unrestricted SQL against PostgreSQL.

---

## 3.3 Human-in-the-Loop

When an interaction falls outside the AI's permitted scope, the system creates an escalation for human review.

```text
Client Message
      |
      v
AI Classification
      |
      +---- Safe / Supported ----> AI Response
      |
      +---- Needs Staff ----------> Escalation
      |
      +---- Uncertain ------------> Escalation
```

---

## 3.4 Event-Driven Automation

Time-based and operational activities should be handled through events and workflows.

Examples:

```text
Appointment approaching
        ↓
Reminder Event
        ↓
n8n Workflow
        ↓
Notification
```

and:

```text
Appointment missed
        ↓
Missed Appointment Event
        ↓
n8n Workflow
        ↓
Follow-up
        ↓
Client Response
        ↓
AI Classification
```

---

# 4. Component Responsibilities

## 4.1 React Frontend

The frontend provides the user interface.

Responsibilities:

- Login interface
- Staff dashboard
- Client management
- Appointment management
- Follow-up queue
- Escalation queue
- Interaction history
- Client communication interface
- Loading states
- Error states

The frontend shall not contain sensitive business logic that should be enforced by the backend.

---

# 5. FastAPI Backend

The FastAPI backend is the central application layer.

Responsibilities:

- REST API
- Authentication
- Authorization
- Request validation
- Business logic
- Database interaction
- AI tool endpoints/services
- Workflow event endpoints
- Audit logging
- Error handling

Suggested structure:

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── clients.py
│   │       ├── appointments.py
│   │       ├── interactions.py
│   │       ├── followups.py
│   │       ├── escalations.py
│   │       ├── messages.py
│   │       └── analytics.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── agents/
│   └── db/
│
└── tests/
```

This is a proposed structure and may be adjusted during implementation.

---

# 6. PostgreSQL Database

PostgreSQL is the primary persistent data store.

The database is responsible for maintaining the system's source-of-truth records.

Core data domains include:

```text
Users
   │
   ├── Roles
   │
Clients
   │
   ├── Appointments
   │
   ├── Interactions
   │
   ├── Follow-ups
   │
   ├── Escalations
   │
   └── Communication Preferences
```

The database shall enforce relationships using foreign keys and appropriate constraints.

---

# 7. AI Agent Architecture

The AI agent operates within a controlled service boundary.

## 7.1 AI Responsibilities

The AI may:

- Understand incoming messages.
- Classify intent.
- Identify supported non-clinical barriers.
- Retrieve approved information.
- Generate supportive responses.
- Request appointment-related actions.
- Create follow-up tasks.
- Create escalations.
- Ask clarifying questions when appropriate.

---

## 7.2 AI Does Not Own Data

The AI should retrieve data through application-controlled tools.

Example:

```text
AI
 |
 +--> get_appointment()
 |
 +--> get_approved_information()
 |
 +--> create_followup()
 |
 +--> create_escalation()
 |
 +--> record_interaction()
```

Each tool call should be validated by the backend.

---

# 8. AI Tool Architecture

AI tools shall follow a controlled interface.

Example:

```text
AI Agent
    |
    v
Tool Request
    |
    v
FastAPI Tool Service
    |
    +--> Authentication
    |
    +--> Authorization
    |
    +--> Input Validation
    |
    +--> Business Rules
    |
    v
PostgreSQL / External Service
```

The agent should not be able to bypass these controls.

---

# 9. n8n Automation Architecture

n8n handles scheduled and event-driven workflows.

Primary responsibilities:

- Appointment reminders
- Missed appointment detection
- Follow-up workflows
- Notification delivery
- Workflow retries
- External service integration
- Workflow-level logging

n8n should not become the primary source of truth for application data.

The FastAPI backend and PostgreSQL database remain the authoritative application layers.

---

# 10. Workflow Communication

The preferred communication pattern is:

```text
n8n
 |
 | HTTP Request
 v
FastAPI API
 |
 v
Business Logic
 |
 v
PostgreSQL
```

Example:

```text
n8n detects upcoming appointment
             |
             v
POST /api/v1/notifications/reminders
             |
             v
FastAPI validates request
             |
             v
Notification created
             |
             v
Interaction recorded
```

---

# 11. API Layer

The API provides communication between application components.

Example API structure:

```text
/api/v1/auth
/api/v1/clients
/api/v1/appointments
/api/v1/interactions
/api/v1/followups
/api/v1/escalations
/api/v1/messages
/api/v1/analytics
```

The exact endpoints shall be defined in `docs/api.md`.

---

# 12. Authentication and Authorization

Authentication verifies who the user is.

Authorization determines what that user is allowed to do.

Example:

```text
User
 |
 v
Authentication
 |
 v
Authenticated User
 |
 v
Role
 |
 +---- Client
 |
 +---- Staff
 |
 +---- Administrator
 |
 v
Permission Check
 |
 v
Requested Resource
```

Authorization shall be enforced by the backend.

The frontend should not be treated as a security boundary.

---

# 13. Data Flow — Client Message

A typical client message shall follow this flow:

```text
Client
  |
  v
Messaging / React Interface
  |
  v
POST /api/v1/messages
  |
  v
FastAPI
  |
  +--> Validate request
  |
  +--> Identify client/session
  |
  +--> Record incoming interaction
  |
  v
AI Agent
  |
  v
Classify intent
  |
  +------------------------+
  |                        |
  v                        v
Supported               Requires Human
  |                        |
  v                        v
Generate Response       Create Escalation
  |                        |
  +------------+-----------+
               |
               v
        Record Interaction
               |
               v
        Return Response
```

---

# 14. Data Flow — Appointment Reminder

```text
PostgreSQL
    |
    | Appointment data
    v
n8n Scheduled Workflow
    |
    v
Find upcoming appointments
    |
    v
Check eligibility
    |
    v
Check communication preference
    |
    v
Generate approved reminder
    |
    v
Send notification
    |
    v
Record result through FastAPI
```

---

# 15. Data Flow — Missed Appointment

```text
Appointment
     |
     v
Appointment time passes
     |
     v
n8n detects missed appointment
     |
     v
FastAPI confirms appointment state
     |
     v
Follow-up created
     |
     v
Supportive message sent
     |
     v
Client responds
     |
     v
AI Agent classifies response
     |
     +-----------------------+
     |                       |
     v                       v
Routine Support          Human Review
     |                       |
     v                       v
Normal Response          Escalation
```

---

# 16. Data Flow — Escalation

```text
Client Message
      |
      v
AI Agent
      |
      v
Clinical / Sensitive / Uncertain
      |
      v
create_escalation()
      |
      v
FastAPI
      |
      v
PostgreSQL
      |
      v
Staff Escalation Queue
      |
      v
Authorized Staff
      |
      v
Review
      |
      v
Resolution
      |
      v
Audit / Interaction Log
```

---

# 17. Analytics Architecture

Operational data shall be transformed into aggregate analytics.

```text
PostgreSQL
     |
     v
Analytics Extraction
     |
     v
Aggregate / De-identified Data
     |
     v
Power BI
```

Power BI shall primarily be used for program-level analytics rather than exposing unnecessary individual client information.

Potential dashboards:

### Program Overview

- Total enrolled clients
- Active clients
- Upcoming appointments
- Missed appointments
- Follow-up status

### Engagement

- Reminder volume
- Reminder delivery
- Client responses
- Re-engagement activity

### Barriers

- Barrier categories
- Barrier frequency
- Follow-up outcomes

### Escalations

- Escalation volume
- Escalation categories
- Open vs resolved
- Resolution time

---

# 18. Security Architecture

Security shall be implemented across multiple layers.

```text
                 Security
                    |
      +-------------+-------------+
      |             |             |
      v             v             v
 Authentication  Authorization  Secrets
      |             |             |
      +-------------+-------------+
                    |
                    v
              FastAPI API
                    |
          +---------+---------+
          |                   |
          v                   v
      PostgreSQL          AI Agent
          |                   |
          v                   v
      Data Access       Controlled Tools
```

Security controls shall include:

- Authentication
- Role-based authorization
- Input validation
- Secure secret management
- HTTPS in production
- Audit logging
- Data minimization
- Controlled AI tool access
- Error handling without secret leakage

---

# 19. AI Safety Boundary

The AI service shall have an explicit boundary.

```text
                    AI Agent
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Support       Logistics    Escalation
          |
          X
          |
    Clinical Decision
    Diagnosis
    Prescription
    Treatment Change
```

The AI must not cross the boundary into autonomous clinical decision-making.

---

# 20. Failure Handling

Every major external dependency can fail.

Potential failures:

```text
React
  |
  X
FastAPI unavailable

FastAPI
  |
  X
PostgreSQL unavailable

AI Agent
  |
  X
LLM provider unavailable

n8n
  |
  X
Notification provider unavailable
```

The system shall handle failures gracefully.

Examples:

- API returns a meaningful error.
- Frontend displays a user-friendly message.
- n8n retries appropriate operations.
- Failed notifications are logged.
- AI failures can fall back to human review.
- Database failures do not result in silent data loss.

---

# 21. Idempotency

Automated workflows must avoid duplicate actions.

Example:

```text
Appointment ID: 123
Reminder Type: 24-hour reminder
```

If the n8n workflow runs twice, the system should not send two identical reminders unintentionally.

A suitable idempotency mechanism may use:

```text
appointment_id
+
reminder_type
+
scheduled_date
```

The exact implementation will be defined during database and workflow design.

---

# 22. Auditability

Important system actions should be traceable.

Example:

```text
Client Message
      |
      v
AI Classification
      |
      v
Tool Call
      |
      v
Backend Action
      |
      v
Database Change
      |
      v
Audit Record
```

This makes it possible to determine:

- What happened?
- When did it happen?
- Which system component performed it?
- Which authorized user was involved?
- What action was taken?

---

# 23. Environment Architecture

Development should be separated from production.

## Development

```text
Developer Machine
      |
      +---- React
      +---- FastAPI
      +---- PostgreSQL
      +---- n8n
      +---- AI Provider
```

Docker may be used to provide consistent development environments.

---

## Production

```text
Internet
   |
HTTPS
   |
Application Infrastructure
   |
   +---- Frontend
   +---- Backend
   +---- Database
   +---- Automation
   +---- AI Provider
```

Production infrastructure is outside the initial MVP scope.

---

# 24. Docker Architecture

The development environment should support containerized services.

Potential services:

```text
docker-compose.yml

services:

  frontend
      |
      +---- React

  backend
      |
      +---- FastAPI

  postgres
      |
      +---- PostgreSQL

  n8n
      |
      +---- Workflow Automation
```

Each service should have a clearly defined responsibility.

---

# 25. Repository Architecture

The repository should eventually follow a structure similar to:

```text
careflow-ai/
│
├── backend/
│
├── frontend/
│
├── n8n/
│
├── database/
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

The exact repository structure may evolve during implementation.

---

# 26. Architectural Boundaries

The following boundaries shall be maintained.

| Component | Responsible For | Should Not Own |
|---|---|---|
| React | User interface | Security/business rules |
| FastAPI | API/business logic | UI rendering |
| PostgreSQL | Persistent data | Workflow orchestration |
| AI Agent | Language understanding/support | Unrestricted data access |
| n8n | Automation/orchestration | Primary application data |
| Power BI | Analytics/visualization | Transaction processing |
| Messaging provider | Message delivery | Application business rules |

---

# 27. Source of Truth

Different components have different sources of truth.

| Domain | Source of Truth |
|---|---|
| Client records | PostgreSQL |
| Appointments | PostgreSQL |
| Interactions | PostgreSQL |
| Follow-ups | PostgreSQL |
| Escalations | PostgreSQL |
| Authentication/authorization | FastAPI + auth system |
| Business rules | FastAPI |
| Workflow orchestration | n8n |
| AI response generation | AI Agent |
| Program analytics | Analytics layer / Power BI |

No component should silently become the authoritative source for another component's domain.

---

# 28. Scalability Considerations

The initial system is a portfolio MVP, but the architecture should allow future growth.

Potential future scaling:

```text
                Load Balancer
                     |
          +----------+----------+
          |                     |
      FastAPI 1              FastAPI 2
          |                     |
          +----------+----------+
                     |
                 PostgreSQL
```

Other future improvements may include:

- Background job processing
- Message queues
- Caching
- Database read replicas
- Dedicated notification services
- Observability infrastructure
- Horizontal scaling

These are not required for the MVP.

---

# 29. Architectural Decision Rules

When adding new functionality, developers and AI coding agents should ask:

1. Which component owns this responsibility?
2. Does the requirement already exist in the PRD or SRS?
3. Does the change introduce a new data entity?
4. Does it change an API contract?
5. Does it affect security?
6. Does it affect AI safety?
7. Does it require a workflow?
8. Does it require a database migration?
9. Does it require new tests?
10. Does the documentation need updating?

---

# 30. AI Coding Agent Rules

AI coding agents must:

- Read this architecture document before making architectural changes.
- Respect component boundaries.
- Avoid putting business logic in React.
- Avoid putting unrestricted database access in the AI agent.
- Avoid using n8n as the primary data store.
- Keep API contracts explicit.
- Keep database changes migration-based.
- Preserve authentication and authorization.
- Preserve AI safety controls.
- Add tests for meaningful changes.
- Update relevant documentation after architectural changes.

An AI coding agent must not introduce a new architectural component merely because it is technically interesting.

The simplest architecture that satisfies the requirements should be preferred.

---

# 31. Architecture Decision Summary

The initial architecture is:

```text
React
  |
  v
FastAPI
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL          AI Agent
                       |
                       v
                 Controlled Tools
                       |
                       v
                    FastAPI

n8n
  |
  v
FastAPI
  |
  v
PostgreSQL

PostgreSQL
  |
  v
Analytics
  |
  v
Power BI
```

This architecture separates:

- User interface
- Application logic
- Persistent data
- AI reasoning
- Workflow automation
- Analytics

while maintaining human oversight over sensitive situations.

---

# 32. Definition of Architecture Complete

The architecture shall be considered sufficiently defined for MVP implementation when:

- Major system components are identified.
- Component responsibilities are defined.
- Data flows are documented.
- API communication boundaries are identified.
- AI boundaries are defined.
- Human escalation is defined.
- Database ownership is defined.
- n8n responsibilities are defined.
- Analytics flow is defined.
- Authentication and authorization boundaries are defined.
- Failure handling principles are documented.
- AI coding-agent rules are documented.

Detailed implementation decisions may be refined in the Database Design, API, AI Agent Specification, and Workflow documents.

---

# 33. Next Technical Documents

After this architecture document, the recommended order is:

```text
01. PRD
      ↓
02. SRS
      ↓
03. System Architecture
      ↓
04. AI Agent Specification
      ↓
05. Database Design
      ↓
06. API Specification
      ↓
07. Workflow Specification
      ↓
08. Safety & Privacy
      ↓
09. Implementation
      ↓
10. Testing
```

The next document should therefore be:

**`docs/ai-agent-specification.md`**

That document will define exactly what the CareFlow AI agent can do, what tools it can call, how it should behave, when it must escalate, what it must refuse, and how an Agentic coding assistant should implement it.