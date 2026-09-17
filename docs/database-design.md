# CareFlow AI — Database Design

**Product:** CareFlow AI  
**Document:** Database Design  
**Version:** 1.0  
**Status:** Draft  
**Database:** PostgreSQL  
**Database Type:** Relational Database

---

# 1. Purpose

This document defines the database architecture for CareFlow AI.

It describes:

- Database entities
- Tables
- Columns
- Relationships
- Primary keys
- Foreign keys
- Constraints
- Indexes
- Enumerated values
- Audit requirements
- Data lifecycle principles

The database is the primary source of truth for application data.

The database shall not contain real patient information in the public portfolio repository.

All development and demonstration data shall be synthetic.

---

# 2. Database Principles

The database shall follow these principles:

1. PostgreSQL is the primary application database.
2. Each entity should have a clear purpose.
3. Relationships should be enforced with foreign keys.
4. Sensitive data should be minimized.
5. Database constraints should prevent invalid states.
6. Important fields should be indexed appropriately.
7. Database changes should use migrations.
8. Application code should access the database through controlled backend services.
9. AI agents must not have unrestricted direct database access.
10. Auditability should be maintained for important actions.

---

# 3. High-Level Entity Model

The initial database consists of the following major entities:

```text id="q1p4a7"
                         USERS
                           |
                           |
                           v
                        ROLES


                         CLIENTS
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
      APPOINTMENTS     INTERACTIONS     CONTACT
            |                           PREFERENCES
            |
            v
       FOLLOW-UPS
            |
            v
       ESCALATIONS


                    APPROVED INFORMATION
                            |
                            v
                        AI AGENT
```

---

# 4. Core Tables

The MVP shall use these core tables:

1. `users`
2. `roles`
3. `clients`
4. `appointments`
5. `communication_preferences`
6. `interactions`
7. `follow_up_tasks`
8. `escalations`
9. `approved_information`
10. `audit_logs`

Additional tables may be introduced if a documented requirement requires them.

---

# 5. Entity Relationship Overview

```text id="m8m1w2"
ROLES
  |
  | 1
  |
  | N
  v
USERS


CLIENTS
  |
  +------< APPOINTMENTS
  |
  +------< INTERACTIONS
  |
  +------< FOLLOW_UP_TASKS
  |
  +------< ESCALATIONS
  |
  +------1 COMMUNICATION_PREFERENCES


USERS
  |
  +------< FOLLOW_UP_TASKS
  |
  +------< ESCALATIONS
  |
  +------< AUDIT_LOGS
```

`1` means one.

`N` means many.

`1:N` means one-to-many.

---

# 6. Table: `roles`

## Purpose

Stores application roles used for authorization.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Unique role identifier |
| `name` | VARCHAR | UNIQUE, NOT NULL | Role name |
| `description` | TEXT | NULL | Role description |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |

### Initial Roles

```text
client
staff
admin
```

The application may eventually use more granular permissions.

---

# 7. Table: `users`

## Purpose

Stores authenticated application users.

This table is primarily intended for staff and administrators.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Unique user ID |
| `role_id` | UUID | FK → roles.id | User role |
| `email` | VARCHAR | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR | NOT NULL | Hashed password |
| `first_name` | VARCHAR | NOT NULL | First name |
| `last_name` | VARCHAR | NOT NULL | Last name |
| `is_active` | BOOLEAN | NOT NULL | Account status |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation time |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

### Security Rule

Plain-text passwords must never be stored.

Only secure password hashes may be stored.

---

# 8. Table: `clients`

## Purpose

Stores the minimum information necessary to manage client engagement and retention workflows.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Internal client identifier |
| `external_reference` | VARCHAR | UNIQUE | Synthetic external reference |
| `preferred_name` | VARCHAR | NULL | Preferred name |
| `preferred_language` | VARCHAR | NOT NULL | Preferred communication language |
| `enrollment_status` | VARCHAR | NOT NULL | Program status |
| `is_active` | BOOLEAN | NOT NULL | Active record |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

