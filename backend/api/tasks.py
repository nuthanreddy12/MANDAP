import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Task, Wedding, User
from backend.core.auth import get_current_user, verify_wedding_access, verify_task_access
from backend.api.notifications import create_notification
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(tags=["Tasks"])

@router.get("/api/v1/weddings/{wedding_id}/tasks", response_model=List[TaskResponse])
def get_wedding_tasks(
    wedding_id: str,
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    overdue_only: Optional[bool] = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_wedding_access(wedding_id, current_user, db, action="view tasks for")

    query = db.query(Task).filter(Task.wedding_id == wedding_id)

    if status and status.lower() != "all":
        query = query.filter(Task.status == status)

    if stage and stage.lower() != "all":
        query = query.filter(Task.stage == stage)

    if owner and owner.lower() != "all":
        query = query.filter(Task.owner_name.ilike(f"%{owner}%"))

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    tasks = query.order_by(Task.created_at.asc()).all()

    if overdue_only:
        today_str = datetime.date.today().isoformat()
        tasks = [
            t for t in tasks
            if t.due_date and t.due_date < today_str and t.status != "done"
        ]

    return tasks

@router.post("/api/v1/weddings/{wedding_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_wedding_task(
    wedding_id: str,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wedding = verify_wedding_access(wedding_id, current_user, db, action="create task for")

    new_task = Task(
        id=f"t_{uuid.uuid4().hex[:8]}",
        wedding_id=wedding_id,
        title=payload.title,
        stage=payload.stage or "venue",
        status=payload.status or "to_plan",
        priority=payload.priority or "medium",
        owner_name=payload.owner_name or wedding.assigned_planner or current_user.name or "Aarav",
        due_date=payload.due_date,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    try:
        create_notification(
            db=db,
            title=f"Task Assigned: {new_task.title}",
            message=f"Assigned to {new_task.owner_name} ({new_task.priority.upper()} priority, Stage: {new_task.stage.title()}).",
            category="task",
            recipient_role="planner",
            wedding_id=wedding_id,
            link_url="/tasks",
        )
    except Exception:
        pass

    return new_task

@router.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = verify_task_access(task_id, current_user, db, action="modify")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(task, field, val)

    db.commit()
    db.refresh(task)
    return task

@router.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = verify_task_access(task_id, current_user, db, action="view")
    return task


@router.post("/api/v1/weddings/{wedding_id}/tasks/check-overdue")
def check_overdue_tasks(
    wedding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check for overdue tasks and trigger persistent notifications for planners."""
    verify_wedding_access(wedding_id, current_user, db, action="check overdue tasks for")
    today_str = datetime.date.today().isoformat()
    overdue = (
        db.query(Task)
        .filter(Task.wedding_id == wedding_id, Task.due_date < today_str, Task.status != "done")
        .all()
    )
    for t in overdue:
        create_notification(
            db=db,
            title=f"Overdue Task Alert: {t.title}",
            message=f"Task assigned to {t.owner_name} was due on {t.due_date} ({t.priority.upper()} priority).",
            category="task",
            recipient_role="planner",
            wedding_id=wedding_id,
            link_url="/tasks",
        )
    return {"overdue_count": len(overdue), "tasks": [t.title for t in overdue]}
