import { NavLink, Link } from 'react-router-dom'
import {
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

interface NavItem {
  name: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

const NAV_ITEMS: NavItem[] = [
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

export function Sidebar() {
  return (
    <aside
      className="hidden lg:flex w-64 flex-col border-r border-warm-stone bg-ivory-card min-h-screen text-ink shrink-0 select-none"
      aria-label="Main Navigation"
    >
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-warm-stone/70 flex items-center">
        <Link
          to={ROUTES.WEDDINGS}
          className="flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass rounded-md group"
          title="Mandap Wedding Operations Home"
        >
          <img
            src="/image_5.png"
            alt="MANDAP Royal Wedding Atelier Brand Mark"
            width={38}
            height={50}
            className="h-11 w-auto max-w-full object-contain rounded-xs shrink-0 drop-shadow-xs transition-transform duration-200 group-hover:scale-102"
          />
          <div>
            <h1 className="font-serif text-2xl font-bold tracking-wide text-ink leading-none">
              MANDAP
            </h1>
            <p className="text-[10px] uppercase tracking-widest text-bronze font-medium mt-1">
              Wedding Operations
            </p>
          </div>
        </Link>
      </div>

      {/* Active Studio Selector */}
      <div className="px-4 py-3 mx-4 my-3 bg-ivory-warm border border-warm-stone/80 rounded-md">
        <div className="flex items-center gap-2 text-xs text-ink-muted">
          <Building2 className="w-3.5 h-3.5 text-bronze shrink-0" aria-hidden="true" />
          <span className="font-medium text-ink truncate">The Royal Pavilion Atelier</span>
        </div>
        <span className="block text-[10px] text-ink-faint mt-0.5">Udaipur & Jaipur Desk</span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto" aria-label="Operations Menu">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center justify-between px-3.5 py-2.5 text-xs font-medium rounded-md transition-colors duration-150',
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

      {/* Footer System Status */}
      <div className="p-4 border-t border-warm-stone/70 text-xs text-ink-muted bg-ivory-warm/40">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium text-ink-muted">Season 2026</span>
          <span className="text-[11px] text-garden font-semibold">Active Production</span>
        </div>
        <p className="text-[10px] text-ink-faint mt-1">12 Royal Celebrations Underway</p>
      </div>
    </aside>
  )
}
