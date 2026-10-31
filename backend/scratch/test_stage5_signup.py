import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Point to stage 5 database
STAGE5_DB = "sqlite:///./backend/storage/backups/mandap_demo_stage5.db"
os.environ["DATABASE_URL"] = STAGE5_DB
os.environ["MANDAP_TESTING"] = "1"

# Override database engine
from backend.core.database import get_db
from backend.main import app
from backend.models.models import Base, Wedding, CustomerInvitation

engine = create_engine(STAGE5_DB, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

print("\n--- Testing Signup with ROYAL-MK-2026 on stage 5 database ---")
signup_payload = {
    "client_name": "Priya Mehra",
    "email": "priya.mehra@gmail.com",
    "password": "Password123!",
    "invitation_code": "ROYAL-MK-2026"
}

res = client.post("/api/v1/customer/auth/signup", json=signup_payload)
print(f"Signup response status: {res.status_code}")
print(f"Signup response json: {res.json()}")

assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
token = res.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Test wedding details
res_w = client.get("/api/v1/customer/wedding", headers=headers)
print(f"Customer wedding status: {res_w.status_code}")
print(f"Customer wedding json: {res_w.json()}")
assert res_w.status_code == 200

# Test schedule
res_s = client.get("/api/v1/customer/schedule", headers=headers)
print(f"Customer schedule status: {res_s.status_code}, count: {len(res_s.json())}")
assert res_s.status_code == 200

# Test payments
res_p = client.get("/api/v1/customer/payments", headers=headers)
print(f"Customer payments status: {res_p.status_code}")
print(f"Customer payments json: {res_p.json()}")
assert res_p.status_code == 200

# Test documents
res_d = client.get("/api/v1/customer/documents", headers=headers)
print(f"Customer documents status: {res_d.status_code}")
print(f"Customer documents json: {res_d.json()}")
assert res_d.status_code == 200
assert len(res_d.json()) >= 2, f"Expected shared documents, got {res_d.json()}"

print("\nAll stage 5 customer portal endpoints verified successfully!")
