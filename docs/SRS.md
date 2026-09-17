# CareFlow AI — Software Requirements Specification (SRS)

**Product:** CareFlow AI  
**Document:** Software Requirements Specification  
**Version:** 1.0  
**Status:** Draft  
**Product Type:** AI-Powered HIV Care Retention & Support Platform  
**Development Approach:** AI-Assisted / Agentic Software Development

---

## 1. Purpose

This document defines the functional and non-functional software requirements for CareFlow AI.

The SRS translates the product requirements defined in the PRD into requirements that can be implemented, tested, and validated by developers and AI coding agents.

The system is designed as an educational and portfolio prototype demonstrating how AI agents, workflow automation, backend services, databases, and analytics can work together to support HIV care-retention programs.

CareFlow AI is **not a clinically validated system and must not be used as a replacement for qualified healthcare professionals or real-world clinical decision-making.**

---

# 2. System Scope

CareFlow AI shall provide a platform for:

1. Managing synthetic client records.
2. Managing appointments.
3. Sending supportive reminders.
4. Detecting missed appointments.
5. Receiving and classifying client responses.
6. Identifying non-clinical barriers to care.
7. Creating follow-up tasks.
8. Escalating sensitive or clinical concerns to authorized staff.
9. Maintaining interaction history.
10. Providing aggregate program-level analytics.

---

# 3. User Roles

The system shall support the following primary roles.

## 3.1 Client

A client is an individual receiving services from an HIV care program.

Clients may:

- Receive reminders.
- Respond to messages.
- Request appointment-related assistance.
- Report barriers to attending care.
- Request human assistance.
- View or manage permitted communication preferences.

Clients shall not have access to other clients' information.

---

## 3.2 Healthcare / Program Staff

Staff members may:

- View authorized client records.
- View appointments.
- Review follow-up tasks.
- Review escalations.
- Review interaction history.
- Update appointment-related information.
- Resolve follow-up tasks.
- Record staff actions.

Staff shall only access information permitted by their role.

---

## 3.3 Program Manager / Administrator

Authorized administrators may:

- Manage users and permissions.
- View aggregate program analytics.
- Monitor workflow activity.
- Review system activity and audit logs.
- Configure approved communication settings.
- Manage system-level configurations.

---

# 4. Functional Requirements

## 4.1 Authentication

### FR-001 — User Authentication

The system shall require authorized staff users to authenticate before accessing protected staff functionality.

### FR-002 — Session Management

The system shall maintain authenticated user sessions securely.

### FR-003 — Authorization

The system shall enforce role-based access control.

Users shall only access resources permitted by their role.

### FR-004 — Unauthorized Access

The system shall reject unauthorized requests with an appropriate HTTP authorization response.

---

# 5. Client Management

## FR-005 — Create Client

Authorized staff shall be able to create a client record.

A client record shall contain only information necessary for the system's supported functions.

Example fields:

- Internal client ID
- Preferred name or identifier
- Communication preference
- Preferred language
- Contact information where required
- Program enrollment status
- Created timestamp
- Updated timestamp

The system shall avoid unnecessary collection of sensitive information.

---

## FR-006 — View Client

Authorized staff shall be able to retrieve an individual client record.

---

## FR-007 — Update Client

Authorized staff shall be able to update permitted client information.

---

## FR-008 — Client Isolation

The system shall prevent one client from accessing another client's information.

---

# 6. Appointment Management

## FR-009 — Create Appointment

Authorized staff shall be able to create an appointment associated with a client.

Appointment information may include:

- Appointment ID
- Client ID
- Appointment date/time
- Appointment status
- Appointment type
- Location or service information where appropriate
- Created timestamp
- Updated timestamp

---

## FR-010 — Appointment Status

The system shall support appointment states such as:

- Scheduled
- Completed
- Missed
- Cancelled
- Rescheduled

---

## FR-011 — Upcoming Appointment Detection

The system shall identify appointments approaching their scheduled date/time.

This functionality shall support automated reminder workflows.

---

## FR-012 — Missed Appointment Detection

The system shall identify appointments that have passed without an appropriate completion or cancellation status.

---

# 7. Communication Management

## FR-013 — Communication Preferences

