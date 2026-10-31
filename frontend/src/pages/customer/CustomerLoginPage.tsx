import React, { useState } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import { Lock, Mail, ArrowRight, AlertCircle, Sparkles, ShieldCheck } from "lucide-react"
import { useAuth } from "@/lib/authContext"

export const CustomerLoginPage: React.FC = () => {
  const { signIn, appUser, refreshAppUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/customer/dashboard"

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Redirect if already logged in as customer
  React.useEffect(() => {
    const localToken = localStorage.getItem("mandap_customer_token")
    if ((appUser && appUser.role === "customer") || localToken) {
      navigate("/customer/dashboard", { replace: true })
    }
  }, [appUser, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setErrorMessage("Please enter both email and password")
      return
    }

    setSubmitting(true)
    setErrorMessage(null)

    try {
      // 1. Direct customer backend authentication
      const res = await fetch("/api/v1/customer/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      if (res.ok) {
        const data = await res.json()
        if (data.token) {
          localStorage.setItem("mandap_customer_token", data.token)
          localStorage.setItem("mandap_customer_user", JSON.stringify(data.user))
          localStorage.setItem("mandap_customer_wedding_id", data.wedding_id)
        }
        // Also sign in Supabase if enabled
        try {
          await signIn(email, password)
        } catch {
          // Local token suffices
        }
        await refreshAppUser()
        navigate(from, { replace: true })
        return
      }

      // If backend returned error, handle friendly message
      const errData = await res.json().catch(() => ({}))
      const detail = errData.detail || ""
      if (
        res.status === 401 ||
        detail.toLowerCase().includes("couldn't find") ||
        detail.toLowerCase().includes("not registered")
      ) {
        setErrorMessage(
          "We couldn't find an account associated with this email. Check your details or contact your wedding planner."
        )
      } else if (res.status === 403) {
        setErrorMessage(
          detail || "Your wedding association could not be verified. Please contact your wedding planner."
        )
      } else {
        setErrorMessage(
          detail || "Invalid email or password. Please verify your credentials and try again."
        )
      }
    } catch (err: unknown) {
      setErrorMessage(
        "Unable to connect to service. Please verify your network and try again."
      )
    } finally {
      setSubmitting(false)
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
          <span className="text-xs uppercase tracking-widest text-[#878074] pl-2 border-l border-[#E8E2D9]">
            Client Sanctuary
          </span>
        </div>
        <Link
          to="/login"
          className="text-xs font-medium text-[#878074] hover:text-[#292E27] transition-colors inline-flex items-center gap-1.5"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-[#C4A46D]" />
          <span>Agency Team Sign In</span>
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md bg-white border border-[#E2DBD0] rounded-xl shadow-sm p-8">
          <div className="mb-6 text-center">
            <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-[#FAF5EB] border border-[#E8E2D9] text-[#C4A46D] mb-3">
              <Sparkles className="w-5 h-5" />
            </div>
            <h1 className="font-editorial text-2xl text-[#292E27] mb-1">
              Client Couple Sign In
            </h1>
            <p className="text-xs text-[#878074]">
              Access your private wedding schedule, payment milestones and planner messages
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
              <label className="block text-xs font-semibold text-[#524E48] mb-1.5" htmlFor="client-email-input">
                Your Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="client-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-[#524E48]" htmlFor="client-password-input">
                  Password
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="client-password-input"
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
                  <span>Enter Couple Sanctuary</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#C4A46D]" />
                </>
              )}
            </button>
          </form>

          {/* Invitation Sign Up Notice */}
          <div className="mt-6 pt-5 border-t border-[#E8E2D9] text-center space-y-3">
            <div className="p-3 bg-[#FAF8F5] border border-[#E2DBD0] rounded-lg text-left">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-[#292E27]">Have an Invitation Code?</span>
                <Link
                  to="/customer/signup"
                  className="text-xs font-semibold text-[#852C1F] hover:underline"
                >
                  Activate Portal &rarr;
                </Link>
              </div>
              <p className="text-[11px] text-[#878074] mt-0.5">
                First time here? Register with the invitation code provided in your welcome package.
              </p>
            </div>

            <p className="text-[11px] text-[#878074]">
              Staff member?{" "}
              <Link to="/login" className="font-medium text-[#292E27] underline hover:text-[#852C1F]">
                Agency Team Sign In
              </Link>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 border-t border-[#E8E2D9] text-center text-[11px] text-[#878074]">
        MANDAP &middot; The Royal Knot Bespoke Wedding Portal &middot; Private Client Sanctuary
      </footer>
    </div>
  )
}
