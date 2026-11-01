import React, { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { Lock, Mail, User, KeyRound, ArrowRight, AlertCircle, Sparkles, CheckCircle2 } from "lucide-react"

export const CustomerSignupPage: React.FC = () => {
  const navigate = useNavigate()

  const [clientName, setClientName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [invitationCode, setInvitationCode] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!clientName || !email || !password) {
      setErrorMessage("Please complete all required fields")
      return
    }

    setSubmitting(true)
    setErrorMessage(null)

    try {
      const res = await fetch("/api/v1/customer/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_name: clientName.trim(),
          email: email.trim().toLowerCase(),
          password,
          invitation_code: invitationCode.trim() || undefined,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        setErrorMessage(
          data.detail || "Unable to register. Please verify your invitation code or email on file."
        )
        return
      }

      if (data.token) {
        localStorage.setItem("mandap_customer_token", data.token)
        localStorage.setItem("mandap_customer_user", JSON.stringify(data.user))
        localStorage.setItem("mandap_customer_wedding_id", data.wedding_id)
        localStorage.removeItem("mandap_auth_token")
        setSuccessMessage("Account created successfully. Taking you to your wedding sanctuary...")
        setTimeout(() => {
          navigate("/customer/dashboard", { replace: true })
        }, 1000)
      } else {
        setSuccessMessage("Account created successfully. Please sign in with your private password.")
        setTimeout(() => {
          navigate("/customer/login", { replace: true })
        }, 1200)
      }
    } catch {
      setErrorMessage("Connection failed. Please check your network and try again.")
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
            Client Registration
          </span>
        </Link>
        <Link
          to="/customer/login"
          className="text-xs font-medium text-[#71717A] hover:text-[#541424] transition-colors"
        >
          Already registered? Sign In
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md bg-white border border-[#E8E2D9] rounded-2xl shadow-sm p-8">
          <div className="mb-8 text-center">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF8F5] border border-[#E8E2D9] text-[#B8860B] text-xs font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Invitation-Only Access</span>
            </div>
            <h1 className="font-serif text-2xl text-[#1A1A1A] mb-2 font-normal">
              Activate Couple Portal
            </h1>
            <p className="text-xs text-[#71717A]">
              Connect your account to your palace celebration file using the invitation code issued by your producer.
            </p>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-start gap-3">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
              <span>{successMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#4A4A4A] mb-1.5 uppercase tracking-wider">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Priya Mehra"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#FAF8F5] border border-[#E8E2D9] rounded-xl text-xs text-[#1A1A1A] focus:outline-none focus:ring-1 focus:ring-[#541424] focus:border-[#541424] transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#4A4A4A] mb-1.5 uppercase tracking-wider">
                Email Address
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
                  placeholder="Create a strong password"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#FAF8F5] border border-[#E8E2D9] rounded-xl text-xs text-[#1A1A1A] focus:outline-none focus:ring-1 focus:ring-[#541424] focus:border-[#541424] transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#4A4A4A] mb-1.5 uppercase tracking-wider">
                Agency Invitation Code
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={invitationCode}
                  onChange={(e) => setInvitationCode(e.target.value)}
                  placeholder="ROYAL-MK-2026"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#FAF8F5] border border-[#E8E2D9] rounded-xl text-xs text-[#1A1A1A] uppercase focus:outline-none focus:ring-1 focus:ring-[#541424] focus:border-[#541424] transition-all"
                />
              </div>
              <p className="text-[11px] text-[#A1A1AA] mt-1">
                Found on your agency welcome letter or digital invitation.
              </p>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 py-3 px-4 rounded-xl text-xs font-medium text-white bg-[#541424] hover:bg-[#6B1728] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#541424] transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 cursor-pointer"
            >
              {submitting ? (
                <span>Registering celebration...</span>
              ) : (
                <>
                  <span>Activate Couple Sanctuary</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[#F0EBE1] text-center">
            <p className="text-xs text-[#71717A]">
              Already activated?{" "}
              <Link
                to="/customer/login"
                className="text-[#541424] font-medium hover:underline inline-flex items-center gap-1"
              >
                Sign in to Couple Sanctuary
                <ArrowRight className="w-3 h-3" />
              </Link>
            </p>
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
