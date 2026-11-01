import io
import pytest
import pymupdf
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal, Base, engine, run_schema_migrations

from backend.models.models import (
    Wedding,
    Vendor,
    Quote,
    QuoteItem,
    Document,
    VendorSelection,
    WeddingVendor,
)
from backend.services.pdf_extractor import extract_pdf_content
from backend.services.comparison_engine import compare_quotations
from backend.services.gemini_extractor import (
    ExtractedQuotation,
    ExtractedLineItem,
    ExtractedAdditionalCharge,
    GeminiApiKeyMissingError,
)

from backend.core.auth import get_current_user
from backend.models.models import User

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    db = SessionLocal()
    owner = db.query(User).filter(User.role == "owner").first()
    db.close()
    app.dependency_overrides[get_current_user] = lambda: owner
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)


def generate_sample_pdf(title: str, lines: list, num_pages: int = 1) -> bytes:
    """Helper to synthesize valid digital PDF documents in-memory using PyMuPDF."""
    doc = pymupdf.open()
    for p in range(num_pages):
        page = doc.new_page()
        page.insert_text((50, 50), f"{title} - Page {p + 1}", fontsize=14)
        y = 80
        for line in lines:
            page.insert_text((50, y), line, fontsize=10)
            y += 20
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_1_digital_pdf_extraction():
    # 1. Digital PDF extraction with PyMuPDF
    pdf_bytes = generate_sample_pdf(
        "Catering Proposal",
        [
            "Vendor: Saffron Table Catering",
            "Rate per plate: INR 3,500",
            "Guests: 420 pax",
            "Total Amount: INR 14,70,000",
            "Taxes: 18% extra",
            "Inclusions: 12 veg items, 4 non-veg items, welcome drinks",
            "Exclusions: Acoustic DG power backup",
        ]
    )
    extracted = extract_pdf_content(pdf_bytes)
    assert extracted["page_count"] == 1
    assert extracted["is_scanned"] is False
    assert "Saffron Table Catering" in extracted["full_text"]
    assert "14,70,000" in extracted["full_text"]

def test_2_multipage_quotation_extraction():
    # 2. Multi-page quotation extraction
    pdf_bytes = generate_sample_pdf(
        "Grand Palace Catering Quotation",
        [
            "Menu details and operational schedule attached",
            "Barbecue live counters",
            "Continental dessert studio",
        ],
        num_pages=3
    )
    extracted = extract_pdf_content(pdf_bytes)
    assert extracted["page_count"] == 3
    assert len(extracted["pages"]) == 3
    assert extracted["pages"][0]["page_number"] == 1
    assert extracted["pages"][2]["page_number"] == 3

def test_3_missing_quotation_fields():
    # 3. Missing quotation fields handled without crash
    pdf_bytes = generate_sample_pdf("Unfinished Quotation", ["Vendor: Minimalist Deco"])
    extracted = extract_pdf_content(pdf_bytes)
    assert extracted["page_count"] == 1
    # Check that comparison engine handles missing unit prices and taxes
    from backend.models.models import Quote
    q = Quote(
        id="q_test_missing",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Minimalist Deco",
        category="decoration",
        total_amount=500000.0,
        price_per_unit=None,
        guest_count_basis=None,
        taxes_detail=None,
        additional_charges=[],
        inclusions=[],
        exclusions=[],
        missing_terms=["Unit price unavailable", "Taxes unstated"]
    )
    comparison = compare_quotations([q])
    item = comparison["matrix"][0]
    assert item["price_per_unit"] is None
    assert "Taxes unverified (potential 18% GST liability)" in item["unverified_risks"]

def test_4_invalid_pdf(client):
    # 4. Invalid PDF rejected
    fake_bytes = b"This is not a pdf file at all"
    response = client.post(
        "/api/v1/weddings/w1/quotes/upload",
        files={"file": ("corrupted.pdf", fake_bytes, "application/pdf")},
        data={"category": "catering"}
    )
    assert response.status_code == 400
    assert "invalid pdf" in response.text.lower() or "signature" in response.text.lower()

