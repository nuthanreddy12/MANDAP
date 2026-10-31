import os
import sys
import hashlib
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath("."))
from backend.models.models import Document
from backend.core.supabase_client import get_supabase_client
from backend.core.config import settings

def migrate_local_documents_to_supabase(dry_run=True, db_path=None):
    print("=" * 65)
    print("MANDAP DOCUMENT CLOUD STORAGE MIGRATION TOOL")
    print(f"Mode: {'DRY RUN (Preview Only)' if dry_run else 'LIVE UPLOAD'}")
    print("=" * 65)

    load_dotenv("backend/.env")
    supabase = get_supabase_client()
    if not supabase:
        raise ValueError("Supabase client could not be initialized. Check backend/.env credentials.")

    bucket_name = getattr(settings, "SUPABASE_BUCKET", "mandap-documents") or "mandap-documents"

    # Resolve database connection
    if db_path:
        target_db_file = os.path.abspath(db_path)
        db_url = f"sqlite:///{target_db_file}"
    else:
        from backend.core.database import engine
        db_url = str(engine.url)
        target_db_file = os.path.abspath(str(engine.url.database))

    print(f"Target Database Engine: {db_url}")
    print(f"Target Database Path:   {target_db_file}")
    print(f"Target Cloud Bucket:    {bucket_name}\n")

    db_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    DbSession = sessionmaker(bind=db_engine)
    db = DbSession()

    try:
        docs = db.query(Document).all()
        local_docs = [d for d in docs if not d.storage_path.startswith("supabase://")]
        cloud_docs = [d for d in docs if d.storage_path.startswith("supabase://")]

        print(f"Total Document records: {len(docs)}")
        print(f"Already in Supabase:    {len(cloud_docs)}")
        print(f"Pending Cloud Upload:   {len(local_docs)}\n")

        if not local_docs:
            print("All documents are already stored in Supabase Storage.")
            return

        for idx, doc in enumerate(local_docs, 1):
            print(f"[{idx}/{len(local_docs)}] Inspecting: {doc.id} ({doc.filename})")
            print(f"     Current DB path: {doc.storage_path}")

            if not os.path.exists(doc.storage_path):
                print(f"     ERROR: File not found on local disk: {doc.storage_path}. Skipping.")
                continue

            with open(doc.storage_path, "rb") as f:
                file_bytes = f.read()

            local_hash = hashlib.sha256(file_bytes).hexdigest()
            if local_hash != doc.file_hash:
                print(f"     WARNING: Local file hash ({local_hash[:12]}...) does not match DB hash ({doc.file_hash[:12]}...)")
            else:
                print(f"     Hash verification: PASSED (SHA-256: {local_hash[:16]}...)")

            safe_filename = "".join(c for c in doc.filename if c.isalnum() or c in "._- ")
            cloud_key = f"{doc.wedding_id}/{doc.id}_{safe_filename}"
            new_storage_path = f"supabase://{bucket_name}/{cloud_key}"
            print(f"     Target Cloud Key: {bucket_name}/{cloud_key}")

            if dry_run:
                print("     [DRY RUN] Would upload to Supabase, verify SHA-256, and update DB reference.")
            else:
                try:
                    # 1. Upload to Supabase Storage
                    supabase.storage.from_(bucket_name).upload(
                        path=cloud_key,
                        file=file_bytes,
                        file_options={"content-type": doc.content_type or "application/pdf", "upsert": "true"}
                    )
                    print("     Cloud upload: SUCCESS")

                    # 2. Download and verify SHA-256 equality
                    downloaded_bytes = supabase.storage.from_(bucket_name).download(cloud_key)
                    down_hash = hashlib.sha256(downloaded_bytes).hexdigest()
                    if down_hash != local_hash:
                        raise ValueError(f"SHA-256 mismatch: downloaded={down_hash} != local={local_hash}")
                    print("     Integrity verification: 100% binary match with original file")

                    # 3. Update database record reference only after verification succeeds
                    doc.storage_path = new_storage_path
                    db.commit()
                    print(f"     Database reference updated -> {new_storage_path}")
                    print("     (Original local file preserved intact)")
                except Exception as upload_err:
                    db.rollback()
                    print(f"     ERROR: Upload or verification failed: {upload_err}. Database reference left unchanged.")

    finally:
        db.close()
        db_engine.dispose()

    print("\n" + "=" * 65)
    print(f"DOCUMENT MIGRATION {'DRY RUN ' if dry_run else ''}COMPLETED")
    print("=" * 65)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mandap Document Cloud Storage Migration Tool")
    parser.add_argument("--db-path", type=str, default=None, help="Explicit SQLite database path to update")
    parser.add_argument("--execute", action="store_true", help="Execute live upload to Supabase Storage")
    args = parser.parse_args()

    migrate_local_documents_to_supabase(dry_run=not args.execute, db_path=args.db_path)
