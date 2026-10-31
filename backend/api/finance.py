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
    total_paid = sum(to_decimal(p.amount) for p in payments if p.recipient_type == "vendor")

    # If payments table has fewer records, also check invoice.paid_amount
    if total_paid == Decimal("0.00"):
        total_paid = sum(to_decimal(inv.paid_amount) for inv in invoices)

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

    return {
        "reconciliation_id": rec_record.id,
        "invoice_id": invoice.id,
        "status": rec_record.status,
        "summary": result,
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
        "discrepancies": rec.discrepancies,
        "ai_explanation": rec.ai_explanation,
        "reviewed_by": rec.reviewed_by,
        "reviewed_at": rec.reviewed_at.isoformat() if rec.reviewed_at else None,
        "review_notes": rec.review_notes,
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
