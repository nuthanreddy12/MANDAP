import React, { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import {
  Calendar,
  CreditCard,
  MessageSquare,
  FileText,
  LogOut,
  MapPin,
  Clock,
  Send,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Download,
  Users,
  Compass,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"
import { formatINR } from "@/lib/formatters"
import { useAuth } from "@/lib/useAuth"

interface CustomerWedding {
  wedding_id: string
  couple_names: string
  dates: string
  destination: string
  venue: string
  package_type: string
  guest_count: number
  assigned_planner: string
  client_name: string
  client_email: string
}

interface TimelineEventItem {
  id: string
  day_number: number
  event_date: string
  start_time: string
  end_time: string
  title: string
  location: string
  status: string
}

interface PaymentMilestoneItem {
  id: string
  stage: string
  amount: number
  date: string
  reference: string
  status: string
}

interface CustomerPaymentsData {
  client_fee_total: number
  total_paid: number
  balance_outstanding: number
  milestones: PaymentMilestoneItem[]
}

interface CustomerRequestItem {
  id: string
  category: string
  title: string
  details: string
  status: string
  planner_response?: string | null
  created_at?: string | null
}

interface SharedDocumentItem {
  id: string
  filename: string
  file_size?: number
  content_type?: string
  created_at?: string | null
}

export const CustomerDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { signOut } = useAuth()

  const [activeTab, setActiveTab] = useState<"schedule" | "payments" | "requests" | "documents">("schedule")
  const [wedding, setWedding] = useState<CustomerWedding | null>(null)
  const [schedule, setSchedule] = useState<TimelineEventItem[]>([])
  const [payments, setPayments] = useState<CustomerPaymentsData | null>(null)
  const [requests, setRequests] = useState<CustomerRequestItem[]>([])
  const [documents, setDocuments] = useState<SharedDocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [downloadingDocId, setDownloadingDocId] = useState<string | null>(null)

  const handleDownloadDocument = async (docId: string, filename: string) => {
    try {
      setDownloadingDocId(docId)
      const res = await fetchWithAuth(`/api/v1/customer/documents/${docId}/download`)
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || "Failed to download document")
      }
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error downloading document")
    } finally {
      setDownloadingDocId(null)
    }
  }

  // Request form state
  const [reqCategory, setReqCategory] = useState("catering")
  const [reqTitle, setReqTitle] = useState("")
  const [reqDetails, setReqDetails] = useState("")
  const [submittingReq, setSubmittingReq] = useState(false)
  const [reqSuccessMsg, setReqSuccessMsg] = useState<string | null>(null)

  const loadDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Fetch wedding details
      const wRes = await fetchWithAuth("/api/v1/customer/wedding")
      if (!wRes.ok) {
        if (wRes.status === 401) {
          localStorage.removeItem("mandap_customer_token")
          localStorage.removeItem("mandap_customer_user")
          localStorage.removeItem("mandap_customer_wedding_id")
          navigate("/customer/login", { replace: true })
          return
        }
        const errJson = await wRes.json().catch(() => ({}))
        throw new Error(errJson.detail || "Could not retrieve wedding details")
      }
      const wData: CustomerWedding = await wRes.json()
      setWedding(wData)

      // 2. Fetch schedule
      const sRes = await fetchWithAuth("/api/v1/customer/schedule")
      if (sRes.ok) {
        const sData = await sRes.json()
        setSchedule(sData)
      }

      // 3. Fetch payments
      const pRes = await fetchWithAuth("/api/v1/customer/payments")
      if (pRes.ok) {
        const pData = await pRes.json()
        setPayments(pData)
      }

      // 4. Fetch requests
      const rRes = await fetchWithAuth("/api/v1/customer/requests")
      if (rRes.ok) {
        const rData = await rRes.json()
        setRequests(rData)
      }

      // 5. Fetch shared documents
      const dRes = await fetchWithAuth("/api/v1/customer/documents")
      if (dRes.ok) {
        const dData = await dRes.json()
        setDocuments(dData)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error loading dashboard")
    } finally {
      setLoading(false)
    }
  }, [navigate])

  useEffect(() => {
    loadDashboardData()
  }, [loadDashboardData])

  const handleLogout = async () => {
    localStorage.removeItem("mandap_customer_token")
    localStorage.removeItem("mandap_customer_user")
    localStorage.removeItem("mandap_customer_wedding_id")
    await signOut()
    navigate("/customer/login", { replace: true })
  }

  const handleRequestSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!reqTitle || !reqDetails) return

    setSubmittingReq(true)
    setReqSuccessMsg(null)
    try {
      const res = await fetchWithAuth("/api/v1/customer/requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: reqCategory,
          title: reqTitle.trim(),
          details: reqDetails.trim(),
        }),
      })

      if (res.ok) {
        const newReq = await res.json()
        setRequests((prev) => [newReq.request, ...prev])
        setReqTitle("")
        setReqDetails("")
        setReqSuccessMsg("Your request was sent directly to your lead wedding planner.")
        setTimeout(() => setReqSuccessMsg(null), 5000)
      } else {
        const err = await res.json()
        setError(err.detail || "Failed to submit request")
      }
    } catch {
      setError("Network error while submitting request")
    } finally {
      setSubmittingReq(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen w-screen bg-[#FBFAF7] flex flex-col items-center justify-center text-[#292E27]">
        <div className="flex items-center gap-2 mb-3">
          <span className="font-editorial text-2xl tracking-wider text-[#292E27]">MANDAP</span>
          <span className="text-[#C4A46D] text-xs">✳</span>
        </div>
        <p className="text-xs text-[#878074]">Preparing your wedding sanctuary...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FBFAF7] text-[#292E27] flex flex-col">
      {/* Top Luxury Navigation */}
      <header className="px-6 py-4 md:px-12 flex items-center justify-between border-b border-[#E8E2D9] bg-white sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3">
            <img src="/mandap-logo.png" alt="MANDAP" className="h-9 w-auto object-contain" />
            <span className="font-serif text-xl tracking-wider text-[#541424] font-medium">
              MANDAP
            </span>
          </div>
          <span className="hidden sm:inline-block text-xs uppercase tracking-widest text-[#B8860B] pl-3 border-l border-[#E8E2D9]">
            Client Couple Sanctuary
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right hidden md:block">
            <div className="text-xs font-semibold text-[#292E27]">
              {wedding?.client_name || "Client Couple"}
            </div>
            <div className="text-[11px] text-[#878074]">
              Planner: {wedding?.assigned_planner || "The Royal Knot Team"}
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-xs text-[#878074] hover:text-[#852C1F] transition-colors inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-[#E2DBD0] hover:border-[#852C1F]"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Hero Wedding Banner */}
      <section className="bg-gradient-to-b from-white to-[#F7F4EE] border-b border-[#E8E2D9] px-6 py-8 md:px-12">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FAF5EB] border border-[#E8E2D9] text-[#C4A46D] text-[11px] font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Royal Bespoke Wedding</span>
            </div>
            <h1 className="font-editorial text-3xl md:text-4xl text-[#292E27] tracking-tight mb-2">
              {wedding?.couple_names || "Your Royal Wedding"}
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-xs text-[#524E48]">
              <span className="inline-flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-[#C4A46D]" />
                {wedding?.venue}, {wedding?.destination}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-[#C4A46D]" />
                {wedding?.dates}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Users className="w-4 h-4 text-[#C4A46D]" />
                {wedding?.guest_count} Honored Guests
              </span>
            </div>
          </div>

          <div className="p-4 bg-white border border-[#E2DBD0] rounded-xl shadow-xs min-w-[260px]">
            <div className="text-[11px] uppercase tracking-wider text-[#878074] mb-1">
              Your Dedicated Lead Planner
            </div>
            <div className="text-sm font-semibold text-[#292E27]">
              {wedding?.assigned_planner || "Nisha Sharma"}
            </div>
            <div className="text-xs text-[#878074] mt-0.5">
              The Royal Knot Wedding Planning Atelier
            </div>
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-[#E8E2D9] px-6 md:px-12">
        <div className="max-w-6xl mx-auto flex items-center gap-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab("schedule")}
            className={`py-3.5 px-4 text-xs font-medium border-b-2 transition-colors inline-flex items-center gap-2 cursor-pointer whitespace-nowrap ${
              activeTab === "schedule"
                ? "border-[#292E27] text-[#292E27]"
                : "border-transparent text-[#878074] hover:text-[#292E27]"
            }`}
          >
            <Clock className="w-4 h-4 text-[#C4A46D]" />
            <span>Wedding Schedule</span>
          </button>

          <button
            onClick={() => setActiveTab("payments")}
            className={`py-3.5 px-4 text-xs font-medium border-b-2 transition-colors inline-flex items-center gap-2 cursor-pointer whitespace-nowrap ${
              activeTab === "payments"
                ? "border-[#292E27] text-[#292E27]"
                : "border-transparent text-[#878074] hover:text-[#292E27]"
            }`}
          >
            <CreditCard className="w-4 h-4 text-[#C4A46D]" />
            <span>Payment Milestones</span>
          </button>

          <button
            onClick={() => setActiveTab("requests")}
            className={`py-3.5 px-4 text-xs font-medium border-b-2 transition-colors inline-flex items-center gap-2 cursor-pointer whitespace-nowrap ${
              activeTab === "requests"
                ? "border-[#292E27] text-[#292E27]"
                : "border-transparent text-[#878074] hover:text-[#292E27]"
            }`}
          >
            <MessageSquare className="w-4 h-4 text-[#C4A46D]" />
            <span>Planner Requests</span>
            {requests.length > 0 && (
              <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-[#FAF5EB] text-[#C4A46D] font-semibold">
                {requests.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("documents")}
            className={`py-3.5 px-4 text-xs font-medium border-b-2 transition-colors inline-flex items-center gap-2 cursor-pointer whitespace-nowrap ${
              activeTab === "documents"
                ? "border-[#292E27] text-[#292E27]"
                : "border-transparent text-[#878074] hover:text-[#292E27]"
            }`}
          >
            <FileText className="w-4 h-4 text-[#C4A46D]" />
            <span>Shared Documents</span>
            {documents.length > 0 && (
              <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-[#FAF5EB] text-[#C4A46D] font-semibold">
                {documents.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full p-6 md:p-12">
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-[#AE5142]/10 border border-[#AE5142]/30 flex items-center gap-3 text-xs text-[#AE5142]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* TAB 1: SCHEDULE */}
        {activeTab === "schedule" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-editorial text-2xl text-[#292E27]">Approved Timeline & Schedule</h2>
                <p className="text-xs text-[#878074] mt-0.5">
                  Live itinerary curated by your lead planner for your multi-day celebration
                </p>
              </div>
            </div>

            {schedule.length === 0 ? (
              <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-xl text-xs text-[#878074]">
                Schedule timeline is being finalized with your planning atelier.
              </div>
            ) : (
              <div className="grid gap-4">
                {schedule.map((item) => (
                  <div
                    key={item.id}
                    className="p-5 bg-white border border-[#E2DBD0] rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-2xs hover:border-[#C4A46D] transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-lg bg-[#FAF5EB] border border-[#E8E2D9] flex flex-col items-center justify-center text-center shrink-0">
                        <span className="text-[10px] font-semibold text-[#878074] uppercase">Day</span>
                        <span className="text-base font-editorial font-bold text-[#292E27]">
                          {item.day_number}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-[#292E27]">{item.title}</h3>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-[#878074] mt-1">
                          <span className="inline-flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-[#C4A46D]" />
                            {item.start_time} - {item.end_time}
                          </span>
                          <span className="inline-flex items-center gap-1">
                            <Compass className="w-3.5 h-3.5 text-[#C4A46D]" />
                            {item.location}
                          </span>
                        </div>
                      </div>
                    </div>

                    <span
                      className={`text-[11px] font-medium px-2.5 py-1 rounded-full uppercase tracking-wider self-start sm:self-center ${
                        item.status === "complete"
                          ? "bg-[#3F5A36]/10 text-[#3F5A36] border border-[#3F5A36]/30"
                          : "bg-[#FAF5EB] text-[#C4A46D] border border-[#E8E2D9]"
                      }`}
                    >
                      {item.status === "complete" ? "Completed" : "Scheduled"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: PAYMENTS */}
        {activeTab === "payments" && (
          <div className="space-y-6">
            <div>
              <h2 className="font-editorial text-2xl text-[#292E27]">Client Payment Milestones</h2>
              <p className="text-xs text-[#878074] mt-0.5">
                Transparent view of your agency service agreement and confirmed transaction records
              </p>
            </div>

            {/* Financial Overview Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-5 bg-white border border-[#E2DBD0] rounded-xl shadow-2xs">
                <div className="text-[11px] font-medium text-[#878074] uppercase tracking-wider">
                  Total Agreed Planning Fee
                </div>
                <div className="text-2xl font-editorial text-[#292E27] mt-1">
                  {formatINR(payments?.client_fee_total ?? 750000)}
                </div>
                <div className="text-[11px] text-[#878074] mt-1">
                  Full service bespoke engagement
                </div>
              </div>

              <div className="p-5 bg-white border border-[#E2DBD0] rounded-xl shadow-2xs">
                <div className="text-[11px] font-medium text-[#878074] uppercase tracking-wider">
                  Total Received by Agency
                </div>
                <div className="text-2xl font-editorial text-[#3F5A36] mt-1">
                  {formatINR(payments?.total_paid ?? 300000)}
                </div>
                <div className="text-[11px] text-[#3F5A36] mt-1 inline-flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Verified receipts issued</span>
                </div>
              </div>

              <div className="p-5 bg-white border border-[#E2DBD0] rounded-xl shadow-2xs">
                <div className="text-[11px] font-medium text-[#878074] uppercase tracking-wider">
                  Outstanding Balance
                </div>
                <div className="text-2xl font-editorial text-[#852C1F] mt-1">
                  {formatINR(payments?.balance_outstanding ?? 450000)}
                </div>
                <div className="text-[11px] text-[#878074] mt-1">
                  Payable per scheduled milestones
                </div>
              </div>
            </div>

            {/* Milestones Ledger */}
            <div className="bg-white border border-[#E2DBD0] rounded-xl p-6 shadow-2xs">
              <h3 className="text-sm font-semibold text-[#292E27] mb-4">Milestone Schedule</h3>
              <div className="divide-y divide-[#E8E2D9]">
                {payments?.milestones?.map((m) => (
                  <div key={m.id} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                    <div>
                      <div className="text-xs font-semibold text-[#292E27]">{m.stage}</div>
                      <div className="text-[11px] text-[#878074] mt-0.5">
                        Target Date: {m.date} &middot; Reference: {m.reference}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs font-bold text-[#292E27]">{formatINR(m.amount)}</div>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full inline-block mt-1 ${
                          m.status === "paid"
                            ? "bg-[#3F5A36]/10 text-[#3F5A36] border border-[#3F5A36]/30"
                            : "bg-[#FAF5EB] text-[#C4A46D] border border-[#E8E2D9]"
                        }`}
                      >
                        {m.status === "paid" ? "Paid" : "Scheduled"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-[#FAF8F5] border border-[#E2DBD0] rounded-xl text-xs text-[#878074] leading-relaxed">
              <strong>Payment Support:</strong> All transactions are settled via NEFT or RTGS directly with The Royal Knot. For GST invoices or bank wiring details, contact your assigned wedding coordinator.
            </div>
          </div>
        )}

        {/* TAB 3: PLANNER REQUESTS */}
        {activeTab === "requests" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Submit Request Column */}
            <div className="lg:col-span-1">
              <div className="bg-white border border-[#E2DBD0] rounded-xl p-6 shadow-2xs sticky top-24">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-[#C4A46D]" />
                  <h3 className="font-editorial text-lg text-[#292E27]">Submit a Requirement</h3>
                </div>
                <p className="text-xs text-[#878074] mb-4">
                  Send special requests, dietary restrictions, or musical selections to your planner
                </p>

                {reqSuccessMsg && (
                  <div className="mb-4 p-3 rounded-md bg-[#3F5A36]/10 border border-[#3F5A36]/30 text-xs text-[#3F5A36] flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{reqSuccessMsg}</span>
                  </div>
                )}

                <form onSubmit={handleRequestSubmit} className="space-y-3.5">
                  <div>
                    <label className="block text-xs font-medium text-[#524E48] mb-1" htmlFor="req-cat">
                      Category
                    </label>
                    <select
                      id="req-cat"
                      value={reqCategory}
                      onChange={(e) => setReqCategory(e.target.value)}
                      className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md px-3 py-2 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
                    >
                      <option value="catering">Dietary & Catering</option>
                      <option value="music">Music & Performance</option>
                      <option value="logistics">Guest Logistics & Transport</option>
                      <option value="decor">Decor & Aesthetic Details</option>
                      <option value="general">General Wedding Inquiry</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[#524E48] mb-1" htmlFor="req-title">
                      Title
                    </label>
                    <input
                      id="req-title"
                      type="text"
                      value={reqTitle}
                      onChange={(e) => setReqTitle(e.target.value)}
                      placeholder="e.g. Jain meal count for Sangeet"
                      required
                      className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md px-3 py-2 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[#524E48] mb-1" htmlFor="req-details">
                      Details
                    </label>
                    <textarea
                      id="req-details"
                      rows={4}
                      value={reqDetails}
                      onChange={(e) => setReqDetails(e.target.value)}
                      placeholder="Please outline the specific details, timings, or guest preferences..."
                      required
                      className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md px-3 py-2 text-[#292E27] focus:outline-none focus:border-[#C4A46D] resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submittingReq}
                    className="w-full h-9 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
                  >
                    {submittingReq ? (
                      <span>Sending...</span>
                    ) : (
                      <>
                        <span>Submit to Lead Planner</span>
                        <Send className="w-3 h-3 text-[#C4A46D]" />
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Requests History Column */}
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h3 className="font-editorial text-2xl text-[#292E27]">Submitted Requests</h3>
                <p className="text-xs text-[#878074] mt-0.5">
                  Track requirements reviewed and confirmed by your planning atelier
                </p>
              </div>

              {requests.length === 0 ? (
                <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-xl text-xs text-[#878074]">
                  No requirements submitted yet. Use the form to coordinate any special wishes with your planner.
                </div>
              ) : (
                <div className="space-y-3.5">
                  {requests.map((r) => (
                    <div
                      key={r.id}
                      className="p-5 bg-white border border-[#E2DBD0] rounded-xl shadow-2xs space-y-3"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="inline-block px-2 py-0.5 rounded-full bg-[#FAF5EB] border border-[#E8E2D9] text-[#C4A46D] text-[10px] font-semibold uppercase tracking-wider mb-1.5">
                            {r.category}
                          </div>
                          <h4 className="text-sm font-semibold text-[#292E27]">{r.title}</h4>
                        </div>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider shrink-0 ${
                            r.status === "confirmed"
                              ? "bg-[#3F5A36]/10 text-[#3F5A36] border border-[#3F5A36]/30"
                              : "bg-[#FAF5EB] text-[#C4A46D] border border-[#E8E2D9]"
                          }`}
                        >
                          {r.status}
                        </span>
                      </div>

                      <p className="text-xs text-[#524E48] leading-relaxed whitespace-pre-wrap">
                        {r.details}
                      </p>

                      {r.planner_response && (
                        <div className="p-3 bg-[#FAF8F5] border border-[#E2DBD0] rounded-lg">
                          <div className="text-[11px] font-semibold text-[#292E27] mb-0.5">
                            Planner Response:
                          </div>
                          <p className="text-xs text-[#524E48] leading-relaxed">
                            {r.planner_response}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: SHARED DOCUMENTS */}
        {activeTab === "documents" && (
          <div className="space-y-6">
            <div>
              <h2 className="font-editorial text-2xl text-[#292E27]">Shared Wedding Documents</h2>
              <p className="text-xs text-[#878074] mt-0.5">
                Official ceremony guides, approved itineraries, and decor layouts published for your review
              </p>
            </div>

            {documents.length === 0 ? (
              <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-xl text-xs text-[#878074]">
                Your planner has not published documents to the client sanctuary yet.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {documents.map((d) => (
                  <div
                    key={d.id}
                    className="p-5 bg-white border border-[#E2DBD0] rounded-xl shadow-2xs flex items-center justify-between gap-4 hover:border-[#C4A46D] transition-colors"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-10 h-10 rounded-lg bg-[#FAF5EB] border border-[#E8E2D9] text-[#C4A46D] flex items-center justify-center shrink-0">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-[#292E27]">{d.filename}</div>
                        <div className="text-[11px] text-[#878074] mt-0.5">
                          {d.file_size ? `${Math.round(d.file_size / 1024)} KB` : "PDF Document"}
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleDownloadDocument(d.id, d.filename)}
                      disabled={downloadingDocId === d.id}
                      className="p-2 rounded-md border border-[#E2DBD0] text-[#878074] hover:text-[#292E27] hover:border-[#292E27] transition-colors cursor-pointer disabled:opacity-50"
                      title="Download document"
                    >
                      <Download className={`w-4 h-4 ${downloadingDocId === d.id ? "animate-pulse" : ""}`} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="p-4 bg-[#FAF8F5] border border-[#E2DBD0] rounded-xl text-xs text-[#878074] leading-relaxed">
              <strong>Sanctuary Privacy:</strong> Confidential vendor quote comparison tables, internal profit margins, and contractor worksheets are retained within the staff planning room.
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="px-6 py-6 border-t border-[#E8E2D9] text-center text-[11px] text-[#878074] bg-white">
        MANDAP &middot; The Royal Knot Bespoke Wedding Portal &middot; Private Client Sanctuary
      </footer>
    </div>
  )
}
