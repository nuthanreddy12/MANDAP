import uuid
import json
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.models import Wedding, TimelineEvent, Incident, User
from backend.core.auth import get_current_user, verify_wedding_access
from backend.services.schedule_recovery import ScheduleRecoveryEngine

router = APIRouter(prefix="/api/v1/weddings/{wedding_id}", tags=["Timeline & Incidents"])

class IncidentCreatePayload(BaseModel):
    title: str
    vendor_name: Optional[str] = None
    timeline_event_id: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    delay_minutes: int
    notes: Optional[str] = None

class IncidentDecisionPayload(BaseModel):
    notes: Optional[str] = None
    decided_by: Optional[str] = "Nisha Sharma"

DEMO_TIMELINE_EVENTS = [
    {
        "id": "te_dj_arrival",
        "day_number": 2,
        "start_time": "06:00 PM",
        "end_time": "07:00 PM",
        "title": "DJ Arrival & Acoustic Sound Setup",
        "location": "Main Lawn Stage",
        "owner_name": "Nisha",
        "vendor_name": "DJ Ronak",
        "vendor_arrival_status": "expected",
        "is_locked": False,
        "notes": "Console assembly, acoustic balancing and wireless mic synchronization.",
    },
    {
        "id": "te_reception_entry",
        "day_number": 2,
        "start_time": "07:00 PM",
        "end_time": "08:00 PM",
        "title": "Reception Opening & Couple Grand Entry",
        "location": "Grand Ballroom Entrance",
        "owner_name": "Kabir",
        "vendor_name": "Gulab House Decor",
        "vendor_arrival_status": "arrived",
        "is_locked": False,
        "notes": "Pyrotechnics, cold-fire entry, and introductory speeches.",
    },
    {
        "id": "te_dinner_banquet",
        "day_number": 2,
        "start_time": "08:00 PM",
        "end_time": "10:00 PM",
        "title": "Royal Banquet Dinner & Live Counters",
        "location": "Dining Pavilion",
        "owner_name": "Aarav",
        "vendor_name": "Royal Rajputana Hospitality",
        "vendor_arrival_status": "arrived",
        "is_locked": False,
        "notes": "420 guests full banquet service with 14 live culinary stations.",
    },
    {
        "id": "te_performances",
        "day_number": 2,
        "start_time": "09:00 PM",
        "end_time": "10:30 PM",
        "title": "Sangeet Dance Performances & Celebration",
        "location": "Main Stage",
        "owner_name": "Rhea",
        "vendor_name": "DJ Ronak",
        "vendor_arrival_status": "expected",
        "is_locked": False,
        "notes": "Family choreography followed by open dance floor.",
    },
    {
        "id": "te_closing_ceremony",
        "day_number": 2,
        "start_time": "10:30 PM",
        "end_time": "11:00 PM",
        "title": "Closing Ceremony & Curfew Wrap-up",
        "location": "Main Courtyard",
        "owner_name": "Aarav",
        "vendor_name": None,
        "vendor_arrival_status": "expected",
        "is_locked": True,
        "notes": "Strict venue acoustic sound curfew at 10:30 PM. Fixed hard constraint.",
    },
]

