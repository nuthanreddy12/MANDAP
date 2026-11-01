with open("backend/api/finance.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update list_invoices
old_list_invoices = '''@router.get("/invoices")
def list_invoices(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all vendor invoices for the wedding."""
    verify_wedding_access(wedding_id, current_user, db, action="view invoices for")
    
    invoices = db.query(Invoice).filter(Invoice.wedding_id == wedding_id).order_by(Invoice.created_at.desc()).all()
    results = []
    for inv in invoices:
        results.append({
            "id": inv.id,
            "wedding_id": inv.wedding_id,
            "vendor_id": inv.vendor_id,
            "vendor_name": inv.vendor_name,
            "category": inv.category,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "agreed_value": float(to_decimal(inv.agreed_value)),
            "approved_extras": float(to_decimal(inv.approved_extras)),
            "invoice_total": float(to_decimal(inv.invoice_total)),
            "paid_amount": float(to_decimal(inv.paid_amount)),
            "remaining_balance": float(to_decimal(inv.invoice_total) - to_decimal(inv.paid_amount)),
            "status": inv.status,
            "source_filename": inv.source_filename,
            "discrepancy_note": inv.discrepancy_note,
            "line_items_count": len(inv.line_items or []),
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        })
    return results'''

new_list_invoices = '''@router.get("/invoices")
def list_invoices(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all vendor invoices for the wedding with live synchronized payments and status."""
    verify_wedding_access(wedding_id, current_user, db, action="view invoices for")
    
    invoices = db.query(Invoice).filter(Invoice.wedding_id == wedding_id).order_by(Invoice.created_at.desc()).all()
    all_payments = db.query(Payment).filter(Payment.wedding_id == wedding_id, Payment.recipient_type == "vendor").all()

    results = []
    for inv in invoices:
        inv_payments = [
            pm for pm in all_payments
            if (inv.vendor_id and pm.vendor_id == inv.vendor_id)
            or (pm.vendor_name and pm.vendor_name.lower().strip() == inv.vendor_name.lower().strip())
            or (pm.vendor_name and pm.vendor_name.lower().split()[0] in inv.vendor_name.lower())
        ]
        calc_paid = sum(to_decimal(pm.amount) for pm in inv_payments)
        if calc_paid == Decimal("0.00") and inv.paid_amount:
            calc_paid = to_decimal(inv.paid_amount)
        else:
            inv.paid_amount = float(calc_paid)

        total_dec = to_decimal(inv.invoice_total)
        rem_balance = max(Decimal("0.00"), total_dec - calc_paid)

        if calc_paid >= total_dec:
            payment_status = "paid"
        elif calc_paid > Decimal("0.00"):
            payment_status = "partially_paid"
        else:
            payment_status = "unpaid"

        pay_pct = float(round((calc_paid / total_dec) * 100, 1)) if total_dec > 0 else 0.0

        results.append({
            "id": inv.id,
            "wedding_id": inv.wedding_id,
            "vendor_id": inv.vendor_id,
            "vendor_name": inv.vendor_name,
            "category": inv.category,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "agreed_value": float(to_decimal(inv.agreed_value)),
            "approved_extras": float(to_decimal(inv.approved_extras)),
            "invoice_total": float(total_dec),
            "paid_amount": float(calc_paid),
            "remaining_balance": float(rem_balance),
            "payment_status": payment_status,
            "payment_percentage": pay_pct,
            "payments_count": len(inv_payments),
            "status": inv.status,
            "source_filename": inv.source_filename,
            "discrepancy_note": inv.discrepancy_note,
            "line_items_count": len(inv.line_items or []),
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        })
    db.commit()
    return results'''

assert old_list_invoices in content, "old_list_invoices not found"
content = content.replace(old_list_invoices, new_list_invoices, 1)

# 2. Update PaymentCreatePayload
old_payload = '''class PaymentCreatePayload(BaseModel):
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    payment_stage: str
    amount: float
    payment_date: str
    reference: Optional[str] = None'''

new_payload = '''class PaymentCreatePayload(BaseModel):
    invoice_id: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    payment_stage: str
    amount: float
    payment_date: str
    reference: Optional[str] = None'''

assert old_payload in content, "old_payload not found"
content = content.replace(old_payload, new_payload, 1)

# 3. Update record_payment_update
old_record = '''@router.post("/payments", status_code=status.HTTP_201_CREATED)
def record_payment_update(
    wedding_id: str,
    payload: PaymentCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a bank transfer or milestone advance payment against a wedding ledger."""
    verify_wedding_access(wedding_id, current_user, db, action="record payment for")
    p = Payment(
        id=f"p_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=payload.vendor_id,
        vendor_name=payload.vendor_name,
        recipient_type="vendor",
        payment_stage=payload.payment_stage,
        amount=payload.amount,
        payment_date=payload.payment_date,
        reference=payload.reference,
        status="recorded",
        recorded_by=current_user.name or "Finance Manager",
    )
    db.add(p)
    db.commit()
    db.refresh(p)'''

new_record = '''@router.post("/payments", status_code=status.HTTP_201_CREATED)
def record_payment_update(
    wedding_id: str,
    payload: PaymentCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a bank transfer or milestone advance payment against a wedding ledger."""
    verify_wedding_access(wedding_id, current_user, db, action="record payment for")

    # 1. Resolve target invoice and vendor
    target_invoice = None
    if payload.invoice_id:
        target_invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id, Invoice.wedding_id == wedding_id).first()

    resolved_vendor_id = payload.vendor_id
    resolved_vendor_name = payload.vendor_name

    if target_invoice:
        resolved_vendor_id = target_invoice.vendor_id or resolved_vendor_id
        resolved_vendor_name = target_invoice.vendor_name or resolved_vendor_name
    elif payload.vendor_id:
        inv = db.query(Invoice).filter(Invoice.wedding_id == wedding_id, Invoice.vendor_id == payload.vendor_id).first()
        if inv:
            target_invoice = inv
            resolved_vendor_name = inv.vendor_name
    elif payload.vendor_name:
        search_term = payload.vendor_name.strip()
        inv = db.query(Invoice).filter(
            Invoice.wedding_id == wedding_id,
            (Invoice.vendor_name.ilike(f"%{search_term}%")) |
            (Invoice.vendor_name.ilike(f"%{search_term.split()[0]}%"))
        ).first()
        if inv:
            target_invoice = inv
            resolved_vendor_id = inv.vendor_id
            resolved_vendor_name = inv.vendor_name

    p = Payment(
        id=f"p_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=resolved_vendor_id,
        vendor_name=resolved_vendor_name,
        recipient_type="vendor",
        payment_stage=payload.payment_stage,
        amount=payload.amount,
        payment_date=payload.payment_date,
        reference=payload.reference,
        status="recorded",
        recorded_by=current_user.name or "Finance Manager",
    )
    db.add(p)
    db.flush()

    # 2. Recalculate and synchronize total payments for this vendor / invoice
    target_invoices = []
    if target_invoice:
        target_invoices = [target_invoice]
    elif resolved_vendor_id or resolved_vendor_name:
        target_invoices = db.query(Invoice).filter(
            Invoice.wedding_id == wedding_id,
            (Invoice.vendor_id == resolved_vendor_id) | (Invoice.vendor_name == resolved_vendor_name)
        ).all()

    for inv in target_invoices:
        matching_payments = db.query(Payment).filter(
            Payment.wedding_id == wedding_id,
            Payment.recipient_type == "vendor",
            (Payment.vendor_id == inv.vendor_id) |
            (Payment.vendor_name == inv.vendor_name) |
            (Payment.vendor_id == resolved_vendor_id) |
            (Payment.vendor_name == resolved_vendor_name)
        ).all()
        calc_paid = sum(to_decimal(pm.amount) for pm in matching_payments)
        inv.paid_amount = float(calc_paid)

        rec = db.query(FinancialReconciliation).filter(FinancialReconciliation.invoice_id == inv.id).first()
        if rec:
            rec.paid_amount = float(calc_paid)

    db.commit()
    db.refresh(p)'''

assert old_record in content, "old_record not found"
content = content.replace(old_record, new_record, 1)

assert "—" not in content, "Em dash detected"

with open("backend/api/finance.py", "w", encoding="utf-8") as f:
    f.write(content)

print("backend/api/finance.py updated successfully.")
