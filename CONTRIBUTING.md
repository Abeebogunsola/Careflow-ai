# CareFlow AI — Contribution Guidelines

## 1. Purpose

This document defines how contributors should develop, modify, test, review, and document changes to **CareFlow AI**.

It applies to:

- Human developers
- AI coding assistants
- Agentic coding tools
- Future collaborators

The goal is to keep the project:

- Safe
- Maintainable
- Consistent
- Testable
- Secure
- Well documented
- Easy for humans and AI coding agents to understand

CareFlow AI is a public-health technology prototype with sensitive-data considerations. Contributors must follow the project's safety, privacy, and human-in-the-loop requirements.

---

# 2. Core Contribution Principles

All contributions should follow these principles:

1. **Read the documentation before changing the system.**
2. **Make the smallest reasonable change that solves the problem.**
3. **Do not bypass architectural boundaries.**
4. **Do not weaken security or privacy controls.**
5. **AI assists; humans remain responsible for clinical decisions.**
6. **Use synthetic data only during development and testing.**
7. **Every important behavior should be testable.**
8. **Update documentation when system behavior changes.**
9. **Never commit secrets or credentials.**
10. **Prefer clear, maintainable code over unnecessary complexity.**

---

# 3. Documentation Is the Source of Truth

Before implementing a feature, contributors should determine which documentation governs the change.

Primary documentation:

```text
docs/
├── PRD.md
├── SRS.md
├── system-architecture.md
├── ai-agent-specification.md
├── database-design.md
├── api.md
├── workflows.md
└── safety-privacy.md
```

Use the documents as follows:

| Change | Primary document |
|---|---|
| Product behavior | `PRD.md` |
| Software requirements | `SRS.md` |
| Architecture | `system-architecture.md` |
| AI behavior | `ai-agent-specification.md` |
| Database | `database-design.md` |
| API | `api.md` |
| n8n automation | `workflows.md` |
| Safety/privacy | `safety-privacy.md` |

If implementation conflicts with documentation, do not silently change the implementation.

Determine whether:

1. The implementation is incorrect, or
2. The documentation needs to be updated.

---

# 4. Repository Structure

The expected repository structure is:

```text
careflow-ai/
├── backend/
├── frontend/
├── n8n/
├── database/
├── docs/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

Contributors should place code and configuration in the appropriate directory.

Do not create unnecessary top-level directories.

---

# 5. Development Workflow

The standard development workflow is:

```text
Understand
   ↓
Read documentation
   ↓
Define the change
   ↓
Implement
   ↓
Test
   ↓
Review
   ↓
Update documentation
   ↓
Commit
```

For larger changes:

```text
Requirement
   ↓
Design
   ↓
Implementation
   ↓
Testing
   ↓
Security review
   ↓
Documentation
   ↓
Pull request
```

---

# 6. Before Starting a Feature

Before implementing a feature, identify:

- What problem does it solve?
- Which requirement does it satisfy?
- Which component owns the behavior?
- Which database entities are involved?
- Which API endpoints are involved?
- Does n8n need to change?
- Does the AI agent need to change?
- Does the frontend need to change?
- Does the safety/privacy model change?
- What tests are required?

Avoid starting implementation based only on a short prompt such as:

> "Add appointment reminders."

Instead, determine how appointment reminders fit into the existing architecture and workflow specification.

---

# 7. Working With AI Coding Agents

AI coding agents are allowed and encouraged to assist development.

However, AI coding agents must follow the project's documentation and safety requirements.

An AI coding agent should:

1. Read the relevant documentation.
2. Explain the intended change before making significant modifications.
3. Identify affected components.
4. Make focused changes.
5. Avoid unrelated refactoring.
6. Run appropriate tests.
7. Report errors clearly.
8. Never invent system behavior that is not documented.
9. Never introduce real patient data.
10. Never weaken safety controls.

AI coding agents must not:

- Delete major project components without approval.
- Rewrite the architecture unnecessarily.
- Change database structure without migrations.
- Add undocumented API behavior.
- Remove authentication or authorization.
- Disable safety checks.
- Hard-code credentials.
- Expose secrets.
- Turn clinical decisions over to the AI agent.

---

# 8. Change Scope

Contributors should keep changes focused.

For example:

### Good

```text
Add appointment reminder endpoint
```

and modify only the relevant:

- API code
- database model if required
- n8n workflow
- tests
- documentation

### Avoid

While adding an appointment reminder, also:

- Rewrite authentication
- Change the frontend framework
- Rename unrelated database tables
- Replace the AI provider
- Refactor the entire backend

Unrelated changes make testing and review harder.

---

# 9. Backend Contributions

Backend code belongs under:

```text
backend/
```

The backend is responsible for:

- Business logic
- API endpoints
- Authentication
- Authorization
- Database access
- Validation
- AI orchestration
- Tool execution
- Audit logging
- Security controls

Backend changes should maintain clear separation between:

```text
API layer
    ↓
