import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Vendor, WeddingVendor, Wedding, User
from backend.core.auth import get_current_user
from backend.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse

router = APIRouter(prefix="/api/v1/vendors", tags=["Vendors"])

@router.get("", response_model=List[VendorResponse])
def get_vendors(
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer accounts cannot access internal vendor directory",
        )
    query = db.query(Vendor).filter(Vendor.is_archived == False)
    if category and category.lower() != "all":
        query = query.filter(Vendor.category.ilike(f"%{category}%"))
    if city and city.lower() != "all":
        query = query.filter(Vendor.city.ilike(f"%{city}%"))
    if status and status.lower() != "all":
        query = query.filter(Vendor.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vendor.name.ilike(search_term)) |
            (Vendor.category.ilike(search_term)) |
            (Vendor.city.ilike(search_term))
        )

    vendors = query.order_by(Vendor.name.asc()).all()
    results = []
    for v in vendors:
        weddings = [
            f"{a.wedding.couple_names} ({a.wedding.dates})"
            for a in v.wedding_associations if not a.wedding.is_archived
        ]
        results.append(
            VendorResponse(
                id=v.id,
                name=v.name,
                category=v.category,
                contact_person=v.contact_person,
                phone=v.phone,
                email=v.email,
                city=v.city,
                address=v.address,
                status=v.status,
                notes=v.notes,
                is_archived=v.is_archived,
                quotes_count=4,
                rating="4.9 · Highly rated",
                associated_weddings=weddings,
            )
        )
    return results

@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_id = f"v_{uuid.uuid4().hex[:8]}"
    vendor = Vendor(
        id=new_id,
        name=payload.name,
        category=payload.category,
        contact_person=payload.contact_person,
        phone=payload.phone,
        email=payload.email,
        city=payload.city,
        address=payload.address,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return VendorResponse(
        id=vendor.id,
        name=vendor.name,
        category=vendor.category,
        contact_person=vendor.contact_person,
        phone=vendor.phone,
        email=vendor.email,
        city=vendor.city,
        address=vendor.address,
        status=vendor.status,
        notes=vendor.notes,
        is_archived=vendor.is_archived,
        quotes_count=0,
        rating="5.0 · New partner",
        associated_weddings=[],
    )

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor_by_id(
    vendor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    v = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.is_archived == False).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vendor not found")

    weddings = [
        f"{a.wedding.couple_names} ({a.wedding.dates})"
        for a in v.wedding_associations if not a.wedding.is_archived
    ]

    return VendorResponse(
        id=v.id,
        name=v.name,
        category=v.category,
        contact_person=v.contact_person,
        phone=v.phone,
        email=v.email,
        city=v.city,
        address=v.address,
        status=v.status,
        notes=v.notes,
        is_archived=v.is_archived,
        quotes_count=4,
        rating="4.9 · Highly rated",
        associated_weddings=weddings,
    )

@router.patch("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: str,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    v = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.is_archived == False).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vendor not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(v, field, val)

    db.commit()
    db.refresh(v)

    weddings = [
        f"{a.wedding.couple_names} ({a.wedding.dates})"
        for a in v.wedding_associations if not a.wedding.is_archived
    ]

    return VendorResponse(
        id=v.id,
        name=v.name,
        category=v.category,
        contact_person=v.contact_person,
        phone=v.phone,
        email=v.email,
        city=v.city,
        address=v.address,
        status=v.status,
        notes=v.notes,
        is_archived=v.is_archived,
        quotes_count=4,
        rating="4.9 · Highly rated",
        associated_weddings=weddings,
    )
