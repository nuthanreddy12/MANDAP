from fastapi.testclient import TestClient
from backend.main import app

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data

def test_agency_overview(auth_headers_owner):
    with TestClient(app) as client:
        response = client.get("/api/v1/overview", headers=auth_headers_owner)
        assert response.status_code == 200
        data = response.json()
        assert "active_weddings_count" in data
        assert data["active_weddings_count"] >= 3
        assert "weddings_in_motion" in data
        assert len(data["weddings_in_motion"]) >= 3

def test_wedding_detail(auth_headers_owner):
    with TestClient(app) as client:
        response = client.get("/api/v1/weddings/w1", headers=auth_headers_owner)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "w1"
        assert "Mehra" in data["couple_names"]
        assert data["client_budget"] == 18500000.0
