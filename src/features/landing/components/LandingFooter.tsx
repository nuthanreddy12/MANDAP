import { Link } from 'react-router-dom'
import { MapPin, Mail, Phone, ArrowUpRight } from 'lucide-react'
import { ROUTES } from '@/routes/routePaths'

export function LandingFooter() {
  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <footer id="contact" className="bg-ivory-warm/80 border-t border-warm-stone text-ink">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 py-16 lg:py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-12 lg:gap-8">
          {/* Brand & Vision (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <img
                src="/image_5.png"
                alt="MANDAP Royal Wedding Atelier Brand Mark"
                width={36}
                height={46}
                className="h-10 w-auto object-contain rounded-xs drop-shadow-xs"
              />
              <span className="font-serif text-2xl font-bold tracking-wide text-ink">
                MANDAP
              </span>
            </div>

            <p className="text-xs sm:text-sm text-ink-muted max-w-sm leading-relaxed">
              The premier operations platform for luxury wedding planning agencies managing
              multi-day royal celebrations across Jaipur, Udaipur, and Rajasthan.
            </p>

            <div className="pt-2">
              <span className="text-[11px] uppercase tracking-widest text-bronze font-semibold block">
                Atelier Hubs
              </span>
              <p className="text-xs text-ink-muted mt-1">
                Lake Palace Road, Udaipur • Sawai Ram Singh Road, Jaipur
              </p>
            </div>
          </div>

          {/* Quick Links (3 cols) */}
          <div className="lg:col-span-3 space-y-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-ink block">
              Platform Navigation
            </span>
            <ul className="space-y-2 text-xs text-ink-muted">
              <li>
                <a
                  href="#hero"
                  onClick={(e) => handleScrollTo(e, '#hero')}
                  className="hover:text-ink transition-colors"
                >
                  Home
                </a>
              </li>
              <li>
                <a
                  href="#about"
                  onClick={(e) => handleScrollTo(e, '#about')}
                  className="hover:text-ink transition-colors"
                >
                  About Mandap
                </a>
              </li>
              <li>
                <a
                  href="#how-it-works"
                  onClick={(e) => handleScrollTo(e, '#how-it-works')}
                  className="hover:text-ink transition-colors"
                >
                  How It Works
                </a>
              </li>
              <li>
                <Link
                  to={ROUTES.DASHBOARD}
                  className="font-medium text-bronze hover:text-ink inline-flex items-center gap-1"
                >
                  <span>Open Management Dashboard</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Details (4 cols) */}
          <div className="lg:col-span-4 space-y-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-ink block">
              Agency Concierge
            </span>
            <div className="space-y-2.5 text-xs text-ink-muted">
              <div className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-bronze shrink-0 mt-0.5" aria-hidden="true" />
                <span>The Royal Pavilion Atelier, Lake Palace Road, Udaipur, Rajasthan 313001</span>
              </div>
              <div className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-bronze shrink-0" aria-hidden="true" />
                <span>concierge@mandapoperations.in</span>
              </div>
              <div className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-bronze shrink-0" aria-hidden="true" />
                <span>+91 294 242 8800 (Mon to Sat, 9:00 AM to 7:00 PM IST)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-12 mt-12 border-t border-warm-stone/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-ink-faint">
          <p>© 2026 MANDAP Wedding Operations Platform. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>Modern Heritage House Architecture</span>
            <Link to={ROUTES.DASHBOARD} className="text-bronze hover:underline">
              Enter Operations Desk
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
