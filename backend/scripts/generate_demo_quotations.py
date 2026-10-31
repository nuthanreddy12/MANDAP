import os
import json
from decimal import Decimal
from pathlib import Path
import pymupdf

OUTPUT_DIR = Path("backend/storage/demo_quotes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf(filename: str, vendor_data: dict):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # Standard A4 size

    # Colors
    c_primary = (0.16, 0.18, 0.15)      # Deep forest #292E27
    c_gold = (0.77, 0.64, 0.43)         # Warm gold #C4A46D
    c_grey = (0.40, 0.40, 0.40)         # Medium grey
    c_light_bg = (0.97, 0.96, 0.94)     # Light warm background #F7F5F0
    c_border = (0.85, 0.82, 0.77)       # Border #D9D2C5
    c_alert = (0.75, 0.25, 0.20)        # Brick red

    y = 40

    # Synthetic demo watermark banner
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 20), color=c_gold, fill=c_light_bg)
    page.insert_text(
        (50, y + 14),
        "[SYNTHETIC DEMONSTRATION DATA FOR MANDAP HACKATHON AUDIT ONLY]",
        fontname="helv",
        fontsize=9,
        color=c_alert
    )
    y += 35

    # Vendor Header
    page.insert_text((40, y), vendor_data["vendor_name"].upper(), fontname="hebo", fontsize=15, color=c_primary)
    y += 16
    page.insert_text((40, y), f"Address: {vendor_data['address']} | GSTIN: {vendor_data['gstin']}", fontname="helv", fontsize=9, color=c_grey)
    y += 14
    page.insert_text((40, y), f"Contact: {vendor_data['contact_person']} | Phone: {vendor_data['phone']} | Email: {vendor_data['email']}", fontname="helv", fontsize=9, color=c_grey)
    y += 20

    page.draw_line(pymupdf.Point(40, y), pymupdf.Point(555, y), color=c_border, width=1)
    y += 16

    # Meta Details (2 columns)
    page.insert_text((40, y), f"Quotation No: {vendor_data['quotation_no']}", fontname="hebo", fontsize=10, color=c_primary)
    page.insert_text((320, y), f"Client: {vendor_data['client_names']}", fontname="hebo", fontsize=10, color=c_primary)
    y += 14
    page.insert_text((40, y), f"Issue Date: {vendor_data['issue_date']}", fontname="helv", fontsize=9, color=c_grey)
    page.insert_text((320, y), f"Event: {vendor_data['event_name']} ({vendor_data['dates']})", fontname="helv", fontsize=9, color=c_grey)
    y += 14
    page.insert_text((40, y), f"Quote Validity: {vendor_data['validity']}", fontname="helv", fontsize=9, color=c_grey)
    page.insert_text((320, y), f"Venue & City: {vendor_data['venue']}, {vendor_data['city']}", fontname="helv", fontsize=9, color=c_grey)
    y += 14
    page.insert_text((40, y), f"Category: {vendor_data['category'].title()}", fontname="helv", fontsize=9, color=c_grey)
    page.insert_text((320, y), f"Guaranteed Guest Count: {vendor_data['guest_count']} Guests", fontname="hebo", fontsize=9, color=c_primary)
    y += 22

    # Table Header
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 20), color=c_primary, fill=c_primary)
    page.insert_text((45, y + 14), "#", fontname="hebo", fontsize=9, color=(1, 1, 1))
    page.insert_text((65, y + 14), "Service / Menu Description", fontname="hebo", fontsize=9, color=(1, 1, 1))
    page.insert_text((310, y + 14), "Qty", fontname="hebo", fontsize=9, color=(1, 1, 1))
    page.insert_text((355, y + 14), "Unit", fontname="hebo", fontsize=9, color=(1, 1, 1))
    page.insert_text((400, y + 14), "Rate (INR)", fontname="hebo", fontsize=9, color=(1, 1, 1))
    page.insert_text((480, y + 14), "Amount (INR)", fontname="hebo", fontsize=9, color=(1, 1, 1))
    y += 20

    # Line Items
    idx = 1
    for item in vendor_data["line_items"]:
        row_bg = c_light_bg if idx % 2 == 1 else (1, 1, 1)
        page.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=c_border, fill=row_bg, width=0.5)
        page.insert_text((45, y + 13), str(idx), fontname="helv", fontsize=8.5, color=c_primary)
        page.insert_text((65, y + 13), item["description"][:52], fontname="helv", fontsize=8.5, color=c_primary)
        page.insert_text((310, y + 13), str(item["quantity"]), fontname="helv", fontsize=8.5, color=c_primary)
        page.insert_text((355, y + 13), item["unit"], fontname="helv", fontsize=8.5, color=c_primary)
        page.insert_text((400, y + 13), f"{item['unit_price']:,.2f}", fontname="helv", fontsize=8.5, color=c_primary)
        page.insert_text((480, y + 13), f"{item['line_total']:,.2f}", fontname="helv", fontsize=8.5, color=c_primary)
        y += 18
        idx += 1

    # Additional Charges Section
    if vendor_data.get("additional_charges_rows"):
        page.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=c_border, fill=(0.94, 0.92, 0.88), width=0.5)
        page.insert_text((45, y + 13), "ADDITIONAL CHARGES & OPERATIONAL SPECIFICATIONS", fontname="hebo", fontsize=8.5, color=c_primary)
        y += 18
        for chg in vendor_data["additional_charges_rows"]:
            page.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=c_border, fill=(1, 1, 1), width=0.5)
            page.insert_text((45, y + 13), str(idx), fontname="helv", fontsize=8.5, color=c_primary)
            page.insert_text((65, y + 13), chg["description"][:52], fontname="helv", fontsize=8.5, color=c_primary)
            page.insert_text((310, y + 13), str(chg.get("quantity", 1)), fontname="helv", fontsize=8.5, color=c_primary)
            page.insert_text((355, y + 13), chg.get("unit", "lump_sum"), fontname="helv", fontsize=8.5, color=c_primary)
            page.insert_text((400, y + 13), f"{chg['unit_price']:,.2f}" if chg['unit_price'] else "Extra", fontname="helv", fontsize=8.5, color=c_primary)
            page.insert_text((480, y + 13), f"{chg['line_total']:,.2f}" if chg['line_total'] else "As noted", fontname="helv", fontsize=8.5, color=c_primary)
            y += 18
            idx += 1

    y += 10
    # Financial Totals Summary Box (Right aligned)
    tot_box_x = 280
    page.draw_rect(pymupdf.Rect(tot_box_x, y, 555, y + 105), color=c_border, fill=c_light_bg, width=1)
    ty = y + 16
    page.insert_text((tot_box_x + 10, ty), "Catering Subtotal:", fontname="helv", fontsize=9, color=c_primary)
    page.insert_text((460, ty), f"INR {vendor_data['subtotal']:,.2f}", fontname="hebo", fontsize=9, color=c_primary)
    ty += 16
    page.insert_text((tot_box_x + 10, ty), "Taxable Additional Charges:", fontname="helv", fontsize=9, color=c_primary)
    page.insert_text((460, ty), f"INR {vendor_data['additional_charges_total']:,.2f}", fontname="helv", fontsize=9, color=c_primary)
    ty += 16
    page.insert_text((tot_box_x + 10, ty), f"GST @ {vendor_data['gst_rate_percent']}% ({vendor_data['gst_breakdown']}):", fontname="helv", fontsize=9, color=c_primary)
    page.insert_text((460, ty), f"INR {vendor_data['tax_amount']:,.2f}", fontname="helv", fontsize=9, color=c_primary)
    ty += 20
    page.draw_line(pymupdf.Point(tot_box_x, ty - 6), pymupdf.Point(555, ty - 6), color=c_gold, width=1)
    page.insert_text((tot_box_x + 10, ty + 8), "FINAL PAYABLE GRAND TOTAL:", fontname="hebo", fontsize=10, color=c_primary)
    page.insert_text((450, ty + 8), f"INR {vendor_data['grand_total']:,.2f}", fontname="hebo", fontsize=11, color=c_primary)
    y += 118

    # Inclusions, Exclusions, Power & Overtime terms
    col1_x = 40
    col2_x = 300

    page.insert_text((col1_x, y), "INCLUDED SERVICES & EQUIPMENT:", fontname="hebo", fontsize=8.5, color=c_primary)
    page.insert_text((col2_x, y), "EXCLUSIONS & SPECIAL CONDITIONS:", fontname="hebo", fontsize=8.5, color=c_primary)
    y += 12

    max_terms = max(len(vendor_data["inclusions"]), len(vendor_data["exclusions"]))
    for i in range(max_terms):
        if i < len(vendor_data["inclusions"]):
            page.insert_text((col1_x, y), f"• {vendor_data['inclusions'][i]}", fontname="helv", fontsize=8, color=c_grey)
        if i < len(vendor_data["exclusions"]):
            page.insert_text((col2_x, y), f"• {vendor_data['exclusions'][i]}", fontname="helv", fontsize=8, color=c_grey)
        y += 12

    y += 10
    # Overtime & Generator clause
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 36), color=c_border, fill=c_light_bg, width=0.5)
    page.insert_text((46, y + 14), "POWER BACKUP & OVERTIME POLICY:", fontname="hebo", fontsize=8.5, color=c_primary)
    page.insert_text((46, y + 27), vendor_data["power_and_overtime_policy"][:110], fontname="helv", fontsize=8, color=c_grey)
    y += 44

    # Commercial Payment Terms
    page.draw_rect(pymupdf.Rect(40, y, 555, y + 32), color=c_border, fill=(1, 1, 1), width=0.5)
    page.insert_text((46, y + 13), "PAYMENT SCHEDULE & COMMERCIAL TERMS:", fontname="hebo", fontsize=8.5, color=c_primary)
    page.insert_text((46, y + 24), vendor_data["payment_terms"][:115], fontname="helv", fontsize=8, color=c_grey)
    y += 40

    # Authorization Footer
    page.insert_text((40, y), "Authorized Signatory: __________________________", fontname="helv", fontsize=8, color=c_grey)
    page.insert_text((350, y), "Client Acceptance: __________________________", fontname="helv", fontsize=8, color=c_grey)

    pdf_path = OUTPUT_DIR / filename
    doc.save(str(pdf_path))
    doc.close()
    print(f"Generated PDF: {pdf_path}")
    return pdf_path

