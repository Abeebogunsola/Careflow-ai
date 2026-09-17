"""
CareFlow AI — Comprehensive API Test Suite (Phase 5).

Tests all API endpoints defined in docs/api.md and docs/database-design.md:
1. Health endpoint
2. Client creation
3. Client retrieval
4. Client listing
5. Client validation
6. Appointment creation
7. Appointment retrieval & query behavior
8. Interaction creation & retrieval
9. Communication preference 1:1 behavior
10. Follow-up task creation & update
11. Escalation creation & resolution
12. Approved information CRUD
13. Appropriate 404 behavior for all resources
14. Appropriate validation errors (422)
15. Database/API error handling (409 conflict, foreign key validation, audit trail)
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from app.models import Base, Role, RoleName


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean all tables before and after each test to ensure complete isolation."""
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def test_role(test_engine):
    """Seed a staff role in the test database for tests that assign users."""
    role_id = uuid.uuid4()
    with test_engine.begin() as conn:
        conn.execute(
            Base.metadata.tables["roles"].insert().values(
                id=role_id,
                name="staff",
                description="Healthcare and support staff",
            )
        )
    return role_id


# ============================================================================
# 1. Health Endpoint Tests
# ============================================================================

def test_api_health_endpoint(client):
    """Test GET /api/v1/health returns operational status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "data" in payload
    assert payload["data"]["status"] == "ok"
    assert payload["data"]["service"] == "CareFlow AI"
    assert payload["data"]["database"] in ["ok", "unavailable"]


def test_api_root_endpoint(client):
    """Test GET / returns service descriptor."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["health_check"] == "/api/v1/health"