### Important Principle

The client table should not contain unnecessary clinical information.

The MVP is an engagement and retention platform, not a clinical records system.

---

# 9. Client Enrollment Status

The initial allowed values are:

```text
active
inactive
completed
withdrawn
```

The implementation may use a PostgreSQL enum or a constrained string depending on migration strategy.

---

# 10. Table: `communication_preferences`

## Purpose

Stores how the client has configured permitted communication.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Preference ID |
| `client_id` | UUID | FK → clients.id, UNIQUE | Client |
| `channel` | VARCHAR | NOT NULL | Preferred channel |
| `is_enabled` | BOOLEAN | NOT NULL | Whether channel is enabled |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

### Initial Channels

```text
web
sms
whatsapp
email
```

Only channels actually implemented should be enabled in the application.

---

# 11. Table: `appointments`

## Purpose

Stores client appointments and their operational status.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Appointment ID |
| `client_id` | UUID | FK → clients.id | Client |
| `appointment_type` | VARCHAR | NOT NULL | Appointment category |
| `scheduled_at` | TIMESTAMPTZ | NOT NULL | Appointment date/time |
| `status` | VARCHAR | NOT NULL | Appointment state |
| `location_label` | VARCHAR | NULL | Permitted location label |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

---

# 12. Appointment Status

Initial allowed values:

```text
scheduled
completed
missed
cancelled
rescheduled
```

The application must prevent invalid appointment states.

---

# 13. Appointment Relationships

```text id="u4c8na"
CLIENT
  |
  | 1
  |
  | N
  v
APPOINTMENT
```

A client may have multiple appointments.

An appointment belongs to one client.

---

# 14. Table: `interactions`

## Purpose

Stores relevant interactions between clients and the CareFlow AI system or staff.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Interaction ID |
| `client_id` | UUID | FK → clients.id | Client |
| `channel` | VARCHAR | NOT NULL | Communication channel |
| `direction` | VARCHAR | NOT NULL | Incoming/outgoing |
| `interaction_type` | VARCHAR | NOT NULL | Interaction category |
| `intent_category` | VARCHAR | NULL | AI classification |
| `message_reference` | VARCHAR | NULL | External message identifier |
| `content` | TEXT | NULL | Interaction content where required |
| `created_at` | TIMESTAMPTZ | NOT NULL | Interaction time |

---

# 15. Interaction Direction

Allowed values:

```text
incoming
outgoing
```

---

# 16. Interaction Types

Initial categories may include:

```text
message
appointment_reminder
follow_up
staff_response
ai_response
system_event
```

Additional types may be added when requirements justify them.

---

# 17. AI Intent Categories

Possible intent categories include:

```text
appointment_assistance
rescheduling
general_support
barrier_to_care
human_staff_request
clinical_concern
medication_concern
emergency_related
unknown
```

The database should not assume that AI classification is always correct.

AI classification is an application output that may be reviewed or overridden by authorized staff where appropriate.

---

# 18. Table: `follow_up_tasks`

## Purpose

Stores tasks requiring follow-up by program staff.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Task ID |
| `client_id` | UUID | FK → clients.id | Client |
| `assigned_to` | UUID | FK → users.id, NULL | Assigned staff |
| `reason` | VARCHAR | NOT NULL | Follow-up reason |
| `priority` | VARCHAR | NOT NULL | Priority |
| `status` | VARCHAR | NOT NULL | Task status |
| `due_at` | TIMESTAMPTZ | NULL | Due date |
| `completed_at` | TIMESTAMPTZ | NULL | Completion timestamp |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation time |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

---

# 19. Follow-Up Priority

Initial values:

```text
normal
high
urgent
```

Priority should be assigned according to documented workflow rules.

The AI must not independently redefine priority rules.

---

# 20. Follow-Up Status

Initial values:

```text
pending
assigned
in_progress
completed
cancelled
```

---

# 21. Table: `escalations`

