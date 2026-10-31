from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class VendorBase(BaseModel):
    name: str = Field(..., description="Vendor Business Name")
    category: str = Field(..., description="Catering, Decoration, Photography, DJ and entertainment, Makeup, Transportation, Venue, Lighting, Other")
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: str = "Jaipur"
    address: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class VendorAssignmentCreate(BaseModel):
    vendor_id: str
    category: Optional[str] = None

class VendorResponse(VendorBase):
    id: str
    is_archived: bool = False
    quotes_count: int = 0
    rating: str = "4.9 · Highly rated"
    associated_weddings: List[str] = []

    model_config = ConfigDict(from_attributes=True)

