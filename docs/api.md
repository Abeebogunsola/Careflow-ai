# CareFlow AI — API Specification

## 1. Purpose

This document defines the REST API for **CareFlow AI — HIV Care Retention & Support Platform**.

The API is the communication layer between:

- React frontend
- FastAPI backend
- PostgreSQL database
- AI support agent
- n8n automation workflows
- Analytics systems
- Authorized staff users

This document is a technical source of truth for API implementation, integration, testing, and future development.

The API must enforce the product's core principle:

> **AI assists; authorized humans remain responsible for clinical and sensitive decisions.**

---

# 2. API Scope

The API provides functionality for:

1. Authentication and authorization
2. Client management
3. Appointment management
4. Communication and messages
5. Interaction history
6. Follow-up task management
7. Escalation management
8. Approved information retrieval
9. Program-level analytics
10. n8n webhook integration
11. Health and service-status checks

The API must not expose unnecessary clinical or personally identifiable information.

---

# 3. API Architecture

```text
React Frontend
      |
      | HTTPS / REST
      v
FastAPI Backend
      |
      +------------------+
      |                  |
      v                  v
 PostgreSQL          AI Agent
                         |
                         v
                  Approved Tools
                         |
                         v
                    FastAPI Services

n8n Automation
      |
      | REST / Webhooks
      v
FastAPI Backend

Power BI / Analytics
      |
      v
Aggregate API Data
```

The frontend, AI agent, and n8n must not directly access PostgreSQL.

All application data access must go through authorized backend services.

---

# 4. API Principles

The API must follow these principles:

- RESTful resource design
- JSON request and response bodies
- HTTPS in production
- Authentication for protected endpoints
- Role-based authorization
- Input validation
- Consistent error responses
- UUID identifiers
- Pagination for collection endpoints
- Explicit API versioning
- Audit logging for sensitive operations
- Idempotency for automation-sensitive operations
- No secrets in request payloads or source code
- No direct database access from the frontend
- No autonomous clinical decision-making by the AI

---

# 5. Base URL

## Development

```text
http://localhost:8000
```

## API Base Path

```text
/api/v1
```

Example:

```text
http://localhost:8000/api/v1/clients
```

Production deployment must use HTTPS.

The production domain must be configured through environment variables rather than hardcoded into the application.

---

# 6. API Versioning

The initial API version is:

```text
v1
```

All application endpoints must use:

```text
/api/v1/
```

Example:

```text
/api/v1/appointments
```

Breaking changes must result in a new API version rather than silently changing the existing contract.

---

# 7. Authentication

Protected endpoints require authentication.

The initial implementation should use token-based authentication.

Example:

```http
Authorization: Bearer <access_token>
```

Tokens must never be hardcoded into:

- source code
- GitHub repositories
- frontend JavaScript
- n8n workflow exports
- documentation
- test fixtures containing real credentials

Development tokens must use synthetic/test accounts.

---

# 8. Authorization

Authentication determines **who the user is**.

Authorization determines **what the user is allowed to do**.

The API must enforce role-based access control.

## Roles

| Role | Description |
|---|---|
| `client` | Person receiving program support |
| `staff` | Authorized healthcare/program staff |
| `admin` | Authorized administrator/program manager |

---

# 9. Role Permissions

| Resource | Client | Staff | Admin |
|---|---:|---:|---:|
| Own profile | Read/update limited fields | Read | Read/update |
| Other clients | No | Yes | Yes |
| Appointments | Own | Yes | Yes |
| Interactions | Own | Yes | Yes |
| Follow-ups | Limited | Yes | Yes |
| Escalations | No | Yes | Yes |
| Approved information | Read | Read | Create/update/delete |
| Analytics | No | Limited | Yes |
| User management | No | No | Yes |
| Audit logs | No | Limited | Yes |

Actual permissions must be enforced server-side.

The frontend must never be trusted to enforce authorization.

---

# 10. HTTP Methods

The API uses standard HTTP methods.

