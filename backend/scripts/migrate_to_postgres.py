import os
import sys
import json
import argparse
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text, inspect, Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))

from backend.core.database import Base
import backend.models.models as models

MIGRATION_ORDER = [
    "users",
    "weddings",
    "vendors",
    "enquiries",
    "tasks",
    "timeline_events",
    "wedding_vendors",
    "documents",
    "quotes",
    "quote_items",
    "ai_jobs",
    "quote_comparisons",
    "vendor_selections",
    "incidents",
    "invoices",
    "payments",
]

MODEL_MAP = {
    "users": models.User,
    "weddings": models.Wedding,
    "vendors": models.Vendor,
    "enquiries": models.Enquiry,
    "tasks": models.Task,
    "timeline_events": models.TimelineEvent,
    "wedding_vendors": models.WeddingVendor,
    "documents": models.Document,
    "quotes": models.Quote,
    "quote_items": models.QuoteItem,
    "ai_jobs": models.AIJob,
    "quote_comparisons": models.QuoteComparison,
    "vendor_selections": models.VendorSelection,
    "incidents": models.Incident,
    "invoices": models.Invoice,
    "payments": models.Payment,
}

# Migration ledger table to guarantee idempotency and audit history
LedgerBase = declarative_base()

class MigrationLedger(LedgerBase):
    __tablename__ = "_mandap_migration_ledger"

    id = Column(String, primary_key=True)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    source_db = Column(String, nullable=False)
    total_records = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    table_stats = Column(JSON, default=dict)
    financial_stats = Column(JSON, default=dict)

def clean_record_for_model(model_cls, raw_dict):
    clean_dict = {}
    mapper = inspect(model_cls)
    
    for col in mapper.columns:
        col_name = col.name
        val = raw_dict.get(col_name)
        
        if val is None:
            clean_dict[col_name] = None
            continue
            
        col_type = col.type.python_type if hasattr(col.type, "python_type") else None
        
        if col_type is bool:
            clean_dict[col_name] = bool(val)
        elif str(col.type).startswith("JSON"):
            if isinstance(val, str):
                try:
                    clean_dict[col_name] = json.loads(val)
                except Exception:
                    clean_dict[col_name] = val
            else:
                clean_dict[col_name] = val
        elif col_type is datetime.datetime and isinstance(val, str):
            try:
                clean_dict[col_name] = datetime.datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                clean_dict[col_name] = val
        elif col_type is Decimal and isinstance(val, (int, float, str)):
            try:
                clean_dict[col_name] = Decimal(str(val))
            except Exception:
                clean_dict[col_name] = val
        else:
            clean_dict[col_name] = val
            
    return clean_dict

