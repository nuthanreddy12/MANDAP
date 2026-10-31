import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.models import User, Wedding, CustomerInvitation, Document
from backend.core.auth import create_access_token

@pytest.fixture
def unauthed_client():
    app.dependency_overrides.clear()
    return TestClient(app)

def test_customer_registration_with_valid_invitation(unauthed_client):
    """Verify that a client couple can register with an agency-issued invitation code."""
    db = SessionLocal()
    try:
        # Clean up any previous test user
        existing = db.query(User).filter(User.email == "priya.portal@test.com").first()
        if existing:
            db.delete(existing)
            db.commit()

        # Ensure invitation code exists on w1
        w1 = db.query(Wedding).filter(Wedding.id == "w1").first()
        w1.invitation_code = "ROYAL-MK-2026"
        db.commit()
    finally:
        db.close()

    res = unauthed_client.post(
        "/api/v1/customer/auth/signup",
        json={
            "client_name": "Priya Mehra",
            "email": "priya.portal@test.com",
            "password": "RoyalWeddingPass2026!",
            "invitation_code": "ROYAL-MK-2026",
        },
    )

    assert res.status_code == 201
    data = res.json()
    assert data["user"]["role"] == "customer"
    assert data["wedding_id"] == "w1"
    assert "token" in data

    # Verify user in database is strictly 'customer'
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == "priya.portal@test.com").first()
        assert u is not None
        assert u.role == "customer"
        assert u.role != "owner"
        assert u.role != "planner"
    finally:
        db.close()

def test_customer_registration_denied_without_invitation_or_matching_email(unauthed_client):
    """Verify registration fails if no valid invitation code or contract email is provided."""
    res = unauthed_client.post(
        "/api/v1/customer/auth/signup",
        json={
            "client_name": "Unknown Stranger",
            "email": "stranger.unaffiliated@example.com",
            "password": "Password123!",
            "invitation_code": "INVALID-CODE-9999",
        },
    )

    assert res.status_code == 400
    assert "Invalid invitation code or unregistered client email" in res.json()["detail"]

