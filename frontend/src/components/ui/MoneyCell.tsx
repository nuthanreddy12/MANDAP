import React from "react"
import { cn } from "@/lib/utils"
import { formatINR } from "@/lib/formatters"

interface MoneyCellProps {
  amount: number | string | null | undefined
  compact?: boolean
  subtitle?: string
  className?: string
  align?: "left" | "right" | "center"
}

export const MoneyCell: React.FC<MoneyCellProps> = ({
  amount,
  compact = false,
  subtitle,
  className,
  align = "right",
}) => {
  const formatted = formatINR(amount, compact)

  return (
    <div
      className={cn(
        "tabular-nums inline-flex flex-col",
        align === "right" && "text-right items-end",
        align === "left" && "text-left items-start",
        align === "center" && "text-center items-center",
        className
      )}
    >
      <span className="font-semibold text-[#292E27] tracking-tight">{formatted}</span>
      {subtitle && (
        <span className="text-[11px] text-[#69655D] tracking-normal font-normal">
          {subtitle}
        </span>
      )}
    </div>
  )
}
