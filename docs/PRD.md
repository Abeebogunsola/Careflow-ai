# CareFlow AI — Product Requirements Document (PRD)

**Product:** CareFlow AI  
**Product Type:** AI-Powered HIV Care Retention & Support Platform  
**Document:** Product Requirements Document (PRD)  
**Version:** 1.0  
**Status:** Draft / Product Definition  
**Primary Use Case:** HIV care retention, patient engagement, and follow-up support  
**Development Approach:** AI-assisted / Agentic Software Development  

---

## 1. Product Overview

### 1.1 Product Name

**CareFlow AI**

### 1.2 Product Title

**CareFlow AI — HIV Care Retention & Support Platform**

### 1.3 Product Summary

CareFlow AI is an AI-powered patient engagement and care-retention platform designed to support HIV care programs by helping maintain consistent communication between healthcare programs and people receiving HIV care.

The platform combines an AI conversational agent, automated workflows, structured patient information, appointment tracking, follow-up management, human escalation, and program-level analytics.

The system is designed to help health programs identify missed appointments, provide appropriate reminders and supportive communication, capture non-clinical barriers to care, and route situations requiring human intervention to authorized healthcare or program staff.

CareFlow AI is **not intended to diagnose HIV, prescribe medication, modify treatment, or replace healthcare professionals**.

---

# 2. Problem Statement

People receiving HIV treatment require ongoing engagement with healthcare services. However, maintaining consistent engagement can be affected by practical, informational, social, and logistical barriers.

Examples may include:

- Forgetting appointments.
- Difficulty remembering routine treatment-related tasks.
- Transportation or financial challenges.
- Work or family commitments.
- Difficulty communicating with healthcare programs.
- Lack of timely follow-up after missed appointments.
- Need for additional information or support.
- Reluctance to contact healthcare workers about challenges.
- Administrative gaps in tracking follow-up activities.

Healthcare and public-health programs may also manage large numbers of clients, making manual follow-up difficult to perform consistently.

### Core Problem

> **Health programs need a scalable and supportive way to maintain communication with clients, identify missed or upcoming care activities, capture reported barriers, and ensure that situations requiring human intervention reach the appropriate staff member.**

---

# 3. Product Vision

> **To create a privacy-conscious, AI-powered care-support platform that helps HIV programs maintain meaningful engagement with clients while keeping healthcare professionals at the center of clinical decision-making.**

CareFlow AI should make routine patient engagement more:

- Timely
- Consistent
- Supportive
- Scalable
- Data-driven
- Human-centered

---

# 4. Product Goals

## 4.1 Primary Goals

CareFlow AI should:

1. Support ongoing patient engagement.
2. Automate appropriate appointment and care-related reminders.
3. Detect missed appointments and initiate predefined follow-up workflows.
4. Allow clients to communicate with the support system through a conversational interface.
5. Identify common non-clinical barriers reported by clients.
6. Escalate appropriate situations to authorized human staff.
7. Maintain structured records of interactions and follow-up activities.
8. Provide program-level analytics through Power BI.
9. Reduce repetitive administrative work for health-program staff.
10. Demonstrate responsible use of Agentic AI in a healthcare-support context.

---

# 5. Product Non-Goals

CareFlow AI will **not**:

- Diagnose HIV or other diseases.
- Prescribe medication.
- Change a client's treatment regimen.
- Recommend stopping treatment.
- Replace doctors, nurses, pharmacists, counselors, or other healthcare professionals.
- Make independent clinical decisions.
- Determine a person's medical eligibility for treatment.
- Interpret laboratory results as a substitute for a clinician.
- Provide emergency medical care.
- Store real patient information in the public GitHub repository.

These boundaries are fundamental product requirements.

---

# 6. Target Users

CareFlow AI has three primary user groups.

## 6.1 Clients / Patients

People enrolled in an HIV care program who require:

- Appointment reminders.
- Supportive communication.
- Program information.
- Follow-up assistance.
- A convenient communication channel.
- A way to request human assistance.

The system should use respectful, non-judgmental, privacy-conscious language.

---

## 6.2 Healthcare / Program Staff

Authorized staff who need to:

- Register clients.
- Manage appointments.
- View follow-up tasks.
- Review escalations.
- Respond to clients.
- Monitor engagement.
- Track follow-up outcomes.

---

## 6.3 Program Managers / Administrators

Users who require aggregate information about program performance.

They may need to monitor:

- Enrollment.
- Appointment activity.
- Missed appointments.
- Follow-up activity.
- Re-engagement.
- Communication trends.
- Reported barriers.
- Workflow performance.

