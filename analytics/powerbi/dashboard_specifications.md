# Power BI Dashboard Specifications — CareFlow AI

This document provides visual design specifications, wireframe layouts, KPI card definitions, visual chart configurations, and slicer interactions for the 4 core Power BI dashboards of CareFlow AI.

All dashboards are built upon the de-identified **Star Schema** (`dim_client`, `dim_date`, `fact_appointments`, `fact_interactions`, `fact_followups`, `fact_escalations`) and standard DAX measures defined in `dax_measures.dax`.

---

## Global Design System & Theme

| Element | Specification |
|---|---|
| **Canvas Size** | 16:9 widescreen (1920 × 1080 px) |
| **Color Palette** | CareFlow Navy (`#0F294A`), Primary Teal (`#0D9488`), Sky Blue (`#0284C7`), Amber Warning (`#D97706`), Crimson Danger (`#DC2626`), Slate Neutral (`#64748B`), Background Off-White (`#F8FAFC`) |
| **Font Family** | Segoe UI (Standard Power BI typography) |
| **Header Banner** | 60px dark navy banner across all pages with Dashboard Title, Data Refresh Timestamp, and CareFlow AI Logo mark |
| **Zero-PII Standard** | No client names, phone numbers, or free-text narrative columns are exposed in any visual or drill-through page |

---

## Dashboard 1: Program Overview & Care Retention

### 1. Objective
Provides public health leadership, facility directors, and program managers with an executive summary of active program enrollment, retention health, appointment attendance adherence, and overall safety escalation rates.

### 2. Layout Wireframe (1920 × 1080)
```
+-----------------------------------------------------------------------------------------------+
| CareFlow AI | Program Overview & Care Retention              Last Refreshed: [Date/Time]     |
+-----------------------------------------------------------------------------------------------+
| [Date Range Slicer]  [Facility Slicer]  [Language Slicer]  [Status Slicer]                    |
+---------------------+---------------------+---------------------+-----------------------------+
| KPI: Total Clients  | KPI: Adherence Rate | KPI: Attended Appts | KPI: Escalation Rate        |
| 1,248 (94.2% Active)| 87.4% (Target 85%)  | 4,812               | 3.2% (Target < 5%)          |
+---------------------+---------------------+---------------------+-----------------------------+
| Visual 1: Monthly Appointment Volume & Adherence Rate Trend     | Visual 3: Active Clients    |
| (Clustered Column + Line Chart: Month vs Attended/Missed + %)   | by Preferred Language       |
|                                                                 | (Donut Chart)               |
+-----------------------------------------------------------------+-----------------------------+
| Visual 2: Appointment Volume by Type & Status                   | Visual 4: Active Clients    |
| (100% Stacked Bar: Routine, Viral Load, Refill, Counseling)     | by Facility                 |
|                                                                 | (Horizontal Bar Chart)      |
+-----------------------------------------------------------------+-----------------------------+
```

### 3. Visual Components & Data Bindings

#### Top Metric Cards (Row 1)
1. **Total Clients**
   - **Measure**: `[Total Clients]`
   - **Secondary Label**: `[Active Clients]` & `[Retention Rate]`
   - **Format**: Integer, `#,#`
2. **Appointment Adherence Rate**
   - **Measure**: `[Appointment Adherence Rate]`
   - **Target Indicator**: Green if `>= 85%`, Amber if `75% - 84.9%`, Red if `< 75%`
   - **Format**: Percentage `0.0%`
3. **Attended Appointments**
   - **Measure**: `[Attended Appointments]`
   - **Secondary Label**: of `[Total Appointments]`
   - **Format**: Integer, `#,#`
4. **Overall Escalation Rate**
   - **Measure**: `[Escalation Rate]`
   - **Target Indicator**: Green if `< 5.0%`, Amber if `5.0% - 8.0%`, Red if `> 8.0%`
   - **Format**: Percentage `0.0%`

