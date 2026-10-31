import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv("backend/.env")
raw_url = os.getenv("SUPABASE_DATABASE_URL", "")
if not raw_url:
    print("SUPABASE_DATABASE_URL not found!")
    exit(1)

pg_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1) if raw_url.startswith("postgresql://") else raw_url
connect_args = {"sslmode": "require"} if "sslmode" not in pg_url else {}

schema = "privilege_test_schema"

TABLES = [
    "users", "enquiries", "weddings", "vendors", "wedding_vendors",
    "tasks", "documents", "quotes", "quote_items", "ai_jobs",
    "quote_comparisons", "vendor_selections", "timeline_events",
    "incidents", "invoices", "payments"
]

PRIVILEGES = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
ROLES = ["anon", "authenticated"]

engine = create_engine(pg_url, connect_args=connect_args, echo=False)

with engine.connect() as conn:
    print(f"Creating isolated schema: {schema}...")
    conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE;"))
    conn.execute(text(f"CREATE SCHEMA {schema};"))
    conn.commit()

    # Create test tables
    for t in TABLES:
        conn.execute(text(f"CREATE TABLE {schema}.{t} (id text primary key, sample text);"))
    conn.commit()

    # Check privileges before hardening
    print("\n--- BEFORE HARDENING PRIVILEGES (Sample check) ---")
    for t in TABLES[:2]:
        for r in ROLES:
            for p in ["SELECT", "TRUNCATE"]:
                res = conn.execute(text(f"SELECT has_table_privilege('{r}', '{schema}.{t}', '{p}');")).scalar()
                print(f"Role {r:13} on {schema}.{t} {p:8}: {res}")

    # Prepare Hardening SQL
    hardening_sql = f"""
    -- 1. Revoke all privileges on existing application tables
    REVOKE ALL ON ALL TABLES IN SCHEMA {schema} FROM anon, authenticated, PUBLIC;
    REVOKE ALL ON ALL SEQUENCES IN SCHEMA {schema} FROM anon, authenticated, PUBLIC;
    REVOKE ALL ON ALL ROUTINES IN SCHEMA {schema} FROM anon, authenticated, PUBLIC;

    -- 2. Explicitly revoke destructive and execution privileges
    REVOKE TRUNCATE, TRIGGER, REFERENCES ON ALL TABLES IN SCHEMA {schema} FROM anon, authenticated, PUBLIC;

    -- 3. Configure default privileges for future tables and objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} REVOKE ALL ON TABLES FROM anon, authenticated, PUBLIC;
    ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} REVOKE ALL ON SEQUENCES FROM anon, authenticated, PUBLIC;
    ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} REVOKE ALL ON ROUTINES FROM anon, authenticated, PUBLIC;
    """

    print("\nExecuting hardening SQL in isolated schema...")
    for stmt in hardening_sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(text(stmt))
    conn.commit()

    # Check privileges after hardening
    print("\n--- AFTER HARDENING VERIFICATION ---")
    total_checks = 0
    violations = 0
    for t in TABLES:
        for r in ROLES:
            for p in PRIVILEGES:
                has_priv = conn.execute(text(f"SELECT has_table_privilege('{r}', '{schema}.{t}', '{p}');")).scalar()
                total_checks += 1
                if has_priv:
                    print(f"VIOLATION: Role '{r}' still has '{p}' on '{schema}.{t}'!")
                    violations += 1

    print(f"Completed {total_checks} privilege checks ({len(TABLES)} tables x {len(ROLES)} roles x {len(PRIVILEGES)} privileges).")
    print(f"Total privilege violations detected: {violations}")

    # Clean up isolated schema
    print(f"\nCleaning up isolated schema: {schema}...")
    conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE;"))
    conn.commit()
    print("Cleanup complete. Public schema was NOT touched.")

engine.dispose()
