import re

with open("backend/api/quotes.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update get_quote_comparison to include Gemini AI intelligence
old_compare_call = """    comparison = compare_quotations(quotes, wedding_guest_count=wedding.guest_count)

    qc = QuoteComparison(
        id=f"qc_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        category=category or "catering",
        comparison_data=comparison["matrix"],
        insights=comparison["insights"],
    )
    db.add(qc)
    db.commit()

    return comparison"""

new_compare_call = """    comparison = compare_quotations(quotes, wedding_guest_count=wedding.guest_count)

    try:
        from backend.services.ai_vendor_intelligence import generate_gemini_vendor_intelligence
        ai_intel = generate_gemini_vendor_intelligence(
            wedding_id=wedding_id,
            category=category or "catering",
            guest_count=wedding.guest_count or 420,
            venue_name=wedding.venue_name or "The Oberoi Udaivilas",
            analyzed_quotes=comparison.get("matrix", []),
        )
        if ai_intel:
            comparison["insights"]["gemini_intelligence"] = ai_intel
    except Exception as e:
        logger.warning(f"Failed to generate Gemini vendor intelligence: {e}")

    qc = QuoteComparison(
        id=f"qc_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        category=category or "catering",
        comparison_data=comparison["matrix"],
        insights=comparison["insights"],
    )
    db.add(qc)
    db.commit()

    return comparison"""

assert old_compare_call in content, "old_compare_call not found in backend/api/quotes.py"
content = content.replace(old_compare_call, new_compare_call, 1)

# 2. Update select_winning_vendor and select_wedding_vendor_quote
old_selection_block = """@router.post("/api/v1/quotes/{quote_id}/select", response_model=VendorSelectionResponse)
def select_winning_vendor(
    quote_id: str,
    payload: VendorSelectionRequest = VendorSelectionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = verify_quote_access(quote_id, current_user, db, action="select")

    wedding_id = quote.wedding_id
    category = quote.category

    existing_selection = db.query(VendorSelection).filter(
        VendorSelection.wedding_id == wedding_id,
        VendorSelection.category == category
    ).first()

    if existing_selection:
        raise HTTPException(
            status_code=400,
            detail=f"Vendor selection already locked for category '{category}' (Quote ID: {existing_selection.quote_id}). Duplicate selection is prevented."
        )

    quote.status = "selected"

    competing = db.query(Quote).filter(
        Quote.wedding_id == wedding_id,
        Quote.category == category,
        Quote.id != quote.id
    ).all()
    for cq in competing:
        cq.status = "closed"

    existing_assignment = db.query(WeddingVendor).filter(
        WeddingVendor.wedding_id == wedding_id,
        WeddingVendor.vendor_id == quote.vendor_id
    ).first()

    if not existing_assignment:
        new_assignment = WeddingVendor(
            id=f"wv_{uuid.uuid4().hex[:8]}",
            wedding_id=wedding_id,
            vendor_id=quote.vendor_id,
            category=category,
            status="confirmed",
        )
        db.add(new_assignment)
    else:
        existing_assignment.status = "confirmed"

    selection_id = f"vs_{uuid.uuid4().hex[:8]}"
    now_str = datetime.datetime.utcnow().isoformat()
    selection = VendorSelection(
        id=selection_id,
        wedding_id=wedding_id,
        vendor_id=quote.vendor_id,
        quote_id=quote.id,
        category=category,
        selected_by=payload.selected_by or current_user.name,
        notes=payload.notes,
    )
    db.add(selection)
    db.commit()

    try:
        create_notification(
            db=db,
            wedding_id=wedding_id,
            recipient_role="staff",
            title="Vendor Contract Selected",
            message=f"Vendor '{quote.vendor_name}' officially selected for '{category}' on {wedding_id}.",
            category="procurement",
            link_url="/quotes",
        )
    except Exception:
        pass

    return VendorSelectionResponse(
        selection_id=selection_id,
        wedding_id=wedding_id,
        vendor_id=quote.vendor_id,
        quote_id=quote.id,
        category=category,
        selected_by=payload.selected_by or current_user.name,
        selected_at=now_str,
        message=f"Vendor '{quote.vendor_name}' approved and assigned to wedding for '{category}'."
    )"""

new_selection_block = """@router.post("/api/v1/quotes/{quote_id}/select", response_model=VendorSelectionResponse)
def select_winning_vendor(
    quote_id: str,
    payload: VendorSelectionRequest = VendorSelectionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    allow_reassign: bool = False,
):
    quote = verify_quote_access(quote_id, current_user, db, action="select")

    wedding_id = quote.wedding_id
    category = quote.category

    existing_selection = db.query(VendorSelection).filter(
        VendorSelection.wedding_id == wedding_id,
        VendorSelection.category == category
    ).first()

    if existing_selection and not payload.reassign and not allow_reassign:
        raise HTTPException(
            status_code=400,
            detail=f"Vendor selection already locked for category '{category}' (Quote ID: {existing_selection.quote_id}). Duplicate selection is prevented."
        )

    now_str = datetime.datetime.utcnow().isoformat()
    if existing_selection:
        selection_id = existing_selection.id
        existing_selection.quote_id = quote.id
        existing_selection.vendor_id = quote.vendor_id
        existing_selection.selected_by = payload.selected_by or current_user.name
        existing_selection.notes = payload.notes or f"Updated winning vendor selection to {quote.vendor_name}"
    else:
        selection_id = f"vs_{uuid.uuid4().hex[:8]}"
        selection = VendorSelection(
            id=selection_id,
            wedding_id=wedding_id,
            vendor_id=quote.vendor_id,
            quote_id=quote.id,
            category=category,
            selected_by=payload.selected_by or current_user.name,
            notes=payload.notes,
        )
        db.add(selection)

    quote.status = "selected"

    competing = db.query(Quote).filter(
        Quote.wedding_id == wedding_id,
        Quote.category == category,
        Quote.id != quote.id
    ).all()
    for cq in competing:
        cq.status = "closed"

    existing_assignment = db.query(WeddingVendor).filter(
        WeddingVendor.wedding_id == wedding_id,
        WeddingVendor.vendor_id == quote.vendor_id
    ).first()

    if not existing_assignment:
        new_assignment = WeddingVendor(
            id=f"wv_{uuid.uuid4().hex[:8]}",
            wedding_id=wedding_id,
            vendor_id=quote.vendor_id,
            category=category,
            status="confirmed",
        )
        db.add(new_assignment)
    else:
        existing_assignment.status = "confirmed"

    other_vendors = db.query(WeddingVendor).filter(
        WeddingVendor.wedding_id == wedding_id,
        WeddingVendor.category == category,
        WeddingVendor.vendor_id != quote.vendor_id
    ).all()
    for ov in other_vendors:
        ov.status = "shortlisted"

    db.commit()

    try:
        create_notification(
            db=db,
            wedding_id=wedding_id,
            recipient_role="staff",
            title="Vendor Contract Selected",
            message=f"Vendor '{quote.vendor_name}' officially selected for '{category}' on {wedding_id}.",
            category="procurement",
            link_url="/quotes",
        )
        create_notification(
            db=db,
            wedding_id=wedding_id,
            recipient_role="finance_manager",
            title="Vendor Contract Approved",
            message=f"Approved quote for {quote.vendor_name} ({category.upper()}) is ready for 3-way invoice reconciliation.",
            category="finance",
            link_url="/finance",
        )
    except Exception:
        pass

    return VendorSelectionResponse(
        selection_id=selection_id,
        wedding_id=wedding_id,
        vendor_id=quote.vendor_id,
        quote_id=quote.id,
        category=category,
        selected_by=payload.selected_by or current_user.name,
        selected_at=now_str,
        message=f"Vendor '{quote.vendor_name}' approved and assigned to wedding for '{category}'."
    )"""

assert old_selection_block in content, "old_selection_block not found in backend/api/quotes.py"
content = content.replace(old_selection_block, new_selection_block, 1)

old_wedding_select = """@router.post("/api/v1/weddings/{wedding_id}/quotes/select", response_model=VendorSelectionResponse)
def select_wedding_vendor_quote(
    wedding_id: str,
    payload: VendorSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    qid = payload.quote_id
    if not qid:
        raise HTTPException(status_code=400, detail="quote_id is required")
    return select_winning_vendor(quote_id=qid, payload=payload, db=db, current_user=current_user)"""

new_wedding_select = """@router.post("/api/v1/weddings/{wedding_id}/quotes/select", response_model=VendorSelectionResponse)
def select_wedding_vendor_quote(
    wedding_id: str,
    payload: VendorSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    qid = payload.quote_id
    if not qid:
        raise HTTPException(status_code=400, detail="quote_id is required")
    return select_winning_vendor(quote_id=qid, payload=payload, db=db, current_user=current_user, allow_reassign=True)"""

assert old_wedding_select in content, "old_wedding_select not found in backend/api/quotes.py"
content = content.replace(old_wedding_select, new_wedding_select, 1)

with open("backend/api/quotes.py", "w", encoding="utf-8") as f:
    f.write(content)

print("backend/api/quotes.py updated successfully.")