def test_openapi_schema_loads(client):
    """Test GET /api/v1/openapi.json returns valid OpenAPI 3.x schema."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/api/v1/clients" in schema["paths"]
    assert "/api/v1/appointments" in schema["paths"]
    assert "/api/v1/interactions" in schema["paths"]
    assert "/api/v1/followups" in schema["paths"]
    assert "/api/v1/escalations" in schema["paths"]
    assert "/api/v1/approved-information" in schema["paths"]
    assert "/api/v1/audit-logs" in schema["paths"]


def test_docs_endpoints(client):
    """Test that documentation endpoints are available."""
    docs_res = client.get("/api/v1/docs")
    assert docs_res.status_code == 200

    redoc_res = client.get("/api/v1/redoc")
    assert redoc_res.status_code == 200


# ============================================================================
# 2. Client Creation Tests
# ============================================================================

def test_create_client_success(client):
    """Test POST /api/v1/clients creates a client and returns 201 with audit log."""
    payload = {
        "external_reference": "SYNTH-PAT-0001",
        "preferred_name": "Alex Taylor",
        "status": "active",
        "enrollment_status": "active",
    }
    response = client.post("/api/v1/clients", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["external_reference"] == "SYNTH-PAT-0001"
    assert data["preferred_name"] == "Alex Taylor"
    assert data["status"] == "active"
    assert data["enrollment_status"] == "active"
    assert "id" in data
    assert "created_at" in data

    # Verify audit log was recorded
    audit_res = client.get(f"/api/v1/audit-logs?entity_id={data['id']}")
    assert audit_res.status_code == 200
    logs = audit_res.json()["data"]
    assert len(logs) == 1
    assert logs[0]["action"] == "client_created"


def test_create_client_duplicate_reference_conflict_409(client):
    """Test POST /api/v1/clients returns 409 Conflict for duplicate external_reference."""
    payload = {
        "external_reference": "SYNTH-DUP-0001",
        "preferred_name": "Jordan Smith",
        "status": "active",
    }
    res1 = client.post("/api/v1/clients", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/clients", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


# ============================================================================
# 3. Client Retrieval Tests
# ============================================================================

def test_get_client_by_id(client):
    """Test GET /api/v1/clients/{id} retrieves the created client."""
    create_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-PAT-0002", "preferred_name": "Morgan Reed"},
    )
    client_id = create_res.json()["data"]["id"]

    get_res = client.get(f"/api/v1/clients/{client_id}")
    assert get_res.status_code == 200
    data = get_res.json()["data"]
    assert data["id"] == client_id
    assert data["preferred_name"] == "Morgan Reed"


def test_update_client_patch(client):
    """Test PATCH /api/v1/clients/{id} updates client fields."""
    create_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-PAT-0003", "preferred_name": "Taylor Ray"},
    )
    client_id = create_res.json()["data"]["id"]

    patch_res = client.patch(
        f"/api/v1/clients/{client_id}",
        json={"preferred_name": "Taylor Ray Updated", "status": "inactive"},
    )
    assert patch_res.status_code == 200
    data = patch_res.json()["data"]
    assert data["preferred_name"] == "Taylor Ray Updated"
    assert data["status"] == "inactive"


# ============================================================================
# 4. Client Listing & Pagination Tests
# ============================================================================

def test_list_clients_with_pagination_and_filtering(client):
    """Test GET /api/v1/clients pagination and status filtering."""
    # Seed 3 clients (2 active, 1 inactive)
    client.post("/api/v1/clients", json={"external_reference": "SYNTH-LST-01", "preferred_name": "User 1", "status": "active"})
    client.post("/api/v1/clients", json={"external_reference": "SYNTH-LST-02", "preferred_name": "User 2", "status": "active"})
    client.post("/api/v1/clients", json={"external_reference": "SYNTH-LST-03", "preferred_name": "User 3", "status": "inactive"})

    # List all
    res_all = client.get("/api/v1/clients?page=1&page_size=10")
    assert res_all.status_code == 200
    body_all = res_all.json()
    assert body_all["pagination"]["total"] == 3
    assert len(body_all["data"]) == 3

    # Filter active only
    res_active = client.get("/api/v1/clients?status=active")
    assert res_active.status_code == 200
    body_active = res_active.json()
    assert body_active["pagination"]["total"] == 2
    assert all(c["status"] == "active" for c in body_active["data"])


# ============================================================================
# 5. Client Validation Tests
# ============================================================================

def test_client_validation_missing_required_fields(client):
    """Test POST /api/v1/clients returns 422 when required fields are missing."""
    response = client.post("/api/v1/clients", json={})
    assert response.status_code == 422


def test_client_validation_invalid_enum_value(client):
    """Test POST /api/v1/clients returns 422 when status enum is invalid."""
    response = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-BAD-01", "preferred_name": "Bad Enum", "status": "unsupported_status"},
    )
    assert response.status_code == 422


# ============================================================================
# 6. Appointment Creation Tests
# ============================================================================

def test_create_appointment_success(client):
    """Test POST /api/v1/appointments creates an appointment for an existing client."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-APT-001", "preferred_name": "Appt User"},
    )
    client_id = c_res.json()["data"]["id"]

    scheduled_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    apt_payload = {
        "client_id": client_id,
        "appointment_type": "clinical_review",
        "scheduled_at": scheduled_time,
        "status": "scheduled",
        "location_label": "Main Clinic Room 3",
    }
    response = client.post("/api/v1/appointments", json=apt_payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["client_id"] == client_id
    assert data["status"] == "scheduled"
    assert data["location_label"] == "Main Clinic Room 3"


def test_create_appointment_nonexistent_client_404(client):
    """Test POST /api/v1/appointments returns 404 if client does not exist."""
    fake_id = str(uuid.uuid4())
    apt_payload = {
        "client_id": fake_id,
        "appointment_type": "refill",
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
        "status": "scheduled",
    }
    response = client.post("/api/v1/appointments", json=apt_payload)
    assert response.status_code == 404
    assert "Referenced client does not exist" in response.json()["detail"]


# ============================================================================
# 7. Appointment Retrieval & Query Tests
# ============================================================================

def test_appointment_query_and_patch(client):
    """Test querying and updating an appointment."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-APT-002", "preferred_name": "Query User"},
    )
    client_id = c_res.json()["data"]["id"]
    sched = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    apt_res = client.post(
        "/api/v1/appointments",
        json={"client_id": client_id, "scheduled_at": sched, "status": "scheduled"},
    )
    apt_id = apt_res.json()["data"]["id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/appointments/{apt_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == apt_id

    # Filter by client_id and status
    list_res = client.get(f"/api/v1/appointments?client_id={client_id}&status=scheduled")
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total"] == 1

    # Patch appointment status to completed
    patch_res = client.patch(
        f"/api/v1/appointments/{apt_id}",
        json={"status": "completed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "completed"


# ============================================================================
# 8. Interaction Tests
# ============================================================================

def test_create_and_list_interactions(client):
    """Test POST and GET /api/v1/interactions."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-INT-001", "preferred_name": "Interact User"},
    )
    client_id = c_res.json()["data"]["id"]

    int_payload = {
        "client_id": client_id,
        "channel": "whatsapp",
        "direction": "incoming",
        "interaction_type": "message",
        "intent_category": "rescheduling",
        "content": "Can I reschedule my appointment for Friday?",
    }
    create_res = client.post("/api/v1/interactions", json=int_payload)
    assert create_res.status_code == 201
    int_data = create_res.json()["data"]
    assert int_data["channel"] == "whatsapp"
    assert int_data["direction"] == "incoming"
    assert int_data["intent_category"] == "rescheduling"

    # Get single interaction
    get_res = client.get(f"/api/v1/interactions/{int_data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == int_data["id"]

    # List interactions filtered by channel
    list_res = client.get(f"/api/v1/interactions?client_id={client_id}&channel=whatsapp")
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total"] == 1


# ============================================================================
# 9. Communication Preference Tests (1:1 Relationship)
# ============================================================================

def test_communication_preference_lifecycle(client):
    """Test 1:1 communication preference creation and update for a client."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-PREF-001", "preferred_name": "Pref User"},
    )
    client_id = c_res.json()["data"]["id"]

    # Initially, preference should be 404 Not Found
    get_init = client.get(f"/api/v1/clients/{client_id}/communication-preference")
    assert get_init.status_code == 404

    # Create preference via PUT
    put_payload = {
        "preferred_channel": "sms",
        "is_enabled": True,
    }
    put_res = client.put(f"/api/v1/clients/{client_id}/communication-preference", json=put_payload)
    assert put_res.status_code == 200
    data = put_res.json()["data"]
    assert data["client_id"] == client_id
    assert data["preferred_channel"] == "sms"
    assert data["is_enabled"] is True

    # Subsequent GET returns the preference
    get_after = client.get(f"/api/v1/clients/{client_id}/communication-preference")
    assert get_after.status_code == 200
    assert get_after.json()["data"]["preferred_channel"] == "sms"
    assert get_after.json()["data"]["is_enabled"] is True

    # Subsequent PUT updates the existing record
    update_res = client.put(
        f"/api/v1/clients/{client_id}/communication-preference",
        json={"preferred_channel": "whatsapp", "is_enabled": False},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["preferred_channel"] == "whatsapp"
    assert update_res.json()["data"]["is_enabled"] is False


# ============================================================================
# 10. Follow-Up Task Tests
# ============================================================================

def test_follow_up_task_lifecycle(client):
    """Test POST, GET, and PATCH /api/v1/followups."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-FOL-001", "preferred_name": "Followup User"},
    )
    client_id = c_res.json()["data"]["id"]

    # Create task
    task_payload = {
        "client_id": client_id,
        "reason": "Missed clinic visit follow-up",
        "priority": "high",
        "status": "pending",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }
    res = client.post("/api/v1/followups", json=task_payload)
    assert res.status_code == 201
    task_id = res.json()["data"]["id"]

    # Patch task to completed; verify completed_at is automatically populated
    patch_res = client.patch(
        f"/api/v1/followups/{task_id}",
        json={"status": "completed"},
    )
    assert patch_res.status_code == 200
    completed_task = patch_res.json()["data"]
    assert completed_task["status"] == "completed"
    assert completed_task["completed_at"] is not None