| Method | Purpose |
|---|---|
| `GET` | Retrieve data |
| `POST` | Create a resource or perform an action |
| `PATCH` | Partially update a resource |
| `PUT` | Replace a resource when required |
| `DELETE` | Remove a resource when permitted |

Sensitive records should generally be deactivated or retained according to the data-retention policy rather than physically deleted.

---

# 11. HTTP Status Codes

| Status | Meaning |
|---|---|
| `200` | Successful request |
| `201` | Resource created |
| `202` | Request accepted for asynchronous processing |
| `204` | Successful request with no response body |
| `400` | Invalid request |
| `401` | Authentication required/invalid |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `409` | Conflict |
| `422` | Validation error |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
| `503` | Service temporarily unavailable |

---

# 12. Standard Response Format

Successful responses should use a predictable structure.

Example:

```json
{
  "data": {
    "id": "client-uuid",
    "status": "active"
  }
}
```

Collection responses should include pagination information.

Example:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

---

# 13. Standard Error Format

Errors should return a consistent structure.

Example:

```json
{
  "error": {
    "code": "CLIENT_NOT_FOUND",
    "message": "The requested client could not be found.",
    "details": null
  }
}
```

Validation errors may include field-level information.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": {
      "phone_number": "Invalid phone number format."
    }
  }
}
```

Error responses must not expose:

- database credentials
- stack traces
- API keys
- internal secrets
- unnecessary personal information
- internal infrastructure details

---

# 14. Health Endpoint

## `GET /api/v1/health`

Checks whether the API is operational.

### Authorization

Public/internal health check depending on deployment configuration.

### Response

```json
{
  "data": {
    "status": "ok",
    "database": "ok"
  }
}
```

The endpoint should not expose sensitive infrastructure information.

---

# 15. Authentication Endpoints

## `POST /api/v1/auth/login`

Authenticates a user.

### Request

```json
{
  "email": "staff@example.test",
  "password": "test-password"
}
```

### Response

```json
{
  "data": {
    "access_token": "<token>",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

Production credentials must never be included in source code or documentation.

---

## `GET /api/v1/auth/me`

Returns information about the currently authenticated user.

### Response

```json
{
  "data": {
    "id": "user-uuid",
    "role": "staff"
  }
}
```

Only information necessary for application functionality should be returned.

---

# 16. Client Endpoints

## `POST /api/v1/clients`

Creates a new client record.

### Authorization

`staff` or `admin`

### Request

Example:

```json
{
  "external_reference": "CLIENT-0001",
  "preferred_name": "Example User",
  "communication_channel": "whatsapp",
  "status": "active"
}
```

### Response

```json
{
  "data": {
    "id": "client-uuid",
    "external_reference": "CLIENT-0001",
    "status": "active"
  }
}
```

### Validation

The API must validate:

- required fields
- supported communication channels
- supported client statuses
- identifier format
- duplicate records where applicable

---

## `GET /api/v1/clients`

Returns a paginated list of clients.

### Authorization

`staff` or `admin`

### Query Parameters

```text
?page=1&page_size=20&status=active
```

Optional filters may include:

- status
- communication channel
- enrollment state

### Response

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 0
  }
}
```

The endpoint must not return unnecessary sensitive information.

---

## `GET /api/v1/clients/{client_id}`

Returns a specific client.

### Authorization

- Client: own record only
- Staff: authorized clients
- Admin: authorized clients

---

## `PATCH /api/v1/clients/{client_id}`

Updates permitted client information.

### Authorization

`staff` or `admin`, with limited self-service fields for clients.

Only explicitly permitted fields may be modified.

---

# 17. Appointment Endpoints

## `POST /api/v1/appointments`

Creates an appointment.

### Authorization

`staff` or `admin`

### Request

```json
{
  "client_id": "client-uuid",
  "scheduled_at": "2026-10-01T10:00:00Z",
  "status": "scheduled"
}
```

### Response

```json
{
  "data": {
    "id": "appointment-uuid",
    "client_id": "client-uuid",
    "scheduled_at": "2026-10-01T10:00:00Z",
    "status": "scheduled"
  }
}
```

---

## `GET /api/v1/appointments`

Returns appointments.

### Query Parameters

```text
?page=1&page_size=20&status=scheduled
```

Optional filters:

- client ID
- appointment status
- date range

---

## `GET /api/v1/appointments/{appointment_id}`

Returns an appointment.

---

## `PATCH /api/v1/appointments/{appointment_id}`

Updates an appointment.

Possible status values:

```text
scheduled
completed
missed
cancelled
rescheduled
```

The API must prevent invalid status transitions where applicable.

---

# 18. Interaction Endpoints

Interactions record communication between the client, system, AI, and authorized staff.

## `POST /api/v1/interactions`

Creates an interaction.

### Request

```json
{
  "client_id": "client-uuid",
  "direction": "incoming",
  "interaction_type": "message",
  "channel": "whatsapp",
  "content": "I need help rescheduling my appointment."
}
```

### Response

```json
{
  "data": {
    "id": "interaction-uuid",
    "client_id": "client-uuid",
    "interaction_type": "message",
    "created_at": "2026-10-01T10:00:00Z"
  }
}
```

Interaction content should be handled according to the privacy and retention requirements.

---

## `GET /api/v1/interactions`

Returns authorized interaction history.

Filters may include:

```text
client_id
channel
interaction_type
direction
start_date
end_date
```

---

# 19. Message Endpoint

## `POST /api/v1/messages`

Receives a client message for processing.

This endpoint is the primary application entry point for AI-assisted communication.

### Request

```json
{
  "client_id": "client-uuid",
  "message": "I missed my appointment. Can I reschedule?",
  "channel": "web"
}
```

### Processing Flow

```text
Client Message
      |
      v
