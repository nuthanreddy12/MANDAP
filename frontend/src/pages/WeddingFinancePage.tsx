import React, { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { SourceChip } from "@/components/ui/SourceChip"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import { formatINR } from "@/lib/formatters"
import {
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  Plus,
  FileText,
  ShieldCheck,
  XCircle,
  HelpCircle,
  TrendingDown,
  TrendingUp,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

interface InvoiceSummary {
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
  source_filename?: string
  discrepancy_note?: string
  line_items_count: number
  created_at?: string
}

interface LineMatch {
  invoice_item: string
  matched_quote_item?: string | null
  invoice_quantity?: number
  agreed_quantity?: number
  invoice_rate?: number
  agreed_rate?: number
  invoice_total: number
  agreed_total: number
  variance: number
  match_type: string
  status: string
}

interface Discrepancy {
  type: string
  item_description?: string
  invoiced_amount?: number
  agreed_rate?: number
  invoiced_rate?: number
  agreed_quantity?: number
  invoiced_quantity?: number
  variance?: number
  invoice_total?: number
  total_paid?: number
  remaining_balance?: number
  details: string
}

interface ReconciliationData {
  id?: string
  invoice_id?: string
  status: string
  requires_human_review: boolean
  agreed_amount: number
  approved_extras: number
  total_authorized: number
  invoice_total: number
  total_paid: number
  remaining_balance: number
  total_variance: number
  unapproved_additional_total: number
  discrepancies_count: number
  discrepancies: Discrepancy[]
  line_matches: LineMatch[]
  ai_explanation?: string
  review_decision?: string
  review_notes?: string
  reviewed_by?: string
  reviewed_at?: string
}

interface OverviewData {
  wedding_id: string
  total_invoiced: number
  total_paid: number
  total_outstanding: number
  invoices_count: number
  review_required_count: number
}

export const WeddingFinancePage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const weddingId = id || "w1"
  const { toasts, addToast, removeToast } = useToast()

  const [invoices, setInvoices] = useState<InvoiceSummary[]>([])
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null)
  const [reconciliation, setReconciliation] = useState<ReconciliationData | null>(null)
  const [overview, setOverview] = useState<OverviewData | null>(null)

  const [loading, setLoading] = useState<boolean>(true)
  const [reconciling, setReconciling] = useState<boolean>(false)
  const [decisionLoading, setDecisionLoading] = useState<boolean>(false)
  const [reviewNotes, setReviewNotes] = useState<string>("")
  const [reviewerName, setReviewerName] = useState<string>("Finance Manager Kabir")

  const loadFinanceData = useCallback(async (preferredInvoiceId?: string) => {
    try {
      setLoading(true)
      const [invRes, ovRes] = await Promise.all([
        fetchWithAuth(`/api/v1/weddings/${weddingId}/finance/invoices`),
        fetchWithAuth(`/api/v1/weddings/${weddingId}/finance/overview`),
      ])

      if (!invRes.ok) throw new Error("Failed to load invoices")
      const invData: InvoiceSummary[] = await invRes.json()
      setInvoices(invData)

      if (ovRes.ok) {
        const ovData: OverviewData = await ovRes.json()
        setOverview(ovData)
      }

      // Select active invoice
      let activeId = preferredInvoiceId
      if (!activeId && invData.length > 0) {
        // Prefer demo invoice or first review_required invoice
        const demoInv = invData.find((i) => i.invoice_number === "INV-RR-8821")
        const reviewInv = invData.find((i) => i.status === "review_required")
        activeId = demoInv?.id || reviewInv?.id || invData[0].id
      }

      if (activeId) {
        setSelectedInvoiceId(activeId)
        await loadReconciliation(activeId)
      } else {
        setReconciliation(null)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error loading finance records"
      addToast(msg, "error")
    } finally {
      setLoading(false)
    }
  }, [weddingId, addToast])

  const loadReconciliation = async (invoiceId: string) => {
    try {
      const res = await fetchWithAuth(
        `/api/v1/weddings/${weddingId}/finance/invoices/${invoiceId}/reconciliation`
      )
      if (res.ok) {
        const data: ReconciliationData = await res.json()
        setReconciliation(data)
        if (data.review_notes) {
          setReviewNotes(data.review_notes)
        }
      } else if (res.status === 404) {
        // No saved reconciliation yet
        setReconciliation(null)
      }
    } catch {
      setReconciliation(null)
    }
  }

  useEffect(() => {
    loadFinanceData()
  }, [loadFinanceData])

  const handleSelectInvoice = async (invoiceId: string) => {
    setSelectedInvoiceId(invoiceId)
    await loadReconciliation(invoiceId)
  }

  const handleSeedDemoInvoice = async () => {
    try {
      setReconciling(true)
      const res = await fetchWithAuth(
        `/api/v1/weddings/${weddingId}/finance/invoices/seed-demo`,
        { method: "POST" }
      )
      if (!res.ok) throw new Error("Failed to seed demonstration invoice")
      const data = await res.json()
      addToast("Synthetic demo invoice INV-RR-8821 seeded with unapproved Rs. 45,000 surcharge", "success")

      // Trigger automatic reconciliation immediately
      const recRes = await fetchWithAuth(
        `/api/v1/weddings/${weddingId}/finance/invoices/${data.invoice_id}/reconcile`,
        { method: "POST" }
      )
      if (recRes.ok) {
        const recData: ReconciliationData = await recRes.json()
        setReconciliation(recData)
      }

      await loadFinanceData(data.invoice_id)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to seed demo invoice"
      addToast(msg, "error")
    } finally {
      setReconciling(false)
    }
  }

  const handleRunReconciliation = async () => {
    if (!selectedInvoiceId) return
    try {
      setReconciling(true)
      const res = await fetchWithAuth(
        `/api/v1/weddings/${weddingId}/finance/invoices/${selectedInvoiceId}/reconcile`,
        { method: "POST" }
      )
      if (!res.ok) throw new Error("Reconciliation failed")
      const data: ReconciliationData = await res.json()
      setReconciliation(data)
      addToast("AI financial reconciliation completed successfully", "success")
      await loadFinanceData(selectedInvoiceId)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error executing reconciliation"
      addToast(msg, "error")
    } finally {
      setReconciling(false)
    }
  }

  const handleDecision = async (decision: "approve" | "reject") => {
    if (!selectedInvoiceId) return
    try {
      setDecisionLoading(true)
      const res = await fetchWithAuth(
        `/api/v1/weddings/${weddingId}/finance/invoices/${selectedInvoiceId}/reconciliation/decide`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision,
            review_notes:
              reviewNotes ||
              (decision === "approve"
                ? "Authorized as approved change order post review."
                : "Discrepancy rejected. Disputed unapproved charges with vendor."),
            decided_by: reviewerName || "Finance Manager Kabir",
          }),
        }
      )
      if (!res.ok) throw new Error("Failed to record decision")
      const updatedRec = await res.json()
      setReconciliation(updatedRec)
      addToast(
        decision === "approve"
          ? "Invoice discrepancy approved as authorized change order"
          : "Invoice discrepancy rejected and flagged for vendor dispute",
        "info"
      )
      await loadFinanceData(selectedInvoiceId)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Decision recording failed"
      addToast(msg, "error")
    } finally {
      setDecisionLoading(false)
    }
  }

  const activeInvoice = invoices.find((i) => i.id === selectedInvoiceId)

  // Calculations for cards
  const agreedVal = reconciliation ? reconciliation.agreed_amount : (activeInvoice?.agreed_value || 0)
  const approvedExtras = reconciliation ? reconciliation.approved_extras : (activeInvoice?.approved_extras || 0)
  const invTotal = reconciliation ? reconciliation.invoice_total : (activeInvoice?.invoice_total || 0)
  const paidVal = reconciliation ? reconciliation.total_paid : (activeInvoice?.paid_amount || 0)
  const balanceVal = reconciliation ? reconciliation.remaining_balance : ((activeInvoice?.invoice_total || 0) - (activeInvoice?.paid_amount || 0))
  const varianceVal = reconciliation ? reconciliation.total_variance : (invTotal - (agreedVal + approvedExtras))

  return (
    <div className="flex flex-col min-h-full">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
      <WeddingWorkspaceHeader
        coupleName="Mehra × Kapoor"
        dates="14–16 November 2026"
        destination="Jaipur"
        packageType="Full service"
        guestCount={420}
        healthStatus={overview && overview.review_required_count > 0 ? "1_open_issue" : "on_track"}
      />

      <div className="p-4 md:p-8 max-w-[1440px] w-full mx-auto space-y-6">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-[#878074]">
              <span>Finance</span>
              <span>/</span>
              <span className="text-[#292E27] font-medium">Vendor Reconciliation</span>
            </div>
            <h3 className="font-editorial text-2xl text-[#292E27] font-normal mt-0.5">
              Financial Reconciliation: {activeInvoice?.vendor_name || "Vendor Audit"}
            </h3>
            <p className="text-xs text-[#69655D] mt-0.5">
              Deterministic Contract vs Invoice Audit · Python Decimal Engine · Gemini CFO Explanations
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {activeInvoice?.source_filename && (
              <SourceChip filename={activeInvoice.source_filename} />
            )}

            <button
              type="button"
              id="seed-demo-invoice-btn"
              onClick={handleSeedDemoInvoice}
              disabled={reconciling}
              className="px-3.5 py-2 bg-[#F4EFEA] hover:bg-[#EAE4DC] text-[#292E27] border border-[#E2DBD0] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 shadow-xs disabled:opacity-60"
              title="Seeds synthetic invoice INV-RR-8821 with unapproved Rs. 45,000 surcharge"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
              <span>Seed Demo (₹45k Surcharge)</span>
            </button>

            <button
              type="button"
              id="run-reconcile-btn"
              onClick={handleRunReconciliation}
              disabled={reconciling || !selectedInvoiceId}
              className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 shadow-xs disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-[#C4A46D] ${reconciling ? "animate-spin" : ""}`} aria-hidden="true" />
              <span>{reconciling ? "Reconciling..." : "Run AI Reconciliation"}</span>
            </button>
          </div>
        </div>

        {/* Invoice Selector Pills */}
        {invoices.length > 0 && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            <span className="text-[#878074] font-medium shrink-0">Invoices ({invoices.length}):</span>
            {invoices.map((inv) => (
              <button
                key={inv.id}
                onClick={() => handleSelectInvoice(inv.id)}
                className={`px-3 py-1.5 rounded-full border text-xs font-medium transition-all shrink-0 inline-flex items-center gap-1.5 ${
                  selectedInvoiceId === inv.id
                    ? "bg-[#292E27] text-white border-[#292E27] shadow-xs"
                    : "bg-white text-[#292E27] border-[#E2DBD0] hover:bg-[#F4EFEA]"
                }`}
              >
                <span>{inv.invoice_number}</span>
                <span className="opacity-75">({inv.vendor_name.split(" ")[0]})</span>
                {inv.status === "review_required" && (
                  <span className="w-2 h-2 rounded-full bg-[#AE5142]" />
                )}
                {inv.status === "approved" && (
                  <span className="w-2 h-2 rounded-full bg-[#61765B]" />
                )}
              </button>
            ))}
          </div>
        )}

        {/* 4 Financial Ledger Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Agreed Value */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#878074]">Agreed Contract Value</span>
              <ShieldCheck className="w-4 h-4 text-[#61765B]" />
            </div>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {formatINR(agreedVal, true)}
            </div>
            <p className="mt-1 text-[11px] text-[#69655D]">Contract baseline · 420 guests</p>
          </div>

          {/* Approved Extras */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#878074]">Approved Extras / Additions</span>
              <CheckCircle2 className="w-4 h-4 text-[#61765B]" />
            </div>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {formatINR(approvedExtras, true)}
            </div>
            <p className="mt-1 text-[11px] text-[#69655D]">Authorized change orders</p>
          </div>

          {/* Invoice Total */}
          <div className={`p-4 bg-white border rounded-lg shadow-xs ${varianceVal > 0 ? "border-[#AE5142]/60 bg-[#AE5142]/5" : "border-[#E2DBD0]"}`}>
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#878074]">Submitted Invoice Total</span>
              {varianceVal > 0 ? (
                <AlertTriangle className="w-4 h-4 text-[#AE5142]" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-[#61765B]" />
              )}
            </div>
            <div className={`mt-1 text-2xl font-editorial tabular-nums ${varianceVal > 0 ? "text-[#AE5142]" : "text-[#292E27]"}`}>
              {formatINR(invTotal, true)}
            </div>
            <p className={`mt-1 text-[11px] ${varianceVal > 0 ? "text-[#852C1F] font-medium" : "text-[#69655D]"}`}>
              {activeInvoice?.invoice_number || "Invoice"} {varianceVal > 0 ? `· Discrepancy: +${formatINR(varianceVal)}` : "· Fully Reconciled"}
            </p>
          </div>

          {/* Paid / Balance */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#878074]">Paid / Remaining Balance</span>
              <span className="text-[10px] font-medium uppercase px-1.5 py-0.5 rounded bg-[#F4EFEA] text-[#69655D]">
                {balanceVal > 0 ? "Partial" : "Settled"}
              </span>
            </div>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {formatINR(paidVal, true)}
            </div>
            <p className="mt-1 text-[11px] text-[#69655D]">
              Remaining balance: {formatINR(balanceVal)}
            </p>
          </div>
        </div>

        {/* Line-Item Contractual Comparison Table */}
        <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h4 className="font-editorial text-lg text-[#292E27] font-normal">
                Line-Item Contractual Comparison
              </h4>
              <p className="text-xs text-[#69655D]">
                Pre-computed Decimal comparison of contract quotations against billed invoice line items
              </p>
            </div>
            {reconciliation && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#878074]">Reconciliation status:</span>
                <StatusBadge
                  status={reconciliation.status === "matched" ? "complete" : "needs_review"}
                  label={reconciliation.status === "matched" ? "Matched" : "Review Required"}
                />
              </div>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E2DBD0] text-[#878074] uppercase text-[11px]">
                  <th className="pb-3 font-medium">Invoice Line Item</th>
                  <th className="pb-3 font-medium">Contracted Item Match</th>
                  <th className="pb-3 font-medium text-center">Qty (Inv / Agr)</th>
                  <th className="pb-3 font-medium text-right">Agreed Rate</th>
                  <th className="pb-3 font-medium text-right">Invoiced Rate</th>
                  <th className="pb-3 font-medium text-right">Line Total</th>
                  <th className="pb-3 font-medium text-right">Variance</th>
                  <th className="pb-3 font-medium text-right">Audit Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F4EFEA] text-[#292E27]">
                {reconciliation?.line_matches && reconciliation.line_matches.length > 0 ? (
                  reconciliation.line_matches.map((item, idx) => {
                    const isUnapproved = item.status === "unapproved" || item.match_type === "unapproved_addition"
                    const isVariance = item.status === "variance" || item.variance !== 0

                    return (
                      <tr
                        key={idx}
                        className={
                          isUnapproved
                            ? "bg-[#AE5142]/10 font-medium"
                            : isVariance
                            ? "bg-[#C4A46D]/10"
                            : "hover:bg-[#FAF8F5]"
                        }
                      >
                        <td className="py-3 font-medium pr-2">
                          <div className="flex items-center gap-1.5">
                            {isUnapproved && (
                              <AlertTriangle className="w-3.5 h-3.5 text-[#AE5142] shrink-0" />
                            )}
                            <span>{item.invoice_item}</span>
                          </div>
                        </td>
                        <td className="py-3 text-[#69655D] pr-2">
                          {item.matched_quote_item || (
                            <span className="text-[#AE5142] font-semibold">Not Contracted</span>
                          )}
                        </td>
                        <td className="py-3 text-center tabular-nums">
                          {item.invoice_quantity !== undefined && item.agreed_quantity !== undefined
                            ? `${item.invoice_quantity} / ${item.agreed_quantity}`
                            : (item.invoice_quantity || 1)}
                        </td>
                        <td className="py-3 text-right tabular-nums text-[#69655D]">
                          {item.agreed_rate ? formatINR(item.agreed_rate) : "N/A"}
                        </td>
                        <td className="py-3 text-right tabular-nums">
                          {item.invoice_rate ? formatINR(item.invoice_rate) : "N/A"}
                        </td>
                        <td className="py-3 text-right font-semibold tabular-nums">
                          {formatINR(item.invoice_total)}
                        </td>
                        <td className={`py-3 text-right tabular-nums font-semibold ${item.variance > 0 ? "text-[#AE5142]" : item.variance < 0 ? "text-[#61765B]" : "text-[#878074]"}`}>
                          {item.variance > 0 ? `+${formatINR(item.variance)}` : item.variance < 0 ? `-${formatINR(Math.abs(item.variance))}` : "₹0"}
                        </td>
                        <td className="py-3 text-right">
                          {isUnapproved ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#AE5142] text-white">
                              +₹45,000 Unapproved
                            </span>
                          ) : isVariance ? (
                            <StatusBadge status="needs_review" label="Variance" />
                          ) : (
                            <StatusBadge status="complete" label="Matched" />
                          )}
                        </td>
                      </tr>
                    )
                  })
                ) : (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-[#878074]">
                      {loading ? "Loading contractual comparison..." : "Click 'Run AI Reconciliation' to perform line-item audit."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Two Columns: Payments & Settlement Schedule + Needs Human Review / AI Briefing */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Payments & Settlement Ledger */}
          <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F4EFEA] pb-2">
              <h4 className="font-editorial text-lg text-[#292E27] font-normal">
                Payments & Settlement Ledger
              </h4>
              <span className="text-[11px] text-[#878074]">Payment schedule matching</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between py-2 border-b border-[#F4EFEA]">
                <div>
                  <span className="font-medium text-[#292E27]">Advance Deposit (30%)</span>
                  <span className="text-[#878074] ml-2">· 10 Oct 2026 · NEFT-RR-9941</span>
                </div>
                <span className="font-semibold text-[#292E27] tabular-nums">
                  {formatINR(paidVal)}
                </span>
              </div>

              <div className="flex items-center justify-between py-2 bg-[#F4EFEA]/60 px-3 rounded">
                <div>
                  <span className="font-medium text-[#292E27]">Remaining Contract Balance</span>
                  <span className="text-[#878074] ml-2">· Due post-event settlement</span>
                </div>
                <span className="font-semibold text-[#292E27] tabular-nums">
                  {formatINR(balanceVal)}
                </span>
              </div>
            </div>

            {/* Reconciliation Variance Summary */}
            <div className="p-3 bg-[#FAF8F5] border border-[#E2DBD0] rounded text-xs space-y-1.5">
              <div className="flex justify-between text-[#69655D]">
                <span>Contract Authorized Total:</span>
                <span className="font-medium text-[#292E27] tabular-nums">{formatINR(agreedVal + approvedExtras)}</span>
              </div>
              <div className="flex justify-between text-[#69655D]">
                <span>Billed Invoice Total:</span>
                <span className="font-medium text-[#292E27] tabular-nums">{formatINR(invTotal)}</span>
              </div>
              <div className="flex justify-between font-semibold border-t border-[#E2DBD0] pt-1.5">
                <span className={varianceVal > 0 ? "text-[#AE5142]" : "text-[#61765B]"}>Total Variance:</span>
                <span className={`tabular-nums ${varianceVal > 0 ? "text-[#AE5142]" : "text-[#61765B]"}`}>
                  {varianceVal > 0 ? `+${formatINR(varianceVal)}` : formatINR(varianceVal)}
                </span>
              </div>
            </div>

            <p className="text-[11px] text-[#878074] pt-1">
              All vendor disbursements link strictly to verified quotation items and approved change orders.
            </p>
          </div>

          {/* Right Column: Needs Human Review & Gemini CFO Briefing */}
          <div className={`bg-white border rounded-lg p-5 shadow-xs flex flex-col justify-between ${
            reconciliation?.requires_human_review ? "border-[#AE5142]/60" : "border-[#E2DBD0]"
          }`}>
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-[#F4EFEA] pb-2">
                <div className="flex items-center gap-2">
                  {reconciliation?.requires_human_review ? (
                    <>
                      <AlertTriangle className="w-4 h-4 text-[#AE5142]" />
                      <span className="text-xs font-semibold text-[#AE5142]">Needs Human Review</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-[#61765B]" />
                      <span className="text-xs font-semibold text-[#61765B]">Reconciliation Matched</span>
                    </>
                  )}
                </div>
                <span className="text-[11px] text-[#878074]">AI Audit Intelligence</span>
              </div>

              {/* Gemini CFO Briefing */}
              {reconciliation?.ai_explanation && (
                <div className="p-3.5 bg-[#F4EFEA] rounded border border-[#E2DBD0] text-xs text-[#292E27] leading-relaxed">
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[#878074] uppercase tracking-wider mb-1">
                    <Sparkles className="w-3.5 h-3.5 text-[#C4A46D]" />
                    <span>Gemini Financial Controller Briefing</span>
                  </div>
                  <p className="text-xs font-serif text-[#292E27]">{reconciliation.ai_explanation}</p>
                </div>
              )}

              {/* Discrepancies Details List */}
              {reconciliation?.discrepancies && reconciliation.discrepancies.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-medium text-[#878074] uppercase">
                    Detected Discrepancies ({reconciliation.discrepancies.length}):
                  </span>
                  <div className="space-y-1.5 max-h-36 overflow-y-auto">
                    {reconciliation.discrepancies.map((d, i) => (
                      <div
                        key={i}
                        className={`p-2 rounded text-xs flex items-start gap-2 ${
                          d.type === "unapproved_additional_charge"
                            ? "bg-[#AE5142]/10 border border-[#AE5142]/30 text-[#852C1F]"
                            : d.type === "duplicate_charge"
                            ? "bg-[#AE5142]/10 border border-[#AE5142]/30 text-[#852C1F]"
                            : "bg-[#F4EFEA] border border-[#E2DBD0] text-[#69655D]"
                        }`}
                      >
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        <span>{d.details}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Persisted Decision Status */}
              {reconciliation?.review_decision && (
                <div className="p-3 bg-[#FAF8F5] border border-[#E2DBD0] rounded text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[#878074]">Manager Decision:</span>
                    <span
                      className={`font-semibold uppercase text-[10px] px-2 py-0.5 rounded ${
                        reconciliation.review_decision === "approve"
                          ? "bg-[#61765B] text-white"
                          : "bg-[#AE5142] text-white"
                      }`}
                    >
                      {reconciliation.review_decision === "approve" ? "Approved as Change Order" : "Disputed / Rejected"}
                    </span>
                  </div>
                  {reconciliation.reviewed_by && (
                    <div className="text-[11px] text-[#69655D]">
                      Decided by {reconciliation.reviewed_by} on {reconciliation.reviewed_at ? new Date(reconciliation.reviewed_at).toLocaleDateString("en-IN") : "Today"}
                    </div>
                  )}
                  {reconciliation.review_notes && (
                    <div className="text-[11px] text-[#292E27] italic">
                      &quot;{reconciliation.review_notes}&quot;
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Finance Manager Action Controls */}
            <div className="pt-4 border-t border-[#F4EFEA] mt-4 space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Review notes or justification..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-xs border border-[#E2DBD0] rounded focus:outline-none focus:ring-1 focus:ring-[#292E27]"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  id="approve-change-order-btn"
                  onClick={() => handleDecision("approve")}
                  disabled={decisionLoading || !selectedInvoiceId}
                  className="py-2 bg-[#61765B] hover:bg-[#4E5F49] text-white text-xs font-medium rounded transition-colors text-center disabled:opacity-60"
                >
                  Approve as Change Order
                </button>

                <button
                  type="button"
                  id="reject-dispute-btn"
                  onClick={() => handleDecision("reject")}
                  disabled={decisionLoading || !selectedInvoiceId}
                  className="py-2 bg-[#AE5142] hover:bg-[#852C1F] text-white text-xs font-medium rounded transition-colors text-center disabled:opacity-60"
                >
                  Dispute / Reject Discrepancy
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Profitability Disclosure Note */}
        <div className="p-3.5 bg-[#F4EFEA] border border-[#E2DBD0] rounded-md text-xs text-[#69655D]">
          <strong>Profitability disclosure:</strong> Provisional. 3 vendor cost categories (Florist, Lighting, Valet final bills) not yet recorded. Current recorded margin is ₹44.8L on ₹1.85Cr budget.
        </div>
      </div>
    </div>
  )
}
