# MANDAP: POSTGRESQL PRODUCTION MIGRATION RUNBOOK
## SQLite to Supabase PostgreSQL Migration Architecture, Runbook & Safeguards

This document specifies the authoritative production migration runbook for transitioning MANDAP from local SQLite (`mandap.db`) to Supabase Hosted PostgreSQL.

---

## 1. ARCHITECTURE & SECURITY BASELINE

- **Backend Architecture:** React 19 + TypeScript frontend communicating with FastAPI Python backend.
- **Database Engine Target:** Supabase PostgreSQL 17.11 (`aws-0-ap-south-1.pooler.supabase.com:5432` / `comxzsluipgjfrfdvlev.supabase.co`).
- **Connection Protocol:** TLS encrypted connection with `sslmode=require` via SQLAlchemy 2 and `psycopg` 3.3.6 (`postgresql+psycopg://`).
- **Backend Role Access:** FastAPI backend connects with service-role privileges, bypassing RLS at the database engine level.
- **Tenant Authorization:** Agency and wedding scoping is strictly validated within FastAPI route handlers (`wedding_id` validation on every query). Browser clients never receive the Supabase secret key.
- **Row Level Security (RLS):** Enabled on all 16 tables. Direct browser (`anon` and `authenticated`) access to business tables is denied by default (zero broad `auth.uid() IS NOT NULL` policies). Future client-side access will require explicit `agency_id` mapping.

---

## 2. ACTIVE SOURCE DATABASE & BACKUP RECONCILIATION

