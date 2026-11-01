import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Menu,
  Search,
  Bell,
  LogOut,
  ChevronDown,
  CheckCheck,
  Shield,
  X,
} from 'lucide-react'
import { useAuth } from '@/lib/useAuth'
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  globalSearch,
  type SearchResultItem,
} from '@/services/api'
import { WeddingSwitcher } from './WeddingSwitcher'

export interface HeaderProps {
  onOpenMobileNav: () => void
}

export function Header({ onOpenMobileNav }: HeaderProps) {
  const { appUser, signOut } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // State
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [isNotifsOpen, setIsNotifsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Refs for click outside
  const profileRef = useRef<HTMLDivElement>(null)
  const notifsRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLDivElement>(null)
  const searchDebounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Notifications query
  const { data: notifData } = useQuery({
    queryKey: ['notifications'],
    queryFn: getNotifications,
    refetchInterval: 30000,
  })

  const notifications = notifData?.notifications || []
  const unreadCount = notifData?.unread_count || 0

  const markReadMutation = useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const markAllReadMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  // Global search debouncing
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      const resetTimer = setTimeout(() => {
        setSearchResults([])
        setIsSearchDropdownOpen(false)
        setIsSearching(false)
      }, 0)
      return () => clearTimeout(resetTimer)
    }

    setIsSearching(true)
    if (searchDebounceTimer.current) {
      clearTimeout(searchDebounceTimer.current)
    }

    searchDebounceTimer.current = setTimeout(async () => {
      try {
        const resp = await globalSearch(searchQuery.trim())
        setSearchResults(resp.results || [])
        setIsSearchDropdownOpen(true)
      } catch (_err) {
        setSearchResults([])
      } finally {
        setIsSearching(false)
      }
    }, 300)

    return () => {
      if (searchDebounceTimer.current) clearTimeout(searchDebounceTimer.current)
    }
  }, [searchQuery])

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node
      if (profileRef.current && !profileRef.current.contains(target)) {
        setIsProfileOpen(false)
      }
      if (notifsRef.current && !notifsRef.current.contains(target)) {
        setIsNotifsOpen(false)
      }
      if (searchRef.current && !searchRef.current.contains(target)) {
        setIsSearchDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSignOut = async () => {
    try {
      await signOut()
      navigate('/login', { replace: true })
    } catch (_err) {
      navigate('/login', { replace: true })
    }
  }

  const handleSearchResultClick = (item: SearchResultItem) => {
    setIsSearchDropdownOpen(false)
    setSearchQuery('')
    if (item.link_url) {
      navigate(item.link_url)
    }
  }

  const handleNotificationClick = (notif: any) => {
    if (!notif.is_read) {
      markReadMutation.mutate(notif.id)
    }
    setIsNotifsOpen(false)
    if (notif.link_url) {
      navigate(notif.link_url)
    }
  }

  const roleLabelMap: Record<string, string> = {
    owner: 'Agency Principal',
    planner: 'Lead Planner',
    coordinator: 'Ceremony Coordinator',
    finance_manager: 'Finance Director',
    customer: 'Royal Client',
  }

  const currentRoleTitle = appUser?.role ? (roleLabelMap[appUser.role] || appUser.role) : 'Producer'
  const displayName = appUser?.name || 'Aarav Mehta'
  const displayInitials =
    appUser?.avatar_initials ||
    displayName
      .split(' ')
      .map((n: string) => n[0])
      .join('')
      .slice(0, 2)
      .toUpperCase()

  return (
    <header className="h-16 border-b border-warm-stone bg-ivory-card px-4 md:px-8 flex items-center justify-between sticky top-0 z-20 shadow-[0_1px_3px_rgba(44,37,35,0.02)]">
      {/* Mobile Hamburger & Studio Identity */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileNav}
          aria-label="Open navigation menu"
          className="lg:hidden p-2 text-ink rounded-md hover:bg-warm-stone-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass min-w-[44px] min-h-[44px] flex items-center justify-center cursor-pointer"
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

        <div className="hidden lg:flex items-center gap-3">
          <h2 className="font-serif text-lg md:text-xl font-semibold text-ink leading-tight">
            Jaipur & Udaipur Wedding Desk
          </h2>
          <span className="text-warm-stone/80 text-sm">|</span>
          <WeddingSwitcher />
        </div>
        <div className="block lg:hidden">
          <WeddingSwitcher />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Quick Global Search */}
        <div ref={searchRef} className="relative hidden md:block w-72">
          <label htmlFor="top-search" className="sr-only">
            Search weddings, vendors, quotes, tasks
          </label>
          <Search
            className="w-4 h-4 text-ink-muted absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"
            aria-hidden="true"
          />
          <input
            id="top-search"
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0) setIsSearchDropdownOpen(true)
            }}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setIsSearchDropdownOpen(false)
            }}
            placeholder="Search weddings, vendors, tasks..."
            className="w-full h-9 pl-9 pr-7 text-xs bg-ivory-warm border border-warm-stone rounded-md text-ink placeholder:text-ink-faint focus:border-bronze focus:outline-none focus:ring-1 focus:ring-bronze transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('')
                setIsSearchDropdownOpen(false)
              }}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-muted hover:text-ink p-0.5 cursor-pointer"
            >
              <X className="w-3 h-3" />
            </button>
          )}

          {/* Search Dropdown Results */}
          {isSearchDropdownOpen && (
            <div className="absolute left-0 right-0 top-10 mt-1 bg-white border border-warm-stone rounded-xl shadow-lg z-50 overflow-hidden max-h-96 overflow-y-auto">
              {isSearching ? (
                <div className="p-4 text-center text-xs text-ink-muted">Searching database...</div>
              ) : searchResults.length === 0 ? (
                <div className="p-4 text-center text-xs text-ink-muted">
                  No matching records found for "{searchQuery}".
                </div>
              ) : (
                <div className="divide-y divide-warm-stone/40">
                  {searchResults.map((item) => (
                    <button
                      key={`${item.category}-${item.id}`}
                      onClick={() => handleSearchResultClick(item)}
                      className="w-full p-3 text-left hover:bg-warm-stone-light/60 transition-colors flex items-start justify-between gap-3 cursor-pointer"
                    >
                      <div>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-bronze block">
                          {item.category}
                        </span>
                        <p className="text-xs font-serif font-bold text-ink mt-0.5">{item.title}</p>
                        <p className="text-[11px] text-ink-muted mt-0.5">{item.subtitle}</p>
                      </div>
                      {item.status && (
                        <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 bg-warm-stone-light rounded-sm font-medium text-ink-muted shrink-0">
                          {item.status}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Operational Notifications Dropdown */}
        <div ref={notifsRef} className="relative">
          <button
            type="button"
            onClick={() => setIsNotifsOpen((prev) => !prev)}
            aria-label={`View operational notifications (${unreadCount} unread)`}
            className="relative min-w-[44px] min-h-[44px] flex items-center justify-center text-ink-muted hover:text-ink hover:bg-warm-stone-light/70 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass transition-colors cursor-pointer"
          >
            <Bell className="w-4 h-4" aria-hidden="true" />
            {unreadCount > 0 && (
              <span className="absolute top-2 right-2 min-w-[16px] h-4 px-1 rounded-full bg-[#541424] text-white text-[10px] font-bold flex items-center justify-center leading-none">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {isNotifsOpen && (
            <div className="absolute right-0 top-12 w-80 sm:w-96 bg-white border border-warm-stone rounded-xl shadow-xl z-50 overflow-hidden">
              <div className="p-3.5 bg-ivory-warm border-b border-warm-stone flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-serif font-bold text-ink uppercase tracking-wider">
                    Operational Alerts
                  </h3>
                  <span className="text-[11px] text-ink-muted">
                    {unreadCount} unread notice{unreadCount !== 1 ? 's' : ''}
                  </span>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={() => markAllReadMutation.mutate()}
                    className="text-[11px] text-bronze hover:underline font-medium flex items-center gap-1 cursor-pointer"
                  >
                    <CheckCheck className="w-3.5 h-3.5" />
                    Mark all read
                  </button>
                )}
              </div>

              <div className="divide-y divide-warm-stone/50 max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-xs text-ink-muted">
                    No active notifications. All operations clear.
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => handleNotificationClick(n)}
                      className={`p-3 text-left transition-colors cursor-pointer flex items-start gap-2.5 ${
                        n.is_read ? 'bg-white hover:bg-warm-stone-light/40 opacity-75' : 'bg-amber-50/40 hover:bg-amber-50/80 font-medium'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${n.is_read ? 'bg-warm-stone' : 'bg-[#541424]'}`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-1">
                          <p className="text-xs font-semibold text-ink truncate">{n.title}</p>
                          <span className="text-[10px] text-ink-faint shrink-0 capitalize">{n.category}</span>
                        </div>
                        <p className="text-[11px] text-ink-muted mt-0.5 line-clamp-2 leading-tight">{n.message}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Authenticated User Profile & Dropdown */}
        <div ref={profileRef} className="relative">
          <button
            type="button"
            onClick={() => setIsProfileOpen((prev) => !prev)}
            aria-label="User Account Menu"
            className="flex items-center gap-2.5 pl-2 border-l border-warm-stone/80 hover:opacity-85 transition-opacity cursor-pointer text-left"
          >
            <div
              className="w-8 h-8 rounded-md bg-warm-stone-light border border-bronze/30 text-ink font-serif font-bold text-xs flex items-center justify-center select-none shadow-2xs shrink-0"
              aria-label={`Profile: ${displayName}`}
            >
              {displayInitials}
            </div>
            <div className="hidden xl:block text-left">
              <span className="block text-xs font-semibold text-ink leading-none">
                {displayName}
              </span>
              <span className="block text-[10px] text-ink-muted mt-0.5">
                {currentRoleTitle}
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-ink-muted hidden xl:block" />
          </button>

          {isProfileOpen && (
            <div className="absolute right-0 top-12 w-64 bg-white border border-warm-stone rounded-xl shadow-xl z-50 p-2 text-xs">
              <div className="p-3 border-b border-warm-stone/60 mb-1 bg-ivory-warm/60 rounded-lg">
                <p className="font-serif font-bold text-ink text-sm">{displayName}</p>
                <p className="text-ink-muted text-[11px]">{appUser?.email || 'aarav@theroyalknot.in'}</p>
                <div className="inline-flex items-center gap-1 mt-1.5 px-2 py-0.5 rounded-full bg-bronze/10 text-bronze font-semibold text-[10px] uppercase tracking-wider">
                  <Shield className="w-3 h-3" />
                  <span>{currentRoleTitle}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={handleSignOut}
                className="w-full flex items-center gap-2 px-3 py-2 text-red-700 hover:bg-red-50 rounded-lg transition-colors cursor-pointer font-medium"
              >
                <LogOut className="w-4 h-4 text-red-600" />
                <span>Log Out of Station</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
