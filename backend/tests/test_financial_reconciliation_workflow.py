from decimal import Decimal
import pytest
from backend.services.financial_reconciliation import FinancialReconciliationEngine, to_decimal
from backend.models.models import Invoice, FinancialReconciliation, Payment, Quote

MOCK_APPROVED_QUOTE = {
    "id": "q_royal_rajputana",
    "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
    "total_amount": 1837260.0,
    "subtotal": 1557000.0,
    "tax_amount": 280260.0,
    "items": [
        {
            "original_description": "Royal Rajputana Grand Buffet Dinner",
            "quantity": 420.0,
            "unit_price": 3600.0,
            "line_total": 1512000.0,
        },
    ],
    "additional_charges": [
        {
            "name": "62.5 kVA Silent Acoustic Generator",
            "amount": 45000.0,
            "status": "bundled",
        }
    ],
}

def test_exact_invoice_match():
    """Verify exact invoice matching produces zero variance and matched status."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-MATCH-001",
        "agreed_value": 1837260.0,
        "invoice_total": 1837260.0,
        "paid_amount": 1837260.0,
        "line_items": [
            {
                "original_description": "Royal Rajputana Grand Buffet Dinner",
                "quantity": 420,
                "unit_price": 3600.0,
                "line_total": 1512000.0,
            },
            {
                "original_description": "62.5 kVA Silent Acoustic Generator",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
            {
                "original_description": "Goods & Services Tax (18% GST)",
                "quantity": 1,
                "unit_price": 280260.0,
                "line_total": 280260.0,
            },
        ],
    }

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
        payments=[{"amount": 1837260.0, "payment_stage": "final_settlement"}],
    )

    assert result["status"] == "matched"
    assert result["requires_human_review"] is False
    assert result["total_variance"] == 0.0
    assert result["unapproved_additional_total"] == 0.0
    assert "matches contractual quotation exactly" in result["ai_explanation"].lower() or "matched" in result["status"]

def test_price_mismatch():
    """Verify that billing above contracted unit rate triggers price_mismatch discrepancy."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-PRICE-ERR",
        "invoice_total": 1596000.0,
        "line_items": [
            {
                "original_description": "Royal Rajputana Grand Buffet Dinner",
                "quantity": 420,
                "unit_price": 3800.0,  # Contract rate is 3,600 (+200/plate)
                "line_total": 1596000.0,
            }
        ],
    }

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
    )

    assert result["requires_human_review"] is True
    price_discs = [d for d in result["discrepancies"] if d["type"] == "price_mismatch"]
    assert len(price_discs) >= 1
    assert price_discs[0]["agreed_rate"] == 3600.0
    assert price_discs[0]["invoiced_rate"] == 3800.0
    assert price_discs[0]["variance"] == 200.0

def test_quantity_mismatch():
    """Verify that billing for extra unapproved quantity triggers quantity_mismatch."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-QTY-ERR",
        "invoice_total": 1620000.0,
        "line_items": [
            {
                "original_description": "Royal Rajputana Grand Buffet Dinner",
                "quantity": 450,  # Contracted for 420 (+30 plates)
                "unit_price": 3600.0,
                "line_total": 1620000.0,
            }
        ],
    }

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
    )

    assert result["requires_human_review"] is True
    qty_discs = [d for d in result["discrepancies"] if d["type"] == "quantity_mismatch"]
    assert len(qty_discs) >= 1
    assert qty_discs[0]["agreed_quantity"] == 420.0
    assert qty_discs[0]["invoiced_quantity"] == 450.0
    assert qty_discs[0]["variance"] == 30.0

def test_duplicate_charge():
    """Verify duplicate line item billing is flagged."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-DUP-ERR",
        "invoice_total": 90000.0,
        "line_items": [
            {
                "original_description": "62.5 kVA Silent Acoustic Generator",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
            {
                "original_description": "62.5 kVA Silent Acoustic Generator",  # Duplicate billing
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
        ],
    }

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
    )

    dup_discs = [d for d in result["discrepancies"] if d["type"] == "duplicate_charge"]
    assert len(dup_discs) >= 1
    assert dup_discs[0]["invoiced_amount"] == 45000.0

