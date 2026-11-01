import os
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.core.config import settings

logger = logging.getLogger(__name__)

class ExtractedAdditionalCharge(BaseModel):
    name: str = Field(..., description="Name of additional charge e.g. Generator, Overtime, DJ Console")
    amount: Optional[float] = Field(None, description="Charge amount if specified")
    status: str = Field("extra", description="extra, included, or not_specified")
    notes: Optional[str] = None

class ExtractedLineItem(BaseModel):
    original_description: str = Field(..., description="Exact original line item description from document")
    normalized_category: str = Field(..., description="Catering, Decoration, Photography, Entertainment, Sound, Lighting, Staff, Transport, Other")
    quantity: Optional[float] = Field(None, description="Numeric quantity or plate count")
    unit: Optional[str] = Field(None, description="plate, pax, hour, piece, lump_sum, etc.")
    unit_price: Optional[float] = Field(None, description="Price per single unit")
    tax_info: Optional[str] = Field(None, description="Tax detail for this line, e.g. 18% extra, Included")
    line_total: Optional[float] = Field(None, description="Calculated or quoted line total")
    source_page: Optional[int] = Field(None, description="Page number where item was found")
    source_text: Optional[str] = Field(None, description="Verbatim text snippet from PDF")
    confidence: float = Field(1.0, description="Extraction confidence score from 0.0 to 1.0")

class ExtractedQuotation(BaseModel):
    vendor_name: str = Field(..., description="Vendor business or brand name")
    vendor_contact: Optional[str] = Field(None, description="Phone, email or address of vendor")
    quotation_number: Optional[str] = Field(None, description="Invoice or quote number e.g. QT-2026-091")
    quotation_date: Optional[str] = Field(None, description="Date of quotation issuance")
    validity_date: Optional[str] = Field(None, description="Date quotation expires")
    currency: str = Field("INR", description="Currency code e.g. INR")
    subtotal: Optional[float] = Field(None, description="Subtotal before taxes and extras")
    tax_amount: Optional[float] = Field(None, description="Explicit tax amount")
    taxes_detail: Optional[str] = Field(None, description="Tax summary e.g. 18% extra, Included, or Needs review")
    grand_total: Optional[float] = Field(None, description="Final payable amount")
    guest_count_basis: Optional[int] = Field(None, description="Number of guests basis e.g. 420")
    price_per_unit: Optional[float] = Field(None, description="Base price per plate or unit before taxes")
    payment_terms: Optional[str] = Field(None, description="Advance percentage, payment milestone schedule")
    inclusions: List[str] = Field(default_factory=list, description="List of explicitly included services or items")
    exclusions: List[str] = Field(default_factory=list, description="List of explicitly excluded items")
    additional_charges: List[ExtractedAdditionalCharge] = Field(default_factory=list, description="Extra charges e.g. Generator, Overtime")
    line_items: List[ExtractedLineItem] = Field(default_factory=list, description="Granular quotation line items")

class QuotationMathValidationResult(BaseModel):
    is_valid: bool
    calculated_line_items_total: float
    calculated_subtotal: float
    declared_subtotal: Optional[float] = None
    declared_tax: Optional[float] = None
    declared_grand_total: Optional[float] = None
    discrepancy_amount: float = 0.0
    discrepancies: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None