Program managers should primarily receive **aggregate or appropriately de-identified information** rather than unnecessary individual-level health information.

---

# 7. Core User Journeys

## 7.1 Client Registration

```text
Authorized Staff
      ↓
Create Client Record
      ↓
Assign Client ID
      ↓
Record Communication Preferences
      ↓
Record Appointment
      ↓
Client Enrolled
```

---

## 7.2 Appointment Reminder

```text
Upcoming Appointment
        ↓
Automation Trigger
        ↓
Check Communication Preferences
        ↓
Generate Approved Reminder
        ↓
Send Notification
        ↓
Record Interaction
```

---

## 7.3 Missed Appointment

```text
Appointment Date Passed
        ↓
Attendance Not Recorded
        ↓
Workflow Triggered
        ↓
Supportive Follow-up Message
        ↓
Client Response
        ↓
AI Intent Classification
        ↓
Appropriate Workflow
```

Possible outcomes:

```text
Rescheduling Request
        ↓
Create Staff Task

General Support
        ↓
Provide Approved Information

Reported Barrier
        ↓
Record Barrier
        ↓
Create Follow-up Task

Potentially Sensitive / Clinical Concern
        ↓
Human Escalation
```

---

# 8. Product Features

## 8.1 Client Management

Authorized staff can:

- Create client records.
- Generate unique client identifiers.
- Update permitted client information.
- Manage communication preferences.
- View relevant engagement history.

---

## 8.2 Appointment Management

The system should support:

- Appointment creation.
- Appointment date/time.
- Appointment status.
- Attendance recording.
- Upcoming appointment detection.
- Missed appointment detection.
- Rescheduling requests.

---

## 8.3 AI Support Agent

The AI agent will provide a conversational interface for clients.

The agent should be able to:

- Understand natural-language messages.
- Identify user intent.
- Answer approved non-clinical questions.
- Assist with appointment-related requests.
- Capture reported barriers.
- Trigger predefined workflows.
- Escalate situations requiring human intervention.
- Maintain appropriate conversational context.

---

## 8.4 Reminder Automation

The system should automatically support:

- Upcoming appointment reminders.
- Follow-up reminders.
- Configurable reminder timing.
- Communication preferences.
- Reminder logging.
- Failed notification handling.

Medication-related reminders, if implemented, should function only as **user-configured reminders** and must not independently modify treatment instructions or provide prescribing advice.

---

## 8.5 Missed Appointment Detection

The platform should detect when:

```text
Expected appointment
        +
No attendance recorded
        =
Potential missed appointment
```

The system can then initiate a predefined follow-up workflow.

---

## 8.6 Barrier Detection

The AI may classify non-clinical barriers communicated by clients.

Examples:

- Transportation difficulties.
- Scheduling conflicts.
- Communication difficulties.
- Financial/logistical concerns.
- Forgetfulness.
- Privacy concerns.
- Desire to speak with staff.

The system should record the appropriate category and trigger the corresponding workflow.

---

## 8.7 Human Escalation

CareFlow AI must support human-in-the-loop workflows.

Examples of escalation situations may include:

- Client requests healthcare staff.
- Client expresses difficulty continuing care.
- Client reports a potentially serious concern.
- AI cannot confidently determine the appropriate workflow.
- Client asks a question outside the system's approved scope.

The AI should **escalate rather than improvise** when human intervention is required.

---

## 8.8 Staff Follow-Up Management

Authorized staff should be able to view:

- Pending follow-ups.
- Reason for follow-up.
- Client identifier.
- Assigned staff member.
- Priority/status.
- Creation date.
- Resolution status.
- Follow-up outcome.

---

## 8.9 Interaction History

The system should maintain appropriate records of:

- Messages.
- Reminders.
- Follow-up events.
- Escalations.
- Staff actions.
- Workflow outcomes.

Access should be controlled according to user roles.

---

# 9. Analytics Requirements

CareFlow AI will include a program analytics layer using **Power BI**.

Analytics should focus primarily on aggregate program performance.

Potential metrics include:

### Engagement

- Total enrolled clients.
- Active clients.
- Number of interactions.
- Response rates.

### Appointment

- Upcoming appointments.
- Completed appointments.
- Missed appointments.
- Rescheduled appointments.

### Follow-up

- Follow-ups initiated.
- Follow-ups completed.
- Pending follow-ups.
- Re-engagement outcomes.

### Barriers

Aggregate categories of reported barriers.

