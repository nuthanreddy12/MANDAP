import {
  FolderKanban,
  FileCheck2,
  ListRestart,
  ClockAlert,
  CreditCard,
  TrendingUp,
} from 'lucide-react'
import { BotanicalDivider } from './FloralFlourish'

export function FeaturesSection() {
  const features = [
    {
      title: 'Centralized Wedding Workspaces',
      icon: FolderKanban,
      description:
        'A dedicated operations hub for each couple. Consolidate palace contracts, guest counts, ceremony schedules, and team assignments into one living workspace.',
    },
    {
      title: 'Vendor and Quotation Tracking',
      icon: FileCheck2,
      description:
        'Maintain a single source of truth for all artisan bids. Review inclusions, negotiate terms, and lock approved rate cards with clear audit histories.',
    },
    {
      title: 'Reusable Wedding Task Plans',
      icon: ListRestart,
      description:
        'Deploy battle-tested production templates tailored for 3-day and 5-day Rajasthani palace celebrations, complete with statutory clearance deadlines.',
    },
    {
      title: 'Event Timelines & Incident Reporting',
      icon: ClockAlert,
      description:
        'Keep ground crews aligned with precise cue sheets. Flag unexpected weather or delay incidents instantly to pivot backup palace courtyards without panic.',
    },
    {
      title: 'Invoice and Payment Tracking',
      icon: CreditCard,
      description:
        'Never miss an artisan advance or milestone payout. Track bank details, GST compliance, and Section 194C TDS tax deductions automatically.',
    },
    {
      title: 'Wedding Profitability Overview',
      icon: TrendingUp,
      description:
        'View real-time agency commissions, direct outlays, and budget realizations across each celebration to safeguard margins and agency cash flow.',
    },
  ]

  return (
    <section id="features" className="py-20 lg:py-32 bg-ivory-warm/60 border-t border-warm-stone/60 relative">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Precision Architecture
          </span>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-ink tracking-tight">
            Key Platform Capabilities
          </h2>
          <div className="flex justify-center pt-1">
            <BotanicalDivider className="w-28 text-bronze" />
          </div>
          <p className="text-sm sm:text-base text-ink-muted leading-relaxed pt-2">
            Engineered to handle high-stakes operational variables with calm authority.
          </p>
        </div>

        {/* Features List with 2-Column Editorial Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-10">
          {features.map((feat) => {
            const Icon = feat.icon
            return (
              <div
                key={feat.title}
                className="p-8 bg-ivory-card border border-warm-stone rounded-xl hover:border-bronze/60 transition-all duration-300 shadow-[0_4px_16px_rgba(44,37,35,0.03)] flex items-start gap-5"
              >
                <div className="w-12 h-12 rounded-lg bg-warm-stone-light/60 border border-bronze/30 text-bronze flex items-center justify-center shrink-0">
                  <Icon className="w-6 h-6" aria-hidden="true" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-serif text-xl font-bold text-ink">
                    {feat.title}
                  </h3>
                  <p className="text-sm text-ink-muted leading-relaxed font-sans">
                    {feat.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
