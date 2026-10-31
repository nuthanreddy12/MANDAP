import os
import sqlite3
from pathlib import Path

SOURCE_DB = "mandap.db"
TARGET_DB = "backend/storage/backups/mandap_curated_staging.db"

AUTHENTIC_WEDDING_IDS = ("w1", "w2", "w3")
AUTHENTIC_USER_IDS = ("u1", "u2", "u3", "u4")
AUTHENTIC_VENDOR_IDS = ("v1", "v2", "v3", "v4", "v5", "v6", "v7", "v_audit_933f57")
AUTHENTIC_ENQUIRY_IDS = ("e1", "e2", "e3", "e4")
AUTHENTIC_QUOTE_IDS = ("q1", "q2", "q3", "q_audit_f8cfe9")

def build_curated_database():
    if os.path.exists(TARGET_DB):
        os.remove(TARGET_DB)

    src = sqlite3.connect(SOURCE_DB)
    tgt = sqlite3.connect(TARGET_DB)

    src_cur = src.cursor()
    tgt_cur = tgt.cursor()

    # 1. Recreate schema
    schema_dump = src_cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL").fetchall()
    for (sql_stmt,) in schema_dump:
        tgt_cur.execute(sql_stmt)
    tgt.commit()

    # 2. Populate curated records
    # Users (all 4)
    rows = src_cur.execute("SELECT * FROM users WHERE id IN ('u1', 'u2', 'u3', 'u4')").fetchall()
    tgt_cur.executemany("INSERT INTO users VALUES (?,?,?,?,?,?)", rows)

    # Enquiries (e1..e4)
    rows = src_cur.execute("SELECT * FROM enquiries WHERE id IN ('e1', 'e2', 'e3', 'e4')").fetchall()
    tgt_cur.executemany(f"INSERT INTO enquiries VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Weddings (w1, w2, w3)
    rows = src_cur.execute("SELECT * FROM weddings WHERE id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO weddings VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Vendors (v1..v7 + Royal Rajputana)
    rows = src_cur.execute("SELECT * FROM vendors WHERE id IN ('v1','v2','v3','v4','v5','v6','v7','v_audit_933f57')").fetchall()
    tgt_cur.executemany(f"INSERT INTO vendors VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Wedding Vendors (assignments for w1, w2, w3 with v1..v7)
    rows = src_cur.execute("SELECT * FROM wedding_vendors WHERE wedding_id IN ('w1', 'w2', 'w3') AND vendor_id IN ('v1','v2','v3','v4','v5','v6','v7','v_audit_933f57')").fetchall()
    tgt_cur.executemany(f"INSERT INTO wedding_vendors VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Tasks (tasks for w1, w2, w3)
    rows = src_cur.execute("SELECT * FROM tasks WHERE wedding_id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO tasks VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Quotes (q1, q2, q3, q_audit_f8cfe9)
    rows = src_cur.execute("SELECT * FROM quotes WHERE id IN ('q1', 'q2', 'q3', 'q_audit_f8cfe9')").fetchall()
    tgt_cur.executemany(f"INSERT INTO quotes VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Quote Items (items for q_audit_f8cfe9 and authentic quotes)
    rows = src_cur.execute("SELECT * FROM quote_items WHERE quote_id IN ('q1', 'q2', 'q3', 'q_audit_f8cfe9')").fetchall()
    if rows:
        tgt_cur.executemany(f"INSERT INTO quote_items VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Vendor Selections (Royal Rajputana selection)
    rows = src_cur.execute("SELECT * FROM vendor_selections WHERE quote_id = 'q_audit_f8cfe9'").fetchall()
    if rows:
        tgt_cur.executemany(f"INSERT INTO vendor_selections VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Quote Comparisons (1 catering comparison for w1)
    rows = src_cur.execute("SELECT * FROM quote_comparisons WHERE wedding_id = 'w1' ORDER BY created_at DESC LIMIT 1").fetchall()
    if rows:
        tgt_cur.executemany(f"INSERT INTO quote_comparisons VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Timeline Events (events for w1)
    rows = src_cur.execute("SELECT * FROM timeline_events WHERE wedding_id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO timeline_events VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Incidents (incidents for w1, w2, w3)
    rows = src_cur.execute("SELECT * FROM incidents WHERE wedding_id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO incidents VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Invoices (invoices for w1, w2, w3)
    rows = src_cur.execute("SELECT * FROM invoices WHERE wedding_id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO invoices VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # Payments (payments for w1, w2, w3)
    rows = src_cur.execute("SELECT * FROM payments WHERE wedding_id IN ('w1', 'w2', 'w3')").fetchall()
    tgt_cur.executemany(f"INSERT INTO payments VALUES ({','.join(['?']*len(rows[0]))})", rows)

    tgt.commit()

    # Integrity verification
    fk_errors = tgt_cur.execute("PRAGMA foreign_key_check").fetchall()
    print("Foreign Key Check Errors:", fk_errors)
    assert len(fk_errors) == 0, f"Foreign key check failed: {fk_errors}"

    tables = [r[0] for r in tgt_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    total_records = 0
    print(f"\n{'Table':25} | Count")
    print("-" * 35)
    for t in sorted(tables):
        cnt = tgt_cur.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        print(f"{t:25} | {cnt:5}")
        total_records += cnt

    print("-" * 35)
    print(f"{'Total Curated Records':25} | {total_records:5}")

    # Financial verification
    w_budget = tgt_cur.execute("SELECT sum(client_budget) FROM weddings").fetchone()[0] or 0.0
    q_total = tgt_cur.execute("SELECT sum(total_amount) FROM quotes").fetchone()[0] or 0.0
    inv_total = tgt_cur.execute("SELECT sum(invoice_total) FROM invoices").fetchone()[0] or 0.0
    inv_paid = tgt_cur.execute("SELECT sum(paid_amount) FROM invoices").fetchone()[0] or 0.0
    pay_total = tgt_cur.execute("SELECT sum(amount) FROM payments").fetchone()[0] or 0.0

    print("\n--- CURATED FINANCIAL TOTALS ---")
    print(f"Weddings Client Budget:  INR {w_budget:,.2f}")
    print(f"Quotes Total Amount:     INR {q_total:,.2f}")
    print(f"Invoices Total:          INR {inv_total:,.2f}")
    print(f"Invoices Paid:           INR {inv_paid:,.2f}")
    print(f"Payments Total:          INR {pay_total:,.2f}")

    src.close()
    tgt.close()

if __name__ == "__main__":
    build_curated_database()
