import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.models import CustomerInvitation

@pytest.fixture
def unauthed_client():
    app.dependency_overrides.clear()
    return TestClient(app)

def test_1_customer_signup_flow(unauthed_client):
    """1. Customer signup generates token and links wedding."""
    db = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:6]
    test_code = f"FLOW-{unique_suffix.upper()}"
    test_email = f"flow.{unique_suffix}@test.com"

    try:
        inv = CustomerInvitation(
            id=f"cinv_{unique_suffix}",
            wedding_id="w1",
            invitation_code=test_code,
            client_email=test_email,
            client_name="Flow Couple",
            is_claimed=False,
        )
        db.add(inv)
        db.commit()
    finally:
        db.close()

    res = unauthed_client.post(
        "/api/v1/customer/auth/signup",
        json={
            "client_name": "Flow Couple",
            "email": test_email,
            "password": "PrivateWeddingPassword2026!",
            "invitation_code": test_code,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["token"] is not None
    assert len(data["token"]) > 20
    assert data["user"]["role"] == "customer"
    assert data["wedding_id"] == "w1"

def test_2_customer_login_with_valid_credentials(unauthed_client):
    """2. Customer login returns valid JWT token and correct payload."""
    db = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:6]
    test_code = f"LOGIN-{unique_suffix.upper()}"
    test_email = f"login.{unique_suffix}@test.com"

    try:
        inv = CustomerInvitation(
            id=f"cinv_{unique_suffix}",
            wedding_id="w1",
            invitation_code=test_code,
            client_email=test_email,
            client_name="Login Couple",
            is_claimed=False,
        )
        db.add(inv)
        db.commit()
    finally:
        db.close()

    # Signup first
    unauthed_client.post(
        "/api/v1/customer/auth/signup",
        json={
            "client_name": "Login Couple",
            "email": test_email,
            "password": "PrivateWeddingPassword2026!",
            "invitation_code": test_code,
        },
    )

    # Login
    res = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": test_email,
            "password": "PrivateWeddingPassword2026!",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["token"] is not None
    assert len(data["token"]) > 20
    assert data["user"]["email"] == test_email
    assert data["user"]["role"] == "customer"
    assert data["wedding_id"] == "w1"

def test_3_customer_login_with_invalid_credentials(unauthed_client):
    """3. Customer login with invalid or empty credentials produces clear error."""
    # Blank password
    res_blank = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={"email": "priya.portal@test.com", "password": ""},
    )
    assert res_blank.status_code == 401

    # Unregistered email
    res_unreg = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={"email": "nonexistent.couple@example.com", "password": "Password123!"},
    )
    assert res_unreg.status_code == 401
    assert "couldn't find" in res_unreg.json()["detail"].lower()

    # Staff email trying to log into customer portal
    res_staff = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={"email": "aarav@theroyalknot.in", "password": "Password123!"},
    )
    assert res_staff.status_code == 401

def test_4_token_persistence_and_restoration(unauthed_client):
    """4. Customer token can be restored and validated via /api/v1/auth/me."""
    login_res = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "priya.portal@test.com",
            "password": "RoyalWeddingPass2026!",
        },
    )
    token = login_res.json()["token"]

    # Verify session profile restore
    me_res = unauthed_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["email"] == "priya.portal@test.com"
    assert profile["role"] == "customer"

def test_5_customer_dashboard_wedding_access(unauthed_client):
    """5. Customer can access their wedding details, timeline and payments."""
    login_res = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "priya.portal@test.com",
            "password": "RoyalWeddingPass2026!",
        },
    )
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Wedding sanctuary details
    w_res = unauthed_client.get("/api/v1/customer/wedding", headers=headers)
    assert w_res.status_code == 200
    assert w_res.json()["wedding_id"] == "w1"

    # Schedule
    s_res = unauthed_client.get("/api/v1/customer/schedule", headers=headers)
    assert s_res.status_code == 200
    assert isinstance(s_res.json(), list)

    # Payments
    p_res = unauthed_client.get("/api/v1/customer/payments", headers=headers)
    assert p_res.status_code == 200
    p_data = p_res.json()
    assert "milestones" in p_data
    assert isinstance(p_data["milestones"], list)

def test_6_customer_access_restrictions(unauthed_client):
    """6. Customer cannot access agency overview or staff wedding endpoints."""
    login_res = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "priya.portal@test.com",
            "password": "RoyalWeddingPass2026!",
        },
    )
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Agency overview is forbidden for customers
    overview_res = unauthed_client.get("/api/v1/overview", headers=headers)
    assert overview_res.status_code == 403
    assert "Customer accounts cannot access agency overview" in overview_res.json()["detail"]

    # Internal staff wedding endpoint is forbidden for customers
    staff_w_res = unauthed_client.get("/api/v1/weddings/w1", headers=headers)
    assert staff_w_res.status_code == 403
    assert "Customer accounts cannot access internal agency staff operations" in staff_w_res.json()["detail"]

def test_7_staff_login_all_four_roles(unauthed_client):
    """7. All 4 agency staff roles can log in and receive valid authenticated sessions."""
    staff_creds = [
        ("aarav@theroyalknot.in", "Password123!", "owner"),
        ("nisha@theroyalknot.in", "Password123!", "planner"),
        ("kabir@theroyalknot.in", "Password123!", "coordinator"),
        ("rhea@theroyalknot.in", "Password123!", "finance_manager"),
    ]

    for email, password, expected_role in staff_creds:
        res = unauthed_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert res.status_code == 200, f"Failed login for {email}: {res.text}"
        data = res.json()
        assert data["token"] is not None
        assert len(data["token"]) > 20
        assert data["user"]["email"] == email
        assert data["user"]["role"] == expected_role

        # Verify token against /api/v1/auth/me
        me_res = unauthed_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["role"] == expected_role

def test_8_staff_authorization_scoping(unauthed_client):
    """8. Agency Owner has agency overview access; Planner has assigned wedding access."""
    # Owner login
    res_owner = unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "aarav@theroyalknot.in", "password": "Password123!"},
    )
    owner_token = res_owner.json()["token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    overview_res = unauthed_client.get("/api/v1/overview", headers=owner_headers)
    assert overview_res.status_code == 200
    assert "active_weddings_count" in overview_res.json()

    # Planner login (Nisha assigned to w1)
    res_nisha = unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "nisha@theroyalknot.in", "password": "Password123!"},
    )
    nisha_token = res_nisha.json()["token"]
    nisha_headers = {"Authorization": f"Bearer {nisha_token}"}

    w1_res = unauthed_client.get("/api/v1/weddings/w1", headers=nisha_headers)
    assert w1_res.status_code == 200
    assert w1_res.json()["id"] == "w1"

    # Nisha denied access to w2 (assigned to Kabir Verma)
    w2_res = unauthed_client.get("/api/v1/weddings/w2", headers=nisha_headers)
    assert w2_res.status_code == 403
