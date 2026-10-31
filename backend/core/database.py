from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings

# If using sqlite, add check_same_thread=False
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_schema_migrations(engine):
    """
    Ensures newly added columns are present in SQLite or PostgreSQL without losing existing seed data.
    """
    try:
        with engine.connect() as conn:
            if "sqlite" in engine.url.drivername:
                # Add auth_user_id to users if not present
                res_users = conn.execute(text("PRAGMA table_info(users)")).fetchall()
                if res_users:
                    existing_user_cols = {row[1] for row in res_users}
                    if "auth_user_id" not in existing_user_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN auth_user_id TEXT"))
                        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_auth_user_id ON users (auth_user_id)"))
                        conn.commit()

                res = conn.execute(text("PRAGMA table_info(quotes)")).fetchall()
                if res:
                    existing_cols = {row[1] for row in res}
                    cols_to_add = [
                        ("document_id", "TEXT"),
                        ("quotation_number", "TEXT"),
                        ("quotation_date", "TEXT"),
                        ("validity_date", "TEXT"),
                        ("currency", "TEXT DEFAULT 'INR'"),
                        ("subtotal", "NUMERIC(12,2)"),
                        ("tax_amount", "NUMERIC(12,2)"),
                        ("payment_terms", "TEXT"),
                        ("additional_charges", "JSON DEFAULT '[]'"),
                        ("extraction_status", "TEXT DEFAULT 'ready'"),
                        ("extraction_error", "TEXT"),
                        ("is_scanned", "BOOLEAN DEFAULT 0"),
                        ("human_verified", "BOOLEAN DEFAULT 0"),
                        ("raw_extracted_text", "TEXT"),
                    ]
                    for col_name, col_type in cols_to_add:
                        if col_name not in existing_cols:
                            conn.execute(text(f"ALTER TABLE quotes ADD COLUMN {col_name} {col_type}"))
                    conn.commit()

                # Weddings customer fields
                res_weddings = conn.execute(text("PRAGMA table_info(weddings)")).fetchall()
                if res_weddings:
                    existing_wedding_cols = {row[1] for row in res_weddings}
                    if "customer_user_id" not in existing_wedding_cols:
                        conn.execute(text("ALTER TABLE weddings ADD COLUMN customer_user_id TEXT"))
                    if "invitation_code" not in existing_wedding_cols:
                        conn.execute(text("ALTER TABLE weddings ADD COLUMN invitation_code TEXT"))
                    conn.commit()

                # Documents client sharing
                res_docs = conn.execute(text("PRAGMA table_info(documents)")).fetchall()
                if res_docs:
                    existing_doc_cols = {row[1] for row in res_docs}
                    if "is_shared_with_client" not in existing_doc_cols:
                        conn.execute(text("ALTER TABLE documents ADD COLUMN is_shared_with_client BOOLEAN DEFAULT 0"))
                    conn.commit()
    except Exception:
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
