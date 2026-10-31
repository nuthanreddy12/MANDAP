import sqlite3

def get_financials(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Weddings client budget
    w_budget = cur.execute("SELECT sum(client_budget) FROM weddings").fetchone()[0] or 0.0
    
    # Quotes total amount
    q_total = cur.execute("SELECT sum(total_amount) FROM quotes WHERE total_amount IS NOT NULL").fetchone()[0] or 0.0
    
    # Invoices total and paid
    inv_total = cur.execute("SELECT sum(invoice_total) FROM invoices").fetchone()[0] or 0.0
    inv_paid = cur.execute("SELECT sum(paid_amount) FROM invoices").fetchone()[0] or 0.0
    
    # Payments total
    pay_total = cur.execute("SELECT sum(amount) FROM payments").fetchone()[0] or 0.0
    
    conn.close()
    return {
        "weddings_budget": w_budget,
        "quotes_total": q_total,
        "invoices_total": inv_total,
        "invoices_paid": inv_paid,
        "payments_total": pay_total,
    }

print("440 Financials:", get_financials("backend/storage/backups/mandap_backup_20261031_154204.db"))
print("479 Financials:", get_financials("backend/storage/backups/mandap_backup_20261031_155135.db"))
print("518 Financials:", get_financials("mandap.db"))
