import { BotanicalDivider } from './FloralFlourish'
import { CheckCircle2 } from 'lucide-react'

export function AboutSection() {
  const pillars = [
    {
      title: 'Built for High-Touch Hospitality',
      description:
        'Designed specifically for wedding producers managing multi-day celebrations, VIP arrivals, and heritage palace curfews.',
    },
    {
      title: 'Artisan & Vendor Transparency',
      description:
        'Compare shehnai ensembles, floral architects, and safa guild bids with line-by-line clarity and milestone escrow terms.',
    },
    {
      title: 'Flawless Ceremony Precision',
      description:
        'Minute-by-minute run-sheets ensure Baraat processions, Varmala fireworks, and sacred Vedic Pheras unfold without a hitch.',
    },
  ]

  return (
    <section id="about" className="pt-12 pb-20 lg:pt-16 lg:pb-32 bg-ivory relative">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Our Purpose & Heritage
          </span>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-ink tracking-tight">
            Elevating the Art of Royal Celebrations
          </h2>
          <div className="flex justify-center pt-1">
            <BotanicalDivider className="w-28 text-bronze" />
          </div>
          <p className="text-sm sm:text-base text-ink-muted leading-relaxed pt-2">
            Mandap brings clarity, calm, and sovereign precision to wedding planners orchestrating
            extraordinary milestones in Rajasthan's most storied palaces.
          </p>
        </div>

        {/* Editorial Story Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Left: Editorial Image Composition */}
          <div className="lg:col-span-5 order-2 lg:order-1 relative">
            <div className="relative mx-auto max-w-sm lg:max-w-none">
              <div className="rounded-xl overflow-hidden border border-warm-stone shadow-[0_8px_24px_rgba(44,37,35,0.06)] bg-ivory aspect-[4/5]">
                <img
                  src="https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=1000&q=80"
                  alt="Couple embracing at a royal wedding celebration"
                  width={500}
                  height={625}
                  className="w-full h-full object-cover object-center"
                  loading="lazy"
                />
              </div>

              {/* Offset secondary photo */}
              <div className="hidden sm:block absolute -bottom-8 -right-8 w-48 h-48 rounded-lg overflow-hidden border-4 border-ivory shadow-[0_12px_28px_rgba(44,37,35,0.1)]">
                <img
                  src="https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&w=600&q=80"
                  alt="Traditional royal wedding floral arrangement and marigold garlands"
                  width={240}
                  height={240}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
            </div>
          </div>

          {/* Right: Editorial Narrative & Pillars */}
          <div className="lg:col-span-7 order-1 lg:order-2 space-y-6">
            <h3 className="font-serif text-2xl sm:text-3xl font-bold text-ink leading-snug">
              Behind every grand royal procession is an intricate web of logistics.
            </h3>

            <p className="text-sm sm:text-base text-ink-muted leading-relaxed font-sans">
              Royal weddings across Rambagh Palace, Jagmandir Island, and Umaid Bhawan involve
              hundreds of artisans, statutory heritage clearances, boat transits, and delicate family
              protocols. Traditional spreadsheets fail when live production demands real-time
              synchronization.
            </p>

            <p className="text-sm sm:text-base text-ink-muted leading-relaxed font-sans">
              Mandap was created to give luxury wedding producers a dignified, centralized command desk.
              We replace fragmented messages and paper files with structured workspaces that unite
              couples, vendors, venue managers, and on-ground coordinators.
            </p>

            {/* Feature List */}
            <div className="space-y-4 pt-4 border-t border-warm-stone/80">
              {pillars.map((pillar) => (
                <div key={pillar.title} className="flex items-start gap-3">
                  <div className="mt-1 w-5 h-5 rounded-full bg-bronze-light/50 text-bronze flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-ink">{pillar.title}</h4>
                    <p className="text-xs text-ink-muted mt-0.5 leading-relaxed">{pillar.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