Validate Request
      |
      v
Load Authorized Context
      |
      v
AI Intent Classification
      |
      +------------------------+
      |                        |
      v                        v
Safe automated help       Human escalation
      |                        |
      v                        v
Response                  Staff task
```

### Response

```json
{
  "data": {
    "interaction_id": "interaction-uuid",
    "intent": "rescheduling",
    "response": "I can help with the next step. A staff member will assist with rescheduling.",
    "escalated": false
  }
}
```

The API must not return unsupported medical advice.

---

# 20. AI Response Rules

AI-generated responses must:

- use approved information where applicable
- use available system data rather than inventing information
- identify uncertainty
- escalate when human judgment is required
- avoid diagnosis
- avoid prescribing
- avoid medication changes
- avoid telling clients to stop treatment
- avoid independently interpreting clinical results
- avoid emergency medical management

The backend must remain the enforcement layer even if the AI agent is compromised or misconfigured.

---

# 21. Follow-Up Endpoints

## `POST /api/v1/followups`

Creates a follow-up task.

### Authorization

`staff`, `admin`, or authorized internal automation

### Request

```json
{
  "client_id": "client-uuid",
  "reason": "Missed appointment",
  "priority": "normal",
  "due_at": "2026-10-02T10:00:00Z"
}
```

### Response

```json
{
  "data": {
    "id": "followup-uuid",
    "status": "pending",
    "priority": "normal"
  }
}
```

---

## `GET /api/v1/followups`

Returns authorized follow-up tasks.

Filters:

```text
status
priority
assigned_user
client_id
due_date
```

---

## `PATCH /api/v1/followups/{followup_id}`

Updates a follow-up task.

Example:

```json
{
  "status": "completed"
}
```

---

# 22. Escalation Endpoints

Escalations allow the AI or automation system to transfer a situation to authorized human staff.

## `POST /api/v1/escalations`

Creates an escalation.

### Request

```json
{
  "client_id": "client-uuid",
  "category": "clinical_concern",
  "priority": "urgent",
  "reason": "Client reported a treatment-related concern.",
  "source": "ai_agent"
}
```

### Response

```json
{
  "data": {
    "id": "escalation-uuid",
    "status": "open",
    "priority": "urgent"
  }
}
```

The escalation record must not contain unnecessary sensitive information.

---

## `GET /api/v1/escalations`

Returns authorized escalations.

### Filters

```text
status
category
priority
assigned_user
created_at
```

---

## `PATCH /api/v1/escalations/{escalation_id}`

Updates escalation status.

Possible statuses:

```text
open
assigned
in_review
resolved
cancelled
```

---

# 23. Human Handoff

When the AI determines that human intervention is required, the backend should:

1. Record the interaction.
2. Create an escalation.
3. Create a follow-up task where appropriate.
4. Assign appropriate priority.
5. Notify authorized staff through the configured workflow.
6. Provide the client with a safe acknowledgement.
7. Record the event in the audit log.

Example client response:

```text
Thanks for letting us know. This needs to be reviewed by a member of the care team. Your message has been passed to the appropriate staff member.
```

The AI must not pretend that a human has already reviewed the message unless that has actually occurred.

---

# 24. Approved Information Endpoints

## `GET /api/v1/approved-information`

Retrieves approved information that the AI may use.

### Query Parameters

```text
?category=appointment_information
```

Possible categories:

```text
appointment_information
clinic_logistics
communication
program_information
approved_education
```

Only approved and active information should be available to the AI.

---

## `POST /api/v1/approved-information`

Creates approved information.

### Authorization

`admin`

---

## `PATCH /api/v1/approved-information/{information_id}`

Updates approved information.

### Authorization

`admin`

Changes should be audit logged.

---

# 25. Analytics Endpoints

Analytics endpoints must return aggregate program-level information wherever possible.

## `GET /api/v1/analytics/overview`

Returns high-level program metrics.

Example:

```json
{
  "data": {
    "active_clients": 250,
    "appointments_scheduled": 180,
    "appointments_missed": 24,
    "followups_open": 17,
    "escalations_open": 5
  }
}
```

The API should avoid exposing personally identifiable information through aggregate analytics.

---

## `GET /api/v1/analytics/appointments`

Returns appointment metrics.

Possible metrics:

- scheduled appointments
- completed appointments
- missed appointments
- cancelled appointments
- rescheduled appointments

---

## `GET /api/v1/analytics/engagement`

Returns communication and engagement metrics.

Possible metrics:

- incoming messages
- outgoing messages
- response rates
- follow-up completion
- escalation volume

---

# 26. n8n Integration

n8n is responsible for scheduled and event-driven automation.

Typical integrations include:

```text
n8n
 |
 +--> GET appointments
 |
 +--> Detect missed appointments
 |
 +--> POST follow-up
 |
 +--> POST message
 |
 +--> POST escalation
 |
 +--> Send notification
