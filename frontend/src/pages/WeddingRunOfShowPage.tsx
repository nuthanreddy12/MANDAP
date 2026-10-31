import React, { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { ApprovalBar } from "@/components/ui/ApprovalBar"
import { Modal } from "@/components/ui/Modal"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import { fetchWithAuth } from "@/lib/api"
import {
  Clock,
  AlertTriangle,
  Lock,
  CheckCircle2,
  Plus,
  RefreshCw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react"

interface TimelineEventItem {
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

interface ProposedEventItem {
  id: string
  title: string
  original_start: string
  original_end: string
  proposed_start: string
  proposed_end: string
  delay_offset_minutes: number
  is_affected: boolean
  is_locked: boolean
  status: string
  change_reason?: string
}

interface IncidentItem {
  id: string
  wedding_id: string
  timeline_event_id?: string
  vendor_name?: string
  title: string
  severity: string
  delay_minutes: number
  affected_activities?: string
  status: string // open, proposed_recovery, approved, rejected
  reported_by: string
  assigned_to: string
  proposed_schedule_adjustment?: {
    is_feasible: boolean
    delay_minutes: number
    incident_event_title?: string
    affected_events_count: number
    unaffected_events_count: number
    buffer_saved_minutes: number
    conflicts: string[]
    proposed_schedule: ProposedEventItem[]
    ai_briefing?: string
  }
  created_at?: string
}

export const WeddingRunOfShowPage: React.FC = () => {
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

  const [events, setEvents] = useState<TimelineEventItem[]>([])
  const [incidents, setIncidents] = useState<IncidentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [publishedMessage, setPublishedMessage] = useState<string | null>(null)

  // Report Modal
  const [isReportOpen, setIsReportOpen] = useState(false)
  const [selectedEventId, setSelectedEventId] = useState<string>("")
  const [vendorName, setVendorName] = useState<string>("DJ Ronak")
  const [delayMinutes, setDelayMinutes] = useState<number>(45)
  const [severity, setSeverity] = useState<string>("high")
  const [incidentTitle, setIncidentTitle] = useState<string>("DJ Console Highway Traffic Delay")
  const [incidentNotes, setIncidentNotes] = useState<string>(
    "Transport vehicle detained at Jaipur bypass toll. Expected on site by 6:45 PM."
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeciding, setIsDeciding] = useState(false)

  // Fetch wedding details
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

  // Fetch timeline events and incidents
  const fetchData = useCallback(() => {
    setLoading(true)
    Promise.all([
      fetchWithAuth(`/api/v1/weddings/${id}/timeline`).then((r) => (r.ok ? r.json() : [])),
      fetchWithAuth(`/api/v1/weddings/${id}/incidents`).then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([eventsData, incidentsData]) => {
        if (Array.isArray(eventsData)) setEvents(eventsData)
        if (Array.isArray(incidentsData)) setIncidents(incidentsData)
      })
      .catch(() => {
        addToast("Failed to load timeline and incident data", "error")
      })
      .finally(() => setLoading(false))
  }, [id, addToast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Locate active proposed recovery
  const activeIncident = incidents.find((i) => i.status === "proposed_recovery")
  const recoveryData = activeIncident?.proposed_schedule_adjustment
  const proposedScheduleMap = new Map<string, ProposedEventItem>()
  if (recoveryData?.proposed_schedule) {
    for (const pe of recoveryData.proposed_schedule) {
      proposedScheduleMap.set(pe.id, pe)
    }
  }

  // Seed / Reset Demonstration Scenario
  const handleResetDemo = async () => {
    try {
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/timeline/seed-demo`, {
        method: "POST",
      })
      if (!res.ok) throw new Error("Failed to reset schedule")
      addToast("Demo schedule reset to baseline (DJ 6:00 PM, Reception 7:00 PM, Curfew 10:30 PM)", "success")
      setPublishedMessage(null)
      fetchData()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error resetting schedule"
      addToast(msg, "error")
    }
  }

  // Submit Incident & Calculate Recovery
  const handleSubmitIncident = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      const targetId = selectedEventId || events[0]?.id
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/incidents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: incidentTitle,
          vendor_name: vendorName,
          timeline_event_id: targetId,
          severity,
          delay_minutes: Number(delayMinutes),
          notes: incidentNotes,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Failed to record incident")

      addToast("Operational incident recorded. Intelligent recovery schedule generated.", "success")
      setIsReportOpen(false)
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error submitting incident"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  // 1-Click Quick Demo Trigger
  const handleQuickDemoTrigger = async () => {
    setIsSubmitting(true)
    try {
      const djEvent = events.find((e) => e.vendor_name?.toLowerCase().includes("dj") || e.id === "te_dj_arrival")
      const targetId = djEvent?.id || events[0]?.id
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/incidents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "DJ Console 45m Traffic Delay",
          vendor_name: "DJ Ronak",
          timeline_event_id: targetId,
          severity: "high",
          delay_minutes: 45,
          notes: "DJ console detained in traffic. Sound setup pushed to 6:45 PM.",
        }),
      })
      if (!res.ok) throw new Error("Quick demo trigger failed")
      addToast("DJ 45-Minute Delay incident simulated. Review recovery plan below.", "success")
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error running demo trigger"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  // Approve Proposed Recovery Plan
  const handleApproveRecovery = async () => {
    if (!activeIncident) return
    setIsDeciding(true)
    try {
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/incidents/${activeIncident.id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notes: "Approved by Lead Planner Nisha Sharma. Stage and banquet captains notified.",
          decided_by: "Nisha Sharma",
        }),
      })
      if (!res.ok) throw new Error("Failed to approve recovery")
      const data = await res.json()
      addToast(data.message || "Schedule update approved and published.", "success")
      setPublishedMessage(
        `Schedule recovery v2.1 approved by Nisha Sharma. Updated times published to on-site coordinators.`
      )
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error approving recovery"
      addToast(msg, "error")
    } finally {
      setIsDeciding(false)
    }
  }

  // Reject Recovery Plan
  const handleRejectRecovery = async () => {
    if (!activeIncident) return
    setIsDeciding(true)
    try {
      const res = await fetchWithAuth(`/api/v1/weddings/${id}/incidents/${activeIncident.id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notes: "Coordination team opted to use acoustic house backup console instead.",
          decided_by: "Nisha Sharma",
        }),
      })
      if (!res.ok) throw new Error("Failed to reject recovery")
      addToast("Recovery proposal rejected. Baseline schedule remains in effect.", "info")
      fetchData()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error rejecting recovery"
      addToast(msg, "error")
    } finally {
      setIsDeciding(false)
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
        {/* Run of show header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-[#878074]">
              <span>Run of show</span>
              <span>/</span>
              <span className="text-[#292E27] font-medium">Wedding Day 2 · Live Operating Schedule</span>
            </div>
            <h3 className="font-editorial text-2xl text-[#292E27] font-normal mt-0.5">
              Intelligent Schedule & Run of Show
            </h3>
            <div className="flex items-center gap-2 mt-1 text-xs text-[#69655D]">
              <Clock className="w-3.5 h-3.5 text-[#C4A46D]" />
              <span className="font-medium text-[#292E27]">Current Time: 5:45 PM</span>
              <span>·</span>
              <span>Jaipur (Event-local)</span>
              <span>·</span>
              <span>Guest Count: {wedding.guest_count}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleResetDemo}
              className="px-3 py-1.5 border border-[#D9D1C3] bg-white hover:bg-[#F9F7F4] text-[#292E27] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5 cursor-pointer shadow-xs"
              title="Reset schedule to baseline demo events"
            >
              <RefreshCw className="w-3 h-3 text-[#878074]" />
              <span>Reset baseline</span>
            </button>

            <button
              type="button"
              onClick={handleQuickDemoTrigger}
              disabled={isSubmitting || !!activeIncident}
              className="px-3.5 py-1.5 bg-[#885A14] hover:bg-[#6D470E] text-white text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <Zap className="w-3.5 h-3.5 text-[#F4EFEA]" />
              <span>Simulate DJ 45m Delay</span>
            </button>

            <button
              type="button"
              onClick={() => setIsReportOpen(true)}
              className="px-3.5 py-1.5 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
              <span>Report incident</span>
            </button>
          </div>
        </div>

        {/* Schedule Recovery Approval Bar if incident open */}
        {activeIncident && recoveryData && (
          <ApprovalBar
            title={`Intelligent Recovery Plan: ${activeIncident.title}`}
            description={
              recoveryData.ai_briefing ||
              `${activeIncident.vendor_name || 'Vendor'} delayed by ${activeIncident.delay_minutes}m. Python schedule engine calculated revised timeline.`
            }
            impact={`${recoveryData.affected_events_count} activities shifted; ${recoveryData.buffer_saved_minutes}m buffer compressed; 10:30 PM closing curfew protected.`}
            approver="Nisha Sharma (Lead Operations Planner)"
            onApprove={handleApproveRecovery}
            onSendBack={handleRejectRecovery}
            isSubmitting={isDeciding}
          />
        )}

        {/* Conflict warnings banner if schedule conflict */}
        {activeIncident && recoveryData?.conflicts && recoveryData.conflicts.length > 0 && (
          <div className="p-4 bg-[#AE5142]/10 border border-[#AE5142]/40 rounded-lg text-xs text-[#852C1F] space-y-1">
            <div className="flex items-center gap-2 font-semibold">
              <AlertTriangle className="w-4 h-4 text-[#AE5142]" />
              <span>Constraint Warning: Manual Intervention Required</span>
            </div>
            {recoveryData.conflicts.map((c, i) => (
              <p key={i} className="pl-6">
                {c}
              </p>
            ))}
          </div>
        )}

        {/* Published Success Banner */}
        {publishedMessage && (
          <div className="p-3.5 bg-[#61765B]/15 border border-[#61765B]/40 rounded-lg text-xs text-[#374B32] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#61765B]" />
              <span className="font-medium">{publishedMessage}</span>
            </div>
            <span className="font-semibold text-xs text-[#292E27] bg-white px-2 py-0.5 rounded border border-[#61765B]/30">
              Published Live
            </span>
          </div>
        )}

        {/* Grid: Live Schedule & Vendor Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Live Minute-by-Minute Timeline (2 Cols) */}
          <div className="lg:col-span-2 bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4 border-b border-[#F4EFEA] pb-3">
              <div>
                <h4 className="font-editorial text-lg text-[#292E27] font-normal">
                  Minute-by-minute timeline
                </h4>
                <p className="text-[11px] text-[#878074]">
                  {activeIncident
                    ? "Side-by-side comparison: Baseline schedule vs Proposed AI recovery"
                    : "Live day-of-event sequence with constraint locking"}
                </p>
              </div>

              {activeIncident && (
                <div className="flex items-center gap-1.5 text-xs text-[#885A14] bg-[#C4A46D]/15 px-2.5 py-1 rounded border border-[#C4A46D]/30">
                  <Sparkles className="w-3.5 h-3.5 text-[#885A14]" />
                  <span className="font-medium">Active Proposal Review</span>
                </div>
              )}
            </div>

            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-20 bg-slate-100 rounded-lg" />
                ))}
              </div>
            ) : (
              <div className="space-y-3.5">
                {events.map((evt) => {
                  const proposed = proposedScheduleMap.get(evt.id)
                  const isAffected = proposed?.is_affected
                  const isLate = evt.vendor_arrival_status === "late" || (isAffected && proposed?.delay_offset_minutes > 0)

                  return (
                    <div
                      key={evt.id}
                      className={`p-4 border rounded-lg transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                        isAffected
                          ? "bg-[#C4A46D]/10 border-[#C4A46D] ring-1 ring-[#C4A46D]/30"
                          : isLate
                          ? "bg-[#AE5142]/5 border-[#AE5142]/40"
                          : "bg-white border-[#E2DBD0]"
                      }`}
                    >
                      <div className="flex items-start gap-3.5">
                        {/* Time slot column */}
                        <div className="w-24 shrink-0 pt-0.5">
                          {isAffected && proposed ? (
                            <div className="space-y-0.5">
                              <span className="text-[11px] text-[#878074] line-through block">
                                {evt.start_time}
                              </span>
                              <div className="flex items-center gap-1 text-xs font-bold text-[#885A14]">
                                <ArrowRight className="w-3 h-3" />
                                <span>{proposed.proposed_start}</span>
                              </div>
                            </div>
                          ) : (
                            <span className="tabular-nums font-semibold text-xs text-[#292E27]">
                              {evt.start_time}
                            </span>
                          )}
                        </div>

                        {/* Event details column */}
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-xs font-semibold text-[#292E27]">{evt.title}</p>
                            {evt.is_locked && (
                              <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#885A14] bg-[#C4A46D]/20 px-1.5 py-0.5 rounded border border-[#C4A46D]/40">
                                <Lock className="w-2.5 h-2.5" /> Curfew Locked
                              </span>
                            )}
                            {isAffected && (
                              <span className="text-[10px] font-bold bg-[#885A14] text-white px-1.5 py-0.2 rounded">
                                +{proposed?.delay_offset_minutes}m
                              </span>
                            )}
                          </div>

                          <p className="text-[11px] text-[#69655D] mt-0.5">
                            Owner: <strong className="text-[#292E27]">{evt.owner_name}</strong>
                            {evt.vendor_name && ` · Vendor: ${evt.vendor_name}`}
                            {evt.location && ` · ${evt.location}`}
                          </p>

                          {/* Reason for change note */}
                          {isAffected && proposed?.change_reason && (
                            <p className="text-[11px] text-[#885A14] mt-1 italic flex items-center gap-1">
                              <Sparkles className="w-3 h-3 shrink-0" />
                              <span>{proposed.change_reason}</span>
                            </p>
                          )}

                          {!isAffected && activeIncident && (
                            <p className="text-[10px] text-emerald-700 mt-0.5 flex items-center gap-1 font-medium">
                              <ShieldCheck className="w-3 h-3 text-emerald-600" />
                              <span>Unaffected by upstream delay; timing preserved.</span>
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="self-end sm:self-center shrink-0">
                        <StatusBadge
                          status={isAffected ? "late" : evt.status}
                          label={
                            isAffected
                              ? `Shifted +${proposed?.delay_offset_minutes}m`
                              : evt.is_locked
                              ? "Locked Curfew"
                              : evt.status === "rescheduled"
                              ? "Rescheduled"
                              : "Scheduled"
                          }
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Right Column: Active Incident & Operational Notes (1 Col) */}
          <div className="space-y-5">
            {/* Active Incident Card */}
            {activeIncident ? (
              <div className="bg-white border border-[#AE5142]/40 rounded-lg p-5 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#AE5142] flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Open Operational Incident</span>
                  </span>
                  <span className="text-[10px] uppercase font-bold text-[#AE5142] bg-[#AE5142]/10 px-1.5 py-0.5 rounded">
                    {activeIncident.severity}
                  </span>
                </div>

                <div>
                  <h5 className="text-xs font-semibold text-[#292E27]">{activeIncident.title}</h5>
                  <p className="text-[11px] text-[#524E48] mt-1">
                    Vendor: <strong className="text-[#292E27]">{activeIncident.vendor_name || 'N/A'}</strong>
                    <br />
                    Reported Delay: <strong>{activeIncident.delay_minutes} minutes</strong>
                    <br />
                    Reported by: {activeIncident.reported_by}
                  </p>
                </div>

                {recoveryData && (
                  <div className="p-2.5 bg-[#F4EFEA] rounded border border-[#E2DBD0] text-[11px] space-y-1">
                    <span className="font-semibold text-[#885A14] block">Recovery Engine Calculation</span>
                    <p className="text-[#524E48]">
                      Shifted <strong>{recoveryData.affected_events_count}</strong> events · Absorbed <strong>{recoveryData.buffer_saved_minutes}m</strong> buffer.
                    </p>
                    <p className="text-[#374B32] font-medium">
                      Status: {recoveryData.is_feasible ? "Feasible within 10:30 PM curfew" : "Breaches curfew"}
                    </p>
                  </div>
                )}

                <div className="pt-2 border-t border-[#F4EFEA] flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleApproveRecovery}
                    disabled={isDeciding}
                    className="w-full py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-medium rounded transition-colors text-center cursor-pointer shadow-xs disabled:opacity-50"
                  >
                    Approve Plan
                  </button>
                  <button
                    type="button"
                    onClick={handleRejectRecovery}
                    disabled={isDeciding}
                    className="w-full py-2 border border-[#E2DBD0] hover:bg-[#F4EFEA] text-[#292E27] text-xs font-medium rounded transition-colors text-center cursor-pointer disabled:opacity-50"
                  >
                    Reject Plan
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-800">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Operations Status: Stable</span>
                </div>
                <p className="text-xs text-[#524E48]">
                  All vendors on track. Venue sound checks, banquet stations and bridal entry proceed as scheduled.
                </p>
                <button
                  type="button"
                  onClick={() => setIsReportOpen(true)}
                  className="w-full mt-2 py-1.5 border border-[#292E27] hover:bg-[#292E27] hover:text-white text-[#292E27] text-xs font-medium rounded transition-colors cursor-pointer"
                >
                  Report Delay or Incident
                </button>
              </div>
            )}

            {/* Vendor Arrival Status Board */}
            <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs">
              <h4 className="font-editorial text-lg text-[#292E27] font-normal mb-3 border-b border-[#F4EFEA] pb-2">
                Key vendor on-site arrivals
              </h4>
              <div className="space-y-2.5 text-xs">
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="font-medium text-[#292E27]">DJ Ronak & Sound Crew</span>
                  <StatusBadge
                    status={activeIncident ? "late" : "due_soon"}
                    label={activeIncident ? "Late (45m)" : "Expected 6:00 PM"}
                  />
                </div>
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="font-medium text-[#292E27]">Royal Rajputana Catering (420 guests)</span>
                  <StatusBadge status="complete" label="Arrived & Prepping" />
                </div>
                <div className="flex items-center justify-between py-1 border-b border-[#F4EFEA]">
                  <span className="font-medium text-[#292E27]">Gulab House Floral & Decor</span>
                  <StatusBadge status="complete" label="Mandap Complete" />
                </div>
                <div className="flex items-center justify-between py-1">
                  <span className="font-medium text-[#292E27]">ParkRight Valet & Security</span>
                  <StatusBadge status="complete" label="Gates Manned" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Incident Modal */}
      <Modal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        title="Report On-Site Operational Incident"
        subtitle="Calculates downstream schedule recovery, respects fixed constraints, and briefs coordinators"
      >
        <form onSubmit={handleSubmitIncident} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-medium mb-1">Incident Headline</label>
            <input
              type="text"
              required
              value={incidentTitle}
              onChange={(e) => setIncidentTitle(e.target.value)}
              placeholder="e.g. DJ console delayed by 45 minutes"
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Target Activity</label>
              <select
                value={selectedEventId}
                onChange={(e) => setSelectedEventId(e.target.value)}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
              >
                {events.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.title} ({e.start_time})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Vendor Name</label>
              <input
                type="text"
                value={vendorName}
                onChange={(e) => setVendorName(e.target.value)}
                placeholder="e.g. DJ Ronak"
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Reported Delay (Minutes)</label>
              <input
                type="number"
                min="5"
                max="300"
                required
                value={delayMinutes}
                onChange={(e) => setDelayMinutes(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
              >
                <option value="low">Low (absorbed by stage buffers)</option>
                <option value="medium">Medium (minor timing shifts)</option>
                <option value="high">High (guest impact / sound curfew risk)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Operational Notes & Context</label>
            <textarea
              rows={3}
              value={incidentNotes}
              onChange={(e) => setIncidentNotes(e.target.value)}
              placeholder="Provide situational details for on-site coordinators..."
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100 focus:outline-none focus:border-[#C4A46D]"
            />
          </div>

          <div className="pt-3 border-t border-slate-700 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsReportOpen(false)}
              className="px-4 py-2 border border-slate-600 hover:bg-slate-800 text-slate-300 rounded font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-[#C4A46D] hover:bg-[#B3935B] text-slate-950 font-semibold rounded transition-colors inline-flex items-center gap-1.5 shadow-sm disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Calculating recovery...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Generate Recovery Plan</span>
                </>
              )}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
