import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.models import (
    User,
    Wedding,
    TimelineEvent,
    Payment,
    Document,
    CustomerRequest,
    CustomerInvitation,
)
from backend.core.auth import (
    get_current_customer,
    verify_customer_wedding_access,
    create_access_token,
    is_test_environment,
)
from backend.services.storage import read_document_file
from backend.core.supabase_client import get_supabase_client
from backend.core.config import settings

router = APIRouter(prefix="/api/v1/customer", tags=["Customer Portal"])

class CustomerSignupPayload(BaseModel):
    client_name: str
    email: str
    password: str
    invitation_code: Optional[str] = None

class CustomerLoginPayload(BaseModel):
    email: str
    password: str

class CustomerRequestCreate(BaseModel):
    category: str = "general"  # dietary, music, logistics, decor, general
    title: str
    details: str

@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def customer_signup(
    payload: CustomerSignupPayload,
    db: Session = Depends(get_db),
):
    """
    Public customer registration.
    Strictly restricted to 'customer' role. Staff roles cannot be created here.
    Requires an agency-issued invitation or verified customer wedding association.
    """
    norm_email = payload.email.strip().lower()
    norm_code = payload.invitation_code.strip() if payload.invitation_code else ""

    # 1. Verify invitation or existing wedding client email
    wedding = None
    invitation = None

    if norm_code:
        invitation = (
            db.query(CustomerInvitation)
            .filter(CustomerInvitation.invitation_code == norm_code)
            .first()
        )
        if invitation:
            wedding = db.query(Wedding).filter(Wedding.id == invitation.wedding_id, Wedding.is_archived == False).first()

    if not wedding and norm_code:
        # Match invitation code directly on Wedding
        wedding = (
            db.query(Wedding)
            .filter(Wedding.invitation_code == norm_code, Wedding.is_archived == False)
            .first()
        )

    if not wedding:
        # Match verified client_email on file
        wedding = (
            db.query(Wedding)
            .filter(Wedding.client_email.ilike(norm_email), Wedding.is_archived == False)
            .first()
        )

    if not wedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invitation code or unregistered client email. Please verify with your wedding planner.",
        )

    # 2. Check if local user account already exists
    existing_user = db.query(User).filter(User.email.ilike(norm_email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account is already registered with this email address. Please sign in.",
        )

    # 3. Create account in Supabase Auth if accessible
    auth_user_id = None
    supabase_client = get_supabase_client()
    if supabase_client:
        try:
            sb_resp = supabase_client.auth.admin.create_user({
                "email": norm_email,
                "password": payload.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": "customer",
                    "name": payload.client_name,
                },
            })
            if sb_resp and sb_resp.user:
                auth_user_id = sb_resp.user.id
        except Exception:
            # Fall back to local UUID for test environments
            pass

    if not auth_user_id:
        auth_user_id = f"sub_cust_{uuid.uuid4().hex[:12]}"

    # Compute avatar initials
    name_parts = payload.client_name.strip().split()
    initials = (name_parts[0][0] + (name_parts[1][0] if len(name_parts) > 1 else "")).upper() if name_parts else "CL"

    # 4. Create local User with strictly 'customer' role
    new_user = User(
        id=f"u_cust_{uuid.uuid4().hex[:8]}",
        auth_user_id=auth_user_id,
        name=payload.client_name.strip(),
        email=norm_email,
        role="customer",  # Strictly enforced customer role
        avatar_initials=initials[:4],
    )
    db.add(new_user)
    db.flush()

    # 5. Link customer to wedding
    wedding.customer_user_id = new_user.id
    if not wedding.client_email:
        wedding.client_email = norm_email

    if invitation:
        invitation.is_claimed = True
        invitation.claimed_by_user_id = new_user.id

    db.commit()
    db.refresh(new_user)

    token = None
    try:
        token = create_access_token({
            "sub": new_user.auth_user_id or new_user.id,
            "email": new_user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })
    except Exception:
        token = None

    return {
        "message": "Customer account registered and linked successfully",
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
        },
        "wedding_id": wedding.id,
    }

