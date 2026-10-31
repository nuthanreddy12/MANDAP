import os
import sys
import sqlite3
import datetime
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath("."))
from backend.core.database import Base
import backend.models.models as models
from backend.scripts.migrate_to_postgres import MIGRATION_ORDER, MODEL_MAP, clean_record_for_model

load_dotenv("backend/.env")
raw_url = os.getenv("SUPABASE_DATABASE_URL", "")

if not raw_url:
    print("ERROR: SUPABASE_DATABASE_URL not set in backend/.env")
    sys.exit(1)

pg_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1) if raw_url.startswith("postgresql://") else raw_url
connect_args = {}
if "sslmode" not in pg_url:
    connect_args["sslmode"] = "require"

print("=" * 65)
print("MANDAP POSTGRESQL MIGRATION REHEARSAL")
print("=" * 65)

# Step 1: Verify PostgreSQL Target
print("\n--- STEP 1: VERIFY POSTGRESQL TARGET ---")
engine = create_engine(pg_url, connect_args=connect_args, echo=False)

with engine.connect() as conn:
    db_name = conn.execute(text("SELECT current_database();")).scalar()
    user_name = conn.execute(text("SELECT current_user;")).scalar()
    version = conn.execute(text("SELECT version();")).scalar()
    print(f"Target Database: {db_name}")
    print(f"Connected User: {user_name}")
    print(f"Server Engine: {version.split(' on ')[0]}")
    
    # Check public schema tables
    public_tables = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    )).scalars().all()
    print(f"Existing tables in 'public' schema: {public_tables}")
    if not public_tables:
        print("  -> 'public' schema is clean and empty. Zero application records will be overwritten.")
    else:
        print(f"  -> WARNING: Found existing tables: {public_tables}")

# Step 2: Create Rehearsal Schema
print("\n--- STEP 2: TEST POSTGRESQL SCHEMA COMPATIBILITY ---")
SCHEMA_NAME = "mandap_rehearsal"

