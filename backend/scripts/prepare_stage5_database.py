import os
import shutil
import sqlite3
import datetime
from sqlalchemy import create_engine
from backend.models.models import Base
from backend.core.database import run_schema_migrations

SOURCE_DB = "backend/storage/backups/mandap_demo_stage4.db"
TARGET_DB = "backend/storage/backups/mandap_demo_stage5.db"

def prepare_stage5_db():
    print(f"Creating separate stage 5 database copy from {SOURCE_DB} -> {TARGET_DB}...")
    shutil.copyfile(SOURCE_DB, TARGET_DB)
    
    # 1. Apply schema migrations
    engine = create_engine(f"sqlite:///{TARGET_DB}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    engine.dispose()

    # 2. Add synthetic invitation and client details to w1
    conn = sqlite3.connect(TARGET_DB)
    cur = conn.cursor()

    # Ensure w1 has invitation code and client contact details
    cur.execute("""
        UPDATE weddings
        SET client_name = 'Priya Mehra',
            client_email = 'priya.mehra@gmail.com',
            client_phone = '+91 98765 43210',
            invitation_code = 'ROYAL-MK-2026',
            customer_user_id = NULL
        WHERE id = 'w1'
    """)

    # Clean any pre-existing user with email priya.mehra@gmail.com to ensure fresh signup works
    cur.execute("DELETE FROM users WHERE email = 'priya.mehra@gmail.com'")

    # Clean existing invitation cinv_1 if present, then insert
    cur.execute("DELETE FROM customer_invitations WHERE invitation_code = 'ROYAL-MK-2026' OR id = 'cinv_1'")
    cur.execute("""
        INSERT INTO customer_invitations (
            id, wedding_id, invitation_code, client_email, client_name, is_claimed, claimed_by_user_id, created_at
        ) VALUES (
            'cinv_1',
            'w1',
            'ROYAL-MK-2026',
            'priya.mehra@gmail.com',
            'Priya Mehra',
            0,
            NULL,
            ?
        )
    """, (datetime.datetime.now(datetime.timezone.utc).isoformat(),))

    # Seed client-shared documents for w1
    cur.execute("DELETE FROM documents WHERE id IN ('doc_client_guide', 'doc_client_menu')")
    cur.execute("""
        INSERT INTO documents (
            id, wedding_id, filename, file_size, file_hash, storage_path, content_type, status, is_shared_with_client, created_at
        ) VALUES (
            'doc_client_guide',
            'w1',
            'Mehra_Kapoor_Wedding_Guest_Guide.pdf',
            184320,
            'hash_guide_mk_2026',
            'backend/storage/documents/Mehra_Kapoor_Wedding_Guest_Guide.pdf',
            'application/pdf',
            'ready',
            1,
            ?
        )
    """, (datetime.datetime.now(datetime.timezone.utc).isoformat(),))

    cur.execute("""
        INSERT INTO documents (
            id, wedding_id, filename, file_size, file_hash, storage_path, content_type, status, is_shared_with_client, created_at
        ) VALUES (
            'doc_client_menu',
            'w1',
            'Royal_Rajputana_Approved_Catering_Tasting_Menu.pdf',
            245760,
            'hash_menu_mk_2026',
            'backend/storage/documents/Royal_Rajputana_Approved_Catering_Tasting_Menu.pdf',
            'application/pdf',
            'ready',
            1,
            ?
        )
    """, (datetime.datetime.now(datetime.timezone.utc).isoformat(),))

    conn.commit()

    # Verify
    cur.execute("SELECT id, couple_names, client_name, client_email, invitation_code, customer_user_id FROM weddings WHERE id='w1'")
    w1_row = cur.fetchone()
    print(f"Verified Wedding w1: {w1_row}")

    cur.execute("SELECT id, wedding_id, invitation_code, client_email, client_name, is_claimed FROM customer_invitations WHERE invitation_code='ROYAL-MK-2026'")
    inv_row = cur.fetchone()
    print(f"Verified Invitation: {inv_row}")

    cur.execute("SELECT id, filename, is_shared_with_client FROM documents WHERE wedding_id='w1'")
    docs = cur.fetchall()
    print(f"Verified Documents for w1: {docs}")

    conn.close()
    print(f"Successfully configured stage 5 database: {TARGET_DB}")

if __name__ == "__main__":
    prepare_stage5_db()
