import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def owner_token():
    return create_access_token({"sub": "u1", "email": "aarav@theroyalknot.in", "role": "authenticated", "aud": "authenticated"})

@pytest.fixture
def planner_token():
    return create_access_token({"sub": "u2", "email": "nisha@theroyalknot.in", "role": "authenticated", "aud": "authenticated"})

@pytest.fixture
def coordinator_token():
    return create_access_token({"sub": "u3", "email": "kabir@theroyalknot.in", "role": "authenticated", "aud": "authenticated"})

@pytest.fixture
def finance_token():
    return create_access_token({"sub": "u4", "email": "rhea@theroyalknot.in", "role": "authenticated", "aud": "authenticated"})

@pytest.fixture
def customer_token():
    return create_access_token({"sub": "u_cust_priya", "email": "priya.mehra@gmail.com", "role": "authenticated", "aud": "authenticated"})


def test_quote_comparison_with_ai_insights(owner_token):
    headers = {"Authorization": f"Bearer {owner_token}"}
    res = client.get("/api/v1/weddings/w1/quotes/compare?category=decoration", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "matrix" in data
    assert "insights" in data
    assert len(data["matrix"]) >= 3
    assert data["insights"].get("recommended_vendor") is not None


def test_vendor_selection_and_reassignment(owner_token):
    headers = {"Authorization": f"Bearer {owner_token}"}
    
    q_res = client.get("/api/v1/weddings/w1/quotes?category=decoration", headers=headers)
    assert q_res.status_code == 200
    quotes = q_res.json()
    assert len(quotes) >= 2
    
    first_quote = quotes[0]
    second_quote = quotes[1]

    # Select first quote via weddings endpoint
    sel_res1 = client.post(
        "/api/v1/weddings/w1/quotes/select",
        headers=headers,
        json={"quote_id": first_quote["id"], "category": "decoration", "notes": "Initial selection"},
    )
    assert sel_res1.status_code == 200
    assert sel_res1.json()["quote_id"] == first_quote["id"]

    # Reassign to second quote with reassign=True
    sel_res2 = client.post(
        "/api/v1/weddings/w1/quotes/select",
        headers=headers,
        json={"quote_id": second_quote["id"], "category": "decoration", "reassign": True, "notes": "Reassigned selection"},
    )
    assert sel_res2.status_code == 200
    assert sel_res2.json()["quote_id"] == second_quote["id"]


def test_duplicate_selection_locked_without_reassign_flag(owner_token):
    headers = {"Authorization": f"Bearer {owner_token}"}
    
    q_res = client.get("/api/v1/weddings/w1/quotes?category=catering", headers=headers)
    assert q_res.status_code == 200
    quotes = q_res.json()
    assert len(quotes) >= 2

    other_quote = [q for q in quotes if q["status"] != "selected"][0]
    dup_res = client.post(
        f"/api/v1/quotes/{other_quote['id']}/select",
        headers=headers,
        json={"notes": "Duplicate selection attempt without reassign flag", "reassign": False},
    )
    assert dup_res.status_code == 400
    assert "already locked" in dup_res.text.lower() or "prevented" in dup_res.text.lower()


def test_top_level_finance_invoices_and_overview(finance_token):
    headers = {"Authorization": f"Bearer {finance_token}"}
    
    # Test top-level /api/v1/finance/invoices
    inv_res = client.get("/api/v1/finance/invoices?wedding_id=w1", headers=headers)
    assert inv_res.status_code == 200
    invoices = inv_res.json()
    assert len(invoices) >= 1

    # Test top-level /api/v1/finance/overview
    ov_res = client.get("/api/v1/finance/overview?wedding_id=w1", headers=headers)
    assert ov_res.status_code == 200
    overview = ov_res.json()
    assert "agreed_value" in overview
    assert "invoice_total" in overview
    assert "paid_amount" in overview


def test_three_way_reconciliation_math_and_discrepancy(finance_token):
    headers = {"Authorization": f"Bearer {finance_token}"}
    
    inv_res = client.get("/api/v1/finance/invoices?wedding_id=w1", headers=headers)
    assert inv_res.status_code == 200
    invoices = inv_res.json()
    assert len(invoices) >= 1
    
    target_inv = invoices[0]
    
    # Reconcile invoice
    rec_res = client.post(f"/api/v1/finance/invoices/{target_inv['id']}/reconcile", headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "status" in rec_data
    assert "ai_explanation" in rec_data
    assert rec_data.get("deterministic_math_verified") is True
    assert rec_data.get("ai_provider") == "Google Gemini"


def test_reconciliation_role_authorization(owner_token, finance_token, planner_token, coordinator_token, customer_token):
    headers_owner = {"Authorization": f"Bearer {owner_token}"}
    inv_res = client.get("/api/v1/finance/invoices?wedding_id=w1", headers=headers_owner)
    assert inv_res.status_code == 200
    invoices = inv_res.json()
    assert len(invoices) >= 1
    invoice_id = invoices[0]["id"]

    # 1. Coordinator (u3) should be REJECTED with 403 Forbidden
    coord_headers = {"Authorization": f"Bearer {coordinator_token}"}
    coord_res = client.post(
        f"/api/v1/finance/invoices/{invoice_id}/reconciliation/decide",
        headers=coord_headers,
        json={"decision": "approve", "review_notes": "Coordinator attempting override"},
    )
    assert coord_res.status_code == 403
    assert "not authorized" in coord_res.text.lower()

    # 2. Customer (u_cust_priya) should be REJECTED with 403 Forbidden
    cust_headers = {"Authorization": f"Bearer {customer_token}"}
    cust_res = client.post(
        f"/api/v1/finance/invoices/{invoice_id}/reconciliation/decide",
        headers=cust_headers,
        json={"decision": "approve", "review_notes": "Customer attempting override"},
    )
    assert cust_res.status_code == 403

    # 3. Planner (u2) should be ALLOWED (200 OK)
    planner_headers = {"Authorization": f"Bearer {planner_token}"}
    planner_res = client.post(
        f"/api/v1/finance/invoices/{invoice_id}/reconciliation/decide",
        headers=planner_headers,
        json={"decision": "approve", "review_notes": "Planner approved after client agreement"},
    )
    assert planner_res.status_code == 200

    # 4. Finance Manager (u4) should be ALLOWED (200 OK)
    fin_headers = {"Authorization": f"Bearer {finance_token}"}
    fin_res = client.post(
        f"/api/v1/finance/invoices/{invoice_id}/reconciliation/decide",
        headers=fin_headers,
        json={"decision": "reject", "review_notes": "Finance manager disputed unapproved line item"},
    )
    assert fin_res.status_code == 200

    # 5. Owner (u1) should be ALLOWED (200 OK)
    owner_res = client.post(
        f"/api/v1/finance/invoices/{invoice_id}/reconciliation/decide",
        headers=headers_owner,
        json={"decision": "approve", "review_notes": "Owner final authorized override"},
    )
    assert owner_res.status_code == 200
