import { Link } from 'react-router-dom'
import {
  CalendarDays,
  Handshake,
  Scale,
  ListTodo,
  Clock,
  Receipt,
  ArrowRight,
} from 'lucide-react'
import { ROUTES } from '@/routes/routePaths'
import { Card } from '@/components/ui/Card'
import { BotanicalDivider } from './FloralFlourish'

export function ServicesSection() {
  const services = [
    {
      title: 'Wedding Management',
      icon: CalendarDays,
      path: ROUTES.WEDDINGS,
      description:
        'Comprehensive multi-day dossiers tracking couple visions, palace venue allocations, guest counts, and lead producer assignments.',
      tag: 'Palace Portfolios',
    },
    {
      title: 'Vendor Coordination',
      icon: Handshake,
      path: ROUTES.VENDORS,
      description:
        'Direct relationship management with shehnai collectives, safa tying guilds, royal catering masters, and cinecraft teams.',
      tag: 'Artisan Networks',
    },
    {
      title: 'Quote Comparison',
      icon: Scale,
      path: ROUTES.QUOTES,
      description:
        'Line-by-line bid evaluations comparing vendor inclusions, advance payment schedules, and technical requirements side by side.',
      tag: 'Procurement Matrices',
    },
    {
      title: 'Task Management',
      icon: ListTodo,
      path: ROUTES.TASKS,
      description:
        'Time-sensitive production checklists ensuring police sound permits, ASI drone clearances, and fire NOCs are secured on schedule.',
      tag: 'Critical Path',
    },
    {
      title: 'Event-Day Scheduling',
      icon: Clock,
      path: ROUTES.RUN_OF_SHOW,
      description:
        'Minute-by-minute ceremony cue sheets synchronizing Baraat horses, Varmala flower drops, and Vedic rituals with on-ground radio cues.',
      tag: 'Live Run-Sheets',
    },
    {
      title: 'Finance Management',
      icon: Receipt,
      path: ROUTES.FINANCE,
      description:
        'Vendor advance releases, GST invoice reconciliation, and Section 194C TDS audits to ensure 100% statutory tax compliance.',
      tag: 'Treasury & Audit',
    },
  ]

  return (
    <section id="services" className="py-20 lg:py-32 bg-ivory relative">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Operational Capabilities
          </span>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-ink tracking-tight">
            What Mandap Helps You Manage
          </h2>
          <div className="flex justify-center pt-1">
            <BotanicalDivider className="w-28 text-bronze" />
          </div>
          <p className="text-sm sm:text-base text-ink-muted leading-relaxed pt-2">
            Every critical dimension of royal wedding logistics consolidated into a single,
            refined workspace.
          </p>
        </div>

        {/* 6 Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service) => {
            const Icon = service.icon
            return (
              <Card
                key={service.title}
                variant="default"
                className="group p-7 bg-ivory-card hover:bg-ivory-warm/40 border-warm-stone hover:border-bronze/60 transition-all duration-300 flex flex-col justify-between shadow-[0_4px_16px_rgba(44,37,35,0.03)] hover:shadow-[0_8px_24px_rgba(44,37,35,0.06)] rounded-xl"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-12 h-12 rounded-lg bg-warm-stone-light/60 group-hover:bg-bronze-light/60 text-ink group-hover:text-bronze flex items-center justify-center transition-colors">
                      <Icon className="w-6 h-6" aria-hidden="true" />
                    </div>
                    <span className="text-[10px] uppercase tracking-wider font-semibold text-bronze bg-bronze-light/40 px-2.5 py-1 rounded-md border border-bronze/30">
                      {service.tag}
                    </span>
                  </div>

                  <h3 className="font-serif text-xl font-bold text-ink group-hover:text-ink transition-colors">
                    {service.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-ink-muted leading-relaxed mt-2.5">
                    {service.description}
                  </p>
                </div>

                <div className="pt-6 mt-6 border-t border-warm-stone/60">
                  <Link
                    to={service.path}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-bronze hover:text-ink transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-antique-brass rounded-xs"
                  >
                    <span>Inspect module in Dashboard</span>
                    <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
