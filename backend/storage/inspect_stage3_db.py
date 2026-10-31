import sqlite3

conn = sqlite3.connect("backend/storage/backups/mandap_demo_stage2.db")
c = conn.cursor()

c.execute("PRAGMA table_info(users)")
cols = [r[1] for r in c.fetchall()]
print("users cols:", cols)

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("tables:", tables)

for t in ["incidents", "events", "timeline_events", "schedule", "tasks"]:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        print(f"{t} cols:", [r[1] for r in c.fetchall()])
        c.execute(f"SELECT count(*) FROM {t}")
        print(f"{t} count:", c.fetchone()[0])

conn.close()
