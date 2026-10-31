import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ROUTES } from '@/routes/routePaths'
import { Button } from '@/components/ui/Button'
import { FloralFlourish } from './FloralFlourish'

export function CtaSection() {
  return (
    <section className="py-20 lg:py-28 bg-ink text-ivory relative overflow-hidden">
      {/* Decorative floral watermark */}
      <div className="absolute -top-12 -left-12 opacity-10 pointer-events-none">
        <FloralFlourish className="w-64 h-64 text-bronze" />
      </div>
      <div className="absolute -bottom-12 -right-12 opacity-10 pointer-events-none rotate-180">
        <FloralFlourish className="w-64 h-64 text-bronze" />
      </div>

      <div className="max-w-4xl mx-auto px-6 text-center relative z-10 space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-ivory/10 border border-bronze/30 rounded-md text-[11px] uppercase tracking-widest text-antique-brass-light font-medium">
          <span>Start Producing Sovereign Celebrations</span>
        </div>

        <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-ivory tracking-tight leading-tight">
          Bring Every Wedding Detail Together.
        </h2>

        <p className="text-sm sm:text-base text-warm-stone-light max-w-xl mx-auto leading-relaxed font-sans font-light">
          Say goodbye to fragmented chats, lost vendor quotes, and paper run-sheets.
          Experience the quiet confidence of a unified luxury operations platform.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to={ROUTES.DASHBOARD}>
            <Button
              variant="outline"
              size="lg"
              rightIcon={<ArrowRight className="w-4 h-4" />}
              className="bg-bronze text-ivory hover:bg-bronze-dark border-bronze shadow-md px-8 py-3.5 font-semibold"
            >
              Enter Mandap Dashboard
            </Button>
          </Link>
        </div>

        <p className="text-[11px] text-warm-stone-dark pt-2">
          Preloaded with Jaipur and Udaipur palace operational files.
        </p>
      </div>
    </section>
  )
}