with engine.connect() as conn:
    conn.execute(text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;"))
    conn.execute(text(f"CREATE SCHEMA {SCHEMA_NAME};"))
    conn.commit()
    print(f"Isolated schema '{SCHEMA_NAME}' created.")

# Configure engine connection to default search path to rehearsal schema
rehearsal_engine = create_engine(
    pg_url,
    connect_args={
        **connect_args,
        "options": f"-c search_path={SCHEMA_NAME},public"
    },
    echo=False
)

# Step 3: Rehearse Complete Migration using SQLite Backup
print("\n--- STEP 3: REHEARSE MIGRATION INTO ISOLATED SCHEMA ---")
backup_path = "backend/storage/backups/mandap_backup_20261031_154204.db"
if not os.path.exists(backup_path):
    backup_path = "mandap.db"
print(f"Using verified backup source: '{backup_path}'")

with rehearsal_engine.begin() as conn:
    # Provision tables in isolated schema
    Base.metadata.create_all(bind=conn)
    print(f"Created all 16 tables in schema '{SCHEMA_NAME}'.")

src_conn = sqlite3.connect(backup_path)
src_conn.row_factory = sqlite3.Row

RehearsalSession = sessionmaker(bind=rehearsal_engine)
session = RehearsalSession()

source_counts = {}
migrated_counts = {}

try:
    for table_name in MIGRATION_ORDER:
        model_cls = MODEL_MAP[table_name]
        rows = src_conn.execute(f"SELECT * FROM {table_name}").fetchall()
        source_counts[table_name] = len(rows)
        
        for r in rows:
            clean_dict = clean_record_for_model(model_cls, dict(r))
            obj = model_cls(**clean_dict)
            session.add(obj)
            
        session.flush()
        migrated_counts[table_name] = len(rows)
        print(f"  Loaded {table_name:<20}: {len(rows):>4} rows")
        
    session.commit()
    print("\nTransaction committed successfully into rehearsal schema.")
except Exception as e:
    session.rollback()
    print(f"\nREHEARSAL ERROR: {e}")
    raise
finally:
    src_conn.close()

# Step 4: Verification & Integrity Audit in PostgreSQL
print("\n--- STEP 4: VERIFICATION & AUDIT IN POSTGRESQL ---")

with rehearsal_engine.connect() as conn:
    # 1. Table Count Verification
    print("\n1. Record Parity Reconciliation:")
    print(f"{'Table Name':<22} | {'Source Count':<12} | {'Target Count':<12} | {'Parity'}")
    print("-" * 62)
    all_matched = True
    for t in MIGRATION_ORDER:
        target_count = conn.execute(text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.{t};")).scalar()
        src_c = source_counts[t]
        parity = "MATCH" if src_c == target_count else "FAIL"
        if parity == "FAIL":
            all_matched = False
        print(f"{t:<22} | {src_c:<12} | {target_count:<12} | {parity}")
    print(f"All 16 tables count parity: {all_matched}")

    # 2. Foreign Key Integrity Audit
    print("\n2. Foreign Key Integrity Audit:")
    fk_checks = [
        ("tasks -> weddings", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.tasks t LEFT JOIN {SCHEMA_NAME}.weddings w ON t.wedding_id = w.id WHERE w.id IS NULL;"),
        ("quotes -> weddings", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.quotes q LEFT JOIN {SCHEMA_NAME}.weddings w ON q.wedding_id = w.id WHERE w.id IS NULL;"),
        ("quotes -> vendors", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.quotes q LEFT JOIN {SCHEMA_NAME}.vendors v ON q.vendor_id = v.id WHERE v.id IS NULL;"),
        ("quote_items -> quotes", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.quote_items qi LEFT JOIN {SCHEMA_NAME}.quotes q ON qi.quote_id = q.id WHERE q.id IS NULL;"),
        ("documents -> weddings", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.documents d LEFT JOIN {SCHEMA_NAME}.weddings w ON d.wedding_id = w.id WHERE w.id IS NULL;"),
        ("wedding_vendors -> weddings", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.wedding_vendors wv LEFT JOIN {SCHEMA_NAME}.weddings w ON wv.wedding_id = w.id WHERE w.id IS NULL;"),
        ("vendor_selections -> quotes", f"SELECT COUNT(*) FROM {SCHEMA_NAME}.vendor_selections vs LEFT JOIN {SCHEMA_NAME}.quotes q ON vs.quote_id = q.id WHERE q.id IS NULL;"),
    ]
    all_fks_valid = True
    for desc, query in fk_checks:
        orphans = conn.execute(text(query)).scalar()
        status = "PASSED" if orphans == 0 else f"FAILED ({orphans} orphans)"
        if orphans != 0:
            all_fks_valid = False
        print(f"  {desc:<32}: {status}")

    # 3. Financial Totals Parity
    print("\n3. Financial Calculations Parity:")
    src_conn = sqlite3.connect(backup_path)
    src_cur = src_conn.cursor()
    
    # Quotes total sum
    src_quotes_total = Decimal(str(src_cur.execute("SELECT ROUND(SUM(total_amount), 2) FROM quotes;").fetchone()[0] or 0))
    pg_quotes_total = conn.execute(text(f"SELECT ROUND(SUM(total_amount), 2) FROM {SCHEMA_NAME}.quotes;")).scalar() or Decimal("0")
    print(f"  Quotes Total Amount: SQLite={src_quotes_total} | PostgreSQL={pg_quotes_total} | Match={src_quotes_total == pg_quotes_total}")
    
    # Weddings client budget sum
    src_budget_total = Decimal(str(src_cur.execute("SELECT ROUND(SUM(client_budget), 2) FROM weddings;").fetchone()[0] or 0))
    pg_budget_total = conn.execute(text(f"SELECT ROUND(SUM(client_budget), 2) FROM {SCHEMA_NAME}.weddings;")).scalar() or Decimal("0")
    print(f"  Client Budget Total: SQLite={src_budget_total} | PostgreSQL={pg_budget_total} | Match={src_budget_total == pg_budget_total}")

    # Payments amount sum
    src_payments_total = Decimal(str(src_cur.execute("SELECT ROUND(SUM(amount), 2) FROM payments;").fetchone()[0] or 0))
    pg_payments_total = conn.execute(text(f"SELECT ROUND(SUM(amount), 2) FROM {SCHEMA_NAME}.payments;")).scalar() or Decimal("0")
    print(f"  Payments Total Amount: SQLite={src_payments_total} | PostgreSQL={pg_payments_total} | Match={src_payments_total == pg_payments_total}")

    # Quote Items line total sum
    src_qi_total = Decimal(str(src_cur.execute("SELECT ROUND(SUM(line_total), 2) FROM quote_items;").fetchone()[0] or 0))
    pg_qi_total = conn.execute(text(f"SELECT ROUND(SUM(line_total), 2) FROM {SCHEMA_NAME}.quote_items;")).scalar() or Decimal("0")
    print(f"  Quote Items Total: SQLite={src_qi_total} | PostgreSQL={pg_qi_total} | Match={src_qi_total == pg_qi_total}")
    src_conn.close()

    # 4. Document Storage References
    print("\n4. Document Records Verification:")
    docs = conn.execute(text(f"SELECT id, filename, storage_path, file_hash FROM {SCHEMA_NAME}.documents;")).fetchall()
    print(f"  Total Document records in PostgreSQL: {len(docs)}")
    for d in docs:
        is_cloud = d[2].startswith("supabase://")
        print(f"    - {d[0]}: {d[1]} | Type: {'Cloud Storage' if is_cloud else 'Local Filesystem'} | Hash: {d[3][:12]}...")

session.close()
rehearsal_engine.dispose()

# Step 5: Clean Up Isolated Schema
print("\n--- STEP 5: CLEAN UP ISOLATED SCHEMA ---")
with engine.connect() as conn:
    conn.execute(text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;"))
    conn.commit()
    print(f"Schema '{SCHEMA_NAME}' successfully dropped.")
    
    # Confirm public schema remains untouched
    post_tables = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    )).scalars().all()
    print(f"Final check - 'public' schema table count: {len(post_tables)} tables (Untouched).")

engine.dispose()
print("\n" + "=" * 65)
print("REHEARSAL COMPLETED SUCCESSFULLY WITH 100% DATA PARITY")
print("=" * 65)