#### Chart Visualizations (Rows 2–3)
- **Visual 1: Appointment Volume & Adherence Trend**
  - **Type**: Clustered Column and Line Chart
  - **X-Axis**: `dim_date[YearMonth]` (Sorted chronologically)
  - **Column Values**: `[Attended Appointments]`, `[Missed Appointments]`, `[Cancelled Appointments]`
  - **Line Value**: `[Appointment Adherence Rate]` (Secondary Y-Axis, 0%–100%)
  - **Tooltip**: `[Total Appointments]`, `[Completion Rate]`
- **Visual 2: Appointment Outcomes by Type**
  - **Type**: 100% Stacked Bar Chart
  - **Y-Axis**: `fact_appointments[appointment_type]` (Routine Check-in, Viral Load, Drug Pick-up, Adherence Counseling)
  - **Legend**: `fact_appointments[status]` (completed, missed, cancelled, scheduled)
  - **Values**: `[Total Appointments]`
- **Visual 3: Client Breakdown by Language**
  - **Type**: Donut Chart
  - **Legend**: `dim_client[preferred_language]` (English, Spanish, French, Swahili, Portuguese)
  - **Values**: `[Active Clients]`
  - **Data Labels**: Category & Percentage of Total
- **Visual 4: Client Enrollment by Facility**
  - **Type**: Horizontal Bar Chart (Sorted descending by Active Clients)
  - **Y-Axis**: `dim_client[facility_name]`
  - **X-Axis**: `[Active Clients]`
  - **Data Color**: Teal (`#0D9488`)

### 4. Interactive Slicers & Page Filters
- **Date Slicer**: `dim_date[Date]` (Relative Date: Last 12 Months / Calendar Slider)
- **Facility Dropdown**: `dim_client[facility_name]` (Multi-select enabled, default: All)
- **Preferred Language**: `dim_client[preferred_language]` (Buttons / Pills)
- **Client Status**: `dim_client[status]` (default: `active`)

---

## Dashboard 2: Client Engagement & Communication

### 1. Objective
Enables outreach coordinators, communication specialists, and contact center leads to evaluate inbound and outbound interaction traffic, delivery channel adoption, intent breakdown, and responsiveness.

### 2. Layout Wireframe (1920 × 1080)
```
+-----------------------------------------------------------------------------------------------+
| CareFlow AI | Client Engagement & Communication              Last Refreshed: [Date/Time]     |
+-----------------------------------------------------------------------------------------------+
| [Date Slicer]  [Channel Slicer]  [Direction Slicer]  [Facility Slicer]                        |
+---------------------+---------------------+---------------------+-----------------------------+
| KPI: Total Messages | KPI: Inbound Msgs   | KPI: Outbound Msgs  | KPI: Response Rate          |
| 14,890              | 6,240 (41.9%)       | 8,650 (58.1%)       | 72.1% (Target > 70%)        |
+---------------------+---------------------+---------------------+-----------------------------+
| Visual 1: Interaction Volume Trend by Channel                   | Visual 2: Inbound Message   |
| (Stacked Area Chart: Date vs SMS, WhatsApp, Voice, In-Person)   | Intent Classification       |
|                                                                 | (Treemap / Horizontal Bar)  |
+-----------------------------------------------------------------+-----------------------------+
| Visual 3: Engagement Density (Day of Week vs Time of Day)       | Visual 4: Channel Share     |
| (Heatmap Matrix: Monday-Sunday vs Hourly Intervals)             | (Donut Chart: SMS vs        |
|                                                                 | WhatsApp vs Voice)          |
+-----------------------------------------------------------------+-----------------------------+
```

### 3. Visual Components & Data Bindings

#### Top Metric Cards (Row 1)
1. **Total Interactions**
   - **Measure**: `[Total Interactions]`
   - **Format**: Integer, `#,#`
2. **Inbound Volume**
   - **Measure**: `[Inbound Interactions]`
   - **Secondary Label**: `[Inbound Share %]`
   - **Format**: Integer, `#,#`
3. **Outbound Volume**
   - **Measure**: `[Outbound Interactions]`
   - **Secondary Label**: Automated reminders & follow-ups
   - **Format**: Integer, `#,#`
4. **Client Response Rate**
   - **Measure**: `[Client Response Rate]`
   - **Formula**: `DIVIDE([Inbound Interactions], [Outbound Interactions], 0)`
   - **Format**: Percentage `0.0%`

