import React from "react"
import { cn } from "@/lib/utils"
import { FileText, ExternalLink } from "lucide-react"

interface SourceChipProps {
  filename: string
  uploadDate?: string
  revision?: string
  url?: string
  onClick?: () => void
  className?: string
}

export const SourceChip: React.FC<SourceChipProps> = ({
  filename,
  uploadDate,
  revision,
  url,
  onClick,
  className,
}) => {
  const handleClick = (e: React.MouseEvent) => {
    if (onClick) {
      e.preventDefault()
      onClick()
    } else if (url) {
      window.open(url, "_blank", "noopener,noreferrer")
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-1 bg-[#F4EFEA] hover:bg-[#E9E3D8] text-[#292E27] rounded text-xs border border-[#E2DBD0] transition-colors focus-visible:ring-1 focus-visible:ring-[#C4A46D] text-left",
        className
      )}
      title={`Source document: ${filename}${uploadDate ? ` (Uploaded ${uploadDate})` : ""}`}
    >
      <FileText className="w-3.5 h-3.5 text-[#69655D] shrink-0" aria-hidden="true" />
      <span className="truncate max-w-[150px] font-medium">{filename}</span>
      {revision && <span className="text-[#878074] text-[10px]">({revision})</span>}
      <ExternalLink className="w-3 h-3 text-[#878074] shrink-0 ml-0.5" aria-hidden="true" />
    </button>
  )
}