The system shall store permitted communication preferences for each client.

Examples:

- SMS
- WhatsApp
- Web
- Email

The system shall respect configured communication preferences.

---

## FR-014 — Reminder Generation

The system shall generate supportive appointment reminders for eligible clients.

Reminder messages shall avoid unnecessarily exposing sensitive health information.

---

## FR-015 — Reminder Logging

The system shall record relevant reminder events.

Example information:

- Client ID
- Reminder type
- Timestamp
- Delivery status
- Communication channel

---

# 8. AI Support Agent

## FR-016 — Message Classification

The AI support agent shall classify incoming client messages into supported categories.

Example categories:

- Appointment assistance
- Rescheduling request
- General support
- Barrier to care
- Request for human staff
- Treatment/clinical concern
- Sensitive concern
- Emergency-related message
- Unknown / uncertain intent

---

## FR-017 — Supported Responses

The AI agent may provide responses related to:

- Appointment logistics
- Approved program information
- General supportive communication
- Communication preferences
- Follow-up processes

---

## FR-018 — Approved Information

The AI agent shall use approved information when providing program or educational information.

The system shall not allow the AI agent to freely invent medical guidance.

---

## FR-019 — Uncertainty Handling

If the AI agent cannot confidently determine the user's intent, it shall avoid making assumptions and may escalate the interaction to authorized staff.

---

# 9. AI Safety Requirements

## FR-020 — No Diagnosis

The AI agent shall not diagnose diseases or medical conditions.

---

## FR-021 — No Prescription

The AI agent shall not prescribe medication.

---

## FR-022 — No Treatment Changes

The AI agent shall not instruct clients to:

- Start medication.
- Stop medication.
- Change dosage.
- Change treatment schedules.

---

## FR-023 — No Clinical Decision-Making

The AI agent shall not independently make clinical decisions based on symptoms, laboratory results, or other health information.

---

## FR-024 — Human Escalation

The system shall create an escalation when an interaction requires human review.

Examples include:

- Treatment concerns.
- Medication concerns.
- Clinical symptoms.
- Requests for healthcare professionals.
- Sensitive situations.
- Emergency-related messages.
- Uncertain AI classification.

---

# 10. Follow-Up Management

## FR-025 — Create Follow-Up Task

The system shall allow an automated workflow or authorized staff member to create a follow-up task.

A task shall include:

- Task ID
- Client ID
- Reason
- Priority
- Assigned staff member where applicable
- Status
- Created timestamp
- Due date where applicable

---

## FR-026 — Task Status

Follow-up tasks shall support statuses such as:

- Pending
- Assigned
- In Progress
- Completed
- Cancelled

---

## FR-027 — Staff Task Resolution

Authorized staff shall be able to update and resolve follow-up tasks.

---

# 11. Escalation Management

## FR-028 — Create Escalation

The system shall create an escalation when configured escalation criteria are met.

---

## FR-029 — Escalation Priority

Escalations shall support priority levels.

Example:

- Normal
- High
- Urgent

---

## FR-030 — Escalation Queue

Authorized staff shall be able to view unresolved escalations.

---

## FR-031 — Escalation Resolution

Authorized staff shall be able to record the resolution or outcome of an escalation.

---

# 12. Interaction History

## FR-032 — Interaction Recording

The system shall record relevant client-system interactions.

Examples:

- Incoming message
- Outgoing message
- Reminder
- AI classification
- Follow-up creation
- Escalation
- Staff response

---

## FR-033 — Interaction Timestamp

Each interaction shall contain a timestamp.

---

## FR-034 — Interaction Traceability

The system shall allow authorized staff to understand the sequence of relevant interactions associated with a client.

---

# 13. Automation Requirements

CareFlow AI shall use n8n or an equivalent workflow automation engine for scheduled and event-driven automation.

## FR-035 — Appointment Reminder Workflow

The automation system shall:

1. Identify upcoming appointments.
2. Determine eligible clients.
3. Check communication preferences.
4. Generate or retrieve an approved reminder.
5. Send the reminder through the configured channel.
6. Record the outcome.

---

## FR-036 — Missed Appointment Workflow

The automation system shall:

