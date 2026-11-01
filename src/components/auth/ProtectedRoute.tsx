import React from "react"
import { Navigate, useLocation, Outlet } from "react-router-dom"
import { useAuth } from "@/lib/useAuth"

export const ProtectedRoute: React.FC = () => {
  const { session, appUser, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-[#FBFAF7] text-[#292E27]">
        <div className="flex items-center gap-2 mb-3">
          <span className="font-serif text-2xl tracking-wider text-[#292E27]">MANDAP</span>
          <span className="text-[#C4A46D] text-xs">*</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#878074]">
          <span className="w-2 h-2 rounded-full bg-[#C4A46D] animate-ping" />
          <span>Restoring session...</span>
        </div>
      </div>
    )
  }

  // If customer attempts to access agency operations desk, route them to couple sanctuary
  if (appUser?.role === "customer" || localStorage.getItem("mandap_customer_token")) {
    return <Navigate to="/customer/dashboard" replace />
  }

  if (!session || !appUser) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
