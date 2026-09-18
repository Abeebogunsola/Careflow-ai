# CareFlow AI — Program Analytics & Power BI Layer (Phase 9)

Welcome to the **CareFlow AI Program Analytics & Reporting Layer**. This directory contains the Star Schema database views, automated ETL data export pipeline, synthetic demonstration data generators, production DAX measures, and Power BI dashboard specifications for CareFlow AI.

---

## 1. Architecture Overview & Star Schema Design

The analytics layer transforms transactional healthcare operations into a de-identified dimensional **Star Schema** optimized for high-performance analytical queries and Power BI reporting.

```
                         +-------------------+
                         |     dim_date      |
                         +-------------------+
                                   | 1
                                   |
         +-------------------------+-------------------------+
         | *                       | *                       | *
+--------------------+   +--------------------+   +--------------------+
| fact_appointments  |   | fact_interactions  |   |  fact_followups    |
+--------------------+   +--------------------+   +--------------------+
         | *                       | *                       | *
         |                         |                         |
         +-------------------------+-------------------------+
                                   | *
                                   |
                                   | 1
                         +-------------------+
                         |    dim_client     |
                         +-------------------+
                                   | 1
                                   |
                                   | *
                         +-------------------+
                         |  fact_escalations |
                         +-------------------+
```

### Table Definitions
1. **`dim_client`**: Client demographic and program status dimension.
   - Surrogate Key: `client_key` (Deterministic SHA-256 hash: `ANON-xxxxxxxx`)
   - Attributes: `facility_name`, `preferred_language`, `status`, `registration_date_key`
2. **`dim_date`**: Master calendar dimension spanning past and future reporting years.
   - Key: `date_key` (Integer: `YYYYMMDD`)
   - Attributes: `Date`, `Year`, `Quarter`, `Month`, `MonthName`, `WeekOfYear`, `DayOfWeek`, `DayOfWeekName`, `IsWeekend`
3. **`fact_appointments`**: Granular appointment schedule and completion records.
   - Keys: `appointment_key`, `client_key`, `appointment_date_key`
   - Attributes & Metrics: `appointment_type`, `status`, `is_attended`, `is_missed`, `is_cancelled`
4. **`fact_interactions`**: Inbound and outbound client communication traffic.
   - Keys: `interaction_key`, `client_key`, `interaction_date_key`
   - Attributes & Metrics: `channel`, `direction`, `intent`, `is_inbound`, `is_outbound`, `is_contained`
5. **`fact_followups`**: Non-clinical barrier identification and task workflow.
   - Keys: `followup_key`, `client_key`, `created_date_key`, `resolved_date_key`
   - Attributes & Metrics: `category`, `priority`, `status`, `is_resolved`, `days_to_resolution`
6. **`fact_escalations`**: Clinical and safety escalation audit trail.
   - Keys: `escalation_key`, `client_key`, `created_date_key`, `resolved_date_key`
   - Attributes & Metrics: `reason`, `urgency`, `trigger_source`, `status`, `is_resolved`, `turnaround_hours`

---

## 2. Zero-PII & Privacy Preservation Standard

In strict adherence to **HIPAA**, public health data ethics, and `docs/safety-privacy.md`:
- **No Direct Identifiers**: Client names, phone numbers, email addresses, and external identifiers (e.g., national IDs) are completely excluded.
- **Irreversible Surrogate Keys**: Clients are identified exclusively via non-reversible SHA-256 hashes (`ANON-xxxxxxxx`).
- **No Free-Text Clinical Notes**: Subjective clinical remarks and raw conversational transcripts are omitted. Only structured analytical categorizations (`category`, `intent`, `urgency`, `reason`) are ingested.

---

## 3. Directory Structure

```
analytics/
├── README.md                                # This architecture and operations guide
├── export_data.py                           # Python ETL pipeline exporting de-identified CSVs
├── generate_synthetic_analytics_data.py      # Generates 100+ synthetic clients & 1,000+ records
├── data/                                    # Target directory for exported de-identified CSVs
│   ├── dim_client.csv
│   ├── dim_date.csv
│   ├── fact_appointments.csv
│   ├── fact_interactions.csv
│   ├── fact_followups.csv
│   └── fact_escalations.csv
├── sql/
│   └── star_schema_views.sql                # SQL views defining dimensional model on database
└── powerbi/
    ├── dax_measures.dax                     # 25+ Production DAX formulas across all 5 domains
    └── dashboard_specifications.md          # Wireframes and chart specs for the 4 core dashboards
```