1. Identify missed appointments.
2. Create a follow-up event.
3. Send an appropriate supportive message where permitted.
4. Monitor the client's response.
5. Escalate when required.
6. Record the workflow outcome.

---

## FR-037 — Retry Handling

Failed automation actions shall support controlled retry behavior.

The system shall avoid creating duplicate actions when a workflow is retried.

---

## FR-038 — Idempotency

Critical automated operations shall be designed so that repeating the same event does not unintentionally create duplicate reminders, tasks, or escalations.

---

# 14. API Requirements

The backend shall expose a REST API.

## FR-039 — API Versioning

API endpoints shall use versioning.

Example:

`/api/v1/...`

---

## FR-040 — Request Validation

The backend shall validate incoming request data before processing it.

Invalid requests shall return appropriate HTTP error responses.

---

## FR-041 — Consistent Responses

API responses shall follow a consistent structure.

---

## FR-042 — Error Handling

The API shall return meaningful error responses without exposing:

- Passwords
- API keys
- Authentication tokens
- Database credentials
- Internal secrets
- Unnecessary internal implementation details

---

# 15. Database Requirements

The system shall use PostgreSQL as the primary relational database.

The database shall maintain relationships between relevant entities.

Initial entities shall include:

- Users
- Clients
- Appointments
- Interactions
- Follow-up tasks
- Escalations
- Communication preferences
- Approved information

The database design shall enforce appropriate:

- Primary keys
- Foreign keys
- Unique constraints
- Required fields
- Indexes
- Timestamps

---

# 16. Analytics Requirements

The system shall provide aggregate data suitable for Power BI or another analytics platform.

The analytics layer shall support metrics such as:

- Total enrolled clients
- Active clients
- Upcoming appointments
- Missed appointments
- Follow-up tasks
- Completed follow-ups
- Re-engagement activity
- Barrier categories
- Reminder delivery
- Escalation volume
- Escalation status

Analytics shall use aggregate or appropriately de-identified data for the portfolio demonstration.

---

# 17. Privacy Requirements

## FR-043 — Data Minimization

The system shall collect only information necessary for supported functionality.

---

## FR-044 — Synthetic Demonstration Data

The public GitHub repository shall use synthetic demonstration data.

Real patient information shall not be included.

---

## FR-045 — Sensitive Information Protection

The system shall avoid exposing HIV status or other sensitive health information in ordinary notification content unless explicitly required and appropriately protected.

---

## FR-046 — Audit Logging

Important actions shall be logged for accountability.

Examples:

- User login
- Record creation
- Record modification
- Escalation creation
- Staff resolution
- Configuration changes

---

# 18. Security Requirements

## NFR-001 — Secrets Management

Secrets shall not be committed to GitHub.

Examples:

- API keys
- Database passwords
- JWT secrets
- OAuth credentials
- n8n credentials

Environment variables or an appropriate secrets-management mechanism shall be used.

---

## NFR-002 — Environment Configuration

The system shall support separate configuration for development and production environments.

---

## NFR-003 — HTTPS

Production deployments shall use HTTPS.

---

## NFR-004 — Access Control

Protected resources shall require appropriate authorization.

---

## NFR-005 — Input Security

The backend shall validate and sanitize appropriate user-controlled input.

---

# 19. Performance Requirements

## NFR-006 — API Response

Normal non-AI API requests should generally return within an acceptable interactive response time under normal development/test load.

---

## NFR-007 — Asynchronous Operations

Long-running operations such as AI processing and external notifications should not unnecessarily block standard API requests.

---

# 20. Reliability Requirements

## NFR-008 — Failure Handling

The system shall gracefully handle failures involving:

- Database connectivity
- AI provider availability
- Notification services
- n8n workflows
- External APIs

---

## NFR-009 — Logging

Application errors and important workflow failures shall be logged.

Logs shall not unnecessarily contain sensitive client information.

---

## NFR-010 — Recovery

The system shall allow failed workflow operations to be retried or manually reviewed where appropriate.

---

# 21. Observability Requirements

The system shall provide sufficient logging to understand:

- API requests
- Application errors
- AI processing outcomes
- Workflow execution
- Notification results
- Escalations
- Database errors

The system should make it possible for developers to determine where a failed workflow occurred.

