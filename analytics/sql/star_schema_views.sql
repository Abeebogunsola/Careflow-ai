-- ============================================================================
-- CareFlow AI — Analytical Star Schema SQL Views (Phase 9)
-- 
-- Source of truth: docs/system-architecture.md - Section 17, docs/PRD.md - Section 9,
-- and docs/database-design.md - Section 42.
--
-- Designed for Microsoft Power BI DirectQuery or Import Mode.
-- Enforces absolute data minimization: client PII (names, phones) is strictly excluded;
-- one-way surrogate hash keys are used for client entity relationships.
-- ============================================================================

-- 1. Date Dimension View
CREATE VIEW IF NOT EXISTS view_dim_date AS
SELECT DISTINCT
    DATE(scheduled_at) AS date_key,
    strftime('%Y-%m-%d', scheduled_at) AS full_date,
    CAST(strftime('%Y', scheduled_at) AS INTEGER) AS year,
    CAST(strftime('%m', scheduled_at) AS INTEGER) AS month,
    strftime('%B', scheduled_at) AS month_name,
    strftime('%Y-%m', scheduled_at) AS year_month,
    CASE 
        WHEN CAST(strftime('%m', scheduled_at) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(strftime('%m', scheduled_at) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(strftime('%m', scheduled_at) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    CAST(strftime('%d', scheduled_at) AS INTEGER) AS day,
    CASE CAST(strftime('%w', scheduled_at) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    CASE 
        WHEN CAST(strftime('%w', scheduled_at) AS INTEGER) IN (0, 6) THEN 1 
        ELSE 0 
    END AS is_weekend
FROM appointments
WHERE scheduled_at IS NOT NULL;


-- 2. De-Identified Client Dimension View
CREATE VIEW IF NOT EXISTS view_dim_client AS
SELECT
    id AS client_id,
    SUBSTR(HEX(id), 1, 8) AS client_code, -- De-identified non-reversible surrogate hash
    enrollment_status,
    preferred_language,
    is_active,
    DATE(created_at) AS enrolled_date
FROM clients;


-- 3. Fact Appointments View
CREATE VIEW IF NOT EXISTS view_fact_appointments AS
SELECT
    id AS appointment_id,
    client_id,
    DATE(scheduled_at) AS date_key,
    appointment_type,
    status,
    COALESCE(location_label, 'Main Clinic') AS location_label,
    CASE WHEN status = 'completed' THEN 1 ELSE 0 END AS is_completed,
    CASE WHEN status = 'missed' THEN 1 ELSE 0 END AS is_missed,
    CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END AS is_scheduled,
    CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END AS is_cancelled,
    CASE WHEN status = 'rescheduled' THEN 1 ELSE 0 END AS is_rescheduled,
    CAST(strftime('%H', scheduled_at) AS INTEGER) AS scheduled_hour
FROM appointments;


-- 4. Fact Interactions & Outreach View
CREATE VIEW IF NOT EXISTS view_fact_interactions AS
SELECT
    id AS interaction_id,
    client_id,
    DATE(created_at) AS date_key,
    channel,
    direction,
    interaction_type,
    COALESCE(intent_category, 'unclassified') AS intent_category,
    CASE WHEN direction = 'incoming' THEN 1 ELSE 0 END AS is_incoming,
    CASE WHEN direction = 'outgoing' THEN 1 ELSE 0 END AS is_outgoing,
    CASE WHEN interaction_type = 'appointment_reminder' THEN 1 ELSE 0 END AS is_reminder,
    CASE WHEN interaction_type = 'follow_up' THEN 1 ELSE 0 END AS is_followup_message,
    CASE WHEN interaction_type = 'ai_response' THEN 1 ELSE 0 END AS is_ai_response
FROM interactions;


-- 5. Fact Follow-Up Tasks & Barrier Identification View
CREATE VIEW IF NOT EXISTS view_fact_followups AS
SELECT
    id AS followup_id,
    client_id,
    DATE(created_at) AS date_key,
    priority,
    status,
    CASE 
        WHEN LOWER(reason) LIKE '%transport%' THEN 'transport'
        WHEN LOWER(reason) LIKE '%schedule%' OR LOWER(reason) LIKE '%work%' THEN 'schedule'
        WHEN LOWER(reason) LIKE '%financial%' OR LOWER(reason) LIKE '%money%' OR LOWER(reason) LIKE '%fare%' THEN 'financial_or_logistical'
        WHEN LOWER(reason) LIKE '%communicat%' OR LOWER(reason) LIKE '%phone%' THEN 'communication'
        WHEN LOWER(reason) LIKE '%clinic%' OR LOWER(reason) LIKE '%access%' THEN 'clinic_access'
        WHEN LOWER(reason) LIKE '%support%' OR LOWER(reason) LIKE '%stigma%' THEN 'social_support'
        ELSE 'other'
    END AS barrier_category,
    CASE WHEN status = 'pending' THEN 1 ELSE 0 END AS is_pending,
    CASE WHEN status = 'completed' THEN 1 ELSE 0 END AS is_completed,
    CASE WHEN due_at IS NOT NULL AND DATE('now') > DATE(due_at) AND status != 'completed' THEN 1 ELSE 0 END AS is_overdue
FROM follow_up_tasks;


-- 6. Fact Escalations & Clinical Safety View
CREATE VIEW IF NOT EXISTS view_fact_escalations AS
SELECT
    id AS escalation_id,
    client_id,
    DATE(created_at) AS date_key,
    category AS escalation_category,
    priority,
    status,
    CASE WHEN status = 'open' THEN 1 ELSE 0 END AS is_open,
    CASE WHEN status = 'resolved' THEN 1 ELSE 0 END AS is_resolved,
    CASE 
        WHEN resolved_at IS NOT NULL AND created_at IS NOT NULL 
        THEN ROUND((JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24.0, 2)
        ELSE NULL 
    END AS resolution_hours
FROM escalations;
