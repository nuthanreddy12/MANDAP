from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.core.database import get_db
from backend.models.models import (
    Wedding,
    Vendor,
    Task,
    Invoice,
    Quote,
    Document,
    Enquiry,
    User,
    TimelineEvent,
)
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/search", tags=["Global Search"])

@router.get("")
def global_search(
    q: str = Query("", min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Permission-aware unified search across all business modules.
    Returns results grouped by module with relevant titles and navigation paths.
    """
    term = q.strip().lower()
    pattern = f"%{term}%"
    results: List[Dict[str, Any]] = []

    # 1. Customer scope restriction
    if current_user.role == "customer":
        # Find customer's wedding
        wedding = db.query(Wedding).filter(
            (Wedding.customer_user_id == current_user.id) |
            (Wedding.client_email.ilike(current_user.email)),
            Wedding.is_archived == False,
        ).first()

        if wedding:
            # Match wedding details
            if term in wedding.couple_names.lower() or term in (wedding.destination or "").lower():
                results.append({
                    "id": wedding.id,
                    "category": "Wedding Sanctuary",
                    "title": wedding.couple_names,
                    "subtitle": f"{wedding.destination} · {wedding.dates or 'Scheduled'}",
                    "status": "active",
                    "link_url": "/customer/dashboard",
                })

            # Match shared timeline events
            events = db.query(TimelineEvent).filter(
                TimelineEvent.wedding_id == wedding.id,
                or_(TimelineEvent.title.ilike(pattern), TimelineEvent.location.ilike(pattern))
            ).all()
            for evt in events:
                results.append({
                    "id": evt.id,
                    "category": "Itinerary Cue",
                    "title": evt.title,
                    "subtitle": f"Day {evt.day_number} · {evt.start_time} - {evt.end_time} · {evt.location}",
                    "status": evt.status,
                    "link_url": "/customer/dashboard",
                })

            # Match shared documents
            docs = db.query(Document).filter(
                Document.wedding_id == wedding.id,
                Document.is_shared_with_client == True,
                Document.filename.ilike(pattern)
            ).all()
            for doc in docs:
                results.append({
                    "id": doc.id,
                    "category": "Guest Document",
                    "title": doc.filename,
                    "subtitle": f"Size: {doc.file_size // 1024} KB · Verified",
                    "status": "ready",
                    "link_url": "/customer/dashboard",
                })

        return {"query": q, "total_results": len(results), "results": results}

    # 2. Staff Roles Scope
    # A. Weddings
    weddings_q = db.query(Wedding).filter(
        Wedding.is_archived == False,
        or_(
            Wedding.couple_names.ilike(pattern),
            Wedding.destination.ilike(pattern),
            Wedding.assigned_planner.ilike(pattern),
            Wedding.client_email.ilike(pattern),
        )
    )
    if current_user.role in ("planner", "coordinator"):
        user_first = current_user.name.split()[0] if current_user.name else ""
        weddings_q = weddings_q.filter(
            (Wedding.assigned_planner.ilike(f"%{current_user.name}%")) |
            (Wedding.assigned_planner.ilike(f"%{user_first}%"))
        )
    for w in weddings_q.limit(5).all():
        results.append({
            "id": w.id,
            "category": "Weddings",
            "title": w.couple_names,
            "subtitle": f"{w.destination} · Assigned: {w.assigned_planner or 'Unassigned'}",
            "status": w.health_status or "on_track",
            "link_url": "/weddings",
        })

    # B. Vendors
    vendors = db.query(Vendor).filter(
        or_(
            Vendor.name.ilike(pattern),
            Vendor.category.ilike(pattern),
            Vendor.city.ilike(pattern),
            Vendor.contact_person.ilike(pattern),
        )
    ).limit(6).all()
    for v in vendors:
        results.append({
            "id": v.id,
            "category": "Vendors",
            "title": v.name,
            "subtitle": f"Category: {v.category.title()} · {v.city}",
            "status": "active",
            "link_url": "/vendors",
        })

    # C. Tasks
    tasks_q = db.query(Task).filter(
        or_(
            Task.title.ilike(pattern),
            Task.owner_name.ilike(pattern),
            Task.stage.ilike(pattern),
        )
    )
    if current_user.role in ("planner", "coordinator"):
        user_first = current_user.name.split()[0] if current_user.name else ""
        tasks_q = tasks_q.filter(
            (Task.owner_name.ilike(f"%{current_user.name}%")) |
            (Task.owner_name.ilike(f"%{user_first}%"))
        )
    for t in tasks_q.limit(6).all():
        results.append({
            "id": t.id,
            "category": "Tasks",
            "title": t.title,
            "subtitle": f"Assignee: {t.owner_name or 'Lead Producer'} · Priority: {t.priority.upper()}",
            "status": t.status,
            "link_url": "/tasks",
        })

    # D. Invoices (Finance Manager & Owner)
    if current_user.role in ("owner", "finance_manager"):
        invoices = db.query(Invoice).filter(
            or_(
                Invoice.invoice_number.ilike(pattern),
                Invoice.vendor_name.ilike(pattern),
                Invoice.discrepancy_note.ilike(pattern),
            )
        ).limit(5).all()
        for inv in invoices:
            results.append({
                "id": inv.id,
                "category": "Invoices",
                "title": f"Invoice {inv.invoice_number}",
                "subtitle": f"Vendor: {inv.vendor_name} · Amount: ₹{float(inv.invoice_total):,.2f}",
                "status": inv.status,
                "link_url": "/finance",
            })

    # E. Enquiries (Planner & Owner)
    if current_user.role in ("owner", "planner"):
        enquiries = db.query(Enquiry).filter(
            or_(
                Enquiry.couple_names.ilike(pattern),
                Enquiry.email.ilike(pattern),
                Enquiry.destination.ilike(pattern),
                Enquiry.phone.ilike(pattern),
            )
        ).limit(5).all()
        for enq in enquiries:
            results.append({
                "id": enq.id,
                "category": "Enquiries",
                "title": enq.couple_names,
                "subtitle": f"Source: {enq.source} · Budget: ₹{float(enq.budget_max or 0):,.2f}",
                "status": enq.status,
                "link_url": "/enquiries",
            })

    # F. Quotations
    quotes = db.query(Quote).filter(
        or_(
            Quote.vendor_name.ilike(pattern),
            Quote.category.ilike(pattern),
            Quote.quotation_number.ilike(pattern),
            Quote.source_filename.ilike(pattern),
        )
    ).limit(5).all()
    for q_item in quotes:
        results.append({
            "id": q_item.id,
            "category": "Quotes",
            "title": f"{q_item.vendor_name} ({q_item.category.title()})",
            "subtitle": f"Total: ₹{float(q_item.total_amount):,.2f} · File: {q_item.source_filename or 'Direct'}",
            "status": q_item.status,
            "link_url": "/quotes",
        })


    # G. Customers & Client Accounts (Owner, Planner, Finance)
    if current_user.role in ("owner", "planner", "finance_manager"):
        client_weddings = db.query(Wedding).filter(
            Wedding.is_archived == False,
            or_(
                Wedding.client_name.ilike(pattern),
                Wedding.client_email.ilike(pattern),
                Wedding.client_phone.ilike(pattern),
            )
        )
        if current_user.role == "planner":
            user_first = current_user.name.split()[0] if current_user.name else ""
            client_weddings = client_weddings.filter(
                (Wedding.assigned_planner.ilike(f"%{current_user.name}%")) |
                (Wedding.assigned_planner.ilike(f"%{user_first}%"))
            )
        for cw in client_weddings.limit(4).all():
            results.append({
                "id": cw.id,
                "category": "Customers",
                "title": cw.client_name or cw.couple_names,
                "subtitle": f"Email: {cw.client_email or 'N/A'} · Phone: {cw.client_phone or 'N/A'} · Wedding: {cw.couple_names}",
                "status": "active",
                "link_url": "/weddings",
            })

    # H. Timeline Events & Ceremonies (All Staff)
    timeline_evts = db.query(TimelineEvent).filter(
        or_(
            TimelineEvent.title.ilike(pattern),
            TimelineEvent.location.ilike(pattern),
            TimelineEvent.vendor_name.ilike(pattern),
        )
    ).limit(5).all()
    for te in timeline_evts:
        results.append({
            "id": te.id,
            "category": "Timeline Events",
            "title": te.title,
            "subtitle": f"Day {te.day_number} ({te.start_time} - {te.end_time}) · Venue: {te.location or 'Main Lawn'} · Vendor: {te.vendor_name or 'Production'}",
            "status": te.status,
            "link_url": "/run-of-show",
        })

    # I. Documents & Statutory Clearances (All Staff)
    docs = db.query(Document).filter(
        Document.filename.ilike(pattern)
    ).limit(5).all()
    for d in docs:
        clean_title = d.filename.replace("_", " ").replace(".pdf", "")
        results.append({
            "id": d.id,
            "category": "Documents",
            "title": clean_title,
            "subtitle": f"File: {d.filename} · Verified Storage",
            "status": d.status,
            "link_url": "/documents",
        })

    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }
