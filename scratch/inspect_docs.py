import sqlite3

conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("SELECT filename, count(*), min(id), max(id) FROM documents WHERE wedding_id='w1' GROUP BY filename")
for r in c.fetchall():
    print(r)

