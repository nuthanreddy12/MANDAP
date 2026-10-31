import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Enquiry, Wedding, User
from backend.core.auth import get_current_user
from backend.schemas.enquiry import EnquiryCreate, EnquiryUpdate, EnquiryResponse
from backend.schemas.wedding import WeddingResponse
from backend.api.task_templates import generate_wedding_tasks

router = APIRouter(prefix="/api/v1/enquiries", tags=["Enquiries"])

@router.get("", response_model=List[EnquiryResponse])
def get_enquiries(
    destination: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer accounts cannot access agency enquiries",
        )
    query = db.query(Enquiry).filter(Enquiry.is_archived == False)
    if destination and destination.lower() != "all":
        query = query.filter(Enquiry.destination.ilike(f"%{destination}%"))
    if status and status.lower() != "all":
        query = query.filter(Enquiry.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Enquiry.couple_names.ilike(search_term)) |
            (Enquiry.destination.ilike(search_term)) |
            (Enquiry.notes.ilike(search_term))
        )
    return query.order_by(Enquiry.created_at.desc()).all()

@router.post("", response_model=EnquiryResponse, status_code=status.HTTP_201_CREATED)
def create_enquiry(
    payload: EnquiryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_id = f"e_{uuid.uuid4().hex[:8]}"
    enquiry = Enquiry(
        id=new_id,
        couple_names=payload.couple_names,
        email=payload.email,
        phone=payload.phone,
        rough_date=payload.rough_date,
        guest_count=payload.guest_count,
        theme=payload.theme,
        budget_max=payload.budget_max,
        destination=payload.destination,
        source=payload.source,
        package_type=payload.package_type,
        status=payload.status,
        follow_up_date=payload.follow_up_date,
        notes=payload.notes,
        assigned_owner=payload.assigned_owner or current_user.name or "Aarav Mehta",
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry

@router.get("/{enquiry_id}", response_model=EnquiryResponse)
def get_enquiry_by_id(
    enquiry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id, Enquiry.is_archived == False).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry

@router.patch("/{enquiry_id}", response_model=EnquiryResponse)
def update_enquiry(
    enquiry_id: str,
    payload: EnquiryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id, Enquiry.is_archived == False).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(enquiry, field, val)

    db.commit()
    db.refresh(enquiry)
    return enquiry

@router.post("/{enquiry_id}/convert")
def convert_enquiry_to_wedding(
    enquiry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    if enquiry.converted_wedding_id:
        raise HTTPException(
            status_code=400,
            detail=f"Enquiry already converted to wedding: {enquiry.converted_wedding_id}"
        )

    try:
        wedding_id = f"w_{uuid.uuid4().hex[:8]}"
        wedding = Wedding(
            id=wedding_id,
            title=f"{enquiry.couple_names} Wedding",
            couple_names=enquiry.couple_names,
            client_name=enquiry.couple_names.split("×")[0].strip() if "×" in enquiry.couple_names else enquiry.couple_names,
            client_email=enquiry.email,
            client_phone=enquiry.phone,
            destination=enquiry.destination,
            dates=enquiry.rough_date or "Dates TBD",
            package_type=enquiry.package_type,
            guest_count=enquiry.guest_count,
            client_budget=float(enquiry.budget_max) if enquiry.budget_max else 15000000.0,
            health_status="on_track",
            assigned_planner=enquiry.assigned_owner or current_user.name or "Aarav Mehta",
            source_enquiry_id=enquiry.id,
        )
        db.add(wedding)
        
        enquiry.status = "converted"
        enquiry.converted_wedding_id = wedding_id
        
        db.flush()

        tasks = generate_wedding_tasks(db, wedding_id=wedding_id, package_type=enquiry.package_type)

        db.commit()
        db.refresh(wedding)

        return {
            "message": "Enquiry successfully converted to wedding",
            "wedding_id": wedding.id,
            "couple_names": wedding.couple_names,
            "destination": wedding.destination,
            "package_type": wedding.package_type,
            "tasks_generated": len(tasks),
            "enquiry_status": enquiry.status,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
