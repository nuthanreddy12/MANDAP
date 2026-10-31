import pytest
from backend.services.schedule_recovery import (
    parse_time_to_minutes,
    format_minutes_to_time,
    ScheduleRecoveryEngine,
)
from backend.models.models import TimelineEvent, Incident

DEMO_EVENTS = [
    {
        "id": "te_dj",
        "title": "DJ Arrival & Acoustic Sound Setup",
        "start_time": "06:00 PM",
        "end_time": "07:00 PM",
        "is_locked": False,
        "vendor_name": "DJ Ronak",
    },
    {
        "id": "te_reception",
        "title": "Reception Opening & Couple Grand Entry",
        "start_time": "07:00 PM",
        "end_time": "08:00 PM",
        "is_locked": False,
        "vendor_name": "Gulab House Decor",
    },
    {
        "id": "te_dinner",
        "title": "Royal Banquet Dinner & Live Counters",
        "start_time": "08:00 PM",
        "end_time": "10:00 PM",
        "is_locked": False,
        "vendor_name": "Royal Rajputana Hospitality",
    },
    {
        "id": "te_performances",
        "title": "Sangeet Dance Performances & Celebration",
        "start_time": "09:00 PM",
        "end_time": "10:30 PM",
        "is_locked": False,
        "vendor_name": "DJ Ronak",
    },
    {
        "id": "te_closing",
        "title": "Closing Ceremony & Curfew Wrap-up",
        "start_time": "10:30 PM",
        "end_time": "11:00 PM",
        "is_locked": True,
        "vendor_name": None,
    },
]

def test_time_parsing_and_formatting():
    """Verify deterministic 12-hour time parsing and formatting math."""
    assert parse_time_to_minutes("06:00 PM") == 18 * 60
    assert parse_time_to_minutes("6:45 PM") == 18 * 60 + 45
    assert parse_time_to_minutes("10:30 PM") == 22 * 60 + 30
    assert parse_time_to_minutes("12:00 PM") == 12 * 60
    assert parse_time_to_minutes("12:30 AM") == 30
    
    assert format_minutes_to_time(18 * 60) == "06:00 PM"
    assert format_minutes_to_time(18 * 60 + 45) == "06:45 PM"
    assert format_minutes_to_time(22 * 60 + 30) == "10:30 PM"

def test_delayed_vendor_recovery_scenario():
    """
    Demonstration scenario:
    - DJ scheduled 6:00 PM.
    - DJ reports 45-minute delay.
    - Reception scheduled 7:00 PM.
    - Dinner scheduled 8:00 PM.
    - Closing ceremony scheduled 10:30 PM (locked).
    """
    recovery = ScheduleRecoveryEngine.calculate_recovery(
        events=DEMO_EVENTS,
        incident_event_id="te_dj",
        delay_minutes=45,
        buffer_compression_max=15,
    )
    
    assert recovery["is_feasible"] is True
    assert recovery["delay_minutes"] == 45
    assert len(recovery["conflicts"]) == 0
    
    proposed = {e["id"]: e for e in recovery["proposed_schedule"]}
    
    # 1. DJ arrival shifted from 6:00 PM to 6:45 PM
    assert proposed["te_dj"]["proposed_start"] == "06:45 PM"
    # Duration compressed from 60m to 45m (15m buffer compressed) -> ends at 7:30 PM
    assert proposed["te_dj"]["proposed_end"] == "07:30 PM"
    assert proposed["te_dj"]["is_affected"] is True
    
    # 2. Reception Opening shifted from 7:00 PM to 7:30 PM (+30m delay)
    assert proposed["te_reception"]["proposed_start"] == "07:30 PM"
    assert proposed["te_reception"]["is_affected"] is True
    
    # 3. Fixed Closing Ceremony at 10:30 PM is protected and untouched
    assert proposed["te_closing"]["proposed_start"] == "10:30 PM"
    assert proposed["te_closing"]["is_affected"] is False
    assert proposed["te_closing"]["is_locked"] is True
    
    # AI explanation test
    explanation = ScheduleRecoveryEngine.generate_ai_explanation(recovery)
    assert "DJ" in explanation
    assert len(explanation) > 20

def test_delay_that_does_not_affect_downstream_events():
    """Verify that a delay absorbed by a large preceding buffer leaves downstream events untouched."""
    events = [
        {
            "id": "e1",
            "title": "Morning Vendor Delivery",
            "start_time": "09:00 AM",
            "end_time": "09:30 AM",
            "is_locked": False,
        },
        {
            "id": "e2",
            "title": "Afternoon Bridal Mehendi",
            "start_time": "01:00 PM",
            "end_time": "03:00 PM",
            "is_locked": False,
        },
    ]
    
    # Delay e1 by 30 minutes (ends at 10:00 AM)
    recovery = ScheduleRecoveryEngine.calculate_recovery(
        events=events,
        incident_event_id="e1",
        delay_minutes=30,
    )
    
    proposed = {e["id"]: e for e in recovery["proposed_schedule"]}
    assert proposed["e1"]["is_affected"] is True
    assert proposed["e2"]["is_affected"] is False
    assert proposed["e2"]["proposed_start"] == "01:00 PM"
    assert recovery["unaffected_events_count"] == 1

