from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class QuoteItemBase(BaseModel):
    original_description: str = Field(..., description="Item description")
    normalized_category: str = Field(default="Catering")
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    tax_info: Optional[str] = None
    line_total: Optional[float] = None
    source_page: Optional[int] = None
    source_text: Optional[str] = None
    confidence: float = 1.0
    is_manually_edited: bool = False

class QuoteItemCreate(QuoteItemBase):
    id: Optional[str] = None

class QuoteItemUpdate(BaseModel):
    original_description: Optional[str] = None
    normalized_category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    tax_info: Optional[str] = None
    line_total: Optional[float] = None

class QuoteItemResponse(QuoteItemBase):
    id: str
    quote_id: str

    model_config = ConfigDict(from_attributes=True)

class QuoteResponse(BaseModel):
    id: str
    wedding_id: str
    vendor_id: str
    vendor_name: str
    category: str
    total_amount: float
    price_per_unit: Optional[float] = None
    guest_count_basis: Optional[int] = None
    quotation_number: Optional[str] = None
    quotation_date: Optional[str] = None
    validity_date: Optional[str] = None
    currency: str = "INR"
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    payment_terms: Optional[str] = None
    scope_summary: Optional[str] = None
    inclusions: List[str] = []
    exclusions: List[str] = []
    missing_terms: List[str] = []
    additional_charges: List[Dict[str, Any]] = []
    taxes_detail: Optional[str] = None
    status: str = "complete"
    extraction_status: str = "ready"
    extraction_error: Optional[str] = None
    is_scanned: bool = False
    human_verified: bool = False
    is_recommended: bool = False
    source_filename: Optional[str] = None
    version: str = "v1"
    uploaded_at: Optional[Any] = None
    items: List[QuoteItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

class QuoteUpdate(BaseModel):
    total_amount: Optional[float] = None
    price_per_unit: Optional[float] = None
    guest_count_basis: Optional[int] = None
    taxes_detail: Optional[str] = None
    scope_summary: Optional[str] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    missing_terms: Optional[List[str]] = None
    additional_charges: Optional[List[Dict[str, Any]]] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None
    human_verified: Optional[bool] = None

class QuoteItemsBulkUpdate(BaseModel):
    items: List[QuoteItemCreate]

class AIJobResponse(BaseModel):
    id: str
    wedding_id: str
    quote_id: Optional[str] = None
    job_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    created_at: Optional[Any] = None
    completed_at: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)

class VendorSelectionRequest(BaseModel):
    quote_id: Optional[str] = None
    category: Optional[str] = None
    rationale: Optional[str] = None
    notes: Optional[str] = None
    selected_by: Optional[str] = "Aarav Mehta"
    reassign: Optional[bool] = False

class VendorSelectionResponse(BaseModel):
    selection_id: str
    wedding_id: str
    vendor_id: str
    quote_id: str
    category: str
    selected_by: str
    selected_at: str
    message: str
