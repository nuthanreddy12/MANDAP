import os
import sys

# 1. Update backend/api/enquiries.py
enquiries_path = "backend/api/enquiries.py"
with open(enquiries_path, "r", encoding="utf-8") as f:
    enq_code = f.read()

if "from backend.api.notifications import create_notification" not in enq_code:
    enq_code = enq_code.replace(
        "from backend.api.task_templates import generate_wedding_tasks",
        "from backend.api.task_templates import generate_wedding_tasks\nfrom backend.api.notifications import create_notification"
    )

if 'category="enquiry"' not in enq_code:
    target = """    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry"""
    replacement = """    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    try:
        create_notification(
            db=db,
            title=f"New Wedding Enquiry: {enquiry.couple_names}",
            message=f"New enquiry for {enquiry.destination or 'Rajasthan'} ({enquiry.guest_count or 400} guests, budget INR {float(enquiry.budget_max or 0):,.2f}). Assigned to {enquiry.assigned_owner}.",
            category="enquiry",
            recipient_role="planner",
            link_url="/enquiries",
        )
    except Exception:
        pass

    return enquiry"""
    enq_code = enq_code.replace(target, replacement)

with open(enquiries_path, "w", encoding="utf-8") as f:
    f.write(enq_code)
print("Updated enquiries.py")

# 2. Update backend/api/tasks.py
tasks_path = "backend/api/tasks.py"
with open(tasks_path, "r", encoding="utf-8") as f:
    tasks_code = f.read()

if "from backend.api.notifications import create_notification" not in tasks_code:
    tasks_code = tasks_code.replace(
        "from backend.core.auth import get_current_user, verify_wedding_access, verify_task_access",
        "from backend.core.auth import get_current_user, verify_wedding_access, verify_task_access\nfrom backend.api.notifications import create_notification"
    )

if 'category="task"' not in tasks_code:
    target_task = """    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task"""
    replacement_task = """    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    try:
        create_notification(
            db=db,
            title=f"Task Assigned: {new_task.title}",
            message=f"Assigned to {new_task.owner_name} ({new_task.priority.upper()} priority, Stage: {new_task.stage.title()}).",
            category="task",
            recipient_role="planner",
            wedding_id=wedding_id,
            link_url="/tasks",
        )
    except Exception:
        pass

    return new_task"""
    tasks_code = tasks_code.replace(target_task, replacement_task)

# Add check-overdue endpoint to tasks.py if not present
if "check_overdue_tasks" not in tasks_code:
    tasks_code += """

@router.post("/api/v1/weddings/{wedding_id}/tasks/check-overdue")
def check_overdue_tasks(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    \"\"\"Check for overdue tasks and trigger persistent notifications for planners.\"\"\"
    verify_wedding_access(wedding_id, current_user, db, action="check overdue tasks for")
    today_str = datetime.date.today().isoformat()
    overdue = (
        db.query(Task)
        .filter(Task.wedding_id == wedding_id, Task.due_date < today_str, Task.status != "done")
        .all()
    )
    for t in overdue:
        create_notification(
            db=db,
            title=f"Overdue Task Alert: {t.title}",
            message=f"Task assigned to {t.owner_name} was due on {t.due_date} ({t.priority.upper()} priority).",
            category="task",
            recipient_role="planner",
            wedding_id=wedding_id,
            link_url="/tasks",
        )
    return {"overdue_count": len(overdue), "tasks": [t.title for t in overdue]}
"""

with open(tasks_path, "w", encoding="utf-8") as f:
    f.write(tasks_code)
print("Updated tasks.py")

# 3. Update backend/api/timeline.py for vendor arrival
timeline_path = "backend/api/timeline.py"
with open(timeline_path, "r", encoding="utf-8") as f:
    timeline_code = f.read()

if "update_vendor_arrival" not in timeline_code:
    timeline_code += """

class VendorArrivalUpdatePayload(BaseModel):
    vendor_arrival_status: str  # "arrived", "expected", "late"
    notes: Optional[str] = None

@router.patch("/timeline/events/{event_id}/arrival")
@router.patch("/events/{event_id}/arrival")
def update_vendor_arrival(
    wedding_id: str,
    event_id: str,
    payload: VendorArrivalUpdatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    \"\"\"Coordinator updates vendor arrival status (arrived / expected / late).\"\"\"
    verify_wedding_access(wedding_id, current_user, db, action="update vendor arrival for")
    evt = db.query(TimelineEvent).filter(TimelineEvent.id == event_id, TimelineEvent.wedding_id == wedding_id).first()
    if not evt:
        raise HTTPException(status_code=404, detail="Timeline event not found")

    evt.vendor_arrival_status = payload.vendor_arrival_status
    if payload.notes:
        evt.notes = payload.notes
    db.commit()
    db.refresh(evt)

    try:
        create_notification(
            db=db,
            title=f"Vendor Arrival Status: {evt.vendor_name or evt.title}",
            message=f"Vendor '{evt.vendor_name or evt.title}' status marked '{payload.vendor_arrival_status.upper()}' at {evt.location or 'Venue'}.",
            category="timeline",
            recipient_role="coordinator",
            wedding_id=wedding_id,
            link_url="/run-of-show",
        )
    except Exception:
        pass

    return evt
"""
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(timeline_code)
    print("Updated timeline.py")

