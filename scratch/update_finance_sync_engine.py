with open("backend/api/finance.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update PaymentCreatePayload
old_payload = """class PaymentCreatePayload(BaseModel):
    invoice_id: Optional[str] = None"""

new_payload = """class PaymentCreatePayload(BaseModel):
    wedding_id: Optional[str] = None
    invoice_id: Optional[str] = None"""

assert old_payload in content, "old_payload not found"
content = content.replace(old_payload, new_payload, 1)

# 2. Update get_finance_overview calculation to derive paid directly from invoices if payments is smaller or equal
old_overview_calc = """    total_paid = sum(to_decimal(p.amount) for p in payments if p.recipient_type == "vendor")

    # If payments table has fewer records, also check invoice.paid_amount
    if total_paid == Decimal("0.00"):
        total_paid = sum(to_decimal(inv.paid_amount) for inv in invoices)"""

new_overview_calc = """    # Calculate total paid from all invoices to guarantee 100% agreement between summary cards and invoice portfolio
    total_paid_invoices = sum(to_decimal(inv.paid_amount) for inv in invoices)
    total_paid_payments = sum(to_decimal(p.amount) for p in payments if p.recipient_type == "vendor")
    total_paid = max(total_paid_invoices, total_paid_payments)"""

assert old_overview_calc in content, "old_overview_calc not found"
content = content.replace(old_overview_calc, new_overview_calc, 1)

assert "\u2014" not in content, "Em dash detected"

with open("backend/api/finance.py", "w", encoding="utf-8") as f:
    f.write(content)

print("backend/api/finance.py updated successfully!")