```

n8n must authenticate when calling protected API endpoints.

Credentials must be stored using secure n8n credential mechanisms or environment configuration.

They must never be committed to GitHub.

---

# 27. Automation Idempotency

Automation workflows may execute more than once.

The API must prevent duplicate operations where practical.

For operations such as creating follow-ups or processing webhook events, an idempotency key may be supplied.

Example:

```http
Idempotency-Key: appointment-reminder-appointment-uuid
```

The backend should recognize previously processed requests and avoid creating duplicate records.

---

# 28. Webhook Endpoints

Webhook endpoints may be used for trusted internal automation.

Example:

```text
POST /api/v1/webhooks/n8n
```

The exact webhook design should be finalized during workflow implementation.

Webhook requests must be:

- authenticated
- validated
- logged
- idempotent where necessary
- protected against replay where appropriate

Webhook payloads must not contain unnecessary sensitive information.

---

# 29. Pagination

Collection endpoints should support pagination.

Example:

```text
?page=1&page_size=20
```

Recommended default:

```text
page_size = 20
```

The API should enforce a maximum page size to prevent excessive database queries.

Example:

```text
?page_size=100
```

may be allowed as a maximum depending on implementation.

---

# 30. Filtering

Endpoints should support filtering where it provides clear application value.

Example:

```text
GET /api/v1/appointments?status=missed
```

Multiple filters may be combined.

Example:

```text
GET /api/v1/followups?status=pending&priority=urgent
```

Filtering parameters must be validated.

---

# 31. Sorting

Collection endpoints may support sorting.

Example:

```text
?sort=created_at&order=desc
```

Only explicitly supported fields may be used for sorting.

The API must not directly insert arbitrary user-provided sorting expressions into SQL queries.

---

# 32. Date and Time Handling

All API timestamps should use ISO 8601 format.

Example:

```text
2026-10-01T10:00:00Z
```

The backend should store timestamps consistently using PostgreSQL `TIMESTAMPTZ`.

The application should avoid ambiguous local date formats.

---

# 33. Validation

FastAPI/Pydantic models must validate incoming data.

Validation should include:

- required fields
- data types
- enum values
- UUID format
- date/time format
- string length
- permitted status transitions
- authorization
- business rules

Validation must happen before database operations.

---

# 34. API Security

The API must implement:

- authentication
- authorization
- HTTPS in production
- secure password handling
- secure token handling
- input validation
- rate limiting where appropriate
- CORS restrictions
- secure headers where appropriate
- audit logging
- secret management
- data minimization
- safe error messages

CORS must allow only configured application origins.

---

# 35. Rate Limiting

Rate limiting should be applied to endpoints that could be abused.

Particular attention should be given to:

- login
- message endpoints
- public webhooks
- password-related endpoints
- high-cost AI operations

The exact limits should be configurable through environment variables.

---

# 36. Audit Logging

Sensitive actions must generate audit events.

Examples:

```text
user_login
client_created
client_updated
appointment_created
appointment_updated
followup_created
followup_completed
escalation_created
escalation_resolved
communication_preference_updated
approved_information_updated
```

Audit logs should record:

- actor
- action
- resource
- timestamp
- relevant metadata
- success/failure

Audit logs must not unnecessarily duplicate sensitive message content.

---

# 37. AI Agent to API Mapping

The AI agent should interact with backend services through controlled tools.

| AI Tool | Backend Capability |
|---|---|
| `get_client_profile()` | `GET /clients/{id}` |
| `get_appointment()` | `GET /appointments/{id}` |
| `create_followup()` | `POST /followups` |
| `update_contact_preference()` | `PATCH /clients/{id}` or preference endpoint |
| `record_interaction()` | `POST /interactions` |
| `send_notification()` | Internal notification service |
| `create_escalation()` | `POST /escalations` |
| `get_approved_information()` | `GET /approved-information` |

The AI must not receive unrestricted access to the API.

Tool permissions must be explicitly defined.

---

# 38. AI Authorization Boundary

The AI agent must not be allowed to:

- modify treatment plans
- prescribe medication
- change medication
- delete client records
- resolve clinical escalations
- override staff decisions
- access unrestricted client data
- access database credentials
- access arbitrary API endpoints

The backend must enforce these restrictions.

---

# 39. API and Frontend Integration

The React frontend should communicate with the backend through API calls.

Example:

```text
React
  |
  | POST /api/v1/messages
  v