## Purpose

Stores situations requiring human review.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Escalation ID |
| `client_id` | UUID | FK → clients.id | Client |
| `assigned_to` | UUID | FK → users.id, NULL | Assigned staff |
| `category` | VARCHAR | NOT NULL | Escalation category |
| `priority` | VARCHAR | NOT NULL | Priority |
| `reason` | TEXT | NOT NULL | Escalation reason |
| `status` | VARCHAR | NOT NULL | Escalation state |
| `resolved_at` | TIMESTAMPTZ | NULL | Resolution time |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation time |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

---

# 22. Escalation Categories

Initial categories:

```text
clinical_concern
medication_concern
sensitive_concern
human_request
emergency_related
unknown_intent
ai_uncertainty
system_failure
```

---

# 23. Escalation Status

Initial values:

```text
open
assigned
in_review
resolved
cancelled
```

---

# 24. Table: `approved_information`

## Purpose

Stores approved information that the AI agent is permitted to retrieve and use.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Information ID |
| `title` | VARCHAR | NOT NULL | Information title |
| `category` | VARCHAR | NOT NULL | Information category |
| `content` | TEXT | NOT NULL | Approved content |
| `version` | INTEGER | NOT NULL | Content version |
| `is_active` | BOOLEAN | NOT NULL | Active status |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update |

---

# 25. Approved Information Principle

The AI should use this table as a controlled source for supported program information.

Example categories:

```text
appointment_information
clinic_logistics
communication
program_information
approved_education
```

The AI must not treat arbitrary database content as medical guidance.

---

# 26. Table: `audit_logs`

## Purpose

Records important system actions for accountability and troubleshooting.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Audit ID |
| `user_id` | UUID | FK → users.id, NULL | User responsible |
| `action` | VARCHAR | NOT NULL | Action performed |
| `entity_type` | VARCHAR | NOT NULL | Affected entity |
| `entity_id` | UUID | NULL | Affected record |
| `metadata` | JSONB | NULL | Relevant non-sensitive metadata |
| `created_at` | TIMESTAMPTZ | NOT NULL | Event timestamp |

---

# 27. Audit Logging Examples

Examples of actions:

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

Sensitive message content should not automatically be copied into audit metadata.

---

# 28. Relationships

## Client → Appointment

```text
clients.id
     |
     | 1:N
     v
appointments.client_id
```

---

## Client → Interaction

```text
clients.id
     |
     | 1:N
     v
interactions.client_id
```

---

## Client → Follow-Up

```text
clients.id
     |
     | 1:N
     v
follow_up_tasks.client_id
```

---

## Client → Escalation

```text
clients.id
     |
     | 1:N
     v
escalations.client_id
```

---

## User → Follow-Up

```text
users.id
     |
     | 1:N
     v
follow_up_tasks.assigned_to
```

---

## User → Escalation

```text
users.id
     |
     | 1:N
     v
escalations.assigned_to
```

---

## Role → User

```text
roles.id
     |
     | 1:N
     v
users.role_id
```

---

# 29. Referential Integrity

Foreign keys shall be used to maintain relationships.

Example:

```text id="qczr4w"
appointments.client_id
        |
        v
clients.id
```

An appointment must not reference a client that does not exist.

---

# 30. Delete Behavior

Sensitive or historically important records should not normally be physically deleted simply because they are no longer active.

Where appropriate, records should use status fields or soft-deletion mechanisms.

Example:

```text id="9ct4vo"
Client
  |
  v
is_active = false
```

The exact retention and deletion policy should be defined in `docs/safety-privacy.md`.

---

# 31. Timestamps

Major tables should include:

```text
created_at
updated_at
```

Timestamp columns should use:

```text
TIMESTAMPTZ
```

to preserve timezone-aware timestamps.

---

# 32. UUIDs

The preferred identifier type is UUID.

Example:

```text id="z1of4b"
550e8400-e29b-41d4-a716-446655440000
```

