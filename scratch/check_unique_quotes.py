import sqlite3

conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("SELECT id, wedding_id, vendor_name, source_filename, document_id FROM quotes WHERE source_filename LIKE '%unique%'")
rows = c.fetchall()
print("Matching quotes:", len(rows))
for r in rows:
    print(r)