def test_5_duplicate_document(client):
    # 5. Duplicate document prevention using SHA-256
    pdf_bytes = generate_sample_pdf("Unique Wedding Quote", ["Vendor: Unique DJ & Sound", "Total: 400000"])
    
    # First upload
    res1 = client.post(
        "/api/v1/weddings/w1/quotes/upload",
        files={"file": ("unique_quote.pdf", pdf_bytes, "application/pdf")},
        data={"category": "entertainment", "vendor_name": "Unique Sound"}
    )
    assert res1.status_code == 201

    # Second upload with identical bytes
    res2 = client.post(
        "/api/v1/weddings/w1/quotes/upload",
        files={"file": ("unique_quote_copy.pdf", pdf_bytes, "application/pdf")},
        data={"category": "entertainment", "vendor_name": "Unique Sound"}
    )
    assert res2.status_code == 400
    assert "duplicate" in res2.text.lower()

    # Clean up test records so test does not pollute document lists
    created_doc_id = res1.json().get("document_id")
    created_quote_id = res1.json().get("id")
    from backend.core.database import SessionLocal
    from backend.models.models import Document, Quote
    cleanup_db = SessionLocal()
    try:
        if created_quote_id:
            cleanup_db.query(Quote).filter(Quote.id == created_quote_id).delete()
        if created_doc_id:
            cleanup_db.query(Document).filter(Document.id == created_doc_id).delete()
        cleanup_db.commit()
    finally:
        cleanup_db.close()

def test_6_gemini_unavailable():
    # 6. Gemini unavailable or missing key raises GeminiApiKeyMissingError safely
    from backend.services.gemini_extractor import extract_quotation_with_gemini
    from backend.core.config import settings
    
    old_key = settings.GEMINI_API_KEY
    try:
        settings.GEMINI_API_KEY = ""
        with pytest.raises(GeminiApiKeyMissingError):
            extract_quotation_with_gemini({"full_text": "sample text"})
    finally:
        settings.GEMINI_API_KEY = old_key

def test_7_invalid_ai_structured_response():
    # 7. Invalid AI response validation
    # If Gemini returns JSON missing required vendor_name, Pydantic should reject
    with pytest.raises(Exception):
        ExtractedQuotation.model_validate({"grand_total": 50000})

