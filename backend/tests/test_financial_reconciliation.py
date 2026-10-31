import json
from pathlib import Path
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.models.models import (
    Base,
    Wedding,
    Vendor,
    Quote,
    QuoteItem,
    Document,
    AIJob,
    QuoteComparison,
    VendorSelection,
)
from backend.services.comparison_engine import compare_quotations

DEMO_DB_PATH = Path("backend/storage/backups/mandap_demo_stage2.db")
DEMO_QUOTES_DIR = Path("backend/storage/demo_quotes")

def test_ground_truth_reconciliation_math():
    """Verify that all 3 ground-truth JSON files satisfy exact decimal financial equality."""
    gt_files = [
        "royal_rajputana_ground_truth.json",
        "saffron_table_ground_truth.json",
        "heritage_mewar_ground_truth.json",
    ]
    
    for filename in gt_files:
        filepath = DEMO_QUOTES_DIR / filename
        assert filepath.exists(), f"Missing ground truth file: {filepath}"
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        base_subtotal = Decimal(str(data["subtotal"]))
        tax_amount = Decimal(str(data["tax_amount"]))
        grand_total = Decimal(str(data["grand_total"]))
        gst_rate = Decimal(str(data["gst_rate_percent"])) / Decimal("100")
        
        # Check additional charges
        addl_sum = sum(
            Decimal(str(r["line_total"]))
            for r in data.get("additional_charges_rows", [])
        )
        
        # In our accounting model: Taxable base = Base Subtotal + Taxable Additional Charges
        taxable_base = base_subtotal + addl_sum
        expected_gst = (taxable_base * gst_rate).quantize(Decimal("0.01"))
        
        assert tax_amount == expected_gst, (
            f"{filename}: Tax mismatch: expected {expected_gst}, got {tax_amount}"
        )
        assert taxable_base + tax_amount == grand_total, (
            f"{filename}: Grand total equation failed: {taxable_base} + {tax_amount} != {grand_total}"
        )

def test_royal_rajputana_generator_charge_tax_treatment():
    """Verify the ₹45,000 acoustic sound and generator charge is properly accounted and taxed at 18%."""
    with open(DEMO_QUOTES_DIR / "royal_rajputana_ground_truth.json", "r", encoding="utf-8") as f:
        rr = json.load(f)
        
    plate_subtotal = Decimal(str(rr["subtotal"]))  # 420 guests * 3600 = 1,512,000
    assert plate_subtotal == Decimal("1512000.00")
    
    gen_charge_row = next(r for r in rr["additional_charges_rows"] if "generator" in r["description"].lower())
    gen_charge = Decimal(str(gen_charge_row["line_total"]))
    assert gen_charge == Decimal("45000.00")
    
    taxable_subtotal = plate_subtotal + gen_charge
    assert taxable_subtotal == Decimal("1557000.00")
    
    cgst = (taxable_subtotal * Decimal("0.09")).quantize(Decimal("0.01"))
    sgst = (taxable_subtotal * Decimal("0.09")).quantize(Decimal("0.01"))
    total_tax = cgst + sgst
    assert total_tax == Decimal("280260.00")
    
    grand_total = taxable_subtotal + total_tax
    assert grand_total == Decimal("1837260.00")
    assert grand_total == Decimal(str(rr["grand_total"]))