FastAPI
  |
  | process message
  v
AI Agent
  |
  v
Response
  |
  v
React
```

The frontend should not contain:

- database credentials
- OpenAI/LLM API keys
- n8n credentials
- PostgreSQL credentials
- privileged backend tokens

---

# 40. API and Database Boundary

The API layer is responsible for:

- validation
- authorization
- business rules
- transaction management
- service orchestration
- audit events

The database is responsible for:

- persistence
- constraints
- indexes
- relationships
- referential integrity

The frontend must never connect directly to PostgreSQL.

---

# 41. API Testing

The API must be tested at multiple levels.

## Unit Tests

Test:

- validation
- business logic
- authorization helpers
- service functions
- AI classification logic where deterministic

## Integration Tests

Test:

- API + PostgreSQL
- authentication
- database transactions
- n8n integration
- escalation creation
- appointment workflows

## API Tests

Test:

- successful requests
- invalid requests
- unauthorized requests
- forbidden requests
- missing resources
- duplicate requests
- invalid state transitions

## Safety Tests

Test that the AI/API does not:

- prescribe
- diagnose
- recommend stopping treatment
- make clinical decisions
- expose restricted information
- bypass human escalation

---

# 42. OpenAPI Documentation

FastAPI should automatically generate OpenAPI documentation.

Development documentation should be available through:

```text
/docs
```

and:

```text
/redoc
```

The generated OpenAPI schema should reflect the actual API implementation.

When API behavior changes, the documentation and tests must be updated.

---

# 43. Example End-to-End Flow

## Missed Appointment

```text
1. Appointment exists in PostgreSQL.