---

# 22. Frontend Requirements

The frontend shall be implemented using React.

## FR-047 — Dashboard

Authorized staff shall have access to a dashboard showing relevant operational information.

---

## FR-048 — Client Interface

The system shall provide an interface for supported client interactions.

---

## FR-049 — Appointment View

Authorized users shall be able to view relevant appointments.

---

## FR-050 — Follow-Up View

Authorized staff shall be able to view pending follow-up tasks.

---

## FR-051 — Escalation View

Authorized staff shall be able to view unresolved escalations.

---

## FR-052 — Loading States

The frontend shall display appropriate loading states during asynchronous operations.

---

## FR-053 — Error States

The frontend shall display understandable error messages when operations fail.

---

# 23. AI Agent Tool Requirements

The AI agent may interact with backend functionality through controlled tools.

Potential tools include:

### `get_client_profile()`

Retrieves permitted client information.

### `get_appointment()`

Retrieves relevant appointment information.

### `create_followup()`

Creates a staff follow-up task.

### `update_contact_preference()`

Updates permitted communication preferences.

### `record_interaction()`

Records an interaction.

### `send_notification()`

Sends an approved notification through an authorized channel.

### `create_escalation()`

Creates a human-review escalation.

### `get_approved_information()`

Retrieves approved program information.

AI agents shall not have unrestricted database access.

---

# 24. Human-in-the-Loop Requirements

The system shall maintain human oversight over situations that require professional judgment.

The AI shall escalate rather than independently resolve situations when:

1. The interaction involves clinical concerns.
2. The client requests a healthcare professional.
3. The client reports potentially serious symptoms.
4. The client asks for treatment changes.
5. The AI is uncertain about the appropriate response.
6. The issue falls outside the approved AI scope.

Human staff shall remain responsible for decisions requiring professional judgment.

---

# 25. High-Level System Flow

```text
Client
   |
   v
React / Messaging Interface
   |
   v
FastAPI Backend
   |
   +--------------------+
   |                    |
   v                    v
PostgreSQL          AI Support Agent
                        |
                        v
                 Controlled Tools
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      Follow-up     Escalation    Approved Info
          |
          v
         n8n
          |
          +--------------------------+
          |                          |
          v                          v
    Reminders / Follow-up       Notifications
          
          |
          v
   Analytics Data
          |
          v
      Power BI
```

---

# 26. MVP Requirements

The Minimum Viable Product shall include:

## Client Management

- Create client
- View client
- Update client
- Communication preferences

## Appointment Management

- Create appointment
- View appointment
- Appointment status
- Upcoming appointment detection
- Missed appointment detection

## AI Support

- Message classification
- Supportive responses
- Approved information retrieval
- Human escalation

## Automation

- Appointment reminder workflow
- Missed appointment workflow
- Follow-up workflow
- Retry handling

## Staff Operations

- Follow-up queue
- Escalation queue
- Interaction history

## Analytics

- Aggregate operational metrics
- Power BI-compatible data

## Security

- Authentication
- Role-based authorization
- Environment-based secrets
- Audit logging

---

# 27. Testing Requirements

The system shall include automated and manual testing.

## Unit Tests

Unit tests shall cover important backend business logic.

Examples:

- Appointment status handling
- Missed appointment detection
- Intent classification handling
- Escalation rules
- Permission checks

---

## API Tests

API tests shall verify:

- Successful requests
- Invalid requests
- Authentication
- Authorization
- Not-found scenarios
- Server errors

---

## Workflow Tests

n8n workflows shall be tested for:

- Successful execution
- Failed external services
- Duplicate events
- Retry behavior
- Escalation behavior

---

## AI Tests

The AI component shall be tested against representative synthetic scenarios.

Examples:

- Appointment request
- Rescheduling request
- General support
- Barrier report
- Treatment concern
- Human escalation request
- Ambiguous message

The tests shall verify that unsafe requests are escalated rather than answered with unsupported medical advice.

---

# 28. Acceptance Criteria

The MVP shall be considered functionally complete when:

