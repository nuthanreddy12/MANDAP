import React from "react"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { formatINR } from "@/lib/formatters"
import { IndianRupee, ArrowUpRight, ArrowDownRight, Plus, Download } from "lucide-react"

export const FinancePage: React.FC = () => {
  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
        <div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight">
            Agency Season Finance
          </h2>
          <p className="text-xs text-[#878074] mt-0.5">
            Season 2026-27 receivables, vendor obligations, and transparent margin coverage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="px-3 py-1.5 border border-[#E2DBD0] hover:bg-[#F4EFEA] text-[#292E27] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-[#69655D]" />
            <span>Export ledger</span>
          </button>
          <button
            type="button"
            className="px-3.5 py-1.5 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded transition-colors inline-flex items-center gap-1.5 shadow-xs"
          >
            <Plus className="w-3.5 h-3.5 text-[#C4A46D]" />
            <span>Record payment</span>
          </button>
        </div>
      </div>

      {/* Top 3 High Level Season Financial Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
          <span className="text-xs text-[#878074]">Total Client Contracted Revenue</span>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#292E27]">
            ₹5.00Cr
          </div>
          <div className="flex items-center gap-1 mt-1 text-xs text-[#61765B]">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>₹2.45Cr collected to date</span>
          </div>
        </div>

        <div className="p-5 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
          <span className="text-xs text-[#878074]">Total Vendor Committed Obligations</span>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#292E27]">
            ₹3.62Cr
          </div>
          <div className="flex items-center gap-1 mt-1 text-xs text-[#AE5142]">
            <ArrowDownRight className="w-3.5 h-3.5" />
            <span>₹1.84Cr paid · ₹1.78Cr remaining</span>
          </div>
        </div>

        <div className="p-5 bg-white border border-[#E2DBD0] rounded-lg shadow-xs">
          <span className="text-xs text-[#878074]">Recorded Operating Margin</span>
          <div className="mt-2 text-3xl font-editorial tabular-nums text-[#885A14]">
            ₹1.38Cr
          </div>
          <p className="mt-1 text-xs text-[#878074]">
            Coverage: <strong>Partial (68%)</strong> · 4 weddings in progress
          </p>
        </div>
      </div>

      {/* Near-term cash schedule */}
      <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-4">
        <h3 className="font-editorial text-lg text-[#292E27] font-normal border-b border-[#F4EFEA] pb-2">
          Near-term payment obligations (Next 14 Days)
        </h3>

        <div className="divide-y divide-[#F4EFEA] text-xs">
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <p className="font-medium text-[#292E27]">Saffron Table · Final balance payment</p>
              <p className="text-[11px] text-[#878074]">Mehra × Kapoor · Catering · Due 20 Nov</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="tabular-nums font-semibold text-sm text-[#292E27]">₹5.62L</span>
              <StatusBadge status="needs_review" label="Pending review" />
            </div>
          </div>

          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <p className="font-medium text-[#292E27]">DJ Nova · Performance fee remainder</p>
              <p className="text-[11px] text-[#878074]">Mehra × Kapoor · Music & Sound · Due 18 Nov</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="tabular-nums font-semibold text-sm text-[#292E27]">₹1.20L</span>
              <StatusBadge status="on_track" label="Ready to pay" />
            </div>
          </div>

          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <p className="font-medium text-[#292E27]">Gulab House · Floral installation second tranche</p>
              <p className="text-[11px] text-[#878074]">Sharma × Bansal · Decor · Due 12 Nov</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="tabular-nums font-semibold text-sm text-[#292E27]">₹3.50L</span>
              <StatusBadge status="due_soon" label="Due in 5 days" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
