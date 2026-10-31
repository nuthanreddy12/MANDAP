import React from "react"
import { cn } from "@/lib/utils"
import { CheckCircle2, Clock, AlertTriangle, AlertCircle, Sparkles } from "lucide-react"

export type StatusVariant =
  | "on_track"
  | "due_soon"
  | "late"
  | "needs_review"
  | "complete"
  | "recommended"
  | "open_issue"
  | "neutral"

interface StatusBadgeProps {
  status: StatusVariant | string
  label?: string
  className?: string
  showIcon?: boolean
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  className,
  showIcon = false,
}) => {
  const norm = status.toLowerCase().replace(/[\s-]/g, "_")
  
  let styles = "bg-[#E9E3D8] text-[#292E27] border-[#D9D1C3]"
  let icon: React.ReactNode = null
  let displayLabel = label || status

  if (norm === "on_track" || norm === "confirmed") {
    styles = "bg-[#61765B]/15 text-[#374B32] border-[#61765B]/40 font-medium"
    icon = <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || "On track"
  } else if (norm === "due_soon" || norm === "scheduled") {
    styles = "bg-[#C98A2C]/15 text-[#885A14] border-[#C98A2C]/40 font-medium"
    icon = <Clock className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || "Due soon"
  } else if (norm === "late" || norm === "open_issue" || norm === "urgent") {
    styles = "bg-[#AE5142]/15 text-[#852C1F] border-[#AE5142]/40 font-medium"
    icon = <AlertCircle className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || (norm === "open_issue" ? "Open issue" : "Late")
  } else if (norm === "needs_review" || norm === "attention") {
    styles = "bg-[#C4A46D]/20 text-[#6B532C] border-[#C4A46D]/50 font-medium"
    icon = <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || "Needs review"
  } else if (norm === "complete" || norm === "arrived") {
    styles = "bg-[#E9E3D8] text-[#292E27] border-[#C9C0B1]"
    icon = <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || (norm === "arrived" ? "Arrived" : "Complete")
  } else if (norm === "recommended") {
    styles = "bg-[#C4A46D]/25 text-[#4D3A19] border-[#C4A46D]/60 font-medium"
    icon = <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
    displayLabel = label || "Recommended*"
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs border tracking-tight transition-colors",
        styles,
        className
      )}
    >
      {showIcon && icon}
      <span>{displayLabel}</span>
    </span>
  )
}
