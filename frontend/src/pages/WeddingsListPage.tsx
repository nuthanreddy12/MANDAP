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
import { Calendar, MapPin, Users, Briefcase, Plus, Search, Filter } from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

const weddingSchema = z.object({
  couple_names: z.string().min(3, "Couple names must be at least 3 characters"),
  title: z.string().optional(),
  destination: z.string().min(1, "Destination required"),
  dates: z.string().min(3, "Date range is required"),
  venue: z.string().min(1, "Venue is required"),
  package_type: z.string().default("full_service"),
  guest_count: z.coerce.number().min(10, "Minimum 10 guests"),
  client_budget: z.coerce.number().min(100000, "Minimum budget Rs 1,00,000"),
  health_status: z.string().default("on_track"),
  assigned_planner: z.string().default("Aarav Mehta"),
})

type WeddingFormData = z.infer<typeof weddingSchema>

interface WeddingItem {
  id: string
  couple_names: string
  title?: string
  destination: string
  dates: string
  venue?: string
  package_type: string
  guest_count: number
  client_budget: number
  health_status: string
  assigned_planner?: string
  planner?: string
  tasks_completed: number
  tasks_total: number
}

export const WeddingsListPage: React.FC = () => {
  const navigate = useNavigate()
  const { toasts, addToast, removeToast } = useToast()

  const [filterCity, setFilterCity] = useState<string>("all")
  const [filterHealth, setFilterHealth] = useState<string>("all")
  const [search, setSearch] = useState<string>("")
  const [weddings, setWeddings] = useState<WeddingItem[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<WeddingFormData>({
    resolver: zodResolver(weddingSchema) as any,

    defaultValues: {
      couple_names: "",
      title: "",
      destination: "Jaipur",
      dates: "14 to 16 November 2026",
      venue: "The Oberoi Rajvilas",
      package_type: "full_service",
      guest_count: 400,
      client_budget: 18000000,
      health_status: "on_track",
      assigned_planner: "Aarav Mehta",
    },
  })

  const fetchWeddings = useCallback(() => {
    setLoading(true)
    fetchWithAuth("/api/v1/weddings")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        setWeddings(data || [])
      })
      .catch(() => {
        addToast("Failed to load weddings from database", "error")
      })
      .finally(() => setLoading(false))
  }, [addToast])

  useEffect(() => {
    fetchWeddings()
  }, [fetchWeddings])

  const onSubmit = async (data: WeddingFormData) => {
    setIsSubmitting(true)
    try {
      const res = await fetchWithAuth("/api/v1/weddings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      const result = await res.json()
      if (!res.ok) throw new Error(result.detail || "Failed to create wedding")

      addToast("Wedding project initiated with automated task checklist", "success")
      setIsCreateOpen(false)
      reset()
      fetchWeddings()

      if (result.id) {
        setTimeout(() => {
          navigate(`/weddings/${result.id}`)
        }, 600)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error creating wedding"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  const filtered = weddings.filter((w) => {
    const matchCity =
      filterCity === "all" || w.destination.toLowerCase() === filterCity.toLowerCase()
    const matchHealth =
      filterHealth === "all" || w.health_status.toLowerCase() === filterHealth.toLowerCase()
    const matchSearch =
      w.couple_names.toLowerCase().includes(search.toLowerCase()) ||
      w.destination.toLowerCase().includes(search.toLowerCase())
    return matchCity && matchHealth && matchSearch
  })

  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-6">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
        <div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight">
            Wedding Portfolio
          </h2>
          <p className="text-xs text-[#878074] mt-0.5">
            Active luxury weddings across Jaipur, Udaipur and Jodhpur
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
          <span>New wedding</span>
        </button>
      </div>

      {/* Filter and search bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white p-3 border border-[#E2DBD0] rounded-lg">
        <div className="relative w-full sm:w-72">
          <Search
            className="w-3.5 h-3.5 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by couple name or city..."
            className="w-full text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-1.5 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D]"
          />
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-[#878074]">
            <Filter className="w-3.5 h-3.5" />
            <span>Destination:</span>
          </div>
          {["all", "Jaipur", "Udaipur", "Jaisalmer"].map((city) => (
            <button
              key={city}
              type="button"
              onClick={() => setFilterCity(city)}
              className={`px-2.5 py-1 text-xs rounded transition-colors cursor-pointer ${
                filterCity === city
                  ? "bg-[#292E27] text-[#FBFAF7] font-medium"
                  : "bg-[#F4EFEA] text-[#69655D] hover:text-[#292E27]"
              }`}
            >
              {city === "all" ? "All" : city}
            </button>
          ))}

          <select
            value={filterHealth}
            onChange={(e) => setFilterHealth(e.target.value)}
            className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2.5 py-1 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
          >
            <option value="all">All Health</option>
            <option value="on_track">On Track</option>
            <option value="needs_review">Needs Review</option>
            <option value="open_issue">Open Issue</option>
          </select>
        </div>
      </div>

      {/* Weddings Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-56 bg-white border border-[#E2DBD0] rounded-lg p-5 space-y-3">
              <div className="h-4 bg-slate-200 rounded w-1/2" />
              <div className="h-3 bg-slate-100 rounded w-1/3" />
              <div className="h-20 bg-slate-50 rounded" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center bg-white border border-[#E2DBD0] rounded-lg space-y-2">
          <p className="text-sm font-medium text-[#292E27]">No weddings match active filters</p>
          <p className="text-xs text-[#878074]">Try clearing your search query or city selection.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((w) => {
            const planner = w.assigned_planner || w.planner || "Aarav Mehta"
            const pct = w.tasks_total > 0 ? Math.round((w.tasks_completed / w.tasks_total) * 100) : 0

            return (
              <div
                key={w.id}
                onClick={() => navigate(`/weddings/${w.id}`)}
                className="bg-white border border-[#E2DBD0] hover:border-[#C4A46D] rounded-lg p-5 shadow-xs transition-all cursor-pointer flex flex-col justify-between group"
                role="button"
                tabIndex={0}
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-editorial text-xl text-[#292E27] group-hover:text-[#885A14] transition-colors">
                      {w.couple_names}
                    </h3>
                    <StatusBadge status={w.health_status} />
                  </div>

                  <div className="space-y-1.5 mt-3 text-xs text-[#524E48]">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{w.dates}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{w.destination}</span>
                      <span className="text-[#D9D1C3]">·</span>
                      <Briefcase className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{w.package_type === "day_of" ? "Day-of" : "Full Service"}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-[#C4A46D]" />
                      <span>{w.guest_count} guests</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-[#F4EFEA] mt-5">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="text-[#878074]">Client Budget</span>
                    <span className="font-semibold text-[#292E27] tabular-nums">
                      {formatINR(w.client_budget, true)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#878074]">Planner: <strong>{planner}</strong></span>
                    <span className="font-medium text-[#292E27] tabular-nums">
                      {w.tasks_completed} / {w.tasks_total} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-[#E9E3D8] h-1.5 rounded-full mt-2 overflow-hidden">
                    <div
                      className="bg-[#292E27] h-full rounded-full transition-all duration-300"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* New Wedding Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => {
          setIsCreateOpen(false)
          reset()
        }}
        title="Initiate New Wedding Project"
        subtitle="Registers project and initializes standard operational tasks"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="space-y-1 sm:col-span-2">
              <label className="text-slate-300 font-medium">Couple Names *</label>
              <input
                {...register("couple_names")}
                placeholder="e.g. Mehra x Kapoor"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.couple_names && (
                <p className="text-rose-400 text-[11px]">{errors.couple_names.message}</p>
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
              <label className="text-slate-300 font-medium">Wedding Dates *</label>
              <input
                {...register("dates")}
                placeholder="e.g. 14 to 16 November 2026"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.dates && (
                <p className="text-rose-400 text-[11px]">{errors.dates.message}</p>
              )}
            </div>

            <div className="space-y-1 sm:col-span-2">
              <label className="text-slate-300 font-medium">Primary Venue *</label>
              <input
                {...register("venue")}
                placeholder="e.g. The Oberoi Rajvilas / Taj Lake Palace"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
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
              <label className="text-slate-300 font-medium">Guest Count *</label>
              <input
                type="number"
                {...register("guest_count")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Client Budget (INR) *</label>
              <input
                type="number"
                {...register("client_budget")}
                step="500000"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium">Assigned Lead Planner *</label>
              <select
                {...register("assigned_planner")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="Aarav Mehta">Aarav Mehta</option>
                <option value="Nisha Sharma">Nisha Sharma</option>
                <option value="Kabir Verma">Kabir Verma</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
            <button
              type="button"
              onClick={() => {
                setIsCreateOpen(false)
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
              {isSubmitting ? "Creating..." : "Create Wedding"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