UUIDs reduce predictable sequential identifiers and make distributed systems easier to manage.

---

# 33. Indexing Strategy

Indexes should be created for fields frequently used in lookups and workflows.

Initial indexes should include:

### Clients

```text
clients.external_reference
clients.enrollment_status
```

### Appointments

```text
appointments.client_id
appointments.scheduled_at
appointments.status
```

### Interactions

```text
interactions.client_id
interactions.created_at
interactions.intent_category
```

### Follow-Ups

```text
follow_up_tasks.client_id
follow_up_tasks.assigned_to
follow_up_tasks.status
follow_up_tasks.due_at
```

### Escalations

```text
escalations.client_id
escalations.assigned_to
escalations.status
escalations.priority
```

Indexes should be added based on actual query patterns rather than added unnecessarily.

---

# 34. Appointment Query Optimization

A common query will identify upcoming appointments.

Conceptually:

```text id="b5r4gc"
WHERE status = 'scheduled'
AND scheduled_at BETWEEN current_time AND future_time
```

An index involving `scheduled_at` and `status` may be appropriate.

The final index strategy should be validated using actual application queries.

---

# 35. Data Validation

The database should enforce basic data integrity.

Examples:

- Required fields cannot be null.
- Email addresses used for authentication should be unique.
- Foreign keys must reference existing records.
- Status fields must contain valid values.
- Communication preference should belong to an existing client.
- Appointment timestamps must be valid.
- Priority values must be valid.

Business-level validation should also exist in the FastAPI application layer.

---

# 36. Database vs Application Validation

Validation should occur at multiple layers.

```text id="c1s98x"
Frontend Validation
        |
        v
FastAPI Validation
        |
        v
Business Rules
        |
        v
Database Constraints
```

Frontend validation improves user experience.

Backend validation provides security and correctness.

Database constraints provide data integrity.

The backend must never rely solely on frontend validation.

---

# 37. Sensitive Data Principles

CareFlow AI should minimize storage of sensitive health information.

The database should not become a full electronic medical record.

The MVP primarily needs operational information required for:

- Engagement
- Appointments
- Communication
- Follow-up
- Escalation
- Program analytics

---

# 38. AI Data Access

The AI should access data through controlled backend services.

Preferred:

```text id="6dqpr5"
AI
 |
 v
FastAPI Tool
 |
 v
Authorization
 |
 v
Database Query
 |
 v
Minimal Result
 |
 v
AI
```

Not permitted:

```text id="0rvvbb"
AI
 |
 v
Direct unrestricted PostgreSQL access
```

---

# 39. Database Migration Strategy

All schema changes shall use migrations.

A migration tool such as Alembic should be used with the FastAPI application.

Example workflow:

```text id="6g6p8u"
Modify SQLAlchemy Model
        |
        v
Generate Migration
        |
        v
Review Migration
        |
        v
Run Migration
        |
        v
Test Database
```

AI coding agents must not silently modify the production schema.

---

# 40. Seed Data

The project should include synthetic seed data for development and demonstration.

Example:

```text id="f4j8qk"
10–50 synthetic clients
Multiple appointments
Multiple interactions
Follow-up tasks
Escalations
Approved information
```

All seed data must clearly be synthetic.

No real patient information should be used.

---

# 41. Example Synthetic Client

Example:

```text id="nq3vja"
Client ID:
client-demo-001

Preferred Name:
Demo Client

Preferred Language:
English

Enrollment Status:
active

Communication Channel:
web
```

This is demonstration data only.

---

# 42. Analytics Data

Power BI should consume appropriately aggregated or de-identified data.

Example analytical dataset:

```text id="1u7pzx"
Date
Appointment Status
Reminder Count
Missed Appointment Count
Follow-Up Count
Barrier Category
Escalation Category
Escalation Status
```

Individual identifying information should not be included unless explicitly required and appropriately protected.

---

# 43. Data Lifecycle

The system should define lifecycle stages.