### Workflow Performance

- Reminder delivery rate.
- Follow-up response rate.
- Escalation volume.
- Average follow-up resolution time.

The analytics layer should avoid exposing unnecessary personally identifiable or sensitive health information.

---

# 10. AI Agent Requirements

The AI system will operate within clearly defined boundaries.

## 10.1 Agent Capabilities

The agent may:

- Interpret user messages.
- Classify intent.
- Extract structured information.
- Retrieve approved information.
- Call authorized tools.
- Trigger predefined workflows.
- Create follow-up tasks.
- Escalate to human staff.

---

## 10.2 Agent Tools

Potential tools include:

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

The final tool set will be defined in the AI Agent Specification.

---

## 10.3 Agent Guardrails

The AI must:

- Follow defined system instructions.
- Remain within its approved domain.
- Avoid unsupported medical claims.
- Avoid making clinical decisions.
- Escalate uncertain or sensitive situations.
- Protect confidential information.
- Use approved information sources where applicable.
- Log relevant actions.

---

# 11. Human-in-the-Loop Design

CareFlow AI follows the principle:

> **AI assists. Humans decide.**

The system should distinguish between:

### Automated actions

Examples:

- Reminder scheduling.
- Appointment-status checks.
- Follow-up workflow initiation.
- Administrative classification.

### Human-required actions

Examples:

- Clinical concerns.
- Treatment-related decisions.
- Sensitive cases.
- Complex support situations.
- Requests for healthcare professionals.

---

# 12. Technical Architecture — Initial Direction

The initial technology stack is:

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | FastAPI / Python |
| Database | PostgreSQL |
| Automation | n8n |
| AI | LLM-powered agent |
| Analytics | Microsoft Power BI |
| API | REST |
| Containerization | Docker |
| Version Control | Git / GitHub |

The final architecture will be defined in the System Architecture document.

---

# 13. High-Level System Flow

```text
                    CLIENT
                       │
                       ▼
             ┌──────────────────┐
             │ React Frontend / │
             │ Communication UI │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │   FastAPI API    │
             └────────┬─────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      PostgreSQL   AI Agent      n8n
                      │            │
                      │            ├── Reminders
                      │            ├── Follow-ups
                      │            └── Escalations
                      │
                      ▼
                Agent Tools
                      │
                      ▼
                 Human Staff
                      │
                      ▼
                 Program Data
                      │
                      ▼
                  Power BI
```

---

# 14. Data Requirements

The system may contain entities including:

```text
Client
Staff
Appointment
Message
Interaction
FollowUp
Notification
Escalation
Facility
AuditLog
```

The exact schema, relationships, indexes, constraints, and data lifecycle will be defined in the Database Design document.

---

# 15. Privacy & Security Requirements

Because CareFlow AI concerns HIV care, privacy and security are core requirements.

The system should implement:

- Authentication.
- Role-based access control.
- Authorization.
- Secure API access.
- Environment-based secret management.
- Audit logging.
- Data minimization.
- Appropriate access restrictions.
- Secure communication.
- Protection against accidental disclosure through notifications.
- Separation of development/demo data from real health data.

### Public Repository Requirement

The GitHub repository must contain **synthetic/demo data only**.

The following must never be committed:

- Real patient records.
- Real HIV status information.
- Real phone numbers.
- Real clinical records.
- Passwords.
- API keys.
- Authentication tokens.
- Production credentials.
- Private healthcare-program information.

---

# 16. Responsible AI Requirements

CareFlow AI must be designed according to responsible AI principles.

### Transparency

Users should understand that they are interacting with an AI-supported system where applicable.

### Safety

The AI must not present itself as a doctor or healthcare professional.

### Human Oversight

Sensitive cases must be routed to authorized human staff.

### Privacy

The system should collect and expose only information necessary for the intended workflow.

### Reliability

The system should have fallback behavior when the AI cannot confidently perform an action.

### Auditability

Important AI actions and automated workflow events should be logged.

---

# 17. MVP Scope

The Minimum Viable Product should focus on the smallest complete workflow that demonstrates the product's value.

## MVP Features

### Client

- Basic registration.
- Communication preferences.
- Conversational support interface.
- Appointment information.
- Reminder interaction.

### Staff

- Client management.
- Appointment management.
- Follow-up queue.
- Escalation queue.

### AI

- Intent classification.
- Approved information retrieval.
- Appointment assistance.
- Barrier classification.
- Follow-up creation.
- Human escalation.

### Automation

