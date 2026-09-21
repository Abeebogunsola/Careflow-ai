# CareFlow AI — Production Deployment Guide & Operational Runbook

This guide details the complete deployment process and operational procedures for running **CareFlow AI** in production using the containerized multi-service Docker Compose stack.

---

## 1. System Requirements & Architecture

### Recommended Hardware:
- **CPU**: 2+ vCPUs (x86_64 or ARM64)
- **RAM**: 4 GB minimum (8 GB recommended for concurrent n8n workflows and Uvicorn workers)
- **Disk**: 20 GB SSD storage
- **Operating System**: Ubuntu 22.04 / 24.04 LTS, Debian 12, or any modern Linux distribution with Docker Engine & Docker Compose v2.

### Port Requirements:
- **Port 80 (HTTP)**: Ingress routing and Let's Encrypt ACME verification
- **Port 443 (HTTPS)**: Encrypted production traffic
- *Note*: Internal service ports (`5432` PostgreSQL, `8000` FastAPI, `5678` n8n) are bound strictly to the private Docker bridge network and are never exposed publicly.

---

## 2. Pre-Deployment Setup

### Step 1: Install Docker & Docker Compose
Ensure Docker Engine and Docker Compose (v2.20+) are installed:
```bash
docker --version
docker compose version
```

### Step 2: Clone the Codebase
```bash
git clone https://github.com/Abeebogunsola/Careflow-ai.git
cd Careflow-ai
```

### Step 3: Configure Production Environment Variables
Copy the production environment template:
```bash
cp .env.production.example .env
chmod 600 .env
```

Generate secure cryptographic keys and insert them into `.env`:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate N8N_ENCRYPTION_KEY
openssl rand -hex 32

# Generate strong database password
openssl rand -base64 24
```

Edit `.env` and set:
- `SECRET_KEY`: Insert generated hex string.
- `N8N_ENCRYPTION_KEY`: Insert generated hex string.
- `POSTGRES_PASSWORD`: Insert generated database password.
- `DOMAIN_NAME`: Set to your production domain (e.g. `careflow.example.com`).
- `CORS_ORIGINS`: Set to your allowed origins (e.g. `https://careflow.example.com`).
- `LLM_PROVIDER`: Keep `mock` for zero-cost offline pilot, or set to `groq` / `openai` with your API key.

---

## 3. Launching Production Services

### Step 1: Build and Launch Containers
Execute the production Compose stack in detached mode:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Step 2: Verify Container Health
Check that all 5 services are active and healthy:
```bash
docker compose -f docker-compose.prod.yml ps
```
Expected output:
```
NAME                    IMAGE              STATUS                    PORTS
careflow-prod-postgres  postgres:15-alpine Up (healthy)              5432/tcp
careflow-prod-backend   backend-image      Up (healthy)              8000/tcp
careflow-prod-frontend  frontend-image     Up                        80/tcp
careflow-prod-n8n       n8nio/n8n:latest   Up                        5678/tcp
careflow-prod-gateway   nginx:alpine       Up                        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### Step 3: Initialize Database Schema and Analytical Views
The backend container automatically applies Alembic migrations on startup (`alembic upgrade head`).
To apply the PostgreSQL Star Schema views for Power BI analytics, pipe the SQL script directly from the project root:
```bash
docker compose -f docker-compose.prod.yml exec -T postgres psql -U careflow_admin -d careflow_prod < analytics/sql/star_schema_views_postgres.sql
```
Or execute the automated database initializer from the project root:
```bash
python deploy/scripts/init_prod_db.py
```

---

## 4. SSL / HTTPS Certificate Setup

### Option A: Certbot Automated Let's Encrypt (Recommended)
1. Point your domain DNS records (`careflow.example.com`) to your server IP.
2. Request certificates via Certbot:
```bash
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  -d careflow.example.com \
  --email admin@example.com --agree-tos --no-eff-email" certbot
