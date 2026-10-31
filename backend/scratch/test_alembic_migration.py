import os
import shutil
import sqlite3
from alembic.config import Config
from alembic import command

# Isolated test database path
test_db_path = "backend/storage/backups/test_alembic_isolated.db"
if os.path.exists(test_db_path):
    os.remove(test_db_path)

# Build isolated alembic config pointing to test database
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

try:
    print("Testing upgrade to 0001...")
    command.upgrade(alembic_cfg, "0001_initial_mandap_schema")
    
    conn = sqlite3.connect(test_db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols_0001 = [row[1] for row in cur.fetchall()]
    print("0001 users columns:", cols_0001)
    assert "auth_user_id" not in cols_0001, "auth_user_id should not exist in 0001"
    conn.close()

    print("Testing upgrade to 0002_add_auth_user_id_to_users...")
    command.upgrade(alembic_cfg, "0002_add_auth_user_id_to_users")
    
    conn = sqlite3.connect(test_db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols_0002 = [row[1] for row in cur.fetchall()]
    print("0002 users columns:", cols_0002)
    assert "auth_user_id" in cols_0002, "auth_user_id must exist in 0002"
    
    cur.execute("PRAGMA index_list(users)")
    indexes = [row[1] for row in cur.fetchall()]
    print("0002 users indexes:", indexes)
    assert any("auth_user_id" in idx for idx in indexes), "Index on auth_user_id must exist"
    conn.close()

    print("Testing downgrade to 0001...")
    command.downgrade(alembic_cfg, "0001_initial_mandap_schema")
    conn = sqlite3.connect(test_db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols_downgrade = [row[1] for row in cur.fetchall()]
    print("Downgraded users columns:", cols_downgrade)
    conn.close()

    print("ALL ALEMBIC ISOLATED MIGRATION AND DOWNGRADE TESTS PASSED.")
finally:
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
