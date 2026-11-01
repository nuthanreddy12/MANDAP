import json
from backend.services.schedule_recovery import ScheduleRecoveryEngine
import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()
c.execute("SELECT id, title, start_time, end_time, is_locked, vendor_name, vendor_arrival_status, delay_minutes FROM timeline_events WHERE wedding_id = 'w1' ORDER BY start_time ASC")
rows = c.fetchall()
events = [
    {
        "id": r[0],
        "title": r[1],
        "start_time": r[2],
        "end_time": r[3],
        "is_locked": bool(r[4]),
        "vendor_name": r[5],
        "vendor_arrival_status": r[6],
        "delay_minutes": r[7]
    }
    for r in rows
]
conn.close()

res = ScheduleRecoveryEngine.calculate_recovery(
    events=events,
    incident_event_id="te_dj_arrival",
    vendor_name="DJ Ronak",
    delay_minutes=30
)
print("Recovery result:")
print(json.dumps(res, indent=2))

