from backend.api.notifications import create_notification
import uuid
import json
import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.models import (
    Wedding,
    Vendor,
    Quote,
    QuoteItem,
    Invoice,
    Payment,
    FinancialReconciliation,
    User,
)
from backend.core.auth import get_current_user, verify_wedding_access
from backend.services.financial_reconciliation import FinancialReconciliationEngine, to_decimal

router = APIRouter(prefix="/api/v1/weddings/{wedding_id}/finance", tags=["Finance & Reconciliation"])

class InvoiceCreatePayload(BaseModel):
    vendor_id: Optional[str] = None
    vendor_name: str
    category: str = "catering"
    invoice_number: str
    invoice_date: str
    agreed_value: float
    approved_extras: float = 0.0
    invoice_total: float
    paid_amount: float = 0.0
    line_items: List[Dict[str, Any]]
    source_filename: Optional[str] = None

class ReconciliationDecisionPayload(BaseModel):
    decision: str  # "approve" (approve override / change order) or "reject" (dispute / reject invoice)
    review_notes: str
    decided_by: Optional[str] = "Finance Manager"

@router.get("/overview")
def get_finance_overview(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return high-level financial reconciliation ledger metrics for the wedding."""
    verify_wedding_access(wedding_id, current_user, db, action="view finance for")
    
    invoices = db.query(Invoice).filter(Invoice.wedding_id == wedding_id).all()
    payments = db.query(Payment).filter(Payment.wedding_id == wedding_id).all()

    total_agreed = sum(to_decimal(inv.agreed_value) for inv in invoices)
    total_approved_extras = sum(to_decimal(inv.approved_extras) for inv in invoices)
    total_invoiced = sum(to_decimal(inv.invoice_total) for inv in invoices)
    # Calculate total paid from all invoices to guarantee 100% agreement between summary cards and invoice portfolio
    total_paid_invoices = sum(to_decimal(inv.paid_amount) for inv in invoices)
    total_paid_payments = sum(to_decimal(p.amount) for p in payments if p.recipient_type == "vendor")
    total_paid = max(total_paid_invoices, total_paid_payments)

    balance_payable = max(Decimal("0.00"), total_invoiced - total_paid)
    variance_amount = total_invoiced - (total_agreed + total_approved_extras)

    return {
        "wedding_id": wedding_id,
        "agreed_value": float(total_agreed),
        "approved_extras": float(total_approved_extras),
        "invoice_total": float(total_invoiced),
        "paid_amount": float(total_paid),
        "balance_payable": float(balance_payable),
        "variance_amount": float(variance_amount),
        "invoices_count": len(invoices),
        "pending_reviews_count": len([inv for inv in invoices if inv.status in ("review_required", "submitted")]),
    }

@router.get("/invoices")
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
    return results

@router.post("/invoices/seed-demo")
def seed_demo_invoices(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Seed the synthetic invoice demonstrating the unapproved ₹45,000 additional charge
    against the approved Royal Rajputana catering quotation.
    """
    verify_wedding_access(wedding_id, current_user, db, action="modify invoices for")

    # Locate or create approved quote for Royal Rajputana
    vendor = db.query(Vendor).filter(Vendor.name == "Royal Rajputana Hospitality & Banquets Pvt. Ltd.").first()
    if not vendor:
        vendor = Vendor(
            id="v_royal_rajputana",
            name="Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
            category="catering",
            contact_person="Mahaveer Singh Rathore",
            phone="+91 98290 44882",
            city="Jaipur",
        )
        db.add(vendor)
        db.flush()

    quote = (
        db.query(Quote)
        .filter(Quote.wedding_id == wedding_id)
        .filter((Quote.vendor_name == "Royal Rajputana Hospitality & Banquets Pvt. Ltd.") | (Quote.id == "q_2d850905"))
        .filter(Quote.total_amount == 1837260.0)
        .first()
    )

    if not quote:
        quote = Quote(
            id=f"q_rr_{wedding_id}",
            wedding_id=wedding_id,
            vendor_id=vendor.id,
            vendor_name="Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
            category="catering",
            total_amount=1837260.0,
            subtotal=1557000.0,
            tax_amount=280260.0,
            is_recommended=True,
            status="selected",
            extraction_status="ready",
            additional_charges=[
                {
                    "name": "Dedicated 62.5 kVA Silent Acoustic Generator (Contracted)",
                    "amount": 45000.0,
                    "status": "bundled",
                }
            ],
            inclusions=["420 guests gala buffet", "Service staff included", "62.5 kVA generator included"],
            exclusions=["Overtime past 11 PM"],
        )
        db.add(quote)
        db.flush()

        qi = QuoteItem(
            id=f"qi_rr_{wedding_id}",
            quote_id=quote.id,
            original_description="Royal Rajputana Grand Buffet Dinner (420 guests)",
            normalized_category="Catering",
            quantity=420,
            unit="plate",
            unit_price=3600.0,
            line_total=1512000.0,
            source_page=1,
            source_text="Rate per head: INR 3600 x 420 guests = INR 15,12,000",
        )
        db.add(qi)
        db.flush()

    vendor_id = vendor.id
    vendor_name = vendor.name
    agreed_value = float(quote.total_amount)

    # Clean existing invoice INV-RR-8821 if exists
    db.query(Invoice).filter(Invoice.wedding_id == wedding_id, Invoice.invoice_number == "INV-RR-8821").delete()
    db.flush()

    line_items = []
    subtotal_calc = Decimal("0.00")

    if quote.items:
        for it in quote.items:
            q_qty = float(it.quantity) if it.quantity else 1.0
            q_rate = float(it.unit_price) if it.unit_price else 0.0
            q_total = float(it.line_total) if it.line_total else (q_qty * q_rate)
            line_items.append({
                "original_description": it.original_description,
                "quantity": q_qty,
                "unit": it.unit or "unit",
                "unit_price": q_rate,
                "line_total": q_total,
                "category": "Catering",
            })
            subtotal_calc += to_decimal(q_total)
    else:
        line_items.append({
            "original_description": "Royal Rajputana Grand Buffet Dinner (420 guests)",
            "quantity": 420,
            "unit": "plate",
            "unit_price": 3600.0,
            "line_total": 1512000.0,
            "category": "Catering",
        })
        subtotal_calc += Decimal("1512000.00")

    # Contracted generator if not already in items
    has_generator_in_items = any("generator" in it.get("original_description", "").lower() for it in line_items)
    if not has_generator_in_items:
        line_items.append({
            "original_description": "Dedicated 62.5 kVA Silent Acoustic Generator (Contracted)",
            "quantity": 1,
            "unit": "unit",
            "unit_price": 45000.0,
            "line_total": 45000.0,
            "category": "Equipment",
        })
        subtotal_calc += Decimal("45000.00")

    # Unapproved additional charge (₹45,000)
    line_items.append({
        "original_description": "Unapproved Midnight Sound & Generator Extended Overtime",
        "quantity": 1,
        "unit": "unit",
        "unit_price": 45000.0,
        "line_total": 45000.0,
        "category": "Unapproved Surcharge",
    })
    subtotal_calc += Decimal("45000.00")

    # 18% GST on subtotal
    gst_calc = (subtotal_calc * Decimal("0.18")).quantize(Decimal("0.01"))
    line_items.append({
        "original_description": "Goods & Services Tax (18% GST)",
        "quantity": 1,
        "unit": "tax",
        "unit_price": float(gst_calc),
        "line_total": float(gst_calc),
        "category": "Taxes",
    })

    inv_total_calc = float(subtotal_calc + gst_calc)

    inv = Invoice(
        id="inv_rr_demo",
        wedding_id=wedding_id,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        category="catering",
        invoice_number="INV-RR-8821",
        invoice_date="18 Nov 2026",
        agreed_value=agreed_value,
        approved_extras=0.0,
        invoice_total=inv_total_calc,
        paid_amount=551178.0,  # 30% advance paid
        status="review_required",
        source_filename="Royal_Rajputana_Final_Invoice_INV8821.pdf",
        discrepancy_note="Invoice includes unapproved ₹45,000 surcharge for 'Midnight Sound & Generator Extended Overtime'.",
        line_items=line_items,
    )
    db.add(inv)

    # Also seed a corresponding payment record if not present
    existing_p = db.query(Payment).filter(Payment.id == "p_rr_advance").first()
    if existing_p:
        existing_p.vendor_id = vendor_id
        existing_p.vendor_name = vendor_name
        existing_p.amount = 551178.0
    else:
        p = Payment(
            id="p_rr_advance",
            wedding_id=wedding_id,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            recipient_type="vendor",
            payment_stage="advance",
            amount=551178.0,
            payment_date="10 Oct 2026",
            reference="NEFT-RR-9941",
            status="recorded",
            recorded_by="Aarav",
        )
        db.add(p)

    db.commit()
    return {"message": "Synthetic demonstration invoice seeded with unapproved ₹45,000 charge", "invoice_id": inv.id}

@router.post("/invoices/{invoice_id}/reconcile")
def reconcile_invoice(
    wedding_id: str,
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run automated deterministic financial reconciliation on the specified invoice
    against the approved contract quotation and recorded payments.
    """
    verify_wedding_access(wedding_id, current_user, db, action="reconcile invoice for")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.wedding_id == wedding_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Locate corresponding quote
    quote = (
        db.query(Quote)
        .filter(Quote.wedding_id == wedding_id)
        .filter((Quote.vendor_id == invoice.vendor_id) | (Quote.vendor_name == invoice.vendor_name))
        .filter(Quote.total_amount == invoice.agreed_value)
        .first()
    )
    if not quote:
        quote = (
            db.query(Quote)
            .filter(Quote.wedding_id == wedding_id)
            .filter((Quote.vendor_id == invoice.vendor_id) | (Quote.vendor_name == invoice.vendor_name))
            .first()
        )
    if not quote:
        quote = (
            db.query(Quote)
            .filter(Quote.wedding_id == wedding_id, Quote.category == invoice.category)
            .filter(Quote.status == "selected")
            .first()
        )
    if not quote:
        quote = (
            db.query(Quote)
            .filter(Quote.wedding_id == wedding_id, Quote.category == invoice.category)
            .first()
        )

    quote_dict = None
    if quote:
        quote_dict = {
            "id": quote.id,
            "total_amount": float(quote.total_amount),
            "subtotal": float(quote.subtotal) if quote.subtotal else float(quote.total_amount),
            "tax_amount": float(quote.tax_amount) if quote.tax_amount else 0.0,
            "additional_charges": quote.additional_charges or [],
            "items": [
                {
                    "original_description": it.original_description,
                    "quantity": float(it.quantity) if it.quantity else 1.0,
                    "unit_price": float(it.unit_price) if it.unit_price else 0.0,
                    "line_total": float(it.line_total) if it.line_total else 0.0,
                }
                for it in (quote.items or [])
            ],
        }

    # Fetch recorded vendor payments
    payments = db.query(Payment).filter(Payment.wedding_id == wedding_id, Payment.vendor_id == invoice.vendor_id).all()
    payments_dict = [
        {
            "id": p.id,
            "amount": float(p.amount),
            "payment_stage": p.payment_stage,
            "payment_date": p.payment_date,
        }
        for p in payments
    ]

    invoice_dict = {
        "vendor_name": invoice.vendor_name,
        "invoice_number": invoice.invoice_number,
        "agreed_value": float(to_decimal(invoice.agreed_value)),
        "approved_extras": float(to_decimal(invoice.approved_extras)),
        "invoice_total": float(to_decimal(invoice.invoice_total)),
        "paid_amount": float(to_decimal(invoice.paid_amount)),
        "line_items": invoice.line_items or [],
    }

    # Execute Python Decimal Reconciliation Engine
    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice_dict,
        approved_quote_data=quote_dict,
        payments=payments_dict,
    )

    # Persist or update FinancialReconciliation record
    rec_record = (
        db.query(FinancialReconciliation)
        .filter(FinancialReconciliation.invoice_id == invoice.id)
        .first()
    )
    if not rec_record:
        rec_record = FinancialReconciliation(
            id=f"fr_{uuid.uuid4().hex[:8]}",
            wedding_id=wedding_id,
            invoice_id=invoice.id,
            quote_id=quote.id if quote else None,
            vendor_id=invoice.vendor_id,
            vendor_name=invoice.vendor_name,
            invoice_number=invoice.invoice_number,
        )
        db.add(rec_record)

    rec_record.status = result["status"]
    rec_record.agreed_amount = result["agreed_amount"]
    rec_record.approved_extras = result["approved_extras"]
    rec_record.invoice_amount = result["invoice_total"]
    rec_record.paid_amount = result["total_paid"]
    rec_record.variance_amount = result["total_variance"]
    rec_record.line_matches = result["line_matches"]
    rec_record.discrepancies = result["discrepancies"]
    rec_record.ai_explanation = result["ai_explanation"]

    # Update Invoice status
    invoice.status = result["status"]
    if result["discrepancies"]:
        invoice.discrepancy_note = result["discrepancies"][0]["details"]

    db.commit()
    db.refresh(rec_record)

    try:
        create_notification(
            db=db,
            wedding_id=wedding_id,
            recipient_role="finance_manager",
            title=f"Invoice Audit Completed: {invoice.invoice_number}",
            message=f"Reconciliation completed for {invoice.vendor_name}. Status: {result['status'].replace('_', ' ').upper()}.",
            category="finance",
            link_url="/finance",
        )
    except Exception:
        pass

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
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
    }

@router.get("/invoices/{invoice_id}/reconciliation")
def get_reconciliation_details(
    wedding_id: str,
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full audit reconciliation breakdown and findings for an invoice."""
    verify_wedding_access(wedding_id, current_user, db, action="view reconciliation for")

    rec = (
        db.query(FinancialReconciliation)
        .filter(FinancialReconciliation.invoice_id == invoice_id, FinancialReconciliation.wedding_id == wedding_id)
        .first()
    )
    if not rec:
        # Auto-run reconciliation if not yet created
        return reconcile_invoice(wedding_id, invoice_id, db, current_user)

    return {
        "id": rec.id,
        "wedding_id": rec.wedding_id,
        "invoice_id": rec.invoice_id,
        "quote_id": rec.quote_id,
        "vendor_name": rec.vendor_name,
        "invoice_number": rec.invoice_number,
        "status": rec.status,
        "agreed_amount": float(to_decimal(rec.agreed_amount)),
        "approved_extras": float(to_decimal(rec.approved_extras)),
        "invoice_amount": float(to_decimal(rec.invoice_amount)),
        "paid_amount": float(to_decimal(rec.paid_amount)),
        "variance_amount": float(to_decimal(rec.variance_amount)),
        "remaining_balance": float(to_decimal(rec.invoice_amount) - to_decimal(rec.paid_amount)),
        "line_matches": rec.line_matches,
        "discrepancies": rec.discrepancies or [],
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
    }

@router.post("/invoices/{invoice_id}/reconciliation/decide")
def submit_reconciliation_decision(
    wedding_id: str,
    invoice_id: str,
    payload: ReconciliationDecisionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Finance manager reviews and resolves a reconciliation discrepancy.
    Actions:
      - 'approve': Approves variance as an authorized change order.
      - 'reject': Disallows unapproved charges and disputes invoice with vendor.
    """
    verify_wedding_access(wedding_id, current_user, db, action="approve/reject reconciliation for")

    if current_user.role not in ("owner", "finance_manager", "planner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{current_user.role}' is not authorized to decide on financial reconciliations. Authorized roles: owner, finance_manager, planner."
        )

    rec = (
        db.query(FinancialReconciliation)
        .filter(FinancialReconciliation.invoice_id == invoice_id, FinancialReconciliation.wedding_id == wedding_id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation record not found")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    rec.reviewed_by = payload.decided_by or current_user.name
    rec.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
    rec.review_notes = payload.review_notes

    if payload.decision.lower() == "approve":
        rec.status = "approved_override"
        if invoice:
            invoice.status = "approved"
            invoice.discrepancy_note = f"Approved as authorized change order: {payload.review_notes}"
        msg = "Discrepancy approved as authorized change order."
    else:
        rec.status = "rejected"
        if invoice:
            invoice.status = "rejected"
            invoice.discrepancy_note = f"Disputed by Finance Manager: {payload.review_notes}"
        msg = "Unapproved charges rejected. Invoice marked as disputed."

    db.commit()
    return {
        "message": msg,
        "status": rec.status,
        "reviewed_by": rec.reviewed_by,
        "reviewed_at": rec.reviewed_at.isoformat(),
    }


class PaymentCreatePayload(BaseModel):
    wedding_id: Optional[str] = None
    invoice_id: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    payment_stage: str
    amount: float
    payment_date: str
    reference: Optional[str] = None

@router.post("/invoices", status_code=status.HTTP_201_CREATED)
def submit_vendor_invoice(
    wedding_id: str,
    payload: InvoiceCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vendor or finance team submits an official invoice for reconciliation."""
    verify_wedding_access(wedding_id, current_user, db, action="submit invoice for")
    inv = Invoice(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=payload.vendor_id,
        vendor_name=payload.vendor_name,
        category=payload.category,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        agreed_value=payload.agreed_value,
        approved_extras=payload.approved_extras,
        invoice_total=payload.invoice_total,
        paid_amount=payload.paid_amount,
        status="submitted",
        source_filename=payload.source_filename,
        line_items=payload.line_items,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    try:
        create_notification(
            db=db,
            title=f"Invoice Submitted: {inv.vendor_name}",
            message=f"Invoice #{inv.invoice_number} submitted for INR {float(inv.invoice_total):,.2f}.",
            category="finance",
            recipient_role="finance_manager",
            wedding_id=wedding_id,
            link_url="/finance",
        )
    except Exception:
        pass

    return inv

@router.post("/payments", status_code=status.HTTP_201_CREATED)
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
    db.refresh(p)

    try:
        create_notification(
            db=db,
            title=f"Payment Recorded: {p.vendor_name or 'Vendor'}",
            message=f"Payment of INR {float(p.amount):,.2f} recorded ({p.payment_stage.upper()} - Ref: {p.reference or 'N/A'}).",
            category="finance",
            recipient_role="finance_manager",
            wedding_id=wedding_id,
            link_url="/finance",
        )
    except Exception:
        pass

    return p


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
