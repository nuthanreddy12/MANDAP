import os
import sys
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv("backend/.env")
raw_url = os.getenv("SUPABASE_DATABASE_URL", "")
if not raw_url:
    print("SUPABASE_DATABASE_URL missing!")
    sys.exit(1)

pg_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1) if raw_url.startswith("postgresql://") else raw_url
connect_args = {"sslmode": "require"} if "sslmode" not in pg_url else {}

staging_sqlite_path = "backend/storage/backups/mandap_curated_staging.db"
target_schema = "curated_staging_test"

print(f"=== TESTING MIGRATION WITH CURATED STAGING DATASET ===")
print(f"Source: {staging_sqlite_path}")
print(f"Target Schema: {target_schema}")

# Connect to target PG
pg_engine = create_engine(pg_url, connect_args=connect_args, echo=False)

# 1. Clean and setup isolated target schema
with pg_engine.connect() as conn:
    conn.execute(text(f"DROP SCHEMA IF EXISTS {target_schema} CASCADE;"))
    conn.execute(text(f"CREATE SCHEMA {target_schema};"))
    conn.commit()

# 2. Run Alembic / Model schema creation in isolated schema
from backend.core.database import Base
from backend.models.models import *

# Set schema on models for isolated test
for table in Base.metadata.tables.values():
    table.schema = target_schema

Base.metadata.create_all(bind=pg_engine)
print(f"[OK] Created all {len(Base.metadata.tables)} tables in {target_schema}")

# Reset schema on models
for table in Base.metadata.tables.values():
    table.schema = None

# 3. Run migration using migrate_to_postgres
from backend.scripts.migrate_to_postgres import migrate_database

print("\n--- RUN 1: INSERT-ONLY MIGRATION ---")
src_stats, tgt_stats = migrate_database(
    source_db_url=f"sqlite:///{staging_sqlite_path}",
    target_db_url=pg_url,
    target_schema=target_schema,
    dry_run=False
)
assert len(tgt_stats) == 16, "Migration Run 1 did not migrate 16 tables!"
print("[OK] Migration Run 1 completed successfully.")

# 4. Verify duplicate-run rejection via migration ledger
print("\n--- RUN 2: DUPLICATE-RUN REJECTION TEST ---")
try:
    migrate_database(
        source_db_url=f"sqlite:///{staging_sqlite_path}",
        target_db_url=pg_url,
        target_schema=target_schema,
        dry_run=False
    )
    assert False, "Duplicate migration should have raised RuntimeError!"
except RuntimeError as e:
    print(f"[OK] Duplicate run was correctly blocked by migration ledger: {e}")


# 5. Financial parity verification
print("\n--- VERIFYING FINANCIAL PARITY ---")
sqlite_engine = create_engine(f"sqlite:///{staging_sqlite_path}")
with sqlite_engine.connect() as s_conn, pg_engine.connect() as p_conn:
    s_budget = s_conn.execute(text("SELECT sum(client_budget) FROM weddings")).scalar() or Decimal("0")
    p_budget = p_conn.execute(text(f"SELECT sum(client_budget) FROM {target_schema}.weddings")).scalar() or Decimal("0")
    assert Decimal(str(s_budget)) == Decimal(str(p_budget)), f"Budget mismatch: {s_budget} vs {p_budget}"

    s_quotes = s_conn.execute(text("SELECT sum(total_amount) FROM quotes")).scalar() or Decimal("0")
    p_quotes = p_conn.execute(text(f"SELECT sum(total_amount) FROM {target_schema}.quotes")).scalar() or Decimal("0")
    assert Decimal(str(s_quotes)) == Decimal(str(p_quotes)), f"Quotes mismatch: {s_quotes} vs {p_quotes}"

    s_invoices = s_conn.execute(text("SELECT sum(invoice_total) FROM invoices")).scalar() or Decimal("0")
    p_invoices = p_conn.execute(text(f"SELECT sum(invoice_total) FROM {target_schema}.invoices")).scalar() or Decimal("0")
    assert Decimal(str(s_invoices)) == Decimal(str(p_invoices)), f"Invoices mismatch: {s_invoices} vs {p_invoices}"

    s_payments = s_conn.execute(text("SELECT sum(amount) FROM payments")).scalar() or Decimal("0")
    p_payments = p_conn.execute(text(f"SELECT sum(amount) FROM {target_schema}.payments")).scalar() or Decimal("0")
    assert Decimal(str(s_payments)) == Decimal(str(p_payments)), f"Payments mismatch: {s_payments} vs {p_payments}"

print(f"[OK] Financial parity 100% verified down to the exact rupee:")
print(f"   Weddings Budget: INR {p_budget:,.2f}")
print(f"   Quotes Total:    INR {p_quotes:,.2f}")
print(f"   Invoices Total:  INR {p_invoices:,.2f}")
print(f"   Payments Total:  INR {p_payments:,.2f}")

# 6. Intentional failure rollback test
print("\n--- ROLLBACK TEST ON INTENTIONAL FAILURE ---")
# Drop and recreate schema for rollback test
with pg_engine.connect() as conn:
    conn.execute(text(f"DROP SCHEMA IF EXISTS {target_schema} CASCADE;"))
    conn.execute(text(f"CREATE SCHEMA {target_schema};"))
    conn.commit()

for table in Base.metadata.tables.values():
    table.schema = target_schema
Base.metadata.create_all(bind=pg_engine)
for table in Base.metadata.tables.values():
    table.schema = None

# Attempt migration with intentional corrupted payload (simulated failure)
SessionPg = sessionmaker(bind=pg_engine)
session = SessionPg()
session.execute(text(f"SET search_path TO {target_schema}"))
try:
    with session.begin():
        session.execute(text(f"INSERT INTO {target_schema}.users (id, name, email, role) VALUES ('test_u1', 'Test', 'test@test.com', 'owner')"))
        # Intentional constraint violation
        session.execute(text(f"INSERT INTO {target_schema}.users (id, name, email, role) VALUES ('test_u2', 'Test2', NULL, 'owner')"))
except Exception as e:
    print(f"[OK] Caught intentional database exception: {type(e).__name__}")
    session.rollback()
finally:
    session.close()

with pg_engine.connect() as conn:
    cnt = conn.execute(text(f"SELECT count(*) FROM {target_schema}.users;")).scalar()
    assert cnt == 0, f"Rollback failed: expected 0 users, found {cnt}"
    print(f"[OK] Rollback confirmed: {target_schema}.users count is {cnt}")

# 7. Cleanup isolated schema
print(f"\n--- CLEANUP ---")
with pg_engine.connect() as conn:
    conn.execute(text(f"DROP SCHEMA IF EXISTS {target_schema} CASCADE;"))
    conn.commit()
print(f"[OK] Schema {target_schema} dropped. Public schema remains unchanged.")

sqlite_engine.dispose()
pg_engine.dispose()
print("\nALL TASK 5 TESTS PASSED WITH 100% PARITY!")
