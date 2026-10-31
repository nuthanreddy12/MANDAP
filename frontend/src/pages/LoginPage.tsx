import React, { useState } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import { Lock, Mail, ArrowRight, AlertCircle, Heart } from "lucide-react"
import { useAuth } from "@/lib/authContext"

export const LoginPage: React.FC = () => {
  const { signIn, session, appUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/overview"

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

    const result = await signIn(email, password)
    setSubmitting(false)

    if (result.success) {
      navigate(from, { replace: true })
    } else {
      const err = (result.error || "").toLowerCase()
      if (err.includes("couldn't find") || err.includes("not registered") || err.includes("not found")) {
        setErrorMessage(
          "We couldn't find an account associated with this email. Check your details or contact your agency administrator."
        )
      } else {
        setErrorMessage(
          "Invalid email or password. Please verify your credentials and try again."
        )
      }
    }
  }

  return (
    <div className="min-h-screen w-screen bg-[#FBFAF7] flex flex-col justify-between text-[#292E27]">
      {/* Header */}
      <header className="px-6 py-6 md:px-12 flex items-center justify-between border-b border-[#E8E2D9]">
        <div className="flex items-center gap-2">
          <span className="font-editorial text-2xl tracking-wider text-[#292E27] font-medium">
            MANDAP
          </span>
          <span className="text-[#C4A46D] text-xs">✳</span>
        </div>
        <Link
          to="/customer/login"
          className="text-xs font-medium text-[#878074] hover:text-[#292E27] transition-colors inline-flex items-center gap-1.5"
        >
          <Heart className="w-3.5 h-3.5 text-[#C4A46D]" />
          <span>Client Couple Portal</span>
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md bg-white border border-[#E2DBD0] rounded-xl shadow-sm p-8">
          <div className="mb-6 text-center">
            <h1 className="font-editorial text-2xl text-[#292E27] mb-1">
              Agency Team Sign In
            </h1>
            <p className="text-xs text-[#878074]">
              Sign in to access your agency workspace and client weddings
            </p>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3 rounded-md bg-[#AE5142]/10 border border-[#AE5142]/30 flex items-start gap-2.5 text-xs text-[#AE5142] leading-relaxed">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#524E48] mb-1.5" htmlFor="email-input">
                Staff Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@theroyalknot.in"
                  required
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-[#524E48]" htmlFor="password-input">
                  Password
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 h-10 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center justify-center gap-2 shadow-sm disabled:opacity-60 cursor-pointer"
            >
              {submitting ? (
                <span>Signing In...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#C4A46D]" />
                </>
              )}
            </button>
          </form>

          {/* Invitation Notice */}
          <div className="mt-6 pt-5 border-t border-[#E8E2D9] text-center space-y-3">
            <p className="text-[11px] text-[#878074]">
              Staff access is restricted to authorized planners and coordinators. New accounts are created by agency administrator invitation only.
            </p>

            <div className="p-3 bg-[#FAF8F5] border border-[#E2DBD0] rounded-lg text-left">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-[#292E27]">Planning your wedding?</span>
                <Link
                  to="/customer/login"
                  className="text-xs font-semibold text-[#852C1F] hover:underline"
                >
                  Client Portal &rarr;
                </Link>
              </div>
              <p className="text-[11px] text-[#878074] mt-0.5">
                Couples and families can track their schedule, review milestones and submit requests.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 border-t border-[#E8E2D9] text-center text-[11px] text-[#878074]">
        MANDAP &middot; The Royal Knot Wedding Operations &middot; Enterprise Agency Workspace
      </footer>
    </div>
  )
}