```
3. Enable the SSL server block:
```bash
cp deploy/nginx/conf.d/careflow-ssl.conf.template deploy/nginx/conf.d/careflow-ssl.conf
sed -i 's/careflow.example.com/your-actual-domain.com/g' deploy/nginx/conf.d/careflow-ssl.conf
docker compose -f docker-compose.prod.yml exec gateway nginx -s reload
```

### Option B: Cloudflare Proxy SSL
If using Cloudflare:
1. Proxy traffic through Cloudflare (Orange Cloud enabled).
2. Set SSL/TLS encryption mode to **Full (Strict)** or **Full**.
3. Use Origin CA certificates or keep standard HTTP ingress behind Cloudflare's edge SSL.

---

## 5. n8n Automation Engine Setup

The 8 core automation workflows are mounted into the n8n container under `/workflows/`:
1. `01_appointment_reminder.json`
2. `02_missed_appointment_followup.json`
3. `03_inbound_message_webhook.json`
4. `04_scheduled_daily_outreach.json`
5. `05_escalation_alert_webhook.json`
6. `06_weekly_retention_kpi_sync.json`
7. `07_mock_sms_gateway_webhook.json`
8. `08_error_handler_workflow.json`

To import them automatically into the n8n instance:
```bash
docker compose -f docker-compose.prod.yml exec -u node n8n n8n import:workflow --input=/workflows/
```
Access the n8n administrative console at:
`https://careflow.example.com/n8n/` to activate the workflows and configure webhooks.

---

## 6. Power BI Integration

Connect Power BI Desktop or Service directly to PostgreSQL for real-time reporting:
1. Open Power BI Desktop -> **Get Data** -> **PostgreSQL Database**.
2. **Server**: `db.careflow.example.com:5432` (or via SSH tunnel / private VPC).
3. **Database**: `careflow_prod`.
4. **Data Connectivity Mode**: **Import** or **DirectQuery**.
5. Select only the 6 Star Schema Views:
   - `view_dim_date`
   - `view_dim_client` (Zero PII, hash codes only)
   - `view_fact_appointments`
   - `view_fact_interactions`
   - `view_fact_followups`
   - `view_fact_escalations`

---

## 7. Production Smoke Testing

Validate deployment health and deterministic clinical guardrails immediately after launching:
```bash
python deploy/smoke_test.py --url https://careflow.example.com
```

The test script automatically runs 5 pre-flight checks:
1. Frontend SPA asset availability (HTTP 200, HTML bundle delivered)
2. Backend & PostgreSQL connection health (`GET /api/v1/health`)
3. Clients directory query (`GET /api/v1/clients`)
4. AI intent triage non-clinical message (`POST /api/v1/messages/triage`)
5. Deterministic emergency escalation safety guardrail (`POST /api/v1/messages/triage`)

All 5 checks must display **PASS** before opening the application to staff.

---

## 8. Operational Runbook & Maintenance

### Viewing Service Logs:
```bash
# View aggregated real-time logs:
docker compose -f docker-compose.prod.yml logs -f --tail=100

# View backend logs only:
docker compose -f docker-compose.prod.yml logs -f backend

# View Nginx access & security logs:
docker compose -f docker-compose.prod.yml logs -f gateway
```

### Database Backups & Point-in-Time Recovery:
Automated backup command (add to daily cron `crontab -e`):
```bash
# Daily automated PostgreSQL snapshot
0 2 * * * docker compose -f /path/to/Careflow-ai/docker-compose.prod.yml exec -T postgres \
  pg_dump -U careflow_admin careflow_prod | gzip > /backups/careflow_db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

Restore from backup:
```bash
gunzip -c /backups/careflow_db_YYYYMMDD_HHMMSS.sql.gz | docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U careflow_admin -d careflow_prod
```

### Rolling Upgrades & Rollbacks:
To deploy a new version:
```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
python deploy/smoke_test.py --url https://careflow.example.com
```

If issues are detected, instantly roll back:
```bash
# Revert to previous git commit or image tag:
git checkout <previous_commit_hash>
docker compose -f docker-compose.prod.yml up -d --build

# If database rollback is needed:
docker compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```