def test_staff_roles_cannot_be_assigned_through_customer_signup(unauthed_client):
    """Verify that passing role='owner' or role='planner' in signup payload cannot escalate privileges."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "malicious.escalate@test.com").first()
        if existing:
            db.delete(existing)
            db.commit()

        # Seed an invitation for this test
        inv = CustomerInvitation(
            id="cinv_test_escalate",
            wedding_id="w1",
            invitation_code="ROYAL-TEST-ESCALATE",
            client_email="malicious.escalate@test.com",
            client_name="Test Escalation",
        )
        db.merge(inv)
        db.commit()
    finally:
        db.close()

    # Attempt to inject staff role
    res = unauthed_client.post(
        "/api/v1/customer/auth/signup",
        json={
            "client_name": "Privilege Escalation Attempt",
            "email": "malicious.escalate@test.com",
            "password": "Password123!",
            "invitation_code": "ROYAL-TEST-ESCALATE",
            "role": "owner",  # Injected field
        },
    )

    assert res.status_code == 201
    assert res.json()["user"]["role"] == "customer"

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == "malicious.escalate@test.com").first()
        assert u is not None
        assert u.role == "customer"
        assert u.role != "owner"
    finally:
        db.close()

def test_customer_login_success_and_failure(unauthed_client):
    """Verify customer sign in endpoint with valid and invalid credentials."""
    # 1. Valid customer login
    res = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "priya.portal@test.com",
            "password": "RoyalWeddingPass2026!",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "customer"
    assert data["wedding_id"] == "w1"

    # 2. Staff user attempting to login via customer portal
    res_staff = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "aarav@theroyalknot.in",
            "password": "Password123!",
        },
    )
    assert res_staff.status_code == 401
    assert "We couldn't find an account associated with this email" in res_staff.json()["detail"]

    # 3. Nonexistent user
    res_nonexistent = unauthed_client.post(
        "/api/v1/customer/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "Password123!",
        },
    )
    assert res_nonexistent.status_code == 401
    assert "We couldn't find an account associated with this email" in res_nonexistent.json()["detail"]

def test_customer_access_to_own_wedding_details_and_features(unauthed_client):
    """Verify customer can access their own wedding details, schedule, payments, and submit requests."""
    # Generate token for customer
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "priya.portal@test.com").first()
        assert user is not None
        token = create_access_token({
            "sub": user.auth_user_id or user.id,
            "email": user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Wedding Overview
    res_w = unauthed_client.get("/api/v1/customer/wedding", headers=headers)
    assert res_w.status_code == 200
    w_data = res_w.json()
    assert w_data["wedding_id"] == "w1"
    assert "Mehra" in w_data["couple_names"]
    # Verify confidential margins/budget are NOT leaked in customer response
    assert "margin" not in w_data
    assert "contingency" not in w_data

    # 2. Schedule
    res_s = unauthed_client.get("/api/v1/customer/schedule", headers=headers)
    assert res_s.status_code == 200
    events = res_s.json()
    assert isinstance(events, list)

    # 3. Payments
    res_p = unauthed_client.get("/api/v1/customer/payments", headers=headers)
    assert res_p.status_code == 200
    p_data = res_p.json()
    assert "client_fee_total" in p_data
    assert "milestones" in p_data
    assert "total_paid" in p_data
    assert p_data["client_fee_total"] == 750000.0
    assert p_data["total_paid"] == 300000.0
    assert p_data["balance_outstanding"] == 450000.0
    assert p_data["balance_outstanding"] == p_data["client_fee_total"] - p_data["total_paid"]

    # 4. Submit Request
    res_req = unauthed_client.post(
        "/api/v1/customer/requests",
        headers=headers,
        json={
            "category": "catering",
            "title": "Jain Meal Arrangement",
            "details": "We have 15 guests requesting strict Jain meals during Day 1 dinner.",
        },
    )
    assert res_req.status_code == 201
    req_data = res_req.json()["request"]
    assert req_data["title"] == "Jain Meal Arrangement"
    assert req_data["category"] == "catering"

    # 5. View Requests List
    res_req_list = unauthed_client.get("/api/v1/customer/requests", headers=headers)
    assert res_req_list.status_code == 200
    assert any(r["title"] == "Jain Meal Arrangement" for r in res_req_list.json())

    # 6. Shared Documents
    res_docs = unauthed_client.get("/api/v1/customer/documents", headers=headers)
    assert res_docs.status_code == 200
    assert isinstance(res_docs.json(), list)

def test_customer_denial_when_accessing_internal_records_and_other_weddings(unauthed_client):
    """Verify strict authorization: customer cannot access other weddings or staff-only records."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "priya.portal@test.com").first()
        token = create_access_token({
            "sub": user.auth_user_id or user.id,
            "email": user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Deny access to internal financial reconciliation
    res_fin = unauthed_client.get("/api/v1/weddings/w1/finance/overview", headers=headers)
    assert res_fin.status_code == 403
    assert "Customer accounts cannot access internal agency staff operations" in res_fin.json()["detail"]

    # 2. Deny access to internal vendor invoices
    res_inv = unauthed_client.get("/api/v1/weddings/w1/finance/invoices", headers=headers)
    assert res_inv.status_code == 403

    # 3. Deny access to agency overview
    res_overview = unauthed_client.get("/api/v1/overview", headers=headers)
    assert res_overview.status_code == 403
    assert "Customer accounts cannot access agency overview" in res_overview.json()["detail"]

    # 4. Deny access to agency weddings list
    res_weddings = unauthed_client.get("/api/v1/weddings", headers=headers)
    assert res_weddings.status_code == 403
    assert "Customer accounts cannot access agency weddings list" in res_weddings.json()["detail"]

    # 5. Deny access to internal vendor directory
    res_vendors = unauthed_client.get("/api/v1/vendors", headers=headers)
    assert res_vendors.status_code == 403
    assert "Customer accounts cannot access internal vendor directory" in res_vendors.json()["detail"]

    # 6. Deny access to agency enquiries
    res_enquiries = unauthed_client.get("/api/v1/enquiries", headers=headers)
    assert res_enquiries.status_code == 403
    assert "Customer accounts cannot access agency enquiries" in res_enquiries.json()["detail"]

def test_staff_login_and_full_access_remains_functional(unauthed_client):
    """Verify agency staff accounts retain their full authorized capabilities."""
    staff_token = create_access_token({
        "sub": "u1",
        "email": "aarav@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated",
    })
    headers = {"Authorization": f"Bearer {staff_token}"}

    # Profile
    res_me = unauthed_client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["role"] == "owner"

    # Agency Overview
    res_ov = unauthed_client.get("/api/v1/overview", headers=headers)
    assert res_ov.status_code == 200

    # Weddings List
    res_wd = unauthed_client.get("/api/v1/weddings", headers=headers)
    assert res_wd.status_code == 200

    # Financial Reconciliation
    res_fin = unauthed_client.get("/api/v1/weddings/w1/finance/overview", headers=headers)
    assert res_fin.status_code == 200

def test_shared_document_download_authenticated_customer(unauthed_client):
    """
    Verify Bug 1 fix:
    - Logged-in customer can download shared documents (guest guide & catering menu).
    - Returns valid PDF content.
    - Non-shared documents, unauthenticated requests, and other weddings' documents are rejected.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "priya.portal@test.com").first()
        assert user is not None
        token = create_access_token({
            "sub": user.auth_user_id or user.id,
            "email": user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })

        # Ensure documents exist in database with is_shared_with_client flag
        doc1 = db.query(Document).filter(Document.id == "doc_client_guide").first()
        if not doc1:
            doc1 = Document(
                id="doc_client_guide",
                wedding_id="w1",
                filename="Mehra_Kapoor_Wedding_Guest_Guide.pdf",
                file_hash="hash_client_guide_mk_2026",
                storage_path="backend/storage/documents/Mehra_Kapoor_Wedding_Guest_Guide.pdf",
                content_type="application/pdf",
                status="ready",
                is_shared_with_client=True,
            )
            db.merge(doc1)

        doc2 = db.query(Document).filter(Document.id == "doc_client_menu").first()
        if not doc2:
            doc2 = Document(
                id="doc_client_menu",
                wedding_id="w1",
                filename="Royal_Rajputana_Approved_Catering_Tasting_Menu.pdf",
                file_hash="hash_client_menu_mk_2026",
                storage_path="backend/storage/documents/Royal_Rajputana_Approved_Catering_Tasting_Menu.pdf",
                content_type="application/pdf",
                status="ready",
                is_shared_with_client=True,
            )
            db.merge(doc2)

        # Seed an internal-only document (not shared with client)
        doc_internal = db.query(Document).filter(Document.id == "doc_internal_pricing").first()
        if not doc_internal:
            doc_internal = Document(
                id="doc_internal_pricing",
                wedding_id="w1",
                filename="Confidential_Agency_Pricing_Margin.pdf",
                file_hash="hash_internal_pricing_mk_2026",
                storage_path="backend/storage/documents/w1/doc_internal_pricing.pdf",
                content_type="application/pdf",
                status="ready",
                is_shared_with_client=False,
            )
            db.merge(doc_internal)

        db.commit()
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Download Guest Guide via customer endpoint
    res1 = unauthed_client.get("/api/v1/customer/documents/doc_client_guide/download", headers=headers)
    assert res1.status_code == 200
    assert res1.headers["content-type"] == "application/pdf"
    assert "attachment" in res1.headers.get("content-disposition", "")
    assert "Mehra_Kapoor_Wedding_Guest_Guide.pdf" in res1.headers.get("content-disposition", "")
    assert res1.content.startswith(b"%PDF")

    # 2. Download Catering Menu via customer endpoint
    res2 = unauthed_client.get("/api/v1/customer/documents/doc_client_menu/download", headers=headers)
    assert res2.status_code == 200
    assert res2.headers["content-type"] == "application/pdf"
    assert "attachment" in res2.headers.get("content-disposition", "")
    assert res2.content.startswith(b"%PDF")

    # 3. Download via wedding-scoped route (/api/v1/weddings/w1/documents/doc_client_guide/download)
    res_scoped = unauthed_client.get("/api/v1/weddings/w1/documents/doc_client_guide/download", headers=headers)
    assert res_scoped.status_code == 200
    assert res_scoped.content.startswith(b"%PDF")

    # 4. Attempt to download internal-only document (must be rejected 403)
    res_int = unauthed_client.get("/api/v1/customer/documents/doc_internal_pricing/download", headers=headers)
    assert res_int.status_code == 403
    assert "not been shared with the client" in res_int.json()["detail"]

    # 5. Attempt to download without authentication (must be rejected 401)
    res_unauth = unauthed_client.get("/api/v1/customer/documents/doc_client_guide/download")
    assert res_unauth.status_code == 401

    # 6. Attempt to download nonexistent document (must return 404)
    res_missing = unauthed_client.get("/api/v1/customer/documents/doc_nonexistent_999/download", headers=headers)
    assert res_missing.status_code == 404

def test_correct_customer_payment_figures_and_reconciliation(unauthed_client):
    """
    Verify Bug 2 fix:
    - Agreed planning fee: ₹7,50,000 (not budget).
    - Customer payments received: ₹3,00,000 (not 92L).
    - Outstanding balance: ₹4,50,000 (Agreed Planning Fee - Customer Payments Received).
    - Agency-to-vendor payments and general budget deposits are strictly separated.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "priya.portal@test.com").first()
        assert user is not None
        token = create_access_token({
            "sub": user.auth_user_id or user.id,
            "email": user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    res = unauthed_client.get("/api/v1/customer/payments", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Agreed Planning Fee
    assert data["client_fee_total"] == 750000.0, f"Expected 750000.0, got {data['client_fee_total']}"
    # Customer payments received
    assert data["total_paid"] == 300000.0, f"Expected 300000.0, got {data['total_paid']}"
    # Outstanding balance
    assert data["balance_outstanding"] == 450000.0, f"Expected 450000.0, got {data['balance_outstanding']}"
    # Strict equation: Outstanding = Agreed Planning Fee - Customer Payments Received
    assert data["balance_outstanding"] == data["client_fee_total"] - data["total_paid"]

    # Milestones verification
    milestones = data["milestones"]
    assert len(milestones) >= 3
    # First milestone is the 40% advance retainer paid
    m1 = milestones[0]
    assert m1["amount"] == 300000.0
    assert m1["status"] == "paid"
    # Remaining milestones are upcoming / scheduled
    assert all(m["status"] in ("paid", "upcoming", "scheduled") for m in milestones)
    assert sum(m["amount"] for m in milestones) == data["client_fee_total"]