#### Chart Visualizations (Rows 2–3)
- **Visual 1: Interaction Volume Trend by Channel**
  - **Type**: Stacked Area Chart
  - **X-Axis**: `dim_date[Date]` (Day level or Week level)
  - **Legend**: `fact_interactions[channel]` (sms, whatsapp, voice_call, in_person)
  - **Values**: `[Total Interactions]`
  - **Colors**: SMS (`#0284C7`), WhatsApp (`#10B981`), Voice (`#F59E0B`), In-Person (`#6366F1`)
- **Visual 2: Inbound Intent Classification**
  - **Type**: Horizontal Bar Chart or Treemap
  - **Category**: `fact_interactions[intent]` (appointment_inquiry, barrier_report, medication_question, general_info, gratitude)
  - **Values**: `[Inbound Interactions]`
  - **Data Label**: Count & `% of Inbound`
- **Visual 3: Engagement Density Heatmap**
  - **Type**: Matrix visual with conditional background color formatting
  - **Rows**: `dim_date[DayOfWeekName]` (Monday through Sunday)
  - **Columns**: Hour of Day (00:00 to 23:00, or grouped into 4-hour windows)
  - **Values**: `[Total Interactions]`
  - **Color Scale**: Slate Light to Deep Teal (Lowest `#F1F5F9` to Highest `#0D9488`)
- **Visual 4: Channel Distribution Share**
  - **Type**: Donut Chart
  - **Legend**: `fact_interactions[channel]`
  - **Values**: `[Total Interactions]`
  - **Tooltip**: `[Inbound Interactions]`, `[Outbound Interactions]`

### 4. Interactive Slicers & Page Filters
- **Date Slicer**: `dim_date[Date]` (Relative Date slider)
- **Channel Filter**: `fact_interactions[channel]` (Multi-select)
- **Direction**: `fact_interactions[direction]` (inbound / outbound)
- **Facility**: `dim_client[facility_name]`

---

## Dashboard 3: Non-Clinical Barriers to Care

### 1. Objective
Supports social workers, case managers, community navigators, and adherence support teams in proactively tracking non-clinical social determinants (transportation, food security, work schedule conflicts, stigma, financial constraints) and monitoring task resolution efficiency.

### 2. Layout Wireframe (1920 × 1080)
```
+-----------------------------------------------------------------------------------------------+
| CareFlow AI | Non-Clinical Barriers to Care                  Last Refreshed: [Date/Time]     |
+-----------------------------------------------------------------------------------------------+
| [Date Slicer]  [Barrier Category Slicer]  [Task Status Slicer]  [Facility Slicer]             |
+---------------------+---------------------+---------------------+-----------------------------+
| KPI: Total Barriers | KPI: Top Barrier    | KPI: Resolution %   | KPI: Avg Resolution Time    |
| 312 Identified      | Transportation (38%)| 81.4% (Target > 80%)| 3.4 Days (Target < 5 Days)  |
+---------------------+---------------------+---------------------+-----------------------------+
| Visual 1: Identified Barriers by Category                       | Visual 3: Follow-up Status  |
| (Donut Chart: Transportation, Food, Schedule, Financial, Stigma)| by Facility                 |
|                                                                 | (Stacked Bar Chart)         |
+-----------------------------------------------------------------+-----------------------------+
| Visual 2: Barrier Resolution Trend Over Time                    | Visual 4: Barrier Impact on |
| (100% Stacked Column Chart: Month vs Open, In Progress, Closed) | Appointment Adherence       |
|                                                                 | (Clustered Bar Chart)       |
+-----------------------------------------------------------------+-----------------------------+
```

### 3. Visual Components & Data Bindings

#### Top Metric Cards (Row 1)
1. **Total Barriers Identified**
   - **Measure**: `[Total Barriers Identified]`
   - **Format**: Integer, `#,#`
2. **Top Barrier Category**
   - **Measure**: Dynamic Card returning highest frequency barrier category and percentage share
3. **Barrier Resolution Rate**
   - **Measure**: `[Barrier Resolution Rate]`
   - **Target Indicator**: Green if `>= 80%`, Amber if `65% - 79.9%`, Red if `< 65%`
   - **Format**: Percentage `0.0%`
