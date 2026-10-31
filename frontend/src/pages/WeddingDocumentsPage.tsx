import React from "react"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { SourceChip } from "@/components/ui/SourceChip"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { Upload, FileText, Download } from "lucide-react"

export const WeddingDocumentsPage: React.FC = () => {
  const docs = [
    { name: "Mehra_Kapoor_Service_Agreement_Signed.pdf", type: "Client Agreement", date: "15 Sep 2026", size: "2.4 MB", status: "complete" },
    { name: "SaffronTable_Catering_v2.pdf", type: "Vendor Quote", date: "26 Oct 2026", size: "1.8 MB", status: "complete" },
    { name: "Mewar_Kitchens_Catering_Quote.pdf", type: "Vendor Quote", date: "27 Oct 2026", size: "3.1 MB", status: "complete" },
    { name: "Saffron_Final_Invoice_INV104.pdf", type: "Vendor Invoice", date: "18 Nov 2026", size: "1.2 MB", status: "needs_review" },
    { name: "Oberoi_Rajvilas_Lawn_Clearance.pdf", type: "Venue License", date: "28 Oct 2026", size: "4.5 MB", status: "complete" },
  ]

  return (
    <div className="flex flex-col min-h-full">
      <WeddingWorkspaceHeader
        coupleName="Mehra × Kapoor"
        dates="14–16 November 2026"
        destination="Jaipur"
        packageType="Full service"
        guestCount={420}
        healthStatus="on_track"
      />

      <div className="p-4 md:p-8 max-w-[1440px] w-full mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
          <div>
            <h3 className="font-editorial text-2xl text-[#292E27] font-normal">
              Wedding Document Vault
            </h3>
            <p className="text-xs text-[#878074] mt-0.5">
              Preserved source PDFs with cryptographic provenance and review audit logs
            </p>
          </div>
          <button
            type="button"
            className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 self-start sm:self-auto shadow-xs"
          >
            <Upload className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
            <span>Upload document</span>
          </button>
        </div>

        <div className="bg-white border border-[#E2DBD0] rounded-lg divide-y divide-[#F4EFEA] shadow-xs">
          {docs.map((doc, idx) => (
            <div key={idx} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#F9F7F4] transition-colors">
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-[#C4A46D] shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-[#292E27]">{doc.name}</p>
                  <p className="text-[11px] text-[#878074]">
                    {doc.type} · Uploaded {doc.date} · {doc.size}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                <StatusBadge status={doc.status} />
                <button
                  type="button"
                  className="p-1.5 text-[#69655D] hover:text-[#292E27] border border-[#E2DBD0] rounded hover:bg-white transition-colors"
                  title="Download document"
                  aria-label="Download document"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