---

## 4. Quickstart: Generating Data & Running ETL Export

### Step 1: Ensure Virtual Environment is Activated
From the project root:
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### Step 2: (Optional) Seed Synthetic Demonstration Data
If you want to populate the CareFlow database with rich, realistic synthetic data for analytics demonstrations (100 synthetic clients across multiple facilities and languages, with 90+ days of appointment outcomes, multi-channel interactions, barrier tasks, and clinical escalations):
```bash
python analytics/generate_synthetic_analytics_data.py
```

### Step 3: Run ETL Data Extraction
Extract de-identified analytical tables from the database into the `analytics/data/` folder:
```bash
python analytics/export_data.py
```
This produces 6 de-identified CSV files verified for zero PII:
- `dim_client.csv`
- `dim_date.csv`
- `fact_appointments.csv`
- `fact_interactions.csv`
- `fact_followups.csv`
- `fact_escalations.csv`

---

## 5. Setting Up Power BI Desktop

### 1. Ingesting Data
1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV** (or connect directly to PostgreSQL views if connecting to live database).
3. Ingest all 6 CSV files from `analytics/data/`.
4. Click **Transform Data** in Power Query to confirm column data types:
   - Date keys (`date_key`, `appointment_date_key`, etc.) -> `Whole Number`
   - Dates (`Date`, `created_date`, etc.) -> `Date` or `Date/Time`
   - Numeric metrics (`turnaround_hours`, `days_to_resolution`) -> `Decimal Number`
   - Flags (`is_attended`, `is_missed`, etc.) -> `Whole Number` or `True/False`

### 2. Modeling Data (Star Schema Relationships)
Navigate to the **Model View** and configure the following 1-to-Many (`1:*`) relationships with **Single** cross-filter direction:
- `dim_client[client_key]` `1` ---> `*` `fact_appointments[client_key]`
- `dim_client[client_key]` `1` ---> `*` `fact_interactions[client_key]`
- `dim_client[client_key]` `1` ---> `*` `fact_followups[client_key]`
- `dim_client[client_key]` `1` ---> `*` `fact_escalations[client_key]`
- `dim_date[date_key]` `1` ---> `*` `fact_appointments[appointment_date_key]`
- `dim_date[date_key]` `1` ---> `*` `fact_interactions[interaction_date_key]`
- `dim_date[date_key]` `1` ---> `*` `fact_followups[created_date_key]`
- `dim_date[date_key]` `1` ---> `*` `fact_escalations[created_date_key]`

### 3. Adding DAX Measures
1. Create a dedicated measure table named `_Measures`.
2. Open `analytics/powerbi/dax_measures.dax`.
3. Copy and paste the DAX measures into your report.
4. Key measures include:
   - `[Total Clients]`, `[Active Clients]`, `[Retention Rate]`
   - `[Total Appointments]`, `[Appointment Adherence Rate]`, `[Attended Appointments]`
   - `[Total Interactions]`, `[Client Response Rate]`, `[Inbound Share %]`
   - `[Total Barriers Identified]`, `[Barrier Resolution Rate]`, `[Average Days to Resolve Followup]`
   - `[Total Escalations]`, `[Urgent Escalations]`, `[Average Escalation Turnaround Hours]`

### 4. Building the 4 Core Dashboards
Follow the comprehensive layout wireframes and visual configurations detailed in:
`analytics/powerbi/dashboard_specifications.md`:
1. **Page 1: Program Overview & Care Retention**
2. **Page 2: Client Engagement & Communication**
3. **Page 3: Non-Clinical Barriers to Care**
4. **Page 4: Escalations & Clinical Safety Oversight**

---

## 6. Backend API Analytics Endpoints

The analytics layer is also exposed via secure, authenticated REST APIs for external dashboard integrations and programmatic consumption:
- `GET /api/v1/analytics/overview` — High-level KPI metrics summary.
- `GET /api/v1/analytics/appointments` — Filterable appointment outcomes and adherence rates by facility, date range, and appointment type.
- `GET /api/v1/analytics/engagement` — Channel volume breakdown, message intent distribution, barrier resolution efficiency, and escalation turnaround SLA metrics.

Refer to `docs/api.md` for complete schema definitions and authentication headers.
