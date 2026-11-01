import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

for table in ['tasks', 'quotes', 'documents', 'timeline_events', 'invoices', 'incidents']:
    print(f"\n--- {table} counts by wedding ---")
    c.execute(f"SELECT wedding_id, count(*) FROM {table} GROUP BY wedding_id")
    for r in c.fetchall():
        print(r)

conn.close()

