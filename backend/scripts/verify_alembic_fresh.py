import os
import shutil
import sqlite3
from pathlib import Path
from alembic.config import Config
from alembic import command

# 1. Fresh copy of Stage 2 database
src = Path("backend/storage/backups/mandap_demo_stage2.db")
test_db = Path("backend/storage/backups/mandap_test_migration.db")

if test_db.exists():
    test_db.unlink()

shutil.copy2(src, test_db)
print(f"Cloned fresh copy: {src} -> {test_db} ({test_db.stat().st_size} bytes)")

# Verify users table before migration
conn = sqlite3.connect(test_db)
c = conn.cursor()
c.execute("PRAGMA table_info(users)")
cols_before = [r[1] for r in c.fetchall()]
print("Users columns BEFORE migration:", cols_before)
assert "auth_user_id" not in cols_before

# Set alembic_version to base revision 0001
c.execute("DELETE FROM alembic_version")
c.execute("INSERT INTO alembic_version (version_num) VALUES ('0001_initial_mandap_schema')")
conn.commit()
conn.close()

# 2. Run Alembic upgrade head pointing to this fresh test database
db_uri = f"sqlite:///{test_db.resolve().as_posix()}"
os.environ["DATABASE_URL"] = db_uri
alembic_ini_path = Path("alembic.ini").resolve()
alembic_cfg = Config(str(alembic_ini_path))
alembic_cfg.set_main_option("sqlalchemy.url", db_uri)

print("Running Alembic upgrade to head on fresh Stage 2 copy...")
command.upgrade(alembic_cfg, "head")

# 3. Verify users table AFTER migration
conn = sqlite3.connect(test_db)
c = conn.cursor()
c.execute("PRAGMA table_info(users)")
cols_after = [r[1] for r in c.fetchall()]
print("Users columns AFTER migration:", cols_after)
assert "auth_user_id" in cols_after

c.execute("PRAGMA index_list(users)")
indexes = [r[1] for r in c.fetchall()]
print("Users indexes AFTER migration:", indexes)
assert any("auth_user_id" in idx for idx in indexes)

c.execute("SELECT version_num FROM alembic_version")
current_rev = c.fetchall()
print("Current Alembic revision:", current_rev)
assert current_rev == [("0002_add_auth_user_id_to_users",)]

conn.close()
print("ALEMBIC MIGRATION ON FRESH STAGE 2 COPY: SUCCESSFUL AND VERIFIED.")

# Clean up test database
if test_db.exists():
    test_db.unlink()
    print("Cleaned up temporary test database.")
