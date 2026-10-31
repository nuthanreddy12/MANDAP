import React from "react"
import { NavLink, useParams } from "react-router-dom"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { cn } from "@/lib/utils"
import { MapPin, Calendar, Users, Briefcase, Plus, Edit } from "lucide-react"

interface WeddingHeaderProps {
  coupleName?: string
  dates?: string
  destination?: string
  packageType?: string
  guestCount?: number | string
  healthStatus?: string
  onEditDetails?: () => void
  onAddUpdate?: () => void
}

export const WeddingWorkspaceHeader: React.FC<WeddingHeaderProps> = ({
  coupleName = "Mehra × Kapoor",
  dates = "14–16 November 2026",
  destination = "Jaipur",
  packageType = "Full service",
  guestCount = 420,
  healthStatus = "On track",
  onEditDetails,
  onAddUpdate,
}) => {
  const { id = "w1" } = useParams<{ id: string }>()

  const tabs = [
    { label: "Overview", to: `/weddings/${id}/overview` },
    { label: "Vendors & quotes", to: `/weddings/${id}/quotes` },
    { label: "Plan", to: `/weddings/${id}/plan` },
    { label: "Run of show", to: `/weddings/${id}/run-of-show` },
    { label: "Finance", to: `/weddings/${id}/finance` },
    { label: "Documents", to: `/weddings/${id}/documents` },
  ]

  return (
    <div className="bg-white border-b border-[#E2DBD0] sticky top-0 z-10 shadow-xs">
      <div className="max-w-[1440px] mx-auto px-4 md:px-8 pt-5 pb-3">
        {/* Breadcrumb & status line */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-[#878074] mb-1">
              <span>Weddings</span>
              <span>/</span>
              <span className="text-[#292E27] font-medium">{coupleName}</span>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="font-editorial text-2xl md:text-3xl font-normal text-[#292E27] tracking-tight">
                {coupleName}
              </h2>
              <StatusBadge status={healthStatus} showIcon />
            </div>

            {/* Metadata pills */}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-[#69655D]">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
                <span>{dates}</span>
              </div>
              <span className="text-[#D9D1C3]">·</span>
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
                <span>{destination}</span>
              </div>
              <span className="text-[#D9D1C3]">·</span>
              <div className="flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
                <span>{packageType}</span>
              </div>
              <span className="text-[#D9D1C3]">·</span>
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
                <span>{guestCount} guests</span>
              </div>
            </div>
          </div>

          {/* Contextual Actions */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={onEditDetails}
              className="px-3 py-1.5 border border-[#E2DBD0] hover:bg-[#F4EFEA] text-[#292E27] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5"
            >
              <Edit className="w-3.5 h-3.5 text-[#69655D]" aria-hidden="true" />
              <span>Edit details</span>
            </button>
            <button
              type="button"
              onClick={onAddUpdate}
              className="px-3.5 py-1.5 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
              <span>Add update</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav
          className="flex items-center gap-1 sm:gap-2 mt-5 -mb-3 overflow-x-auto scrollbar-none"
          aria-label="Wedding sections"
        >
          {tabs.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                cn(
                  "px-3 py-2.5 text-xs font-medium border-b-2 whitespace-nowrap transition-colors",
                  isActive
                    ? "border-[#292E27] text-[#292E27]"
                    : "border-transparent text-[#69655D] hover:text-[#292E27] hover:border-[#D9D1C3]"
                )
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  )
}
