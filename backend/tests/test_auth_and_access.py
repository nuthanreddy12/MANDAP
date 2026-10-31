import datetime
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal, Base, engine
from backend.core.auth import create_access_token
from backend.models.models import Wedding, Task, Quote, Document, User

@pytest.fixture(scope="module")
def unauthed_client():
    # TestClient without any dependency overrides
    with TestClient(app) as client:
        yield client

def test_missing_token_returns_401(unauthed_client):
    res = unauthed_client.get("/api/v1/weddings/w1")
    assert res.status_code == 401
    assert "Authorization header missing" in res.json()["detail"] or "missing" in res.json()["detail"].lower()

def test_invalid_signature_returns_401(unauthed_client):
    fake_token = create_access_token(
        {"sub": "u1", "email": "aarav@theroyalknot.in", "role": "authenticated", "aud": "authenticated"},
        secret="completely-wrong-forged-secret-signature"
    )
    res = unauthed_client.get("/api/v1/weddings/w1", headers={"Authorization": f"Bearer {fake_token}"})
    assert res.status_code == 401
    assert "Invalid authentication token signature" in res.json()["detail"]

def test_expired_token_returns_401(unauthed_client):
    expired_token = create_access_token(
        {"sub": "u1", "email": "aarav@theroyalknot.in", "role": "authenticated", "aud": "authenticated"},
        expires_delta=datetime.timedelta(seconds=-10)
    )
    res = unauthed_client.get("/api/v1/weddings/w1", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "Authentication token expired" in res.json()["detail"]

def test_unknown_user_returns_403(unauthed_client):
    token = create_access_token({
        "sub": "u_stranger_danger",
        "email": "intruder@external-company.com",
        "role": "authenticated",
        "aud": "authenticated"
    })
    res = unauthed_client.get("/api/v1/weddings/w1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "not registered in this agency application" in res.json()["detail"]

def test_user_a_nisha_can_access_her_wedding_w1(unauthed_client, auth_headers_nisha):
    res = unauthed_client.get("/api/v1/weddings/w1", headers=auth_headers_nisha)
    assert res.status_code == 200
    assert res.json()["id"] == "w1"
    assert "Mehra" in res.json()["couple_names"]

def test_user_b_kabir_denied_access_to_user_a_wedding_w1(unauthed_client, auth_headers_kabir):
    # Kabir is assigned to w2, NOT w1 (w1 is assigned to Nisha Sharma)
    res = unauthed_client.get("/api/v1/weddings/w1", headers=auth_headers_kabir)
    assert res.status_code == 403
    assert "not authorized to view wedding w1" in res.json()["detail"]

def test_user_b_kabir_denied_modifying_w1_wedding(unauthed_client, auth_headers_kabir):
    res = unauthed_client.patch(
        "/api/v1/weddings/w1",
        json={"notes": "Hacked by unauthorized user"},
        headers=auth_headers_kabir
    )
    assert res.status_code == 403
    assert "not authorized to modify wedding w1" in res.json()["detail"]

def test_user_b_kabir_denied_viewing_w1_tasks(unauthed_client, auth_headers_kabir):
    res = unauthed_client.get("/api/v1/weddings/w1/tasks", headers=auth_headers_kabir)
    assert res.status_code == 403
    assert "not authorized to view tasks for wedding w1" in res.json()["detail"]

def test_user_b_kabir_denied_tampering_w1_task_by_id(unauthed_client, auth_headers_kabir):
    db = SessionLocal()
    w1_task = db.query(Task).filter(Task.wedding_id == "w1").first()
    db.close()
    assert w1_task is not None

    # Kabir attempts to modify w1's task directly using the task endpoint
    res = unauthed_client.patch(
        f"/api/v1/tasks/{w1_task.id}",
        json={"title": "Unauthorized task title change"},
        headers=auth_headers_kabir
    )
    assert res.status_code == 403
    assert "not authorized to modify task" in res.json()["detail"]

def test_user_b_kabir_denied_uploading_quote_to_w1(unauthed_client, auth_headers_kabir):
    fake_pdf = b"%PDF-1.4 header and mock bytes for testing"
    res = unauthed_client.post(
        "/api/v1/weddings/w1/quotes/upload",
        files={"file": ("fake.pdf", fake_pdf, "application/pdf")},
        data={"category": "catering"},
        headers=auth_headers_kabir
    )
    assert res.status_code == 403
    assert "not authorized to upload quote to wedding w1" in res.json()["detail"]

def test_user_b_kabir_denied_viewing_w1_quotes(unauthed_client, auth_headers_kabir):
    res = unauthed_client.get("/api/v1/weddings/w1/quotes", headers=auth_headers_kabir)
    assert res.status_code == 403
    assert "not authorized to view quotes for wedding w1" in res.json()["detail"]

def test_user_b_kabir_denied_downloading_w1_document(unauthed_client, auth_headers_kabir):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.wedding_id == "w1").first()
    db.close()
    if doc:
        res = unauthed_client.get(f"/api/v1/documents/{doc.id}/download", headers=auth_headers_kabir)
        assert res.status_code == 403
        assert "not authorized to download document" in res.json()["detail"]

def test_user_b_kabir_can_access_his_own_wedding_w2(unauthed_client, auth_headers_kabir):
    res = unauthed_client.get("/api/v1/weddings/w2", headers=auth_headers_kabir)
    assert res.status_code == 200
    assert res.json()["id"] == "w2"
    assert "Rathore" in res.json()["couple_names"]

def test_agency_owner_aarav_has_full_access(unauthed_client, auth_headers_owner):
    res1 = unauthed_client.get("/api/v1/weddings/w1", headers=auth_headers_owner)
    assert res1.status_code == 200
    res2 = unauthed_client.get("/api/v1/weddings/w2", headers=auth_headers_owner)
    assert res2.status_code == 200
    res_overview = unauthed_client.get("/api/v1/overview", headers=auth_headers_owner)
    assert res_overview.status_code == 200
    assert "weddings_in_motion" in res_overview.json()

def test_auth_me_returns_profile(unauthed_client, auth_headers_nisha):
    res = unauthed_client.get("/api/v1/auth/me", headers=auth_headers_nisha)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Nisha Sharma"
    assert data["email"] == "nisha@theroyalknot.in"
    assert data["role"] == "planner"
    assert data["avatar_initials"] == "NS"

def test_supabase_uuid_auth_user_id_mapping(unauthed_client):
    test_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    
    # 1. First authenticate with email + Supabase UUID (simulating Supabase login)
    token_with_email = create_access_token({
        "sub": test_uuid,
        "email": "nisha@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated"
    })
    res1 = unauthed_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_with_email}"})
    assert res1.status_code == 200
    assert res1.json()["id"] == "u2"
    assert res1.json()["auth_user_id"] == test_uuid

    # 2. Subsequent authentication using ONLY the Supabase UUID sub (no email in token)
    token_uuid_only = create_access_token({
        "sub": test_uuid,
        "role": "authenticated",
        "aud": "authenticated"
    })
    res2 = unauthed_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_uuid_only}"})
    assert res2.status_code == 200
    assert res2.json()["id"] == "u2"
    assert res2.json()["email"] == "nisha@theroyalknot.in"

    # 3. Verify wedding authorization still works via auth_user_id
    res3 = unauthed_client.get("/api/v1/weddings/w1", headers={"Authorization": f"Bearer {token_uuid_only}"})
    assert res3.status_code == 200
    assert res3.json()["id"] == "w1"

