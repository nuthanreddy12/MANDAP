import { useEffect } from 'react'
import { NavLink, Link } from 'react-router-dom'
import {
  X,
  CalendarDays,
  Inbox,
  Handshake,
  Scale,
  ListTodo,
  Clock,
  Receipt,
  FileText,
  BarChart3,
  Building2,
} from 'lucide-react'
import { ROUTES } from '@/routes/routePaths'
import { cn } from '@/lib/utils'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
}

const NAV_ITEMS = [
  { name: 'Weddings', path: ROUTES.WEDDINGS, icon: CalendarDays },
  { name: 'Enquiries', path: ROUTES.ENQUIRIES, icon: Inbox, badge: '4 New' },
  { name: 'Vendors', path: ROUTES.VENDORS, icon: Handshake },
  { name: 'Quote Comparison', path: ROUTES.QUOTES, icon: Scale },
  { name: 'Task Planning', path: ROUTES.TASKS, icon: ListTodo },
  { name: 'Run of Show', path: ROUTES.RUN_OF_SHOW, icon: Clock },
  { name: 'Finance & Invoices', path: ROUTES.FINANCE, icon: Receipt },
  { name: 'Documents', path: ROUTES.DOCUMENTS, icon: FileText },
  { name: 'Agency Profitability', path: ROUTES.ANALYTICS, icon: BarChart3 },
]

export function MobileDrawer({ isOpen, onClose }: MobileDrawerProps) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 lg:hidden flex"
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation Menu"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-ink/40 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Container */}
      <div className="relative w-4/5 max-w-xs bg-ivory-card border-r border-warm-stone h-full flex flex-col z-10 shadow-2xl">
        {/* Header with Close */}
        <div className="h-16 px-4 border-b border-warm-stone/70 flex items-center justify-between">
          <Link
            to={ROUTES.WEDDINGS}
            onClick={onClose}
            className="flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass rounded-md"
            title="Mandap Wedding Operations Home"
          >
            <img
              src="/image_5.png"
              alt="MANDAP Brand Mark"
              width={35}
              height={46}
              className="h-10 w-auto object-contain rounded-xs shrink-0 drop-shadow-xs"
            />
            <div>
              <span className="font-serif text-xl font-bold text-ink leading-none block">
                MANDAP
              </span>
              <span className="block text-[10px] uppercase tracking-widest text-bronze font-medium mt-0.5">
                Wedding Operations
              </span>
            </div>
          </Link>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close navigation menu"
            className="min-w-[44px] min-h-[44px] flex items-center justify-center text-ink-muted hover:text-ink rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass"
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Studio Indicator */}
        <div className="px-4 py-2.5 mx-4 my-3 bg-ivory-warm border border-warm-stone rounded-md">
          <div className="flex items-center gap-2 text-xs text-ink-muted">
            <Building2 className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
            <span className="font-medium text-ink">The Royal Pavilion Atelier</span>
          </div>
          <span className="block text-[10px] text-ink-faint mt-0.5">Udaipur & Jaipur Desk</span>
        </div>

        {/* Links */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center justify-between px-3.5 min-h-[44px] text-xs font-medium rounded-md transition-colors',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass',
                    isActive
                      ? 'bg-warm-stone-light/90 text-ink font-semibold border-l-2 border-bronze shadow-2xs'
                      : 'text-ink-muted hover:text-ink hover:bg-warm-stone-light/50'
                  )
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-ink-muted shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] bg-terracotta-light text-terracotta font-semibold px-2 py-0.5 rounded-md border border-terracotta/20">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-warm-stone/70 text-xs text-ink-muted bg-ivory-warm/40">
          <p className="text-[11px] font-medium text-ink">Season 2026</p>
          <p className="text-[10px] text-ink-faint mt-0.5">
            Udaivilas & Rambagh Palace Circuits
          </p>
        </div>
      </div>
    </div>
  )
}
