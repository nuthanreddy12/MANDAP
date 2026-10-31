-- ==============================================================================
-- MANDAP POSTGRESQL ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
-- Architecture Security Model:
-- 1. All business data access is mediated through the FastAPI backend.
-- 2. FastAPI backend connects via service_role credentials / pooler connection.
-- 3. Application-level agency scoping and authorization is enforced in FastAPI route handlers.
-- 4. Browser clients communicate only with FastAPI and never receive Supabase secret keys.
-- 5. RLS is ENABLED on all 16 tables.
-- 6. Direct browser/anon/authenticated access to business tables is DENIED by default.
--    (No broad 'auth.uid() IS NOT NULL' policies).
-- 7. If direct client-side Supabase queries are introduced in future phases, explicit
--    agency_id and auth_user_id mapping columns must be added to the schema first.
-- ==============================================================================

-- Step 1: Enable RLS on all 16 tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE weddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE enquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE timeline_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE wedding_vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quote_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE quote_comparisons ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendor_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Step 2: Grant full access exclusively to backend service_role
CREATE POLICY "service_role_all_users" ON users FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_weddings" ON weddings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_vendors" ON vendors FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_enquiries" ON enquiries FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_tasks" ON tasks FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_timeline_events" ON timeline_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_wedding_vendors" ON wedding_vendors FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_documents" ON documents FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_quotes" ON quotes FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_quote_items" ON quote_items FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_ai_jobs" ON ai_jobs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_quote_comparisons" ON quote_comparisons FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_vendor_selections" ON vendor_selections FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_incidents" ON incidents FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_invoices" ON invoices FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_payments" ON payments FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Step 3: Default Deny for 'anon' and 'authenticated' roles
-- With RLS enabled and zero policies for 'anon' or 'authenticated', any direct client
-- query from the browser or unauthorized token returns 0 rows / permission denied.
