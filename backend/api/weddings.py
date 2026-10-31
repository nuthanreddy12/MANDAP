import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Wedding, Vendor, WeddingVendor, Task, User, Document
from backend.core.auth import get_current_user, verify_wedding_access, verify_customer_wedding_access
from backend.services.storage import read_document_file
from backend.schemas.wedding import WeddingCreate, WeddingUpdate, WeddingResponse
from backend.schemas.vendor import VendorAssignmentCreate, VendorResponse
from backend.api.task_templates import generate_wedding_tasks

router = APIRouter(prefix="/api/v1/weddings", tags=["Weddings"])

@router.get("", response_model=List[WeddingResponse])
def get_weddings(
    destination: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer accounts cannot access agency weddings list",
        )
    query = db.query(Wedding).filter(Wedding.is_archived == False)

    # Scoped access: planners and coordinators only see their assigned weddings
    if current_user.role not in ("owner", "finance_manager"):
        user_first = current_user.name.split()[0] if current_user.name else ""
        query = query.filter(
            (Wedding.assigned_planner.ilike(f"%{current_user.name}%")) |
            (Wedding.assigned_planner.ilike(f"%{user_first}%"))
        )

    if destination and destination.lower() != "all":
        query = query.filter(Wedding.destination.ilike(f"%{destination}%"))
    if status and status.lower() != "all":
        query = query.filter(Wedding.health_status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Wedding.couple_names.ilike(search_term)) |
            (Wedding.destination.ilike(search_term))
        )
    
    weddings = query.order_by(Wedding.created_at.desc()).all()
    results = []
    for w in weddings:
        total_tasks = len(w.tasks)
        done_tasks = len([t for t in w.tasks if t.status == "done"])
        assigned_vendors = len(w.vendor_assignments)
        results.append(
            WeddingResponse(
                id=w.id,
                couple_names=w.couple_names,
                title=w.title,
                client_name=w.client_name,
                client_email=w.client_email,
                client_phone=w.client_phone,
                destination=w.destination,
                dates=w.dates,
                start_date=w.start_date,
                end_date=w.end_date,
                venue=w.venue,
                package_type="Full service" if w.package_type == "full_service" else "Day-of",
                guest_count=w.guest_count,
                client_budget=float(w.client_budget),
                health_status=w.health_status,
                assigned_planner=w.assigned_planner,
                source_enquiry_id=w.source_enquiry_id,
                is_archived=w.is_archived,
                tasks_completed=done_tasks,
                tasks_total=total_tasks,
                assigned_vendors_count=assigned_vendors or 14,
            )
        )
    return results

