import os
import sqlite3
import datetime
import hashlib

def create_sqlite_backup(source_db_path="mandap.db", backup_dir="backend/storage/backups"):
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"mandap_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)

    print(f"Starting online SQLite backup from '{source_db_path}' to '{backup_path}'...")
    
    source_conn = sqlite3.connect(source_db_path)
    backup_conn = sqlite3.connect(backup_path)

    # Use SQLite's native C backup API
    with backup_conn:
        source_conn.backup(backup_conn, pages=100)

    backup_conn.close()
    source_conn.close()

    print("Native SQLite backup completed successfully.")
    
    # Verification Procedure
    print("Verifying backup integrity...")
    verify_conn = sqlite3.connect(backup_path)
    cur = verify_conn.cursor()
    
    # 1. PRAGMA integrity_check
    integrity_result = cur.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"  Integrity Check: {integrity_result}")
    assert integrity_result == "ok", f"Integrity check failed: {integrity_result}"
    
    # 2. Table count check
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    print(f"  Tables backed up: {len(tables)} tables")
    
    # 3. Row count reconciliation
    orig_conn = sqlite3.connect(source_db_path)
    orig_cur = orig_conn.cursor()
    mismatches = []
    total_rows = 0
    
    for t in tables:
        orig_count = orig_cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        bak_count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        total_rows += bak_count
        if orig_count != bak_count:
            mismatches.append((t, orig_count, bak_count))
            
    orig_conn.close()
    verify_conn.close()
    
    if mismatches:
        raise ValueError(f"Backup verification failed. Row count mismatches: {mismatches}")
        
    print(f"  Row reconciliation: All {len(tables)} tables matched exactly ({total_rows} total rows).")
    
    # Calculate SHA256 of backup file
    with open(backup_path, "rb") as f:
        bak_sha256 = hashlib.sha256(f.read()).hexdigest()
    print(f"  Backup SHA-256: {bak_sha256}")
    print(f"  Backup file size: {os.path.getsize(backup_path):,} bytes")
    
    return backup_path

if __name__ == "__main__":
    backup_file = create_sqlite_backup()
    print(f"\nBACKUP VERIFIED AND READY: {backup_file}")