# ==============================================================================
# VENDOR 1: Royal Rajputana Hospitality & Banquets Pvt. Ltd.
# ==============================================================================
v1_data = {
    "vendor_name": "Royal Rajputana Hospitality & Banquets Pvt. Ltd.",
    "address": "42-A, M.I. Road, C-Scheme, Jaipur 302001",
    "gstin": "08AAACR4291K1Z5",
    "contact_person": "Mahaveer Singh Rathore",
    "phone": "+91 98290 44882",
    "email": "events@royalrajputana.in",
    "quotation_no": "RRH-2026-CAT-042",
    "issue_date": "2026-10-15",
    "validity": "Valid for 30 days (Until 14 Nov 2026)",
    "client_names": "Mehra × Kapoor Wedding Reception",
    "event_name": "Royal Imperial Wedding Feast",
    "dates": "14–16 November 2026",
    "venue": "The Oberoi Rajvilas",
    "city": "Jaipur",
    "category": "catering",
    "guest_count": 420,
    "line_items": [
        {
            "description": "Royal Rajasthani Imperial Dinner Buffet (Live kitchen, silver chafers)",
            "quantity": 420,
            "unit": "plate",
            "unit_price": 2850.00,
            "line_total": 1197000.00,
        },
        {
            "description": "Live Chaat & Jodhpur Street Food Counter (12 varieties)",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 350.00,
            "line_total": 147000.00,
        },
        {
            "description": "Artisan Royal Dessert & Traditional Mithai Display (Ghewar, Malpua)",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 250.00,
            "line_total": 105000.00,
        },
        {
            "description": "Welcome Beverage & Handcrafted Mocktail Station",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 150.00,
            "line_total": 63000.00,
        },
    ],
    "additional_charges_rows": [
        {
            "description": "Dedicated 62.5 kVA Silent Acoustic Sound & Power Generator (8 hrs fuel)",
            "quantity": 1,
            "unit": "lump_sum",
            "unit_price": 45000.00,
            "line_total": 45000.00,
        },
        {
            "description": "Service Crew Uniformed Staffing (40 banquet waitstaff, 4 captains)",
            "quantity": 44,
            "unit": "staff",
            "unit_price": 0.00,
            "line_total": 0.00,
        },
    ],
    "subtotal": 1512000.00,
    "additional_charges_total": 45000.00,
    "gst_rate_percent": 18,
    "gst_breakdown": "9% CGST + 9% SGST",
    "tax_amount": 280260.00,
    "grand_total": 1837260.00,
    "inclusions": [
        "Full brass and silver-plated dining setup & bone china",
        "40 uniformed banquet staff and 4 supervisory captains",
        "Dedicated 62.5 kVA acoustic sound & power generator with 8 hrs diesel",
        "Live cooking counters and breakdown within 3 hours",
        "Hygienic RO mineral water and food-grade ice carving stations",
    ],
    "exclusions": [
        "Alcoholic beverages & excise bar serving permits",
        "Overtime service extending past 1:00 AM (billed @ INR 12,000/hr)",
        "Venue lawn clearance deposit (payable directly to Oberoi Rajvilas)",
    ],
    "power_and_overtime_policy": "Dedicated 62.5 kVA acoustic silent generator included with 8 hours fuel. Overtime past 1:00 AM charged at INR 12,000/hr.",
    "payment_terms": "30% booking advance upon signing; 50% 14 days prior to event; 20% on the morning of 14 November 2026.",
}

