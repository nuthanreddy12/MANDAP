from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    stage: str = Field(default="venue", description="venue, design, catering, vendors, big_day, wrap_up")
    status: str = Field(default="to_plan", description="to_plan, in_progress, blocked, done")
    priority: str = Field(default="medium", description="low, medium, high, critical")
    owner_name: str = "Aarav"
    due_date: Optional[str] = None

class TaskCreate(TaskBase):
    wedding_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_name: Optional[str] = None
    due_date: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    wedding_id: str

    model_config = ConfigDict(from_attributes=True)