4. **Average Resolution Time**
   - **Measure**: `[Average Days to Resolve Followup]`
   - **Target Indicator**: Green if `<= 4.0 Days`, Amber if `4.1 - 7.0 Days`, Red if `> 7.0 Days`
   - **Format**: Decimal `0.0 Days`

#### Chart Visualizations (Rows 2–3)
- **Visual 1: Identified Barriers by Category**
  - **Type**: Donut Chart
  - **Legend**: `fact_followups[category]` (transportation, nutrition_food, work_schedule, financial, social_stigma)
  - **Values**: `[Total Followups]`
  - **Data Labels**: Category & Percentage of Total
  - **Colors**: Transportation (`#0284C7`), Food (`#10B981`), Work (`#F59E0B`), Financial (`#8B5CF6`), Stigma (`#EC4899`)
- **Visual 2: Barrier Resolution Trend Over Time**
  - **Type**: 100% Stacked Column Chart
  - **X-Axis**: `dim_date[YearMonth]`
  - **Legend**: `fact_followups[status]` (pending, in_progress, completed, cancelled)
  - **Values**: `[Total Followups]`
- **Visual 3: Barrier Follow-up Status by Facility**
  - **Type**: Horizontal Stacked Bar Chart
  - **Y-Axis**: `dim_client[facility_name]`
  - **Legend**: `fact_followups[status]`
  - **Values**: `[Total Followups]`
- **Visual 4: Follow-up Resolution Time by Priority**
  - **Type**: Clustered Column Chart
  - **X-Axis**: `fact_followups[priority]` (low, medium, high, urgent)
  - **Values**: `[Average Days to Resolve Followup]`
  - **Data Labels**: Enabled

### 4. Interactive Slicers & Page Filters
- **Date Slicer**: `dim_date[Date]` (Follow-up created date)
- **Barrier Category**: `fact_followups[category]` (Multi-select dropdown)
- **Priority**: `fact_followups[priority]` (low, medium, high, urgent)
- **Status**: `fact_followups[status]` (pending, in_progress, completed)
- **Facility**: `dim_client[facility_name]`

---

## Dashboard 4: Escalations & Clinical Safety Oversight

### 1. Objective
Enables clinical supervisors, medical safety officers, and compliance auditors to inspect clinical and safety escalation events, evaluate response turnaround times, verify safety boundary enforcement, and maintain continuous clinical governance with zero PII exposure.

### 2. Layout Wireframe (1920 × 1080)
```
+-----------------------------------------------------------------------------------------------+
| CareFlow AI | Escalations & Clinical Safety Oversight        Last Refreshed: [Date/Time]     |
+-----------------------------------------------------------------------------------------------+
| [Date Slicer]  [Urgency Level Slicer]  [Escalation Reason Slicer]  [Facility Slicer]          |
+---------------------+---------------------+---------------------+-----------------------------+
| KPI: Total Escalated| KPI: Urgent / Emerg | KPI: Clinical Concerns| KPI: Avg Turnaround Time  |
| 64 Total Events     | 4 Critical (100% Ack| 38 Clinical Reviews | 1.8 Hours (Target < 2.0h)   |
+---------------------+---------------------+---------------------+-----------------------------+
| Visual 1: Escalation Volume by Urgency Level Trend              | Visual 2: Escalations by    |
| (Stacked Column Chart: Month vs Low, Medium, High, Critical)    | Primary Clinical Reason     |
|                                                                 | (Horizontal Bar Chart)      |
+-----------------------------------------------------------------+-----------------------------+
| Visual 3: Average Turnaround Time by Urgency Level              | Visual 4: De-Identified     |
| (Column Chart with SLA Threshold Target Line)                   | Safety Audit Log            |
|                                                                 | (Table Grid - Zero PII)     |
+-----------------------------------------------------------------+-----------------------------+
```

### 3. Visual Components & Data Bindings

#### Top Metric Cards (Row 1)
1. **Total Escalations**
   - **Measure**: `[Total Escalations]`
   - **Secondary Label**: `[Escalation Rate]` of all interactions
   - **Format**: Integer, `#,#`
