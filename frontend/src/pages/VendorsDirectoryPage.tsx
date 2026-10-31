import React, { useEffect, useState, useCallback } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { Modal } from "@/components/ui/Modal"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import {
  Users,
  Phone,
  Mail,
  MapPin,
  Plus,
  Search,
  Filter,
  Edit2,
  CalendarCheck,
  CheckCircle2,
  XCircle,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

const vendorSchema = z.object({
  name: z.string().min(2, "Vendor name must be at least 2 characters"),
  category: z.string().min(1, "Please select a category"),
  contact_person: z.string().optional(),
  phone: z.string().min(8, "Phone number required"),
  email: z.string().email("Valid email required").or(z.literal("")),
  city: z.string().min(1, "City required"),
  address: z.string().optional(),
  status: z.string().default("active"),
  notes: z.string().optional(),
})

type VendorFormData = z.infer<typeof vendorSchema>

interface VendorItem {
  id: string
  name: string
  category: string
  contact_person?: string
  contact?: string
  phone: string
  email?: string
  city: string
  address?: string
  status: string
  notes?: string
  rating?: string
  quotes_count?: number
  associated_weddings?: string[]
}

interface WeddingSummary {
  id: string
  couple_names: string
  dates: string
  destination: string
}

export const VendorsDirectoryPage: React.FC = () => {
  const { toasts, addToast, removeToast } = useToast()

  const [categoryFilter, setCategoryFilter] = useState("all")
  const [cityFilter, setCityFilter] = useState("all")
  const [search, setSearch] = useState("")
  const [vendors, setVendors] = useState<VendorItem[]>([])
  const [weddings, setWeddings] = useState<WeddingSummary[]>([])
  const [loading, setLoading] = useState(true)

  // Modals state
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [editingVendor, setEditingVendor] = useState<VendorItem | null>(null)
  const [assigningVendor, setAssigningVendor] = useState<VendorItem | null>(null)
  const [selectedWeddingId, setSelectedWeddingId] = useState("")
  const [assignmentCategory, setAssignmentCategory] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<VendorFormData>({
    resolver: zodResolver(vendorSchema) as any,

    defaultValues: {
      name: "",
      category: "Catering",
      contact_person: "",
      phone: "",
      email: "",
      city: "Jaipur",
      address: "",
      status: "active",
      notes: "",
    },
  })

  const fetchVendors = useCallback(() => {
    setLoading(true)
    fetchWithAuth("/api/v1/vendors")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        setVendors(data || [])
      })
      .catch(() => {
        addToast("Failed to load vendor directory", "error")
      })
      .finally(() => setLoading(false))
  }, [addToast])

  useEffect(() => {
    fetchVendors()
    // Fetch weddings list for assignment modal
    fetchWithAuth("/api/v1/weddings")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        setWeddings(data || [])
        if (data && data.length > 0) setSelectedWeddingId(data[0].id)
      })
      .catch(() => {})
  }, [fetchVendors])

  const handleEditClick = (v: VendorItem) => {
    setEditingVendor(v)
    setValue("name", v.name)
    setValue("category", v.category)
    setValue("contact_person", v.contact_person || v.contact || "")
    setValue("phone", v.phone)
    setValue("email", v.email || "")
    setValue("city", v.city)
    setValue("address", v.address || "")
    setValue("status", v.status.toLowerCase() === "active" ? "active" : "inactive")
    setValue("notes", v.notes || "")
  }

  const handleToggleStatus = async (v: VendorItem) => {
    const nextStatus = v.status.toLowerCase() === "active" ? "inactive" : "active"
    try {
      const res = await fetchWithAuth(`/api/v1/vendors/${v.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      })
      if (!res.ok) throw new Error("Failed to update status")
      addToast(`Vendor '${v.name}' marked as ${nextStatus}`, "success")
      fetchVendors()
    } catch {
      addToast("Failed to update vendor status", "error")
    }
  }

  const onSubmit = async (data: VendorFormData) => {
    setIsSubmitting(true)
    try {
      if (editingVendor) {
        const res = await fetchWithAuth(`/api/v1/vendors/${editingVendor.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to update vendor")
        addToast("Vendor details updated successfully", "success")
        setEditingVendor(null)
      } else {
        const res = await fetchWithAuth("/api/v1/vendors", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to register vendor")
        addToast("Vendor registered in agency directory", "success")
        setIsAddOpen(false)
      }
      reset()
      fetchVendors()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error saving vendor"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handle Assign Vendor to Wedding
  const handleAssignSubmit = async () => {
    if (!assigningVendor || !selectedWeddingId) return
    setIsSubmitting(true)
    try {
      const res = await fetchWithAuth(`/api/v1/weddings/${selectedWeddingId}/vendors`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vendor_id: assigningVendor.id,
          category: assignmentCategory || assigningVendor.category,
        }),
      })
      const result = await res.json()
      if (!res.ok) throw new Error(result.detail || "Assignment failed")

      addToast(result.message || "Vendor assigned to wedding successfully", "success")
      setAssigningVendor(null)
      fetchVendors()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error assigning vendor"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  const categories = [
    "all",
    "Catering",
    "Decoration",
    "Photography",
    "DJ and entertainment",
    "Makeup",
    "Transportation",
    "Venue",
    "Lighting",
    "Other",
  ]

  const filtered = vendors.filter((v) => {
    const matchCat =
      categoryFilter === "all" ||
      v.category.toLowerCase().includes(categoryFilter.toLowerCase())
    const matchCity =
      cityFilter === "all" || v.city.toLowerCase() === cityFilter.toLowerCase()
    const matchSearch =
      v.name.toLowerCase().includes(search.toLowerCase()) ||
      v.category.toLowerCase().includes(search.toLowerCase()) ||
      v.city.toLowerCase().includes(search.toLowerCase())

    return matchCat && matchCity && matchSearch
  })

  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-6">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
        <div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight">
            Vendor Directory
          </h2>
          <p className="text-xs text-[#878074] mt-0.5">
            Verified luxury event partners, category profiles, and wedding assignments
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            reset()
            setIsAddOpen(true)
          }}
          className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 self-start sm:self-auto shadow-xs cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          <span>Add vendor</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 bg-white p-3 border border-[#E2DBD0] rounded-lg">
        <div className="relative w-full md:w-80">
          <Search
            className="w-3.5 h-3.5 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search vendor by name, category or city..."
            className="w-full text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-1.5 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D]"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-3.5 h-3.5 text-[#878074]" />
          <select
            value={cityFilter}
            onChange={(e) => setCityFilter(e.target.value)}
            className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2.5 py-1 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
          >
            <option value="all">All Cities</option>
            <option value="Jaipur">Jaipur</option>
            <option value="Udaipur">Udaipur</option>
            <option value="Jodhpur">Jodhpur</option>
          </select>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-1">
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setCategoryFilter(cat)}
            className={`px-3 py-1.5 text-xs rounded transition-colors shrink-0 cursor-pointer ${
              categoryFilter === cat
                ? "bg-[#292E27] text-[#FBFAF7] font-medium"
                : "bg-white border border-[#E2DBD0] text-[#69655D] hover:text-[#292E27]"
            }`}
          >
            {cat === "all" ? "All Categories" : cat}
          </button>
        ))}
      </div>

      {/* Vendors Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-56 bg-white border border-[#E2DBD0] rounded-lg p-5 space-y-3">
              <div className="h-4 bg-slate-200 rounded w-1/2" />
              <div className="h-3 bg-slate-100 rounded w-1/3" />
              <div className="h-20 bg-slate-50 rounded" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-lg space-y-2">
          <p className="text-sm font-medium text-[#292E27]">No vendors found</p>
          <p className="text-xs text-[#878074]">
            Try clearing your search query or selecting a different category.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((v) => {
            const isActive = v.status.toLowerCase() === "active"
            const contactPerson = v.contact_person || v.contact || "Partner Representative"
            const weddingsList = v.associated_weddings || []

            return (
              <div
                key={v.id}
                className="bg-white border border-[#E2DBD0] hover:border-[#C4A46D] rounded-lg p-5 shadow-xs transition-all space-y-3.5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-editorial text-lg text-[#292E27]">{v.name}</h3>
                      <span className="inline-block mt-0.5 text-xs text-[#885A14] font-medium">
                        {v.category}
                      </span>
                    </div>
                    <StatusBadge status={isActive ? "active" : "inactive"} />
                  </div>

                  <div className="space-y-1.5 text-xs text-[#524E48] mt-3">
                    <div className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{contactPerson}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{v.phone}</span>
                    </div>
                    {v.email && (
                      <div className="flex items-center gap-1.5">
                        <Mail className="w-3.5 h-3.5 text-[#C4A46D]" />
                        <span className="truncate">{v.email}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{v.city}</span>
                    </div>
                  </div>

                  {/* Associated Weddings */}
                  <div className="text-[11px] bg-[#FBFAF7] p-2.5 rounded border border-[#F4EFEA] text-[#69655D] mt-3">
                    <span className="font-medium text-[#292E27] block mb-1">
                      Assigned Weddings ({weddingsList.length}):
                    </span>
                    {weddingsList.length > 0 ? (
                      <ul className="space-y-0.5 list-disc list-inside text-[#524E48]">
                        {weddingsList.slice(0, 3).map((wTitle, idx) => (
                          <li key={idx} className="truncate">
                            {wTitle}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-[#878074] italic">Not yet assigned to any wedding</span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-2.5 border-t border-[#F4EFEA]">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleEditClick(v)}
                      className="p-1 rounded text-[#878074] hover:text-[#292E27] hover:bg-[#E9E3D8] transition-colors cursor-pointer"
                      title="Edit vendor"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleToggleStatus(v)}
                      className={`text-[11px] font-medium transition-colors cursor-pointer flex items-center gap-1 ${
                        isActive
                          ? "text-slate-500 hover:text-rose-600"
                          : "text-emerald-700 hover:text-emerald-800"
                      }`}
                      title={isActive ? "Mark Inactive" : "Mark Active"}
                    >
                      {isActive ? (
                        <>
                          <XCircle className="w-3 h-3" />
                          <span>Deactivate</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Activate</span>
                        </>
                      )}
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setAssigningVendor(v)
                      setAssignmentCategory(v.category)
                    }}
                    className="text-xs px-2.5 py-1 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] rounded transition-colors inline-flex items-center gap-1 cursor-pointer"
                  >
                    <CalendarCheck className="w-3 h-3 text-[#C4A46D]" />
                    <span>Assign</span>
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Add / Edit Vendor Modal */}
      <Modal
        isOpen={isAddOpen || editingVendor !== null}
        onClose={() => {
          setIsAddOpen(false)
          setEditingVendor(null)
          reset()
        }}
        title={editingVendor ? "Edit Vendor Details" : "Register New Vendor Partner"}
        subtitle="Maintain vendor contact info, category and operational status"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="space-y-1 sm:col-span-2">
              <label className="text-slate-300 font-medium">Business / Brand Name *</label>
              <input
                {...register("name")}
                placeholder="e.g. Royal Shahi Caterers"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.name && (
                <p className="text-rose-400 text-[11px]">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Category *</label>
              <select
                {...register("category")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Catering">Catering</option>
                <option value="Decoration">Decoration</option>
                <option value="Photography">Photography</option>
                <option value="DJ and entertainment">DJ and entertainment</option>
                <option value="Makeup">Makeup</option>
                <option value="Transportation">Transportation</option>
                <option value="Venue">Venue</option>
                <option value="Lighting">Lighting</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">City *</label>
              <select
                {...register("city")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Jaipur">Jaipur</option>
                <option value="Udaipur">Udaipur</option>
                <option value="Jodhpur">Jodhpur</option>
                <option value="Jaisalmer">Jaisalmer</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Contact Person</label>
              <input
                {...register("contact_person")}
                placeholder="Primary point of contact"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Contact Phone *</label>
              <input
                {...register("phone")}
                placeholder="+91 98290 12345"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.phone && (
                <p className="text-rose-400 text-[11px]">{errors.phone.message}</p>
              )}
            </div>

            <div className="space-y-1 sm:col-span-2">
              <label className="text-slate-300 font-medium">Email Address</label>
              <input
                {...register("email")}
                placeholder="vendor@business.com"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.email && (
                <p className="text-rose-400 text-[11px]">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1 sm:col-span-2">
              <label className="text-slate-300 font-medium">Status *</label>
              <select
                {...register("status")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div className="space-y-1 text-xs">
            <label className="text-slate-300 font-medium">Notes & Capabilities</label>
            <textarea
              {...register("notes")}
              rows={2}
              placeholder="Specialties, equipment, past palace experience..."
              className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
            <button
              type="button"
              onClick={() => {
                setIsAddOpen(false)
                setEditingVendor(null)
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
              {isSubmitting ? "Saving..." : editingVendor ? "Update Vendor" : "Register Vendor"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Assign Vendor to Wedding Modal */}
      <Modal
        isOpen={assigningVendor !== null}
        onClose={() => setAssigningVendor(null)}
        title="Assign Vendor to Wedding"
        subtitle={`Select wedding project to assign ${assigningVendor?.name}`}
        maxWidth="max-w-md"
      >
        {assigningVendor && (
          <div className="space-y-4 text-xs">
            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Target Wedding *</label>
              <select
                value={selectedWeddingId}
                onChange={(e) => setSelectedWeddingId(e.target.value)}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                {weddings.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.couple_names} ({w.destination} · {w.dates})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Assignment Role / Category</label>
              <input
                type="text"
                value={assignmentCategory}
                onChange={(e) => setAssignmentCategory(e.target.value)}
                placeholder={assigningVendor.category}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
              <button
                type="button"
                onClick={() => setAssigningVendor(null)}
                className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleAssignSubmit}
                disabled={isSubmitting}
                className="px-4 py-2 rounded text-xs font-semibold bg-[#C4A46D] hover:bg-[#B3935C] text-[#131926] transition-colors disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? "Assigning..." : "Confirm Assignment"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
