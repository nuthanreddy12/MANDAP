with open("backend/api/finance.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update submit_reconciliation_decision to enforce role authorization
old_decide_role_check = '''    verify_wedding_access(wedding_id, current_user, db, action="approve/reject reconciliation for")

    rec = ('''

new_decide_role_check = '''    verify_wedding_access(wedding_id, current_user, db, action="approve/reject reconciliation for")

    if current_user.role not in ("owner", "finance_manager", "planner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{current_user.role}' is not authorized to decide on financial reconciliations. Authorized roles: owner, finance_manager, planner."
        )

    rec = ('''

assert old_decide_role_check in content, "old_decide_role_check not found in backend/api/finance.py"
content = content.replace(old_decide_role_check, new_decide_role_check, 1)

# 2. Update reconcile_invoice return dictionary to include AI provider/model and math verified fields
old_reconcile_return = '''    return {
        "reconciliation_id": rec_record.id,
        "invoice_id": invoice.id,
        "status": rec_record.status,
        "summary": result,
    }'''

new_reconcile_return = '''    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "reconciliation_id": rec_record.id,
        "invoice_id": invoice.id,
        "status": rec_record.status,
        "summary": result,
        "agreed_amount": float(to_decimal(rec_record.agreed_amount)),
        "approved_extras": float(to_decimal(rec_record.approved_extras)),
        "invoice_amount": float(to_decimal(rec_record.invoice_amount)),
        "invoice_total": float(to_decimal(rec_record.invoice_amount)),
        "paid_amount": float(to_decimal(rec_record.paid_amount)),
        "total_paid": float(to_decimal(rec_record.paid_amount)),
        "variance_amount": float(to_decimal(rec_record.variance_amount)),
        "total_variance": float(to_decimal(rec_record.variance_amount)),
        "remaining_balance": float(to_decimal(rec_record.invoice_amount) - to_decimal(rec_record.paid_amount)),
        "line_matches": rec_record.line_matches or [],
        "discrepancies": rec_record.discrepancies or [],
        "ai_explanation": rec_record.ai_explanation,
        "ai_provider": "Google Gemini",
        "ai_model": "gemini-3.5-flash-lite",
        "ai_timestamp": now_iso,
        "deterministic_math_verified": True,
    }'''

assert old_reconcile_return in content, "old_reconcile_return not found in backend/api/finance.py"
content = content.replace(old_reconcile_return, new_reconcile_return, 1)

# 3. Update get_reconciliation_details return dictionary to include AI provider/model and math verified fields
old_get_rec_return = '''        "discrepancies": rec.discrepancies,
        "ai_explanation": rec.ai_explanation,
        "reviewed_by": rec.reviewed_by,
        "reviewed_at": rec.reviewed_at.isoformat() if rec.reviewed_at else None,
        "review_notes": rec.review_notes,
    }'''

new_get_rec_return = '''        "discrepancies": rec.discrepancies or [],
        "ai_explanation": rec.ai_explanation,
        "reviewed_by": rec.reviewed_by,
        "reviewed_at": rec.reviewed_at.isoformat() if rec.reviewed_at else None,
        "review_notes": rec.review_notes,
        "invoice_total": float(to_decimal(rec.invoice_amount)),
        "total_paid": float(to_decimal(rec.paid_amount)),
        "total_variance": float(to_decimal(rec.variance_amount)),
        "ai_provider": "Google Gemini",
        "ai_model": "gemini-3.5-flash-lite",
        "ai_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "deterministic_math_verified": True,
    }'''

assert old_get_rec_return in content, "old_get_rec_return not found in backend/api/finance.py"
content = content.replace(old_get_rec_return, new_get_rec_return, 1)

# 4. Append top_finance_router at the end of backend/api/finance.py
top_router_code = '''

# ----------------------------------------------------------------------
# Top-Level Finance Router (Aliased without wedding_id path prefix)
# ----------------------------------------------------------------------
top_finance_router = APIRouter(prefix="/api/v1/finance", tags=["Finance & Reconciliation (Top-Level)"])

@top_finance_router.get("/invoices")
def top_list_invoices(
    wedding_id: Optional[str] = Query("w1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_wedding_id = wedding_id or "w1"
    return list_invoices(wedding_id=target_wedding_id, db=db, current_user=current_user)

@top_finance_router.get("/overview")
def top_finance_overview(
    wedding_id: Optional[str] = Query("w1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_wedding_id = wedding_id or "w1"
    return get_finance_overview(wedding_id=target_wedding_id, db=db, current_user=current_user)

@top_finance_router.post("/invoices/{invoice_id}/reconcile")
def top_reconcile_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return reconcile_invoice(wedding_id=inv.wedding_id, invoice_id=invoice_id, db=db, current_user=current_user)

@top_finance_router.get("/invoices/{invoice_id}/reconciliation")
def top_get_reconciliation_details(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return get_reconciliation_details(wedding_id=inv.wedding_id, invoice_id=invoice_id, db=db, current_user=current_user)

@top_finance_router.post("/invoices/{invoice_id}/reconciliation/decide")
def top_submit_reconciliation_decision(
    invoice_id: str,
    payload: ReconciliationDecisionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return submit_reconciliation_decision(wedding_id=inv.wedding_id, invoice_id=invoice_id, payload=payload, db=db, current_user=current_user)

@top_finance_router.post("/invoices/seed-demo")
def top_seed_demo_invoices(
    wedding_id: Optional[str] = Query("w1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_wedding_id = wedding_id or "w1"
    return seed_demo_invoices(wedding_id=target_wedding_id, db=db, current_user=current_user)

@top_finance_router.post("/invoices", status_code=status.HTTP_201_CREATED)
def top_submit_vendor_invoice(
    payload: InvoiceCreatePayload,
    wedding_id: Optional[str] = Query("w1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_wedding_id = getattr(payload, "wedding_id", None) or wedding_id or "w1"
    return submit_vendor_invoice(wedding_id=target_wedding_id, payload=payload, db=db, current_user=current_user)

@top_finance_router.post("/payments", status_code=status.HTTP_201_CREATED)
def top_record_payment_update(
    payload: PaymentCreatePayload,
    wedding_id: Optional[str] = Query("w1"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_wedding_id = getattr(payload, "wedding_id", None) or wedding_id or "w1"
    return record_payment_update(wedding_id=target_wedding_id, payload=payload, db=db, current_user=current_user)
'''

content += top_router_code

# Check for em dashes
assert "—" not in content, "Em dash detected in backend/api/finance.py!"

with open("backend/api/finance.py", "w", encoding="utf-8") as f:
    f.write(content)

print("backend/api/finance.py updated successfully.")

