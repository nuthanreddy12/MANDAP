import os
import json
import logging
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.core.config import settings

logger = logging.getLogger(__name__)

class BidderEvaluation(BaseModel):
    vendor_name: str = Field(..., description="Name of the bidder vendor")
    effective_commercial_cost: float = Field(..., description="Total effective cost in INR")
    scope_grade: str = Field(..., description="High-level scope rating: Comprehensive, Standard, or High-Risk")
    key_advantages: List[str] = Field(default_factory=list, description="Top tangible advantages")
    key_risks: List[str] = Field(default_factory=list, description="Top commercial or operational risks")
    missing_scope_or_clarifications: List[str] = Field(default_factory=list, description="Gaps requiring vendor clarification")

class GeminiVendorIntelligence(BaseModel):
    recommended_vendor: str = Field(..., description="Name of recommended winning vendor")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    executive_summary: str = Field(..., description="2-3 sentence executive briefing for the wedding host")
    recommendation_rationale: str = Field(..., description="Comprehensive commercial rationale justifying recommendation")
    key_advantages: List[str] = Field(default_factory=list, description="Top advantages of the recommended vendor")
    key_risks: List[str] = Field(default_factory=list, description="Identified operational or cost risks")
    hidden_charges_and_pitfalls: List[str] = Field(default_factory=list, description="Excluded costs, surcharges, or power risks")
    missing_information_to_clarify: List[str] = Field(default_factory=list, description="Questions for planner to resolve prior to signing")
    bidder_evaluations: List[BidderEvaluation] = Field(default_factory=list, description="Comparative evaluation of each competing bidder")
    commercial_tradeoff_verdict: str = Field(..., description="Clear explanation of trade-off between lowest nominal bid vs best value")
    distinction_of_evidence: str = Field(
        default="Analysis formulated strictly from verified quotation PDF text, line-item pricing and contractual terms on file.",
        description="Explicit note stating grounds of recommendation without inventing data"
    )

def generate_gemini_vendor_intelligence(
    wedding_id: str,
    category: str,
    guest_count: int,
    venue_name: str,
    analyzed_quotes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Invokes Google Gemini with structured comparison matrix data.
    Evaluates commercial trade-offs, hidden charges, payment risks, and inclusions.
    Falls back gracefully to deterministic analysis if Gemini is unavailable.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    model_name = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite") or "gemini-3.5-flash-lite"
    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not api_key or api_key in ("your-gemini-api-key", ""):
        return {
            "is_ai_generated": False,
            "ai_provider": "Deterministic Comparison Engine",
            "ai_model": "None (Rule-based Fallback)",
            "ai_timestamp": now_ts,
            "ai_status": "unavailable",
            "ai_error": "Gemini API key is not configured in backend environment.",
            "intelligence": None,
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Prepare summary of bidders
        bidders_summary = []
        for q in analyzed_quotes:
            bidders_summary.append({
                "vendor_name": q.get("vendor_name"),
                "quote_id": q.get("quote_id"),
                "quoted_grand_total": q.get("actual_final_payable") or q.get("original_total"),
                "subtotal": q.get("subtotal"),
                "tax_amount": q.get("tax_amount"),
                "price_per_unit": q.get("price_per_unit"),
                "taxes_detail": q.get("taxes_detail"),
                "generator_status": q.get("generator_status"),
                "overtime_condition": q.get("overtime_condition"),
                "payment_terms": q.get("payment_terms"),
                "payment_risk": q.get("payment_term_risk"),
                "inclusions_count": q.get("inclusions_count"),
                "exclusions_count": q.get("exclusions_count"),
                "missing_items": q.get("missing_items", []),
                "unverified_risks": q.get("unverified_risks", []),
            })

        prompt = f"""
You are MANDAP's Principal Procurement Intelligence Partner for luxury weddings.
Analyze the following verified quotations submitted for the Mehra x Kapoor wedding.

WEDDING CONTEXT:
- Wedding ID: {wedding_id}
- Category: {category.upper()}
- Venue: {venue_name}
- Guaranteed Guest Count: {guest_count} Guests

BIDDERS SUBMISSIONS:
{json.dumps(bidders_summary, indent=2)}

INSTRUCTIONS:
1. Evaluate commercial trade-offs: compare nominal lowest bid against true total cost of ownership.
2. Scrutinize hidden charges: look for excluded power backup / generators, unbundled freight, overtime penalties after midnight.
3. Assess payment terms risk: high non-refundable advances represent host liquidity risk.
4. Verify scope completeness for {guest_count} guests.
5. Base your analysis STRICTLY on the data provided above. DO NOT invent vendor historical ratings, reviews, or numbers.
6. Provide a decisive recommended vendor with clear advantages, risks, and items to clarify before contract execution.
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiVendorIntelligence,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response body.")

        parsed_data = json.loads(response.text)
        validated = GeminiVendorIntelligence.model_validate(parsed_data)

        return {
            "is_ai_generated": True,
            "ai_provider": "Google Gemini",
            "ai_model": model_name,
            "ai_timestamp": now_ts,
            "ai_status": "completed",
            "ai_error": None,
            "intelligence": validated.model_dump(),
        }

    except Exception as e:
        logger.warning(f"Gemini vendor intelligence generation failed: {e}")
        return {
            "is_ai_generated": False,
            "ai_provider": "Deterministic Comparison Engine",
            "ai_model": "None (Rule-based Fallback)",
            "ai_timestamp": now_ts,
            "ai_status": "unavailable",
            "ai_error": f"Gemini analysis could not be completed ({str(e)}). Falling back to deterministic scoring.",
            "intelligence": None,
        }

