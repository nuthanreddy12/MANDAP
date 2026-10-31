import uuid
from typing import List
from sqlalchemy.orm import Session
from backend.models.models import Task

FULL_SERVICE_TEMPLATE = [
    # Venue Stage
    ("Inspect venue layout & perimeter security", "venue", "to_plan", "high", "Aarav Mehta", "10 Oct"),
    ("Review catering staging area & water connections", "venue", "to_plan", "high", "Nisha Sharma", "12 Oct"),
    ("Confirm power generator backup and distribution", "venue", "to_plan", "critical", "Kabir Verma", "15 Oct"),
    ("Verify couple green room air conditioning & amenities", "venue", "done", "medium", "Rhea Kapoor", "28 Oct"),
    ("Verify fireworks and sound clearance licenses", "venue", "done", "critical", "Aarav Mehta", "28 Oct"),
    ("Audit generator fuel reserves for lawn illuminations", "venue", "to_plan", "high", "Kabir Verma", "12 Nov"),

    # Design Stage
    ("Finalize theme color boards & swatch sign-offs", "design", "done", "medium", "Nisha Sharma", "20 Oct"),
    ("Finalize Mandap floral installation spec & 3D render", "design", "in_progress", "critical", "Nisha Sharma", "03 Nov"),
    ("Design custom wedding signage and directional easels", "design", "in_progress", "low", "Rhea Kapoor", "01 Nov"),
    ("Distribute welcome hampers and gift boxes to guest suites", "design", "done", "medium", "Rhea Kapoor", "30 Oct"),
    ("Finalize seating chart & name cards for gala banquet", "design", "in_progress", "high", "Nisha Sharma", "06 Nov"),

    # Catering Stage
    ("Conduct menu tasting and finalize live counters", "catering", "due_soon", "critical", "Nisha Sharma", "02 Nov"),
    ("Confirm guest dietary allergies & Jain food requirements", "catering", "done", "high", "Nisha Sharma", "25 Oct"),
    ("Test cocktail bar refrigeration units and ice machines", "catering", "to_plan", "medium", "Nisha Sharma", "07 Nov"),
    ("Audit banquet cutlery, copper chafing dishes & linen count", "catering", "to_plan", "medium", "Kabir Verma", "08 Nov"),

    # Vendors Stage
    ("Review vintage car battery & chauffeur route", "vendors", "done", "medium", "Kabir Verma", "29 Oct"),
    ("Confirm DJ console & acoustic generator clearance", "vendors", "to_plan", "high", "Kabir Verma", "05 Nov"),
    ("Coordinate Mehendi artist team reporting time", "vendors", "done", "medium", "Rhea Kapoor", "26 Oct"),
    ("Review valet parking capacity & traffic marshals", "vendors", "done", "high", "Kabir Verma", "27 Oct"),
    ("Confirm photography drone clearance permits with local police", "vendors", "done", "critical", "Aarav Mehta", "22 Oct"),
    ("Coordinate safa tying turbans team count & fabric check", "vendors", "to_plan", "low", "Kabir Verma", "11 Nov"),
    ("Coordinate dhol player squad reporting and stage cue", "vendors", "to_plan", "medium", "Kabir Verma", "13 Nov"),

    # Big Day Stage
    ("Conduct audio sound check on Main Lawn stage", "big_day", "to_plan", "critical", "Kabir Verma", "14 Nov"),
    ("Rehearse bridal entrance procession cue & lighting track", "big_day", "to_plan", "high", "Rhea Kapoor", "08 Nov"),
    ("Confirm Pandit ji arrival & auspicious samagri inventory", "big_day", "in_progress", "critical", "Nisha Sharma", "06 Nov"),
    ("Verify dry ice & cold pyro safety distances", "big_day", "to_plan", "high", "Kabir Verma", "09 Nov"),
    ("Prepare bridal emergency repair kit and steam iron", "big_day", "done", "medium", "Rhea Kapoor", "31 Oct"),

    # Wrap Up Stage
    ("Review banquet master billing sign-off scope with hotel", "wrap_up", "to_plan", "high", "Aarav Mehta", "16 Nov"),
    ("Schedule final vendor settlement meeting", "wrap_up", "to_plan", "high", "Rhea Kapoor", "18 Nov"),
    ("Collect client feedback questionnaire & gift handover", "wrap_up", "to_plan", "low", "Nisha Sharma", "20 Nov"),
]

