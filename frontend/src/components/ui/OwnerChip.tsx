import React from "react"
import { cn } from "@/lib/utils"

interface OwnerChipProps {
  name: string
  role?: string
  avatarUrl?: string
  className?: string
  size?: "sm" | "md"
}

export const OwnerChip: React.FC<OwnerChipProps> = ({
  name,
  role,
  className,
  size = "md",
}) => {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()

  return (
    <div
      className={cn("inline-flex items-center gap-2", className)}
      title={`${name}${role ? ` (${role})` : ""}`}
    >
      <div
        className={cn(
          "rounded-full bg-[#E9E3D8] text-[#292E27] font-medium border border-[#D9D1C3] flex items-center justify-center select-none",
          size === "sm" ? "w-6 h-6 text-[10px]" : "w-7 h-7 text-xs"
        )}
        aria-hidden="true"
      >
        {initials}
      </div>
      <div className="flex flex-col text-left">
        <span
          className={cn(
            "font-medium text-[#292E27] leading-tight",
            size === "sm" ? "text-xs" : "text-sm"
          )}
        >
          {name}
        </span>
        {role && (
          <span className="text-[11px] text-[#69655D] leading-none">
            {role}
          </span>
        )}
      </div>
    </div>
  )
}