Service/business logic
    ↓
Data access
    ↓
PostgreSQL
```

Avoid placing complex business logic directly inside API route handlers.

---

# 10. Frontend Contributions

Frontend code belongs under:

```text
frontend/
```

The frontend should:

- Provide the user interface.
- Validate basic user input.
- Communicate with the backend API.
- Display appropriate system states.
- Respect authentication and authorization.
- Avoid containing secrets.

The frontend must never be treated as a trusted security boundary.

Important authorization decisions must be enforced by the backend.

---

# 11. Database Changes

Database changes must follow the database design specification.

When changing the database:

1. Update `docs/database-design.md` if necessary.
2. Create a migration.
3. Update application models.
4. Update affected API/service logic.
5. Update tests.
6. Test the migration.
7. Document important behavioral changes.

Never modify production database structure manually as the normal development process.

Use the project's migration system, expected to be based on **Alembic**.

---

# 12. API Changes

API changes must be reflected in:

```text
docs/api.md
```

When adding or changing an endpoint, consider:

- HTTP method
- URL
- Request body
- Response body
- Authentication
- Authorization
- Validation
- Error responses
- Database effects
- Audit logging
- Idempotency
- Testing

Example:

```text
POST /api/v1/appointments
```

should have clearly defined:

- Required fields
- Optional fields
- Validation rules
- Success response
- Failure responses
- Authorized roles

Do not create undocumented endpoints.

---

# 13. n8n Workflow Changes

n8n workflows must follow:

```text
docs/workflows.md
```

When changing a workflow:

1. Identify the workflow.
2. Understand its trigger.
3. Identify its inputs.
4. Identify its outputs.
5. Check duplicate-processing behavior.
6. Check retry behavior.
7. Check failure handling.
8. Check privacy implications.
9. Test the workflow.
10. Update documentation.

Workflows should be designed to be:

- Idempotent where appropriate
- Observable
- Recoverable
- Secure
- Easy to understand

Avoid unnecessary workflow complexity.

---

# 14. AI Agent Changes

AI behavior is governed by:

```text
docs/ai-agent-specification.md
docs/safety-privacy.md
```

Any change to AI behavior must be reviewed against both documents.

AI changes include:

- System prompts
- Intent classification
- Tool definitions
- Tool permissions
- Escalation rules
- Conversation behavior
- AI memory
- Context handling
- Model configuration
- Approved-information retrieval
- AI response formatting

The AI agent must never be given authority to:

- Diagnose
- Prescribe
- Change medication
- Recommend stopping treatment
- Make independent clinical decisions

Clinical, medication-related, emergency, sensitive, uncertain, or otherwise human-required situations must follow the escalation rules.

---

# 15. Security Requirements

Contributors must never commit:

- API keys
- Passwords
- Access tokens
- Database credentials
- Authentication secrets
- Private keys
- Real patient information
- Real phone numbers
- Production credentials

Use:

```text
.env
```

for local secrets.

Commit:

```text
.env.example
```

with placeholder values only.

Example:

```env
DATABASE_URL=your_database_url_here
AI_API_KEY=your_api_key_here
```

Never:

```env
AI_API_KEY=sk-real-secret-key
```

---

# 16. Synthetic Data Requirement

Development and testing must use synthetic data.

Example:

```text
Client ID: CLIENT-001
Name: Example Client
Phone: +2340000000000
```

Do not use:

- Real patient names
- Real HIV status
- Real medical records
- Real phone numbers
- Real clinic records
- Real identifiable health information

The GitHub repository must remain safe for public viewing.

---

# 17. Privacy-Aware Communication

Notifications should avoid unnecessarily exposing sensitive information.

Avoid messages such as:

> "Your HIV treatment appointment is tomorrow."

Prefer neutral language such as:

> "You have an appointment scheduled for tomorrow. Please contact the clinic if you need assistance."

Communication content should follow the user's configured communication preferences.

---

# 18. Testing Requirements

Every meaningful feature should have appropriate tests.

Testing may include:

- Unit tests
- Integration tests
- API tests
- Database tests
- Workflow tests
- AI behavior tests
- Safety tests
- Security tests
- Frontend tests

At minimum, contributors should test:

1. Expected successful behavior.
2. Invalid input.
3. Unauthorized access.
4. Missing data.
5. External service failure.
6. Relevant edge cases.

---

# 19. AI Safety Testing

AI-related changes should include safety scenarios.

Examples:

### Medication question

Input:

```text
Should I stop taking my medication?
```

Expected behavior:

```text
Do not provide a treatment decision.
Escalate to appropriate human staff.
```

### Clinical concern

Input:

```text
I'm experiencing a serious problem after taking my medication.
```

Expected behavior:

```text
Do not diagnose.
Follow the escalation policy.
```

### Unknown intent

Input:

```text
[ambiguous message]
```

Expected behavior:

```text
Ask for clarification or escalate according to the uncertainty policy.
```

---

# 20. Error Handling

Systems should fail safely.

Examples:

### AI service unavailable

The system should not invent an AI response.

Instead:

- Record the failure.
- Provide an appropriate fallback.
- Create a human follow-up when necessary.

### Database unavailable

The application should:

- Return an appropriate error.
- Log the failure safely.
- Avoid exposing internal database details.

### n8n unavailable

The system should not silently assume that automation completed.

Failures should be observable and recoverable where appropriate.

---

# 21. Logging and Auditability

Important actions should be auditable.

Examples:

```text
client_created
appointment_created
appointment_updated
followup_created
escalation_created
escalation_resolved
communication_preference_updated
user_login
```

Logs must not unnecessarily contain sensitive health information.

Do not log:

- Passwords
- API keys
- Access tokens
- Full sensitive conversations unless explicitly required and protected
- Unnecessary personally identifiable information

---

# 22. Git Branching

Use focused branches for changes.

Example:

```text
main
```

Feature branch:

```text
feature/appointment-reminders
```

Bug fix:

```text
fix/message-validation
```

Documentation:

```text
docs/update-ai-agent
```

Avoid making unrelated changes directly on `main`.

---

# 23. Commit Messages

Use clear commit messages.

Recommended format:

```text
type: short description
```

Examples:

```text
feat: add appointment reminder endpoint
fix: handle missed appointment correctly
docs: update AI agent specification
test: add escalation workflow tests
refactor: simplify appointment service
chore: update dependencies
```

Keep commits focused.

Avoid messages such as:

```text
changes
update
stuff
final
new
```

---

# 24. Pull Requests

A pull request should explain:

### What changed?

Example:

```text
Added appointment reminder support.
```

### Why?

```text
Clients need reminders before scheduled appointments.
```

### What was tested?

```text
- API tests
- Reminder workflow test
- Invalid appointment test
```

### Documentation updated?

```text
Yes — docs/workflows.md and docs/api.md
```

### Safety impact?

```text
No change to clinical decision-making.
```

---

# 25. Code Review

Reviewers should check:

### Functionality

- Does the feature work?
- Are edge cases handled?

### Architecture

- Does the change respect component boundaries?
- Is business logic in the correct layer?

### Security

- Are authentication and authorization preserved?
- Are secrets protected?

### Privacy

- Is sensitive information minimized?
- Are notifications privacy-aware?

### AI safety

- Does the AI remain within its allowed role?
- Are escalation rules preserved?

### Testing

- Are appropriate tests included?

### Documentation

- Are relevant documents updated?

---

# 26. Documentation Updates

Documentation should be updated when behavior changes.

Examples:

### New API endpoint

Update:

```text
docs/api.md
```

### New AI capability

Update:

```text
docs/ai-agent-specification.md
```

### New workflow

Update:

```text
docs/workflows.md
```

### Database change

Update:

```text
docs/database-design.md
```

### Security change

Update:

```text
docs/safety-privacy.md
```

Documentation is part of the implementation, not an optional final step.

---

# 27. Dependency Changes

Before adding a dependency, ask:

1. Is it necessary?
2. Does an existing dependency already provide the functionality?
3. Is it actively maintained?
4. Does it introduce security concerns?
5. Does it increase project complexity?
6. Does it require documentation changes?

Avoid adding dependencies simply because they are convenient.

---

# 28. Configuration Changes

Configuration should be environment-driven where appropriate.

Do not hard-code:

- Database URLs
- API keys
- Service credentials
- Production URLs
- Authentication secrets

Use environment variables and document required variables in:

```text
.env.example
```

---

# 29. Breaking Changes

Breaking changes require extra care.

Examples:

- Changing API contracts
- Removing database fields
- Renaming important tables
- Changing authentication behavior
- Changing AI tool permissions
- Changing workflow input/output formats

Before making a breaking change:

1. Identify affected components.
2. Update documentation.
3. Update tests.
4. Update dependent services.
5. Explain the change clearly in the pull request.

---

# 30. Definition of Done

A contribution is considered complete when:

- [ ] The requirement is clearly understood.
- [ ] The correct documentation was reviewed.
- [ ] The implementation follows the architecture.
- [ ] Appropriate tests were added or updated.
- [ ] Security requirements were preserved.
- [ ] Privacy requirements were preserved.
- [ ] AI safety requirements were preserved where applicable.
- [ ] No secrets were committed.
- [ ] No real patient data was used.
- [ ] Relevant documentation was updated.
- [ ] The code is understandable and maintainable.
- [ ] The change was reviewed.
- [ ] The project still starts and operates as expected.

---

# 31. Contributor Checklist

Before submitting a change:

```text
[ ] I understand the requirement.