@router.post("", response_model=WeddingResponse, status_code=status.HTTP_201_CREATED)
def create_wedding(
    payload: WeddingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_id = f"w_{uuid.uuid4().hex[:8]}"
    assigned_planner = payload.assigned_planner or current_user.name or "Aarav Mehta"
    wedding = Wedding(
        id=new_id,
        title=payload.title or f"{payload.couple_names} Wedding",
        couple_names=payload.couple_names,
        client_name=payload.client_name,
        client_email=payload.client_email,
        client_phone=payload.client_phone,
        destination=payload.destination,
        dates=payload.dates,
        start_date=payload.start_date,
        end_date=payload.end_date,
        venue=payload.venue,
        package_type=payload.package_type,
        guest_count=payload.guest_count,
        client_budget=payload.client_budget,
        health_status=payload.health_status,
        assigned_planner=assigned_planner,
        source_enquiry_id=payload.source_enquiry_id,
    )
    db.add(wedding)
    db.flush()

    # Generate 25+ tasks from package template
    tasks = generate_wedding_tasks(db, wedding_id=new_id, package_type=payload.package_type)

    db.commit()
    db.refresh(wedding)

    return WeddingResponse(
        id=wedding.id,
        couple_names=wedding.couple_names,
        title=wedding.title,
        client_name=wedding.client_name,
        client_email=wedding.client_email,
        client_phone=wedding.client_phone,
        destination=wedding.destination,
        dates=wedding.dates,
        start_date=wedding.start_date,
        end_date=wedding.end_date,
        venue=wedding.venue,
        package_type=wedding.package_type,
        guest_count=wedding.guest_count,
        client_budget=float(wedding.client_budget),
        health_status=wedding.health_status,
        assigned_planner=wedding.assigned_planner,
        source_enquiry_id=wedding.source_enquiry_id,
        is_archived=wedding.is_archived,
        tasks_completed=0,
        tasks_total=len(tasks),
        assigned_vendors_count=0,
    )

@router.get("/{wedding_id}", response_model=WeddingResponse)
def get_wedding_by_id(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    w = verify_wedding_access(wedding_id, current_user, db, action="view")

    total_tasks = len(w.tasks)
    done_tasks = len([t for t in w.tasks if t.status == "done"])
    assigned_vendors = len(w.vendor_assignments)

    plan_pct = int((done_tasks / total_tasks * 100)) if total_tasks else 0
    collections = sum(float(p.amount) for p in w.payments if p.recipient_type == "agency") if w.payments else 0.0

    return WeddingResponse(
        id=w.id,
        couple_names=w.couple_names,
        title=w.title,
        client_name=w.client_name,
        client_email=w.client_email,
        client_phone=w.client_phone,
        destination=w.destination,
        dates=w.dates,
        start_date=w.start_date,
        end_date=w.end_date,
        venue=w.venue,
        package_type=w.package_type,
        guest_count=w.guest_count,
        client_budget=float(w.client_budget),
        health_status=w.health_status,
        assigned_planner=w.assigned_planner,
        source_enquiry_id=w.source_enquiry_id,
        is_archived=w.is_archived,
        tasks_completed=done_tasks,
        tasks_total=total_tasks,
        assigned_vendors_count=assigned_vendors,
        plan_progress_percent=plan_pct,
        tasks_completed_count=done_tasks,
        tasks_total_count=total_tasks,
        vendors_confirmed_count=assigned_vendors,
        vendors_target_count=18,
        client_collections_amount=collections,
        open_decisions_count=len([t for t in w.tasks if t.status == "blocked"]),
        latest_update=f"{w.assigned_planner.split()[0] if w.assigned_planner else 'Team'} · Updated",
    )

@router.patch("/{wedding_id}", response_model=WeddingResponse)
def update_wedding(
    wedding_id: str,
    payload: WeddingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    w = verify_wedding_access(wedding_id, current_user, db, action="modify")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(w, field, val)

    db.commit()
    db.refresh(w)

    total_tasks = len(w.tasks)
    done_tasks = len([t for t in w.tasks if t.status == "done"])

    return WeddingResponse(
        id=w.id,
        couple_names=w.couple_names,
        title=w.title,
        client_name=w.client_name,
        client_email=w.client_email,
        client_phone=w.client_phone,
        destination=w.destination,
        dates=w.dates,
        start_date=w.start_date,
        end_date=w.end_date,
        venue=w.venue,
        package_type=w.package_type,
        guest_count=w.guest_count,
        client_budget=float(w.client_budget),
        health_status=w.health_status,
        assigned_planner=w.assigned_planner,
        source_enquiry_id=w.source_enquiry_id,
        is_archived=w.is_archived,
        tasks_completed=done_tasks,
        tasks_total=total_tasks,
        assigned_vendors_count=len(w.vendor_assignments),
    )

@router.post("/{wedding_id}/vendors")
def assign_vendor_to_wedding(
    wedding_id: str,
    payload: VendorAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wedding = verify_wedding_access(wedding_id, current_user, db, action="assign vendor to")

    vendor = db.query(Vendor).filter(Vendor.id == payload.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Check if already assigned
    existing = db.query(WeddingVendor).filter(
        WeddingVendor.wedding_id == wedding_id,
        WeddingVendor.vendor_id == payload.vendor_id
    ).first()

    if existing:
        return {"message": "Vendor already assigned to this wedding", "assignment_id": existing.id}

    assignment = WeddingVendor(
        id=f"wv_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        vendor_id=payload.vendor_id,
        category=payload.category or vendor.category,
        status="assigned",
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": f"Vendor '{vendor.name}' assigned to '{wedding.couple_names}'",
        "assignment_id": assignment.id,
        "vendor_name": vendor.name,
        "category": assignment.category,
    }

@router.get("/{wedding_id}/vendors")
def list_wedding_vendors(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wedding = verify_wedding_access(wedding_id, current_user, db, action="view vendors for")

    assignments = db.query(WeddingVendor).filter(WeddingVendor.wedding_id == wedding_id).all()
    results = []
    for a in assignments:
        v = a.vendor
        results.append({
            "assignment_id": a.id,
            "vendor_id": v.id,
            "name": v.name,
            "category": a.category or v.category,
            "phone": v.phone,
            "city": v.city,
            "status": a.status,
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
        })
    return results

@router.get("/{wedding_id}/documents/{document_id}/download")
def download_wedding_document(
    wedding_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Secure document download endpoint scoped to wedding.
    Supports both staff and authenticated customer access.
    Customers may only download documents marked is_shared_with_client=True for their wedding.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or doc.wedding_id != wedding_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found for this wedding")

    if current_user.role == "customer":
        verify_customer_wedding_access(current_user, db, wedding_id=wedding_id)
        if not doc.is_shared_with_client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This document has not been shared with the client",
            )
    else:
        verify_wedding_access(wedding_id, current_user, db, action="download document for")

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
