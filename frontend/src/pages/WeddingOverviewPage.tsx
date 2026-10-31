import React, { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { formatINR } from "@/lib/formatters"
import { ArrowRight } from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

interface WeddingDetail {
  id: string
  couple_names: string
  title?: string
  client_name?: string
  client_email?: string
  client_phone?: string
  destination: string
  dates: string
  venue?: string
  package_type: string
  guest_count: number
  client_budget: number
  health_status: string
  assigned_planner: string
  plan_progress_percent: number
  tasks_completed_count: number
  tasks_total_count: number
  vendors_confirmed_count: number
  vendors_target_count: number
  client_collections_amount: number
  open_decisions_count: number
  latest_update: string
}

interface WeddingTask {
  id: string
  title: string
  stage: string
  status: string
  priority: string
  owner_name: string
  due_date?: string
}

interface AssignedVendor {
  assignment_id: string
  vendor_id: string
  name: string
  category: string
  city: string
  status: string
}

export const WeddingOverviewPage: React.FC = () => {
  const { id = "w1" } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [detail, setDetail] = useState<WeddingDetail | null>(null)
  const [tasks, setTasks] = useState<WeddingTask[]>([])
  const [assignedVendors, setAssignedVendors] = useState<AssignedVendor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetchWithAuth(`/api/v1/weddings/${id}`).then((res) => (res.ok ? res.json() : null)),
      fetchWithAuth(`/api/v1/weddings/${id}/tasks`).then((res) => (res.ok ? res.json() : [])),
      fetchWithAuth(`/api/v1/weddings/${id}/vendors`).then((res) => (res.ok ? res.json() : [])),
    ])
      .then(([weddingData, tasksData, vendorsData]) => {
        if (weddingData && !weddingData.error) {
          setDetail(weddingData)
        }
        if (tasksData && Array.isArray(tasksData)) {
          setTasks(tasksData)
        }
        if (vendorsData && Array.isArray(vendorsData)) {
          setAssignedVendors(vendorsData)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  const wedding: WeddingDetail = detail || {
    id: id,
    couple_names: "Mehra x Kapoor",
    destination: "Jaipur",
    dates: "14 to 16 November 2026",
    package_type: "Full service",
    guest_count: 420,
    client_budget: 18500000,
    health_status: "on_track",
    assigned_planner: "Nisha Sharma",
    plan_progress_percent: 62,
    tasks_completed_count: 18,
    tasks_total_count: 29,
    vendors_confirmed_count: 14,
    vendors_target_count: 18,
    client_collections_amount: 9200000,
    open_decisions_count: 3,
    latest_update: "Nisha · 10:42 AM",
  }

  // Calculate dynamic task metrics from actual database tasks
  const realTasksTotal = tasks.length > 0 ? tasks.length : wedding.tasks_total_count
  const realTasksCompleted =
    tasks.length > 0
      ? tasks.filter((t) => t.status === "done").length
      : wedding.tasks_completed_count
  const realProgressPct =
    realTasksTotal > 0 ? Math.round((realTasksCompleted / realTasksTotal) * 100) : 0
  const realVendorsCount =
    assignedVendors.length > 0
      ? assignedVendors.length
      : wedding.vendors_confirmed_count

  // Upcoming unfinished tasks for "Next Up"
  const upcomingTasks = tasks.filter((t) => t.status !== "done").slice(0, 3)

  return (
    <div className="flex flex-col min-h-full">
      {/* Persistent Workspace Header */}
      <WeddingWorkspaceHeader
        coupleName={wedding.couple_names}
        dates={wedding.dates}
        destination={wedding.destination}
        packageType={wedding.package_type}
        guestCount={wedding.guest_count}
        healthStatus={wedding.health_status}
      />

      {/* Main Workspace Body */}
      <div className="p-4 md:p-8 max-w-[1440px] w-full mx-auto space-y-6">
        {/* 4 Overview Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Client Budget */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <span className="text-xs text-[#878074]">Client budget</span>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {formatINR(wedding.client_budget, true)}
            </div>
            <p className="mt-1 text-[11px] text-[#69655D]">
              Venue: {wedding.venue || "The Oberoi Rajvilas"}
            </p>
          </div>

          {/* Guests */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <span className="text-xs text-[#878074]">Guests</span>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {wedding.guest_count}
            </div>
            <p className="mt-1 text-[11px] text-[#69655D]">
              Lead Planner: {wedding.assigned_planner}
            </p>
          </div>

          {/* Plan Progress */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <span className="text-xs text-[#878074]">Plan progress</span>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#292E27]">
              {realProgressPct}%
            </div>
            <div className="w-full bg-[#E9E3D8] h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-[#292E27] h-full rounded-full transition-all"
                style={{ width: `${realProgressPct}%` }}
              />
            </div>
          </div>

          {/* Open Decisions */}
          <div className="p-4 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
            <span className="text-xs text-[#878074]">Open decisions</span>
            <div className="mt-1 text-2xl font-editorial tabular-nums text-[#AE5142]">
              {String(wedding.open_decisions_count).padStart(2, "0")}
            </div>
            <p className="mt-1 text-[11px] text-[#852C1F]">Pending coordination items</p>
          </div>
        </div>

        {/* Two Columns: Next Up & At A Glance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Next Up (2 Cols) */}
          <div className="lg:col-span-2 bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs">
            <div className="flex items-center justify-between border-b border-[#E2DBD0] pb-3 mb-4">
              <div>
                <h3 className="font-editorial text-lg text-[#292E27] font-normal">Next up</h3>
                <p className="text-[11px] text-[#878074]">Operational priorities from active task plan</p>
              </div>
              <button
                type="button"
                onClick={() => navigate(`/weddings/${id}/plan`)}
                className="text-xs text-[#69655D] hover:text-[#292E27] font-medium flex items-center gap-1 transition-colors cursor-pointer"
              >
                <span>View full plan</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-14 bg-slate-100 rounded" />
                ))}
              </div>
            ) : upcomingTasks.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#878074] bg-[#FBFAF7] rounded border border-[#E2DBD0]">
                All scheduled tasks completed or up to date.
              </div>
            ) : (
              <div className="space-y-3">
                {upcomingTasks.map((t) => (
                  <div
                    key={t.id}
                    className="p-3.5 bg-[#FBFAF7] border border-[#E2DBD0] rounded-md flex items-center justify-between gap-4"
                  >
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-[#292E27]">{t.title}</p>
                      <p className="text-[11px] text-[#69655D]">
                        <span className="capitalize">{t.stage.replace("_", " ")}</span> ·{" "}
                        {t.owner_name} · Due {t.due_date || "Upcoming"}
                      </p>
                    </div>
                    <StatusBadge status={t.status} />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* At a Glance (1 Col) */}
          <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="border-b border-[#E2DBD0] pb-3 mb-4">
                <h3 className="font-editorial text-lg text-[#292E27] font-normal">At a glance</h3>
                <p className="text-[11px] text-[#878074]">Live project parameters</p>
              </div>

              <div className="space-y-3.5 text-xs">
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="text-[#69655D]">Vendors confirmed</span>
                  <span className="font-semibold text-[#292E27] tabular-nums">
                    {realVendorsCount} / {wedding.vendors_target_count}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="text-[#69655D]">Tasks complete</span>
                  <span className="font-semibold text-[#292E27] tabular-nums">
                    {realTasksCompleted} / {realTasksTotal}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="text-[#69655D]">Client collections</span>
                  <span className="font-semibold text-[#292E27] tabular-nums">
                    {formatINR(wedding.client_collections_amount, true)} /{" "}
                    {formatINR(wedding.client_budget, true)}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="text-[#69655D]">Assigned planner</span>
                  <span className="font-medium text-[#292E27]">{wedding.assigned_planner}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-[#F4EFEA] mt-4 space-y-2">
              <button
                type="button"
                onClick={() => navigate(`/weddings/${id}/plan`)}
                className="w-full py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded transition-colors text-center inline-flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <span>Open Task Plan</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#C4A46D]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
