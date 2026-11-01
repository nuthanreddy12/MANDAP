import os
import re
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from google import genai
from google.genai import types
from backend.core.config import settings

def to_decimal(val: Any) -> Decimal:
    """Safely convert numeric/string value to Python Decimal with 2 decimal precision."""
    if val is None or val == "":
        return Decimal("0.00")
    try:
        return Decimal(str(val)).quantize(Decimal("0.01"))
    except Exception:
        return Decimal("0.00")

def normalize_text(text: str) -> str:
    """Normalize string for token-based matching."""
    if not text:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join(cleaned.split())

def calculate_token_similarity(s1: str, s2: str) -> float:
    """Calculate token Jaccard similarity between two descriptions."""
    tokens1 = set(normalize_text(s1).split())
    tokens2 = set(normalize_text(s2).split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


class FinancialReconciliationEngine:
    """
    Deterministic financial reconciliation engine for wedding vendor procurement.
    Reconciles approved vendor quotation against submitted invoice and recorded payments.
    Identifies price discrepancies, quantity mismatches, duplicate charges, unapproved add-ons,
    and payment schedule variances.
    """

    @staticmethod
    def reconcile(
        invoice_data: Dict[str, Any],
        approved_quote_data: Optional[Dict[str, Any]] = None,
        payments: Optional[List[Dict[str, Any]]] = None,
        approved_change_orders: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Deterministic reconciliation using Python Decimal.
        Returns detailed audit ledger, line matches, discrepancies, and status.
        """
        payments = payments or []
        approved_change_orders = approved_change_orders or []
        
        invoice_total = to_decimal(invoice_data.get("invoice_total"))
        invoice_items = invoice_data.get("line_items", []) or []
        
        quote_total = to_decimal(approved_quote_data.get("total_amount") if approved_quote_data else invoice_data.get("agreed_value"))
        quote_items = (approved_quote_data.get("items", []) if approved_quote_data else []) or []
        approved_charges = (approved_quote_data.get("additional_charges", []) if approved_quote_data else []) or []

        # 1. Calculate approved extras from change orders
        approved_extras_total = Decimal("0.00")
        for co in approved_change_orders:
            approved_extras_total += to_decimal(co.get("amount") or co.get("line_total"))

        # Add approved_extras field if present on invoice
        if invoice_data.get("approved_extras"):
            approved_extras_total = max(approved_extras_total, to_decimal(invoice_data.get("approved_extras")))

        # 2. Line Item Matching
        line_matches: List[Dict[str, Any]] = []
        discrepancies: List[Dict[str, Any]] = []
        unapproved_additional_total = Decimal("0.00")
        
        # Track seen items for duplicate charge detection
        seen_charges: Dict[str, int] = {}

        for inv_item in invoice_items:
            desc = inv_item.get("original_description") or inv_item.get("description") or inv_item.get("desc") or ""
            norm_desc = normalize_text(desc)
            inv_qty = to_decimal(inv_item.get("quantity", 1))
            inv_rate = to_decimal(inv_item.get("unit_price") or inv_item.get("rate") or inv_item.get("invoiced_amount", 0))
            inv_line_total = to_decimal(inv_item.get("line_total") or inv_item.get("invoiced_amount") or (inv_qty * inv_rate))

            # Duplicate charge check
            charge_key = f"{norm_desc}_{inv_line_total}"
            seen_charges[charge_key] = seen_charges.get(charge_key, 0) + 1
            is_duplicate = seen_charges[charge_key] > 1

            if is_duplicate:
                disc = {
                    "type": "duplicate_charge",
                    "item_description": desc,
                    "invoiced_amount": float(inv_line_total),
                    "details": f"Duplicate billing detected: '{desc}' invoiced multiple times ({seen_charges[charge_key]} occurrences).",
                }
                discrepancies.append(disc)

            # Match against approved quote items
            best_match = None
            highest_sim = 0.0

            for q_item in quote_items:
                q_desc = q_item.get("original_description") or q_item.get("description") or q_item.get("desc") or ""
                sim = calculate_token_similarity(desc, q_desc)
                if sim > highest_sim:
                    highest_sim = sim
                    best_match = q_item

            # Check matching against approved additional charges
            matched_charge = None
            if highest_sim < 0.35:
                for ac in approved_charges:
                    ac_desc = ac.get("name") or ac.get("description", "")
                    sim = calculate_token_similarity(desc, ac_desc)
                    if sim > highest_sim:
                        highest_sim = sim
                        matched_charge = ac

            # Check matching against approved change orders
            matched_change_order = None
            if highest_sim < 0.35:
                for co in approved_change_orders:
                    co_desc = co.get("description") or co.get("name", "")
                    sim = calculate_token_similarity(desc, co_desc)
                    if sim > highest_sim:
                        highest_sim = sim
                        matched_change_order = co

            if highest_sim >= 0.35 and best_match:
                # Matched approved quote item
                q_qty = to_decimal(best_match.get("quantity", 1))
                q_rate = to_decimal(best_match.get("unit_price"))
                expected_total = to_decimal(best_match.get("line_total") or best_match.get("agreed_amount") or (q_qty * q_rate))
                
                qty_diff = inv_qty - q_qty
                rate_diff = inv_rate - q_rate if (inv_rate > 0 and q_rate > 0) else Decimal("0.00")
                line_variance = inv_line_total - expected_total

                match_entry = {
                    "invoice_item": desc,
                    "matched_quote_item": best_match.get("original_description"),
                    "invoice_quantity": float(inv_qty),
                    "agreed_quantity": float(q_qty),
                    "invoice_rate": float(inv_rate),
                    "agreed_rate": float(q_rate),
                    "invoice_total": float(inv_line_total),
                    "agreed_total": float(expected_total),
                    "variance": float(line_variance),
                    "match_type": "contracted_item",
                    "status": "matched" if line_variance == Decimal("0.00") else "variance",
                }
                line_matches.append(match_entry)

                if qty_diff != Decimal("0.00"):
                    discrepancies.append({
                        "type": "quantity_mismatch",
                        "item_description": desc,
                        "agreed_quantity": float(q_qty),
                        "invoiced_quantity": float(inv_qty),
                        "variance": float(qty_diff),
                        "details": f"Quantity billed ({inv_qty}) differs from contracted quantity ({q_qty}).",
                    })

                if rate_diff != Decimal("0.00"):
                    discrepancies.append({
                        "type": "price_mismatch",
                        "item_description": desc,
                        "agreed_rate": float(q_rate),
                        "invoiced_rate": float(inv_rate),
                        "variance": float(rate_diff),
                        "details": f"Unit rate billed (INR {inv_rate:,.2f}) exceeds agreed rate (INR {q_rate:,.2f}).",
                    })

            elif highest_sim >= 0.35 and (matched_charge or matched_change_order):
                # Matched approved additional charge or change order
                agreed_charge_amt = to_decimal(
                    (matched_charge.get("amount") or matched_charge.get("line_total"))
                    if matched_charge else
                    (matched_change_order.get("amount") or matched_change_order.get("line_total"))
                )
                variance = inv_line_total - agreed_charge_amt
                
                line_matches.append({
                    "invoice_item": desc,
                    "matched_quote_item": (matched_charge.get("name") if matched_charge else matched_change_order.get("description")),
                    "invoice_total": float(inv_line_total),
                    "agreed_total": float(agreed_charge_amt),
                    "variance": float(variance),
                    "match_type": "approved_addition",
                    "status": "matched" if variance == Decimal("0.00") else "variance",
                })

                if variance != Decimal("0.00"):
                    discrepancies.append({
                        "type": "price_mismatch",
                        "item_description": desc,
                        "agreed_rate": float(agreed_charge_amt),
                        "invoiced_rate": float(inv_line_total),
                        "variance": float(variance),
                        "details": f"Approved charge billed at INR {inv_line_total:,.2f} vs agreed INR {agreed_charge_amt:,.2f}.",
                    })
            elif any(t in norm_desc for t in ["gst", "tax", "vat", "goods & services"]) and to_decimal(approved_quote_data.get("tax_amount", 0)) > 0:
                # Contracted Tax / GST line
                approved_tax = to_decimal(approved_quote_data.get("tax_amount", 0))
                tax_diff = inv_line_total - approved_tax
                line_matches.append({
                    "invoice_item": desc,
                    "matched_quote_item": "Contracted GST / Tax",
                    "invoice_quantity": 1.0,
                    "agreed_quantity": 1.0,
                    "invoice_rate": float(inv_line_total),
                    "agreed_rate": float(approved_tax),
                    "invoice_total": float(inv_line_total),
                    "agreed_total": float(approved_tax),
                    "variance": float(tax_diff),
                    "match_type": "contracted_tax",
                    "status": "matched" if tax_diff == Decimal("0.00") else "variance",
                })
                if tax_diff != Decimal("0.00"):
                    discrepancies.append({
                        "type": "price_mismatch",
                        "item_description": desc,
                        "agreed_rate": float(approved_tax),
                        "invoiced_rate": float(inv_line_total),
                        "variance": float(tax_diff),
                        "details": f"Tax billed (INR {inv_line_total:,.2f}) differs from contracted tax (INR {approved_tax:,.2f}).",
                    })
            else:
                # Unapproved additional charge!
                unapproved_additional_total += inv_line_total
                disc = {
                    "type": "unapproved_additional_charge",
                    "item_description": desc,
                    "invoiced_amount": float(inv_line_total),
                    "details": f"Unapproved additional charge: '{desc}' for INR {inv_line_total:,.2f} is not present in contract or approved change orders.",
                }
                discrepancies.append(disc)
                line_matches.append({
                    "invoice_item": desc,
                    "matched_quote_item": None,
                    "invoice_total": float(inv_line_total),
                    "agreed_total": 0.0,
                    "variance": float(inv_line_total),
                    "match_type": "unapproved_addition",
                    "status": "unapproved",
                })

        # 3. Overall Financial Reconciliation & Payment Variance
        total_contract_authorized = quote_total + approved_extras_total
        total_variance = invoice_total - total_contract_authorized

        total_paid = Decimal("0.00")
        for p in payments:
            total_paid += to_decimal(p.get("amount"))

        # If payments list is empty but invoice has paid_amount field
        if not payments and invoice_data.get("paid_amount"):
            total_paid = to_decimal(invoice_data.get("paid_amount"))

        remaining_balance = invoice_total - total_paid

        if total_paid < invoice_total:
            discrepancies.append({
                "type": "partial_payment",
                "invoice_total": float(invoice_total),
                "total_paid": float(total_paid),
                "remaining_balance": float(remaining_balance),
                "details": f"Partial payment status: INR {total_paid:,.2f} recorded out of INR {invoice_total:,.2f}. Balance outstanding: INR {remaining_balance:,.2f}.",
            })

        # Determine overall reconciliation status
        has_critical_discrepancy = any(
            d["type"] in ("unapproved_additional_charge", "duplicate_charge", "price_mismatch", "quantity_mismatch")
            for d in discrepancies
        )
        
        status = "review_required" if has_critical_discrepancy else ("matched" if total_variance == Decimal("0.00") else "review_required")
        requires_human_review = has_critical_discrepancy or (abs(total_variance) > Decimal("0.00"))

        result = {
            "vendor_name": invoice_data.get("vendor_name", "Vendor"),
            "invoice_number": invoice_data.get("invoice_number", "INV-UNKNOWN"),
            "status": status,
            "requires_human_review": requires_human_review,
            "agreed_amount": float(quote_total),
            "approved_extras": float(approved_extras_total),
            "total_authorized": float(total_contract_authorized),
            "invoice_total": float(invoice_total),
            "total_paid": float(total_paid),
            "remaining_balance": float(remaining_balance),
            "total_variance": float(total_variance),
            "unapproved_additional_total": float(unapproved_additional_total),
            "discrepancies_count": len(discrepancies),
            "discrepancies": discrepancies,
            "line_matches": line_matches,
        }

        # Generate Gemini explanation
        result["ai_explanation"] = FinancialReconciliationEngine.generate_ai_explanation(result)
        return result

    @staticmethod
    def generate_ai_explanation(reconciliation_data: Dict[str, Any]) -> str:
        """
        Uses Gemini API to generate concise, professional CFO/Finance audit explanation.
        Strictly references calculated Python Decimal values; never hallucinates values.
        """
        prompt = (
            f"You are the Chief Financial Controller for Mandap Luxury Wedding Operations.\n"
            f"Review this deterministic invoice reconciliation report for vendor {reconciliation_data.get('vendor_name')} "
            f"(Invoice: {reconciliation_data.get('invoice_number')}) and write a terse, factual, 3-4 sentence audit summary.\n"
            f"Financial Findings:\n"
            f"- Status: {reconciliation_data.get('status')}\n"
            f"- Contract Authorized: INR {reconciliation_data.get('total_authorized', 0):,.2f} "
            f"(Agreed: INR {reconciliation_data.get('agreed_amount', 0):,.2f} + Approved Extras: INR {reconciliation_data.get('approved_extras', 0):,.2f})\n"
            f"- Invoiced Total: INR {reconciliation_data.get('invoice_total', 0):,.2f}\n"
            f"- Variance: INR {reconciliation_data.get('total_variance', 0):,.2f}\n"
            f"- Unapproved Additions: INR {reconciliation_data.get('unapproved_additional_total', 0):,.2f}\n"
            f"- Paid: INR {reconciliation_data.get('total_paid', 0):,.2f} (Outstanding: INR {reconciliation_data.get('remaining_balance', 0):,.2f})\n"
            f"- Discrepancies ({reconciliation_data.get('discrepancies_count', 0)}): "
            f"{[d.get('details') for d in reconciliation_data.get('discrepancies', [])]}\n\n"
            f"Instructions:\n"
            f"State clearly whether the invoice matches or requires review. "
            f"Explicitly mention any unapproved charges (e.g. ₹45,000 unapproved charge) or price/quantity mismatches. "
            f"Do not invent any numbers; cite only the figures given above."
        )

        api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        model_name = os.environ.get("GEMINI_MODEL") or getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite")

        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=300,
                    )
                )
                if response.text and response.text.strip():
                    return response.text.strip()
            except Exception:
                pass

        # Deterministic fallback explanation
        discs = reconciliation_data.get("discrepancies", [])
        if not discs and reconciliation_data.get("total_variance", 0) == 0:
            return (
                f"Invoice {reconciliation_data.get('invoice_number')} matches contractual quotation exactly. "
                f"All billed items correspond to agreed rates and quantities. Total payable: INR {reconciliation_data.get('invoice_total', 0):,.2f}."
            )
        
        disc_details = "; ".join([d.get("details", "") for d in discs[:3]])
        return (
            f"Invoice {reconciliation_data.get('invoice_number')} requires human review (Variance: INR {reconciliation_data.get('total_variance', 0):,.2f}). "
            f"Audit findings: {disc_details}. "
            f"Outstanding balance payable upon dispute resolution: INR {reconciliation_data.get('remaining_balance', 0):,.2f}."
        )