- **Active Engine URL:** `sqlite:///./mandap.db`
- **Absolute Source Path:** `C:\Users\nutha\OneDrive\Desktop\1\mandap.db` (344,064 bytes)
- **Verified Point-in-Time Backup:** [backend/storage/backups/mandap_backup_20261031_155135.db](file:///c:/Users/nutha/OneDrive/Desktop/1/backend/storage/backups/mandap_backup_20261031_155135.db) (344,064 bytes)
- **Backup Method:** Native SQLite C Backup API (`sqlite3.Connection.backup`) with incremental 100-page stepping.
- **Integrity Status:** `PRAGMA integrity_check: ok`
- **Reconciliation Parity:** All 16 tables and 479 records matched with 100% exact parity:

| Table Name | Source SQLite Count | Verified Backup Count | Parity Status |
| :--- | :---: | :---: | :---: |
| `users` | 4 | 4 | **MATCH** |
| `weddings` | 14 | 14 | **MATCH** |
| `vendors` | 20 | 20 | **MATCH** |
| `enquiries` | 15 | 15 | **MATCH** |
| `tasks` | 359 | 359 | **MATCH** |
| `timeline_events` | 5 | 5 | **MATCH** |
| `wedding_vendors` | 13 | 13 | **MATCH** |
| `documents` | 7 | 7 | **MATCH** |
| `quotes` | 11 | 11 | **MATCH** |
| `quote_items` | 10 | 10 | **MATCH** |
| `ai_jobs` | 7 | 7 | **MATCH** |
| `quote_comparisons` | 8 | 8 | **MATCH** |
| `vendor_selections` | 1 | 1 | **MATCH** |
| `incidents` | 1 | 1 | **MATCH** |
| `invoices` | 1 | 1 | **MATCH** |
| `payments` | 3 | 3 | **MATCH** |
| **TOTALS** | **479** | **479** | **100% PARITY** |

---

## 3. VERSIONED SCHEMA MIGRATIONS (ALEMBIC)

Versioned migration created at [backend/alembic/versions/0001_initial_mandap_schema.py](file:///c:/Users/nutha/OneDrive/Desktop/1/backend/alembic/versions/0001_initial_mandap_schema.py):
- Contains explicit DDL for all 16 application tables.
- Preserves primary keys, foreign key constraints, and unique indices.
- Preserves `NUMERIC(12, 2)` decimal precision for monetary calculations.
- Preserves `JSON` / `JSONB` structures for line items, inclusions, and comparisons.
- Preserves `TIMESTAMP WITH TIME ZONE` for chronological auditing.
- Retains full dual compatibility for SQLite and PostgreSQL.

Execution command:
```powershell
.\backend\.venv\Scripts\alembic upgrade head
```

---

## 4. INSERT-ONLY ATOMIC DATA MIGRATION PROCEDURE

Migration engine: [backend/scripts/migrate_to_postgres.py](file:///c:/Users/nutha/OneDrive/Desktop/1/backend/scripts/migrate_to_postgres.py)

### Safeguards Implemented:
1. **Target Pre-Flight Check:** Verifies that target application tables in schema `public` are clean and empty. Aborts immediately if unexpected records exist.
2. **Ledger Protection (`_mandap_migration_ledger`):** Aborts immediately if a previous completed migration is recorded, preventing accidental re-execution or duplication.
3. **No Overwrites (Insert-Only):** Employs `target_session.add()` rather than `merge()`. Primary keys from SQLite are preserved verbatim.
4. **Strict Dependency Order:** Populates parent entities before children:
   `users` -> `weddings` -> `vendors` -> `enquiries` -> `tasks` -> `timeline_events` -> `wedding_vendors` -> `documents` -> `quotes` -> `quote_items` -> `ai_jobs` -> `quote_comparisons` -> `vendor_selections` -> `incidents` -> `invoices` -> `payments`.
5. **Single Atomic Transaction:** Flushes each table in order. The single `commit()` occurs only after all 16 tables are populated and audited.
6. **Pre-Commit Verification:** Compares source vs target row counts and validates exact financial sums:
   - Quotes Total: `INR 16,936,600.00`
   - Client Budget Total: `INR 270,000,000.00`
   - Payments Total: `INR 10,200,000.00`
   - Quote Items Total: `INR 12,292,000.00`

---

## 5. DOCUMENT CLOUD STORAGE MIGRATION SEQUENCE

Document migration script: [backend/scripts/migrate_documents_to_supabase.py](file:///c:/Users/nutha/OneDrive/Desktop/1/backend/scripts/migrate_documents_to_supabase.py)

### Sequence:
1. Identify all documents with local filesystem paths (`backend/storage/documents/...`).
2. Read local bytes and verify SHA-256 against `document.file_hash`.
3. Upload to private Supabase Storage bucket `mandap-documents` (`{wedding_id}/{doc_id}_{filename}`).
4. Download the uploaded object from Supabase and verify downloaded SHA-256 equals original hash.
5. Update database `storage_path` to `supabase://mandap-documents/{wedding_id}/{doc_id}_{filename}`.
6. Preserve local disk files (no local files are deleted).

---

## 6. ROW LEVEL SECURITY (RLS) ACTIVATION

Apply [backend/scripts/setup_rls_policies.sql](file:///c:/Users/nutha/OneDrive/Desktop/1/backend/scripts/setup_rls_policies.sql) via Supabase SQL Editor or migration tool:
- Enables RLS across all 16 tables.
- Creates explicit `FOR ALL TO service_role` policies.
- Grants zero policies to `anon` and `authenticated` roles (default deny).

---

## 7. ROLLBACK & RECOVERY PROCEDURE

If any failure occurs during live migration:
1. **Automatic Transaction Rollback:** `target_session.rollback()` reverts all inserted rows in PostgreSQL.
2. **Environment Safeguard:** `DATABASE_URL` in `backend/.env` remains `sqlite:///./mandap.db`.
3. **Database Restoration:** The verified backup `mandap_backup_20261031_155135.db` guarantees instantaneous restoration if the source SQLite file were ever affected.
4. **Zero Destructive Commands:** No `DROP TABLE` or `DROP SCHEMA` commands are executed against the public schema.

---

## 8. POST-MIGRATION APPLICATION TESTING

Once migration is executed and `DATABASE_URL` is switched to the Supabase connection string:
1. Run backend test suite: `pytest backend/tests/` (all 20 tests must pass against PostgreSQL).
2. Start backend server: `uvicorn backend.main:app --port 8000`
3. Launch React frontend: `npm run dev`
4. Verify overview, weddings, quotes, and document downloads in the web browser.
