import requests
import json

BASE_URL = "http://127.0.0.1:8001"

# 1. Login as Finance Manager (Kavita)
login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "rhea@theroyalknot.in", "password": "Password123!"})

token = login_res.json()["token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("1. Authenticated as Finance Manager successfully.")

# 2. Get initial overview and invoices
overview_res = requests.get(f"{BASE_URL}/api/v1/finance/overview?wedding_id=w1", headers=headers)
overview = overview_res.json()
print("\nInitial Overview:")
print(f"Total Contracted PO: INR {overview['agreed_value']:,.2f}")
print(f"Billed Invoices: INR {overview['invoice_total']:,.2f}")
print(f"Disbursed Payments: INR {overview['paid_amount']:,.2f}")
print(f"Balance Payable: INR {overview['balance_payable']:,.2f}")

inv_res = requests.get(f"{BASE_URL}/api/v1/finance/invoices?wedding_id=w1", headers=headers)
invoices = inv_res.json()
print(f"\nInvoices count: {len(invoices)}")
rr_inv = next(i for i in invoices if "Royal Rajputana" in i["vendor_name"])
print("Royal Rajputana Initial:")
print(f"Invoice Total: INR {rr_inv['invoice_total']:,.2f}")
print(f"Paid Amount: INR {rr_inv['paid_amount']:,.2f}")
print(f"Remaining Balance: INR {rr_inv['remaining_balance']:,.2f}")
print(f"Payment Status: {rr_inv.get('payment_status')}")
print(f"Payment Pct: {rr_inv.get('payment_percentage')}%")

# 3. Record a payment of INR 100,000 for Royal Rajputana linked to invoice_id
payment_payload = {
    "wedding_id": "w1",
    "invoice_id": rr_inv["id"],
    "vendor_id": rr_inv["vendor_id"],
    "vendor_name": rr_inv["vendor_name"],
    "payment_stage": "second_payment",
    "amount": 100000.0,
    "payment_date": "01 Nov 2026",
    "reference": "NEFT-VERIFY-99281",
}
pay_res = requests.post(f"{BASE_URL}/api/v1/finance/payments?wedding_id=w1", headers=headers, json=payment_payload)
assert pay_res.status_code == 201, f"Failed to record payment: {pay_res.text}"
recorded_payment = pay_res.json()
print(f"\nPayment recorded successfully! Payment ID: {recorded_payment.get('id')}")

# 4. Re-fetch Invoices and verify Royal Rajputana updated
inv_res_after = requests.get(f"{BASE_URL}/api/v1/finance/invoices?wedding_id=w1", headers=headers)
invoices_after = inv_res_after.json()
rr_after = next(i for i in invoices_after if i["id"] == rr_inv["id"])
print("\nRoyal Rajputana After Payment:")
print(f"Invoice Total: INR {rr_after['invoice_total']:,.2f}")
print(f"Paid Amount: INR {rr_after['paid_amount']:,.2f}")
print(f"Remaining Balance: INR {rr_after['remaining_balance']:,.2f}")
print(f"Payment Status: {rr_after.get('payment_status')}")
print(f"Payment Pct: {rr_after.get('payment_percentage')}%")

expected_paid = rr_inv["paid_amount"] + 100000.0
assert abs(rr_after["paid_amount"] - expected_paid) < 0.01, f"Expected {expected_paid}, got {rr_after['paid_amount']}"
expected_balance = rr_inv["invoice_total"] - expected_paid
assert abs(rr_after["remaining_balance"] - expected_balance) < 0.01, f"Expected {expected_balance}, got {rr_after['remaining_balance']}"

# 5. Re-fetch Overview and verify live synchronization
overview_res_after = requests.get(f"{BASE_URL}/api/v1/finance/overview?wedding_id=w1", headers=headers)
overview_after = overview_res_after.json()
print("\nOverview After Payment:")
print(f"Total Contracted PO: INR {overview_after['agreed_value']:,.2f}")
print(f"Billed Invoices: INR {overview_after['invoice_total']:,.2f}")
print(f"Disbursed Payments: INR {overview_after['paid_amount']:,.2f}")
print(f"Balance Payable: INR {overview_after['balance_payable']:,.2f}")

assert abs(overview_after["paid_amount"] - (overview["paid_amount"] + 100000.0)) < 0.01
assert abs(overview_after["balance_payable"] - (overview["balance_payable"] - 100000.0)) < 0.01

# 6. Check 3-Way Reconciliation endpoint
rec_res = requests.get(f"{BASE_URL}/api/v1/finance/invoices/{rr_inv['id']}/reconciliation?wedding_id=w1", headers=headers)
rec_data = rec_res.json()
print("\nReconciliation Card C Values:")
print(f"Reconciliation Paid Amount: INR {rec_data['paid_amount']:,.2f}")
print(f"Reconciliation Remaining Balance: INR {rec_data['remaining_balance']:,.2f}")
assert abs(rec_data["paid_amount"] - expected_paid) < 0.01
assert abs(rec_data["remaining_balance"] - expected_balance) < 0.01

# 7. Clean up the test payment to restore pristine baseline
import sqlite3
conn = sqlite3.connect("mandap.db")
c = conn.cursor()
c.execute("DELETE FROM payments WHERE reference = 'NEFT-VERIFY-99281'")
# Re-sync invoice paid amount
c.execute("UPDATE invoices SET paid_amount = 551178 WHERE id = 'inv_rr_demo'")
c.execute("UPDATE financial_reconciliations SET paid_amount = 551178 WHERE invoice_id = 'inv_rr_demo'")
conn.commit()
conn.close()

# Re-check baseline after cleanup
inv_res_clean = requests.get(f"{BASE_URL}/api/v1/finance/invoices?wedding_id=w1", headers=headers)
rr_clean = next(i for i in inv_res_clean.json() if i["id"] == rr_inv["id"])
print("\nRestored Clean Baseline:")
print(f"Royal Rajputana Paid: INR {rr_clean['paid_amount']:,.2f}")
print(f"Royal Rajputana Balance: INR {rr_clean['remaining_balance']:,.2f}")

print("\nALL FINANCIAL PAYMENT AND STATUS SYNCHRONIZATION TESTS PASSED!")
