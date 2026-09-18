# CareFlow AI — n8n Automation Workflows (Phase 8)

## 1. Overview

**n8n** serves as the workflow automation and orchestration engine for **CareFlow AI — HIV Care Retention & Support Platform**. It automates operational routines, scheduled outreach, message ingestion, barrier triage, follow-up tracking, escalation routing, daily summary reporting, and error handling.

### Architectural Boundary Rule

> **FastAPI remains the authoritative application and data-access layer.**  
> n8n interacts with the system exclusively through authenticated REST endpoints and webhooks. n8n **never** directly queries or mutates the PostgreSQL database.

---

## 2. Core Workflows

The `n8n/workflows/` directory contains 8 production-grade workflow JSON definitions:

| File | Workflow Name | Trigger | Primary Responsibility |
|---|---|---|---|
| [`01_appointment_reminder.json`](./workflows/01_appointment_reminder.json) | `CF — Appointment Reminder` | Schedule (`*/15 * * * *`) | Identifies appointments within reminder window (default: 24h), checks idempotency, generates privacy-conscious reminders, logs outgoing interactions. |
| [`02_missed_appointment.json`](./workflows/02_missed_appointment.json) | `CF — Missed Appointment Detection` | Schedule (`*/30 * * * *`) | Identifies scheduled appointments past grace period (default: 60m), updates status to `missed`, provisions follow-up tasks, sends supportive outreach. |
| [`03_client_message.json`](./workflows/03_client_message.json) | `CF — Client Message Processing` | Webhook (`POST /webhook/careflow-message`) | Normalizes incoming message payloads, invokes FastAPI AI Agent (`/api/v1/messages/process`), branches response vs. escalation, dispatches replies. |
| [`04_barrier_followup.json`](./workflows/04_barrier_followup.json) | `CF — Barrier Follow-Up` | Webhook (`POST /webhook/barrier-event`) | Classifies non-clinical barriers (transport, scheduling, financial, clinic access), creates structured follow-up tasks, logs client acknowledgment. |
| [`05_escalation_notification.json`](./workflows/05_escalation_notification.json) | `CF — Escalation Notification` | Webhook (`POST /webhook/escalation-alert`) | Evaluates escalation category and urgency (`emergency_related`, `clinical_concern`, `medication_concern`), routes immediate alerts to clinical/support staff. |
| [`06_followup_management.json`](./workflows/06_followup_management.json) | `CF — Follow-Up Task Management` | Schedule (`0 */4 * * *`) | Queries pending follow-ups, identifies overdue or high-priority items, compiles coordinator digests to prevent client loss to follow-up. |
| [`07_daily_program_summary.json`](./workflows/07_daily_program_summary.json) | `CF — Daily Program Summary` | Schedule (`0 8 * * *`) | Queries aggregate program metrics via `/api/v1/analytics/overview`, formats an executive daily summary report with zero individual PII. |
| [`08_error_handler.json`](./workflows/08_error_handler.json) | `CF — Automation Error Handler` | Error Trigger | Global error handler. Evaluates execution failures, distinguishes retryable transient network errors from fatal validation bugs, dispatches alerts. |

---

## 3. Privacy & Safety Guarantees

In strict alignment with `docs/safety-privacy.md` and `docs/workflows.md`:

1. **Neutral Outreach Language**: Automated appointment reminders and follow-up messages **never** mention HIV status, antiretroviral therapy (ART), viral load, or sensitive clinical diagnoses.
   - *Prohibited*: `"Your HIV clinic appointment is tomorrow."`
   - *Enforced*: `"Hello! This is a reminder of your upcoming clinic visit on [Date] at [Time]."`
2. **Clinical Non-Intervention**: n8n workflows never make clinical decisions, diagnose, or advise treatment modifications. All clinical concerns route to human staff via `CF — Escalation Notification`.
3. **De-Identified Analytics**: The daily summary workflow consumes `/api/v1/analytics/overview`, ensuring that daily management digests expose only aggregate operational counts and zero PII.

---

## 4. Idempotency & Duplicate Prevention

To prevent sending repeated messages or creating redundant follow-up tasks:
- **Appointment Reminders**: Evaluates outgoing interactions created within the reminder cycle. If an outgoing `appointment_reminder` interaction exists for the client within the window, the appointment is skipped.
- **Missed Appointments**: Only appointments with status `scheduled` are processed. Once transitioned to `missed`, subsequent runs ignore them.
- **Error Retries**: Retries are restricted to retryable transient errors (502, 503, 504, ECONNREFUSED, ETIMEDOUT). Permanent errors (400, 404, 422) fail fast without looping.

---

## 5. Running n8n Locally

### Option A: Unified Docker Compose (Recommended)

From the project root directory:

```bash
docker compose up -d
```

This starts both PostgreSQL (`localhost:5432`) and n8n (`localhost:5678`). The workflow definitions in `./n8n/workflows` are automatically mounted inside the container at `/workflows:ro`.

### Option B: Standalone n8n Compose

From the `n8n/` directory:

```bash
docker compose -f docker-compose.n8n.yml up -d
```

### Accessing the Web UI

Open your browser to:
```text
http://localhost:5678
```

On first startup, create your local administrator user.

---

## 6. Importing & Managing Workflows

Workflows can be imported directly into n8n:
1. Open n8n web interface at `http://localhost:5678`.
2. Click **Workflows** in the left sidebar.
3. Click the **+ Add workflow** button (or the menu in the top right) and select **Import from File...**.
4. Select any JSON file from `n8n/workflows/`.
5. Verify the node parameters and toggle the workflow to **Active** when ready for execution.

CLI import inside the Docker container:
```bash
docker compose exec n8n n8n import:workflow --separate --input=/workflows
```

---

## 7. Environment Variables

Configure these variables in your root `.env` file (copied from `.env.example`):

```env
# n8n Core
N8N_PORT=5678
N8N_HOST=localhost
N8N_PROTOCOL=http
N8N_WEBHOOK_URL=http://localhost:5678/

# Backend Integration
API_BASE_URL=http://backend:8000

# Workflow Parameters
REMINDER_WINDOW_HOURS=24
MISSED_APPOINTMENT_GRACE_MINUTES=60
```
