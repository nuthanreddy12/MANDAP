import sqlite3
conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("SELECT id, wedding_id, vendor_id, vendor_name, amount, payment_stage, reference FROM payments WHERE wedding_id='w1'")
rows = c.fetchall()
print(f"Payments count: {len(rows)}")
for r in rows:
    print(r)

print("\nInvoices:")
c.execute("SELECT id, invoice_number, vendor_id, vendor_name, invoice_total, paid_amount FROM invoices WHERE wedding_id='w1'")
for r in c.fetchall():
    print(r)

