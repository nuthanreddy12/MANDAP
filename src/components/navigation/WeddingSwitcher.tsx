import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check, Building2, Users, Sparkles } from 'lucide-react'
import { useWedding } from '@/context/WeddingContext'
import { Badge } from '@/components/ui/Badge'

export function WeddingSwitcher() {
  const { activeWeddingId, setActiveWeddingId, activeWedding, weddings } = useWedding()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 bg-ivory-warm hover:bg-warm-stone/50 border border-warm-stone rounded-xl transition-all text-left focus:outline-none focus:ring-1 focus:ring-bronze cursor-pointer group"
        aria-label="Switch active wedding workspace"
        title="Switch active wedding workspace"
      >
        <div className="w-7 h-7 rounded-lg bg-bronze/10 border border-bronze/20 flex items-center justify-center text-bronze shrink-0 group-hover:scale-105 transition-transform">
          <Building2 className="w-4 h-4" />
        </div>

        <div className="hidden sm:block leading-tight text-left">
          <div className="flex items-center gap-1.5">
            <span className="font-serif text-xs md:text-sm font-bold text-ink truncate max-w-[140px] md:max-w-[180px]">
              {activeWedding?.couple || 'Select Wedding'}
            </span>
            <span className="text-[10px] px-1.5 py-0.2 bg-white/80 border border-warm-stone rounded text-ink-muted uppercase tracking-wider">
              {activeWedding?.city || 'Jaipur'}
            </span>
          </div>
          <span className="text-[10px] text-ink-muted truncate block max-w-[170px]">
            {activeWedding?.venue || 'Heritage Palace Circuit'}
          </span>
        </div>

        <ChevronDown
          className={`w-3.5 h-3.5 text-ink-muted transition-transform duration-200 shrink-0 ${
            isOpen ? 'rotate-180 text-ink' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute left-0 mt-2 w-80 md:w-96 bg-white border border-warm-stone rounded-2xl shadow-xl z-50 overflow-hidden animate-in fade-in-50 duration-150">
          <div className="px-4 py-3 bg-[#FAF8F5] border-b border-warm-stone flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#541424] uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-bronze" />
              <span>Active Weddings Portfolio</span>
            </div>
            <span className="text-[11px] text-ink-muted font-medium">
              {weddings.length} Active Desks
            </span>
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-warm-stone/40">
            {weddings.map((w) => {
              const isActive = w.id === activeWeddingId

              return (
                <button
                  key={w.id}
                  type="button"
                  onClick={() => {
                    setActiveWeddingId(w.id)
                    setIsOpen(false)
                  }}
                  className={`w-full p-3.5 text-left flex items-start justify-between gap-3 transition-colors cursor-pointer ${
                    isActive
                      ? 'bg-amber-50/60 hover:bg-amber-50'
                      : 'hover:bg-warm-stone/20'
                  }`}
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-serif text-sm font-bold text-ink">
                        {w.couple}
                      </span>
                      {isActive && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
                          <Check className="w-3 h-3" />
                          Active
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-ink-muted flex items-center gap-1">
                      <span>{w.venue}</span>
                      <span>·</span>
                      <strong className="text-ink">{w.city}</strong>
                    </p>

                    <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-ink-muted">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3 text-bronze" />
                        {w.guestCount} Guests
                      </span>
                      <span>·</span>
                      <span className="font-medium text-ink">
                        {w.budgetSummary}
                      </span>
                    </div>
                  </div>

                  <div className="shrink-0 pt-0.5">
                    <Badge variant={w.status === 'In Production' ? 'success' : w.status === 'Contract Signed' ? 'bronze' : 'warning'}>
                      {w.status}
                    </Badge>
                  </div>
                </button>
              )
            })}
          </div>

          <div className="p-2.5 bg-[#FAF8F5] border-t border-warm-stone text-center">
            <span className="text-[11px] text-ink-muted">
              Switching weddings synchronizes quotes, tasks, run-of-show & finances.
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

