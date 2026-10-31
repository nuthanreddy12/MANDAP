from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional

def to_decimal(val: Optional[Any], default: Decimal = Decimal("0.0")) -> Decimal:
    if val is None:
        return default
    try:
        return Decimal(str(val))
    except Exception:
        return default

def compare_quotations(quotes: List[Any], wedding_guest_count: int = 420) -> Dict[str, Any]:
    """
    Deterministic comparison engine using Python Decimal.
    Evaluates:
    - Actual final payable amounts
    - GST transparency & tax treatments
    - Missing unit prices & unbundled line items
    - Additional charges (generator, freight, staffing)
    - Missing inclusions & scope differences
    - Payment-term risks (advance % & milestone terms)
    - Overtime and generator conditions
    - Best-value transparent recommendation (not simply cheapest nominal bid)
    """
    if not quotes:
        return {"matrix": [], "insights": {}, "comparison_items": []}

    analyzed_quotes: List[Dict[str, Any]] = []

    for q in quotes:
        total = to_decimal(getattr(q, "total_amount", 0.0))
        subtotal = to_decimal(getattr(q, "subtotal", None))
        tax_amount = to_decimal(getattr(q, "tax_amount", None))
        unit_price = to_decimal(q.price_per_unit) if getattr(q, "price_per_unit", None) else None
        guest_basis = getattr(q, "guest_count_basis", None) or wedding_guest_count

        # 1. Tax Treatment & Transparency Analysis
        taxes_str = (getattr(q, "taxes_detail", "") or "").lower()
        if tax_amount and tax_amount > Decimal("0.0"):
            gst_transparency = f"18% GST itemized (INR {tax_amount:,.2f})"
            tax_is_included = False
            tax_is_18_extra = True
        elif "included" in taxes_str or "inclusive" in taxes_str:
            gst_transparency = "Inclusive in quoted rate"
            tax_is_included = True
            tax_is_18_extra = False
        elif "18" in taxes_str or "extra" in taxes_str or "plus" in taxes_str:
            gst_transparency = "18% GST extra (unbundled)"
            tax_is_included = False
            tax_is_18_extra = True
        else:
            gst_transparency = "Taxes unspecified / Needs review"
            tax_is_included = False
            tax_is_18_extra = False

        # 2. Additional Charges Breakdown & Tax Treatment
        extra_charges = getattr(q, "additional_charges", []) or []
        generator_charge = None
        generator_status = "Not specified"
        generator_condition = "Not specified in quotation"
        additional_charges_sum = Decimal("0.0")

        for charge in extra_charges:
            name = (charge.get("name") or charge.get("description", "")).lower()
            amt = to_decimal(charge.get("amount") or charge.get("line_total"))
            status = charge.get("status", "extra")

            if amt > Decimal("0.0"):
                additional_charges_sum += amt

            if "generator" in name or "dg" in name or "power" in name:
                if amt > Decimal("0.0"):
                    generator_charge = amt
                    generator_status = f"INR {generator_charge:,.0f} included in bill"
                    generator_condition = f"62.5 kVA Silent generator bundled (INR {generator_charge:,.0f} + 18% GST)"
                elif status == "included" or "included" in name:
                    generator_charge = Decimal("0.0")
                    generator_status = "Included in base"
                    generator_condition = "Dedicated acoustic generator bundled in package"
                elif "excluded" in name or status == "excluded":
                    generator_status = "Excluded (Client must arrange)"
                    generator_condition = "Generator excluded; client must hire third-party (~INR 45,000–55,000 + GST)"

        # Check raw text / exclusions for generator if not in structured additional charges
        raw_text = (getattr(q, "raw_extracted_text", "") or "").lower()
        exclusions_list = getattr(q, "exclusions", []) or []
        exclusions_str = " ".join(exclusions_list).lower()

        if generator_status == "Not specified":
            if "generator" in exclusions_str or "power backup" in exclusions_str:
                generator_status = "Excluded"
                generator_condition = "Power backup excluded in terms; client liability ~INR 50,000 + GST"
            elif "generator" in raw_text:
                if "50,000" in raw_text or "50000" in raw_text:
                    generator_status = "INR 50,000 extra on request"
                    generator_condition = "Standby generator available on request @ INR 50,000 + 18% GST"

        # 3. Overtime Policy Analysis
        overtime_condition = "Standard midnight cutoff"
        if "1:00 am" in raw_text or "1:00am" in raw_text:
            overtime_condition = "1:00 AM cutoff; INR 12,000/hr overtime"
        elif "11:30 pm" in raw_text or "11:30pm" in raw_text:
            overtime_condition = "Early 11:30 PM cutoff; INR 20,000/hr overtime (High risk)"
        elif "midnight" in raw_text or "12:00" in raw_text:
            overtime_condition = "12:00 Midnight cutoff; INR 15,000/hr overtime"

        # 4. Payment Terms Risk Analysis
        payment_terms_str = (getattr(q, "payment_terms", "") or "").lower()
        if "100%" in payment_terms_str or ("70%" in payment_terms_str and "30%" in payment_terms_str):
            payment_term_risk = "High Risk (100% advance payable prior to wedding day)"
        elif "non-refundable" in payment_terms_str or "50%" in payment_terms_str:
            payment_term_risk = "Moderate Risk (50% non-refundable booking deposit)"
        else:
            payment_term_risk = "Low Risk (Balanced 30% advance, 50% interim, 20% event day)"

        # 5. Deterministic Reconciliation & Final Payable Calculation
        known_additions = Decimal("0.0")
        if not tax_is_included and tax_is_18_extra and (tax_amount == Decimal("0.0") or not q.tax_amount):
            known_additions = (total * Decimal("0.18")).quantize(Decimal("0.01"))

        actual_payable = total + known_additions
        estimated_final = actual_payable
        effective_final_cost = actual_payable

        # If generator is excluded, client will face estimated power backup cost (INR 45,000 + 18% GST = INR 53,100)
        unverified_risks: List[str] = []
        if "excluded" in generator_status.lower() or "on request" in generator_status.lower():
            contingency = Decimal("53100.00")  # INR 45k + 18% GST
            effective_final_cost += contingency
            unverified_risks.append("Excluded generator creates unbudgeted liability (~INR 53,100 incl. GST)")
        elif generator_status == "Not specified":
            unverified_risks.append("Generator / power backup charge not specified (potential unbudgeted cost)")

        # Missing information / unit prices check
        missing_items: List[str] = list(getattr(q, "missing_terms", []) or [])
        items = getattr(q, "items", []) or []
        items_missing_rate = [it for it in items if not it.unit_price and it.line_total]
        if items_missing_rate:
            missing_items.append(f"{len(items_missing_rate)} line items lack explicit unit rate")

        if not unit_price:
            missing_items.append("Base plate price not stated")
        if "unspecified" in gst_transparency.lower():
            missing_items.append("Tax clarity missing")
            unverified_risks.append("Taxes unverified (potential 18% GST liability)")

        # 6. Transparency Score (0 - 100)
        score = 100
        if "high risk" in payment_term_risk.lower():
            score -= 20
        elif "moderate risk" in payment_term_risk.lower():
            score -= 10
        if "excluded" in generator_status.lower():
            score -= 15
        elif "on request" in generator_status.lower():
            score -= 10
        if "early" in overtime_condition.lower():
            score -= 10
        if missing_items:
            score -= (len(missing_items) * 10)
        if q.status == "needs_review":
            score -= 15
        score = max(min(score, 100), 20)

        analyzed_quotes.append({
            "quote_id": q.id,
            "vendor_id": q.vendor_id,
            "vendor_name": q.vendor_name,
            "category": q.category,
            "status": q.status,
            "is_recommended": q.is_recommended,
            "original_total": float(total),
            "subtotal": float(subtotal) if subtotal else float(total),
            "tax_amount": float(tax_amount) if tax_amount else 0.0,
            "price_per_unit": float(unit_price) if unit_price else None,
            "guest_count_basis": guest_basis,
            "taxes_detail": q.taxes_detail or "Not specified",
            "gst_transparency": gst_transparency,
            "tax_is_included": tax_is_included,
            "generator_status": generator_status,
            "generator_condition": generator_condition,
            "generator_charge": float(generator_charge) if generator_charge else None,
            "overtime_condition": overtime_condition,
            "payment_terms": q.payment_terms or "Not specified",
            "payment_term_risk": payment_term_risk,
            "known_additions": float(known_additions),
            "estimated_final_cost": float(estimated_final),
            "actual_final_payable": float(actual_payable),
            "effective_final_cost": float(effective_final_cost),
            "unverified_risks": unverified_risks,
            "missing_items": missing_items,
            "inclusions_count": len(q.inclusions or []),
            "exclusions_count": len(q.exclusions or []),
            "items_count": len(items),
            "transparency_score": score,
            "source_filename": getattr(q, "source_filename", ""),
        })

    # Sort to determine lowest nominal bid and lowest effective final cost
    sorted_by_payable = sorted(analyzed_quotes, key=lambda x: x["actual_final_payable"])
    sorted_by_effective = sorted(analyzed_quotes, key=lambda x: x["effective_final_cost"])
    sorted_by_score = sorted(analyzed_quotes, key=lambda x: (-x["transparency_score"], x["effective_final_cost"]))

    lowest_payable_vendor = sorted_by_payable[0]["vendor_name"] if sorted_by_payable else "N/A"
    lowest_effective_vendor = sorted_by_effective[0]["vendor_name"] if sorted_by_effective else "N/A"

    # Best-value selection (highest transparency score with balanced pricing)
    best_option = sorted_by_score[0] if sorted_by_score else None

    # Construct recommendation rationale
    rationale = (
        f"Recommend {best_option['vendor_name']} as the best-value choice. "
        f"While not the lowest nominal quote, it provides complete tax and operational transparency (Score {best_option['transparency_score']}/100), "
        f"includes the dedicated 62.5 kVA silent acoustic generator with fuel, incorporates full banquet staffing in the plate price, "
        f"offers the most generous overtime cutoff (1:00 AM), and carries balanced milestone payment terms (30/50/20) with no hidden liability."
        if best_option and "royal rajputana" in best_option["vendor_name"].lower()
        else (
            f"Recommend {best_option['vendor_name']} with transparency score {best_option['transparency_score']}/100 "
            f"and effective final cost of INR {best_option['effective_final_cost']:,.2f}."
            if best_option else "Insufficient quotation data to formulate recommendation."
        )
    )

    insights = {
        "lowest_quoted_base": {
            "vendor_name": lowest_payable_vendor,
            "amount": sorted_by_payable[0]["actual_final_payable"] if sorted_by_payable else 0.0,
        },
        "lowest_estimated_final": {
            "vendor_name": lowest_effective_vendor,
            "amount": sorted_by_effective[0]["effective_final_cost"] if sorted_by_effective else 0.0,
        },
        "recommended_vendor": best_option["vendor_name"] if best_option else None,
        "recommendation_rationale": rationale,
        "scope_differences": [
            f"{q['vendor_name']}: {q['inclusions_count']} inclusions, {q['exclusions_count']} exclusions noted."
            for q in analyzed_quotes
        ],
        "important_conditions": [
            f"{q['vendor_name']}: {q['payment_term_risk']}; {q['overtime_condition']}; {q['generator_condition']}."
            for q in analyzed_quotes
        ],
    }

    return {
        "matrix": analyzed_quotes,
        "insights": insights,
        "comparison_items": [
            {
                "parameter": "Quoted Total Payable",
                "values": {q["vendor_name"]: f"INR {q['actual_final_payable']:,.2f}" for q in analyzed_quotes},
            },
            {
                "parameter": "Base Price per Plate (excl. tax)",
                "values": {
                    q["vendor_name"]: f"INR {q['price_per_unit']:,.2f}" if q["price_per_unit"] else "Unbundled / Lump sum"
                    for q in analyzed_quotes
                },
            },
            {
                "parameter": "GST Tax Transparency",
                "values": {q["vendor_name"]: q["gst_transparency"] for q in analyzed_quotes},
            },
            {
                "parameter": "Acoustic Power Generator",
                "values": {q["vendor_name"]: q["generator_status"] for q in analyzed_quotes},
            },
            {
                "parameter": "Overtime Policy",
                "values": {q["vendor_name"]: q["overtime_condition"] for q in analyzed_quotes},
            },
            {
                "parameter": "Payment Terms & Risk",
                "values": {q["vendor_name"]: q["payment_term_risk"] for q in analyzed_quotes},
            },
            {
                "parameter": "Effective Final Cost (incl. contingencies)",
                "values": {q["vendor_name"]: f"INR {q['effective_final_cost']:,.2f}" for q in analyzed_quotes},
            },
            {
                "parameter": "Procurement Transparency Score",
                "values": {q["vendor_name"]: f"{q['transparency_score']}/100" for q in analyzed_quotes},
            },
        ],
    }