2. n8n scheduled workflow checks appointments.

3. Appointment is identified as missed.

4. n8n calls the follow-up API.

5. FastAPI validates the request.

6. FastAPI creates a follow-up task.

7. n8n sends an appropriate supportive notification.

8. Client responds.

9. Message is sent to /messages.

10. AI classifies the intent.

11. If rescheduling is requested:
       create appropriate follow-up/task.

12. If a clinical concern is reported:
       create escalation.

13. Authorized staff review the escalation.

14. Staff resolve the issue.

15. Events are recorded for audit and analytics.
```

---

# 44. Example API Flow — Client Message

### Request

```http
POST /api/v1/messages
```

```json
{
  "client_id": "client-uuid",
  "channel": "web",
  "message": "I missed my appointment. Can I reschedule?"
}
```

### Backend

```text
Validate
   ↓
Authenticate
   ↓
Authorize
   ↓
Load permitted context
   ↓
Record interaction
   ↓
Classify intent
   ↓
Determine action
   ↓
Execute permitted tool
   ↓
Record result
   ↓
Return safe response
```

### Response

```json
{
  "data": {
    "interaction_id": "interaction-uuid",
    "intent": "rescheduling",
    "escalated": false,
    "response": "I can help with the next step. A staff member will assist with rescheduling."
  }
}
```

---

# 45. API Failure Handling

If an external AI service fails:

```text
Client
  |
  v
FastAPI
  |
  v
AI Service
  |
  X
Failure
  |
  v
Safe fallback
```

The system should not fabricate an AI response.

A safe fallback may be:

```text
I'm unable to process your request right now. Please try again later or contact the appropriate program staff.
```

The failure should be logged for monitoring.

---

# 46. Transaction Handling

Operations that modify multiple related records should use database transactions.

For example, creating an escalation may involve:

```text
Create escalation
+
Create follow-up task
+
Create audit event
```

These operations should be handled consistently so the system does not leave partially completed state.

---

# 47. Concurrency

The API must account for multiple workers or automation workflows operating simultaneously.

Examples:

- two n8n executions processing the same appointment
- staff member updating an escalation while automation updates it
- duplicate client messages
- multiple workers creating follow-up tasks

Use appropriate database constraints, transactions, and idempotency mechanisms.

---

# 48. Logging and Observability

The API should log operational events such as:

- request failures
- authentication failures
- service errors
- AI service failures
- database failures
- webhook failures
- escalation creation
- automation failures

Logs must avoid unnecessary sensitive information.

Never log:

- passwords
- access tokens
- API keys
- database credentials
- unnecessary full message contents

---

# 49. Environment Configuration

Configuration must come from environment variables.

Example `.env.example`:

```env
APP_ENV=development
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://...
SECRET_KEY=change-me
AI_API_KEY=change-me
N8N_WEBHOOK_URL=http://localhost:5678
```

The actual `.env` file must not be committed to GitHub.

Only `.env.example` should be committed.

---

# 50. API Repository Structure

The backend should organize API code approximately as follows:

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── clients.py
│   │       ├── appointments.py
│   │       ├── interactions.py
│   │       ├── messages.py
│   │       ├── followups.py
│   │       ├── escalations.py
│   │       ├── approved_information.py
│   │       ├── analytics.py
│   │       └── health.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── core/
│   └── db/
├── tests/
└── requirements.txt
```

