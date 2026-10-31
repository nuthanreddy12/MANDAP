import { useState } from 'react'
import { Plus, Calendar, MapPin } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface Enquiry {
  id: string
  client: string
  hometown: string
  targetVenues: string
  estimatedDates: string
  guestCount: number
  budgetRange: string
  stage: 'New Inquiry' | 'Palace Availability Check' | 'Proposal Sent'
  receivedAt: string
}

const MOCK_ENQUIRIES: Enquiry[] = [
  {
    id: 'enq-101',
    client: 'Suhani Piramal & Vihaan Jindal',
    hometown: 'Mumbai',
    targetVenues: 'The Oberoi Udaivilas or Jagmandir Island Palace',
    estimatedDates: 'Mid November 2026',
    guestCount: 350,
    budgetRange: '₹5.5 Cr to ₹7 Cr',
    stage: 'New Inquiry',
    receivedAt: 'Today, 11:30 AM',
  },
  {
    id: 'enq-102',
    client: 'Kritika Birla & Samar Singhania',
    hometown: 'London / New Delhi',
    targetVenues: 'Rambagh Palace or City Palace, Jaipur',
    estimatedDates: 'December 2026',
    guestCount: 500,
    budgetRange: '₹8 Cr to ₹10 Cr',
    stage: 'Palace Availability Check',
    receivedAt: 'Yesterday',
  },
  {
    id: 'enq-103',
    client: 'Nandini Ruia & Aaryaman Goenka',
    hometown: 'Kolkata',
    targetVenues: 'Taj Lake Palace, Udaipur',
    estimatedDates: 'February 2027',
    guestCount: 220,
    budgetRange: '₹4 Cr to ₹5 Cr',
    stage: 'Proposal Sent',
    receivedAt: '3 days ago',
  },
]

export function EnquiriesPage() {
  const [enquiries] = useState<Enquiry[]>(MOCK_ENQUIRIES)

  const stageVariant = (stage: Enquiry['stage']) => {
    switch (stage) {
      case 'New Inquiry':
        return 'danger'
      case 'Palace Availability Check':
        return 'warning'
      case 'Proposal Sent':
        return 'success'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Intake Pipeline
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Client Enquiries Desk
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            High net worth client requests for destination celebrations in Jaipur and
            Udaipur, tracking palace availability and proposal cycles.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('Log new inquiry form will open in Stage 2.')}
        >
          Log New Inquiry
        </Button>
      </div>

      {/* Enquiries List */}
      <div className="space-y-4">
        {enquiries.map((enq) => (
          <Card key={enq.id} variant="default" className="p-0 overflow-hidden hover:border-bronze/50 transition-all duration-200">
            <div className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2.5">
                  <Badge variant={stageVariant(enq.stage)}>{enq.stage}</Badge>
                  <span className="text-xs text-ink-faint">Logged {enq.receivedAt}</span>
                </div>
                <h2 className="font-serif text-2xl font-bold text-ink">{enq.client}</h2>
                <div className="flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                    Target: {enq.targetVenues}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                    {enq.estimatedDates}
                  </span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-6 pt-4 lg:pt-0 border-t lg:border-t-0 border-warm-stone/60">
                <div className="text-left sm:text-right">
                  <span className="text-[11px] uppercase tracking-wider text-ink-muted block font-medium">
                    Delegation & Budget
                  </span>
                  <span className="text-sm font-semibold text-ink block">
                    {enq.guestCount} Guests
                  </span>
                  <span className="text-xs text-garden font-medium block">
                    {enq.budgetRange}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => alert(`Reviewing proposal dossier for ${enq.client}`)}
                  >
                    View Details
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => alert(`Checking palace dates for ${enq.targetVenues}`)}
                  >
                    Verify Dates
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
