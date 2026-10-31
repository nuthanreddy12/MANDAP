import sqlite3

databases = {
    "mandap.db": "mandap.db",
    "mandap_demo_stage4.db": "backend/storage/backups/mandap_demo_stage4.db",
    "mandap_demo_stage3.db": "backend/storage/backups/mandap_demo_stage3.db",
}

for name, path in databases.items():
    print(f"\n=================== Checking {name} ({path}) ===================")
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Tables present: {tables}")
    
    # Check wedding w1
    if "weddings" in tables:
        cur.execute("PRAGMA table_info(weddings)")
        cols = [r[1] for r in cur.fetchall()]
        print(f"Weddings columns: {cols}")
        
        cur.execute("SELECT id, couple_names, client_name, client_email, customer_user_id, invitation_code FROM weddings WHERE id='w1'")
        w1 = cur.fetchone()
        print(f"Wedding w1: {w1}")
        
        cur.execute("SELECT id, invitation_code FROM weddings WHERE invitation_code='ROYAL-MK-2026'")
        match = cur.fetchall()
        print(f"Weddings with ROYAL-MK-2026: {match}")
    
    # Check customer_invitations table
    if "customer_invitations" in tables:
        cur.execute("PRAGMA table_info(customer_invitations)")
        cols = [r[1] for r in cur.fetchall()]
        print(f"customer_invitations columns: {cols}")
        
        cur.execute("SELECT * FROM customer_invitations")
        invs = cur.fetchall()
        print(f"All customer_invitations: {invs}")
    else:
        print("customer_invitations table NOT PRESENT in this database!")

    conn.close()
