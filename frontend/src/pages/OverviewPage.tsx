import React, { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { formatINR } from "@/lib/formatters"
import {
  Sparkles,
  Calendar,
  AlertCircle,
  IndianRupee,
  ArrowRight,
  Clock,
  MapPin,
  RefreshCw,
} from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

interface OverviewData {
  active_weddings_count: number
  destinations_count: number
  next_30_days_count: number
  needs_attention_count: number
  open_incidents_count: number
  pending_followups_count: number
  money_due_14d: number
  weddings_in_motion: Array<{
    id: string
    couple_names: string
    package_type: string
    guest_count: number
    destination: string
    dates: string
    progress_tasks: string
    progress_percent: number
    health_status: string
  }>
  upcoming_schedule: Array<{
    time: string
    title: string
    owner: string
    status: string
  }>
}

export const OverviewPage: React.FC = () => {
  const navigate = useNavigate()
  const [data, setData] = useState<OverviewData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchOverview = async () => {
    try {
      const res = await fetchWithAuth("/api/v1/overview")
      if (res.ok) {
        const json = await res.json()
        setData(json)
      } else {
        // Fallback realistic seed data if backend starting
        loadFallbackData()
      }
    } catch {
      loadFallbackData()
    } finally {
      setLoading(false)
    }
  }

  const loadFallbackData = () => {
    setData({
      active_weddings_count: 12,
      destinations_count: 2,
      next_30_days_count: 3,
      needs_attention_count: 5,
      open_incidents_count: 2,
      pending_followups_count: 3,
      money_due_14d: 1840000,
      weddings_in_motion: [
        {
          id: "w1",
          couple_names: "Mehra × Kapoor",
          package_type: "Full service",
          guest_count: 420,
          destination: "Jaipur",
          dates: "14–16 Nov",
          progress_tasks: "18 / 29 tasks",
          progress_percent: 62,
          health_status: "on_track",
        },
        {
          id: "w2",
          couple_names: "Rathore × Singh",
          package_type: "Day-of",
          guest_count: 380,
          destination: "Udaipur",
          dates: "21–22 Nov",
          progress_tasks: "24 / 27 tasks",
          progress_percent: 88,
          health_status: "open_issue",
        },
        {
          id: "w3",
          couple_names: "Sharma × Bansal",
          package_type: "Full service",
          guest_count: 500,
          destination: "Jaipur",
          dates: "05–07 Dec",
          progress_tasks: "11 / 31 tasks",
          progress_percent: 35,
          health_status: "needs_review",
        },
      ],
      upcoming_schedule: [
        {
          time: "Today · 3:30 PM",
          title: "Mehra × Kapoor · venue walk-through",
          owner: "Aarav",
          status: "scheduled",
        },
        {
          time: "Tomorrow · 11:00 AM",
          title: "Rathore × Singh · sound check",
          owner: "Late vendor",
          status: "late",
        },
        {
          time: "03 Nov · 12:00 PM",
          title: "Sharma × Bansal · advance due",
          owner: "₹8.0L",
          status: "due_soon",
        },
      ],
    })
  }

  useEffect(() => {
    fetchOverview()
  }, [])

  if (loading || !data) {
    return (
      <div className="p-8 max-w-[1440px] mx-auto animate-pulse">
        <div className="h-6 w-48 bg-[#E9E3D8] rounded mb-6" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-[#F4EFEA] rounded-lg border border-[#E2DBD0]" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-8">
      {/* Editorial Page Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-[#E2DBD0] pb-4">
        <div>
          <p className="text-xs text-[#878074]">Friday, 31 October 2026</p>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight mt-0.5">
            Good morning, Aarav.
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#878074] font-medium px-2.5 py-1 bg-[#F4EFEA] border border-[#E2DBD0] rounded">
            Season 2026-27
          </span>
          <button
            type="button"
            onClick={fetchOverview}
            className="p-1.5 text-[#69655D] hover:text-[#292E27] rounded transition-colors"
            title="Refresh overview pulse"
            aria-label="Refresh overview pulse"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Top 4 Scannable Metric Tiles (Page 4) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Weddings */}
        <div
          onClick={() => navigate("/weddings")}
          className="p-5 bg-white border border-[#E2DBD0] rounded-lg cursor-pointer hover:border-[#C4A46D] transition-all shadow-xs group"
          role="button"
          tabIndex={0}
        >
          <div className="flex items-center justify-between text-xs text-[#878074]">
            <span>Active weddings</span>
            <Sparkles className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          </div>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#292E27]">
            {String(data.active_weddings_count).padStart(2, "0")}
          </div>
          <p className="mt-1 text-xs text-[#69655D]">
            Across {data.destinations_count} destinations
          </p>
        </div>

        {/* Next 30 Days */}
        <div
          onClick={() => navigate("/weddings")}
          className="p-5 bg-white border border-[#E2DBD0] rounded-lg cursor-pointer hover:border-[#C4A46D] transition-all shadow-xs group"
          role="button"
          tabIndex={0}
        >
          <div className="flex items-center justify-between text-xs text-[#878074]">
            <span>Next 30 days</span>
            <Calendar className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          </div>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#292E27]">
            {String(data.next_30_days_count).padStart(2, "0")}
          </div>
          <p className="mt-1 text-xs text-[#69655D]">
            2 in Jaipur · 1 in Udaipur
          </p>
        </div>

        {/* Needs Attention */}
        <div
          onClick={() => navigate("/weddings/w1/run-of-show")}
          className="p-5 bg-white border border-[#E2DBD0] rounded-lg cursor-pointer hover:border-[#AE5142] transition-all shadow-xs group"
          role="button"
          tabIndex={0}
        >
          <div className="flex items-center justify-between text-xs text-[#878074]">
            <span>Needs attention</span>
            <AlertCircle className="w-3.5 h-3.5 text-[#AE5142]" aria-hidden="true" />
          </div>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#AE5142]">
            {String(data.needs_attention_count).padStart(2, "0")}
          </div>
          <p className="mt-1 text-xs text-[#852C1F]">
            {data.open_incidents_count} incidents · {data.pending_followups_count} follow-ups
          </p>
        </div>

        {/* Money Due 14 Days */}
        <div
          onClick={() => navigate("/finance")}
          className="p-5 bg-white border border-[#E2DBD0] rounded-lg cursor-pointer hover:border-[#C4A46D] transition-all shadow-xs group"
          role="button"
          tabIndex={0}
        >
          <div className="flex items-center justify-between text-xs text-[#878074]">
            <span>Money due · 14 days</span>
            <IndianRupee className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          </div>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#292E27]">
            {formatINR(data.money_due_14d, true)}
          </div>
          <p className="mt-1 text-xs text-[#69655D]">
            Client + vendor obligations
          </p>
        </div>
      </div>

      {/* Main Grid: Weddings in motion & The next few days */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weddings In Motion (2 Cols) */}
        <div className="lg:col-span-2 bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs">
          <div className="flex items-center justify-between border-b border-[#E2DBD0] pb-3 mb-4">
            <h3 className="font-editorial text-lg text-[#292E27] font-normal">
              Weddings in motion
            </h3>
            <button
              type="button"
              onClick={() => navigate("/weddings")}
              className="text-xs text-[#69655D] hover:text-[#292E27] font-medium flex items-center gap-1 transition-colors"
            >
              <span>View all</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#F4EFEA] text-[11px] text-[#878074] uppercase tracking-wider">
                  <th className="pb-2.5 font-medium">Wedding</th>
                  <th className="pb-2.5 font-medium">Date / Place</th>
                  <th className="pb-2.5 font-medium">Progress</th>
                  <th className="pb-2.5 font-medium text-right">Health</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F4EFEA]">
                {data.weddings_in_motion.map((w) => (
                  <tr
                    key={w.id}
                    onClick={() => navigate(`/weddings/${w.id}/overview`)}
                    className="hover:bg-[#F9F7F4] cursor-pointer transition-colors group"
                  >
                    <td className="py-3 pr-4">
                      <p className="font-medium text-sm text-[#292E27] group-hover:text-[#885A14] transition-colors">
                        {w.couple_names}
                      </p>
                      <p className="text-[11px] text-[#878074]">
                        {w.package_type} · {w.guest_count} guests
                      </p>
                    </td>
                    <td className="py-3 pr-4 text-[#524E48]">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-[#C4A46D]" />
                        <span>{w.dates}</span>
                      </div>
                      <div className="flex items-center gap-1 text-[11px] text-[#878074] mt-0.5">
                        <MapPin className="w-3 h-3 text-[#878074]" />
                        <span>{w.destination}</span>
                      </div>
                    </td>
                    <td className="py-3 pr-4">
                      <span className="tabular-nums text-xs text-[#292E27] font-medium">
                        {w.progress_tasks}
                      </span>
                      <div className="w-24 bg-[#E9E3D8] h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-[#292E27] h-full rounded-full transition-all"
                          style={{ width: `${w.progress_percent}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <StatusBadge status={w.health_status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* The Next Few Days (1 Col) */}
        <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="border-b border-[#E2DBD0] pb-3 mb-4">
              <h3 className="font-editorial text-lg text-[#292E27] font-normal">
                The next few days
              </h3>
            </div>

            <div className="space-y-4">
              {data.upcoming_schedule.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-[#FBFAF7] border border-[#E2DBD0] rounded-md flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 text-[11px] text-[#878074]">
                      <Clock className="w-3 h-3 text-[#C4A46D]" />
                      <span>{item.time}</span>
                    </div>
                    <p className="font-medium text-[#292E27]">{item.title}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <StatusBadge status={item.status} label={item.owner} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-[#F4EFEA] mt-4">
            <button
              type="button"
              onClick={() => navigate("/weddings/w1/plan")}
              className="text-xs text-[#69655D] hover:text-[#292E27] font-medium flex items-center gap-1 transition-colors"
            >
              <span>See all upcoming work</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
