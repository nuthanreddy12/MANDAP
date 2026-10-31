import sqlite3

for db in ['backend/storage/backups/mandap_backup_20261031_154204.db', 'backend/storage/backups/mandap_backup_20261031_155135.db', 'mandap.db']:
    c = sqlite3.connect(db)
    q = c.execute("SELECT id FROM quotes WHERE id LIKE '%test%'").fetchall()
    qc = c.execute("SELECT id FROM quote_comparisons WHERE id LIKE '%test%'").fetchall()
    all_q = [r[0] for r in c.execute("SELECT id FROM quotes").fetchall()]
    all_qc = [r[0] for r in c.execute("SELECT id FROM quote_comparisons").fetchall()]
    print(db)
    print("  quotes with test:", q)
    print("  comparisons with test:", qc)
    print("  all quotes:", all_q)
    print("  all comparisons:", all_qc)
    c.close()