DAY_OF_TEMPLATE = [
    ("Inspect venue layout & handover check", "venue", "to_plan", "high", "Kabir Verma", "Day 1"),
    ("Confirm power generator backup", "venue", "to_plan", "critical", "Kabir Verma", "Day 1"),
    ("Verify couple green room access", "venue", "to_plan", "medium", "Rhea Kapoor", "Day 1"),
    ("Confirm Mandap floral readiness", "design", "to_plan", "high", "Nisha Sharma", "Day 1"),
    ("Place directional signage at hotel gates", "design", "to_plan", "low", "Rhea Kapoor", "Day 1"),
    ("Check banquet table arrangement", "design", "to_plan", "medium", "Nisha Sharma", "Day 1"),
    ("Confirm caterer staff reporting count", "catering", "to_plan", "high", "Nisha Sharma", "Day 1"),
    ("Inspect live counter preparation", "catering", "to_plan", "medium", "Nisha Sharma", "Day 1"),
    ("Verify bar stock and glassware", "catering", "to_plan", "medium", "Nisha Sharma", "Day 1"),
    ("Check DJ console placement & sound check", "vendors", "to_plan", "critical", "Kabir Verma", "Day 1"),
    ("Verify valet drivers stationed at entrance", "vendors", "to_plan", "high", "Kabir Verma", "Day 1"),
    ("Confirm photographer briefing on family shots", "vendors", "to_plan", "high", "Aarav Mehta", "Day 1"),
    ("Coordinate dhol team reporting time", "vendors", "to_plan", "medium", "Kabir Verma", "Day 1"),
    ("Coordinate safa tying master", "vendors", "to_plan", "low", "Kabir Verma", "Day 1"),
    ("Verify vintage car arrival", "vendors", "to_plan", "medium", "Kabir Verma", "Day 1"),
    ("Check makeup artist room lighting", "vendors", "to_plan", "medium", "Rhea Kapoor", "Day 1"),
    ("Conduct stage acoustic balancing", "big_day", "to_plan", "high", "Kabir Verma", "Day 1"),
    ("Brief bridal party on entry timeline", "big_day", "to_plan", "high", "Rhea Kapoor", "Day 1"),
    ("Confirm Pandit ji arrival on Mandap", "big_day", "to_plan", "critical", "Nisha Sharma", "Day 1"),
    ("Check varmala garlands chilled and fresh", "big_day", "to_plan", "critical", "Rhea Kapoor", "Day 1"),
    ("Test cold pyro triggers for stage entrance", "big_day", "to_plan", "high", "Kabir Verma", "Day 1"),
    ("Manage guest movement from courtyard to lawn", "big_day", "to_plan", "high", "Kabir Verma", "Day 1"),
    ("Monitor buffet opening on time", "big_day", "to_plan", "high", "Nisha Sharma", "Day 1"),
    ("Oversee Jaimala music cue synchronization", "big_day", "to_plan", "critical", "Aarav Mehta", "Day 1"),
    ("Coordinate family photo stage queue", "big_day", "to_plan", "medium", "Rhea Kapoor", "Day 1"),
    ("Reconcile hotel banquet master sheet", "wrap_up", "to_plan", "high", "Aarav Mehta", "Day 2"),
    ("Coordinate vendor equipment load-out", "wrap_up", "to_plan", "medium", "Kabir Verma", "Day 2"),
]

def generate_wedding_tasks(db: Session, wedding_id: str, package_type: str = "full_service") -> List[Task]:
    """
    Idempotent task generation. If tasks already exist for this wedding,
    return existing tasks without creating duplicates.
    """
    existing_tasks = db.query(Task).filter(Task.wedding_id == wedding_id).all()
    if existing_tasks and len(existing_tasks) >= 25:
        return existing_tasks

    template = FULL_SERVICE_TEMPLATE if package_type == "full_service" else DAY_OF_TEMPLATE
    created_tasks = []

    for item in template:
        title, stage, status, priority, owner, due = item
        task = Task(
            id=str(uuid.uuid4())[:8],
            wedding_id=wedding_id,
            title=title,
            stage=stage,
            status=status,
            priority=priority,
            owner_name=owner,
            due_date=due,
        )
        db.add(task)
        created_tasks.append(task)

    db.commit()
    return created_tasks
