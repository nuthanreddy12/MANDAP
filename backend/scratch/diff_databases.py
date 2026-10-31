import sqlite3

def diff_records(db_old, db_new, label):
    c_old = sqlite3.connect(db_old)
    c_new = sqlite3.connect(db_new)
    
    cur_old = c_old.cursor()
    cur_new = c_new.cursor()
    
    tables = [r[0] for r in cur_new.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    print(f"\n=== DIFF: {label} ===")
    
    for t in sorted(tables):
        if t == "alembic_version": continue
        cols = [c[1] for c in cur_new.execute(f'PRAGMA table_info("{t}")').fetchall()]
        pk = cols[0] # assuming first col is id
        
        old_ids = set(r[0] for r in cur_old.execute(f'SELECT "{pk}" FROM "{t}"').fetchall())
        new_rows = cur_new.execute(f'SELECT * FROM "{t}"').fetchall()
        
        added = [r for r in new_rows if r[0] not in old_ids]
        if added:
            print(f"\nTable: {t} (+{len(added)} records):")
            for r in added:
                # print summary
                if t == 'tasks':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, title: {r[2]}, status: {r[4]}")
                elif t == 'weddings':
                    print(f"  ID: {r[0]}, couple: {r[2]}, dates: {r[6]}, created_at: {r[14] if len(r)>14 else 'N/A'}")
                elif t == 'quotes':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, vendor_name: {r[4]}, amount: {r[6]}")
                elif t == 'quote_items':
                    print(f"  ID: {r[0]}, quote_id: {r[1]}, desc: {r[2]}, total: {r[7]}")
                elif t == 'documents':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, filename: {r[3]}, hash: {r[5][:12]}...")
                elif t == 'ai_jobs':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, type: {r[3]}, status: {r[4]}")
                elif t == 'quote_comparisons':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, category: {r[2]}")
                elif t == 'enquiries':
                    print(f"  ID: {r[0]}, couple: {r[1]}, status: {r[10]}")
                elif t == 'vendors':
                    print(f"  ID: {r[0]}, name: {r[1]}, category: {r[2]}")
                elif t == 'wedding_vendors':
                    print(f"  ID: {r[0]}, wedding_id: {r[1]}, vendor_id: {r[2]}")
                else:
                    print(f"  {r}")
    c_old.close()
    c_new.close()

diff_records("backend/storage/backups/mandap_backup_20261031_154204.db", "backend/storage/backups/mandap_backup_20261031_155135.db", "440 -> 479 (+39)")
diff_records("backend/storage/backups/mandap_backup_20261031_155135.db", "mandap.db", "479 -> 518 (+39)")
