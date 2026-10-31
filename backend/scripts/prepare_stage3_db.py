import shutil
import sqlite3
from pathlib import Path

src = Path("backend/storage/backups/mandap_demo_stage2.db")
dst = Path("backend/storage/backups/mandap_demo_stage3.db")

shutil.copy2(src, dst)
print(f"Copied {src} to {dst}")

conn = sqlite3.connect(dst)
c = conn.cursor()

# Check if auth_user_id already exists
c.execute("PRAGMA table_info(users)")
cols = [r[1] for r in c.fetchall()]
if "auth_user_id" not in cols:
    c.execute("ALTER TABLE users ADD COLUMN auth_user_id VARCHAR")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_auth_user_id ON users (auth_user_id)")
    print("Added auth_user_id and unique index to users table.")

c.execute("DELETE FROM alembic_version")
c.execute("INSERT INTO alembic_version (version_num) VALUES ('0002_add_auth_user_id_to_users')")
conn.commit()

c.execute("PRAGMA table_info(users)")
print("Updated users cols:", [r[1] for r in c.fetchall()])
c.execute("SELECT * FROM alembic_version")
print("Alembic version in stage3 DB:", c.fetchall())

# Check total records in stage3 db
c.execute("SELECT count(*) FROM quotes")
print("Quotes count:", c.fetchone()[0])
c.execute("SELECT count(*) FROM documents")
print("Documents count:", c.fetchone()[0])
c.execute("SELECT count(*) FROM timeline_events")
print("Timeline events count:", c.fetchone()[0])

conn.close()
