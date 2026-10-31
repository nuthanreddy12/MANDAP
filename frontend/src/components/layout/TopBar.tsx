import React, { useState } from "react"
import { Menu, Plus, Bell, Search, Check } from "lucide-react"

interface TopBarProps {
  onToggleMobileNav: () => void
  onNewEnquiry?: () => void
  onNewWedding?: () => void
  onRecordPayment?: () => void
  currentTitle?: string
}

export const TopBar: React.FC<TopBarProps> = ({
  onToggleMobileNav,
  onNewEnquiry,
  onNewWedding,
  onRecordPayment,
  currentTitle = "Jaipur & Udaipur Season 2026-27",
}) => {
  const [showNewDropdown, setShowNewDropdown] = useState(false)

  return (
    <header className="h-16 border-b border-[#E2DBD0] bg-white px-4 md:px-8 flex items-center justify-between shrink-0 z-10">
      <div className="flex items-center gap-3">
        {/* Mobile menu trigger */}
        <button
          type="button"
          onClick={onToggleMobileNav}
          className="md:hidden w-11 h-11 flex items-center justify-center rounded-lg border border-[#E2DBD0] text-[#292E27] hover:bg-[#F4EFEA] transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Title / Context */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#878074] hidden sm:inline">The Royal Knot</span>
          <span className="text-xs text-[#878074] hidden sm:inline">/</span>
          <h1 className="text-sm font-semibold text-[#292E27] tracking-tight">{currentTitle}</h1>
        </div>
      </div>

      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Quick Search */}
        <div className="relative hidden lg:block w-64">
          <Search className="w-3.5 h-3.5 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="search"
            placeholder="Search wedding, vendor, invoice..."
            className="w-full text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-1.5 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] transition-colors"
          />
        </div>

        {/* Notification indicator */}
        <button
          type="button"
          className="w-9 h-9 rounded-md border border-[#E2DBD0] text-[#524E48] hover:text-[#292E27] hover:bg-[#F4EFEA] flex items-center justify-center relative transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" aria-hidden="true" />
          <span className="w-2 h-2 rounded-full bg-[#AE5142] absolute top-2 right-2 border-2 border-white" />
        </button>

        {/* Global Action Menu */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNewDropdown(!showNewDropdown)}
            className="h-9 px-3.5 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 shadow-sm"
            aria-expanded={showNewDropdown}
          >
            <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
            <span>New</span>
          </button>

          {showNewDropdown && (
            <div
              className="absolute right-0 mt-1.5 w-48 bg-white border border-[#E2DBD0] rounded-md shadow-lg py-1 z-30 animate-in fade-in-50 duration-100"
              role="menu"
            >
              <button
                type="button"
                onClick={() => {
                  setShowNewDropdown(false)
                  onNewEnquiry?.()
                }}
                className="w-full text-left px-3.5 py-2 text-xs text-[#292E27] hover:bg-[#F4EFEA] flex items-center gap-2"
                role="menuitem"
              >
                <Check className="w-3 h-3 text-[#C4A46D]" />
                <span>New enquiry</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowNewDropdown(false)
                  onNewWedding?.()
                }}
                className="w-full text-left px-3.5 py-2 text-xs text-[#292E27] hover:bg-[#F4EFEA] flex items-center gap-2"
                role="menuitem"
              >
                <Check className="w-3 h-3 text-[#C4A46D]" />
                <span>New wedding</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowNewDropdown(false)
                  onRecordPayment?.()
                }}
                className="w-full text-left px-3.5 py-2 text-xs text-[#292E27] hover:bg-[#F4EFEA] flex items-center gap-2 border-t border-[#F4EFEA]"
                role="menuitem"
              >
                <Check className="w-3 h-3 text-[#C4A46D]" />
                <span>Record payment</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