# 4. Update backend/api/finance.py for invoice submission and payment updates
finance_path = "backend/api/finance.py"
with open(finance_path, "r", encoding="utf-8") as f:
    finance_code = f.read()

if "submit_vendor_invoice" not in finance_code:
    finance_code += """

class PaymentCreatePayload(BaseModel):
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    payment_stage: str
    amount: float
    payment_date: str
    reference: Optional[str] = None

@router.post("/invoices", status_code=status.HTTP_201_CREATED)
def submit_vendor_invoice(
    wedding_id: str,
    payload: InvoiceCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    \"\"\"Vendor or finance team submits an official invoice for reconciliation.\"\"\"
    verify_wedding_access(wedding_id, current_user, db, action="submit invoice for")
    inv = Invoice(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=payload.vendor_id,
        vendor_name=payload.vendor_name,
        category=payload.category,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        agreed_value=payload.agreed_value,
        approved_extras=payload.approved_extras,
        invoice_total=payload.invoice_total,
        paid_amount=payload.paid_amount,
        status="submitted",
        source_filename=payload.source_filename,
        line_items=payload.line_items,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    try:
        create_notification(
            db=db,
            title=f"Invoice Submitted: {inv.vendor_name}",
            message=f"Invoice #{inv.invoice_number} submitted for INR {float(inv.invoice_total):,.2f}.",
            category="finance",
            recipient_role="finance_manager",
            wedding_id=wedding_id,
            link_url="/finance",
        )
    except Exception:
        pass

    return inv

@router.post("/payments", status_code=status.HTTP_201_CREATED)
def record_payment_update(
    wedding_id: str,
    payload: PaymentCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    \"\"\"Record a bank transfer or milestone advance payment against a wedding ledger.\"\"\"
    verify_wedding_access(wedding_id, current_user, db, action="record payment for")
    p = Payment(
        id=f"p_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=payload.vendor_id,
        vendor_name=payload.vendor_name,
        recipient_type="vendor",
        payment_stage=payload.payment_stage,
        amount=payload.amount,
        payment_date=payload.payment_date,
        reference=payload.reference,
        status="recorded",
        recorded_by=current_user.name or "Finance Manager",
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    try:
        create_notification(
            db=db,
            title=f"Payment Recorded: {p.vendor_name or 'Vendor'}",
            message=f"Payment of INR {float(p.amount):,.2f} recorded ({p.payment_stage.upper()} - Ref: {p.reference or 'N/A'}).",
            category="finance",
            recipient_role="finance_manager",
            wedding_id=wedding_id,
            link_url="/finance",
        )
    except Exception:
        pass

    return p
"""
    with open(finance_path, "w", encoding="utf-8") as f:
        f.write(finance_code)
    print("Updated finance.py")

# 5. Update backend/api/quotes.py for document upload notifications and client sharing
quotes_path = "backend/api/quotes.py"
with open(quotes_path, "r", encoding="utf-8") as f:
    quotes_code = f.read()

# Add notification in upload_quote_document before return quote
target_quote_return = "    db.commit()\n    db.refresh(quote)\n    return quote"
replacement_quote_return = """    db.commit()
    db.refresh(quote)

    try:
        create_notification(
            db=db,
            title=f"Quotation Uploaded: {quote.vendor_name}",
            message=f"Quotation received for {quote.category.title()} (Total: INR {float(quote.total_amount):,.2f}).",
            category="quote",
            recipient_role="planner",
            wedding_id=wedding_id,
            link_url="/quotes",
        )
    except Exception:
        pass

    return quote"""

if 'title=f"Quotation Uploaded:' not in quotes_code and target_quote_return in quotes_code:
    quotes_code = quotes_code.replace(target_quote_return, replacement_quote_return, 1)

# Add client document share toggle route with customer notification
if "toggle_document_client_share" not in quotes_code:
    quotes_code += """

@router.patch("/api/v1/weddings/{wedding_id}/documents/{document_id}/share")
def toggle_document_client_share(
    wedding_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    \"\"\"Planner shares or unshares a verified document with the client sanctuary.\"\"\"
    doc = verify_document_access(document_id, current_user, db, action="share")
    doc.is_shared_with_client = not doc.is_shared_with_client
    db.commit()
    db.refresh(doc)

    if doc.is_shared_with_client:
        try:
            create_notification(
                db=db,
                title="New Document Shared by Planner",
                message=f"Your lead wedding planner has shared '{doc.filename}' to your wedding sanctuary.",
                category="document",
                recipient_role="customer",
                wedding_id=wedding_id,
                link_url="/customer/dashboard",
            )
        except Exception:
            pass

    return {"message": "Document sharing status updated", "is_shared_with_client": doc.is_shared_with_client}
"""

with open(quotes_path, "w", encoding="utf-8") as f:
    f.write(quotes_code)
print("Updated quotes.py")

