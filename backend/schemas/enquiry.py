from typing import Optional
from pydantic import BaseModel, Field, computed_field, ConfigDict

class EnquiryBase(BaseModel):
    couple_names: str = Field(..., description="Couple's names, e.g. 'Singhania × Agrawal'")
    email: Optional[str] = None
    phone: Optional[str] = None
    rough_date: Optional[str] = None
    guest_count: int = 400
    theme: Optional[str] = None
    budget_max: Optional[float] = None
    destination: str = "Jaipur"
    source: str = "Direct Call"
    package_type: str = "full_service"
    status: str = "new"
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    assigned_owner: str = "Aarav Mehta"

class EnquiryCreate(EnquiryBase):
    pass

class EnquiryUpdate(BaseModel):
    couple_names: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    rough_date: Optional[str] = None
    guest_count: Optional[int] = None
    theme: Optional[str] = None
    budget_max: Optional[float] = None
    destination: Optional[str] = None
    source: Optional[str] = None
    package_type: Optional[str] = None
    status: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    assigned_owner: Optional[str] = None
    service_agreement_signed: Optional[bool] = None

class EnquiryResponse(EnquiryBase):
    id: str
    service_agreement_signed: bool = False
    agreement_url: Optional[str] = None
    converted_wedding_id: Optional[str] = None
    is_archived: bool = False

    @computed_field
    @property
    def couple(self) -> str:
        return self.couple_names

    @computed_field
    @property
    def date(self) -> Optional[str]:
        return self.rough_date

    @computed_field
    @property
    def guests(self) -> int:
        return self.guest_count

    @computed_field
    @property
    def budget(self) -> float:
        return float(self.budget_max) if self.budget_max else 0.0

    @computed_field
    @property
    def owner(self) -> str:
        return self.assigned_owner or "Aarav Mehta"

    model_config = ConfigDict(from_attributes=True)