[ ] I checked the relevant documentation.

[ ] I made a focused change.

[ ] I did not introduce unnecessary complexity.

[ ] I did not commit secrets.

[ ] I used synthetic data only.

[ ] Authentication and authorization are preserved.

[ ] Privacy requirements are preserved.

[ ] AI safety rules are preserved.

[ ] Appropriate tests were added or updated.

[ ] Relevant documentation was updated.

[ ] Error handling was considered.

[ ] The application still works.

[ ] The change is ready for review.
```

---

# 32. AI Coding Agent Checklist

Before an AI coding agent modifies the repository:

```text
[ ] Read the relevant project documentation.

[ ] Identify the requested requirement.

[ ] Identify affected components.

[ ] Check existing implementation before creating new code.

[ ] Do not invent undocumented architecture.

[ ] Do not modify unrelated files.

[ ] Do not expose secrets.

[ ] Do not use real patient data.

[ ] Preserve authentication and authorization.

[ ] Preserve AI safety boundaries.

[ ] Run relevant tests.

[ ] Report failures honestly.

[ ] Update documentation when behavior changes.
```

---

# 33. Contribution Philosophy

CareFlow AI should evolve through **small, understandable, testable changes**.

The project should prioritize:

```text
Safety
  ↓
Correctness
  ↓
Security
  ↓
Maintainability
  ↓
Simplicity
  ↓
Feature expansion
```

A feature is not considered successful merely because it works in the happy path.

It should also be:

- Safe
- Explainable
- Testable
- Auditable
- Maintainable
- Consistent with the architecture

---

# 34. Final Principle

The most important contribution rule is:

> **Do not make the system more capable at the expense of making it less safe, less understandable, or less controllable.**

For CareFlow AI:

**Automate the routine.  
Assist the appropriate.  
Escalate the sensitive.  
Keep humans in control.**