import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.core.database import get_db
from backend.models.models import Notification, User
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    recipient_role: Optional[str] = None
    wedding_id: Optional[str] = None
    title: str
    message: str
    category: str
    link_url: Optional[str] = None
    is_read: bool
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int

def create_notification(
    db: Session,
    title: str,
    message: str,
    category: str = "operational",
    user_id: Optional[str] = None,
    recipient_role: Optional[str] = None,
    wedding_id: Optional[str] = None,
    link_url: Optional[str] = None,
) -> Notification:
    """Helper to persist a notification targeted to a specific user or role."""
    notif = Notification(
        id=f"notif_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        recipient_role=recipient_role,
        wedding_id=wedding_id,
        title=title,
        message=message,
        category=category,
        link_url=link_url,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

@router.get("", response_model=NotificationListResponse)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve notifications scoped to the authenticated user and their role."""
    filters = []

    # Direct notifications for this specific user
    filters.append(Notification.user_id == current_user.id)

    # Role-based notifications
    if current_user.role != "customer":
        filters.append(Notification.recipient_role == current_user.role)
        filters.append(Notification.recipient_role == "all")
        filters.append(Notification.recipient_role == "staff")
        filters.append(Notification.recipient_role == None)
        if current_user.role == "owner":
            # Owner receives all agency staff notifications
            filters.append(Notification.recipient_role.in_(["planner", "coordinator", "finance_manager"]))
    else:
        # Customer only receives customer notifications
        filters.append(Notification.recipient_role == "customer")

    query = db.query(Notification).filter(or_(*filters)).order_by(Notification.created_at.desc())
    items = query.limit(50).all()

    unread_count = sum(1 for n in items if not n.is_read)

    return {
        "notifications": items,
        "unread_count": unread_count,
    }

@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read", "id": notification_id}

@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all eligible notifications for the authenticated user as read."""
    filters = [Notification.user_id == current_user.id]
    if current_user.role != "customer":
        filters.append(Notification.recipient_role == current_user.role)
        filters.append(Notification.recipient_role == "all")
        filters.append(Notification.recipient_role == "staff")
        filters.append(Notification.recipient_role == None)
        if current_user.role == "owner":
            filters.append(Notification.recipient_role.in_(["planner", "coordinator", "finance_manager"]))
    else:
        filters.append(Notification.recipient_role == "customer")

    notifs = db.query(Notification).filter(or_(*filters), Notification.is_read == False).all()
    for n in notifs:
        n.is_read = True
    db.commit()
    return {"message": f"Marked {len(notifs)} notifications as read", "unread_count": 0}
