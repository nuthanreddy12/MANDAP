import sqlite3

conn = sqlite3.connect("mandap.db")
cur = conn.cursor()

print("=== QUOTES ===")
for r in cur.execute("SELECT id, wedding_id, vendor_id, vendor_name, category, total_amount, status, extraction_status, source_filename, document_id FROM quotes").fetchall():
    print(r)

print("\n=== QUOTE COMPARISONS ===")
for r in cur.execute("SELECT id, wedding_id, category, created_at FROM quote_comparisons").fetchall():
    print(r)

print("\n=== DOCUMENTS ===")
for r in cur.execute("SELECT id, wedding_id, filename, file_hash, storage_path, status FROM documents").fetchall():
    print(r)

print("\n=== AI JOBS ===")
for r in cur.execute("SELECT id, wedding_id, quote_id, job_type, status, created_at FROM ai_jobs").fetchall():
    print(r)

print("\n=== WEDDINGS ===")
for r in cur.execute("SELECT id, couple_names, dates, destination, assigned_planner FROM weddings").fetchall():
    print(r)

conn.close()
