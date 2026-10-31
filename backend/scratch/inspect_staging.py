import sqlite3

conn = sqlite3.connect("backend/storage/backups/mandap_curated_staging.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables in mandap_curated_staging.db:")
counts = {}
for t in tables:
    if not t.startswith("sqlite") and not t.startswith("alembic"):
        c = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        counts[t] = c
print(counts)

print("\nWeddings in staging:")
for w in cur.execute("SELECT id, couple_names, guest_count, client_budget FROM weddings").fetchall():
    print("  Wedding:", w)

print("\nVendors in staging:")
for v in cur.execute("SELECT id, name, category FROM vendors").fetchall():
    print("  Vendor:", v)

print("\nQuotes in staging:")
for q in cur.execute("SELECT id, wedding_id, vendor_name, total_amount, status FROM quotes").fetchall():
    print("  Quote:", q)

conn.close()
