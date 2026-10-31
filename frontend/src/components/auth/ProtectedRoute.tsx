import React from "react"
import { Navigate, useLocation, Outlet } from "react-router-dom"
import { useAuth } from "@/lib/authContext"

export const ProtectedRoute: React.FC = () => {
  const { session, appUser, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-[#FBFAF7] text-[#292E27]">
        <div className="flex items-center gap-2 mb-3">
          <span className="font-editorial text-2xl tracking-wider text-[#292E27]">MANDAP</span>
          <span className="text-[#C4A46D] text-xs">✳</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#878074]">
          <span className="w-2 h-2 rounded-full bg-[#C4A46D] animate-ping" />
          <span>Restoring session...</span>
        </div>
      </div>
    )
  }

  if (!session || !appUser) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (appUser.role === "customer") {
    return <Navigate to="/customer/dashboard" replace />
  }

  return <Outlet />
}