```text id="2j6fca"
Created
   |
   v
Active
   |
   v
Updated / Used
   |
   v
Inactive
   |
   v
Retained / Deleted according to policy
```

Exact retention periods are outside this document and shall be defined by the safety/privacy requirements and deployment context.

---

# 44. Transaction Requirements

Operations involving multiple related database changes should use database transactions.

Example:

```text id="8k0rws"
Create Escalation
       |
       +--> Create escalation record
       |
       +--> Record interaction
       |
       +--> Create audit event
       |
       v
Commit Transaction
```

If a critical operation fails, the system should avoid leaving partially completed data.

---

# 45. Concurrency Considerations

The application should account for situations where multiple users or workflows attempt to modify the same record.

Examples:

- Two staff members update the same appointment.
- A workflow creates a follow-up while staff manually creates one.
- A reminder workflow runs twice.

The backend should use appropriate transaction and uniqueness strategies to prevent inconsistent states.

---

# 46. Idempotency Database Support

Critical automated operations should have a mechanism for detecting duplicates.

For example, a reminder event may use a unique combination such as:

```text id="ly6n7p"
client_id
appointment_id
reminder_type
scheduled_date
```

The final schema may introduce a dedicated notification/event table if required by the workflow implementation.

---

# 47. Future Tables

The following tables may be introduced later if the product expands:

```text
notifications
message_templates
workflow_events
barriers
staff_notes
organizations
facilities
consent_records
```

These should not be added to the MVP database unless required.

---

# 48. Database Security

Database security shall include:

- Strong database credentials.
- Secrets stored outside source control.
- Least-privilege database users.
- Restricted network access.
- Encrypted connections in production where applicable.
- Regular backups in production.
- No database passwords committed to GitHub.

---

# 49. Development Database

Local development may use Docker.

Example:

```text id="e1h3zv"
Docker
  |
  v
PostgreSQL Container
  |
  v
CareFlow Database
```

The development database should use synthetic data.

---

# 50. Production Database

A production deployment should use a managed or appropriately secured PostgreSQL environment.

Production requirements may include:

- Automated backups
- Monitoring
- Access controls
- Encryption
- Recovery procedures
- Database migrations
- Disaster recovery planning

Production deployment is outside the MVP scope.

---

# 51. Database Testing

Database-related tests should cover:

- Table creation
- Required fields
- Foreign keys
- Unique constraints
- Valid statuses
- Invalid statuses
- Relationship behavior
- Migration correctness
- Transaction behavior
- Duplicate prevention

---

# 52. Example Database Test

A synthetic test might verify:

```text id="7fj4f9"
Given:
A valid client exists.

When:
An appointment is created for that client.

Then:
The appointment is stored successfully.

And:
appointments.client_id references the correct client.
```

---

# 53. Database Definition of Done

The database design shall be considered MVP-ready when:

- Core entities are defined.
- Tables are implemented.
- Relationships are enforced.
- Primary keys are defined.
- Foreign keys are defined.
- Required constraints exist.
- Appropriate indexes exist.
- Migrations are implemented.
- Synthetic seed data exists.
- Database tests exist.
- Sensitive data is minimized.
- AI access occurs through controlled backend services.
- No real patient information is included.

---

# 54. Database Source-of-Truth Principle

PostgreSQL is the authoritative source for:

- Client records
- Appointment records
- Interaction records
- Follow-up tasks
- Escalations
- Communication preferences
- Approved information
- Audit records

n8n may orchestrate workflows.

The AI may reason and request actions.

The frontend may display information.

But PostgreSQL remains the primary persistent source of truth.

---

# 55. Related Documentation

This document should be used together with:

- `docs/PRD.md`
- `docs/SRS.md`
- `docs/system-architecture.md`
- `docs/ai-agent-specification.md`

The next technical document is:

**`docs/api.md`**

That document will define the actual FastAPI REST API: endpoints, HTTP methods, request schemas, response schemas, authentication, authorization, validation, errors, and how the frontend, AI agent, and n8n communicate with the backend.