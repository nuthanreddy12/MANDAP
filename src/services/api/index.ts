import { fetchWithAuth } from "@/lib/api"

export interface ApiWedding {
  id: string
  couple_names: string
  client_name?: string
  client_email?: string
  client_phone?: string
  destination: string
  dates: string
  venue: string
  package_type: string
  guest_count: number
  client_budget?: number
  health_status: 'on_track' | 'attention_needed' | 'critical' | string
  assigned_planner?: string
  planner?: string
  tasks_completed_count?: number
  tasks_total_count?: number
  vendors_confirmed_count?: number
  vendors_target_count?: number
}

export interface ApiEnquiry {
  id: string
  client_names?: string
  couple_names?: string
  email: string
  phone: string
  destination: string
  dates_interested?: string
  rough_date?: string
  estimated_guest_count?: number
  guest_count?: number
  estimated_budget?: number
  budget_max?: number
  theme?: string
  status: string
  notes?: string
  assigned_owner?: string
  created_at?: string
}

export interface ApiVendor {
  id: string
  name: string
  category: string
  contact_person: string
  phone: string
  email?: string
  city: string
  rating?: number
  status: string
}

export interface ApiQuoteItem {
  id?: string
  original_description: string
  normalized_category: string
  quantity?: number
  unit?: string
  unit_price?: number
  tax_info?: string
  line_total?: number
  is_manually_edited?: boolean
}

export interface ApiQuote {
  id: string
  wedding_id: string
  vendor_id?: string
  vendor_name: string
  category: string
  total_amount: number
  price_per_unit?: number
  guest_count_basis?: number
  quotation_number?: string
  quotation_date?: string
  validity_date?: string
  taxes_detail?: string
  payment_terms?: string
  inclusions: string[]
  exclusions: string[]
  additional_charges: Array<{ name: string; amount?: number; status: string }>
  status: string
  extraction_status: string
  extraction_error?: string
  is_recommended: boolean
  is_scanned: boolean
  human_verified: boolean
  source_filename?: string
  items: ApiQuoteItem[]
}

export interface ApiTimelineEvent {
  id: string
  wedding_id: string
  day_number: number
  start_time: string
  end_time: string
  title: string
  location?: string
  owner_name: string
  vendor_name?: string
  vendor_arrival_status: string
  delay_minutes: number
  status: string
  is_locked: boolean
  notes?: string
}

export interface ApiInvoice {
  id: string
  invoice_number: string
  vendor_id?: string
  vendor_name: string
  category: string
  invoice_date?: string
  agreed_value: number
  approved_extras: number
  invoice_total: number
  paid_amount: number
  remaining_balance: number
  status: string
  line_items_count: number
  source_filename?: string
  discrepancy_note?: string
  payment_status?: string
  payment_percentage?: number
  payments_count?: number
}

export interface ApiReconciliation {
  id?: string
  invoice_id?: string
  status: string
  requires_human_review: boolean
  agreed_amount: number
  approved_extras: number
  total_authorized: number
  invoice_total: number
  variance_amount: number
  discrepancy_count: number
  discrepancies: Array<{
    type: string
    item_description?: string
    invoiced_amount?: number
    agreed_rate?: number
    invoiced_rate?: number
    variance?: number
    details: string
  }>
  line_matches: Array<{
    invoice_item: string
    matched_quote_item?: string | null
    invoice_total: number
    agreed_total: number
    variance: number
    match_type: string
    status: string
  }>
  human_resolution_notes?: string
  audit_summary?: string
  total_paid?: number
  remaining_balance?: number
  ai_explanation?: string
  ai_provider?: string
  ai_model?: string
  ai_timestamp?: string
  deterministic_math_verified?: boolean
  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string
}

// 1. Weddings
export async function getWeddings(): Promise<ApiWedding[]> {
  const res = await fetchWithAuth("/api/v1/weddings")
  if (!res.ok) throw new Error("Failed to fetch weddings")
  return res.json()
}

