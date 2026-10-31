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
