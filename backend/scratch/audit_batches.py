import sqlite3

c440 = sqlite3.connect("backend/storage/backups/mandap_backup_20261031_154204.db")
c479 = sqlite3.connect("backend/storage/backups/mandap_backup_20261031_155135.db")
c518 = sqlite3.connect("mandap.db")

def get_added_records(source_conn, target_conn):
    added_by_table = {}
    tables = [r[0] for r in target_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    for t in sorted(tables):
        if t == "alembic_version": continue
        cols = [c[1] for c in target_conn.execute(f'PRAGMA table_info("{t}")').fetchall()]
        pk = cols[0]
        src_ids = set(r[0] for r in source_conn.execute(f'SELECT "{pk}" FROM "{t}"').fetchall())
        tgt_rows = target_conn.execute(f'SELECT * FROM "{t}"').fetchall()
        added = [r for r in tgt_rows if r[0] not in src_ids]
        if added:
            added_by_table[t] = (cols, added)
    return added_by_table

batch1 = get_added_records(c440, c479)
batch2 = get_added_records(c479, c518)

print("=== BATCH 1 (440 -> 479: +39 records) ===")
total_b1 = 0
for t, (cols, rows) in batch1.items():
    print(f"Table {t}: {len(rows)} record(s)")
    total_b1 += len(rows)
    for r in rows:
        print(f"   PK: {r[0]} | {dict(zip(cols[:4], r[:4]))}")
print(f"Total Batch 1: {total_b1}")

print("\n=== BATCH 2 (479 -> 518: +39 records) ===")
total_b2 = 0
for t, (cols, rows) in batch2.items():
    print(f"Table {t}: {len(rows)} record(s)")
    total_b2 += len(rows)
    for r in rows:
        print(f"   PK: {r[0]} | {dict(zip(cols[:4], r[:4]))}")
print(f"Total Batch 2: {total_b2}")

c440.close()
c479.close()
c518.close()
