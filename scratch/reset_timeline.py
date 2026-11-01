import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

baseline = [
    ('te_dj_arrival', '07:00 PM', '07:30 PM', 'expected', 0),
    ('te_reception_entry', '07:30 PM', '08:15 PM', 'arrived', 0),
    ('te_dinner_banquet', '08:15 PM', '10:00 PM', 'arrived', 0),
    ('te_performances', '09:00 PM', '10:30 PM', 'expected', 0),
    ('te_closing_ceremony', '10:30 PM', '11:00 PM', 'expected', 0),
]

for tid, st, et, status, delay in baseline:
    c.execute(
        "UPDATE timeline_events SET start_time = ?, end_time = ?, vendor_arrival_status = ?, delay_minutes = ? WHERE id = ?",
        (st, et, status, delay, tid)
    )

conn.commit()
print("Baseline timeline restored!")
conn.close()