def test_test_secret_rejected_in_production_mode(unauthed_client, monkeypatch):
    import backend.core.auth as auth_mod
    # Simulate production mode (is_test_environment returns False)
    monkeypatch.setattr(auth_mod, "is_test_environment", lambda: False)
    monkeypatch.setattr(auth_mod.settings, "SUPABASE_JWT_SECRET", "")

    # Token signed with the test secret
    forged_token = create_access_token(
        {"sub": "u1", "email": "aarav@theroyalknot.in", "role": "authenticated", "aud": "authenticated"},
        secret="mandap-jwt-secret-audit-key-2026"
    )

    res = unauthed_client.get("/api/v1/weddings/w1", headers={"Authorization": f"Bearer {forged_token}"})
    assert res.status_code == 401
    assert "Invalid authentication token signature" in res.json()["detail"]

def test_unverified_email_cannot_hijack_staff_account(unauthed_client, monkeypatch):
    import backend.core.auth as auth_mod
    # Ensure unverified check is active
    monkeypatch.setattr(auth_mod, "is_test_environment", lambda: False)
    
    # Supabase allows signing secret only if configured
    monkeypatch.setattr(auth_mod.settings, "SUPABASE_JWT_SECRET", "mandap-jwt-secret-audit-key-2026")

    # Attacker token has unverified email (email_confirmed_at missing/False)
    unverified_token = create_access_token(
        {
            "sub": "attacker-uuid-9999",
            "email": "rhea@theroyalknot.in",
            "role": "authenticated",
            "aud": "authenticated",
            "email_confirmed_at": None,
            "email_verified": False,
        },
        secret="mandap-jwt-secret-audit-key-2026"
    )

    res = unauthed_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {unverified_token}"})
    assert res.status_code == 403
    assert "Email address must be confirmed" in res.json()["detail"]