2. **Urgent & Critical Escalations**
   - **Measure**: `[Urgent Escalations]`
   - **Secondary Indicator**: Count of critical emergency safety events
   - **Format**: Integer, `#,#` (Highlighted Crimson `#DC2626` if `> 0`)
3. **Clinical & Medication Inquiries**
   - **Measure**: `[Clinical Escalations]` + `[Medication Escalations]`
   - **Secondary Label**: Deterministically routed to human staff
   - **Format**: Integer, `#,#`
4. **Average Turnaround Time (Hours)**
   - **Measure**: `[Average Escalation Turnaround Hours]`
   - **Target Indicator**: Green if `<= 2.0 Hours`, Amber if `2.1 - 4.0 Hours`, Red if `> 4.0 Hours`
   - **Format**: Decimal `0.0 hrs`

#### Chart Visualizations (Rows 2–3)
- **Visual 1: Escalation Volume Trend by Urgency Level**
  - **Type**: Stacked Column Chart
  - **X-Axis**: `dim_date[YearMonth]`
  - **Legend**: `fact_escalations[urgency]` (routine, medium, high, critical)
  - **Values**: `[Total Escalations]`
  - **Colors**: Routine (`#94A3B8`), Medium (`#0284C7`), High (`#F59E0B`), Critical (`#DC2626`)
- **Visual 2: Escalations by Primary Clinical Reason**
  - **Type**: Horizontal Bar Chart (Sorted descending)
  - **Y-Axis**: `fact_escalations[reason]` (clinical_concern, medication_concern, emergency_symptoms, boundary_violation, repeated_misunderstanding)
  - **X-Axis**: `[Total Escalations]`
  - **Data Label**: Count & Percentage
- **Visual 3: Turnaround Time vs SLA Target by Urgency**
  - **Type**: Clustered Column Chart with Constant Target Line
  - **X-Axis**: `fact_escalations[urgency]` (Critical, High, Medium, Routine)
  - **Values**: `[Average Escalation Turnaround Hours]`
  - **Constant Lines**: Critical SLA = 0.5 hr (30 mins), High SLA = 2.0 hrs, Routine SLA = 24.0 hrs
- **Visual 4: De-Identified Safety Audit Log (Grid Table)**
  - **Type**: Table
  - **Columns**:
    1. `fact_escalations[escalation_key]` (e.g., `ESC-00104`)
    2. `fact_escalations[client_key]` (Surrogate hash `ANON-4a7b9c1d`)
    3. `fact_escalations[reason]` (e.g., `clinical_concern`)
    4. `fact_escalations[urgency]` (e.g., `critical`)
    5. `fact_escalations[trigger_source]` (e.g., `ai_safety_boundary`)
    6. `fact_escalations[created_date]`
    7. `fact_escalations[resolved_date]`
    8. `fact_escalations[turnaround_hours]`
    9. `fact_escalations[status]`
  - **Conditional Formatting**: Background color on `urgency` column (Critical = Soft Red, High = Soft Amber)
  - **Strict Constraint**: NO client name, phone number, or free-text narrative columns are present.

### 4. Interactive Slicers & Page Filters
- **Date Slicer**: `dim_date[Date]` (Escalation created date)
- **Urgency Filter**: `fact_escalations[urgency]` (Critical, High, Medium, Routine)
- **Escalation Reason**: `fact_escalations[reason]` (Dropdown)
- **Status Filter**: `fact_escalations[status]` (pending, reviewing, resolved, closed)
- **Facility**: `dim_client[facility_name]`

---

## Drill-Through & Cross-Filtering Behavior

1. **Drill-Through from Overview to Facility Profile**:
   - Right-clicking any facility bar in *Dashboard 1* allows drill-through to a detailed *Facility Engagement & Retention Sheet*, pre-filtering all cards and appointment visuals to that specific site.
2. **Cross-Filtering**:
   - Selecting a barrier category (e.g., `transportation`) in *Dashboard 3* immediately filters *Follow-up Status by Facility* and *Resolution Time by Priority* to show transportation-specific bottlenecks.
3. **Safety Incident Drill-Across**:
   - Clicking a critical escalation in *Dashboard 4* highlights the corresponding month and reason category, enabling rapid review of clinical safety adherence.
