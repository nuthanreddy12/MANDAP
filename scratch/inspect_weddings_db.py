import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()
c.execute("SELECT id, couple_names, venue, destination, dates, guest_count, client_budget, assigned_planner, health_status FROM weddings")
for r in c.fetchall():
    print(r)
conn.close()
