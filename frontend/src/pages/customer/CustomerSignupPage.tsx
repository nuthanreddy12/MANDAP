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
      }

      setSuccessMessage("Account created successfully. Taking you to your wedding dashboard...")
      setTimeout(() => {
        navigate("/customer/dashboard", { replace: true })
      }, 1200)
    } catch (err: unknown) {
      setErrorMessage("Connection failed. Please check your network and try again.")
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
            Client Portal Registration
          </span>
        </div>
        <Link
          to="/customer/login"
          className="text-xs font-medium text-[#878074] hover:text-[#292E27] transition-colors"
        >
          Already registered? Sign In
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
              Activate Couple Portal
            </h1>
            <p className="text-xs text-[#878074]">
              Enter your invitation code or registered contract email to access your wedding space
            </p>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3 rounded-md bg-[#AE5142]/10 border border-[#AE5142]/30 flex items-start gap-2.5 text-xs text-[#AE5142] leading-relaxed">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="mb-5 p-3 rounded-md bg-[#3F5A36]/10 border border-[#3F5A36]/30 flex items-start gap-2.5 text-xs text-[#3F5A36] leading-relaxed">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{successMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#524E48] mb-1.5" htmlFor="client-name-input">
                Your Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="client-name-input"
                  type="text"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Priya Mehra"
                  required
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#524E48] mb-1.5" htmlFor="client-signup-email">
                Email Address on Contract
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="client-signup-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="priya.mehra@gmail.com"
                  required
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#524E48] mb-1.5" htmlFor="client-signup-password">
                Create Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="client-signup-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  required
                  minLength={6}
                  className="w-full text-xs bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-[#524E48]" htmlFor="invitation-code-input">
                  Invitation Code
                </label>
                <span className="text-[11px] text-[#878074]">Example: ROYAL-MK-2026</span>
              </div>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-[#878074] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="invitation-code-input"
                  type="text"
                  value={invitationCode}
                  onChange={(e) => setInvitationCode(e.target.value.toUpperCase())}
                  placeholder="ROYAL-MK-2026"
                  className="w-full text-xs uppercase tracking-wider bg-[#FBFAF7] border border-[#E2DBD0] rounded-md pl-9 pr-3 py-2 text-[#292E27] placeholder:text-[#968F83] focus:outline-none focus:border-[#C4A46D] focus:ring-1 focus:ring-[#C4A46D] transition-colors"
                />
              </div>
              <p className="text-[11px] text-[#878074] mt-1">
                Provided in your agency onboarding email or welcome brochure.
              </p>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 h-10 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center justify-center gap-2 shadow-sm disabled:opacity-60 cursor-pointer"
            >
              {submitting ? (
                <span>Registering Portal...</span>
              ) : (
                <>
                  <span>Activate Couple Portal</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#C4A46D]" />
                </>
              )}
            </button>
          </form>

          {/* Privacy Note */}
          <div className="mt-6 pt-5 border-t border-[#E8E2D9] text-center">
            <p className="text-[11px] text-[#878074] leading-relaxed">
              Every couple portal is private and isolated. Staff roles cannot be created here. Registration is verified against your agency contract.
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
