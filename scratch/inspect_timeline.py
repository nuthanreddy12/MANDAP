import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()
c.execute("SELECT id, title, start_time, end_time, is_locked, vendor_name, vendor_arrival_status, delay_minutes FROM timeline_events WHERE wedding_id = 'w1' ORDER BY start_time ASC")
for r in c.fetchall():
    print(r)
conn.close()

