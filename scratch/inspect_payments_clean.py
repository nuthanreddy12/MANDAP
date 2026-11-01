import sqlite3
conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("SELECT id, vendor_id, vendor_name, recipient_type, amount, payment_stage, reference FROM payments WHERE wedding_id='w1'")
rows = c.fetchall()
print(f"Payments count: {len(rows)}")
vendor_sum = 0
for r in rows:
    print(r)
    if r[3] == "vendor":
        vendor_sum += r[4]
print(f"Vendor payments sum: {vendor_sum}")

