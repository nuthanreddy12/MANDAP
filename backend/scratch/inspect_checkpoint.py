import os
import glob
import time
from pathlib import Path

print("=== CHECKPOINT INSPECTION SCRIPT ===")
files_to_check = [
    "backend/core/auth.py",
    "backend/core/config.py",
    "backend/core/database.py",
    "backend/api/quotes.py",
    "backend/api/weddings.py",
    "backend/api/tasks.py",
    "backend/api/enquiries.py",
    "backend/api/vendors.py",
    "backend/main.py",
    "backend/scripts/migrate_to_postgres.py",
    "backend/scripts/migrate_documents_to_supabase.py",
    "backend/scripts/harden_pg_privileges.sql",
    "backend/scripts/build_curated_staging.py",
    "backend/scripts/test_curated_migration_pg.py",
    "backend/tests/test_auth_and_access.py",
    "backend/tests/conftest.py",
    "backend/tests/test_api.py",
    "backend/tests/test_milestone2.py",
    "backend/tests/test_milestone3.py",
    "backend/storage/backups/mandap_curated_staging.db",
    "backend/storage/backups/mandap_backup_20261031_163030.db",
    "mandap.db"
]

for f in files_to_check:
    p = Path(f)
    if p.exists():
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p.stat().st_mtime))
        print(f"[FOUND] {f:<55} | Size: {p.stat().st_size:>8} bytes | Modified: {mtime}")
    else:
        print(f"[MISSING] {f}")
