import React from "react"
import { NavLink } from "react-router-dom"
import {
  Compass,
  MessageSquare,
  Sparkles,
  Users,
  IndianRupee,
  Settings,
  ChevronRight,
  LogOut,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/lib/authContext"

interface SidebarProps {
  enquiryCount?: number
  className?: string
  onCloseMobile?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  enquiryCount = 4,
  className,
  onCloseMobile,
}) => {
  const { appUser, signOut } = useAuth()
  const primaryNav = [
    { label: "Overview", to: "/overview", icon: Compass },
    {
      label: "Enquiries",
      to: "/enquiries",
      icon: MessageSquare,
      badge: enquiryCount,
    },
    { label: "Weddings", to: "/weddings", icon: Sparkles },
    { label: "Vendors", to: "/vendors", icon: Users },
  ]

  const businessNav = [
    { label: "Finance", to: "/finance", icon: IndianRupee },
    { label: "Settings", to: "/settings", icon: Settings },
  ]

  return (
    <aside
      className={cn(
        "w-[230px] bg-[#292E27] text-[#FBFAF7] flex flex-col justify-between shrink-0 h-full border-r border-[#3E453C] select-none",
        className
      )}
    >
      {/* Brand Header */}
      <div>
        <div className="p-6 pb-5 border-b border-[#3E453C]">
          <div className="flex items-center gap-2">
            <span className="font-editorial text-2xl tracking-wider text-[#FBFAF7] font-normal">
              MANDAP
            </span>
            <span className="text-[#C4A46D] text-xs">✳</span>
          </div>
          <p className="text-[10px] uppercase tracking-widest text-[#B5AEA4] mt-1 font-mono">
            Wedding work, well held
          </p>
        </div>

        {/* Primary Workspace Nav */}
        <div className="px-3 py-4">
          <p className="px-3 text-[10px] uppercase tracking-wider text-[#989287] font-semibold mb-2">
            Workspace
          </p>
          <nav className="space-y-0.5" aria-label="Workspace navigation">
            {primaryNav.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center justify-between px-3 py-2 rounded text-xs font-medium transition-colors",
                      isActive
                        ? "bg-[#3D443A] text-[#FBFAF7]"
                        : "text-[#D5CFC5] hover:bg-[#343B31] hover:text-[#FBFAF7]"
                    )
                  }
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-[#C4A46D] shrink-0" aria-hidden="true" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge ? (
                    <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded-full bg-[#C4A46D]/20 text-[#C4A46D] border border-[#C4A46D]/40">
                      {item.badge}
                    </span>
                  ) : null}
                </NavLink>
              )
            })}
          </nav>
        </div>

        {/* Business Nav */}
        <div className="px-3 py-2 border-t border-[#3E453C]/60">
          <p className="px-3 text-[10px] uppercase tracking-wider text-[#989287] font-semibold mb-2">
            Business
          </p>
          <nav className="space-y-0.5" aria-label="Business navigation">
            {businessNav.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-2.5 px-3 py-2 rounded text-xs font-medium transition-colors",
                      isActive
                        ? "bg-[#3D443A] text-[#FBFAF7]"
                        : "text-[#D5CFC5] hover:bg-[#343B31] hover:text-[#FBFAF7]"
                    )
                  }
                >
                  <Icon className="w-4 h-4 text-[#C4A46D] shrink-0" aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Agency Identity Footer */}
      <div className="p-4 border-t border-[#3E453C] bg-[#222620]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-[#C4A46D]/20 border border-[#C4A46D]/50 text-[#C4A46D] text-xs font-semibold flex items-center justify-center shrink-0">
              {appUser?.avatar_initials || "AM"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-[#FBFAF7] truncate">
                {appUser?.name || "Aarav Mehta"}
              </p>
              <p className="text-[10px] text-[#A69F93] truncate capitalize">
                {appUser?.role ? `${appUser.role.replace('_', ' ')}` : "Owner"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => signOut()}
            title="Sign out"
            aria-label="Sign out"
            className="w-7 h-7 rounded flex items-center justify-center text-[#888175] hover:text-[#AE5142] hover:bg-[#343B31] transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </aside>
  )
}
