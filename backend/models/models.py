import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship
from backend.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    auth_user_id = Column(String, unique=True, index=True, nullable=True)  # Supabase Auth UUID (sub)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="planner")  # owner, planner, coordinator, finance_manager
    avatar_initials = Column(String(4), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(String, primary_key=True, index=True)
    couple_names = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    rough_date = Column(String, nullable=True)
    guest_count = Column(Integer, default=400)
    theme = Column(String, nullable=True)
    budget_max = Column(Numeric(12, 2), nullable=True)
    destination = Column(String, default="Jaipur")
    source = Column(String, default="Direct Call")  # Call, WhatsApp, Instagram, Referral, Website
    package_type = Column(String, default="full_service")  # full_service, day_of
    status = Column(String, default="new")  # new, qualified, meeting_booked, proposal_sent, converted, lost
    follow_up_date = Column(String, nullable=True)
    service_agreement_signed = Column(Boolean, default=False)
    agreement_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    assigned_owner = Column(String, default="Aarav Mehta")
    converted_wedding_id = Column(String, ForeignKey("weddings.id"), nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Wedding(Base):
    __tablename__ = "weddings"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=True)
    couple_names = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    destination = Column(String, default="Jaipur")
    dates = Column(String, nullable=False)  # e.g., "14–16 November 2026"
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    venue = Column(String, default="The Oberoi Rajvilas")
    package_type = Column(String, default="full_service")  # full_service, day_of
    guest_count = Column(Integer, default=400)
    client_budget = Column(Numeric(12, 2), default=0.0)
    health_status = Column(String, default="on_track")  # on_track, 1_open_issue, needs_review
    assigned_planner = Column(String, default="Aarav Mehta")
    source_enquiry_id = Column(String, nullable=True)
    customer_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    invitation_code = Column(String, nullable=True, unique=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="wedding", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="wedding", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="wedding", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="wedding", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="wedding", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="wedding", cascade="all, delete-orphan")
    vendor_assignments = relationship("WeddingVendor", back_populates="wedding", cascade="all, delete-orphan")
    customer_requests = relationship("CustomerRequest", back_populates="wedding", cascade="all, delete-orphan")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # Catering, Decoration, Photography, DJ and entertainment, Makeup, Transportation, Venue, Lighting, Other
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    city = Column(String, default="Jaipur")
    address = Column(String, nullable=True)
    status = Column(String, default="active")  # active, inactive, needs_review
    notes = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding_associations = relationship("WeddingVendor", back_populates="vendor")

class WeddingVendor(Base):
    __tablename__ = "wedding_vendors"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, default="assigned")  # assigned, contracted, confirmed, completed
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="vendor_assignments")
    vendor = relationship("Vendor", back_populates="wedding_associations")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    title = Column(String, nullable=False)
    stage = Column(String, default="venue")  # venue, design, catering, vendors, big_day, wrap_up
    status = Column(String, default="to_plan")  # to_plan, in_progress, blocked, done
    priority = Column(String, default="medium")  # low, medium, high, critical
    owner_name = Column(String, default="Aarav")
    due_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="tasks")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    file_hash = Column(String, index=True, nullable=False)  # SHA-256
    storage_path = Column(String, nullable=False)
    content_type = Column(String, default="application/pdf")
    status = Column(String, default="uploaded")  # uploaded, extracting, ready, failed
    is_shared_with_client = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding")
    vendor = relationship("Vendor")

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    vendor_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=True)
    guest_count_basis = Column(Integer, nullable=True)
    quotation_number = Column(String, nullable=True)
    quotation_date = Column(String, nullable=True)
    validity_date = Column(String, nullable=True)
    currency = Column(String, default="INR")
    subtotal = Column(Numeric(12, 2), nullable=True)
    tax_amount = Column(Numeric(12, 2), nullable=True)
    payment_terms = Column(Text, nullable=True)
    scope_summary = Column(Text, nullable=True)
    inclusions = Column(JSON, default=list)
    exclusions = Column(JSON, default=list)
    missing_terms = Column(JSON, default=list)
    additional_charges = Column(JSON, default=list)
    taxes_detail = Column(String, nullable=True)  # "18% extra", "Included", "Needs review"
    status = Column(String, default="complete")  # complete, needs_review, selected, closed
    extraction_status = Column(String, default="ready")  # uploaded, extracting, needs_review, ready, failed
    extraction_error = Column(Text, nullable=True)
    is_scanned = Column(Boolean, default=False)
    human_verified = Column(Boolean, default=False)
    raw_extracted_text = Column(Text, nullable=True)
    is_recommended = Column(Boolean, default=False)
    source_filename = Column(String, nullable=True)
    source_file_url = Column(String, nullable=True)
    version = Column(String, default="v1")
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="quotes")
    vendor = relationship("Vendor")
    document = relationship("Document", backref="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

VendorQuote = Quote

class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(String, primary_key=True, index=True)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=False)
    original_description = Column(Text, nullable=False)
    normalized_category = Column(String, default="Catering")
    quantity = Column(Numeric(10, 2), nullable=True)
    unit = Column(String, nullable=True)  # "plate", "pax", "hours", "units", "lump_sum"
    unit_price = Column(Numeric(12, 2), nullable=True)
    tax_info = Column(String, nullable=True)
    line_total = Column(Numeric(12, 2), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_text = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    is_manually_edited = Column(Boolean, default=False)

    quote = relationship("Quote", back_populates="items")

class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=True)
    job_type = Column(String, nullable=False)  # "quote_extraction", "quote_comparison"
    status = Column(String, default="pending")  # "pending", "processing", "completed", "failed"
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class QuoteComparison(Base):
    __tablename__ = "quote_comparisons"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    category = Column(String, nullable=False)
    comparison_data = Column(JSON, default=dict)
    insights = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VendorSelection(Base):
    __tablename__ = "vendor_selections"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=False)
    category = Column(String, nullable=False)
    selected_by = Column(String, default="Aarav Mehta")
    selected_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

    wedding = relationship("Wedding")
    vendor = relationship("Vendor")
    quote = relationship("Quote")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    day_number = Column(Integer, default=1)
    event_date = Column(String, nullable=True)
    start_time = Column(String, nullable=False)  # "04:00 PM"
    end_time = Column(String, nullable=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    owner_name = Column(String, default="Aarav")
    vendor_name = Column(String, nullable=True)
    vendor_arrival_status = Column(String, default="expected")  # expected, arrived, late
    vendor_arrived_time = Column(String, nullable=True)
    delay_minutes = Column(Integer, default=0)
    status = Column(String, default="upcoming")  # upcoming, in_progress, complete
    is_locked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    wedding = relationship("Wedding", back_populates="timeline_events")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    timeline_event_id = Column(String, ForeignKey("timeline_events.id"), nullable=True)
    vendor_name = Column(String, nullable=True)
    title = Column(String, nullable=False)
    severity = Column(String, default="medium")  # low, medium, high
    delay_minutes = Column(Integer, default=0)
    affected_activities = Column(String, nullable=True)
    status = Column(String, default="open")  # open, proposed_recovery, approved, resolved
    reported_by = Column(String, default="Nisha")
    assigned_to = Column(String, default="Kabir")
    proposed_schedule_adjustment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="incidents")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    vendor_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    invoice_number = Column(String, nullable=False)
    invoice_date = Column(String, nullable=True)
    agreed_value = Column(Numeric(12, 2), default=0.0)
    approved_extras = Column(Numeric(12, 2), default=0.0)
    invoice_total = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0.0)
    status = Column(String, default="submitted")  # submitted, matched, review_required, approved, paid
    source_filename = Column(String, nullable=True)
    discrepancy_note = Column(Text, nullable=True)
    line_items = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="invoices")
    vendor = relationship("Vendor")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String, nullable=True)
    recipient_type = Column(String, default="vendor")  # vendor, agency (client collection)
    payment_stage = Column(String, nullable=False)  # advance, second_payment, final_payment
    amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    status = Column(String, default="recorded")
    recorded_by = Column(String, default="Aarav")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="payments")

class FinancialReconciliation(Base):
    __tablename__ = "financial_reconciliations"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String, nullable=False)
    invoice_number = Column(String, nullable=False)
    status = Column(String, default="flagged")  # matched, flagged, approved_override, rejected
    agreed_amount = Column(Numeric(12, 2), default=0.0)
    approved_extras = Column(Numeric(12, 2), default=0.0)
    invoice_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0.0)
    variance_amount = Column(Numeric(12, 2), default=0.0)
    line_matches = Column(JSON, default=list)
    discrepancies = Column(JSON, default=list)
    ai_explanation = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding")
    invoice = relationship("Invoice")
    quote = relationship("Quote")

class CustomerRequest(Base):
    __tablename__ = "customer_requests"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    category = Column(String, default="general")  # dietary, music, logistics, decor, general
    title = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, reviewed, approved
    planner_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding", back_populates="customer_requests")
    customer = relationship("User")

class CustomerInvitation(Base):
    __tablename__ = "customer_invitations"

    id = Column(String, primary_key=True, index=True)
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=False)
    invitation_code = Column(String, unique=True, index=True, nullable=False)
    client_email = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    is_claimed = Column(Boolean, default=False)
    claimed_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    wedding = relationship("Wedding")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    recipient_role = Column(String, nullable=True, index=True)  # owner, planner, coordinator, finance_manager, customer, all
    wedding_id = Column(String, ForeignKey("weddings.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String, default="operational")  # operational, schedule, financial, quotes, enquiry, concierge
    link_url = Column(String, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
    wedding = relationship("Wedding")
