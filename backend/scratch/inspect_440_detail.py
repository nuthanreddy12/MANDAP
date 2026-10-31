import sqlite3

c = sqlite3.connect("backend/storage/backups/mandap_backup_20261031_154204.db")
cur = c.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
print("=== 440-ROW BACKUP TABLES & COUNTS ===")
for t in sorted(tables):
    cnt = cur.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
    print(f"{t:25}: {cnt}")

print("\n=== WEDDINGS IN 440 ===")
for r in cur.execute("SELECT id, couple_names, dates, destination, assigned_planner FROM weddings").fetchall():
    print(r)

print("\n=== VENDORS IN 440 ===")
for r in cur.execute("SELECT id, name, category FROM vendors").fetchall():
    print(r)

print("\n=== ENQUIRIES IN 440 ===")
for r in cur.execute("SELECT id, couple_names, status FROM enquiries").fetchall():
    print(r)

c.close()
