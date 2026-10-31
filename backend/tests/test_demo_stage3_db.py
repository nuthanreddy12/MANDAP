import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.models.models import (
    Base,
    Wedding,
    Vendor,
    Quote,
    QuoteItem,
    Document,
    AIJob,
    TimelineEvent,
    Incident,
    QuoteComparison,
    VendorSelection,
    User,
)
from backend.services.storage import read_document_file
from backend.core.database import run_schema_migrations

STAGE3_DB_PATH = "backend/storage/backups/mandap_demo_stage3.db"

def test_stage3_database_loads_independently():
    """Verify application models and relationships load from mandap_demo_stage3.db."""
    engine = create_engine(f"sqlite:///{STAGE3_DB_PATH}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Verify Wedding w1 exists
        wedding = db.query(Wedding).filter(Wedding.id == "w1").first()
        assert wedding is not None
        assert wedding.couple_names == "Mehra × Kapoor"
        assert wedding.guest_count == 420
        
        # 2. Verify users table has auth_user_id column
        users = db.query(User).all()
        assert len(users) >= 4
        assert hasattr(users[0], "auth_user_id")
        
        # 3. Verify all 3 demonstration quotations exist and link to w1
        quotes = db.query(Quote).filter(Quote.wedding_id == "w1", Quote.category == "catering").all()
        assert len(quotes) >= 3
        vendor_names = {q.vendor_name for q in quotes}
        assert "Royal Rajputana Hospitality & Banquets Pvt. Ltd." in vendor_names
        assert "Saffron Table Gourmet Catering Services" in vendor_names
        assert "Heritage Mewar Culinary Arts" in vendor_names
        
        # 4. Verify all 3 documents exist and resolve to valid PDF bytes on local disk
        documents = db.query(Document).filter(Document.wedding_id == "w1").all()
        assert len(documents) >= 3
        for doc in documents:
            assert os.path.exists(doc.storage_path), f"Document path does not exist: {doc.storage_path}"
            file_bytes = read_document_file(doc.storage_path)
            assert len(file_bytes) > 0
            assert file_bytes.startswith(b"%PDF"), f"File is not a valid PDF: {doc.storage_path}"
            
        # 5. Verify TimelineEvents and Incidents exist for w1
        events = db.query(TimelineEvent).filter(TimelineEvent.wedding_id == "w1").all()
        assert len(events) >= 5
        
        incidents = db.query(Incident).filter(Incident.wedding_id == "w1").all()
        assert len(incidents) >= 1
        
        # 6. Verify FK integrity
        fk_violations = db.execute(text("PRAGMA foreign_key_check")).fetchall()
        assert len(fk_violations) == 0
        
    finally:
        db.close()
