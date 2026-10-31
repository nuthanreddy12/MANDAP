import { Link } from 'react-router-dom'
import { Menu, Search, Bell } from 'lucide-react'

export interface HeaderProps {
  onOpenMobileNav: () => void
}

export function Header({ onOpenMobileNav }: HeaderProps) {
  return (
    <header className="h-16 border-b border-warm-stone bg-ivory-card px-4 md:px-8 flex items-center justify-between sticky top-0 z-20 shadow-[0_1px_3px_rgba(44,37,35,0.02)]">
      {/* Mobile Hamburger & Studio Identity */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileNav}
          aria-label="Open navigation menu"
          className="lg:hidden p-2 text-ink rounded-md hover:bg-warm-stone-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <Menu className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Brand Lockup for Mobile when Sidebar is hidden */}
        <Link
          to="/weddings"
          className="flex lg:hidden items-center gap-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass rounded-md"
          title="Mandap Wedding Operations Home"
        >
          <img
            src="/image_5.png"
            alt="MANDAP Royal Wedding Atelier Brand Mark"
            width={34}
            height={44}
            className="h-9.5 w-auto object-contain rounded-xs shrink-0 drop-shadow-xs"
          />
          <div>
            <span className="font-serif text-lg font-bold text-ink leading-none block">
              MANDAP
            </span>
            <span className="block text-[9px] uppercase tracking-wider text-bronze font-medium mt-0.5">
              Wedding Operations
            </span>
          </div>
        </Link>

        <div className="hidden lg:block">
          <h2 className="font-serif text-lg md:text-xl font-semibold text-ink leading-tight">
            Jaipur & Udaipur Wedding Desk
          </h2>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Quick Search */}
        <div className="relative hidden md:block w-64">
          <label htmlFor="top-search" className="sr-only">
            Search weddings, vendors, quotes
          </label>
          <Search
            className="w-4 h-4 text-ink-muted absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"
            aria-hidden="true"
          />
          <input
            id="top-search"
            type="search"
            placeholder="Search weddings, venues..."
            className="w-full h-9 pl-9 pr-3 text-xs bg-ivory-warm border border-warm-stone rounded-md text-ink placeholder:text-ink-faint focus:border-bronze focus:outline-none focus:ring-1 focus:ring-bronze transition-colors"
          />
        </div>

        {/* Operational Notifications */}
        <button
          type="button"
          aria-label="View operational notifications (3 alerts)"
          className="relative min-w-[44px] min-h-[44px] flex items-center justify-center text-ink-muted hover:text-ink hover:bg-warm-stone-light/70 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass transition-colors"
        >
          <Bell className="w-4 h-4" aria-hidden="true" />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 rounded-full bg-terracotta" />
        </button>

        {/* Agency Lead Profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-warm-stone/80">
          <div
            className="w-8 h-8 rounded-md bg-warm-stone-light border border-bronze/30 text-ink font-serif font-bold text-xs flex items-center justify-center select-none shadow-2xs"
            aria-label="Planner profile: Gayatri Rathore"
          >
            GR
          </div>
          <div className="hidden xl:block text-left">
            <span className="block text-xs font-semibold text-ink leading-none">
              Gayatri Rathore
            </span>
            <span className="block text-[10px] text-ink-muted mt-0.5">
              Principal Producer
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
