import sqlite3
import uuid
import datetime

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

weddings_data = [
    {
        'id': 'w1',
        'title': 'Mehra x Kapoor Wedding',
        'couple_names': 'Mehra x Kapoor',
        'client_name': 'Priya Mehra',
        'client_email': 'priya.mehra@gmail.com',
        'client_phone': '+91 98201 12345',
        'destination': 'Jaipur',
        'dates': '14 to 16 November 2026',
        'start_date': '2026-11-14',
        'end_date': '2026-11-16',
        'venue': 'The Oberoi Rajvilas, Heritage Pavilions',
        'package_type': 'Royal Palace Circuit',
        'guest_count': 420,
        'client_budget': 18500000.0,
        'health_status': 'on_track',
        'assigned_planner': 'Nisha Sharma',
    },
    {
        'id': 'w2',
        'title': 'Singhania x Rathore Wedding',
        'couple_names': 'Singhania x Rathore',
        'client_name': 'Ananya Singhania',
        'client_email': 'ananya.singhania@gmail.com',
        'client_phone': '+91 98190 54321',
        'destination': 'Udaipur',
        'dates': '12 to 15 December 2026',
        'start_date': '2026-12-12',
        'end_date': '2026-12-15',
        'venue': 'The Oberoi Udaivilas, Lake Pichola',
        'package_type': 'Lakeside Royal Heritage',
        'guest_count': 380,
        'client_budget': 48000000.0,
        'health_status': 'on_track',
        'assigned_planner': 'Nisha Sharma',
    },
    {
        'id': 'w3',
        'title': 'Kothari x Mehta Wedding',
        'couple_names': 'Kothari x Mehta',
        'client_name': 'Rhea Kothari',
        'client_email': 'rhea.kothari@gmail.com',
        'client_phone': '+91 98330 67890',
        'destination': 'Jaipur',
        'dates': '04 to 07 January 2027',
        'start_date': '2027-01-04',
        'end_date': '2027-01-07',
        'venue': 'Rambagh Palace, Heritage Courtyards',
        'package_type': 'Grand Rajputana Imperial',
        'guest_count': 450,
        'client_budget': 62000000.0,
        'health_status': 'attention_needed',
        'assigned_planner': 'Nisha Sharma',
    },
    {
        'id': 'w4',
        'title': 'Sethi x Chawla Wedding',
        'couple_names': 'Sethi x Chawla',
        'client_name': 'Meera Chordia',
        'client_email': 'sethi.chawla@example.com',
        'client_phone': '+91 98450 11223',
        'destination': 'Jaisalmer',
        'dates': '20 to 22 February 2027',
        'start_date': '2027-02-20',
        'end_date': '2027-02-22',
        'venue': 'Suryagarh Heritage Citadel, Desert Dunes',
        'package_type': 'Desert Fort Royal Atelier',
        'guest_count': 350,
        'client_budget': 39000000.0,
        'health_status': 'on_track',
        'assigned_planner': 'Nisha Sharma',
    },
]

now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

