import React, { useState } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import { Lock, Mail, ArrowRight, AlertCircle, Heart } from "lucide-react"
import { useAuth } from "@/lib/useAuth"

export const LoginPage: React.FC = () => {
  const { signIn, session, appUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/weddings"

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Redirect if already logged in as staff
  React.useEffect(() => {
    if (session && appUser) {
      if (appUser.role === "customer") {
        navigate("/customer/dashboard", { replace: true })
      } else {
        navigate(from, { replace: true })
      }
    }
  }, [session, appUser, navigate, from])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setErrorMessage("Please enter both email and password")
      return
    }

    setSubmitting(true)
    setErrorMessage(null)

    // Clear any conflicting customer session tokens
    localStorage.removeItem("mandap_customer_token")
    localStorage.removeItem("mandap_customer_user")
    localStorage.removeItem("mandap_customer_wedding_id")

    const result = await signIn(email, password)
    setSubmitting(false)

    if (result.success) {
      navigate(from, { replace: true })
    } else {
      const err = (result.error || "").toLowerCase()
      if (err.includes("couldn't find") || err.includes("not registered") || err.includes("not found")) {
        setErrorMessage(
          "We could not find an account associated with this email. Check your details or contact your agency administrator."
        )
      } else {
        setErrorMessage(
          "Invalid email or password. Please verify your credentials and try again."
        )
      }
    }
  }

  return (
    <div className="min-h-screen w-screen bg-[#FAF8F5] flex flex-col justify-between text-[#1A1A1A]">
      {/* Header */}
      <header className="px-6 py-5 md:px-12 flex items-center justify-between border-b border-[#E8E2D9] bg-white">
        <Link to="/" className="flex items-center gap-3">
          <img src="/mandap-logo.png" alt="MANDAP" className="h-10 w-auto object-contain" />
          <span className="font-serif text-xl tracking-wider text-[#541424] font-medium">
            MANDAP
          </span>
        </Link>
        <Link
          to="/customer/login"
          className="text-xs font-medium text-[#71717A] hover:text-[#541424] transition-colors inline-flex items-center gap-1.5"
        >
          <Heart className="w-3.5 h-3.5 text-[#B8860B]" />
          <span>Client Couple Portal</span>
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md bg-white border border-[#E8E2D9] rounded-2xl shadow-sm p-8">
          <div className="mb-8 text-center">
            <span className="text-xs uppercase tracking-widest text-[#B8860B] font-medium">
              Agency Operations Desk
            </span>
            <h1 className="font-serif text-2xl text-[#1A1A1A] mt-2 mb-2 font-normal">
              Sign In to Your Workspace
            </h1>
            <p className="text-xs text-[#71717A]">
              Oversee multi-day royal production, heritage palace logistics, and live ceremony schedules.
            </p>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#4A4A4A] mb-1.5 uppercase tracking-wider">
                Work Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@theroyalknot.in"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#FAF8F5] border border-[#E8E2D9] rounded-xl text-xs text-[#1A1A1A] focus:outline-none focus:ring-1 focus:ring-[#541424] focus:border-[#541424] transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#4A4A4A] mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#FAF8F5] border border-[#E8E2D9] rounded-xl text-xs text-[#1A1A1A] focus:outline-none focus:ring-1 focus:ring-[#541424] focus:border-[#541424] transition-all"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 py-3 px-4 rounded-xl text-xs font-medium text-white bg-[#541424] hover:bg-[#6B1728] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#541424] transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 cursor-pointer"
            >
              {submitting ? (
                <span>Verifying credentials...</span>
              ) : (
                <>
                  <span>Enter Operations Desk</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[#F0EBE1] text-center">
            <p className="text-xs text-[#71717A]">
              Are you a client couple?{" "}
              <Link
                to="/customer/login"
                className="text-[#541424] font-medium hover:underline inline-flex items-center gap-1"
              >
                Access Couple Sanctuary
                <ArrowRight className="w-3 h-3" />
              </Link>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 text-center text-[11px] text-[#A1A1AA] border-t border-[#E8E2D9] bg-white">
        MANDAP Luxury Wedding Operating System &copy; 2026
      </footer>
    </div>
  )
}
