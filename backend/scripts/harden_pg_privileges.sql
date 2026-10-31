-- =========================================================================
-- MANDAP POSTGRESQL TABLE PRIVILEGE HARDENING SCRIPT
-- Target: Supabase PostgreSQL (Applied post-migration)
-- Purpose:
--   1. Ensure browser roles (anon, authenticated) and PUBLIC have ZERO direct
--      privileges (SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER)
--      on any Mandap application business tables.
--   2. Explicitly revoke TRUNCATE on all tables.
--   3. Correct default privileges for any future tables created by table owner.
--   4. Guarantee all client requests MUST route through authenticated FastAPI backend.
-- =========================================================================

-- Step 1: Revoke all existing table privileges from browser & public roles
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated, PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated, PUBLIC;
REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated, PUBLIC;

-- Step 2: Explicitly remove destructive and administrative privileges
REVOKE TRUNCATE, TRIGGER, REFERENCES ON ALL TABLES IN SCHEMA public FROM anon, authenticated, PUBLIC;

-- Step 3: Hardened Default Privileges (Prevents future tables from auto-granting permissions)
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated, PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated, PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON ROUTINES FROM anon, authenticated, PUBLIC;

-- Step 4: Verification Helper Query
-- Run this to confirm 0 privileges for anon and authenticated:
/*
SELECT 
    schemaname, tablename, 
    has_table_privilege('anon', schemaname || '.' || tablename, 'SELECT') AS anon_select,
    has_table_privilege('anon', schemaname || '.' || tablename, 'TRUNCATE') AS anon_truncate,
    has_table_privilege('authenticated', schemaname || '.' || tablename, 'SELECT') AS auth_select,
    has_table_privilege('authenticated', schemaname || '.' || tablename, 'TRUNCATE') AS auth_truncate
FROM pg_tables 
WHERE schemaname = 'public';
*/
