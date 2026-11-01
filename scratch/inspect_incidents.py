import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()
c.execute("SELECT id, wedding_id, title, status, delay_minutes, created_at FROM incidents WHERE wedding_id = 'w1'")
for r in c.fetchall():
    print(r)
conn.close()