def run_migration(source_db_url=None, target_db_url=None, dry_run=True, target_schema=None):
    # Resolve exact absolute path for SQLite source
    if not source_db_url:
        source_db_url = "sqlite:///" + os.path.abspath("mandap.db")

    print("=" * 65)
    print("MANDAP PRODUCTION DATABASE MIGRATION ENGINE")
    print(f"Source DB: {source_db_url}")
    print(f"Target DB: {'[DRY RUN - Validation Only]' if dry_run else target_db_url.split('@')[-1] if '@' in str(target_db_url) else target_db_url}")
    if target_schema:
        print(f"Target Schema: {target_schema}")
    print(f"Mode: {'DRY RUN (Validation only)' if dry_run else 'LIVE PRODUCTION MIGRATION'}")
    print("=" * 65)
    
    src_engine = create_engine(source_db_url, connect_args={"check_same_thread": False})
    
    # Phase 1: Validate Source SQLite Records
    print("\nPhase 1: Validating Source SQLite Records & Schemas...")
    source_stats = {}
    total_source_records = 0
    validation_errors = []
    
    with src_engine.connect() as src_conn:
        for table_name in MIGRATION_ORDER:
            model_cls = MODEL_MAP[table_name]
            rows = src_conn.execute(text(f"SELECT * FROM {table_name}")).mappings().fetchall()
            source_stats[table_name] = len(rows)
            total_source_records += len(rows)
            
            for row_idx, r in enumerate(rows):
                try:
                    clean_dict = clean_record_for_model(model_cls, dict(r))
                    model_cls(**clean_dict)
                except Exception as ve:
                    validation_errors.append(f"{table_name} row {row_idx} ID {r.get('id')}: {ve}")
                    
            print(f"  Validated {table_name:<20}: {len(rows):>4} records")
            
        # Calculate source financial totals
        src_quotes_total = Decimal(str(src_conn.execute(text("SELECT ROUND(SUM(total_amount), 2) FROM quotes")).scalar() or 0))
        src_budget_total = Decimal(str(src_conn.execute(text("SELECT ROUND(SUM(client_budget), 2) FROM weddings")).scalar() or 0))
        src_payments_total = Decimal(str(src_conn.execute(text("SELECT ROUND(SUM(amount), 2) FROM payments")).scalar() or 0))
        src_qi_total = Decimal(str(src_conn.execute(text("SELECT ROUND(SUM(line_total), 2) FROM quote_items")).scalar() or 0))

    print(f"\nTotal source records: {total_source_records} across {len(MIGRATION_ORDER)} tables.")
    print(f"Source Financial Totals:")
    print(f"  - Quotes Total Amount: INR {src_quotes_total:,.2f}")
    print(f"  - Client Budget Total: INR {src_budget_total:,.2f}")
    print(f"  - Payments Total:      INR {src_payments_total:,.2f}")
    print(f"  - Quote Items Total:   INR {src_qi_total:,.2f}")
    
    if validation_errors:
        print(f"\nVALIDATION ERRORS FOUND ({len(validation_errors)}):")
        for err in validation_errors[:10]:
            print(f"  - {err}")
        src_engine.dispose()
        raise ValueError("Source record validation failed.")
    else:
        print("All records successfully passed schema and type validation.")
        
    if dry_run:
        print("\n[DRY RUN COMPLETE] Zero changes made to target database.")
        src_engine.dispose()
        return source_stats, {}

    # Phase 2: Connect Target & Check Overwrite / Duplicate Safeguards
    print("\nPhase 2: Verifying Target Database Safeguards...")
    target_connect_args = {}
    if "postgresql" in target_db_url and "sslmode" not in target_db_url:
        target_connect_args["sslmode"] = "require"
    if target_schema:
        target_connect_args["options"] = f"-c search_path={target_schema}"
    if "sqlite" in target_db_url:
        target_connect_args["check_same_thread"] = False
        
    target_engine = create_engine(target_db_url, connect_args=target_connect_args, echo=False)

    with target_engine.connect() as tgt_conn:
        if target_schema:
            tgt_conn.execute(text(f"SET search_path TO {target_schema}"))
            tgt_conn.commit()

        # Check Ledger table for previous completion
        inspector = inspect(target_engine)
        existing_tables = inspector.get_table_names(schema=target_schema) if target_schema else inspector.get_table_names()

        
        if "_mandap_migration_ledger" in existing_tables:
            completed = tgt_conn.execute(text(
                "SELECT id, applied_at, total_records FROM _mandap_migration_ledger WHERE status = 'completed'"
            )).mappings().first()
            if completed:
                tgt_conn.close()
                target_engine.dispose()
                src_engine.dispose()
                raise RuntimeError(
                    f"MIGRATION ABORTED: Ledger records an existing completed migration "
                    f"'{completed['id']}' on {completed['applied_at']} ({completed['total_records']} rows). "
                    f"To prevent duplicate records or accidental overwrite, migration will not re-run."
                )

        # Check existing tables for non-empty state
        non_empty_tables = []
        for t in MIGRATION_ORDER:
            if t in existing_tables:
                cnt = tgt_conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                if cnt > 0:
                    non_empty_tables.append((t, cnt))

        if non_empty_tables:
            tgt_conn.close()
            target_engine.dispose()
            src_engine.dispose()
            raise RuntimeError(
                f"MIGRATION ABORTED: Found existing records in target tables: {non_empty_tables}. "
                f"Insert-only migration requires target application tables to be empty."
            )

    print("Target safety checks passed: Target tables are empty and ledger is clear.")

    # Phase 3: Provision Schema & Ledger Table
    print("\nPhase 3: Provisioning Target Application Tables & Ledger...")
    Base.metadata.create_all(bind=target_engine)
    LedgerBase.metadata.create_all(bind=target_engine)
    print("Tables and migration ledger table provisioned successfully.")

    TargetSession = sessionmaker(bind=target_engine)
    target_session = TargetSession()
    target_stats = {}
    total_migrated_records = 0

    # Phase 4: Atomic Insert-Only Data Migration
    print("\nPhase 4: Migrating Data in Strict Topological Dependency Order...")
    try:
        with src_engine.connect() as src_conn:
            for table_name in MIGRATION_ORDER:
                model_cls = MODEL_MAP[table_name]
                rows = src_conn.execute(text(f"SELECT * FROM {table_name}")).mappings().fetchall()
                
                inserted_count = 0
                for r in rows:
                    clean_dict = clean_record_for_model(model_cls, dict(r))
                    # INSERT ONLY - do not use merge() to ensure no overwrites occur
                    obj = model_cls(**clean_dict)
                    target_session.add(obj)
                    inserted_count += 1
                    
                target_session.flush()
                target_stats[table_name] = inserted_count
                total_migrated_records += inserted_count
                print(f"  Flushed {table_name:<20}: {inserted_count:>4} records")

        # Phase 5: Pre-Commit Parity & Financial Reconciliation
        print("\nPhase 5: Pre-Commit Parity & Financial Reconciliation...")
        # Verify row counts
        count_mismatches = []
        for t in MIGRATION_ORDER:
            src_c = source_stats[t]
            tgt_c = target_session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            if src_c != tgt_c:
                count_mismatches.append((t, src_c, tgt_c))

        if count_mismatches:
            raise ValueError(f"Pre-commit row count mismatch: {count_mismatches}")

        # Verify financial totals
        tgt_quotes_total = Decimal(str(target_session.execute(text("SELECT ROUND(SUM(total_amount), 2) FROM quotes")).scalar() or 0))
        tgt_budget_total = Decimal(str(target_session.execute(text("SELECT ROUND(SUM(client_budget), 2) FROM weddings")).scalar() or 0))
        tgt_payments_total = Decimal(str(target_session.execute(text("SELECT ROUND(SUM(amount), 2) FROM payments")).scalar() or 0))
        tgt_qi_total = Decimal(str(target_session.execute(text("SELECT ROUND(SUM(line_total), 2) FROM quote_items")).scalar() or 0))

        financial_mismatches = []
        if src_quotes_total != tgt_quotes_total:
            financial_mismatches.append(f"Quotes total: {src_quotes_total} != {tgt_quotes_total}")
        if src_budget_total != tgt_budget_total:
            financial_mismatches.append(f"Budget total: {src_budget_total} != {tgt_budget_total}")
        if src_payments_total != tgt_payments_total:
            financial_mismatches.append(f"Payments total: {src_payments_total} != {tgt_payments_total}")
        if src_qi_total != tgt_qi_total:
            financial_mismatches.append(f"QuoteItems total: {src_qi_total} != {tgt_qi_total}")

        if financial_mismatches:
            raise ValueError(f"Pre-commit financial totals mismatch: {financial_mismatches}")

        print("  Row count parity: 100% MATCH across all 16 tables.")
        print("  Financial figures: 100% EXACT MATCH on Quotes, Budgets, Payments, and QuoteItems.")

        # Record Ledger Entry
        migration_id = f"mandap_mig_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        ledger_entry = MigrationLedger(
            id=migration_id,
            source_db=source_db_url,
            total_records=total_migrated_records,
            status="completed",
            table_stats=target_stats,
            financial_stats={
                "quotes_total": str(tgt_quotes_total),
                "budget_total": str(tgt_budget_total),
                "payments_total": str(tgt_payments_total),
                "quote_items_total": str(tgt_qi_total),
            }
        )
        target_session.add(ledger_entry)

        # Single atomic commit for entire migration and ledger
        target_session.commit()
        print(f"\nATOMIC COMMIT SUCCESSFUL. Migration recorded in ledger as '{migration_id}'.")

    except Exception as e:
        target_session.rollback()
        print(f"\nMIGRATION FAILED - Full rollback executed. Target DB remains clean: {e}")
        raise
    finally:
        target_session.close()
        target_engine.dispose()
        src_engine.dispose()

    return source_stats, target_stats

migrate_database = run_migration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MANDAP Production Migration Engine")
    parser.add_argument("--source", type=str, default=None, help="Path or URL to source SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run validation without writing to target")
    parser.add_argument("--test-local", action="store_true", help="Migrate to temporary local SQLite database to test ETL pipeline")
    parser.add_argument("--execute", action="store_true", help="Execute live migration against target PostgreSQL")
    
    args = parser.parse_args()
    
    if args.test_local:
        test_db_path = "backend/storage/test_target_migration.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        run_migration(
            source_db_url=args.source,
            target_db_url=f"sqlite:///{test_db_path}",
            dry_run=False
        )
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"Cleaned up temporary test target: {test_db_path}")
    elif args.execute:
        load_dotenv("backend/.env")
        target_url = os.getenv("SUPABASE_DATABASE_URL")
        if not target_url:
            print("ERROR: SUPABASE_DATABASE_URL not set in backend/.env")
            sys.exit(1)
        if target_url.startswith("postgresql://"):
            target_url = target_url.replace("postgresql://", "postgresql+psycopg://", 1)
        run_migration(
            source_db_url=args.source,
            target_db_url=target_url,
            dry_run=False
        )
    else:
        run_migration(
            source_db_url=args.source,
            dry_run=True
        )
