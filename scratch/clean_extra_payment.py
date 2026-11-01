import sqlite3
conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("DELETE FROM payments WHERE id = 'p_9eaf7bab'")
c.execute("UPDATE invoices SET paid_amount = 1062000 WHERE id = 'inv_virasat_decor_clean'")
c.execute("UPDATE financial_reconciliations SET paid_amount = 1062000 WHERE invoice_id = 'inv_virasat_decor_clean'")
conn.commit()
conn.close()
print("Cleaned test payment p_9eaf7bab successfully!")