for w in weddings_data:
    c.execute("SELECT id FROM weddings WHERE id = ?", (w['id'],))
    existing = c.fetchone()
    if existing:
        c.execute("""
            UPDATE weddings SET
                title = ?, couple_names = ?, client_name = ?, client_email = ?, client_phone = ?,
                destination = ?, dates = ?, start_date = ?, end_date = ?, venue = ?,
                package_type = ?, guest_count = ?, client_budget = ?, health_status = ?,
                assigned_planner = ?, is_archived = 0
            WHERE id = ?
        """, (
            w['title'], w['couple_names'], w['client_name'], w['client_email'], w['client_phone'],
            w['destination'], w['dates'], w['start_date'], w['end_date'], w['venue'],
            w['package_type'], w['guest_count'], w['client_budget'], w['health_status'],
            w['assigned_planner'], w['id']
        ))
    else:
        c.execute("""
            INSERT INTO weddings (
                id, title, couple_names, client_name, client_email, client_phone,
                destination, dates, start_date, end_date, venue, package_type,
                guest_count, client_budget, health_status, assigned_planner,
                is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            w['id'], w['title'], w['couple_names'], w['client_name'], w['client_email'], w['client_phone'],
            w['destination'], w['dates'], w['start_date'], w['end_date'], w['venue'],
            w['package_type'], w['guest_count'], w['client_budget'], w['health_status'],
            w['assigned_planner'], now_str
        ))

# Ensure w_5b00f82e has assigned_planner Nisha Sharma
c.execute("UPDATE weddings SET assigned_planner = 'Nisha Sharma' WHERE id = 'w_5b00f82e'")
conn.commit()

# Copy sample tasks, quotes, timeline events, invoices, documents to w2, w3, w4 if missing
for target_wid, couple, city, venue in [
    ('w2', 'Singhania x Rathore', 'Udaipur', 'The Oberoi Udaivilas'),
    ('w3', 'Kothari x Mehta', 'Jaipur', 'Rambagh Palace'),
    ('w4', 'Sethi x Chawla', 'Jaisalmer', 'Suryagarh Citadel'),
]:
    # Tasks: ['id', 'wedding_id', 'title', 'stage', 'status', 'priority', 'owner_name', 'due_date', 'created_at']
    c.execute("SELECT count(*) FROM tasks WHERE wedding_id = ?", (target_wid,))
    if c.fetchone()[0] == 0:
        c.execute("SELECT title, stage, status, priority, owner_name, due_date FROM tasks WHERE wedding_id = 'w1'")
        w1_tasks = c.fetchall()
        for t in w1_tasks:
            tid = f"t_{target_wid}_{uuid.uuid4().hex[:6]}"
            c.execute("""
                INSERT INTO tasks (id, wedding_id, title, stage, status, priority, owner_name, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tid, target_wid, t[0], t[1], t[2], t[3], t[4], t[5], now_str))
        print(f"Seeded {len(w1_tasks)} tasks for {target_wid}")

    # Timeline events
    c.execute("SELECT count(*) FROM timeline_events WHERE wedding_id = ?", (target_wid,))
    if c.fetchone()[0] == 0:
        c.execute("SELECT title, start_time, end_time, location, owner_name, vendor_name, vendor_arrival_status, delay_minutes, status, is_locked, notes FROM timeline_events WHERE wedding_id = 'w1'")
        w1_timeline = c.fetchall()
        for te in w1_timeline:
            te_id = f"te_{target_wid}_{uuid.uuid4().hex[:6]}"
            c.execute("""
                INSERT INTO timeline_events (id, wedding_id, day_number, title, start_time, end_time, location, owner_name, vendor_name, vendor_arrival_status, delay_minutes, status, is_locked, notes)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
            """, (te_id, target_wid, te[0], te[1], te[2], venue, te[4], te[5], te[6], te[8], te[9], te[10]))
        print(f"Seeded {len(w1_timeline)} timeline events for {target_wid}")

    # Quotes: ['id', 'wedding_id', 'vendor_id', 'document_id', 'vendor_name', 'category', 'total_amount', 'price_per_unit', 'guest_count_basis', 'quotation_number', 'quotation_date', 'validity_date', 'currency', 'subtotal', 'tax_amount', 'payment_terms', 'scope_summary', 'inclusions', 'exclusions', 'missing_terms', 'additional_charges', 'taxes_detail', 'status', 'extraction_status', 'extraction_error', 'is_scanned', 'human_verified', 'raw_extracted_text', 'is_recommended', 'source_filename', 'source_file_url', 'version', 'uploaded_at']
    c.execute("SELECT count(*) FROM quotes WHERE wedding_id = ?", (target_wid,))
    if c.fetchone()[0] == 0:
        c.execute("""
            SELECT vendor_id, document_id, vendor_name, category, total_amount, price_per_unit, guest_count_basis,
                   quotation_number, quotation_date, validity_date, currency, subtotal, tax_amount, payment_terms,
                   scope_summary, inclusions, exclusions, missing_terms, additional_charges, taxes_detail,
                   status, extraction_status, extraction_error, is_scanned, human_verified, raw_extracted_text,
                   is_recommended, source_filename, source_file_url, version
            FROM quotes WHERE wedding_id = 'w1'
        """)
        w1_quotes = c.fetchall()
        for q in w1_quotes:
            qid = f"q_{target_wid}_{uuid.uuid4().hex[:6]}"
            c.execute("""
                INSERT INTO quotes (
                    id, wedding_id, vendor_id, document_id, vendor_name, category, total_amount, price_per_unit, guest_count_basis,
                    quotation_number, quotation_date, validity_date, currency, subtotal, tax_amount, payment_terms,
                    scope_summary, inclusions, exclusions, missing_terms, additional_charges, taxes_detail,
                    status, extraction_status, extraction_error, is_scanned, human_verified, raw_extracted_text,
                    is_recommended, source_filename, source_file_url, version, uploaded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (qid, target_wid, *q, now_str))
        print(f"Seeded {len(w1_quotes)} quotes for {target_wid}")

    # Invoices: ['id', 'wedding_id', 'vendor_id', 'vendor_name', 'category', 'invoice_number', 'invoice_date', 'agreed_value', 'approved_extras', 'invoice_total', 'paid_amount', 'status', 'source_filename', 'discrepancy_note', 'line_items', 'created_at']
    c.execute("SELECT count(*) FROM invoices WHERE wedding_id = ?", (target_wid,))
    if c.fetchone()[0] == 0:
        c.execute("""
            SELECT vendor_id, vendor_name, category, invoice_number, invoice_date, agreed_value, approved_extras, invoice_total, paid_amount, status, source_filename, discrepancy_note, line_items
            FROM invoices WHERE wedding_id = 'w1'
        """)
        w1_invoices = c.fetchall()
        for inv in w1_invoices:
            inv_id = f"inv_{target_wid}_{uuid.uuid4().hex[:6]}"
            c.execute("""
                INSERT INTO invoices (
                    id, wedding_id, vendor_id, vendor_name, category, invoice_number, invoice_date, agreed_value, approved_extras, invoice_total, paid_amount, status, source_filename, discrepancy_note, line_items, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (inv_id, target_wid, *inv, now_str))
        print(f"Seeded {len(w1_invoices)} invoices for {target_wid}")

    # Documents: ['id', 'wedding_id', 'vendor_id', 'filename', 'file_size', 'file_hash', 'storage_path', 'content_type', 'status', 'is_shared_with_client', 'error_message', 'created_at']
    c.execute("SELECT count(*) FROM documents WHERE wedding_id = ?", (target_wid,))
    if c.fetchone()[0] == 0:
        c.execute("""
            SELECT vendor_id, filename, file_size, file_hash, storage_path, content_type, status, is_shared_with_client, error_message
            FROM documents WHERE wedding_id = 'w1'
        """)
        w1_docs = c.fetchall()
        for doc in w1_docs:
            doc_id = f"doc_{target_wid}_{uuid.uuid4().hex[:6]}"
            c.execute("""
                INSERT INTO documents (
                    id, wedding_id, vendor_id, filename, file_size, file_hash, storage_path, content_type, status, is_shared_with_client, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc_id, target_wid, *doc, now_str))
        print(f"Seeded {len(w1_docs)} documents for {target_wid}")

conn.commit()

print("\nAll weddings verified:")
c.execute("SELECT id, couple_names, venue, destination, client_budget, assigned_planner FROM weddings WHERE is_archived = 0")
for r in c.fetchall():
    print(" -", r)

conn.close()