@router.get("/timeline")
def get_timeline_events(
    wedding_id: str,
    day_number: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve wedding timeline events."""
    verify_wedding_access(wedding_id, current_user, db, action="view timeline for")
    
    query = db.query(TimelineEvent).filter(TimelineEvent.wedding_id == wedding_id)
    if day_number:
        query = query.filter(TimelineEvent.day_number == day_number)
        
    events = query.order_by(TimelineEvent.day_number, TimelineEvent.start_time).all()
    
    # If no events exist yet for this wedding, return the seeded demonstration scenario
    if not events and wedding_id == "w1":
        # Auto seed if requested or empty
        events = []
        for d in DEMO_TIMELINE_EVENTS:
            evt = TimelineEvent(
                id=d["id"],
                wedding_id="w1",
                day_number=d["day_number"],
                start_time=d["start_time"],
                end_time=d["end_time"],
                title=d["title"],
                location=d["location"],
                owner_name=d["owner_name"],
                vendor_name=d["vendor_name"],
                vendor_arrival_status=d["vendor_arrival_status"],
                is_locked=d["is_locked"],
                notes=d["notes"],
            )
            db.add(evt)
        db.commit()
        events = db.query(TimelineEvent).filter(TimelineEvent.wedding_id == wedding_id).all()

    return [
        {
            "id": e.id,
            "wedding_id": e.wedding_id,
            "day_number": e.day_number,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "title": e.title,
            "location": e.location,
            "owner_name": e.owner_name,
            "vendor_name": e.vendor_name,
            "vendor_arrival_status": e.vendor_arrival_status,
            "delay_minutes": e.delay_minutes,
            "status": e.status,
            "is_locked": e.is_locked,
            "notes": e.notes,
        }
        for e in events
    ]

@router.post("/timeline/seed-demo")
def seed_demo_timeline(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Explicitly reset and seed the 5-event demonstration schedule for Stage 3."""
    verify_wedding_access(wedding_id, current_user, db, action="modify timeline for")
    
    # Remove existing timeline events for w1
    db.query(TimelineEvent).filter(TimelineEvent.wedding_id == wedding_id).delete()
    db.flush()
    
    created = []
    for d in DEMO_TIMELINE_EVENTS:
        evt = TimelineEvent(
            id=d["id"],
            wedding_id=wedding_id,
            day_number=d["day_number"],
            start_time=d["start_time"],
            end_time=d["end_time"],
            title=d["title"],
            location=d["location"],
            owner_name=d["owner_name"],
            vendor_name=d["vendor_name"],
            vendor_arrival_status=d["vendor_arrival_status"],
            is_locked=d["is_locked"],
            notes=d["notes"],
        )
        db.add(evt)
        created.append(evt)
        
    db.commit()
    return {"message": "Demo timeline successfully seeded", "events_count": len(created)}

@router.get("/incidents")
def list_incidents(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List operational incidents and their recovery status."""
    verify_wedding_access(wedding_id, current_user, db, action="view incidents for")
    
    incidents = (
        db.query(Incident)
        .filter(Incident.wedding_id == wedding_id)
        .order_by(Incident.created_at.desc())
        .all()
    )
    
    results = []
    for inc in incidents:
        adjustment_data = None
        if inc.proposed_schedule_adjustment:
            try:
                adjustment_data = json.loads(inc.proposed_schedule_adjustment)
            except Exception:
                adjustment_data = {"explanation": inc.proposed_schedule_adjustment}
                
        results.append({
            "id": inc.id,
            "wedding_id": inc.wedding_id,
            "timeline_event_id": inc.timeline_event_id,
            "vendor_name": inc.vendor_name,
            "title": inc.title,
            "severity": inc.severity,
            "delay_minutes": inc.delay_minutes,
            "affected_activities": inc.affected_activities,
            "status": inc.status,
            "reported_by": inc.reported_by,
            "assigned_to": inc.assigned_to,
            "proposed_schedule_adjustment": adjustment_data,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
        })
    return results

@router.post("/incidents")
def report_incident(
    wedding_id: str,
    payload: IncidentCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Report an operational incident, calculate deterministic recovery schedule,
    and generate natural language briefing via Gemini AI.
    """
    wedding = verify_wedding_access(wedding_id, current_user, db, action="report incident for")
    
    # 1. Fetch current timeline events
    events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.wedding_id == wedding_id)
        .order_by(TimelineEvent.day_number, TimelineEvent.start_time)
        .all()
    )
    
    if not events:
        raise HTTPException(status_code=400, detail="No timeline events found for this wedding.")

    event_dicts = [
        {
            "id": e.id,
            "title": e.title,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "is_locked": e.is_locked,
            "vendor_name": e.vendor_name,
            "owner_name": e.owner_name,
            "location": e.location,
            "status": e.status,
        }
        for e in events
    ]

    # 2. Run Deterministic Python Schedule Recovery Engine
    recovery = ScheduleRecoveryEngine.calculate_recovery(
        events=event_dicts,
        incident_event_id=payload.timeline_event_id,
        vendor_name=payload.vendor_name,
        delay_minutes=payload.delay_minutes,
    )

    # 3. Generate Gemini Briefing
    ai_briefing = ScheduleRecoveryEngine.generate_ai_explanation(
        recovery_data=recovery,
        wedding_name=wedding.couple_names or "Mehta Wedding"
    )
    recovery["ai_briefing"] = ai_briefing

    # 4. Save Incident Record
    inc_id = f"inc_{uuid.uuid4().hex[:8]}"
    affected_str = ", ".join(recovery.get("affected_event_ids", []))
    
    incident = Incident(
        id=inc_id,
        wedding_id=wedding_id,
        timeline_event_id=payload.timeline_event_id,
        vendor_name=payload.vendor_name,
        title=payload.title,
        severity=payload.severity,
        delay_minutes=payload.delay_minutes,
        affected_activities=affected_str,
        status="proposed_recovery",
        reported_by=current_user.name or "Nisha Sharma",
        assigned_to="Kabir",
        proposed_schedule_adjustment=json.dumps(recovery),
    )
    db.add(incident)
    
    # Update timeline event status if target identified
    if payload.timeline_event_id:
        target_evt = db.query(TimelineEvent).filter(TimelineEvent.id == payload.timeline_event_id).first()
        if target_evt:
            target_evt.vendor_arrival_status = "late"
            target_evt.delay_minutes = payload.delay_minutes
            
    db.commit()
    db.refresh(incident)

    return {
        "incident_id": incident.id,
        "status": incident.status,
        "recovery": recovery,
        "ai_briefing": ai_briefing,
        "message": f"Incident recorded. Schedule recovery proposed ({recovery['affected_events_count']} activities affected)."
    }

