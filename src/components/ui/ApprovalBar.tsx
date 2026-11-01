import React from "react"
import { cn } from "@/lib/utils"
import { Check, X, AlertCircle } from "lucide-react"

interface ApprovalBarProps {
  title: string
  description?: string
  impact?: string
  approver?: string
  onApprove: () => void
  onSendBack: () => void
  isSubmitting?: boolean
  className?: string
}

export const ApprovalBar: React.FC<ApprovalBarProps> = ({
  title,
  description,
  impact,
  approver,
  onApprove,
  onSendBack,
  isSubmitting = false,
  className,
}) => {
  return (
    <div
      className={cn(
        "p-4 bg-[#F4EFEA] border border-[#C4A46D]/40 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm",
        className
      )}
    >
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#885A14] shrink-0" aria-hidden="true" />
          <h4 className="text-sm font-semibold text-[#292E27]">{title}</h4>
        </div>
        {description && <p className="text-xs text-[#524E48]">{description}</p>}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[#69655D]">
          {impact && (
            <span>
              <strong className="text-[#292E27]">Impact:</strong> {impact}
            </span>
          )}
          {approver && (
            <span>
              <strong className="text-[#292E27]">Required Approver:</strong> {approver}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={onSendBack}
          disabled={isSubmitting}
          className="px-3 py-1.5 border border-[#D9D1C3] bg-white hover:bg-[#F9F7F4] text-[#292E27] text-xs font-medium rounded transition-colors focus-visible:ring-1 focus-visible:ring-[#C4A46D] inline-flex items-center gap-1.5"
        >
          <X className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Send back</span>
        </button>
        <button
          type="button"
          onClick={onApprove}
          disabled={isSubmitting}
          className="px-3.5 py-1.5 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded transition-colors focus-visible:ring-1 focus-visible:ring-[#C4A46D] inline-flex items-center gap-1.5 shadow-sm"
        >
          <Check className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
          <span>Approve change</span>
        </button>
      </div>
    </div>
  )
}
