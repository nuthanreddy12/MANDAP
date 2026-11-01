with open("src/services/api/index.ts", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Expand ApiInvoice interface
old_api_invoice = '''export interface ApiInvoice {
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
}'''

new_api_invoice = '''export interface ApiInvoice {
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
}'''

assert old_api_invoice in content, "old_api_invoice not found"
content = content.replace(old_api_invoice, new_api_invoice, 1)

# 2. Expand ApiReconciliation interface
old_api_rec = '''  human_resolution_notes?: string
  audit_summary?: string
}'''

new_api_rec = '''  human_resolution_notes?: string
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
}'''

assert old_api_rec in content, "old_api_rec not found"
content = content.replace(old_api_rec, new_api_rec, 1)

# 3. Update selectQuoteVendor to pass reassign: true and capture detailed errors
old_select_vendor = '''export async function selectQuoteVendor(weddingId: string, quoteId: string, category: string, rationale?: string): Promise<any> {
  const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/quotes/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      quote_id: quoteId,
      category,
      rationale,
    }),
  })
  if (!res.ok) throw new Error("Failed to record vendor selection")
  return res.json()
}'''

new_select_vendor = '''export async function selectQuoteVendor(weddingId: string, quoteId: string, category: string, rationale?: string): Promise<any> {
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
}'''

assert old_select_vendor in content, "old_select_vendor not found"
content = content.replace(old_select_vendor, new_select_vendor, 1)

# 4. Update getInvoices and add finance helper functions
old_finance_section = '''// 7. Finance & Reconciliation (AI Feature 3: Financial Reconciliation with AI Audit)
export async function getInvoices(weddingId?: string): Promise<ApiInvoice[]> {
  const url = weddingId ? `/api/v1/finance/invoices?wedding_id=${weddingId}` : "/api/v1/finance/invoices"
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error("Failed to fetch invoices")
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
}'''

new_finance_section = '''// 7. Finance & Reconciliation (AI Feature 3: Financial Reconciliation with AI Audit)
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
}'''

assert old_finance_section in content, "old_finance_section not found"
content = content.replace(old_finance_section, new_finance_section, 1)

assert "—" not in content, "Em dash detected in src/services/api/index.ts"

with open("src/services/api/index.ts", "w", encoding="utf-8") as f:
    f.write(content)

print("src/services/api/index.ts updated successfully.")

