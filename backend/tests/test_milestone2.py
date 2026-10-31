import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal, Base, engine
from backend.models.models import Enquiry, Wedding, Vendor, Task, WeddingVendor

from backend.core.auth import get_current_user
from backend.models.models import User

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    owner = db.query(User).filter(User.role == "owner").first()
    db.close()
    app.dependency_overrides[get_current_user] = lambda: owner
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)

def test_milestone2_enquiry_lifecycle(client):
    # 1. Create an enquiry and retrieve it through the API
    create_payload = {
        "couple_names": "Sethi × Chawla",
        "email": "sethi.chawla@example.com",
        "phone": "+91 99887 76655",
        "rough_date": "20–22 February 2027",
        "guest_count": 350,
        "theme": "Desert Elegance",
        "budget_max": 20000000.0,
        "destination": "Jaisalmer",
        "source": "Instagram",
        "package_type": "full_service",
        "status": "new",
        "follow_up_date": "2026-11-05",
        "notes": "Interested in Suryagarh heritage fort.",
        "assigned_owner": "Nisha Sharma",
    }
    res = client.post("/api/v1/enquiries", json=create_payload)
    assert res.status_code == 201, res.text
    enquiry = res.json()
    enquiry_id = enquiry["id"]
    assert enquiry["couple_names"] == "Sethi × Chawla"
    assert enquiry["status"] == "new"

    # Retrieve enquiry by ID
    get_res = client.get(f"/api/v1/enquiries/{enquiry_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == enquiry_id
    assert retrieved["email"] == "sethi.chawla@example.com"

    # 2. Edit the enquiry and verify persistence
    patch_payload = {
        "status": "meeting_booked",
        "notes": "Initial consultation completed via video call. Client loves Suryagarh.",
        "assigned_owner": "Aarav Mehta",
    }
    patch_res = client.patch(f"/api/v1/enquiries/{enquiry_id}", json=patch_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "meeting_booked"
    assert updated["assigned_owner"] == "Aarav Mehta"

    # Verify persistence by re-fetching
    verify_res = client.get(f"/api/v1/enquiries/{enquiry_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "meeting_booked"

    # 3. Convert the enquiry into a wedding
    convert_res = client.post(f"/api/v1/enquiries/{enquiry_id}/convert")
    assert convert_res.status_code == 200, convert_res.text
    conv_data = convert_res.json()
    wedding_id = conv_data["wedding_id"]
    assert conv_data["tasks_generated"] >= 25
    assert conv_data["enquiry_status"] == "converted"

    # 4. Confirm duplicate conversion is rejected safely
    dup_res = client.post(f"/api/v1/enquiries/{enquiry_id}/convert")
    assert dup_res.status_code == 400
    assert "already converted" in dup_res.text.lower()

    # 5. Verify that the wedding is visible in the portfolio
    portfolio_res = client.get("/api/v1/weddings")
    assert portfolio_res.status_code == 200
    portfolio = portfolio_res.json()
    wedding_ids = [w["id"] for w in portfolio]
    assert wedding_id in wedding_ids

    # Verify wedding workspace details
    wedding_detail_res = client.get(f"/api/v1/weddings/{wedding_id}")
    assert wedding_detail_res.status_code == 200
    wedding_detail = wedding_detail_res.json()
    assert wedding_detail["couple_names"] == "Sethi × Chawla"
    assert wedding_detail["source_enquiry_id"] == enquiry_id
    assert wedding_detail["tasks_total"] >= 25

    # 6. Verify that 25+ tasks are generated exactly once
    tasks_res = client.get(f"/api/v1/weddings/{wedding_id}/tasks")
    assert tasks_res.status_code == 200
    tasks = tasks_res.json()
    assert len(tasks) >= 25

    # Test idempotency: calling task generator again on same wedding should not duplicate
    from backend.api.task_templates import generate_wedding_tasks
    db = SessionLocal()
    try:
        repeat_tasks = generate_wedding_tasks(db, wedding_id=wedding_id, package_type="full_service")
        assert len(repeat_tasks) == len(tasks)
    finally:
        db.close()

    # 7. Assign a vendor to the wedding
    # First get or create a vendor
    vendors_res = client.get("/api/v1/vendors")
    assert vendors_res.status_code == 200
    vendors = vendors_res.json()
    if not vendors:
        v_create = client.post("/api/v1/vendors", json={
            "name": "Royal Shahi Caterers",
            "category": "catering",
            "contact_person": "Vikram Singh",
            "phone": "+91 98290 12345",
            "email": "vikram@royalshahi.com",
            "city": "Jaipur"
        })
        vendor_id = v_create.json()["id"]
    else:
        vendor_id = vendors[0]["id"]

    assign_res = client.post(
        f"/api/v1/weddings/{wedding_id}/vendors",
        json={"vendor_id": vendor_id, "category": "catering"}
    )
    assert assign_res.status_code == 200, assign_res.text

    # 8. Verify the vendor appears in the wedding workspace
    wv_res = client.get(f"/api/v1/weddings/{wedding_id}/vendors")
    assert wv_res.status_code == 200
    assigned_list = wv_res.json()
    assert any(a["vendor_id"] == vendor_id for a in assigned_list)

    # 9. Update task status and verify persistence
    first_task = tasks[0]
    task_id = first_task["id"]
    task_patch_res = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "done", "priority": "critical"}
    )
    assert task_patch_res.status_code == 200
    updated_task = task_patch_res.json()
    assert updated_task["status"] == "done"
    assert updated_task["priority"] == "critical"

    # Re-fetch task to verify persistence
    task_get = client.get(f"/api/v1/tasks/{task_id}")
    assert task_get.status_code == 200
    assert task_get.json()["status"] == "done"

def test_vendor_directory_crud(client):
    # Test vendor creation
    v_payload = {
        "name": "Lumière Heritage Lighting",
        "category": "lighting",
        "contact_person": "Karan Singhal",
        "phone": "+91 98450 99887",
        "email": "karan@lumiere.in",
        "city": "Udaipur",
        "status": "active",
        "notes": "Architectural palace projection mapping specialists."
    }
    res = client.post("/api/v1/vendors", json=v_payload)
    assert res.status_code == 201
    vendor = res.json()
    v_id = vendor["id"]
    assert vendor["name"] == "Lumière Heritage Lighting"

    # Search / filter vendors
    search_res = client.get("/api/v1/vendors?category=lighting")
    assert search_res.status_code == 200
    found = [v for v in search_res.json() if v["id"] == v_id]
    assert len(found) == 1

    # Update vendor
    update_res = client.patch(f"/api/v1/vendors/{v_id}", json={"status": "inactive"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "inactive"