def test_unapproved_additional_charge():
    """Verify synthetic scenario: unapproved ₹45,000 additional charge is identified and flagged."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-RR-8821",
        "agreed_value": 1837260.0,
        "invoice_total": 1890360.0,
        "paid_amount": 551178.0,
        "line_items": [
            {
                "original_description": "Royal Rajputana Grand Buffet Dinner",
                "quantity": 420,
                "unit_price": 3600.0,
                "line_total": 1512000.0,
            },
            {
                "original_description": "62.5 kVA Silent Acoustic Generator",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,
            },
            {
                "original_description": "Unapproved Midnight Sound & Generator Extended Overtime",
                "quantity": 1,
                "unit_price": 45000.0,
                "line_total": 45000.0,  # Unapproved ₹45,000 line item!
            },
        ],
    }

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
    )

    assert result["requires_human_review"] is True
    assert result["status"] == "review_required"
    assert result["unapproved_additional_total"] == 45000.0
    
    unapproved_discs = [d for d in result["discrepancies"] if d["type"] == "unapproved_additional_charge"]
    assert len(unapproved_discs) >= 1
    assert unapproved_discs[0]["invoiced_amount"] == 45000.0
    assert "Unapproved Midnight Sound" in unapproved_discs[0]["item_description"]

def test_partial_payment_calculation():
    """Verify remaining balance and partial payment status when payments are pending."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-PARTIAL",
        "agreed_value": 1837260.0,
        "invoice_total": 1837260.0,
        "paid_amount": 551178.0,  # 30% advance
        "line_items": [],
    }

    payments = [{"amount": 551178.0, "payment_stage": "advance"}]

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
        payments=payments,
    )

    partial_discs = [d for d in result["discrepancies"] if d["type"] == "partial_payment"]
    assert len(partial_discs) == 1
    assert partial_discs[0]["remaining_balance"] == 1286082.0
    assert result["remaining_balance"] == 1286082.0

def test_approved_change_order_match():
    """Verify that a formally approved change order matches and is NOT marked unapproved."""
    invoice = {
        "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        "invoice_number": "INV-CO-01",
        "agreed_value": 1837260.0,
        "invoice_total": 1879260.0,
        "line_items": [
            {
                "original_description": "Additional late-night dessert counter (Change Order #2)",
                "quantity": 1,
                "unit_price": 42000.0,
                "line_total": 42000.0,
            }
        ],
    }

    approved_cos = [
        {
            "description": "Additional late-night dessert counter (Change Order #2)",
            "amount": 42000.0,
            "status": "approved",
        }
    ]

    result = FinancialReconciliationEngine.reconcile(
        invoice_data=invoice,
        approved_quote_data=MOCK_APPROVED_QUOTE,
        approved_change_orders=approved_cos,
    )

    # Should be recognized as approved addition, not unapproved
    assert result["unapproved_additional_total"] == 0.0
    match_item = result["line_matches"][0]
    assert match_item["match_type"] == "approved_addition"
    assert match_item["status"] == "matched"

def test_api_reconciliation_workflow_and_rejection(client):
    """Test full API endpoint workflow: seed invoice -> reconcile -> reject discrepancy."""
    # 1. Seed demo invoice with unapproved ₹45,000 charge
    seed_res = client.post("/api/v1/weddings/w1/finance/invoices/seed-demo")
    assert seed_res.status_code == 200
    inv_id = seed_res.json()["invoice_id"]

    # 2. Reconcile the invoice
    rec_res = client.post(f"/api/v1/weddings/w1/finance/invoices/{inv_id}/reconcile")
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["status"] == "review_required"
    assert rec_data["summary"]["unapproved_additional_total"] == 45000.0

    # 3. Reject the unapproved finding (dispute invoice)
    decide_res = client.post(
        f"/api/v1/weddings/w1/finance/invoices/{inv_id}/reconciliation/decide",
        json={
            "decision": "reject",
            "review_notes": "₹45,000 overtime charge disallowed. Overtime was not pre-authorized by wedding planner.",
            "decided_by": "Finance Manager Kabir",
        }
    )
    assert decide_res.status_code == 200
    dec_data = decide_res.json()
    assert dec_data["status"] == "rejected"

    # 4. Verify persisted reconciliation details reflect rejection
    detail_res = client.get(f"/api/v1/weddings/w1/finance/invoices/{inv_id}/reconciliation")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["status"] == "rejected"
    assert "₹45,000 overtime charge disallowed" in detail_data["review_notes"]

def test_api_reconciliation_approval_override(client):
    """Test full API endpoint workflow: seed invoice -> reconcile -> approve override."""
    # 1. Seed demo invoice
    seed_res = client.post("/api/v1/weddings/w1/finance/invoices/seed-demo")
    assert seed_res.status_code == 200
    inv_id = seed_res.json()["invoice_id"]

    # 2. Reconcile
    rec_res = client.post(f"/api/v1/weddings/w1/finance/invoices/{inv_id}/reconcile")
    assert rec_res.status_code == 200

    # 3. Finance manager approves override as authorized change order
    decide_res = client.post(
        f"/api/v1/weddings/w1/finance/invoices/{inv_id}/reconciliation/decide",
        json={
            "decision": "approve",
            "review_notes": "Family approved extended acoustic sound buffer verbally on night of event.",
            "decided_by": "Finance Manager Kabir",
        }
    )
    assert decide_res.status_code == 200
    assert decide_res.json()["status"] == "approved_override"

    # 4. Verify invoice is now approved
    inv_list_res = client.get("/api/v1/weddings/w1/finance/invoices")
    assert inv_list_res.status_code == 200
    inv_match = next(i for i in inv_list_res.json() if i["id"] == inv_id)
    assert inv_match["status"] == "approved"
