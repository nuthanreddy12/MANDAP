import React from "react"
import { cn } from "@/lib/utils"
import { StatusBadge } from "./StatusBadge"
import { formatINR } from "@/lib/formatters"
import { AlertTriangle, ArrowRight } from "lucide-react"

interface ExceptionRowProps {
  title: string
  expected: string | number
  actual: string | number
  variance?: string | number
  evidence?: string
  status?: string
  assignedReviewer?: string
  onReview?: () => void
  className?: string
}

export const ExceptionRow: React.FC<ExceptionRowProps> = ({
  title,
  expected,
  actual,
  variance,
  evidence,
  status = "Needs review",
  assignedReviewer,
  onReview,
  className,
}) => {
  const formatVal = (val: string | number) => {
    return typeof val === "number" ? formatINR(val) : val
  }

  return (
    <div
      className={cn(
        "p-4 bg-white border border-[#E2DBD0] rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all hover:border-[#C4A46D]/60",
        className
      )}
    >
      <div className="space-y-1.5 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <AlertTriangle className="w-4 h-4 text-[#AE5142] shrink-0" aria-hidden="true" />
          <span className="font-medium text-sm text-[#292E27]">{title}</span>
          <StatusBadge status={status} />
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs text-[#524E48]">
          <span className="tabular-nums">
            <span className="text-[#878074]">Expected:</span>{" "}
            <strong>{formatVal(expected)}</strong>
          </span>
          <ArrowRight className="w-3 h-3 text-[#878074]" aria-hidden="true" />
          <span className="tabular-nums">
            <span className="text-[#878074]">Invoiced/Actual:</span>{" "}
            <strong className="text-[#AE5142]">{formatVal(actual)}</strong>
          </span>
          {variance !== undefined && (
            <span className="tabular-nums text-xs px-1.5 py-0.5 bg-[#AE5142]/10 text-[#852C1F] rounded font-medium">
              Δ {formatVal(variance)}
            </span>
          )}
        </div>

        {evidence && (
          <p className="text-xs text-[#69655D] italic">
            Evidence: {evidence}
          </p>
        )}

        {assignedReviewer && (
          <p className="text-[11px] text-[#878074]">
            Assigned reviewer: <span className="text-[#292E27] font-medium">{assignedReviewer}</span>
          </p>
        )}
      </div>

      {onReview && (
        <div className="shrink-0">
          <button
            type="button"
            onClick={onReview}
            className="px-3.5 py-1.5 border border-[#292E27] hover:bg-[#292E27] hover:text-white text-[#292E27] text-xs font-medium rounded transition-colors focus-visible:ring-1 focus-visible:ring-[#C4A46D]"
          >
            Review discrepancy
          </button>
        </div>
      )}
    </div>
  )
}
