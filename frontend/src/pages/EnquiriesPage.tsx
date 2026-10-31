import React, { useEffect, useState, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { Modal } from "@/components/ui/Modal"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import { formatINR } from "@/lib/formatters"
import {
  Calendar,
  MapPin,
  Users,
  Plus,
  Search,
  Phone,
  Mail,
  Edit2,
  CheckCircle,
  ArrowRight,
  Filter,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

const enquirySchema = z.object({
  couple_names: z.string().min(3, "Couple names must be at least 3 characters"),
  email: z.string().email("Please provide a valid email address").or(z.literal("")),
  phone: z.string().min(8, "Valid phone number required"),
  source: z.string().min(1, "Select enquiry source"),
  rough_date: z.string().min(1, "Wedding date or month is required"),
  destination: z.string().min(1, "Destination is required"),
  guest_count: z.coerce.number().min(10, "Minimum 10 guests"),
  budget_max: z.coerce.number().min(100000, "Minimum budget is Rs 1,00,000"),
  theme: z.string().min(1, "Theme preference is required"),
  package_type: z.string().default("full_service"),
  status: z.string().default("new"),
  assigned_owner: z.string().default("Aarav Mehta"),
  follow_up_date: z.string().optional(),
  notes: z.string().optional(),
})

type EnquiryFormData = z.infer<typeof enquirySchema>

interface EnquiryItem {
  id: string
  couple_names: string
  couple?: string
  destination: string
  rough_date?: string
  date?: string
  guest_count: number
  guests?: number
  theme?: string
  budget_max?: number
  budget?: number
  source?: string
  package_type?: string
  status: string
  assigned_owner?: string
  owner?: string
  notes?: string
  phone?: string
  email?: string
  follow_up_date?: string
  converted_wedding_id?: string
}

export const EnquiriesPage: React.FC = () => {
  const navigate = useNavigate()
  const { toasts, addToast, removeToast } = useToast()

  const [leads, setLeads] = useState<EnquiryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [destinationFilter, setDestinationFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")

  // Modals state
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [editingEnquiry, setEditingEnquiry] = useState<EnquiryItem | null>(null)
  const [convertingEnquiry, setConvertingEnquiry] = useState<EnquiryItem | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // React Hook Form for Create/Edit
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<EnquiryFormData>({
    resolver: zodResolver(enquirySchema) as any,

    defaultValues: {
      couple_names: "",
      email: "",
      phone: "",
      source: "Direct Call",
      rough_date: "",
      destination: "Jaipur",
      guest_count: 400,
      budget_max: 15000000,
      theme: "Royal Rajputana Palace",
      package_type: "full_service",
      status: "new",
      assigned_owner: "Aarav Mehta",
      follow_up_date: "",
      notes: "",
    },
  })

  const fetchEnquiries = useCallback(() => {
    setLoading(true)
    fetchWithAuth("/api/v1/enquiries")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        setLeads(data || [])
      })
      .catch(() => {
        addToast("Failed to load enquiries from database", "error")
      })
      .finally(() => setLoading(false))
  }, [addToast])

  useEffect(() => {
    fetchEnquiries()
  }, [fetchEnquiries])

  // Open Edit Modal
  const handleEditClick = (lead: EnquiryItem) => {
    setEditingEnquiry(lead)
    setValue("couple_names", lead.couple_names || lead.couple || "")
    setValue("email", lead.email || "")
    setValue("phone", lead.phone || "")
    setValue("source", lead.source || "Direct Call")
    setValue("rough_date", lead.rough_date || lead.date || "")
    setValue("destination", lead.destination || "Jaipur")
    setValue("guest_count", lead.guest_count || lead.guests || 400)
    setValue("budget_max", lead.budget_max || lead.budget || 15000000)
    setValue("theme", lead.theme || "Royal Rajputana Palace")
    setValue("package_type", lead.package_type || "full_service")
    setValue("status", lead.status || "new")
    setValue("assigned_owner", lead.assigned_owner || lead.owner || "Aarav Mehta")
    setValue("follow_up_date", lead.follow_up_date || "")
    setValue("notes", lead.notes || "")
  }

  // Handle Create or Update submission
  const onSubmit = async (data: EnquiryFormData) => {
    setIsSubmitting(true)
    try {
      if (editingEnquiry) {
        // Edit PATCH
        const res = await fetchWithAuth(`/api/v1/enquiries/${editingEnquiry.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to update enquiry")
        addToast("Enquiry updated successfully", "success")
        setEditingEnquiry(null)
      } else {
        // Create POST
        const res = await fetchWithAuth("/api/v1/enquiries", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to create enquiry")
        addToast("Enquiry created successfully", "success")
        setIsCreateOpen(false)
      }
      reset()
      fetchEnquiries()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred"
      addToast(message, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handle Enquiry to Wedding Conversion
  const handleConvertConfirm = async () => {
    if (!convertingEnquiry) return
    setIsSubmitting(true)
    try {
      const res = await fetchWithAuth(`/api/v1/enquiries/${convertingEnquiry.id}/convert`, {
        method: "POST",
      })
      const result = await res.json()
      if (!res.ok) {
        throw new Error(result.detail || "Conversion failed")
      }
      addToast(
        `Converted to wedding! Generated ${result.tasks_generated} package tasks.`,
        "success"
      )
      setConvertingEnquiry(null)
      fetchEnquiries()
      // Navigate to wedding workspace after slight delay
      if (result.wedding_id) {
        setTimeout(() => {
          navigate(`/weddings/${result.wedding_id}`)
        }, 800)
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Conversion error"
      addToast(message, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  const filtered = leads.filter((l) => {
    const coupleName = l.couple_names || l.couple || ""
    const dest = l.destination || ""
    const matchesSearch =
      coupleName.toLowerCase().includes(search.toLowerCase()) ||
      dest.toLowerCase().includes(search.toLowerCase())

    const matchesDest =
      destinationFilter === "all" ||
      dest.toLowerCase().includes(destinationFilter.toLowerCase())

    const matchesStatus =
      statusFilter === "all" ||
      l.status.toLowerCase() === statusFilter.toLowerCase()

    return matchesSearch && matchesDest && matchesStatus
  })

  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-6">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
        <div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight">
            Client Enquiries & Leads
          </h2>
          <p className="text-xs text-[#878074] mt-0.5">
            Incoming luxury wedding consultations, status tracking and booking conversions
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            reset()
            setIsCreateOpen(true)
          }}
          className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 self-start sm:self-auto shadow-xs cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          <span>New enquiry</span>
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white p-3.5 border border-[#E2DBD0] rounded-lg flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search
            className="w-3.5 h-3.5 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search enquiries by couple or destination..."
            className="w-full text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-1.5 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D]"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-[#878074]">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={destinationFilter}
            onChange={(e) => setDestinationFilter(e.target.value)}
            className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2.5 py-1.5 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
          >
            <option value="all">All Destinations</option>
            <option value="Jaipur">Jaipur</option>
            <option value="Udaipur">Udaipur</option>
            <option value="Jodhpur">Jodhpur</option>
            <option value="Jaisalmer">Jaisalmer</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2.5 py-1.5 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
          >
            <option value="all">All Statuses</option>
            <option value="new">New</option>
            <option value="meeting_booked">Meeting Booked</option>
            <option value="proposal_sent">Proposal Sent</option>
            <option value="converted">Converted</option>
            <option value="lost">Lost</option>
          </select>
        </div>
      </div>

      {/* Loading Skeletons */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-48 bg-white border border-[#E2DBD0] rounded-lg p-5 space-y-3">
              <div className="h-4 bg-slate-200 rounded w-1/3" />
              <div className="h-3 bg-slate-100 rounded w-1/2" />
              <div className="h-16 bg-slate-50 rounded" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        /* Empty State */
        <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-lg space-y-3">
          <p className="text-sm font-medium text-[#292E27]">No enquiries found</p>
          <p className="text-xs text-[#878074]">
            {search || destinationFilter !== "all" || statusFilter !== "all"
              ? "Try adjusting your search criteria or active filters."
              : "Register your first wedding client lead using the button above."}
          </p>
        </div>
      ) : (
        /* Enquiries Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((lead) => {
            const couple = lead.couple_names || lead.couple || "Untitled Enquiry"
            const dateStr = lead.rough_date || lead.date || "Date to be confirmed"
            const guests = lead.guest_count || lead.guests || 400
            const budgetVal = lead.budget_max || lead.budget || 0
            const ownerVal = lead.assigned_owner || lead.owner || "Aarav Mehta"
            const isConverted = lead.status === "converted" || !!lead.converted_wedding_id

            return (
              <div
                key={lead.id}
                className="p-5 bg-white border border-[#E2DBD0] hover:border-[#C4A46D] rounded-lg shadow-xs transition-all space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-editorial text-lg text-[#292E27]">{couple}</h3>
                    <p className="text-xs text-[#885A14] font-medium">{lead.theme || "Heritage Luxury"}</p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <StatusBadge status={lead.status} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-[#524E48] pt-1">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-[#C4A46D]" />
                    <span>{dateStr}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-[#C4A46D]" />
                    <span>{lead.destination}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-[#C4A46D]" />
                    <span>{guests} guests</span>
                  </div>
                  <div className="tabular-nums font-medium text-[#292E27]">
                    Budget: {formatINR(budgetVal, true)}
                  </div>
                </div>

                <div className="text-xs bg-[#FBFAF7] p-2.5 rounded border border-[#F4EFEA] text-[#69655D] space-y-1.5">
                  <p className="line-clamp-2">{lead.notes || "No additional notes provided."}</p>
                  <div className="flex items-center justify-between text-[11px] text-[#878074] pt-1.5 border-t border-[#F4EFEA]">
                    <span>
                      Owner: <strong className="text-[#292E27]">{ownerVal}</strong>
                    </span>
                    <div className="flex items-center gap-3">
                      {lead.phone && (
                        <span className="flex items-center gap-1">
                          <Phone className="w-2.5 h-2.5" /> {lead.phone}
                        </span>
                      )}
                      {lead.email && (
                        <span className="flex items-center gap-1">
                          <Mail className="w-2.5 h-2.5" /> {lead.email}
                        </span>
                      )}
                    </div>
                  </div>
                  {lead.follow_up_date && (
                    <div className="text-[11px] text-[#885A14] font-medium pt-0.5">
                      Next Follow-up: {lead.follow_up_date}
                    </div>
                  )}
                </div>

                {/* Card Action Buttons */}
                <div className="flex items-center justify-between pt-2 border-t border-[#F4EFEA]">
                  <button
                    type="button"
                    onClick={() => handleEditClick(lead)}
                    className="inline-flex items-center gap-1 text-xs text-[#292E27] hover:text-[#C4A46D] font-medium transition-colors cursor-pointer"
                  >
                    <Edit2 className="w-3 h-3" />
                    <span>Edit enquiry</span>
                  </button>

                  {isConverted ? (
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/weddings/${lead.converted_wedding_id || "w1"}`)
                      }
                      className="inline-flex items-center gap-1 text-xs text-emerald-700 font-medium hover:underline cursor-pointer"
                    >
                      <CheckCircle className="w-3 h-3" />
                      <span>View wedding workspace</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setConvertingEnquiry(lead)}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-[#C4A46D] hover:bg-[#B3935C] text-[#292E27] font-semibold rounded transition-colors shadow-xs cursor-pointer"
                    >
                      <span>Convert to wedding</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Create / Edit Modal Form */}
      <Modal
        isOpen={isCreateOpen || editingEnquiry !== null}
        onClose={() => {
          setIsCreateOpen(false)
          setEditingEnquiry(null)
          reset()
        }}
        title={editingEnquiry ? "Edit Client Enquiry" : "Create New Client Enquiry"}
        subtitle="Record prospective couple preferences and wedding scope"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Couple Names *</label>
              <input
                {...register("couple_names")}
                placeholder="e.g. Singhania x Agrawal"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.couple_names && (
                <p className="text-rose-400 text-[11px]">{errors.couple_names.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Contact Phone *</label>
              <input
                {...register("phone")}
                placeholder="+91 98111 22334"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.phone && (
                <p className="text-rose-400 text-[11px]">{errors.phone.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Email Address</label>
              <input
                {...register("email")}
                placeholder="couple@example.com"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.email && (
                <p className="text-rose-400 text-[11px]">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Enquiry Source *</label>
              <select
                {...register("source")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Direct Call">Direct Call</option>
                <option value="Instagram">Instagram</option>
                <option value="Hotel GM Referral">Hotel GM Referral</option>
                <option value="Website Form">Website Form</option>
                <option value="Past Client Referral">Past Client Referral</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Target Wedding Date *</label>
              <input
                {...register("rough_date")}
                placeholder="e.g. 14 to 16 November 2026"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.rough_date && (
                <p className="text-rose-400 text-[11px]">{errors.rough_date.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Destination *</label>
              <select
                {...register("destination")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Jaipur">Jaipur</option>
                <option value="Udaipur">Udaipur</option>
                <option value="Jodhpur">Jodhpur</option>
                <option value="Jaisalmer">Jaisalmer</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Guest Count *</label>
              <input
                type="number"
                {...register("guest_count")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.guest_count && (
                <p className="text-rose-400 text-[11px]">{errors.guest_count.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Budget Cap (INR) *</label>
              <input
                type="number"
                {...register("budget_max")}
                step="500000"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.budget_max && (
                <p className="text-rose-400 text-[11px]">{errors.budget_max.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Theme Preference *</label>
              <input
                {...register("theme")}
                placeholder="Royal Heritage Palace / Desert Oasis"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.theme && (
                <p className="text-rose-400 text-[11px]">{errors.theme.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Package Type *</label>
              <select
                {...register("package_type")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="full_service">Full Service Planning</option>
                <option value="day_of">Day-of Coordination</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Assigned Lead Planner *</label>
              <select
                {...register("assigned_owner")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Aarav Mehta">Aarav Mehta</option>
                <option value="Nisha Sharma">Nisha Sharma</option>
                <option value="Rohan Roy">Rohan Roy</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Pipeline Status *</label>
              <select
                {...register("status")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="new">New Lead</option>
                <option value="meeting_booked">Meeting Booked</option>
                <option value="proposal_sent">Proposal Sent</option>
                <option value="lost">Lost</option>
              </select>
            </div>
          </div>

          <div className="space-y-1 text-xs">
            <label className="text-slate-300 font-medium">Follow-up Date</label>
            <input
              type="date"
              {...register("follow_up_date")}
              className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="space-y-1 text-xs">
            <label className="text-slate-300 font-medium">Notes & Consultation Brief</label>
            <textarea
              {...register("notes")}
              rows={3}
              placeholder="Key requirements, preferred venues, family background..."
              className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
            <button
              type="button"
              onClick={() => {
                setIsCreateOpen(false)
                setEditingEnquiry(null)
                reset()
              }}
              className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded text-xs font-semibold bg-[#C4A46D] hover:bg-[#B3935C] text-[#131926] transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isSubmitting ? "Saving..." : editingEnquiry ? "Update Enquiry" : "Create Enquiry"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog for Conversion */}
      <Modal
        isOpen={convertingEnquiry !== null}
        onClose={() => setConvertingEnquiry(null)}
        title="Confirm Wedding Booking Conversion"
        subtitle="This action initiates an active wedding project with automated task templates"
        maxWidth="max-w-md"
      >
        {convertingEnquiry && (
          <div className="space-y-4 text-xs text-slate-300">
            <div className="p-3 bg-[#1A2234] rounded-lg border border-[#2A364F] space-y-1.5">
              <div className="text-sm font-semibold text-white">
                {convertingEnquiry.couple_names || convertingEnquiry.couple}
              </div>
              <div>Destination: {convertingEnquiry.destination}</div>
              <div>
                Package:{" "}
                {convertingEnquiry.package_type === "day_of"
                  ? "Day-of Coordination"
                  : "Full Service Planning"}
              </div>
              <div>
                Budget:{" "}
                {formatINR(convertingEnquiry.budget_max || convertingEnquiry.budget || 0, true)}
              </div>
            </div>

            <div className="space-y-1 text-slate-300 leading-relaxed">
              <p>When confirmed, the system will atomically:</p>
              <ul className="list-disc list-inside space-y-1 text-slate-400 pl-1">
                <li>Create an active wedding record in the portfolio</li>
                <li>Generate 25+ package-based workflow tasks with deadlines</li>
                <li>Link the source enquiry and update status to Converted</li>
              </ul>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
              <button
                type="button"
                onClick={() => setConvertingEnquiry(null)}
                className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConvertConfirm}
                disabled={isSubmitting}
                className="px-4 py-2 rounded text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? "Converting..." : "Confirm & Launch Workspace"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
