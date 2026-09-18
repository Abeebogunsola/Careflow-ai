-- ============================================================================
-- CareFlow AI — Analytical Star Schema SQL Views for PostgreSQL 15+ (Production)
--
-- Source of truth: docs/system-architecture.md - Section 17, docs/PRD.md - Section 9,
-- and docs/database-design.md - Section 42.
--
-- Designed for Microsoft Power BI DirectQuery or Import Mode against PostgreSQL.
-- Enforces absolute data minimization: client PII (names, phones) is strictly excluded;
-- one-way surrogate hash keys are used for client entity relationships.
-- ============================================================================

-- 1. Date Dimension View
CREATE OR REPLACE VIEW view_dim_date AS
SELECT DISTINCT
    scheduled_at::date AS date_key,
    TO_CHAR(scheduled_at, 'YYYY-MM-DD') AS full_date,
    EXTRACT(YEAR FROM scheduled_at)::INTEGER AS year,
    EXTRACT(MONTH FROM scheduled_at)::INTEGER AS month,
    TRIM(TO_CHAR(scheduled_at, 'Month')) AS month_name,
    TO_CHAR(scheduled_at, 'YYYY-MM') AS year_month,
    'Q' || EXTRACT(QUARTER FROM scheduled_at)::INTEGER AS quarter,
    EXTRACT(DAY FROM scheduled_at)::INTEGER AS day,
    TRIM(TO_CHAR(scheduled_at, 'Day')) AS day_of_week,
    CASE 
        WHEN EXTRACT(ISODOW FROM scheduled_at) IN (6, 7) THEN 1 
        ELSE 0 
    END AS is_weekend
FROM appointments
WHERE scheduled_at IS NOT NULL;


-- 2. De-Identified Client Dimension View
CREATE OR REPLACE VIEW view_dim_client AS
SELECT
    id AS client_id,
    SUBSTRING(MD5(id::text), 1, 8) AS client_code, -- De-identified non-reversible surrogate hash
    enrollment_status,
    preferred_language,
    is_active,
    created_at::date AS enrolled_date
FROM clients;


-- 3. Fact Appointments View
CREATE OR REPLACE VIEW view_fact_appointments AS
SELECT
    id AS appointment_id,
    client_id,
    scheduled_at::date AS date_key,
    appointment_type,
    status,
    COALESCE(location_label, 'Main Clinic') AS location_label,
    CASE WHEN status = 'completed' THEN 1 ELSE 0 END AS is_completed,
    CASE WHEN status = 'missed' THEN 1 ELSE 0 END AS is_missed,
    CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END AS is_scheduled,
    CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END AS is_cancelled,
    CASE WHEN status = 'rescheduled' THEN 1 ELSE 0 END AS is_rescheduled,
    EXTRACT(HOUR FROM scheduled_at)::INTEGER AS scheduled_hour
FROM appointments;


-- 4. Fact Interactions & Outreach View
CREATE OR REPLACE VIEW view_fact_interactions AS
SELECT
    id AS interaction_id,
    client_id,
    created_at::date AS date_key,
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
CREATE OR REPLACE VIEW view_fact_followups AS
SELECT
    id AS followup_id,
    client_id,
    created_at::date AS date_key,
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
    CASE WHEN due_at IS NOT NULL AND CURRENT_DATE > due_at::date AND status != 'completed' THEN 1 ELSE 0 END AS is_overdue
FROM follow_up_tasks;


-- 6. Fact Escalations & Clinical Safety View
CREATE OR REPLACE VIEW view_fact_escalations AS
SELECT
    id AS escalation_id,
    client_id,
    created_at::date AS date_key,
    category AS escalation_category,
    priority,
    status,
    CASE WHEN status = 'open' THEN 1 ELSE 0 END AS is_open,
    CASE WHEN status = 'resolved' THEN 1 ELSE 0 END AS is_resolved,
    CASE 
        WHEN resolved_at IS NOT NULL AND created_at IS NOT NULL 
        THEN ROUND((EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0)::numeric, 2)
        ELSE NULL 
    END AS resolution_hours
FROM escalations;
