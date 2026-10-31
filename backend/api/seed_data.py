from sqlalchemy.orm import Session
from backend.models.models import (
    User,
    Enquiry,
    Wedding,
    Vendor,
    Task,
    Quote,
    QuoteItem,
    Document,
    TimelineEvent,

    Incident,
    Invoice,
    Payment,
    CustomerInvitation,
)

def seed_initial_data(db: Session):
    # Check if already seeded
    if db.query(Wedding).first():
        return {"message": "Data already seeded"}

    # 1. Users
    aarav = User(id="u1", name="Aarav Mehta", email="aarav@theroyalknot.in", role="owner", avatar_initials="AM")
    nisha = User(id="u2", name="Nisha Sharma", email="nisha@theroyalknot.in", role="planner", avatar_initials="NS")
    kabir = User(id="u3", name="Kabir Verma", email="kabir@theroyalknot.in", role="coordinator", avatar_initials="KV")
    rhea = User(id="u4", name="Rhea Kapoor", email="rhea@theroyalknot.in", role="finance_manager", avatar_initials="RK")
    db.add_all([aarav, nisha, kabir, rhea])

    # 2. Vendors
    v_saffron = Vendor(id="v1", name="Saffron Table", category="catering", contact_person="Vikram Rao", phone="+91 98290 11223", city="Jaipur")
    v_mewar = Vendor(id="v2", name="Mewar Kitchens", category="catering", contact_person="Arjun Singh", phone="+91 98291 44556", city="Udaipur")
    v_marigold = Vendor(id="v3", name="The Marigold Co.", category="catering", contact_person="Sonia Sen", phone="+91 98292 77889", city="Jaipur")
    v_djnova = Vendor(id="v4", name="DJ Nova", category="sound_dj", contact_person="Rohan Das", phone="+91 98293 99001", city="Jaipur")
    v_gulab = Vendor(id="v5", name="Gulab House", category="floral", contact_person="Manish Jain", phone="+91 98294 33221", city="Jaipur")
    v_noor = Vendor(id="v6", name="Noor Events", category="lighting", contact_person="Salim Khan", phone="+91 98295 66778", city="Jaipur")
    v_parkright = Vendor(id="v7", name="ParkRight", category="valet", contact_person="Dharmendra", phone="+91 98296 22110", city="Jaipur")
    db.add_all([v_saffron, v_mewar, v_marigold, v_djnova, v_gulab, v_noor, v_parkright])

    # 3. Weddings
    w1 = Wedding(
        id="w1",
        couple_names="Mehra × Kapoor",
        destination="Jaipur",
        dates="14–16 November 2026",
        package_type="full_service",
        guest_count=420,
        client_budget=18500000.00,  # ₹1.85 Cr
        client_name="Priya Mehra",
        client_email="priya.mehra@gmail.com",
        client_phone="+91 98290 88771",
        invitation_code="ROYAL-MK-2026",
        health_status="on_track",
        assigned_planner="Nisha Sharma",
    )
    w2 = Wedding(
        id="w2",
        couple_names="Rathore × Singh",
        destination="Udaipur",
        dates="21–22 November 2026",
        package_type="day_of",
        guest_count=380,
        client_budget=9500000.00,
        client_name="Divya Rathore",
        client_email="divya.rathore@gmail.com",
        client_phone="+91 98291 22334",
        invitation_code="ROYAL-RS-2026",
        health_status="1_open_issue",
        assigned_planner="Kabir Verma",
    )
    w3 = Wedding(
        id="w3",
        couple_names="Sharma × Bansal",
        destination="Jaipur",
        dates="05–07 December 2026",
        package_type="full_service",
        guest_count=500,
        client_budget=22000000.00,
        health_status="needs_review",
        assigned_planner="Aarav Mehta",
    )
    db.add_all([w1, w2, w3])

    # 4. Enquiries (Leads)
    e1 = Enquiry(
        id="e1",
        couple_names="Singhania × Agrawal",
        email="aditya.singhania@gmail.com",
        phone="+91 98111 22334",
        rough_date="January 2027",
        guest_count=450,
        theme="Royal Heritage Palace",
        budget_max=25000000.00,
        destination="Udaipur",
        status="meeting_booked",
        assigned_owner="Aarav Mehta",
        notes="Referred by Oberoi Udaivilas GM. High priority.",
    )
    e2 = Enquiry(
        id="e2",
        couple_names="Bhatia × Sethi",
        email="ananya.bhatia@outlook.com",
        phone="+91 98222 33445",
        rough_date="February 2027",
        guest_count=350,
        theme="Desert Chic Dunes",
        budget_max=15000000.00,
        destination="Jaisalmer",
        status="new",
        assigned_owner="Nisha Sharma",
        notes="Called on Instagram DM for destination wedding.",
    )
    e3 = Enquiry(
        id="e3",
        couple_names="Joshi × Patel",
        email="dev.joshi@gmail.com",
        phone="+91 98333 44556",
        rough_date="March 2027",
        guest_count=500,
        theme="Garden Heritage",
        budget_max=18000000.00,
        destination="Jaipur",
        status="proposal_sent",
        assigned_owner="Kabir Verma",
        notes="Service agreement sent digitally for client review.",
    )
    e4 = Enquiry(
        id="e4",
        couple_names="Malhotra × Khanna",
        email="rohit.m@gmail.com",
        phone="+91 98444 55667",
        rough_date="April 2027",
        guest_count=300,
        theme="Intimate Fort",
        budget_max=12000000.00,
        destination="Jaipur",
        status="qualified",
        assigned_owner="Aarav Mehta",
        notes="Initial consultation completed.",
    )
    db.add_all([e1, e2, e3, e4])

    # 5. Quotes for Mehra × Kapoor (Catering Comparison - Page 6)
    q1 = Quote(
        id="q1",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Saffron Table",
        category="catering",
        total_amount=1470000.00,  # ₹14.7L
        price_per_unit=3500.00,
        guest_count_basis=420,
        scope_summary="12 vegetarian + 4 non-veg items, Service staff included",
        inclusions=["12 vegetarian items", "4 non-veg items", "Full service staff", "Cutlery and glassware"],
        additional_charges=[{"name": "Acoustic Generator", "amount": None, "status": "not_specified"}],
        taxes_detail="18% extra",
        status="complete",
        extraction_status="ready",
        is_recommended=False,
        source_filename="SaffronTable_v2.pdf",
        version="v2",
    )
    q2 = Quote(
        id="q2",
        wedding_id="w1",
        vendor_id="v2",
        vendor_name="Mewar Kitchens",
        category="catering",
        total_amount=1510000.00,  # ₹15.1L
        price_per_unit=3595.00,
        guest_count_basis=420,
        scope_summary="14 vegetarian + 5 non-veg items, Service staff included",
        inclusions=["14 vegetarian items", "5 non-veg items", "Service staff included", "Specialist live chaat counter"],
        exclusions=["Generator: ₹35,000 extra"],
        missing_terms=[],
        additional_charges=[{"name": "Acoustic Generator", "amount": 35000, "status": "extra"}],
        taxes_detail="Included",
        status="complete",
        extraction_status="ready",
        is_recommended=True,
        source_filename="Mewar_quote.pdf",
        version="v1",
    )
    q3 = Quote(
        id="q3",
        wedding_id="w1",
        vendor_id="v3",
        vendor_name="The Marigold Co.",
        category="catering",
        total_amount=1390000.00,  # ₹13.9L
        price_per_unit=None,
        guest_count_basis=None,
        scope_summary="Menu details attached in PDF, Taxes unclear",
        inclusions=["Menu attached in PDF"],
        exclusions=[],
        missing_terms=["Unit price unavailable", "Guest count basis missing", "Taxes unclear"],
        additional_charges=[{"name": "Acoustic Generator", "amount": None, "status": "not_specified"}],
        taxes_detail="Needs review",
        status="needs_review",
        extraction_status="needs_review",
        is_recommended=False,
        source_filename="Marigold_estimate.pdf",
        version="v1",
    )
    db.add_all([q1, q2, q3])
    db.flush()

    # Seed initial items for q1 and q2
    qi1 = QuoteItem(
        id="qi_1", quote_id="q1", original_description="Royal Rajputana Gala Buffet (420 pax)",
        normalized_category="Catering", quantity=420, unit="plate", unit_price=3500, line_total=1470000,
        source_page=1, source_text="Rate per head: INR 3500 x 420 guests = INR 14,70,000",
    )
    qi2 = QuoteItem(
        id="qi_2", quote_id="q2", original_description="Heritage Mewari Banquet & Live Chaat Stations",
        normalized_category="Catering", quantity=420, unit="plate", unit_price=3595, line_total=1509900,
        source_page=1, source_text="Per person inclusive of GST: INR 3,595",
    )
    db.add_all([qi1, qi2])


    # 6. Tasks for Mehra × Kapoor (Generated 25+ wedding plan tasks)
    tasks_seed = [
        ("Approve final menu tasting notes", "catering", "due_soon", "Nisha", "02 Nov"),
        ("Confirm guest transfer manifest", "transport", "in_progress", "Kabir", "04 Nov"),
        ("Venue walk-through at Oberoi Rajvilas", "venue", "scheduled", "Aarav", "Today · 3:30 PM"),
        ("Finalize Mandap floral installation spec", "design", "in_progress", "Nisha", "03 Nov"),
        ("Confirm DJ console & acoustic generator", "vendors", "to_plan", "Kabir", "05 Nov"),
        ("Rehearse bridal entrance procession cue", "big_day", "to_plan", "Rhea", "08 Nov"),
        ("Verify fireworks safety clearance license", "venue", "done", "Aarav", "28 Oct"),
        ("Review vintage car battery & chauffeur route", "transport", "done", "Kabir", "29 Oct"),
        ("Confirm Pandit ji arrival & samagri inventory", "big_day", "in_progress", "Nisha", "06 Nov"),
        ("Coordinate Mehendi artist team arrival", "vendors", "done", "Rhea", "26 Oct"),
        ("Finalize Sangeet dance sequence & audio cues", "big_day", "in_progress", "Kabir", "05 Nov"),
        ("Test cocktail bar refrigeration units", "catering", "to_plan", "Nisha", "07 Nov"),
        ("Distribute welcome hampers to hotel desks", "design", "done", "Rhea", "30 Oct"),
        ("Review valet parking capacity & traffic plan", "vendors", "done", "Kabir", "27 Oct"),
        ("Verify dry ice & cold pyro safety distances", "big_day", "to_plan", "Kabir", "09 Nov"),
        ("Confirm guest dietary allergies with caterer", "catering", "done", "Nisha", "25 Oct"),
        ("Inspect bridal suite preparation & amenities", "venue", "to_plan", "Rhea", "10 Nov"),
        ("Coordinate safa tying turbans team count", "vendors", "to_plan", "Kabir", "11 Nov"),
        ("Conduct audio sound check on Main Lawn", "big_day", "scheduled", "Kabir", "14 Nov"),
        ("Confirm luggage bell desk protocol with resort", "transport", "done", "Aarav", "24 Oct"),
        ("Finalize seating chart for gala banquet", "design", "in_progress", "Nisha", "06 Nov"),
        ("Audit generator fuel reserves for lawn lights", "venue", "to_plan", "Kabir", "12 Nov"),
        ("Confirm photography drone clearance permits", "vendors", "done", "Aarav", "22 Oct"),
        ("Prepare bridal emergency repair kit", "big_day", "done", "Rhea", "31 Oct"),
        ("Coordinate dhol player squad reporting time", "vendors", "to_plan", "Kabir", "13 Nov"),
        ("Verify couple green room air conditioning", "venue", "done", "Nisha", "28 Oct"),
        ("Review banquet master billing sign-off scope", "wrap_up", "to_plan", "Aarav", "16 Nov"),
        ("Schedule final vendor settlement meeting", "wrap_up", "to_plan", "Rhea", "18 Nov"),
        ("Collect client feedback questionnaire", "wrap_up", "to_plan", "Nisha", "20 Nov"),
    ]

    for idx, (title, stage, status, owner, due) in enumerate(tasks_seed):
        t = Task(
            id=f"t{idx+1}",
            wedding_id="w1",
            title=title,
            stage=stage,
            status=status,
            owner_name=owner,
            due_date=due,
        )
        db.add(t)

    # 7. Timeline & Run of Show for Day 2 (15 November)
    t1 = TimelineEvent(
        id="te1",
        wedding_id="w1",
        day_number=2,
        event_date="15 November 2026",
        start_time="03:30 PM",
        end_time="04:00 PM",
        title="Venue handover & perimeter check",
        location="Main Lawn",
        owner_name="Kabir",
        status="complete",
        vendor_name="Gulab House",
        vendor_arrival_status="arrived",
        vendor_arrived_time="03:42 PM",
    )
    t2 = TimelineEvent(
        id="te2",
        wedding_id="w1",
        day_number=2,
        event_date="15 November 2026",
        start_time="04:00 PM",
        end_time="04:45 PM",
        title="Sound check & acoustic balancing",
        location="Main Lawn Stage",
        owner_name="Nisha",
        status="in_progress",
        vendor_name="DJ Nova",
        vendor_arrival_status="late",
        delay_minutes=18,
    )
    t3 = TimelineEvent(
        id="te3",
        wedding_id="w1",
        day_number=2,
        event_date="15 November 2026",
        start_time="04:45 PM",
        end_time="05:30 PM",
        title="Family entry procession rehearsal",
        location="Main Courtyard",
        owner_name="Rhea",
        status="upcoming",
    )
    t4 = TimelineEvent(
        id="te4",
        wedding_id="w1",
        day_number=2,
        event_date="15 November 2026",
        start_time="05:30 PM",
        end_time="06:15 PM",
        title="Guest arrival, welcome drinks & dhol",
        location="East Gate",
        owner_name="Kabir",
        status="upcoming",
        vendor_name="ParkRight",
        vendor_arrival_status="arrived",
        vendor_arrived_time="03:55 PM",
    )
    t5 = TimelineEvent(
        id="te5",
        wedding_id="w1",
        day_number=2,
        event_date="15 November 2026",
        start_time="06:15 PM",
        end_time="07:00 PM",
        title="Jaimala ceremony under floral mandap",
        location="Main Lawn",
        owner_name="Aarav",
        status="upcoming",
        is_locked=True,  # Auspicious Muhurat time locked
        notes="Auspicious Muhurat locked with Pandit ji. Cannot shift.",
    )
    db.add_all([t1, t2, t3, t4, t5])

    # 8. Incident (DJ delay - Page 7)
    inc = Incident(
        id="inc1",
        wedding_id="w1",
        timeline_event_id="te2",
        vendor_name="DJ Nova",
        title="DJ console delayed by 18 minutes",
        severity="high",
        delay_minutes=18,
        affected_activities="Sound check and family rehearsal overlap",
        status="open",
        reported_by="Nisha",
        assigned_to="Kabir",
        proposed_schedule_adjustment="Compress sound check to 25 mins. Shift family rehearsal start by 10 mins without breaching 6:15 PM Jaimala locked Muhurat.",
    )
    db.add(inc)

    # 9. Invoice & Reconciliation for Saffron Table (Page 8)
    inv = Invoice(
        id="inv1",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Saffron Table",
        category="catering",
        invoice_number="INV-104",
        invoice_date="18 November 2026",
        agreed_value=1470000.00,
        approved_extras=42000.00,  # 12 additional plates
        invoice_total=1562000.00,  # includes unapproved ₹50k service charge
        paid_amount=1000000.00,
        status="review_required",
        source_filename="Saffron_Final_INV104.pdf",
        discrepancy_note="Invoice includes a ₹50,000 service charge adjustment not found in the original agreement or approved additions.",
        line_items=[
            {
                "item": "Wedding catering · 420 plates",
                "agreed": 1470000.00,
                "approved": 0.0,
                "invoiced": 1470000.00,
                "status": "matched"
            },
            {
                "item": "Additional plates · 12 plates",
                "agreed": 0.0,
                "approved": 42000.00,
                "invoiced": 42000.00,
                "status": "matched"
            },
            {
                "item": "Service charge adjustment",
                "agreed": "Included",
                "approved": 0.0,
                "invoiced": 50000.00,
                "status": "review_required"
            }
        ]
    )
    db.add(inv)

    # 10. Payments recorded
    p1 = Payment(
        id="p1",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Saffron Table",
        recipient_type="vendor",
        payment_stage="advance",
        amount=500000.00,
        payment_date="10 Oct 2026",
        reference="NEFT-HDFC-992140",
        status="recorded",
    )
    p2 = Payment(
        id="p2",
        wedding_id="w1",
        vendor_id="v1",
        vendor_name="Saffron Table",
        recipient_type="vendor",
        payment_stage="second_payment",
        amount=500000.00,
        payment_date="02 Nov 2026",
        reference="RTGS-ICICI-441092",
        status="recorded",
    )
    # Client collection payment
    p_client = Payment(
        id="pc1",
        wedding_id="w1",
        recipient_type="agency",
        payment_stage="client_booking",
        amount=9200000.00,  # ₹92L collected
        payment_date="15 Sep 2026",
        reference="CLIENT-WIRE-88120",
        status="recorded",
    )
    db.add_all([p1, p2, p_client])

    # 11. Customer Invitations
    inv1 = CustomerInvitation(
        id="cinv_1",
        wedding_id="w1",
        invitation_code="ROYAL-MK-2026",
        client_email="priya.mehra@gmail.com",
        client_name="Priya Mehra",
        is_claimed=False,
    )
    inv2 = CustomerInvitation(
        id="cinv_2",
        wedding_id="w2",
        invitation_code="ROYAL-RS-2026",
        client_email="divya.rathore@gmail.com",
        client_name="Divya Rathore",
        is_claimed=False,
    )
    db.add_all([inv1, inv2])

    # 12. Client-Shared Documents
    doc1 = Document(
        id="doc_client_guide",
        wedding_id="w1",
        filename="Mehra_Kapoor_Wedding_Guest_Guide.pdf",
        file_size=184320,
        file_hash="hash_client_guide_mk_2026",
        storage_path="documents/Mehra_Kapoor_Wedding_Guest_Guide.pdf",
        content_type="application/pdf",
        status="ready",
        is_shared_with_client=True,
    )
    doc2 = Document(
        id="doc_client_menu",
        wedding_id="w1",
        filename="Imperial_Banquet_Tasting_Menu.pdf",
        file_size=122880,
        file_hash="hash_client_menu_mk_2026",
        storage_path="documents/Imperial_Banquet_Tasting_Menu.pdf",
        content_type="application/pdf",
        status="ready",
        is_shared_with_client=True,
    )
    db.add_all([doc1, doc2])

    db.commit()
    return {"message": "The Royal Knot season data successfully seeded"}
