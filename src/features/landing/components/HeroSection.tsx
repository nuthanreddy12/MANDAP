import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ROUTES } from '@/routes/routePaths'

export function HeroSection() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col justify-center items-center text-center px-6 pt-36 pb-32 md:pt-44 md:pb-40 overflow-hidden bg-ink"
    >
      {/* Immersive High-Resolution Wedding Photography Background */}
      <img
        src="https://images.unsplash.com/photo-1537633552985-df8429e8048b?auto=format&fit=crop&w=2000&q=85"
        alt="Wedding couple holding hands in golden sunlight amidst pampas grass"
        width={2000}
        height={1333}
        className="absolute inset-0 w-full h-full object-cover object-center scale-105 animate-in fade-in duration-700"
        fetchPriority="high"
      />

      {/* Dark Vignette & Multi-Stage Gradient Overlay for Pristine Contrast */}
      <div
        className="absolute inset-0 bg-gradient-to-b from-ink/75 via-ink/40 to-ink/80 mix-blend-multiply"
        aria-hidden="true"
      />
      <div
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(44,37,35,0.15)_0%,rgba(44,37,35,0.85)_100%)] pointer-events-none"
        aria-hidden="true"
      />

      {/* Centered Editorial Typography & Call-to-Action */}
      <div className="relative z-10 max-w-5xl mx-auto space-y-6 md:space-y-8">
        {/* Subtle Decorative Atelier Marker */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white/90 text-[10px] md:text-[11px] uppercase tracking-[0.25em] font-medium shadow-sm">
          <span>JAIPUR & UDAIPUR ATELIER</span>
        </div>

        {/* Main Heading: Serif, Uppercase, Elegant Tracking */}
        <h1 className="font-serif text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-normal text-white uppercase tracking-[0.16em] sm:tracking-[0.18em] leading-[1.18] sm:leading-[1.15] drop-shadow-md">
          TURNING YOUR WEDDING DREAMS INTO ULTIMATE REALITY
        </h1>

        {/* Subtitle */}
        <p className="font-sans text-sm sm:text-base md:text-lg text-white/90 font-light tracking-wide max-w-2xl mx-auto leading-relaxed drop-shadow-sm">
          Crafting every detail to shape your perfect wedding day.
        </p>

        {/* Primary Call-to-Action: Main Focus Button */}
        <div className="pt-4 flex justify-center">
          <Link
            to={ROUTES.DASHBOARD}
            className="group inline-flex items-center gap-3 rounded-full px-10 py-4.5 bg-white text-ink hover:bg-white/95 text-xs sm:text-sm font-semibold uppercase tracking-[0.2em] shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.35)] transition-all duration-300 transform hover:-translate-y-1 cursor-pointer focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-antique-brass"
          >
            <span>Go to Dashboard</span>
            <ArrowRight className="w-4 h-4 text-ink transform group-hover:translate-x-1.5 transition-transform" />
          </Link>
        </div>
      </div>

      {/* Smooth Curved Bottom Transition into Subsequent Ivory Page Section */}
      <div className="absolute -bottom-1 left-0 right-0 w-full overflow-hidden leading-none z-20 pointer-events-none">
        <svg
          viewBox="0 0 1440 90"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="none"
          className="w-full h-12 sm:h-16 md:h-20 lg:h-24 text-ivory fill-current block"
        >
          {/* Symmetrical gentle arched curve rising in the center */}
          <path d="M 0,60 Q 720,0 1440,60 L 1440,90 L 0,90 Z" />
        </svg>
      </div>
    </section>
  )
}
