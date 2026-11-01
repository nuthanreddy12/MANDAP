import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()
c.execute("PRAGMA table_info(users)")
for col in c.fetchall():
    print(col)
c.execute("SELECT * FROM users WHERE email = 'charanraghu38@gmail.com'")
print(c.fetchall())
conn.close()