- A staff user can create a synthetic client.
- A staff user can create an appointment.
- The system can identify upcoming appointments.
- The system can trigger an appointment reminder workflow.
- The system can identify a missed appointment.
- The system can initiate supportive follow-up.
- The AI can classify supported client messages.
- The AI can create follow-up actions through controlled tools.
- Sensitive/clinical concerns are escalated.
- Staff can view and resolve follow-up tasks.
- Staff can view unresolved escalations.
- Relevant interactions are recorded.
- Aggregate metrics can be visualized.
- Tests cover the major backend and workflow logic.
- No secrets or real patient information are present in the repository.

---

# 29. Out of Scope for MVP

The MVP shall not include:

- Clinical diagnosis
- Clinical decision support
- Prescription recommendations
- Medication changes
- Autonomous treatment decisions
- Real patient deployment
- Real HIV patient records
- Real patient contact information in GitHub
- Emergency medical response
- Integration with hospital electronic medical records
- Automated clinical interpretation of laboratory results

These may be considered only as future research or product-development areas and would require substantially different safety, compliance, validation, and governance requirements.

---

# 30. Technical Constraints

The initial implementation shall use:

| Component | Technology |
|---|---|
| Frontend | React |
| Backend | FastAPI / Python |
| Database | PostgreSQL |
| Automation | n8n |
| AI | LLM-powered AI agent |
| Analytics | Microsoft Power BI |
| API | REST |
| Containerization | Docker |
| Version Control | Git / GitHub |

The architecture shall keep components modular enough to allow individual technologies to be replaced later.

---

# 31. Development Rules for AI Coding Agents

AI coding agents working on this repository shall follow these rules:

1. Read the relevant documentation before modifying code.
2. Treat the PRD and SRS as product and requirements sources of truth.
3. Do not invent undocumented business requirements.
4. Do not introduce clinical functionality without an explicit requirement.
5. Do not remove safety or authorization controls to make a feature work.
6. Do not hard-code secrets.
7. Do not add real patient information.
8. Follow the existing project architecture.
9. Write tests for significant backend functionality.
10. Keep changes focused and explain important architectural decisions.
11. Do not silently change database schemas or API contracts.
12. Update documentation when behavior changes.
13. Prefer simple, maintainable implementations over unnecessary complexity.
14. Validate changes before considering a task complete.

---

# 32. Requirement Traceability

Each major implementation feature should be traceable to one or more requirements in this document.

Example:

| Feature | Requirement |
|---|---|
| Client creation | FR-005 |
| Appointment creation | FR-009 |
| Missed appointment detection | FR-012 |
| AI message classification | FR-016 |
| Human escalation | FR-024 |
| Follow-up tasks | FR-025 |
| Reminder automation | FR-035 |
| PostgreSQL database | Section 15 |
| Authentication | FR-001 |
| Role-based access | FR-003 |
| Audit logging | FR-046 |

This traceability helps developers and AI coding agents understand **why a piece of code exists and which requirement it satisfies.**

---

# 33. Definition of Software Requirement Complete

A requirement shall be considered implemented when:

1. The functionality exists.
2. The relevant API or UI behavior works.
3. Validation is implemented.
4. Appropriate error handling exists.
5. Authorization is enforced where required.
6. Relevant tests exist.
7. Logging is appropriate.
8. No sensitive information is unnecessarily exposed.
9. Documentation is updated where necessary.

---

# 34. Document Dependencies

This SRS is derived from the Product Requirements Document.

The planned documentation hierarchy is:

```text
PRD
 |
 v
SRS
 |
 +----------+------------+-------------+
 |          |            |             |
 v          v            v             v
Architecture  Database   API        AI Agent
 |
 v
Workflows
 |
 v
Safety & Privacy
 |
 v
Implementation + Testing
```

Future technical documents shall remain consistent with this SRS.

---

# 35. Final Product Requirement Statement

CareFlow AI shall provide a secure, modular, AI-assisted platform that helps HIV care programs automate appropriate client engagement and retention workflows while maintaining human oversight for sensitive and clinical situations.

The system shall prioritize:

- Safety
- Privacy
- Human oversight
- Clear system boundaries
- Reliable automation
- Testability
- Maintainability
- Explainability
- Responsible use of AI

The AI is an assistant within the care-retention workflow—not a replacement for healthcare professionals.