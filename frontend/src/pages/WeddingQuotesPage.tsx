import React, { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { SourceChip } from "@/components/ui/SourceChip"
import { Modal } from "@/components/ui/Modal"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import { formatINR } from "@/lib/formatters"
import {
  Upload,
  Check,
  AlertCircle,
  FileText,
  Edit2,
  Sparkles,
  RefreshCw,
  Plus,
  Trash2,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

interface QuoteItem {
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

interface QuoteData {
  id: string
  wedding_id: string
  vendor_id: string
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
  scope_summary?: string
  inclusions: string[]
  exclusions: string[]
  missing_terms: string[]
  additional_charges: Array<{ name: string; amount?: number; status: string }>
  status: string // complete, needs_review, selected, closed
  extraction_status: string // uploaded, extracting, needs_review, ready, failed
  extraction_error?: string
  is_recommended: boolean
  is_scanned: boolean
  human_verified: boolean
  source_filename?: string
  version: string
  items: QuoteItem[]
}

interface ComparisonMatrixItem {
  parameter: string
  values: Record<string, string>
}

interface ComparisonInsights {
  lowest_quoted_base?: { vendor_name: string; amount: number }
  lowest_estimated_final?: { vendor_name: string; amount: number }
  recommended_vendor?: string
  recommendation_rationale?: string
  scope_differences?: string[]
  important_conditions?: string[]
}

export const WeddingQuotesPage: React.FC = () => {
  const { id = "w1" } = useParams<{ id: string }>()
  const { toasts, addToast, removeToast } = useToast()

  const [wedding, setWedding] = useState({
    couple_names: "Mehra x Kapoor",
    dates: "14 to 16 November 2026",
    destination: "Jaipur",
    package_type: "Full service",
    guest_count: 420,
    health_status: "on_track",
  })

  const [quotes, setQuotes] = useState<QuoteData[]>([])
  const [loading, setLoading] = useState(true)
  const [category] = useState("catering")

  // Comparison data
  const [comparisonItems, setComparisonItems] = useState<ComparisonMatrixItem[]>([])
  const [insights, setInsights] = useState<ComparisonInsights>({})

  // Modals
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadVendorName, setUploadVendorName] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  // Edit Line Items Modal
  const [editingQuote, setEditingQuote] = useState<QuoteData | null>(null)
  const [editableItems, setEditableItems] = useState<QuoteItem[]>([])
  const [editableTotal, setEditableTotal] = useState<number>(0)
  const [editableTaxes, setEditableTaxes] = useState<string>("")
  const [isSavingEdit, setIsSavingEdit] = useState(false)

  // Selection confirmation
  const [confirmSelectQuote, setConfirmSelectQuote] = useState<QuoteData | null>(null)
  const [isSelecting, setIsSelecting] = useState(false)

  // Fetch wedding header
  useEffect(() => {
    fetchWithAuth(`/api/v1/weddings/${id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && !data.error) {
          setWedding({
            couple_names: data.couple_names,
            dates: data.dates,
            destination: data.destination,
            package_type: data.package_type,
            guest_count: data.guest_count,
            health_status: data.health_status,
          })
        }
      })
      .catch(() => {})
  }, [id])

  // Fetch Quotes and Comparison
  const fetchData = useCallback(() => {
    setLoading(true)
    Promise.all([
      fetchWithAuth(`/api/v1/weddings/${id}/quotes?category=${category}`).then((r) =>
        r.ok ? r.json() : []
      ),
      fetchWithAuth(`/api/v1/weddings/${id}/quote-comparisons?category=${category}`, {
        method: "POST",
      }).then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([quotesData, compData]) => {
        if (Array.isArray(quotesData)) {
          setQuotes(quotesData)
        }
        if (compData) {
          if (compData.comparison_items) setComparisonItems(compData.comparison_items)
          if (compData.insights) setInsights(compData.insights)
        }
      })
      .catch(() => {
        addToast("Failed to retrieve quote intelligence from server", "error")
      })
      .finally(() => setLoading(false))
  }, [id, category, addToast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Handle PDF Upload
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadFile) {
      addToast("Please choose a PDF quotation file to upload", "error")
      return
    }

    setIsUploading(true)
    const formData = new FormData()
    formData.append("file", uploadFile)
    formData.append("vendor_name", uploadVendorName || uploadFile.name.replace(".pdf", ""))
    formData.append("category", category)

    try {
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/quotes/upload`, {
        method: "POST",
        body: formData,
      })
      const result = await res.json()
      if (!res.ok) {
        throw new Error(result.detail || "Upload failed")
      }

      addToast(`Uploaded ${uploadFile.name}. Processing quotation pipeline.`, "success")
      setIsUploadOpen(false)
      setUploadFile(null)
      setUploadVendorName("")
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error uploading file"
      addToast(msg, "error")
    } finally {
      setIsUploading(false)
    }
  }

  // Open Edit Line Items Modal
  const handleOpenEdit = (quote: QuoteData) => {
    setEditingQuote(quote)
    setEditableItems(
      quote.items && quote.items.length > 0
        ? [...quote.items]
        : [
            {
              original_description: quote.scope_summary || "Catering Service Package",
              normalized_category: "Catering",
              quantity: quote.guest_count_basis || 420,
              unit: "plate",
              unit_price: quote.price_per_unit || 3500,
              line_total: quote.total_amount,
            },
          ]
    )
    setEditableTotal(quote.total_amount)
    setEditableTaxes(quote.taxes_detail || "Included")
  }

  const handleAddItemRow = () => {
    setEditableItems([
      ...editableItems,
      {
        original_description: "",
        normalized_category: "Catering",
        quantity: 1,
        unit: "unit",
        unit_price: 0,
        line_total: 0,
      },
    ])
  }

  const handleRemoveItemRow = (index: number) => {
    setEditableItems(editableItems.filter((_, idx) => idx !== index))
  }

  const handleItemFieldChange = (
    index: number,
    field: keyof QuoteItem,
    val: string | number
  ) => {
    const updated = [...editableItems]
    updated[index] = { ...updated[index], [field]: val }
    if (field === "quantity" || field === "unit_price") {
      const qty = Number(updated[index].quantity) || 0
      const up = Number(updated[index].unit_price) || 0
      updated[index].line_total = qty * up
    }
    setEditableItems(updated)

    // Recalculate total
    const sum = updated.reduce((acc, it) => acc + (Number(it.line_total) || 0), 0)
    if (sum > 0) setEditableTotal(sum)
  }

  const handleSaveItems = async () => {
    if (!editingQuote) return
    setIsSavingEdit(true)
    try {
      // 1. Update line items
      const resItems = await fetchWithAuth(`/api/v1/quotes/${editingQuote.id}/items`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: editableItems }),
      })
      if (!resItems.ok) throw new Error("Failed to update items")

      // 2. Update quote total and tax detail
      await fetchWithAuth(`/api/v1/quotes/${editingQuote.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          total_amount: editableTotal,
          taxes_detail: editableTaxes,
          human_verified: true,
        }),
      })

      addToast("Quotation corrections saved and verified", "success")
      setEditingQuote(null)
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error saving corrections"
      addToast(msg, "error")
    } finally {
      setIsSavingEdit(false)
    }
  }

  // Handle Vendor Selection
  const handleSelectConfirm = async () => {
    if (!confirmSelectQuote) return
    setIsSelecting(true)
    try {
      const res = await fetchWithAuth(`/api/v1/quotes/${confirmSelectQuote.id}/select`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notes: "Approved vendor selected via procurement comparison matrix.",
          selected_by: "Aarav Mehta",
        }),
      })
      const result = await res.json()
      if (!res.ok) {
        throw new Error(result.detail || "Selection approval failed")
      }

      addToast(result.message || "Vendor approved successfully", "success")
      setConfirmSelectQuote(null)
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error selecting vendor"
      addToast(msg, "error")
    } finally {
      setIsSelecting(false)
    }
  }

  return (
    <div className="flex flex-col min-h-full">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      <WeddingWorkspaceHeader
        coupleName={wedding.couple_names}
        dates={wedding.dates}
        destination={wedding.destination}
        packageType={wedding.package_type}
        guestCount={wedding.guest_count}
        healthStatus={wedding.health_status}
      />

      <div className="p-4 md:p-8 max-w-[1440px] w-full mx-auto space-y-6">
        {/* Category Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-[#878074]">
              <span>Vendors & quotes</span>
              <span>/</span>
              <span className="text-[#292E27] font-medium capitalize">{category}</span>
            </div>
            <h3 className="font-editorial text-2xl text-[#292E27] font-normal mt-0.5">
              Catering · {wedding.guest_count} expected guests
            </h3>
            <p className="text-xs text-[#69655D] mt-0.5">
              Wedding dinner · {wedding.dates} · The Oberoi Rajvilas
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-[#878074] font-medium">
              {quotes.length} quotations evaluated
            </span>
            <button
              type="button"
              onClick={() => setIsUploadOpen(true)}
              className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Upload className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
              <span>Upload quote PDF</span>
            </button>
          </div>
        </div>

        {/* AI Procurement Insights Bar */}
        {insights && insights.recommended_vendor && (
          <div className="p-4 bg-[#F4EFEA] border border-[#E2DBD0] rounded-lg shadow-xs space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#885A14]">
              <Sparkles className="w-4 h-4 text-[#C4A46D]" />
              <span>AI Procurement Intelligence & Comparison Insights</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 text-xs text-[#524E48]">
              <div className="bg-white p-3 rounded border border-[#E2DBD0]">
                <span className="text-[11px] text-[#878074] block">Lowest Base Quoted</span>
                <span className="font-semibold text-[#292E27]">
                  {insights.lowest_quoted_base?.vendor_name}
                </span>
                <span className="text-[11px] text-[#524E48] block">
                  {formatINR(insights.lowest_quoted_base?.amount || 0, true)}
                </span>
              </div>

              <div className="bg-white p-3 rounded border border-[#E2DBD0]">
                <span className="text-[11px] text-[#878074] block">
                  Lowest Estimated Final (with GST & DG)
                </span>
                <span className="font-semibold text-[#292E27]">
                  {insights.lowest_estimated_final?.vendor_name}
                </span>
                <span className="text-[11px] text-[#61765B] font-medium block">
                  {formatINR(insights.lowest_estimated_final?.amount || 0, true)}
                </span>
              </div>

              <div className="bg-white p-3 rounded border border-[#E2DBD0]">
                <span className="text-[11px] text-[#878074] block">Recommended Selection</span>
                <span className="font-semibold text-[#885A14]">
                  {insights.recommended_vendor}
                </span>
                <span className="text-[11px] text-[#69655D] block line-clamp-1">
                  Highest transparency score
                </span>
              </div>
            </div>
            <p className="text-[11px] text-[#69655D] italic pt-1">
              {insights.recommendation_rationale}
            </p>
          </div>
        )}

        {/* 3 Quotation Cards Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-white border border-[#E2DBD0] rounded-lg p-5" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {quotes.map((q) => {
              const isSelected = q.status === "selected"
              const isClosed = q.status === "closed"

              return (
                <div
                  key={q.id}
                  className={`bg-white border rounded-lg p-5 shadow-xs transition-all flex flex-col justify-between ${
                    isSelected
                      ? "border-emerald-600 ring-2 ring-emerald-500/30"
                      : isClosed
                      ? "border-[#E2DBD0] opacity-75"
                      : "border-[#E2DBD0] hover:border-[#C4A46D]/60"
                  }`}
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h4 className="font-editorial text-xl text-[#292E27]">
                          {q.vendor_name}
                        </h4>
                        <div className="flex items-center gap-1.5 text-[11px] text-[#878074] mt-0.5">
                          <span>{q.source_filename || "Document uploaded"}</span>
                          {q.human_verified && (
                            <span className="text-emerald-700 font-medium">(Verified)</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 flex-col items-end">
                        <StatusBadge status={q.status} />
                        {q.extraction_status && q.extraction_status !== "ready" && (
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded capitalize ${
                              q.extraction_status === "failed"
                                ? "bg-rose-100 text-rose-700"
                                : "bg-amber-100 text-amber-700"
                            }`}
                          >
                            {q.extraction_status.replace("_", " ")}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="py-2">
                      <div className="text-2xl font-editorial tabular-nums text-[#292E27]">
                        {formatINR(q.total_amount, true)}
                      </div>
                      <p className="text-xs text-[#69655D] mt-0.5">
                        {q.price_per_unit
                          ? `₹${q.price_per_unit.toLocaleString("en-IN")} / plate · before tax`
                          : "Unit price unavailable"}
                      </p>
                    </div>

                    <ul className="text-xs text-[#524E48] space-y-1.5 mt-3 border-t border-[#F4EFEA] pt-3">
                      <li className="flex items-start gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#C4A46D] mt-1 shrink-0" />
                        <span className="line-clamp-2">
                          {q.scope_summary ||
                            (q.inclusions.length > 0
                              ? q.inclusions.slice(0, 2).join(", ")
                              : "Standard catering scope")}
                        </span>
                      </li>
                      <li className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#C4A46D] shrink-0" />
                        <span>Taxes: {q.taxes_detail || "Needs review"}</span>
                      </li>
                      <li className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#C4A46D] shrink-0" />
                        <span>
                          Generator:{" "}
                          {q.additional_charges.find((c) =>
                            c.name.toLowerCase().includes("generator")
                          )?.amount
                            ? `₹${q.additional_charges.find((c) => c.name.toLowerCase().includes("generator"))?.amount?.toLocaleString("en-IN")} extra`
                            : q.additional_charges.find((c) =>
                                c.name.toLowerCase().includes("generator")
                              )?.status === "included"
                            ? "Included"
                            : "Not specified"}
                        </span>
                      </li>
                      {q.missing_terms && q.missing_terms.length > 0 && (
                        <li className="flex items-start gap-1 text-[11px] text-rose-700 bg-rose-50 p-1.5 rounded">
                          <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                          <span>{q.missing_terms.join("; ")}</span>
                        </li>
                      )}
                    </ul>
                  </div>

                  <div className="pt-4 border-t border-[#F4EFEA] mt-4 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <SourceChip filename={q.source_filename || "PDF Quote"} />
                      <button
                        type="button"
                        onClick={() => handleOpenEdit(q)}
                        className="text-[11px] font-medium text-[#292E27] hover:text-[#C4A46D] inline-flex items-center gap-1 cursor-pointer"
                      >
                        <Edit2 className="w-3 h-3" />
                        <span>Review & edit items</span>
                      </button>
                    </div>

                    <button
                      type="button"
                      disabled={isSelected || isClosed}
                      onClick={() => setConfirmSelectQuote(q)}
                      className={`w-full py-2 text-xs font-medium rounded transition-colors text-center inline-flex items-center justify-center gap-1.5 cursor-pointer disabled:cursor-not-allowed ${
                        isSelected
                          ? "bg-emerald-700 text-white"
                          : isClosed
                          ? "bg-slate-100 text-slate-400 border border-slate-200"
                          : "border border-[#292E27] hover:bg-[#292E27] hover:text-white text-[#292E27]"
                      }`}
                    >
                      {isSelected ? (
                        <>
                          <Check className="w-3.5 h-3.5" />
                          <span>Selected vendor</span>
                        </>
                      ) : isClosed ? (
                        <span>Archived quotation</span>
                      ) : (
                        <span>Select this vendor</span>
                      )}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Side-by-side Comparison Matrix Table */}
        <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4 border-b border-[#E2DBD0] pb-3">
            <div>
              <h4 className="font-editorial text-lg text-[#292E27] font-normal">
                Side-by-side scope details & comparison matrix
              </h4>
              <p className="text-[11px] text-[#878074]">
                Normalized financial and operational breakdown calculated deterministically
              </p>
            </div>
            <button
              type="button"
              onClick={fetchData}
              className="text-xs text-[#69655D] hover:text-[#292E27] flex items-center gap-1 font-medium transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Refresh matrix</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E2DBD0] text-[#878074] uppercase text-[11px]">
                  <th className="pb-3 font-medium">Item / Term</th>
                  {quotes.map((q) => (
                    <th key={q.id} className="pb-3 font-medium">
                      {q.vendor_name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F4EFEA] text-[#292E27]">
                {comparisonItems.length > 0 ? (
                  comparisonItems.map((item, idx) => (
                    <tr key={idx}>
                      <td className="py-3 font-medium text-[#69655D]">{item.parameter}</td>
                      {quotes.map((q) => (
                        <td key={q.id} className="py-3 font-semibold tabular-nums">
                          {item.values[q.vendor_name] || "Not specified"}
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  <>
                    <tr>
                      <td className="py-3 font-medium text-[#69655D]">Base scope quoted</td>
                      {quotes.map((q) => (
                        <td key={q.id} className="py-3 font-semibold tabular-nums">
                          {formatINR(q.total_amount, true)}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-3 font-medium text-[#69655D]">Acoustic generator</td>
                      {quotes.map((q) => {
                        const gen = q.additional_charges.find((c) =>
                          c.name.toLowerCase().includes("generator")
                        )
                        return (
                          <td
                            key={q.id}
                            className={`py-3 ${
                              !gen || gen.status === "not_specified" ? "text-[#AE5142]" : ""
                            }`}
                          >
                            {gen && gen.amount
                              ? `₹${gen.amount.toLocaleString("en-IN")} extra`
                              : gen && gen.status === "included"
                              ? "Included"
                              : "Not specified"}
                          </td>
                        )
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 font-medium text-[#69655D]">Taxes</td>
                      {quotes.map((q) => (
                        <td key={q.id} className="py-3">
                          {q.taxes_detail || "Needs review"}
                        </td>
                      ))}
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-[#878074] mt-4 italic">
            *Deterministic procurement comparison based on uploaded documents. Final contract
            terms verified before booking.
          </p>
        </div>
      </div>

      {/* Upload Quotation Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title="Upload Vendor Quotation PDF"
        subtitle="Extract pricing, line items, taxes and terms using AI extraction pipeline"
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
          <div className="space-y-1">
            <label className="text-slate-300 font-medium">Vendor / Business Name *</label>
            <input
              type="text"
              value={uploadVendorName}
              onChange={(e) => setUploadVendorName(e.target.value)}
              placeholder="e.g. Saffron Table / Mewar Kitchens"
              className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="space-y-1">
            <label className="text-slate-300 font-medium">PDF Document *</label>
            <div className="border-2 border-dashed border-[#2A364F] hover:border-[#C4A46D] rounded-lg p-6 text-center transition-colors">
              <input
                type="file"
                accept=".pdf,application/pdf"
                id="quote-file-input"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setUploadFile(e.target.files[0])
                    if (!uploadVendorName) {
                      setUploadVendorName(
                        e.target.files[0].name.replace(".pdf", "").replace("_", " ")
                      )
                    }
                  }
                }}
              />
              <label
                htmlFor="quote-file-input"
                className="flex flex-col items-center gap-2 cursor-pointer"
              >
                <FileText className="w-8 h-8 text-[#C4A46D]" />
                <span className="text-slate-200 font-medium">
                  {uploadFile ? uploadFile.name : "Click to select quotation PDF"}
                </span>
                <span className="text-[11px] text-slate-400">
                  Maximum file size: 15 MB. Text extraction and duplicate verification enabled.
                </span>
              </label>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
            <button
              type="button"
              onClick={() => setIsUploadOpen(false)}
              className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUploading || !uploadFile}
              className="px-4 py-2 rounded text-xs font-semibold bg-[#C4A46D] hover:bg-[#B3935C] text-[#131926] transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isUploading ? "Uploading & Extracting..." : "Process Quotation"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Review & Edit Extracted Line Items Modal */}
      <Modal
        isOpen={editingQuote !== null}
        onClose={() => setEditingQuote(null)}
        title={`Review & Correct: ${editingQuote?.vendor_name}`}
        subtitle="Planner verification for extracted line items, plate rates and tax terms"
        maxWidth="max-w-3xl"
      >
        <div className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3 p-3 bg-[#1A2234] rounded border border-[#2A364F]">
            <div>
              <label className="text-slate-400 block mb-1">Total Amount (INR)</label>
              <input
                type="number"
                value={editableTotal}
                onChange={(e) => setEditableTotal(Number(e.target.value) || 0)}
                className="w-full bg-[#131926] border border-[#2A364F] rounded px-2.5 py-1.5 text-white font-semibold"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Tax Terms</label>
              <input
                type="text"
                value={editableTaxes}
                onChange={(e) => setEditableTaxes(e.target.value)}
                placeholder="e.g. 18% extra or Included"
                className="w-full bg-[#131926] border border-[#2A364F] rounded px-2.5 py-1.5 text-white"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-white">Extracted Line Items:</span>
              <button
                type="button"
                onClick={handleAddItemRow}
                className="inline-flex items-center gap-1 text-[11px] text-[#C4A46D] hover:underline cursor-pointer"
              >
                <Plus className="w-3 h-3" />
                <span>Add Item</span>
              </button>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {editableItems.map((item, idx) => (
                <div
                  key={idx}
                  className="p-2.5 bg-[#1A2234] border border-[#2A364F] rounded flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={item.original_description}
                    onChange={(e) =>
                      handleItemFieldChange(idx, "original_description", e.target.value)
                    }
                    placeholder="Description"
                    className="flex-1 bg-[#131926] border border-[#2A364F] rounded px-2 py-1 text-white text-xs"
                  />
                  <input
                    type="number"
                    value={item.quantity || ""}
                    onChange={(e) =>
                      handleItemFieldChange(idx, "quantity", Number(e.target.value) || 0)
                    }
                    placeholder="Qty"
                    className="w-16 bg-[#131926] border border-[#2A364F] rounded px-2 py-1 text-white text-xs"
                  />
                  <input
                    type="text"
                    value={item.unit || ""}
                    onChange={(e) => handleItemFieldChange(idx, "unit", e.target.value)}
                    placeholder="Unit"
                    className="w-16 bg-[#131926] border border-[#2A364F] rounded px-2 py-1 text-white text-xs"
                  />
                  <input
                    type="number"
                    value={item.unit_price || ""}
                    onChange={(e) =>
                      handleItemFieldChange(idx, "unit_price", Number(e.target.value) || 0)
                    }
                    placeholder="Rate"
                    className="w-20 bg-[#131926] border border-[#2A364F] rounded px-2 py-1 text-white text-xs"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveItemRow(idx)}
                    className="p-1 text-slate-400 hover:text-rose-400"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
            <button
              type="button"
              onClick={() => setEditingQuote(null)}
              className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveItems}
              disabled={isSavingEdit}
              className="px-4 py-2 rounded text-xs font-semibold bg-[#C4A46D] hover:bg-[#B3935C] text-[#131926] transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isSavingEdit ? "Saving..." : "Verify & Save Corrections"}
            </button>
          </div>
        </div>
      </Modal>

      {/* Select Vendor Confirmation Modal */}
      <Modal
        isOpen={confirmSelectQuote !== null}
        onClose={() => setConfirmSelectQuote(null)}
        title="Confirm Vendor Selection"
        subtitle="This action locks in the chosen vendor and marks competing proposals closed"
        maxWidth="max-w-md"
      >
        {confirmSelectQuote && (
          <div className="space-y-4 text-xs text-slate-300">
            <div className="p-3 bg-[#1A2234] rounded border border-[#2A364F] space-y-1">
              <div className="text-sm font-semibold text-white">
                {confirmSelectQuote.vendor_name}
              </div>
              <div>Category: {confirmSelectQuote.category}</div>
              <div>Quoted Total: {formatINR(confirmSelectQuote.total_amount, true)}</div>
            </div>

            <p className="leading-relaxed text-slate-400">
              When approved:
              <br />· Vendor will be assigned as the confirmed partner for this wedding.
              <br />· Competing quotations in this category will be archived as closed.
              <br />· Duplicate selections for this category are permanently blocked.
            </p>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
              <button
                type="button"
                onClick={() => setConfirmSelectQuote(null)}
                className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSelectConfirm}
                disabled={isSelecting}
                className="px-4 py-2 rounded text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50 cursor-pointer"
              >
                {isSelecting ? "Selecting..." : "Approve & Lock Selection"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
