import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.models import User, Wedding, TimelineEvent, Document, Notification
from backend.core.auth import create_access_token

client = TestClient(app)

# 1. Staff and Customer Auth Fixtures
@pytest.fixture
def owner_auth_header():
    token = create_access_token({
        "sub": "u1",
        "email": "aarav@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated",
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def planner_auth_header():
    token = create_access_token({
        "sub": "u2",
        "email": "nisha@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated",
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def coordinator_auth_header():
    token = create_access_token({
        "sub": "u3",
        "email": "kabir@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated",
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def finance_auth_header():
    token = create_access_token({
        "sub": "u4",
        "email": "rhea@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated",
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_auth_header():
    token = create_access_token({
        "sub": "cust_w1",
        "email": "priya.mehra@gmail.com",
        "role": "authenticated",
        "aud": "authenticated",
    })
    return {"Authorization": f"Bearer {token}"}

# Test 1: All 4 Staff Roles Authentication and /auth/me Profile
def test_all_four_staff_roles_login_and_me():
    staff_credentials = [
        ("aarav@theroyalknot.in", "Password123!", "owner"),
        ("nisha@theroyalknot.in", "Password123!", "planner"),
        ("kabir@theroyalknot.in", "Password123!", "coordinator"),
        ("rhea@theroyalknot.in", "Password123!", "finance_manager"),
    ]
    for email, pwd, expected_role in staff_credentials:
        login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert login_resp.status_code == 200, f"Login failed for {email}"
        data = login_resp.json()
        assert "token" in data
        assert data["user"]["role"] == expected_role

        # Verify /auth/me
        me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["email"].lower() == email.lower()

# Test 2: Protected Route Rejection without Token
def test_protected_route_rejection():
    # Attempt to access overview without token
    resp = client.get("/api/v1/overview")
    assert resp.status_code in (401, 403)

    # Attempt to access with invalid token
    bad_resp = client.get("/api/v1/overview", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert bad_resp.status_code in (401, 403)

# Test 3: Customer Login and Wedding Access
def test_customer_auth_and_isolation(owner_auth_header):
    # Customer login
    login_resp = client.post("/api/v1/customer/auth/login", json={
        "email": "priya.mehra@gmail.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    cust_data = login_resp.json()
    assert "access_token" in cust_data
    token = cust_data["access_token"]
    cust_header = {"Authorization": f"Bearer {token}"}

    # Customer wedding data accessible
    dash_resp = client.get("/api/v1/customer/wedding", headers=cust_header)
    assert dash_resp.status_code == 200

    # Customer CANNOT access internal staff overview
    agency_resp = client.get("/api/v1/overview", headers=cust_header)
    assert agency_resp.status_code == 403

# Test 4: Comprehensive Global Search across all Categories
def test_global_search_all_categories(owner_auth_header):
    # 1. Search for wedding / customer / venue
    resp = client.get("/api/v1/search?q=Mehra", headers=owner_auth_header)
    assert resp.status_code == 200
    results = resp.json()["results"]
    categories = {r["category"] for r in results}
    assert "Weddings" in categories or "Customers" in categories

    # 2. Search for vendors
    resp_v = client.get("/api/v1/search?q=Saffron", headers=owner_auth_header)
    assert resp_v.status_code == 200
    assert any(r["category"] == "Vendors" for r in resp_v.json()["results"])

    # 3. Search for tasks
    resp_t = client.get("/api/v1/search?q=tasting", headers=owner_auth_header)
    assert resp_t.status_code == 200
    assert any(r["category"] == "Tasks" for r in resp_t.json()["results"])

    # 4. Search for documents
    resp_d = client.get("/api/v1/search?q=Mooring", headers=owner_auth_header)
    assert resp_d.status_code == 200
    assert any(r["category"] == "Documents" for r in resp_d.json()["results"])

# Test 5: Role-based Permissions on Search (Coordinator cannot see Invoices)
def test_search_role_permission_isolation(coordinator_auth_header, finance_auth_header):
    # Finance manager searches for invoices
    fin_resp = client.get("/api/v1/search?q=INV", headers=finance_auth_header)
    assert fin_resp.status_code == 200
    fin_cats = [r["category"] for r in fin_resp.json()["results"]]
    assert "Invoices" in fin_cats

    # Coordinator searches for invoices - Invoices MUST NOT be returned
    coord_resp = client.get("/api/v1/search?q=INV", headers=coordinator_auth_header)
    assert coord_resp.status_code == 200
    coord_cats = [r["category"] for r in coord_resp.json()["results"]]
    assert "Invoices" not in coord_cats

# Test 6: Notifications Lifecycle
def test_notifications_lifecycle(owner_auth_header):
    resp = client.get("/api/v1/notifications", headers=owner_auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "notifications" in data
    assert "unread_count" in data
    assert len(data["notifications"]) > 0

    notif_id = data["notifications"][0]["id"]
    patch_resp = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=owner_auth_header)
    assert patch_resp.status_code == 200

    mark_all_resp = client.post("/api/v1/notifications/mark-all-read", headers=owner_auth_header)
    assert mark_all_resp.status_code == 200
    assert mark_all_resp.json()["unread_count"] == 0

# Test 7: Quotation Comparison Matrix & Recommendations
def test_quote_comparison_matrix(owner_auth_header):
    resp = client.get("/api/v1/weddings/w1/quotes/compare?category=catering", headers=owner_auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "matrix" in data
    assert "insights" in data

    # Verify entertainment category comparison
    resp_ent = client.get("/api/v1/weddings/w1/quotes/compare?category=entertainment", headers=owner_auth_header)
    assert resp_ent.status_code == 200
    ent_data = resp_ent.json()
    assert len(ent_data.get("matrix", [])) >= 2

# Test 8: Timeline Delay Calculation & Approval
def test_timeline_delay_and_approval(owner_auth_header):
    delay_resp = client.post(
        "/api/v1/weddings/w1/timeline/events/te_dj_arrival/delay",
        headers=owner_auth_header,
        json={"delay_minutes": 15, "reason": "Late arrival of DJ console"}
    )
    assert delay_resp.status_code == 200
    delay_data = delay_resp.json()
    assert "incident_id" in delay_data
    assert "ai_briefing" in delay_data
    assert "proposed_schedule" in delay_data
    incident_id = delay_data["incident_id"]

    approve_resp = client.post(
        f"/api/v1/weddings/w1/timeline/incidents/{incident_id}/approve",
        headers=owner_auth_header,
        json={"notes": "Approved by lead producer"}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"

# Test 9: Palace Documents and Real Download
def test_wedding_documents_download_and_watermark(owner_auth_header):
    docs_resp = client.get("/api/v1/weddings/w1/documents", headers=owner_auth_header)
    assert docs_resp.status_code == 200
    docs = docs_resp.json()
    assert len(docs) > 0

    # Test the synthetic permit document
    dl_resp = client.get("/api/v1/documents/doc_palace_mooring/download", headers=owner_auth_header)
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert dl_resp.content.startswith(b"%PDF")
    # Verify synthetic demo sample notice
    assert b"DEMONSTRATION SAMPLE ONLY" in dl_resp.content


# Test 10: Strict Mathematical Validation on Quotations
def test_quotation_math_validation_consistent_and_inconsistent():
    from backend.services.gemini_extractor import (
        ExtractedQuotation,
        ExtractedLineItem,
        validate_quotation_math,
    )

    # Valid quote matching exact figures
    valid_q = ExtractedQuotation(
        vendor_name="Saffron Table Gourmet Catering Services",
        quotation_number="ST-2026-NOV-114",
        subtotal=1663000.0,
        tax_amount=299340.0,
        grand_total=1962340.0,
        line_items=[
            ExtractedLineItem(original_description="Awadhi Buffet Spread", normalized_category="Catering", quantity=420, unit="plate", unit_price=3200.0, line_total=1344000.0),
            ExtractedLineItem(original_description="Live Sigri Kebab Station", normalized_category="Catering", quantity=420, unit="pax", unit_price=400.0, line_total=168000.0),
            ExtractedLineItem(original_description="Gourmet Dessert Studio", normalized_category="Catering", quantity=420, unit="pax", unit_price=300.0, line_total=126000.0),
            ExtractedLineItem(original_description="Kitchen Logistics Transport", normalized_category="Catering", quantity=1, unit="lump_sum", unit_price=25000.0, line_total=25000.0),
        ]
    )
    val_valid = validate_quotation_math(valid_q)
    assert val_valid.is_valid is True
    assert val_valid.explanation is None
    assert val_valid.discrepancy_amount == 0.0

    # Inconsistent quote (sum of items 2,435,000 vs subtotal 1,663,000)
    inconsistent_q = ExtractedQuotation(
        vendor_name="Inconsistent Vendor",
        quotation_number="INC-001",
        subtotal=1663000.0,
        tax_amount=299340.0,
        grand_total=1962340.0,
        line_items=[
            ExtractedLineItem(original_description="High Tea", normalized_category="Catering", quantity=450, unit="guest", unit_price=650.0, line_total=292500.0),
            ExtractedLineItem(original_description="Grand Feast Buffet", normalized_category="Catering", quantity=450, unit="guest", unit_price=1800.0, line_total=810000.0),
            ExtractedLineItem(original_description="Thali Lunch", normalized_category="Catering", quantity=250, unit="guest", unit_price=950.0, line_total=237500.0),
            ExtractedLineItem(original_description="Reception Banquet", normalized_category="Catering", quantity=450, unit="guest", unit_price=2100.0, line_total=945000.0),
            ExtractedLineItem(original_description="Midnight Refreshments", normalized_category="Catering", quantity=1, unit="setup", unit_price=150000.0, line_total=150000.0),
        ]
    )
    val_inc = validate_quotation_math(inconsistent_q)
    assert val_inc.is_valid is False
    assert val_inc.discrepancy_amount == 772000.0
    assert "Line items total mismatch" in val_inc.explanation
    assert "INR 2,435,000.00" in val_inc.explanation
    assert "INR 1,663,000.00" in val_inc.explanation

# Test 11: Inconsistent Extraction Blocks Ready/Complete Status in API
def test_quote_extraction_inconsistency_blocks_ready_status(owner_auth_header, monkeypatch):
    import backend.api.quotes as quotes_api
    from backend.services.gemini_extractor import ExtractedQuotation, ExtractedLineItem

    # Mock extract_quotation_with_gemini to return inconsistent figures
    def mock_extract_inconsistent(pdf_data):
        return ExtractedQuotation(
            vendor_name="Mock Inconsistent Vendor",
            quotation_number="MOCK-INC-101",
            subtotal=1663000.0,
            tax_amount=299340.0,
            grand_total=1962340.0,
            line_items=[
                ExtractedLineItem(original_description="High Tea", normalized_category="Catering", quantity=450, unit="guest", unit_price=650.0, line_total=292500.0),
                ExtractedLineItem(original_description="Grand Feast Buffet", normalized_category="Catering", quantity=450, unit="guest", unit_price=1800.0, line_total=810000.0),
                ExtractedLineItem(original_description="Thali Lunch", normalized_category="Catering", quantity=250, unit="guest", unit_price=950.0, line_total=237500.0),
                ExtractedLineItem(original_description="Reception Banquet", normalized_category="Catering", quantity=450, unit="guest", unit_price=2100.0, line_total=945000.0),
                ExtractedLineItem(original_description="Midnight Refreshments", normalized_category="Catering", quantity=1, unit="setup", unit_price=150000.0, line_total=150000.0),
            ]
        )

    monkeypatch.setattr(quotes_api, "extract_quotation_with_gemini", mock_extract_inconsistent)

    # Fetch an existing quote in w1 dynamically to avoid stale hardcoded ID
    quotes_resp = client.get("/api/v1/weddings/w1/quotes", headers=owner_auth_header)
    assert quotes_resp.status_code == 200
    quotes_list = quotes_resp.json()
    assert len(quotes_list) > 0
    target_quote_id = quotes_list[0]["id"]

    resp = client.post(f"/api/v1/weddings/w1/quotes/{target_quote_id}/extract", headers=owner_auth_header)
    assert resp.status_code == 200
    data = resp.json()
    quote_data = data["quote"]

    # Assertions: Inconsistent extraction must be marked needs_review and NOT verified
    assert quote_data["extraction_status"] == "needs_review"
    assert quote_data["status"] == "needs_review"
    assert quote_data["human_verified"] is False
    assert "Line items total mismatch" in quote_data["extraction_error"]
    # Assertions: Extracted figures are preserved without fabrication
    assert quote_data["subtotal"] == 1663000.0
    assert quote_data["total_amount"] == 1962340.0