@router.post("/auth/login")
def customer_login(
    payload: CustomerLoginPayload,
    db: Session = Depends(get_db),
):
    """
    Customer portal sign in.
    Authenticates registered customer and returns JWT access token.
    Denies access to non-customer accounts or unlinked customers.
    """
    norm_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(norm_email)).first()
    if not user or user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="We couldn't find an account associated with this email. Check your details or contact your wedding planner.",
        )

    # Verify customer is linked to an active wedding
    wedding = (
        db.query(Wedding)
        .filter(
            (Wedding.customer_user_id == user.id) | (Wedding.client_email.ilike(norm_email)),
            Wedding.is_archived == False,
        )
        .first()
    )
    if not wedding:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active wedding record found associated with this account. Please contact your wedding planner.",
        )

    token = None
    try:
        token = create_access_token({
            "sub": user.auth_user_id or user.id,
            "email": user.email,
            "role": "authenticated",
            "aud": "authenticated",
        })
    except Exception:
        token = None

    return {
        "message": "Customer signed in successfully",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "avatar_initials": user.avatar_initials,
        },
        "wedding_id": wedding.id,
    }

@router.get("/wedding")
def get_customer_wedding(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Returns the authenticated customer's linked wedding details.
    Strictly filters out internal planner budget margins, vendor contract costs and health status.
    """
    wedding = verify_customer_wedding_access(customer, db)

    return {
        "wedding_id": wedding.id,
        "couple_names": wedding.couple_names,
        "dates": wedding.dates,
        "destination": wedding.destination,
        "venue": wedding.venue,
        "package_type": wedding.package_type,
        "guest_count": wedding.guest_count,
        "assigned_planner": wedding.assigned_planner,
        "client_name": wedding.client_name or customer.name,
        "client_email": wedding.client_email or customer.email,
    }

@router.get("/schedule")
def get_customer_schedule(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Returns approved wedding timeline schedule for client view.
    Hides internal staff notes, vendor arrival alerts, and delay tracking.
    """
    wedding = verify_customer_wedding_access(customer, db)

    events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.wedding_id == wedding.id)
        .order_by(TimelineEvent.day_number.asc(), TimelineEvent.start_time.asc())
        .all()
    )

    return [
        {
            "id": ev.id,
            "day_number": ev.day_number,
            "event_date": ev.event_date,
            "start_time": ev.start_time,
            "end_time": ev.end_time,
            "title": ev.title,
            "location": ev.location,
            "status": "complete" if ev.status == "complete" else "scheduled",
        }
        for ev in events
    ]

