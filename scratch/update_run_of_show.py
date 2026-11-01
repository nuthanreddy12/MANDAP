code = '''import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  Lock,
  RefreshCw,
  Zap,
  Clock,
  RotateCcw,
  ShieldAlert,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import {
  getTimeline,
  calculateScheduleRecovery,
  approveRecoverySchedule,
  type ApiTimelineEvent,
} from '@/services/api'

function parseTimeToMinutes(tStr: string): number {
  if (!tStr) return 0
  const clean = tStr.trim().toUpperCase()
  const isPM = clean.includes('PM')
  const isAM = clean.includes('AM')
  const stripped = clean.replace(/[AP]M/, '').trim()
  const parts = stripped.split(':')
  let hours = parseInt(parts[0], 10) || 0
  const minutes = parseInt(parts[1], 10) || 0
  if (isPM && hours < 12) hours += 12
  if (isAM && hours === 12) hours = 0
  return hours * 60 + minutes
}

export function RunOfShowPage() {
  const queryClient = useQueryClient()
  const [weddingId] = useState('w1')
  const [isDelayModalOpen, setIsDelayModalOpen] = useState(false)
  const [selectedEventId, setSelectedEventId] = useState('')
  const [delayMinutes, setDelayMinutes] = useState(30)
  const [delayReason, setDelayReason] = useState('VIP Baraat convoy delayed in traffic on heritage palace approach')
  const [recoveryResult, setRecoveryResult] = useState<any | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // 1. Fetch real timeline events for wedding w1
  const {
    data: events = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['timeline', weddingId],
    queryFn: () => getTimeline(weddingId),
  })

  // 2. Synchronize main production run-sheet with AI cascaded proposed schedule
  const syncedRunSheet = useMemo(() => {
    if (!recoveryResult || !recoveryResult.proposed_schedule) {
      return events.map((cue) => ({
        ...cue,
        activeStartTime: cue.start_time,
        activeEndTime: cue.end_time,
        delayOffsetMinutes: cue.delay_minutes || 0,
        isCascaded: false,
        isDelayed: (cue.delay_minutes || 0) > 0,
        originalStart: cue.start_time,
        originalEnd: cue.end_time,
        changeReason: undefined as string | undefined,
        hasConflict: false,
        conflictMessage: undefined as string | undefined,
      }))
    }

    const proposedMap = new Map<string, any>()
    for (const item of recoveryResult.proposed_schedule) {
      if (item.id) proposedMap.set(item.id, item)
      if (item.title) proposedMap.set(item.title.toLowerCase().trim(), item)
    }

    const conflictsList: string[] = recoveryResult.conflicts || []

    return events.map((cue, idx) => {
      const proposed = proposedMap.get(cue.id) || proposedMap.get(cue.title.toLowerCase().trim())

      const proposedStart = proposed?.proposed_start || proposed?.proposedWindow?.start || cue.start_time
      const proposedEnd = proposed?.proposed_end || proposed?.proposedWindow?.end || cue.end_time
      const offset = proposed?.delay_offset_minutes ?? (proposed?.is_affected ? (recoveryResult.delay_minutes || 0) : cue.delay_minutes || 0)
      const isAffected = Boolean(proposed?.is_affected || offset > 0)
      const isLocked = Boolean(cue.is_locked || proposed?.is_locked)
      const changeReason = proposed?.change_reason

      // Check conflict conditions
      let conflictMsg: string | undefined = conflictsList.find(
        (c) => c.toLowerCase().includes(cue.title.toLowerCase()) || (isLocked && c.toLowerCase().includes('locked'))
      )

      if (!conflictMsg && isLocked && idx > 0) {
        const prevCue = events[idx - 1]
        const prevProposed = proposedMap.get(prevCue.id) || proposedMap.get(prevCue.title.toLowerCase().trim())
        const prevProposedEnd = prevProposed?.proposed_end || prevCue.end_time
        const prevEndMin = parseTimeToMinutes(prevProposedEnd)
        const currentStartMin = parseTimeToMinutes(proposedStart)
        if (prevEndMin > currentStartMin) {
          const overlap = prevEndMin - currentStartMin
          conflictMsg = `Preceding ceremony '${prevCue.title}' extends to ${prevProposedEnd}, encroaching by ${overlap}m on locked '${cue.title}'.`
        }
      }

      const endMin = parseTimeToMinutes(proposedEnd)
      const curfewMin = parseTimeToMinutes('10:30 PM')
      if (!conflictMsg && !isLocked && endMin > curfewMin) {
        const breach = endMin - curfewMin
        conflictMsg = `Projected completion at ${proposedEnd} breaches 10:30 PM Sound Curfew and Palace Closure constraint by ${breach}m.`
      }

      return {
        ...cue,
        activeStartTime: proposedStart,
        activeEndTime: proposedEnd,
        delayOffsetMinutes: offset,
        isCascaded: isAffected,
        isDelayed: offset > 0,
        originalStart: proposed?.original_start || cue.start_time,
        originalEnd: proposed?.original_end || cue.end_time,
        changeReason,
        isLocked,
        hasConflict: Boolean(conflictMsg),
        conflictMessage: conflictMsg,
      }
    })
  }, [events, recoveryResult])

  const affectedCount = syncedRunSheet.filter((c) => c.isCascaded || c.isDelayed).length
  const conflictCount = syncedRunSheet.filter((c) => c.hasConflict).length

  // 3. Mutation for schedule recovery
  const recoveryMutation = useMutation({
    mutationFn: () =>
      calculateScheduleRecovery(weddingId, selectedEventId, delayMinutes, delayReason),
    onSuccess: (data) => {
      setRecoveryResult(data)
      setIsDelayModalOpen(false)
      setActionMessage('AI schedule recovery calculated. Active production run-sheet updated with cascaded timings.')
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to calculate schedule recovery')
    },
  })

  // 4. Mutation for approving recovery schedule
  const approveMutation = useMutation({
    mutationFn: (incidentId: string) => approveRecoverySchedule(weddingId, incidentId),
    onSuccess: () => {
      setActionMessage('Recovered schedule approved and committed to master database!')
      setRecoveryResult(null)
      queryClient.invalidateQueries({ queryKey: ['timeline', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to approve recovery schedule')
    },
  })

  const openDelayModalForEvent = (eventId: string) => {
    setSelectedEventId(eventId)
    setIsDelayModalOpen(true)
  }

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            AI Schedule Recovery & Live Operations
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Run of Show Master Schedule
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Real-time ceremonial timing gates, vendor arrival checkpoints, and intelligent AI delay cascade recovery for Mehra x Kapoor wedding.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>

          <Button
            variant="bronze"
            size="md"
            leftIcon={<AlertTriangle className="w-4 h-4" />}
            onClick={() => {
              if (events.length > 0 && !selectedEventId) {
                setSelectedEventId(events[0].id)
              }
              setIsDelayModalOpen(true)
            }}
          >
            Report Delay & Recalculate
          </Button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{actionMessage}</span>
          </div>
          <button
            onClick={() => setActionMessage(null)}
            className="text-emerald-700 hover:text-emerald-900 text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-red-700 hover:text-red-900 text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Critical Conflict Banner */}
      {(conflictCount > 0 || (recoveryResult?.conflicts && recoveryResult.conflicts.length > 0)) && (
        <div className="bg-red-50/95 border-2 border-red-400 rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex items-center gap-2.5 text-red-900 font-bold text-sm uppercase tracking-wide">
            <ShieldAlert className="w-5 h-5 text-red-600 shrink-0" />
            <span>Hard Stop & Curfew Conflict Warning</span>
          </div>
          <p className="text-xs text-red-950 font-medium leading-relaxed">
            The cascaded schedule breaches hard operational constraints. Preceding ceremonial activities overlap with locked curfew wrap-up timings:
          </p>
          <ul className="space-y-1 pl-5 list-disc text-xs text-red-900 font-semibold">
            {(recoveryResult?.conflicts || []).map((conf: string, i: number) => (
              <li key={i}>{conf}</li>
            ))}
            {(!recoveryResult?.conflicts || recoveryResult.conflicts.length === 0) && (
              <li>Preceding evening entertainment exceeds the 10:30 PM Rajasthan Sound Curfew and Palace Closure boundary.</li>
            )}
          </ul>
        </div>
      )}

      {/* AI Schedule Recovery Briefing & Cascade Panel */}
      {recoveryResult && (
        <div className="bg-[#FAF8F5] border-2 border-[#B8860B] rounded-2xl p-6 shadow-md space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#E8E2D9] pb-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#B8860B]/15 text-[#805B10] text-[11px] font-semibold uppercase tracking-wider mb-2">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Schedule Recovery Briefing</span>
              </div>
              <h3 className="font-serif text-2xl font-bold text-ink">
                Cascade Impact & Contingency Adjustment
              </h3>
              <p className="text-xs text-ink-muted">
                Reported {recoveryResult.delay_minutes} min delay on {recoveryResult.incident_event_title || 'ceremony'}. Live run-sheet updated below.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
                onClick={() => setRecoveryResult(null)}
              >
                Revert to Original
              </Button>
              {recoveryResult.incident_id && (
                <Button
                  variant="bronze"
                  size="md"
                  leftIcon={<CheckCircle2 className="w-4 h-4" />}
                  onClick={() => approveMutation.mutate(recoveryResult.incident_id)}
                  disabled={approveMutation.isPending}
                >
                  {approveMutation.isPending ? 'Publishing...' : 'Approve & Publish Recovered Schedule'}
                </Button>
              )}
            </div>
          </div>

          {/* AI Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3.5 bg-white border border-[#E8E2D9] rounded-xl text-center">
              <span className="text-[11px] uppercase tracking-wider text-ink-muted block">Feasibility</span>
              <span className={`font-serif text-xl font-bold ${recoveryResult.is_feasible ? 'text-emerald-700' : 'text-red-700'}`}>
                {recoveryResult.is_feasible ? 'Achievable' : 'Curfew Breach'}
              </span>
            </div>
            <div className="p-3.5 bg-white border border-[#E8E2D9] rounded-xl text-center">
              <span className="text-[11px] uppercase tracking-wider text-ink-muted block">Buffer Absorbed</span>
              <span className="font-serif text-xl font-bold text-ink">
                {recoveryResult.buffer_saved_minutes || 0} mins
              </span>
            </div>
            <div className="p-3.5 bg-white border border-[#E8E2D9] rounded-xl text-center">
              <span className="text-[11px] uppercase tracking-wider text-ink-muted block">Affected Ceremonies</span>
              <span className="font-serif text-xl font-bold text-amber-700">
                {recoveryResult.affected_events_count || affectedCount}
              </span>
            </div>
            <div className="p-3.5 bg-white border border-[#E8E2D9] rounded-xl text-center">
              <span className="text-[11px] uppercase tracking-wider text-ink-muted block">Unaffected Cues</span>
              <span className="font-serif text-xl font-bold text-emerald-700">
                {recoveryResult.unaffected_events_count || (events.length - affectedCount)}
              </span>
            </div>
          </div>

          {/* AI Planner Briefing Prose */}
          {recoveryResult.ai_briefing && (
            <div className="p-4 bg-white border border-warm-stone rounded-xl">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-[#541424] mb-1.5 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-bronze" />
                <span>Producer Operational Guidance</span>
              </h4>
              <p className="text-xs text-ink leading-relaxed whitespace-pre-line">
                {recoveryResult.ai_briefing}
              </p>
            </div>
          )}

          {/* Proposed Cascade Table */}
          {recoveryResult.proposed_schedule && recoveryResult.proposed_schedule.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-ink mb-2">
                Cascade Shift Table
              </h4>
              <div className="overflow-x-auto bg-white rounded-xl border border-warm-stone">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-warm-stone text-ink-muted uppercase tracking-wider">
                      <th className="py-2.5 px-4">Ceremony</th>
                      <th className="py-2.5 px-4">Original Window</th>
                      <th className="py-2.5 px-4">Proposed Window</th>
                      <th className="py-2.5 px-4">Offset</th>
                      <th className="py-2.5 px-4 text-right">Impact</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-warm-stone/50">
                    {recoveryResult.proposed_schedule.map((item: any, i: number) => (
                      <tr key={item.id || i} className={item.is_affected ? 'bg-amber-50/50' : ''}>
                        <td className="py-2.5 px-4 font-medium text-ink flex items-center gap-2">
                          {item.is_locked && <span title="Locked milestone"><Lock className="w-3 h-3 text-ink-muted" /></span>}
                          <span>{item.title}</span>
                        </td>
                        <td className="py-2.5 px-4 text-ink-muted">{item.original_start} to {item.original_end}</td>
                        <td className="py-2.5 px-4 font-semibold text-ink">{item.proposed_start} to {item.proposed_end}</td>
                        <td className="py-2.5 px-4">
                          {item.delay_offset_minutes > 0 ? (
                            <span className="text-amber-700 font-semibold">+{item.delay_offset_minutes}m</span>
                          ) : (
                            <span className="text-ink-muted">On Time</span>
                          )}
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <Badge variant={item.is_affected ? 'warning' : 'success'}>
                            {item.is_affected ? 'Cascaded' : 'Steady'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Live Timeline Run-Sheet */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-warm-stone/60">
          <div>
            <h2 className="font-serif text-xl font-bold text-ink">
              Production Run-Sheet ({events.length} Cues)
            </h2>
            <p className="text-xs text-ink-muted">
              Active ceremonial timings: {recoveryResult ? 'Live AI cascaded projection active' : 'Master baseline schedule'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {recoveryResult && (
              <>
                <Badge variant="warning" className="bg-amber-100 text-amber-900 border-amber-300 font-semibold">
                  <Clock className="w-3 h-3 mr-1" />
                  Cascaded Schedule Active ({affectedCount} Shifted)
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRecoveryResult(null)}
                >
                  Reset Baseline
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="space-y-3">
          {syncedRunSheet.map((cue) => {
            const isCardDelayed = cue.delayOffsetMinutes > 0
            const isCardConflict = cue.hasConflict
            const hasShiftedTime = cue.activeStartTime !== cue.originalStart || cue.activeEndTime !== cue.originalEnd

            return (
              <Card
                key={cue.id}
                variant="elevated"
                className={`transition-all ${
                  isCardConflict
                    ? 'border-2 border-red-400 bg-red-50/20 shadow-sm'
                    : isCardDelayed
                    ? 'border-l-4 border-l-amber-500 border-warm-stone/80 bg-amber-50/15'
                    : 'hover:border-bronze/50'
                }`}
              >
                <CardContent className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    {/* Time Window Badge Box */}
                    <div
                      className={`w-20 sm:w-24 text-center py-2 px-1 rounded-lg border shrink-0 ${
                        isCardConflict
                          ? 'bg-red-100/80 border-red-300 text-red-950 font-semibold'
                          : isCardDelayed
                          ? 'bg-amber-100/70 border-amber-300 text-amber-950 font-semibold'
                          : 'bg-ivory-warm border-warm-stone/80 text-ink'
                      }`}
                    >
                      <span className="block text-xs font-serif font-bold tracking-tight">
                        {cue.activeStartTime}
                      </span>
                      <span className="block text-[10px] text-ink-muted">
                        {cue.activeEndTime}
                      </span>
                      {hasShiftedTime && (
                        <span className="block text-[9px] text-ink-muted/80 line-through mt-0.5 border-t border-warm-stone/40 pt-0.5">
                          was {cue.originalStart}
                        </span>
                      )}
                    </div>

                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-serif text-lg font-bold text-ink">{cue.title}</h3>

                        {cue.isLocked && (
                          <span
                            title="Locked fixed muhurat / curfew constraint"
                            className="inline-flex items-center gap-1 text-[11px] font-semibold text-bronze bg-bronze/10 px-2 py-0.5 rounded-md border border-bronze/20"
                          >
                            <Lock className="w-3 h-3 text-bronze" /> Fixed Constraint
                          </span>
                        )}

                        {cue.delayOffsetMinutes > 0 && (
                          <Badge variant="warning" className="bg-amber-100 text-amber-900 border-amber-300 font-bold text-[11px]">
                            +{cue.delayOffsetMinutes}m delayed
                          </Badge>
                        )}

                        {isCardConflict && (
                          <Badge variant="danger" className="bg-red-100 text-red-800 border-red-300 font-bold text-[11px] flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            Curfew Conflict
                          </Badge>
                        )}
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-ink-muted">
                        <span>Locus: <strong className="text-ink">{cue.location || 'Heritage Courtyard'}</strong></span>
                        <span>Lead: <strong className="text-ink">{cue.owner_name}</strong></span>
                        {cue.vendor_name && (
                          <span>Vendor: <strong className="text-ink">{cue.vendor_name}</strong></span>
                        )}
                        <span>
                          Arrival: <strong className={cue.vendor_arrival_status === 'on_site' ? 'text-emerald-700' : cue.vendor_arrival_status === 'late' ? 'text-amber-700' : 'text-ink'}>
                            {cue.vendor_arrival_status}
                          </strong>
                        </span>
                      </div>

                      {/* Conflict Alert Box on Card */}
                      {cue.conflictMessage && (
                        <div className="p-2.5 rounded-lg bg-red-100/80 border border-red-300 text-red-900 text-xs font-semibold flex items-center gap-2 mt-2">
                          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
                          <span>{cue.conflictMessage}</span>
                        </div>
                      )}

                      {/* AI Cascade Explanation Note on Card */}
                      {!cue.conflictMessage && cue.changeReason && (
                        <p className="text-xs text-amber-900 font-medium mt-1 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                          <span>{cue.changeReason}</span>
                        </p>
                      )}

                      {cue.notes && (
                        <p className="text-xs text-ink-muted mt-1 italic">
                          Cue notes: {cue.notes}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 shrink-0 self-end md:self-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openDelayModalForEvent(cue.id)}
                      className="text-xs text-ink-muted hover:text-ink"
                    >
                      Report Delay
                    </Button>
                    <Badge variant={cue.status === 'completed' ? 'success' : cue.status === 'in_progress' ? 'bronze' : 'neutral'}>
                      {cue.status === 'in_progress' ? 'Live Cue' : cue.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Delay Reporting Modal */}
      <Modal
        isOpen={isDelayModalOpen}
        onClose={() => setIsDelayModalOpen(false)}
        title="Report Ceremony Delay & Trigger AI Recovery"
      >
        <div className="space-y-4 text-xs">
          <p className="text-ink-muted">
            Select the delayed ceremony, input delay duration, and Mandap's AI recovery engine will recalculate cascade buffers and downstream cues.
          </p>

          <div>
            <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
              Delayed Ceremony Event
            </label>
            <select
              value={selectedEventId}
              onChange={(e) => setSelectedEventId(e.target.value)}
              className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
            >
              {events.map((ev) => (
                <option key={ev.id} value={ev.id}>
                  {ev.start_time} - {ev.title} ({ev.owner_name})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
              Delay Duration (Minutes)
            </label>
            <input
              type="number"
              min={5}
              max={180}
              step={5}
              value={delayMinutes}
              onChange={(e) => setDelayMinutes(Number(e.target.value))}
              className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink font-semibold"
            />
          </div>

          <div>
            <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
              Operational Reason
            </label>
            <textarea
              rows={3}
              value={delayReason}
              onChange={(e) => setDelayReason(e.target.value)}
              className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsDelayModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="bronze"
              size="sm"
              leftIcon={<Sparkles className="w-3.5 h-3.5" />}
              onClick={() => recoveryMutation.mutate()}
              disabled={recoveryMutation.isPending}
            >
              {recoveryMutation.isPending ? 'Calculating...' : 'Execute AI Schedule Recovery'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
'''

assert "—" not in code, "Em dash detected in code"

with open("src/features/run-of-show/pages/RunOfShowPage.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated src/features/run-of-show/pages/RunOfShowPage.tsx successfully!")

module_code = '''// Alias export for canonical RunOfShowPage component
export { RunOfShowPage as default, RunOfShowPage as RunOfShowModule } from '@/features/run-of-show/pages/RunOfShowPage'
'''

assert "—" not in module_code, "Em dash detected in module_code"

with open("src/components/RunOfShowModule.tsx", "w", encoding="utf-8") as f:
    f.write(module_code)

print("Created src/components/RunOfShowModule.tsx successfully!")

