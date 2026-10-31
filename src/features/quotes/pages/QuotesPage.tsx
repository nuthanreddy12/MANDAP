import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface QuoteComparison {
  id: string
  wedding: string
  deliverable: string
  bidders: {
    vendorName: string
    quoteAmount: string
    advanceRequired: string
    inclusions: string
    status: 'Selected' | 'Evaluating' | 'Archived'
  }[]
}

const MOCK_QUOTES: QuoteComparison[] = [
  {
    id: 'qc-01',
    wedding: 'Ananya Singhania & Devendra Rathore (Udaivilas)',
    deliverable: 'Sangeet Stage Floral Architecture & Heritage Chandeliers',
    bidders: [
      {
        vendorName: 'Mewar Floral Artisans',
        quoteAmount: '₹34,50,000',
        advanceRequired: '40% on contract',
        inclusions: '10,000 Dutch roses, brass candelabras, 48hr turnaround',
        status: 'Selected',
      },
      {
        vendorName: 'Jaipur Royal Bloom Guild',
        quoteAmount: '₹38,20,000',
        advanceRequired: '50% on contract',
        inclusions: 'Imported hydrangeas, gold leaf filigree structures',
        status: 'Evaluating',
      },
    ],
  },
  {
    id: 'qc-02',
    wedding: 'Rhea Kothari & Arjun Mehta (Rambagh Palace)',
    deliverable: 'Traditional Shehnai & Nagada Welcoming Procession',
    bidders: [
      {
        vendorName: 'Jaipur Royal Brass & Shehnai Collective',
        quoteAmount: '₹8,50,000',
        advanceRequired: '30% on contract',
        inclusions: '16 master performers in ceremonial gold-embroidered achkans',
        status: 'Selected',
      },
      {
        vendorName: 'Desert Melody Troupe',
        quoteAmount: '₹7,90,000',
        advanceRequired: '50% on contract',
        inclusions: '12 folk instrumentalists with percussionists',
        status: 'Evaluating',
      },
    ],
  },
]

export function QuotesPage() {
  const [quotes] = useState<QuoteComparison[]>(MOCK_QUOTES)

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Procurement Analysis
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Quote Comparison Matrices
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Side by side evaluation of artisan quotes, advance terms, and technical specifications
            for royal ceremonies.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('New quote evaluation request will open in Stage 2.')}
        >
          New Quote Matrix
        </Button>
      </div>

      <div className="space-y-6">
        {quotes.map((q) => (
          <Card key={q.id} variant="default" className="p-0 overflow-hidden shadow-xs hover:border-bronze/50 transition-colors">
            <CardHeader className="bg-ivory-warm/60">
              <span className="text-[11px] font-semibold text-bronze uppercase tracking-wider block">
                {q.wedding}
              </span>
              <CardTitle className="text-xl font-serif mt-1">{q.deliverable}</CardTitle>
            </CardHeader>

            <CardContent className="p-0">
              <div className="divide-y divide-warm-stone/60">
                {q.bidders.map((bidder) => (
                  <div
                    key={bidder.vendorName}
                    className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-ivory-warm/30 transition-colors"
                  >
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-ink text-sm">
                          {bidder.vendorName}
                        </span>
                        <Badge
                          variant={bidder.status === 'Selected' ? 'success' : 'neutral'}
                        >
                          {bidder.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-ink-muted">
                        Inclusions: {bidder.inclusions}
                      </p>
                      <span className="text-[11px] text-ink-faint block">
                        Advance Terms: {bidder.advanceRequired}
                      </span>
                    </div>

                    <div className="flex items-center gap-5">
                      <div className="text-left md:text-right">
                        <span className="text-xs text-ink-muted block uppercase tracking-wider font-medium">
                          Quoted Total
                        </span>
                        <span className="font-serif text-lg font-bold text-ink">
                          {bidder.quoteAmount}
                        </span>
                      </div>

                      <Button
                        variant={bidder.status === 'Selected' ? 'outline' : 'secondary'}
                        size="sm"
                        onClick={() =>
                          alert(`Viewing detailed bid breakdown from ${bidder.vendorName}`)
                        }
                      >
                        Inspect Line Items
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
