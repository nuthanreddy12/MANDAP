from typing import Optional, List
from pydantic import BaseModel, Field, computed_field, ConfigDict

class WeddingBase(BaseModel):
    couple_names: str = Field(..., description="Couple's names, e.g. 'Mehra × Kapoor'")
    title: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    destination: str = "Jaipur"
    dates: str = Field(..., description="Date range e.g. '14 to 16 November 2026'")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    venue: str = "The Oberoi Rajvilas"
    package_type: str = "full_service"
    guest_count: int = 400
    client_budget: float = 0.0
    health_status: str = "on_track"
    assigned_planner: str = "Aarav Mehta"

class WeddingCreate(WeddingBase):
    source_enquiry_id: Optional[str] = None

class WeddingUpdate(BaseModel):
    couple_names: Optional[str] = None
    title: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    destination: Optional[str] = None
    dates: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    venue: Optional[str] = None
    package_type: Optional[str] = None
    guest_count: Optional[int] = None
    client_budget: Optional[float] = None
    health_status: Optional[str] = None
    assigned_planner: Optional[str] = None

class WeddingResponse(WeddingBase):
    id: str
    source_enquiry_id: Optional[str] = None
    is_archived: bool = False
    tasks_completed: int = 0
    tasks_total: int = 0
    assigned_vendors_count: int = 0
    plan_progress_percent: int = 0
    tasks_completed_count: int = 0
    tasks_total_count: int = 0
    vendors_confirmed_count: int = 0
    vendors_target_count: int = 18
    client_collections_amount: float = 0.0
    open_decisions_count: int = 0
    latest_update: str = "Recently updated"

    @computed_field
    @property
    def planner(self) -> str:
        return self.assigned_planner

    model_config = ConfigDict(from_attributes=True)