def validate_quotation_math(extracted: ExtractedQuotation) -> QuotationMathValidationResult:
    """
    Validates arithmetic consistency between line items, additional charges, subtotal, taxes, and grand total.
    Never fabricates or alters financial values.
    Flags discrepancies if:
    1. Individual line item math (qty * unit_price) differs from line_total.
    2. Sum of line items (+ separate additional charges) differs from declared subtotal.
    3. Declared subtotal + tax_amount differs from declared grand_total.
    """
    discrepancies: List[str] = []

    # 1. Sum up all valid line item totals and verify individual line math
    item_sum = 0.0
    for idx, item in enumerate(extracted.line_items):
        item_total = None
        if item.line_total is not None and item.line_total > 0:
            item_total = float(item.line_total)
        elif item.quantity is not None and item.unit_price is not None and item.quantity > 0 and item.unit_price > 0:
            item_total = float(item.quantity) * float(item.unit_price)

        if item.quantity is not None and item.unit_price is not None and item.line_total is not None:
            expected_line = float(item.quantity) * float(item.unit_price)
            if abs(expected_line - float(item.line_total)) > 1.0:
                discrepancies.append(
                    f"Line item math mismatch in '{item.original_description}': "
                    f"Qty {item.quantity} * Rate {item.unit_price} = INR {expected_line:,.2f}, "
                    f"but extracted line_total is INR {float(item.line_total):,.2f}."
                )

        if item_total is not None:
            item_sum += item_total

    # 2. Check additional charges
    extra_charges_sum = sum(
        float(c.amount)
        for c in extracted.additional_charges
        if c.amount is not None and float(c.amount) > 0
    )

    subtotal = float(extracted.subtotal) if extracted.subtotal is not None else None
    tax_amount = float(extracted.tax_amount) if extracted.tax_amount is not None else 0.0
    grand_total = float(extracted.grand_total) if extracted.grand_total is not None else None

    # Check Subtotal vs Line Items
    if subtotal is not None and len(extracted.line_items) > 0:
        diff_direct = abs(item_sum - subtotal)
        diff_with_charges = abs((item_sum + extra_charges_sum) - subtotal)

        # Allow 1.00 INR epsilon for rounding
        if diff_direct > 1.0 and diff_with_charges > 1.0:
            best_diff = min(diff_direct, diff_with_charges)
            discrepancies.append(
                f"Line items total mismatch: Sum of extracted line items is INR {item_sum:,.2f}, "
                f"which differs from declared subtotal INR {subtotal:,.2f} by INR {best_diff:,.2f}."
            )

    # Check Grand Total vs Subtotal + Tax
    if subtotal is not None and grand_total is not None:
        expected_grand = subtotal + tax_amount
        if abs(expected_grand - grand_total) > 1.0:
            diff = abs(expected_grand - grand_total)
            discrepancies.append(
                f"Grand total reconciliation mismatch: Subtotal (INR {subtotal:,.2f}) + "
                f"Tax (INR {tax_amount:,.2f}) = INR {expected_grand:,.2f}, but declared "
                f"grand total is INR {grand_total:,.2f} (Difference: INR {diff:,.2f})."
            )
    elif grand_total is not None and subtotal is None and len(extracted.line_items) > 0:
        if abs(item_sum - grand_total) > 1.0 and abs((item_sum + tax_amount) - grand_total) > 1.0:
            diff = abs(item_sum - grand_total)
            discrepancies.append(
                f"Grand total vs items mismatch: Sum of extracted line items is INR {item_sum:,.2f}, "
                f"which differs from grand total INR {grand_total:,.2f} by INR {diff:,.2f}."
            )

    is_valid = len(discrepancies) == 0
    explanation = None if is_valid else " | ".join(discrepancies)

    return QuotationMathValidationResult(
        is_valid=is_valid,
        calculated_line_items_total=round(item_sum, 2),
        calculated_subtotal=round(subtotal if subtotal is not None else item_sum, 2),
        declared_subtotal=subtotal,
        declared_tax=tax_amount if extracted.tax_amount is not None else None,
        declared_grand_total=grand_total,
        discrepancy_amount=round(abs(item_sum - subtotal), 2) if subtotal is not None else 0.0,
        discrepancies=discrepancies,
        explanation=explanation,
    )

class GeminiExtractionError(Exception):
    pass

class GeminiApiKeyMissingError(GeminiExtractionError):
    pass

def extract_quotation_with_gemini(extracted_pdf_data: dict) -> ExtractedQuotation:
    """
    Calls Google Gemini using the google-genai SDK with strict Pydantic schema validation.
    Raises GeminiApiKeyMissingError if the API key is not configured.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    if not api_key or api_key in ("your-gemini-api-key", ""):
        raise GeminiApiKeyMissingError(
            "Gemini API key is not configured in backend environment. Please set GEMINI_API_KEY."
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are MANDAP's senior wedding procurement extraction engine.
Analyze the following vendor quotation document text carefully.
Extract all details strictly according to the requested JSON schema.

Rules:
1. Do not fabricate or invent missing figures. If a price, date, or tax is not in the text, use null.
2. Preserve the exact original line item description in original_description.
3. Identify whether taxes are included, excluded (e.g. "18% extra"), or unstated.
4. Separate out additional charges such as Acoustic Generator, Valet, Chauffeur, or Overtime fees.
5. Identify payment terms (e.g. 50% advance, 50% on event day).
6. Note the source page for line items.

DOCUMENT CONTENT:
{extracted_pdf_data.get('full_text', '')}
"""
        model_to_use = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite") or "gemini-3.5-flash-lite"
        response = client.models.generate_content(
            model=model_to_use,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedQuotation,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise GeminiExtractionError("Gemini returned an empty response.")

        raw_json = json.loads(response.text)
        return ExtractedQuotation.model_validate(raw_json)

    except GeminiExtractionError:
        raise
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        raise GeminiExtractionError(f"AI extraction failed: {str(e)}")