- Appointment reminder workflow.
- Missed appointment workflow.
- Follow-up workflow.
- Escalation workflow.

### Backend

- REST API.
- Authentication/authorization foundation.
- PostgreSQL database.
- Structured logging.

### Analytics

Initial Power BI dashboard containing:

- Client enrollment.
- Appointment activity.
- Missed appointments.
- Follow-ups.
- Escalations.
- Engagement trends.

---

# 18. Future Scope

Features that may be considered after the MVP:

- WhatsApp integration.
- SMS integration.
- Voice interaction.
- Multilingual support.
- Additional chronic-care programs.
- Advanced analytics.
- Facility-level comparisons.
- More sophisticated AI evaluation.
- Retrieval-Augmented Generation (RAG).
- Notification provider integrations.
- Advanced staff dashboards.
- Offline/community-health-worker functionality.

Future features should not be implemented until the MVP is stable.

---

# 19. Success Metrics

The prototype will be evaluated using measurable system and workflow metrics.

Potential metrics include:

### Engagement

- Percentage of reminders successfully delivered.
- Percentage of clients responding to follow-ups.
- Follow-up completion rate.

### Workflow

- Percentage of missed appointments detected.
- Percentage of follow-ups successfully created.
- Escalation routing accuracy.
- Workflow execution success rate.

### AI

- Intent classification accuracy.
- Tool-selection accuracy.
- Appropriate escalation rate.
- Unsafe-response rate.
- AI fallback rate.

### System

- API response time.
- Workflow failure rate.
- Error rate.
- Test coverage.
- System availability during demonstration.

These metrics will be refined during system design and testing.

---

# 20. Product Constraints

CareFlow AI is an educational/capstone prototype.

Therefore:

1. Development will use synthetic data.
2. The system will not be presented as a clinically validated product.
3. AI outputs will have clearly defined boundaries.
4. Clinical decision-making remains outside the system's scope.
5. External messaging integrations may be simulated during development.
6. The project must remain deployable within reasonable capstone resources.
7. The architecture should be extensible without making the MVP unnecessarily complex.

---

# 21. Key Product Principles

CareFlow AI will follow these principles:

### 1. Human-centered

Technology should support people, not replace human care.

### 2. Privacy by design

Privacy should be considered during system design rather than added later.

### 3. AI with boundaries

The AI should have clearly defined capabilities and limitations.

### 4. Automation with accountability

Every important automated action should have an understandable workflow and appropriate logging.

### 5. Data-driven

Operational decisions should be supported by reliable, structured data.

### 6. Simple before complex

The MVP should solve one clearly defined problem well before additional functionality is added.

### 7. Modular architecture

Components should be replaceable and independently maintainable.

### 8. AI-assisted development

AI coding assistants should work from documented requirements and architectural constraints rather than generating the system without guidance.

---

# 22. Definition of Done — Product Level

The MVP will be considered complete when a user can successfully move through the core workflow:

```text
Client Registration
        ↓
Appointment Created
        ↓
Reminder Generated
        ↓
Client Interaction
        ↓
AI Intent Classification
        ↓
Appropriate Workflow
        ↓
Follow-up / Escalation
        ↓
Staff Action
        ↓
Database Update
        ↓
Analytics
```

The system must also demonstrate:

- Working frontend.
- Working backend API.
- PostgreSQL persistence.
- Working AI agent.
- Working n8n automation.
- Human escalation.
- Basic Power BI analytics.
- Authentication/authorization foundation.
- Automated tests for critical functionality.
- No real patient data.
- Documented limitations and safety boundaries.

---

# 23. Project Documentation Structure

The project documentation will be maintained as a set of related engineering documents.

```text
docs/
│
├── PRD.md
├── SRS.md
├── system-architecture.md
├── ai-agent-specification.md
├── database-design.md
├── api.md
├── workflows.md
└── safety-privacy.md
```

The `README.md` will provide the public-facing overview and developer setup instructions.

---

# 24. Document Status

**Current Status:** Draft — Product Definition

This PRD establishes the product vision, problem, scope, users, requirements, technology direction, and high-level success criteria.

Changes to major product requirements should be reflected in this document before implementation.

---

## Product Statement

> **CareFlow AI is an AI-powered HIV care retention and support platform designed to help health programs maintain consistent, respectful communication with clients, automate appropriate reminders and follow-up workflows, identify reported barriers to care, escalate situations requiring human intervention, and provide program-level analytics — while keeping clinical decision-making and sensitive care decisions with authorized healthcare professionals.**