# ==============================================================================
# VENDOR 2: Saffron Table Gourmet Catering Services
# ==============================================================================
v2_data = {
    "vendor_name": "Saffron Table Gourmet Catering Services",
    "address": "B-12, Vaishali Nagar, Jaipur 302021",
    "gstin": "08AAGCS9912L1ZY",
    "contact_person": "Vikram Rao",
    "phone": "+91 98290 11223",
    "email": "vikram@saffrontable.in",
    "quotation_no": "ST-2026-NOV-114",
    "issue_date": "2026-10-18",
    "validity": "Valid for 21 days (Until 08 Nov 2026)",
    "client_names": "Mehra × Kapoor Wedding Reception",
    "event_name": "Luxury Awadhi & Pan-Indian Reception",
    "dates": "14–16 November 2026",
    "venue": "The Oberoi Rajvilas",
    "city": "Jaipur",
    "category": "catering",
    "guest_count": 420,
    "line_items": [
        {
            "description": "Signature Awadhi & Pan-Indian Buffet Spread (420 guests)",
            "quantity": 420,
            "unit": "plate",
            "unit_price": 3200.00,
            "line_total": 1344000.00,
        },
        {
            "description": "Live Sigri Kebab & Lucknowi Tandoor Station",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 400.00,
            "line_total": 168000.00,
        },
        {
            "description": "Gourmet Dessert Studio with Nitrogen Ice Cream Station",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 300.00,
            "line_total": 126000.00,
        },
    ],
    "additional_charges_rows": [
        {
            "description": "Kitchen Logistics, Refrigerated Van Transport & Freight",
            "quantity": 1,
            "unit": "lump_sum",
            "unit_price": 25000.00,
            "line_total": 25000.00,
        },
        {
            "description": "Dedicated Acoustic Generator: EXCLUDED (Client must arrange independently)",
            "quantity": 1,
            "unit": "unit",
            "unit_price": 0.00,
            "line_total": 0.00,
        },
    ],
    "subtotal": 1638000.00,
    "additional_charges_total": 25000.00,
    "gst_rate_percent": 18,
    "gst_breakdown": "9% CGST + 9% SGST",
    "tax_amount": 299340.00,
    "grand_total": 1962340.00,
    "inclusions": [
        "Premium German porcelain tableware and gold-rimmed crystal glassware",
        "50 executive banquet servers and 5 certified floor managers",
        "Full kitchen setup, chafers, induction food warmers",
        "Complimentary 3-tier custom wedding cake",
    ],
    "exclusions": [
        "Acoustic power generator (Venue power hookup or generator must be client arranged)",
        "Liquor license handling & bar refrigeration units",
        "Overtime service past midnight (billed @ INR 15,000/hr)",
    ],
    "power_and_overtime_policy": "Power backup generator excluded. Client must arrange minimum 60 kVA. Overtime after 12:00 midnight @ INR 15,000/hr.",
    "payment_terms": "50% non-refundable booking deposit; 40% 7 days prior to event; 10% post-event within 24 hours.",
}