@router.post("/incidents/{incident_id}/approve")
def approve_recovery(
    wedding_id: str,
    incident_id: str,
    payload: IncidentDecisionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Coordinator approves proposed recovery schedule.
    Updates the live timeline event start/end times in database.
    """
    verify_wedding_access(wedding_id, current_user, db, action="approve recovery for")
    
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id, Incident.wedding_id == wedding_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    if not incident.proposed_schedule_adjustment:
        raise HTTPException(status_code=400, detail="No proposed schedule adjustment found on incident")

    recovery_data = json.loads(incident.proposed_schedule_adjustment)
    proposed_schedule = recovery_data.get("proposed_schedule", [])

    # Apply proposed times to TimelineEvents in DB
    updated_count = 0
    for pe in proposed_schedule:
        evt = db.query(TimelineEvent).filter(TimelineEvent.id == pe["id"]).first()
        if evt and pe.get("is_affected"):
            evt.start_time = pe["proposed_start"]
            evt.end_time = pe["proposed_end"]
            evt.delay_minutes = pe.get("delay_offset_minutes", 0)
            evt.status = "rescheduled"
            updated_count += 1

    incident.status = "approved"
    db.commit()

    return {
        "message": f"Recovery plan approved. {updated_count} timeline events updated in database.",
        "incident_id": incident.id,
        "status": "approved",
        "decided_by": payload.decided_by or current_user.name,
    }

@router.post("/incidents/{incident_id}/reject")
def reject_recovery(
    wedding_id: str,
    incident_id: str,
    payload: IncidentDecisionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Coordinator rejects proposed recovery schedule.
    Original timeline times remain unchanged.
    """
    verify_wedding_access(wedding_id, current_user, db, action="reject recovery for")
    
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id, Incident.wedding_id == wedding_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "rejected"
    db.commit()

    return {
        "message": "Recovery plan rejected. Original timeline remains in effect.",
        "incident_id": incident.id,
        "status": "rejected",
        "decided_by": payload.decided_by or current_user.name,
    }