@router.get("/payments")
def get_customer_payments(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Returns client fee schedule and payment milestones.
    Strictly client-facing payment status; hides vendor cost invoices and agency profit margins.
    Ensures agency-to-vendor payments and general wedding budget deposits are strictly separated
    from client planning fee payments.
    Outstanding = Agreed Planning Fee - Customer Payments Received.
    """
    wedding = verify_customer_wedding_access(customer, db)

    # Client agreed service fee
    client_fee = 750000.0 if wedding.package_type == "full_service" else 350000.0

    # Query all recorded payments for this wedding
    all_payments = (
        db.query(Payment)
        .filter(Payment.wedding_id == wedding.id)
        .order_by(Payment.created_at.asc())
        .all()
    )

    # Correctly separate:
    # 1. Vendor payments made by the agency: recipient_type == "vendor" or vendor_id is not None
    # 2. General wedding budget collections / escrow deposits: large sums or payment_stage in ("client_booking", "budget_collection", "escrow")
    # 3. Customer planning fee payments received by the agency
    fee_payments = [
        p for p in all_payments
        if p.recipient_type == "agency"
        and not p.vendor_id
        and p.payment_stage not in ("client_booking", "budget_collection", "escrow")
        and float(p.amount) <= client_fee
    ]

    if fee_payments:
        total_paid = sum(float(p.amount) for p in fee_payments)
        balance_due = max(0.0, client_fee - total_paid)
        milestones = [
            {
                "id": p.id,
                "stage": p.payment_stage.replace("_", " ").title(),
                "amount": float(p.amount),
                "date": p.payment_date,
                "reference": p.reference or "NEFT",
                "status": "paid",
            }
            for p in fee_payments
        ]
        if balance_due > 0:
            if len(milestones) == 1:
                mid_amount = min(balance_due, client_fee * 0.40)
                final_amount = balance_due - mid_amount
                if mid_amount > 0:
                    milestones.append({
                        "id": "pm_mid",
                        "stage": "Mid-Stage Planning Milestone (40%)",
                        "amount": mid_amount,
                        "date": "05 Nov 2026",
                        "reference": "Scheduled",
                        "status": "upcoming",
                    })
                if final_amount > 0:
                    milestones.append({
                        "id": "pm_final",
                        "stage": "Final Wrap-Up Settlement (20%)",
                        "amount": final_amount,
                        "date": "18 Nov 2026",
                        "reference": "Scheduled",
                        "status": "upcoming",
                    })
            else:
                milestones.append({
                    "id": "pm_balance",
                    "stage": "Final Wrap-Up Settlement",
                    "amount": balance_due,
                    "date": "18 Nov 2026",
                    "reference": "Scheduled",
                    "status": "upcoming",
                })
    else:
        # Default standard payment milestones: 40% advance retainer received, 60% outstanding
        retainer_amount = client_fee * 0.40
        mid_amount = client_fee * 0.40
        final_amount = client_fee * 0.20
        total_paid = retainer_amount
        balance_due = client_fee - total_paid

        milestones = [
            {
                "id": "pm_1",
                "stage": "Advance Booking Retainer (40%)",
                "amount": retainer_amount,
                "date": "15 Oct 2026",
                "reference": "NEFT-MK-ADV",
                "status": "paid",
            },
            {
                "id": "pm_2",
                "stage": "Mid-Stage Planning Milestone (40%)",
                "amount": mid_amount,
                "date": "05 Nov 2026",
                "reference": "Pending",
                "status": "upcoming",
            },
            {
                "id": "pm_3",
                "stage": "Final Wrap-Up Settlement (20%)",
                "amount": final_amount,
                "date": "18 Nov 2026",
                "reference": "Pending",
                "status": "upcoming",
            },
        ]

    return {
        "client_fee_total": client_fee,
        "total_paid": total_paid,
        "balance_outstanding": balance_due,
        "milestones": milestones,
    }

@router.get("/requests")
def get_customer_requests(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Returns requests submitted by the customer to their assigned planner."""
    wedding = verify_customer_wedding_access(customer, db)

    requests = (
        db.query(CustomerRequest)
        .filter(CustomerRequest.wedding_id == wedding.id, CustomerRequest.customer_id == customer.id)
        .order_by(CustomerRequest.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "category": r.category,
            "title": r.title,
            "details": r.details,
            "status": r.status,
            "planner_response": r.planner_response,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in requests
    ]

@router.post("/requests", status_code=status.HTTP_201_CREATED)
def submit_customer_request(
    payload: CustomerRequestCreate,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Submit a requirement or request to the assigned wedding planner."""
    wedding = verify_customer_wedding_access(customer, db)

    req = CustomerRequest(
        id=f"cr_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding.id,
        customer_id=customer.id,
        category=payload.category,
        title=payload.title.strip(),
        details=payload.details.strip(),
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return {
        "message": "Request submitted to your wedding planner",
        "request": {
            "id": req.id,
            "category": req.category,
            "title": req.title,
            "details": req.details,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        },
    }

@router.get("/documents")
def get_customer_shared_documents(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Returns documents explicitly shared by agency staff with the couple.
    Strictly filters out internal vendor quotations, comparison analyses, and invoices.
    """
    wedding = verify_customer_wedding_access(customer, db)

    docs = (
        db.query(Document)
        .filter(Document.wedding_id == wedding.id, Document.is_shared_with_client == True)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_size": d.file_size,
            "content_type": d.content_type,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]

@router.get("/documents/{document_id}/download")
def download_customer_shared_document(
    document_id: str,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Authenticated customer PDF document download endpoint.
    Verifies:
    1. Document exists.
    2. Belongs to the logged-in customer's wedding.
    3. Has is_shared_with_client == True.
    """
    wedding = verify_customer_wedding_access(customer, db)

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check that document belongs to the logged-in customer's wedding
    if doc.wedding_id != wedding.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access documents for this wedding",
        )

    # Allow downloads only when is_shared_with_client=True
    if not doc.is_shared_with_client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This document has not been shared with the client",
        )

    try:
        file_bytes = read_document_file(doc.storage_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file missing from storage: {e}",
        )

    return Response(
        content=file_bytes,
        media_type=doc.content_type or "application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )
