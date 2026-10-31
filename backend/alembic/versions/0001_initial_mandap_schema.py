"""0001_initial_mandap_schema

Initial versioned schema containing all 16 MANDAP application tables.
Compatible with PostgreSQL (Supabase) and SQLite.

Revision ID: 0001_initial_mandap_schema
Revises: 
Create Date: 2026-10-31
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_mandap_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('role', sa.String(), server_default='planner'),
        sa.Column('avatar_initials', sa.String(length=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. weddings
    op.create_table(
        'weddings',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('couple_names', sa.String(), nullable=False),
        sa.Column('client_name', sa.String(), nullable=True),
        sa.Column('client_email', sa.String(), nullable=True),
        sa.Column('client_phone', sa.String(), nullable=True),
        sa.Column('destination', sa.String(), server_default='Jaipur'),
        sa.Column('dates', sa.String(), nullable=False),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('venue', sa.String(), server_default='The Oberoi Rajvilas'),
        sa.Column('package_type', sa.String(), server_default='full_service'),
        sa.Column('guest_count', sa.Integer(), server_default='400'),
        sa.Column('client_budget', sa.Numeric(precision=12, scale=2), server_default='0.0'),
        sa.Column('health_status', sa.String(), server_default='on_track'),
        sa.Column('assigned_planner', sa.String(), server_default='Aarav Mehta'),
        sa.Column('source_enquiry_id', sa.String(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_weddings_id'), 'weddings', ['id'], unique=False)

    # 3. vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('city', sa.String(), server_default='Jaipur'),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)

    # 4. enquiries
    op.create_table(
        'enquiries',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('couple_names', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('rough_date', sa.String(), nullable=True),
        sa.Column('guest_count', sa.Integer(), server_default='400'),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('budget_max', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('destination', sa.String(), server_default='Jaipur'),
        sa.Column('source', sa.String(), server_default='Direct Call'),
        sa.Column('package_type', sa.String(), server_default='full_service'),
        sa.Column('status', sa.String(), server_default='new'),
        sa.Column('follow_up_date', sa.String(), nullable=True),
        sa.Column('service_agreement_signed', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('agreement_url', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('assigned_owner', sa.String(), server_default='Aarav Mehta'),
        sa.Column('converted_wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=True),
        sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_enquiries_id'), 'enquiries', ['id'], unique=False)

    # 5. tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('stage', sa.String(), server_default='venue'),
        sa.Column('status', sa.String(), server_default='to_plan'),
        sa.Column('priority', sa.String(), server_default='medium'),
        sa.Column('owner_name', sa.String(), server_default='Aarav'),
        sa.Column('due_date', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)

    # 6. timeline_events
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('day_number', sa.Integer(), server_default='1'),
        sa.Column('event_date', sa.String(), nullable=True),
        sa.Column('start_time', sa.String(), nullable=False),
        sa.Column('end_time', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('owner_name', sa.String(), server_default='Aarav'),
        sa.Column('vendor_name', sa.String(), nullable=True),
        sa.Column('vendor_arrival_status', sa.String(), server_default='expected'),
        sa.Column('vendor_arrived_time', sa.String(), nullable=True),
        sa.Column('delay_minutes', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(), server_default='upcoming'),
        sa.Column('is_locked', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_index(op.f('ix_timeline_events_id'), 'timeline_events', ['id'], unique=False)

    # 7. wedding_vendors
    op.create_table(
        'wedding_vendors',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='assigned'),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_wedding_vendors_id'), 'wedding_vendors', ['id'], unique=False)

    # 8. documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), server_default='0'),
        sa.Column('file_hash', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), server_default='application/pdf'),
        sa.Column('status', sa.String(), server_default='uploaded'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_file_hash'), 'documents', ['file_hash'], unique=False)

    # 9. quotes
    op.create_table(
        'quotes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('document_id', sa.String(), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('vendor_name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('guest_count_basis', sa.Integer(), nullable=True),
        sa.Column('quotation_number', sa.String(), nullable=True),
        sa.Column('quotation_date', sa.String(), nullable=True),
        sa.Column('validity_date', sa.String(), nullable=True),
        sa.Column('currency', sa.String(), server_default='INR'),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('scope_summary', sa.Text(), nullable=True),
        sa.Column('inclusions', sa.JSON(), nullable=True),
        sa.Column('exclusions', sa.JSON(), nullable=True),
        sa.Column('missing_terms', sa.JSON(), nullable=True),
        sa.Column('additional_charges', sa.JSON(), nullable=True),
        sa.Column('taxes_detail', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='complete'),
        sa.Column('extraction_status', sa.String(), server_default='ready'),
        sa.Column('extraction_error', sa.Text(), nullable=True),
        sa.Column('is_scanned', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('human_verified', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('raw_extracted_text', sa.Text(), nullable=True),
        sa.Column('is_recommended', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('source_filename', sa.String(), nullable=True),
        sa.Column('source_file_url', sa.String(), nullable=True),
        sa.Column('version', sa.String(), server_default='v1'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_quotes_id'), 'quotes', ['id'], unique=False)

    # 10. quote_items
    op.create_table(
        'quote_items',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('quote_id', sa.String(), sa.ForeignKey('quotes.id'), nullable=False),
        sa.Column('original_description', sa.Text(), nullable=False),
        sa.Column('normalized_category', sa.String(), server_default='Catering'),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('tax_info', sa.String(), nullable=True),
        sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_text', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
        sa.Column('is_manually_edited', sa.Boolean(), server_default=sa.text('false')),
    )
    op.create_index(op.f('ix_quote_items_id'), 'quote_items', ['id'], unique=False)

    # 11. ai_jobs
    op.create_table(
        'ai_jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('quote_id', sa.String(), sa.ForeignKey('quotes.id'), nullable=True),
        sa.Column('job_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='pending'),
        sa.Column('progress', sa.Integer(), server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_ai_jobs_id'), 'ai_jobs', ['id'], unique=False)

    # 12. quote_comparisons
    op.create_table(
        'quote_comparisons',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('comparison_data', sa.JSON(), nullable=True),
        sa.Column('insights', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_quote_comparisons_id'), 'quote_comparisons', ['id'], unique=False)

    # 13. vendor_selections
    op.create_table(
        'vendor_selections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('quote_id', sa.String(), sa.ForeignKey('quotes.id'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('selected_by', sa.String(), server_default='Aarav Mehta'),
        sa.Column('selected_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_index(op.f('ix_vendor_selections_id'), 'vendor_selections', ['id'], unique=False)

    # 14. incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('timeline_event_id', sa.String(), sa.ForeignKey('timeline_events.id'), nullable=True),
        sa.Column('vendor_name', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), server_default='medium'),
        sa.Column('delay_minutes', sa.Integer(), server_default='0'),
        sa.Column('affected_activities', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='open'),
        sa.Column('reported_by', sa.String(), server_default='Nisha'),
        sa.Column('assigned_to', sa.String(), server_default='Kabir'),
        sa.Column('proposed_schedule_adjustment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_incidents_id'), 'incidents', ['id'], unique=False)

    # 15. invoices
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('vendor_name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('invoice_number', sa.String(), nullable=False),
        sa.Column('invoice_date', sa.String(), nullable=True),
        sa.Column('agreed_value', sa.Numeric(precision=12, scale=2), server_default='0.0'),
        sa.Column('approved_extras', sa.Numeric(precision=12, scale=2), server_default='0.0'),
        sa.Column('invoice_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(precision=12, scale=2), server_default='0.0'),
        sa.Column('status', sa.String(), server_default='submitted'),
        sa.Column('source_filename', sa.String(), nullable=True),
        sa.Column('discrepancy_note', sa.Text(), nullable=True),
        sa.Column('line_items', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)

    # 16. payments
    op.create_table(
        'payments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('wedding_id', sa.String(), sa.ForeignKey('weddings.id'), nullable=False),
        sa.Column('vendor_id', sa.String(), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('vendor_name', sa.String(), nullable=True),
        sa.Column('recipient_type', sa.String(), server_default='vendor'),
        sa.Column('payment_stage', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_date', sa.String(), nullable=False),
        sa.Column('reference', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='recorded'),
        sa.Column('recorded_by', sa.String(), server_default='Aarav'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)

def downgrade() -> None:
    tables = [
        'payments', 'invoices', 'incidents', 'vendor_selections', 'quote_comparisons',
        'ai_jobs', 'quote_items', 'quotes', 'documents', 'wedding_vendors',
        'timeline_events', 'tasks', 'enquiries', 'vendors', 'weddings', 'users'
    ]
    for t in tables:
        op.drop_table(t)
