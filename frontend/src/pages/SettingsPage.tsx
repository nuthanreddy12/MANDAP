import React from "react"
import { OwnerChip } from "@/components/ui/OwnerChip"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { Building, Shield, Users, Save } from "lucide-react"

export const SettingsPage: React.FC = () => {
  const team = [
    { name: "Aarav Mehta", role: "Agency Owner", email: "aarav@theroyalknot.in", permissions: "Full Administrator" },
    { name: "Nisha Sharma", role: "Lead Planner", email: "nisha@theroyalknot.in", permissions: "Wedding Lead, Vendor Selection" },
    { name: "Kabir Verma", role: "On-site Coordinator", email: "kabir@theroyalknot.in", permissions: "Day-of Run of Show, Incidents" },
    { name: "Rhea Kapoor", role: "Finance Manager", email: "rhea@theroyalknot.in", permissions: "Invoices, Payments, Reconciliation" },
  ]

  return (
    <div className="p-4 md:p-8 max-w-[1440px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
        <div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-normal text-[#292E27] tracking-tight">
            Agency Configuration & Permissions
          </h2>
          <p className="text-xs text-[#878074] mt-0.5">
            The Royal Knot operational settings, role-based security, and templates
          </p>
        </div>
        <button
          type="button"
          className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 self-start sm:self-auto shadow-xs"
        >
          <Save className="w-3.5 h-3.5 text-[#C4A46D]" />
          <span>Save preferences</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Agency Profile */}
        <div className="bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-[#F4EFEA] pb-3">
            <Building className="w-4 h-4 text-[#C4A46D]" />
            <h3 className="font-editorial text-base text-[#292E27]">Agency Profile</h3>
          </div>
          <div className="space-y-3 text-xs">
            <div>
              <label className="text-[#878074] block mb-1">Agency Name</label>
              <input
                type="text"
                defaultValue="The Royal Knot"
                className="w-full bg-[#F4EFEA] border border-[#E2DBD0] rounded px-3 py-1.5 text-[#292E27]"
              />
            </div>
            <div>
              <label className="text-[#878074] block mb-1">Operating Hubs</label>
              <input
                type="text"
                defaultValue="Jaipur & Udaipur, Rajasthan"
                className="w-full bg-[#F4EFEA] border border-[#E2DBD0] rounded px-3 py-1.5 text-[#292E27]"
              />
            </div>
            <div>
              <label className="text-[#878074] block mb-1">Default Currency</label>
              <input
                type="text"
                defaultValue="INR (₹)"
                disabled
                className="w-full bg-[#E9E3D8]/50 border border-[#E2DBD0] rounded px-3 py-1.5 text-[#69655D]"
              />
            </div>
          </div>
        </div>

        {/* Team & Permissions (2 Cols) */}
        <div className="md:col-span-2 bg-white border border-[#E2DBD0] rounded-lg p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-[#F4EFEA] pb-3">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#C4A46D]" />
              <h3 className="font-editorial text-base text-[#292E27]">Role-Based Access Control</h3>
            </div>
            <span className="text-xs text-[#878074]">4 members</span>
          </div>

          <div className="divide-y divide-[#F4EFEA]">
            {team.map((m, idx) => (
              <div key={idx} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="space-y-0.5">
                  <p className="font-medium text-[#292E27]">{m.name}</p>
                  <p className="text-[11px] text-[#878074]">{m.role} · {m.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] px-2 py-0.5 bg-[#F4EFEA] border border-[#E2DBD0] rounded text-[#524E48]">
                    {m.permissions}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
