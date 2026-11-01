import React, { useState, useEffect } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import { Lock, Mail, ArrowRight, AlertCircle, Sparkles, ShieldCheck } from "lucide-react"

export const CustomerLoginPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/customer/dashboard"

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Redirect if already logged in with active customer token
  useEffect(() => {
    const localToken = localStorage.getItem("mandap_customer_token")
    if (localToken) {
      navigate("/customer/dashboard", { replace: true })
    }
  }, [navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setErrorMessage("Please enter both email and password")
      return
    }

    setSubmitting(true)
    setErrorMessage(null)

    try {
      const res = await fetch("/api/v1/customer/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      })

      if (res.ok) {
        const data = await res.json()
        if (data.token) {
          localStorage.setItem("mandap_customer_token", data.token)
          localStorage.setItem("mandap_customer_user", JSON.stringify(data.user))
          localStorage.setItem("mandap_customer_wedding_id", data.wedding_id)
          localStorage.removeItem("mandap_auth_token")
          navigate(from, { replace: true })
          return
        } else {
          setErrorMessage("Unable to obtain authorization token. Please contact your wedding planner.")
          return
        }
      }

      const errData = await res.json().catch(() => ({}))
      const detail = errData.detail || ""
      if (
        res.status === 401 ||
        detail.toLowerCase().includes("couldn't find") ||
        detail.toLowerCase().includes("could not find") ||
        detail.toLowerCase().includes("not registered")
      ) {
        setErrorMessage(
          "We could not find an account associated with this email. Check your details or contact your wedding planner."
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
    } catch {
      setErrorMessage(
        "Unable to connect to service. Please verify your network and try again."
      )
    } finally {
      setSubmitting(false)
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
          <span className="text-xs uppercase tracking-widest text-[#B8860B] pl-2 border-l border-[#E8E2D9]">
            Client Couple Sanctuary
          </span>
        </Link>
        <Link
          to="/login"
          className="text-xs font-medium text-[#71717A] hover:text-[#541424] transition-colors"
        >
          Agency Planner Login
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md bg-white border border-[#E8E2D9] rounded-2xl shadow-sm p-8">
          <div className="mb-8 text-center">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF8F5] border border-[#E8E2D9] text-[#B8860B] text-xs font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Private Client Sanctuary</span>
            </div>
            <h1 className="font-serif text-2xl text-[#1A1A1A] mb-2 font-normal">
              Welcome to Your Celebration
            </h1>
            <p className="text-xs text-[#71717A]">
              Review your palace itinerary, confirmed guest services, payment status, and concierge requests.
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
                Registered Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="priya.mehra@gmail.com"
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
                  placeholder="Enter your private password"
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
                <span>Unlocking sanctuary...</span>
              ) : (
                <>
                  <span>Enter Wedding Sanctuary</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          {/* Demo Bypass / Quick Access for Local Development */}
          <div className="mt-6 pt-5 border-t border-[#F0EBE1] space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#B8860B] uppercase tracking-wider flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Demo Access / Dev Bypass
              </span>
              <span className="text-[10px] text-[#A1A1AA] bg-[#FAF8F5] px-1.5 py-0.5 rounded border border-[#E8E2D9]">
                Auto-mapped
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setEmail('charanraghu38@gmail.com')
                  setPassword('demo1234')
                }}
                className="p-2 text-left bg-[#FAF8F5] hover:bg-[#F3EFEA] border border-[#E8E2D9] rounded-xl text-xs transition-colors cursor-pointer"
              >
                <span className="block font-medium text-[#1A1A1A]">Charan Raghu</span>
                <span className="block text-[10px] text-[#71717A] truncate">charanraghu38@gmail.com</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setEmail('priya.mehra@gmail.com')
                  setPassword('demo1234')
                }}
                className="p-2 text-left bg-[#FAF8F5] hover:bg-[#F3EFEA] border border-[#E8E2D9] rounded-xl text-xs transition-colors cursor-pointer"
              >
                <span className="block font-medium text-[#1A1A1A]">Priya Mehra</span>
                <span className="block text-[10px] text-[#71717A] truncate">priya.mehra@gmail.com</span>
              </button>
            </div>
          </div>
          </form>

          <div className="mt-8 pt-6 border-t border-[#F0EBE1] flex flex-col gap-3 text-center">
            <p className="text-xs text-[#71717A]">
              Have an agency invitation code?{" "}
              <Link
                to="/customer/signup"
                className="text-[#541424] font-medium hover:underline inline-flex items-center gap-1"
              >
                Create Couple Account
                <ArrowRight className="w-3 h-3" />
              </Link>
            </p>
            <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#A1A1AA] pt-2">
              <ShieldCheck className="w-3.5 h-3.5 text-[#B8860B]" />
              <span>Strict couple privacy and verified guest confidentiality</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 text-center text-[11px] text-[#A1A1AA] border-t border-[#E8E2D9] bg-white">
        MANDAP Royal Wedding Atelier &copy; 2026
      </footer>
    </div>
  )
}
