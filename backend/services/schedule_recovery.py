import re
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import os
import json
from google import genai
from google.genai import types
from backend.core.config import settings

def parse_time_to_minutes(time_str: str) -> int:
    """Parse time string like '6:00 PM', '06:00 PM', '18:00', '18:30' into minutes from midnight."""
    cleaned = time_str.strip().upper()
    match = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", cleaned)
    if not match:
        raise ValueError(f"Invalid time format: '{time_str}'. Expected 'HH:MM AM/PM'.")
    
    hours = int(match.group(1))
    minutes = int(match.group(2))
    meridiem = match.group(3)
    
    if meridiem == "PM" and hours != 12:
        hours += 12
    elif meridiem == "AM" and hours == 12:
        hours = 0
        
    return hours * 60 + minutes

def format_minutes_to_time(minutes: int) -> str:
    """Format minutes from midnight into 12-hour 'HH:MM AM/PM' string."""
    minutes = minutes % (24 * 60)
    hours = minutes // 60
    mins = minutes % 60
    meridiem = "AM" if hours < 12 else "PM"
    
    display_hour = hours % 12
    if display_hour == 0:
        display_hour = 12
        
    return f"{display_hour:02d}:{mins:02d} {meridiem}"


class ScheduleRecoveryEngine:
    """
    Deterministic schedule recovery engine for wedding operations.
    Calculates downstream delay propagations, respects fixed time constraints (locked muhurats/curfews),
    compresses flexible buffers where possible, and identifies unaffected vs affected events.
    """

    @staticmethod
    def calculate_recovery(
        events: List[Dict[str, Any]],
        incident_event_id: Optional[str] = None,
        vendor_name: Optional[str] = None,
        delay_minutes: int = 0,
        buffer_compression_max: int = 15,
    ) -> Dict[str, Any]:
        """
        Deterministic Python schedule recalculation.
        Returns:
            - affected_events
            - unaffected_events
            - proposed_schedule
            - conflicts
            - is_feasible
            - reason_breakdown
        """
        if delay_minutes <= 0:
            return {
                "is_feasible": True,
                "delay_minutes": 0,
                "affected_events": [],
                "unaffected_events": [e["id"] for e in events],
                "proposed_schedule": events,
                "conflicts": [],
                "summary": "No delay reported. Schedule remains intact.",
                "buffer_saved_minutes": 0,
            }

        # Identify target incident event
        target_idx = -1
        if incident_event_id:
            for idx, e in enumerate(events):
                if e["id"] == incident_event_id:
                    target_idx = idx
                    break
        elif vendor_name:
            v_lower = vendor_name.lower()
            for idx, e in enumerate(events):
                if e.get("vendor_name") and v_lower in e["vendor_name"].lower():
                    target_idx = idx
                    break

        if target_idx == -1:
            # Fallback to first event if not found
            target_idx = 0

        target_event = events[target_idx]
        
        # Parse all event times
        parsed_events = []
        for e in events:
            s_min = parse_time_to_minutes(e["start_time"])
            e_min = parse_time_to_minutes(e["end_time"]) if e.get("end_time") else (s_min + 60)
            parsed_events.append({
                **e,
                "start_min": s_min,
                "end_min": e_min,
                "duration_min": e_min - s_min,
                "is_locked": bool(e.get("is_locked", False)),
            })

        conflicts: List[str] = []
        affected_ids: List[str] = []
        unaffected_ids: List[str] = []
        reasons: Dict[str, str] = {}
        proposed_events: List[Dict[str, Any]] = []

        # Current accumulated delay
        current_delay = delay_minutes
        buffer_saved_total = 0

        last_end_min = 0

        for i, pe in enumerate(parsed_events):
            if i < target_idx:
                # Prior events are completely unaffected
                unaffected_ids.append(pe["id"])
                last_end_min = pe["end_min"]
                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": pe["start_time"],
                    "proposed_end": pe["end_time"],
                    "delay_offset_minutes": 0,
                    "is_affected": False,
                    "is_locked": pe["is_locked"],
                    "status": pe.get("status", "upcoming"),
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": "Precedes incident; unaffected.",
                })
                continue

            if i == target_idx:
                # The incident event itself
                affected_ids.append(pe["id"])
                new_start_min = pe["start_min"] + current_delay
                
                # Check if this event duration can be slightly compressed (e.g. sound check from 60m to 45m)
                compression = 0
                if pe["duration_min"] > 30 and buffer_compression_max > 0:
                    compression = min(buffer_compression_max, pe["duration_min"] - 30)
                    buffer_saved_total += compression
                
                new_duration = pe["duration_min"] - compression
                new_end_min = new_start_min + new_duration
                last_end_min = new_end_min
                
                # Propagating delay to downstream events is (new_end_min - pe["end_min"])
                downstream_delay = max(0, new_end_min - pe["end_min"])
                current_delay = downstream_delay

                reasons[pe["id"]] = f"Delayed by {delay_minutes}m due to vendor delay."
                if compression > 0:
                    reasons[pe["id"]] += f" Activity duration compressed by {compression}m to absorb buffer."

                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": format_minutes_to_time(new_start_min),
                    "proposed_end": format_minutes_to_time(new_end_min),
                    "delay_offset_minutes": delay_minutes,
                    "is_affected": True,
                    "is_locked": pe["is_locked"],
                    "status": "delayed",
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": reasons[pe["id"]],
                })
                continue

            # Downstream events (i > target_idx)
            prev_proposed = proposed_events[i - 1]
            prev_end_min = last_end_min

            # Check if this event is a hard locked constraint (e.g. 10:30 PM curfew or muhurat)
            if pe["is_locked"]:
                # Check if preceding event overlaps with this locked event
                if prev_end_min > pe["start_min"]:
                    overlap = prev_end_min - pe["start_min"]
                    conflicts.append(
                        f"CRITICAL CONSTRAINT CONFLICT: Preceding activity '{prev_proposed['title']}' ends at "
                        f"{format_minutes_to_time(prev_end_min)}, which encroaches by {overlap}m on locked event "
                        f"'{pe['title']}' starting at {pe['start_time']}."
                    )
                
                # Locked event cannot move
                unaffected_ids.append(pe["id"])
                last_end_min = pe["end_min"]
                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": pe["start_time"],
                    "proposed_end": pe["end_time"],
                    "delay_offset_minutes": 0,
                    "is_affected": False,
                    "is_locked": True,
                    "status": "locked",
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": "Fixed constraint / curfew; cannot be moved.",
                })
                current_delay = 0  # Cannot propagate past a hard locked barrier
                continue

            if current_delay <= 0:
                # Buffer has absorbed the delay completely
                unaffected_ids.append(pe["id"])
                last_end_min = pe["end_min"]
                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": pe["start_time"],
                    "proposed_end": pe["end_time"],
                    "delay_offset_minutes": 0,
                    "is_affected": False,
                    "is_locked": pe["is_locked"],
                    "status": pe.get("status", "upcoming"),
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": "Protected by upstream buffer absorption; on schedule.",
                })
                continue

            # Dependent non-locked event
            # Start time must be at least prev_end_min
            new_start_min = max(pe["start_min"], prev_end_min)
            shift_minutes = new_start_min - pe["start_min"]

            if shift_minutes > 0:
                affected_ids.append(pe["id"])
                
                # Check if duration can be slightly compressed
                compression = 0
                if pe["duration_min"] > 45 and buffer_compression_max > 0:
                    compression = min(15, pe["duration_min"] - 30)
                    buffer_saved_total += compression

                new_duration = pe["duration_min"] - compression
                new_end_min = new_start_min + new_duration
                last_end_min = new_end_min
                current_delay = max(0, new_end_min - pe["end_min"])

                reason = f"Shifted +{shift_minutes}m to maintain dependency on '{prev_proposed['title']}'."
                if compression > 0:
                    reason += f" Compressed by {compression}m to protect downstream curfew."

                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": format_minutes_to_time(new_start_min),
                    "proposed_end": format_minutes_to_time(new_end_min),
                    "delay_offset_minutes": shift_minutes,
                    "is_affected": True,
                    "is_locked": False,
                    "status": "rescheduled",
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": reason,
                })
            else:
                # Absorbed by the natural gap/buffer
                unaffected_ids.append(pe["id"])
                last_end_min = pe["end_min"]
                current_delay = 0
                proposed_events.append({
                    "id": pe["id"],
                    "title": pe["title"],
                    "original_start": pe["start_time"],
                    "original_end": pe["end_time"],
                    "proposed_start": pe["start_time"],
                    "proposed_end": pe["end_time"],
                    "delay_offset_minutes": 0,
                    "is_affected": False,
                    "is_locked": False,
                    "status": pe.get("status", "upcoming"),
                    "location": pe.get("location"),
                    "vendor_name": pe.get("vendor_name"),
                    "owner_name": pe.get("owner_name", "Coordinator"),
                    "change_reason": f"Buffer absorbed preceding delay; unchanged.",
                })

        is_feasible = (len(conflicts) == 0)

        return {
            "is_feasible": is_feasible,
            "delay_minutes": delay_minutes,
            "incident_event_title": target_event["title"],
            "affected_events_count": len(affected_ids),
            "unaffected_events_count": len(unaffected_ids),
            "affected_event_ids": affected_ids,
            "unaffected_event_ids": unaffected_ids,
            "buffer_saved_minutes": buffer_saved_total,
            "conflicts": conflicts,
            "proposed_schedule": proposed_events,
        }

    @staticmethod
    def generate_ai_explanation(recovery_data: Dict[str, Any], wedding_name: str = "Mehta Wedding") -> str:
        """
        Uses configured Gemini API to generate a professional, clear coordinator briefing
        explaining the calculated recovery schedule and constraint safeguards.
        Falls back cleanly to deterministic explanation if API is unavailable.
        """
        prompt = (
            f"You are the Lead Operations AI for Mandap Luxury Wedding Management.\n"
            f"Review this deterministic schedule recovery plan for {wedding_name} and write a terse, "
            f"factual, 3-4 sentence operational briefing for the on-site coordinators.\n"
            f"Data:\n"
            f"- Incident: {recovery_data.get('incident_event_title')} delayed by {recovery_data.get('delay_minutes')} mins.\n"
            f"- Feasible: {recovery_data.get('is_feasible')}\n"
            f"- Affected Activities ({recovery_data.get('affected_events_count')}): "
            f"{[e['title'] + ' (' + e['original_start'] + ' -> ' + e['proposed_start'] + ')' for e in recovery_data.get('proposed_schedule', []) if e.get('is_affected')]}\n"
            f"- Unaffected Activities ({recovery_data.get('unaffected_events_count')}): "
            f"{[e['title'] for e in recovery_data.get('proposed_schedule', []) if not e.get('is_affected')]}\n"
            f"- Conflicts/Warnings: {recovery_data.get('conflicts')}\n"
            f"- Buffer Compressed: {recovery_data.get('buffer_saved_minutes')} mins\n\n"
            f"Instructions:\n"
            f"Explain clearly what was shifted, how buffers were utilized, and how fixed constraints (like closing curfew or locked ceremonies) were protected. "
            f"Never invent new times; refer only to the calculated times provided."
        )

        api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        model_name = os.environ.get("GEMINI_MODEL") or getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite")

        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=300,
                    )
                )
                if response.text and response.text.strip():
                    return response.text.strip()
            except Exception as e:
                pass

        # Deterministic fallback explanation
        affected = [e for e in recovery_data.get("proposed_schedule", []) if e.get("is_affected")]
        if not affected:
            return f"Delay of {recovery_data.get('delay_minutes')}m was absorbed by existing stage buffers without impacting any scheduled guest activities."

        shift_desc = "; ".join([f"{e['title']} shifted from {e['original_start']} to {e['proposed_start']}" for e in affected])
        conflict_desc = f" WARNING: {recovery_data['conflicts'][0]}" if recovery_data.get("conflicts") else " Fixed closing and locked ceremonies are fully protected."
        return (
            f"{recovery_data.get('incident_event_title')} delayed by {recovery_data.get('delay_minutes')}m. "
            f"Adjusted schedule: {shift_desc}. "
            f"Reclaimed {recovery_data.get('buffer_saved_minutes', 0)}m via buffer compression.{conflict_desc}"
        )
