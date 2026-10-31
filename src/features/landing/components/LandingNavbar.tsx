import { useState, useEffect } from 'react'
import { Menu, X } from 'lucide-react'

export function LandingNavbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 40)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { label: 'ABOUT', href: '#about' },
    { label: 'HOW IT WORKS', href: '#how-it-works' },
    { label: 'CONTACT', href: '#contact' },
  ]

  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    setMobileMenuOpen(false)
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-ink/80 backdrop-blur-md border-b border-white/10 py-3.5 shadow-md'
          : 'bg-gradient-to-b from-ink/60 via-ink/20 to-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-12 flex items-center justify-between">
        {/* Brand Title & Subtitle */}
        <a
          href="#hero"
          onClick={(e) => handleScrollTo(e, '#hero')}
          className="flex items-center gap-3 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass rounded-xs"
        >
          <img
            src="/image_5.png"
            alt="MANDAP Brand Mark"
            width={34}
            height={44}
            className="h-9 md:h-10 w-auto object-contain rounded-xs drop-shadow-sm shrink-0 transition-transform duration-200 group-hover:scale-105"
          />
          <div className="flex flex-col items-start">
            <span className="font-serif text-2xl md:text-3xl font-bold tracking-[0.2em] text-white leading-none group-hover:text-antique-brass-light transition-colors">
              MANDAP
            </span>
            <span className="text-[9px] uppercase tracking-[0.28em] text-white/80 font-medium mt-1">
              ROYAL WEDDING ATELIER
            </span>
          </div>
        </a>

        {/* Cleanly Spaced Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 lg:gap-10" aria-label="Landing Navigation">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={(e) => handleScrollTo(e, link.href)}
              className="text-xs uppercase tracking-[0.2em] font-medium text-white/85 hover:text-white transition-colors relative py-1 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-0 after:h-[1.5px] after:bg-white hover:after:w-full after:transition-all"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Swapped Action: Explore Mandap Button */}
        <div className="hidden md:flex items-center">
          <a
            href="#about"
            onClick={(e) => handleScrollTo(e, '#about')}
            className="rounded-full px-6 py-2.5 text-xs font-semibold uppercase tracking-widest bg-white/10 hover:bg-white text-white hover:text-ink border border-white/25 hover:border-white shadow-md hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5 cursor-pointer backdrop-blur-sm"
          >
            Explore Mandap
          </a>
        </div>

        {/* Mobile Hamburger Toggle */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-expanded={mobileMenuOpen}
          aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
          className="md:hidden min-w-[44px] min-h-[44px] flex items-center justify-center text-white rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-antique-brass"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-ink/95 backdrop-blur-xl border-b border-white/10 px-6 py-6 space-y-4 shadow-2xl animate-in fade-in slide-in-from-top-4 duration-200">
          <nav className="flex flex-col space-y-3" aria-label="Mobile Navigation">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="text-sm uppercase tracking-[0.2em] font-medium text-white/80 hover:text-white py-2 border-b border-white/10"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="pt-2">
            <a
              href="#about"
              onClick={(e) => handleScrollTo(e, '#about')}
              className="w-full block rounded-full px-6 py-3 text-xs font-semibold uppercase tracking-widest bg-white/10 hover:bg-white text-white hover:text-ink border border-white/25 text-center transition-all cursor-pointer backdrop-blur-sm"
            >
              Explore Mandap
            </a>
          </div>
        </div>
      )}
    </header>
  )
}
