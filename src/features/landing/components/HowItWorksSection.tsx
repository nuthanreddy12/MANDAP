import { BotanicalDivider } from './FloralFlourish'

export function HowItWorksSection() {
  const steps = [
    {
      step: '01',
      title: 'Create a Wedding Workspace',
      description:
        'Initialize a dedicated dossier for the celebration. Set up palace venues, dates, guest counts, and assign the lead producer.',
    },
    {
      step: '02',
      title: 'Coordinate Vendors, Tasks and Schedules',
      description:
        'Evaluate artisan quote matrices, assign critical compliance checklists, and establish the minute-by-minute ceremony run-sheets.',
    },
    {
      step: '03',
      title: 'Track Finances and Manage the Celebration',
      description:
        'Execute advance releases with automated tax deductions, monitor live ceremony radio cues, and analyze final agency profitability.',
    },
  ]

  return (
    <section id="how-it-works" className="py-20 lg:py-32 bg-ivory border-t border-warm-stone/60 relative">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Simple, Thoughtful Workflow
          </span>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-ink tracking-tight">
            How Mandap Works
          </h2>
          <div className="flex justify-center pt-1">
            <BotanicalDivider className="w-28 text-bronze" />
          </div>
          <p className="text-sm sm:text-base text-ink-muted leading-relaxed pt-2">
            A three-phase approach from intake to the final royal reception.
          </p>
        </div>

        {/* 3 Steps in Horizontal Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12 relative">
          {steps.map((item, idx) => (
            <div
              key={item.step}
              className="relative p-8 bg-ivory-card border border-warm-stone rounded-xl space-y-4 shadow-[0_4px_16px_rgba(44,37,35,0.03)] hover:border-bronze/60 transition-all duration-300"
            >
              <div className="flex items-center justify-between">
                <span className="font-serif text-4xl sm:text-5xl font-bold text-bronze">
                  {item.step}
                </span>
                <span className="text-[10px] uppercase tracking-wider font-semibold text-ink-muted bg-warm-stone-light/80 px-2.5 py-1 rounded-md border border-warm-stone">
                  Phase {idx + 1}
                </span>
              </div>

              <h3 className="font-serif text-xl font-bold text-ink pt-2">
                {item.title}
              </h3>

              <p className="text-xs sm:text-sm text-ink-muted leading-relaxed font-sans">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