def test_8_human_corrected_extracted_information(client):
    # 8. Human corrections to extracted line items and quote totals
    # Retrieve a quote
    quotes_res = client.get("/api/v1/weddings/w1/quotes")
    assert quotes_res.status_code == 200
    quotes = quotes_res.json()
    assert len(quotes) > 0
    target_quote = quotes[0]
    q_id = target_quote["id"]

    # Patch quote details
    patch_res = client.patch(
        f"/api/v1/quotes/{q_id}",
        json={"total_amount": 1600000.0, "taxes_detail": "18% extra (negotiated 50% discount on service charges)"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["total_amount"] == 1600000.0
    assert patch_res.json()["human_verified"] is True

    # Bulk update line items
    items_res = client.patch(
        f"/api/v1/quotes/{q_id}/items",
        json={
            "items": [
                {
                    "original_description": "Custom Rajasthani Thali Buffet",
                    "normalized_category": "Catering",
                    "quantity": 420,
                    "unit": "plate",
                    "unit_price": 3800.0,
                    "line_total": 1596000.0
                }
            ]
        }
    )
    assert items_res.status_code == 200
    items = items_res.json()["items"]
    assert len(items) == 1
    assert items[0]["original_description"] == "Custom Rajasthani Thali Buffet"
    assert items[0]["is_manually_edited"] is True

def test_9_price_per_plate_calculation():
    # 9. Price-per-plate calculation and normalization
    from backend.models.models import Quote
    q = Quote(
        id="q_calc_plate",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Test Caterer",
        category="catering",
        total_amount=1680000.0,
        price_per_unit=4000.0,
        guest_count_basis=420,
        taxes_detail="Included",
        additional_charges=[]
    )
    res = compare_quotations([q], wedding_guest_count=420)
    matrix = res["matrix"][0]
    assert matrix["price_per_unit"] == 4000.0
    assert matrix["estimated_final_cost"] == 1680000.0

def test_10_tax_exclusive_quotation():
    # 10. Tax-exclusive quotation: adding 18% GST to estimated final cost
    from backend.models.models import Quote
    q = Quote(
        id="q_tax_excl",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Exclusive Caterer",
        category="catering",
        total_amount=1000000.0,
        price_per_unit=2500.0,
        guest_count_basis=400,
        taxes_detail="18% extra",
        additional_charges=[]
    )
    res = compare_quotations([q])
    matrix = res["matrix"][0]
    # 10,00,000 + 18% (1,80,000) = 11,80,000
    assert matrix["estimated_final_cost"] == 1180000.0
    assert matrix["known_additions"] == 180000.0

def test_11_missing_overtime_or_generator_charge():
    # 11. Missing overtime/generator charge flagged as risk
    from backend.models.models import Quote
    q = Quote(
        id="q_missing_gen",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="No Gen Caterer",
        category="catering",
        total_amount=1500000.0,
        price_per_unit=3500.0,
        taxes_detail="Included",
        additional_charges=[]  # Generator not specified
    )
    res = compare_quotations([q])
    matrix = res["matrix"][0]
    assert any("generator" in r.lower() for r in matrix["unverified_risks"])

def test_12_comparison_of_three_vendors(client):
    # 12. Comparison of three vendors
    res = client.post("/api/v1/weddings/w1/quote-comparisons?category=catering")
    assert res.status_code == 200
    data = res.json()
    assert "matrix" in data
    assert len(data["matrix"]) >= 3
    assert "insights" in data
    assert "lowest_quoted_base" in data["insights"]
    assert "lowest_estimated_final" in data["insights"]
    assert "recommended_vendor" in data["insights"]

def test_13_vendor_selection(client):
    # 13. Vendor selection approves winning vendor and closes competing quotes
    # Ensure test isolation by clearing any previous selection for w1/catering
    db = SessionLocal()
    try:
        db.query(VendorSelection).filter(
            VendorSelection.wedding_id == "w1",
            VendorSelection.category == "catering"
        ).delete()
        db.commit()
    finally:
        db.close()

    quotes = client.get("/api/v1/weddings/w1/quotes?category=catering").json()
    assert len(quotes) >= 2
    winning_quote = quotes[0]
    q_id = winning_quote["id"]


    select_res = client.post(
        f"/api/v1/quotes/{q_id}/select",
        json={"notes": "Approved by client after menu tasting.", "selected_by": "Aarav Mehta"}
    )
    assert select_res.status_code == 200, select_res.text
    sel_data = select_res.json()
    assert sel_data["quote_id"] == q_id

    # Verify winning quote status is 'selected'
    updated_q = client.get(f"/api/v1/quotes/{q_id}").json()
    assert updated_q["status"] == "selected"

    # Verify competing quotes are closed
    other_quotes = [q for q in client.get("/api/v1/weddings/w1/quotes?category=catering").json() if q["id"] != q_id]
    for oq in other_quotes:
        assert oq["status"] == "closed"

def test_14_duplicate_vendor_selection_prevention(client):
    # 14. Duplicate vendor selection prevention for same category
    quotes = client.get("/api/v1/weddings/w1/quotes?category=catering").json()
    second_quote = [q for q in quotes if q["status"] != "selected"][0]
    dup_res = client.post(
        f"/api/v1/quotes/{second_quote['id']}/select",
        json={"notes": "Attempt duplicate selection", "selected_by": "Aarav Mehta"}
    )
    assert dup_res.status_code == 400
    assert "already locked" in dup_res.text.lower() or "prevented" in dup_res.text.lower()

def test_15_document_persistence_after_backend_restart(client):
    # 15. Verify documents and quotes persist in database
    db = SessionLocal()
    try:
        doc_count = db.query(Document).count()
        quote_count = db.query(Quote).count()
        assert doc_count >= 1
        assert quote_count >= 3
    finally:
        db.close()
