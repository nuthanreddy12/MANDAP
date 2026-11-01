import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

# 1. Update invoices
c.execute("UPDATE invoices SET paid_amount = 1102000 WHERE id = 'inv1'")
c.execute("UPDATE invoices SET paid_amount = 1062000 WHERE id = 'inv_virasat_decor_clean'")
c.execute("UPDATE invoices SET paid_amount = 551178 WHERE id = 'inv_rr_demo'")

# 2. Update financial_reconciliations
c.execute("UPDATE financial_reconciliations SET paid_amount = 1102000 WHERE invoice_id = 'inv1'")
c.execute("UPDATE financial_reconciliations SET paid_amount = 1062000 WHERE invoice_id = 'inv_virasat_decor_clean'")
c.execute("UPDATE financial_reconciliations SET paid_amount = 551178 WHERE invoice_id = 'inv_rr_demo'")

# 3. Clean payments for w1 and set clean canonical records
c.execute("DELETE FROM payments WHERE wedding_id = 'w1'")
c.execute("""
INSERT INTO payments (id, wedding_id, vendor_id, vendor_name, recipient_type, payment_stage, amount, payment_date, reference, status, recorded_by)
VALUES
('p_saffron_adv', 'w1', 'v_cat_1', 'Saffron Table Gourmet Catering Services', 'vendor', 'advance', 1102000, '15 Oct 2026', 'NEFT-884120', 'recorded', 'Finance Manager'),
('p_virasat_adv', 'w1', 'v_dec_1', 'Virasat Mandap & Floral Scenography', 'vendor', 'advance', 1062000, '18 Oct 2026', 'RTGS-992140', 'recorded', 'Finance Manager'),
('p_rr_adv', 'w1', 'v_cat_2', 'Royal Rajputana Hospitality & Banquets Pvt. Ltd.', 'vendor', 'advance', 551178, '22 Oct 2026', 'NEFT-551178', 'recorded', 'Finance Manager')
""")

conn.commit()
conn.close()
print("Financial ledger baseline reset to exact canonical state!")

