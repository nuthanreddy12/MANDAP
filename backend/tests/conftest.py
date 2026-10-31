import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal, Base, engine
from backend.core.auth import get_current_user, create_access_token
from backend.models.models import User
from backend.api.seed_data import seed_initial_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()

@pytest.fixture
def auth_headers_owner():
    token = create_access_token({
        "sub": "u1",
        "email": "aarav@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_nisha():
    # Assigned planner for w1
    token = create_access_token({
        "sub": "u2",
        "email": "nisha@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_kabir():
    # Assigned coordinator/planner for w2
    token = create_access_token({
        "sub": "u3",
        "email": "kabir@theroyalknot.in",
        "role": "authenticated",
        "aud": "authenticated"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def default_owner_override():
    db = SessionLocal()
    owner = db.query(User).filter(User.role == "owner").first()
    db.close()
    app.dependency_overrides[get_current_user] = lambda: owner
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def client():
    db = SessionLocal()
    owner = db.query(User).filter(User.role == "owner").first()
    db.close()
    app.dependency_overrides[get_current_user] = lambda: owner
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)