def test_comparison_engine_deterministic_recommendation():
    """Verify that Python Decimal comparison engine recommends Royal Rajputana as best value."""
    # Create mock quotes matching the 3 demonstration vendors
    q1 = Quote(
        id="q_rr_test",
        wedding_id="w1",
        vendor_id="v_rr_test",
        vendor_name="Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
        category="catering",
        total_amount=1837260.0,
        subtotal=1557000.0,
        tax_amount=280260.0,
        price_per_unit=3600.0,
        guest_count_basis=420,
        taxes_detail="18% GST (9% CGST + 9% SGST)",
        payment_terms="30% booking advance, 50% 14 days prior, 20% on event completion",
        inclusions=["Staff included", "Generator included", "Chafing dishes", "Cutlery", "Menu tasting"],
        exclusions=["Liquor license", "Fireworks"],
        additional_charges=[{"name": "62.5 kVA Silent Acoustic Generator", "amount": 45000.0, "status": "taxable"}],
        status="complete",
    )
    
    q2 = Quote(
        id="q_st_test",
        wedding_id="w1",
        vendor_id="v_st_test",
        vendor_name="Saffron Table Gourmet Catering Services",
        category="catering",
        total_amount=1962340.0,
        subtotal=1663000.0,
        tax_amount=299340.0,
        price_per_unit=3900.0,
        guest_count_basis=420,
        taxes_detail="18% GST extra",
        payment_terms="50% booking deposit, 50% 7 days prior",
        inclusions=["Executive Chef", "Artisanal tableware", "Live stations"],
        exclusions=["Power generator excluded", "Waste disposal"],
        additional_charges=[{"name": "Refrigerated transport", "amount": 25000.0, "status": "taxable"}],
        status="complete",
    )
    
    q3 = Quote(
        id="q_hm_test",
        wedding_id="w1",
        vendor_id="v_hm_test",
        vendor_name="Heritage Mewar Culinary Arts",
        category="catering",
        total_amount=1623680.0,
        subtotal=1376000.0,
        tax_amount=247680.0,
        price_per_unit=3050.0,
        guest_count_basis=420,
        taxes_detail="18% GST extra",
        payment_terms="100% full advance before event date",
        inclusions=["Traditional copper buffet", "Turbaned servers"],
        exclusions=["Generator excluded", "Service staffing separate"],
        additional_charges=[
            {"name": "Staffing service fee", "amount": 60000.0, "status": "taxable"},
            {"name": "Logistics fee", "amount": 35000.0, "status": "taxable"},
        ],
        status="complete",
    )
    
    result = compare_quotations([q1, q2, q3], wedding_guest_count=420)
    insights = result["insights"]
    
    # 1. Heritage Mewar has lowest nominal quote
    assert insights["lowest_quoted_base"]["vendor_name"] == "Heritage Mewar Culinary Arts"
    assert insights["lowest_quoted_base"]["amount"] == 1623680.0
    
    # 2. But Royal Rajputana is recommended as best-value
    assert insights["recommended_vendor"] == "Royal Rajputana Hospitality & Banquets Pvt. Ltd."
    assert "best-value choice" in insights["recommendation_rationale"]
    assert "Score 90/100" in insights["recommendation_rationale"]
    
    # 3. Check matrix transparency scores
    scores = {m["vendor_name"]: m["transparency_score"] for m in result["matrix"]}
    assert scores["Royal Rajputana Hospitality & Banquets Pvt. Ltd."] == 90
    assert scores["Saffron Table Gourmet Catering Services"] == 75
    assert scores["Heritage Mewar Culinary Arts"] == 65
    assert scores["Royal Rajputana Hospitality & Banquets Pvt. Ltd."] > scores["Saffron Table Gourmet Catering Services"] > scores["Heritage Mewar Culinary Arts"]

def test_staging_database_foreign_key_and_record_integrity():
    """Verify record counts, relationships, and foreign key integrity in mandap_demo_stage2.db."""
    if not DEMO_DB_PATH.exists():
        pytest.skip("Demo database has not been populated yet.")
        
    engine = create_engine(f"sqlite:///{DEMO_DB_PATH}")
    with engine.connect() as conn:
        # FK integrity check in SQLite
        fk_violations = conn.execute(text("PRAGMA foreign_key_check")).fetchall()
        assert len(fk_violations) == 0, f"Foreign key violations found: {fk_violations}"
        
        # Verify 3 Documents exist for w1
        doc_count = conn.execute(text("SELECT count(*) FROM documents WHERE wedding_id = 'w1'")).scalar()
        assert doc_count >= 3
        
        # Verify 3 Catering Quotes exist for w1
        quote_count = conn.execute(text("SELECT count(*) FROM quotes WHERE wedding_id = 'w1' AND category = 'catering'")).scalar()
        assert quote_count >= 3
        
        # Verify QuoteItems exist and link to existing Quotes
        orphan_items = conn.execute(text(
            "SELECT count(*) FROM quote_items WHERE quote_id NOT IN (SELECT id FROM quotes)"
        )).scalar()
        assert orphan_items == 0
        
        # Verify AIJobs exist and completed
        ai_jobs = conn.execute(text(
            "SELECT count(*) FROM ai_jobs WHERE wedding_id = 'w1' AND status = 'completed'"
        )).scalar()
        assert ai_jobs >= 3
        
        # Verify QuoteComparison and VendorSelection
        qc_count = conn.execute(text("SELECT count(*) FROM quote_comparisons WHERE wedding_id = 'w1'")).scalar()
        assert qc_count >= 1
        
        vs = conn.execute(text("SELECT vendor_id, quote_id FROM vendor_selections WHERE wedding_id = 'w1'")).fetchall()
        assert len(vs) >= 1
        selected_vendor_id, selected_quote_id = vs[-1]
        
        # Selected vendor must be Royal Rajputana
        vendor_name = conn.execute(text("SELECT name FROM vendors WHERE id = :vid"), {"vid": selected_vendor_id}).scalar()
        assert "Royal Rajputana" in vendor_name