export async function getWedding(weddingId: string): Promise<ApiWedding> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}`)
  if (!res.ok) throw new Error(`Failed to fetch wedding ${weddingId}`)
  return res.json()
}

// 2. Enquiries
export async function getEnquiries(): Promise<ApiEnquiry[]> {
  const res = await fetchWithAuth("/api/v1/enquiries")
  if (!res.ok) throw new Error("Failed to fetch enquiries")
  return res.json()
}

export async function createEnquiry(payload: Partial<ApiEnquiry>): Promise<ApiEnquiry> {
  const res = await fetchWithAuth("/api/v1/enquiries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error("Failed to create enquiry")
  return res.json()
}

// 3. Vendors
export async function getVendors(): Promise<ApiVendor[]> {
  const res = await fetchWithAuth("/api/v1/vendors")
  if (!res.ok) throw new Error("Failed to fetch vendors")
  return res.json()
}

// 4. Quotes (AI Feature 1: Multimodal PDF Quote Extractor)
export async function getQuotes(weddingId: string, category?: string): Promise<ApiQuote[]> {
  const url = category
    ? `/api/v1/weddings/${weddingId}/quotes?category=${category}`
    : `/api/v1/weddings/${weddingId}/quotes`
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error("Failed to fetch quotes")
  return res.json()
}

export async function uploadQuoteFile(weddingId: string, file: File, category: string, vendorId?: string): Promise<any> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("category", category)
  if (vendorId) formData.append("vendor_id", vendorId)

  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/quotes/upload`, {
    method: "POST",
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to upload quote document")
  }
  return res.json()
}

export async function triggerQuoteExtraction(weddingId: string, quoteId: string): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/quotes/${quoteId}/extract`, {
    method: "POST",
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to execute AI quote extraction")
  }
  return res.json()
}

export async function getQuoteComparison(weddingId: string, category: string = "catering"): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/quotes/compare?category=${category}`)
  if (!res.ok) throw new Error("Failed to fetch quote comparison matrix")
  return res.json()
}

export async function selectQuoteVendor(weddingId: string, quoteId: string, category: string, rationale?: string): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/quotes/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      quote_id: quoteId,
      category,
      rationale,
      reassign: true,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to record vendor selection")
  }
  return res.json()
}

// 5. Tasks
export async function getWeddingTasks(weddingId: string): Promise<any[]> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/tasks`)
  if (!res.ok) throw new Error("Failed to fetch tasks")
  return res.json()
}

// 6. Timeline (AI Feature 2: Schedule Recovery with AI Briefing)
export async function getTimeline(weddingId: string): Promise<ApiTimelineEvent[]> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/timeline`)
  if (!res.ok) throw new Error("Failed to fetch timeline")
  return res.json()
}

export async function calculateScheduleRecovery(
  weddingId: string,
  eventId: string,
  delayMinutes: number,
  reason: string
): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/timeline/events/${eventId}/delay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      delay_minutes: delayMinutes,
      reason,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to calculate AI schedule recovery")
  }
  return res.json()
}

export async function approveRecoverySchedule(weddingId: string, incidentId: string): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/timeline/incidents/${incidentId}/approve`, {
    method: "POST",
  })
  if (!res.ok) throw new Error("Failed to apply recovery schedule")
  return res.json()
}

// 7. Finance & Reconciliation (AI Feature 3: Financial Reconciliation with AI Audit)
export async function getInvoices(weddingId: string = "w1"): Promise<ApiInvoice[]> {
  const url = weddingId ? `/api/v1/finance/invoices?wedding_id=${weddingId}` : "/api/v1/finance/invoices"
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error("Failed to fetch invoices")
  return res.json()
}

export async function getFinanceOverview(weddingId: string = "w1"): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/finance/overview?wedding_id=${weddingId}`)
  if (!res.ok) throw new Error("Failed to fetch finance overview")
  return res.json()
}

