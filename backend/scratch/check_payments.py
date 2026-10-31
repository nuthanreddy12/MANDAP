import sqlite3

conn = sqlite3.connect("backend/storage/backups/mandap_demo_stage5.db")
cur = conn.cursor()
cur.execute("SELECT id, recipient_type, payment_stage, amount, payment_date, reference, status FROM payments WHERE wedding_id='w1'")
rows = cur.fetchall()
print(f"Total payments for w1: {len(rows)}")
for r in rows:
    print(r)
conn.close()