def test_conflict_with_fixed_event():
    """Verify that excessive delay encroaching on a locked event generates a conflict warning."""
    # Delay DJ by 240 minutes (4 hours)
    recovery = ScheduleRecoveryEngine.calculate_recovery(
        events=DEMO_EVENTS,
        incident_event_id="te_dj",
        delay_minutes=240,
    )
    
    assert recovery["is_feasible"] is False
    assert len(recovery["conflicts"]) > 0
    assert "CRITICAL CONSTRAINT CONFLICT" in recovery["conflicts"][0]

def test_multiple_dependent_events_chain():
    """Verify delay ripples sequentially through multiple dependent non-locked activities."""
    events = [
        {"id": "e1", "title": "Setup", "start_time": "04:00 PM", "end_time": "05:00 PM", "is_locked": False},
        {"id": "e2", "title": "Rehearsal", "start_time": "05:00 PM", "end_time": "06:00 PM", "is_locked": False},
        {"id": "e3", "title": "Entry", "start_time": "06:00 PM", "end_time": "07:00 PM", "is_locked": False},
        {"id": "e4", "title": "Dinner", "start_time": "07:00 PM", "end_time": "09:00 PM", "is_locked": False},
    ]
    
    recovery = ScheduleRecoveryEngine.calculate_recovery(
        events=events,
        incident_event_id="e1",
        delay_minutes=30,
        buffer_compression_max=0,  # No compression to test strict chain shift
    )
    
    proposed = {e["id"]: e for e in recovery["proposed_schedule"]}
    assert proposed["e1"]["proposed_start"] == "04:30 PM"
    assert proposed["e2"]["proposed_start"] == "05:30 PM"
    assert proposed["e3"]["proposed_start"] == "06:30 PM"
    assert proposed["e4"]["proposed_start"] == "07:30 PM"
    assert recovery["affected_events_count"] == 4

def test_api_incident_report_and_reject_workflow(client):
    """Test reporting an incident via API and having the coordinator reject it."""
    # 1. Reset / Seed demo schedule
    seed_res = client.post("/api/v1/weddings/w1/timeline/seed-demo")
    assert seed_res.status_code == 200
    
    # 2. Report incident: DJ delayed 45 minutes
    rep_res = client.post(
        "/api/v1/weddings/w1/incidents",
        json={
            "title": "DJ Console Highway Traffic Delay",
            "vendor_name": "DJ Ronak",
            "timeline_event_id": "te_dj_arrival",
            "severity": "high",
            "delay_minutes": 45,
            "notes": "Vehicle stuck near Jaipur bypass",
        }
    )
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    incident_id = rep_data["incident_id"]
    assert rep_data["status"] == "proposed_recovery"
    assert "recovery" in rep_data
    assert "ai_briefing" in rep_data
    
    # 3. Reject the recovery proposal
    rej_res = client.post(
        f"/api/v1/weddings/w1/incidents/{incident_id}/reject",
        json={"notes": "Coordination team opted to use auxiliary sound system instead."}
    )
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "rejected"
    
    # 4. Verify timeline event times were NOT modified in DB
    tl_res = client.get("/api/v1/weddings/w1/timeline")
    assert tl_res.status_code == 200
    events = {e["id"]: e for e in tl_res.json()}
    assert events["te_dj_arrival"]["start_time"] == "06:00 PM"
    assert events["te_reception_entry"]["start_time"] == "07:00 PM"

def test_api_incident_report_and_approve_persistence(client):
    """Test reporting an incident via API and having the coordinator approve and persist it."""
    # 1. Reset / Seed demo schedule
    seed_res = client.post("/api/v1/weddings/w1/timeline/seed-demo")
    assert seed_res.status_code == 200
    
    # 2. Report incident: DJ delayed 45 minutes
    rep_res = client.post(
        "/api/v1/weddings/w1/incidents",
        json={
            "title": "DJ Console Highway Traffic Delay",
            "vendor_name": "DJ Ronak",
            "timeline_event_id": "te_dj_arrival",
            "severity": "high",
            "delay_minutes": 45,
            "notes": "Vehicle stuck near Jaipur bypass",
        }
    )
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    incident_id = rep_data["incident_id"]
    
    # 3. Approve the recovery proposal
    appr_res = client.post(
        f"/api/v1/weddings/w1/incidents/{incident_id}/approve",
        json={"notes": "Approved by Nisha Sharma. Stage captains notified.", "decided_by": "Nisha Sharma"}
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"
    
    # 4. Verify timeline event times ARE updated and persisted in DB
    tl_res = client.get("/api/v1/weddings/w1/timeline")
    assert tl_res.status_code == 200
    events = {e["id"]: e for e in tl_res.json()}
    
    # DJ arrival is now 06:45 PM
    assert events["te_dj_arrival"]["start_time"] == "06:45 PM"
    assert events["te_dj_arrival"]["status"] == "rescheduled"
    
    # Reception entry shifted to 07:30 PM
    assert events["te_reception_entry"]["start_time"] == "07:30 PM"
    
    # Fixed closing ceremony at 10:30 PM was protected and untouched
    assert events["te_closing_ceremony"]["start_time"] == "10:30 PM"
    assert events["te_closing_ceremony"]["is_locked"] is True