# ==============================================================================
# VENDOR 3: Heritage Mewar Culinary Arts
# ==============================================================================
v3_data = {
    "vendor_name": "Heritage Mewar Culinary Arts",
    "address": "15, City Palace Road, Udaipur 313001",
    "gstin": "08AAUHM7741P1ZB",
    "contact_person": "Arjun Singh Mewari",
    "phone": "+91 98291 44556",
    "email": "orders@heritagemewar.com",
    "quotation_no": "HMC-2026-881",
    "issue_date": "2026-10-20",
    "validity": "Valid for 15 days (Until 04 Nov 2026)",
    "client_names": "Mehra × Kapoor Wedding Reception",
    "event_name": "Royal Feast & Mewari Banquet",
    "dates": "14–16 November 2026",
    "venue": "The Oberoi Rajvilas",
    "city": "Jaipur",
    "category": "catering",
    "guest_count": 420,
    "line_items": [
        {
            "description": "Heritage Mewari Thali & Buffet Spread (420 guests basis)",
            "quantity": 420,
            "unit": "plate",
            "unit_price": 2600.00,
            "line_total": 1092000.00,
        },
        {
            "description": "Live Dal Baati Churma, Gatte & Ker Sangri Counter",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 250.00,
            "line_total": 105000.00,
        },
        {
            "description": "Traditional Halwai Live Sweet Counter (Imarti, Rabdi, Jalebi)",
            "quantity": 420,
            "unit": "pax",
            "unit_price": 200.00,
            "line_total": 84000.00,
        },
    ],
    "additional_charges_rows": [
        {
            "description": "Unbundled Service Crew Staffing Fee (40 servers)",
            "quantity": 1,
            "unit": "lump_sum",
            "unit_price": 60000.00,
            "line_total": 60000.00,
        },
        {
            "description": "Kitchen Transport & Freight from Udaipur Base to Jaipur",
            "quantity": 1,
            "unit": "lump_sum",
            "unit_price": 35000.00,
            "line_total": 35000.00,
        },
        {
            "description": "Silent Acoustic Generator: Standby only @ INR 50,000 + GST extra",
            "quantity": 1,
            "unit": "unit",
            "unit_price": 0.00,
            "line_total": 0.00,
        },
    ],
    "subtotal": 1281000.00,
    "additional_charges_total": 95000.00,
    "gst_rate_percent": 18,
    "gst_breakdown": "9% CGST + 9% SGST",
    "tax_amount": 247680.00,
    "grand_total": 1623680.00,
    "inclusions": [
        "Traditional copper and brass serving vessels",
        "Raw grocery materials and authentic Rajasthani spices",
        "Live clay oven and tandoor setup",
    ],
    "exclusions": [
        "Service waitstaff unbundled (billed separately as INR 60,000)",
        "Acoustic power generator not included (available on request @ INR 50,000 + GST)",
        "Overtime beyond 11:30 PM charged at INR 20,000 per hour",
    ],
    "power_and_overtime_policy": "Generator available on request for INR 50,000 extra + GST. Overtime past 11:30 PM charged at INR 20,000/hr.",
    "payment_terms": "70% booking advance upon contract signing; 30% 15 days prior to event date. 100% upfront required.",
}

# Run generation
p1 = create_pdf("royal_rajputana_catering_quote.pdf", v1_data)
p2 = create_pdf("saffron_table_catering_quote.pdf", v2_data)
p3 = create_pdf("heritage_mewar_catering_quote.pdf", v3_data)

# Save ground truth JSON files
for fname, data in [
    ("royal_rajputana_ground_truth.json", v1_data),
    ("saffron_table_ground_truth.json", v2_data),
    ("heritage_mewar_ground_truth.json", v3_data),
]:
    json_path = OUTPUT_DIR / fname
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated ground truth JSON: {json_path}")

print("All 3 demonstration quotation PDFs and ground truth JSON files generated successfully.")