The exact structure may change during implementation if the architectural boundaries remain intact.

---

# 51. API Design Rules for AI Coding Agents

Any AI coding assistant working on the API must follow these rules:

1. Read `docs/PRD.md` before implementing product behavior.
2. Read `docs/SRS.md` before implementing requirements.
3. Read `docs/system-architecture.md` before changing architecture.
4. Read `docs/ai-agent-specification.md` before modifying AI behavior.
5. Read `docs/database-design.md` before changing models or database access.
6. Treat this document as the API contract.
7. Do not invent undocumented endpoints without updating this document.
8. Do not expose database access to the frontend.
9. Do not hardcode secrets.
10. Do not weaken authentication or authorization to make tests pass.
11. Do not bypass AI safety rules.
12. Add tests for new endpoints.
13. Update OpenAPI documentation through the implementation.
14. Preserve backward compatibility unless a version change is intentional.
15. Prefer small, reviewable changes.
16. Do not modify unrelated components.
17. Update documentation when API behavior changes.

---

# 52. Definition of API Complete

The API implementation is considered complete for MVP when:

- [ ] FastAPI application is running.
- [ ] `/api/v1/health` works.
- [ ] Authentication works.
- [ ] Role-based authorization works.
- [ ] Client endpoints work.
- [ ] Appointment endpoints work.
- [ ] Interaction endpoints work.
- [ ] Message endpoint works.
- [ ] Follow-up endpoints work.
- [ ] Escalation endpoints work.
- [ ] Approved information endpoint works.
- [ ] Required analytics endpoints work.
- [ ] n8n can communicate with the API.
- [ ] Validation is implemented.
- [ ] Error responses are consistent.
- [ ] Pagination is implemented where required.
- [ ] Idempotency is implemented for relevant automation operations.
- [ ] Audit logging is implemented.
- [ ] API tests pass.
- [ ] AI safety tests pass.
- [ ] OpenAPI documentation reflects the implementation.
- [ ] Secrets are excluded from Git.
- [ ] Synthetic data is used for the public project.
- [ ] No unauthorized direct database access exists.

---

# 53. Related Documentation

This document should be used together with:

```text
docs/PRD.md
docs/SRS.md
docs/system-architecture.md
docs/ai-agent-specification.md
docs/database-design.md
docs/workflows.md
docs/safety-privacy.md
README.md
```

Each document has a different responsibility:

| Document | Responsibility |
|---|---|
| PRD | What and why |
| SRS | Detailed system requirements |
| Architecture | How the system is structured |
| AI Agent Specification | How the AI behaves |
| Database Design | How data is stored |
| API Specification | How components communicate |
| Workflows | How automation operates |
| Safety & Privacy | How sensitive and risky situations are handled |
| README | How developers understand and run the project |

---

# 54. Source-of-Truth Rule

The API implementation must remain consistent with this specification.

If an implementation requirement changes:

1. Update the relevant documentation.
2. Update the API contract.
3. Update the implementation.
4. Update tests.
5. Verify frontend integration.
6. Verify n8n integration.
7. Verify AI tool integration.

Documentation, implementation, and tests should not contradict each other.

---

# 55. API Design Summary

CareFlow AI uses FastAPI as the controlled application layer between users, automation, AI services, and PostgreSQL.

The API is responsible for:

- authentication
- authorization
- validation
- business rules
- data access
- AI orchestration
- automation integration
- escalation
- auditability
- safe error handling

The API must remain the enforcement boundary for privacy, security, authorization, and AI safety.

**Core principle:**

> The API should make safe behavior easy, unsafe behavior difficult, and human oversight unavoidable where human judgment is required.