export async function reconcileInvoice(invoiceId: string): Promise<ApiReconciliation> {
  const res = await fetchWithAuth(`/api/v1/finance/invoices/${invoiceId}/reconcile`, {
    method: "POST",
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to execute AI financial reconciliation")
  }
  return res.json()
}

export async function getReconciliationDetails(invoiceId: string): Promise<ApiReconciliation> {
  const res = await fetchWithAuth(`/api/v1/finance/invoices/${invoiceId}/reconciliation`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to fetch reconciliation details")
  }
  return res.json()
}

export async function decideReconciliation(
  invoiceId: string,
  decision: "approve" | "reject",
  reviewNotes: string,
  decidedBy?: string
): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/finance/invoices/${invoiceId}/reconciliation/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      review_notes: reviewNotes,
      decided_by: decidedBy || "Finance Manager",
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to record reconciliation decision")
  }
  return res.json()
}

export async function seedDemoInvoices(weddingId: string = "w1"): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/finance/invoices/seed-demo?wedding_id=${weddingId}`, {
    method: "POST",
  })
  if (!res.ok) throw new Error("Failed to seed demonstration invoices")
  return res.json()
}

export async function uploadVendorInvoice(invoiceData: any): Promise<any> {
  const res = await fetchWithAuth("/api/v1/finance/invoices", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(invoiceData),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to submit vendor invoice")
  }
  return res.json()
}

export async function recordPayment(paymentData: any): Promise<any> {
  const res = await fetchWithAuth("/api/v1/finance/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paymentData),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Failed to record payment")
  }
  return res.json()
}

// 8. Overview Analytics
export async function getOverview(): Promise<any> {
  const res = await fetchWithAuth("/api/v1/overview")
  if (!res.ok) throw new Error("Failed to fetch studio overview")
  return res.json()
}

// 9. Documents
export interface ApiDocument {
  id: string
  wedding_id: string
  filename: string
  title: string
  storage_path: string
  file_size: number
  status: string
  is_shared_with_client: boolean
  uploaded_at?: string
}

export async function getDocuments(weddingId: string): Promise<ApiDocument[]> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/documents`)
  if (!res.ok) throw new Error("Failed to fetch documents")
  return res.json()
}

export async function downloadDocument(documentId: string): Promise<Blob> {
  const res = await fetchWithAuth(`/api/v1/documents/${documentId}/download`)
  if (!res.ok) throw new Error("Failed to download document")
  return res.blob()
}

// 10. Notifications
export interface ApiNotification {
  id: string
  user_id?: string
  recipient_role?: string
  wedding_id?: string
  title: string
  message: string
  category: string
  link_url?: string
  is_read: boolean
  created_at?: string
}

export interface ApiNotificationList {
  notifications: ApiNotification[]
  unread_count: number
}

export async function getNotifications(): Promise<ApiNotificationList> {
  const res = await fetchWithAuth("/api/v1/notifications")
  if (!res.ok) throw new Error("Failed to fetch notifications")
  return res.json()
}

export async function markNotificationRead(notificationId: string): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/notifications/${notificationId}/read`, {
    method: "PATCH",
  })
  if (!res.ok) throw new Error("Failed to mark notification as read")
  return res.json()
}

export async function markAllNotificationsRead(): Promise<any> {
  const res = await fetchWithAuth("/api/v1/notifications/mark-all-read", {
    method: "POST",
  })
  if (!res.ok) throw new Error("Failed to mark all notifications as read")
  return res.json()
}

// 11. Global Search
export interface SearchResultItem {
  id: string
  category: string
  title: string
  subtitle: string
  status?: string
  link_url: string
}

export interface GlobalSearchResponse {
  query: string
  total_results: number
  results: SearchResultItem[]
}

export async function globalSearch(query: string): Promise<GlobalSearchResponse> {
  const res = await fetchWithAuth(`/api/v1/search?q=${encodeURIComponent(query)}`)
  if (!res.ok) throw new Error("Search failed")
  return res.json()
}

// 12. Task Management
export async function updateTask(taskId: string, payload: { status?: string; owner_name?: string }): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error("Failed to update task")
  return res.json()
}


