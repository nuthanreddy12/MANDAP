import os
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.models import (
    Base,
    Wedding,
    Quote,
    Invoice,
    Payment,
    FinancialReconciliation,
    User,
)
from backend.services.financial_reconciliation import FinancialReconciliationEngine, to_decimal
from backend.core.database import run_schema_migrations

STAGE4_DB_PATH = "backend/storage/backups/mandap_demo_stage4.db"

def test_stage4_database_financial_reconciliation_workflow():
    """Verify financial reconciliation executes deterministically against mandap_demo_stage4.db."""
    assert os.path.exists(STAGE4_DB_PATH), f"Stage 4 database missing: {STAGE4_DB_PATH}"

    engine = create_engine(f"sqlite:///{STAGE4_DB_PATH}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Wedding w1 exists
        wedding = db.query(Wedding).filter(Wedding.id == "w1").first()
        assert wedding is not None
        assert wedding.couple_names == "Mehra × Kapoor"

        # 2. Approved Royal Rajputana Quote exists
        quote = (
            db.query(Quote)
            .filter(Quote.wedding_id == "w1")
            .filter(Quote.vendor_name == "Royal Rajputana Hospitality & Banquets Pvt. Ltd.")
            .first()
        )
        assert quote is not None
        assert float(quote.total_amount) == 1837260.0
        assert len(quote.items) >= 4

        # 3. Seed synthetic invoice with unapproved ₹45,000 surcharge
        db.query(Invoice).filter(Invoice.wedding_id == "w1", Invoice.invoice_number == "INV-RR-8821").delete()
        db.query(FinancialReconciliation).filter(FinancialReconciliation.wedding_id == "w1").delete()
        db.flush()

        line_items = [
            {
                "original_description": "Royal Rajasthani Imperial Dinner Buffet (Live kitchen, silver chafers)",
                "quantity": 420,
                "unit_price": 2850.0,
                "line_total": 1197000.0,
            },
            {
                "original_description": "Live Chaat & Jodhpur Street Food Counter (12 varieties)",
                "quantity": 420,
                "unit_price": 350.0,
                "line_total": 147000.0,
            },
            {
                "original_description": "Artisan Royal Dessert & Traditional Mithai Display (Ghewar, Malpua)",
                "quantity": 420,
                "unit_price": 250.0,
                "line_total": 105000.0,
            },
            {
                "original_description": "Welcome Beverage & Handcrafted Mocktail Station",
                "quantity": 420,
                "unit_price": 150.0,
                "line_total": 63000.0,
            },
            {
                "original_description": "Dedicated 62.5 kVA Silent Acoustic Sound & Power Generator (Contracted)",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
            {
                "original_description": "Unapproved Midnight Sound & Generator Extended Overtime",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
            {
                "original_description": "Goods & Services Tax (18% GST)",
                "quantity": 1,
                "unit_price": 288360.0,
                "line_total": 288360.0,
            },
        ]

        inv = Invoice(
            id="inv_demo_stage4_rr",
            wedding_id="w1",
            vendor_id=quote.vendor_id,
            vendor_name=quote.vendor_name,
            category="catering",
            invoice_number="INV-RR-8821",
            invoice_date="18 Nov 2026",
            agreed_value=1837260.0,
            approved_extras=0.0,
            invoice_total=1890360.0,
            paid_amount=551178.0,
            status="review_required",
            source_filename="Royal_Rajputana_Final_Invoice_INV8821.pdf",
            discrepancy_note="Unapproved ₹45,000 overtime surcharge detected.",
            line_items=line_items,
        )
        db.add(inv)

        # Ensure payment record exists
        p = db.query(Payment).filter(Payment.id == "p_rr_advance").first()
        if not p:
            p = Payment(
                id="p_rr_advance",
                wedding_id="w1",
                vendor_id=quote.vendor_id,
                vendor_name=quote.vendor_name,
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

        # 4. Execute deterministic reconciliation
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
                for it in quote.items
            ],
        }

        inv_dict = {
            "vendor_name": inv.vendor_name,
            "invoice_number": inv.invoice_number,
            "agreed_value": float(inv.agreed_value),
            "approved_extras": float(inv.approved_extras),
            "invoice_total": float(inv.invoice_total),
            "paid_amount": float(inv.paid_amount),
            "line_items": inv.line_items,
        }

        reconciliation_result = FinancialReconciliationEngine.reconcile(
            invoice_data=inv_dict,
            approved_quote_data=quote_dict,
            payments=[{"amount": 551178.0, "payment_stage": "advance"}],
        )

        assert reconciliation_result["status"] == "review_required"
        assert reconciliation_result["requires_human_review"] is True
        assert reconciliation_result["unapproved_additional_total"] == 45000.0
        assert reconciliation_result["agreed_amount"] == 1837260.0
        assert reconciliation_result["invoice_total"] == 1890360.0
        assert reconciliation_result["total_variance"] == 53100.0  # 45000 + 18% GST (8100)
        assert reconciliation_result["total_paid"] == 551178.0
        assert reconciliation_result["remaining_balance"] == 1339182.0

        # Verify AI explanation was generated
        assert len(reconciliation_result["ai_explanation"]) > 20

        # 5. Persist reconciliation findings
        rec_model = FinancialReconciliation(
            id="rec_demo_stage4_rr",
            wedding_id="w1",
            invoice_id=inv.id,
            quote_id=quote.id,
            vendor_id=inv.vendor_id,
            vendor_name=inv.vendor_name,
            invoice_number=inv.invoice_number,
            status="review_required",
            agreed_amount=reconciliation_result["agreed_amount"],
            approved_extras=reconciliation_result["approved_extras"],
            invoice_amount=reconciliation_result["invoice_total"],
            paid_amount=reconciliation_result["total_paid"],
            variance_amount=reconciliation_result["total_variance"],
            discrepancies=reconciliation_result["discrepancies"],
            line_matches=reconciliation_result["line_matches"],
            ai_explanation=reconciliation_result["ai_explanation"],
        )
        db.add(rec_model)
        db.commit()

        # 6. Finance manager rejection decision
        rec_model.status = "rejected"
        rec_model.reviewed_by = "Finance Manager Kabir"
        rec_model.review_notes = "₹45,000 midnight overtime surcharge disallowed per contract Section 4."
        inv.status = "disputed"
        db.commit()

        # 7. Verify persisted record reflects decision
        saved = db.query(FinancialReconciliation).filter(FinancialReconciliation.id == "rec_demo_stage4_rr").first()
        assert saved.status == "rejected"
        assert "disallowed" in saved.review_notes

    finally:
        db.close()