# ============================================================================
# 11. Escalation Tests
# ============================================================================

def test_escalation_lifecycle(client):
    """Test POST, GET, and PATCH /api/v1/escalations."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "SYNTH-ESC-001", "preferred_name": "Escalation User"},
    )
    client_id = c_res.json()["data"]["id"]

    # Create escalation
    esc_payload = {
        "client_id": client_id,
        "category": "clinical_concern",
        "priority": "urgent",
        "reason": "Client reported unusual side effects requiring clinician review.",
        "status": "open",
    }
    res = client.post("/api/v1/escalations", json=esc_payload)
    assert res.status_code == 201
    esc_id = res.json()["data"]["id"]
    assert res.json()["data"]["category"] == "clinical_concern"
    assert res.json()["data"]["priority"] == "urgent"

    # List escalations
    list_res = client.get("/api/v1/escalations?category=clinical_concern&priority=urgent")
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total"] == 1

    # Resolve escalation
    patch_res = client.patch(
        f"/api/v1/escalations/{esc_id}",
        json={"status": "resolved"},
    )
    assert patch_res.status_code == 200
    resolved_esc = patch_res.json()["data"]
    assert resolved_esc["status"] == "resolved"
    assert resolved_esc["resolved_at"] is not None


# ============================================================================
# 12. Approved Information Tests
# ============================================================================

def test_approved_information_crud(client):
    """Test POST, GET, and PATCH /api/v1/approved-information."""
    info_payload = {
        "title": "Clinic Operating Hours & Location",
        "category": "clinic_logistics",
        "content": "The central clinic is open Monday through Friday, 8:00 AM to 5:00 PM.",
        "version": 1,
        "is_active": True,
    }
    create_res = client.post("/api/v1/approved-information", json=info_payload)
    assert create_res.status_code == 201
    info_id = create_res.json()["data"]["id"]

    # Get by ID
    get_res = client.get(f"/api/v1/approved-information/{info_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["title"] == "Clinic Operating Hours & Location"

    # List with category filter
    list_res = client.get("/api/v1/approved-information?category=clinic_logistics")
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total"] == 1

    # Update content & version
    patch_res = client.patch(
        f"/api/v1/approved-information/{info_id}",
        json={"version": 2, "content": "Updated operating hours: Monday through Saturday."},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["version"] == 2


# ============================================================================
# 13. Resource 404 Behavior Tests
# ============================================================================

@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/clients/{uuid}",
        "/api/v1/appointments/{uuid}",
        "/api/v1/interactions/{uuid}",
        "/api/v1/followups/{uuid}",
        "/api/v1/escalations/{uuid}",
        "/api/v1/approved-information/{uuid}",
        "/api/v1/audit-logs/{uuid}",
        "/api/v1/users/{uuid}",
    ],
)
def test_resource_not_found_returns_404(client, path):
    """Test that requesting non-existent UUIDs across all resources returns 404."""
    non_existent_uuid = str(uuid.uuid4())
    url = path.format(uuid=non_existent_uuid)
    response = client.get(url)
    assert response.status_code == 404


# ============================================================================
# 14. Validation Error Tests (422)
# ============================================================================

def test_invalid_uuid_parameter_returns_422(client):
    """Test that passing non-UUID path parameters returns 422 Unprocessable Entity."""
    response = client.get("/api/v1/clients/not-a-valid-uuid")
    assert response.status_code == 422


def test_invalid_query_parameter_bounds_returns_422(client):
    """Test that page < 1 or page_size > 100 returns 422."""
    res_page = client.get("/api/v1/clients?page=0")
    assert res_page.status_code == 422

    res_size = client.get("/api/v1/clients?page_size=500")
    assert res_size.status_code == 422


# ============================================================================
# 15. User Management & Audit Log Tests
# ============================================================================

def test_roles_and_user_creation_with_audit_trail(client, test_role):
    """Test roles listing, user creation with hashed passwords, and audit log generation."""
    # List roles
    roles_res = client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles = roles_res.json()["data"]
    assert any(r["name"] == "staff" for r in roles)

    # Create user
    user_payload = {
        "role_id": str(test_role),
        "email": "staff.nurse@clinic.example.test",
        "password": "SecurePassword123!",
        "first_name": "Sarah",
        "last_name": "Jenkins",
    }
    user_res = client.post("/api/v1/users", json=user_payload)
    assert user_res.status_code == 201
    user_data = user_res.json()["data"]
    assert user_data["email"] == "staff.nurse@clinic.example.test"
    # CRITICAL: Verify password_hash is not returned in API response
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # Verify duplicate email conflict returns 409
    dup_res = client.post("/api/v1/users", json=user_payload)
    assert dup_res.status_code == 409

    # Verify audit log trail captured the user creation
    audit_res = client.get(f"/api/v1/audit-logs?entity_type=user")
    assert audit_res.status_code == 200
    assert audit_res.json()["pagination"]["total"] >= 1
