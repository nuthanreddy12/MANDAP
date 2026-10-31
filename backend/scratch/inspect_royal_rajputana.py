import sqlite3

c = sqlite3.connect("mandap.db")
cur = c.cursor()
print("=== ROYAL RAJPUTANA QUOTE DETAILS ===")
q = cur.execute("SELECT * FROM quotes WHERE id = 'q_audit_f8cfe9'").fetchone()
cols = [col[0] for col in cur.description]
for k, v in zip(cols, q):
    print(f"  {k}: {v}")

print("\n=== ITEMS FOR ROYAL RAJPUTANA QUOTE ===")
for r in cur.execute("SELECT * FROM quote_items WHERE quote_id = 'q_audit_f8cfe9'").fetchall():
    print(r)

print("\n=== VENDOR SELECTIONS FOR ROYAL RAJPUTANA ===")
for r in cur.execute("SELECT * FROM vendor_selections WHERE quote_id = 'q_audit_f8cfe9'").fetchall():
    print(r)

print("\n=== ALL VENDOR SELECTIONS ===")
for r in cur.execute("SELECT * FROM vendor_selections").fetchall():
    print(r)

c.close()
