import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, MapPin, Users, Calendar, ArrowRight, Filter, RefreshCw } from 'lucide-react'
import { MOCK_WEDDINGS, PalaceWedding } from '@/mocks/data/weddings'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { getWeddings } from '@/services/api'
import { useWedding } from '@/context/WeddingContext'

export function WeddingsPage() {
  const navigate = useNavigate()
  const [selectedCity, setSelectedCity] = useState<'All' | 'Jaipur' | 'Udaipur' | 'Jaisalmer'>('All')
  const { activeWeddingId, setActiveWeddingId } = useWedding()

  const { data: apiWeddings, isLoading, isError, refetch } = useQuery({
    queryKey: ['weddings'],
    queryFn: getWeddings,
    retry: 1,
  })

  // Normalize API data to PalaceWedding shape with fallback to MOCK_WEDDINGS
  const weddings: PalaceWedding[] = apiWeddings && apiWeddings.length > 0
    ? apiWeddings.map((w, idx) => ({
        id: w.id,
        couple: w.couple_names,
        venue: w.venue,
        city: (w.destination.includes('Udaipur') ? 'Udaipur' : w.destination.includes('Jaisalmer') ? 'Jaisalmer' : 'Jaipur') as any,
        dates: w.dates,
        guestCount: w.guest_count,
        status: w.health_status === 'attention_needed' ? 'Final Review' : 'In Production',
        nextMilestone: w.health_status === 'attention_needed' ? 'Catering Tasting and Surcharge Audit' : 'Ceremony Schedule Coordination',
        leadProducer: w.assigned_planner || w.planner || 'Gayatri Rathore',
        ceremoniesCount: idx === 0 ? 5 : 4,
        budgetSummary: w.client_budget ? `Production allocation: ₹${(w.client_budget / 10000000).toFixed(1)} Cr` : 'Production allocation: ₹4.8 Cr',
      }))
    : MOCK_WEDDINGS

  const filteredWeddings = weddings.filter(
    (w) => selectedCity === 'All' || w.city === selectedCity
  )

  const statusVariant = (status: PalaceWedding['status']) => {
    switch (status) {
      case 'In Production':
        return 'success'
      case 'Contract Signed':
        return 'bronze'
      case 'Final Review':
        return 'warning'
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
            Celebrations Portfolio
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Active Palace Weddings
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Overseeing multi-day royal production, heritage palace logistics, and live
            ceremony schedules across Rajasthan.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<Filter className="w-4 h-4 text-bronze" />}
            onClick={() => {
              setSelectedCity((prev) =>
                prev === 'All' ? 'Udaipur' : prev === 'Udaipur' ? 'Jaipur' : prev === 'Jaipur' ? 'Jaisalmer' : 'All'
              )
            }}
          >
            Filter: {selectedCity}
          </Button>

          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>

          <Button
            variant="bronze"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => navigate('/enquiries')}
          >
            New Wedding File
          </Button>
        </div>
      </div>

      {isLoading && !apiWeddings && (
        <div className="p-8 text-center bg-ivory-card border border-warm-stone rounded-lg">
          <RefreshCw className="w-6 h-6 animate-spin text-bronze mx-auto mb-2" />
          <p className="text-xs text-ink-muted">Loading active palace weddings from backend API...</p>
        </div>
      )}

      {isError && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-xs">
          Notice: Operating in offline mode with cached portfolio data. Verify backend connectivity at http://localhost:8000/api/v1.
        </div>
      )}

      {/* Weddings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredWeddings.map((wedding) => (
          <Card key={wedding.id} variant="elevated" className="hover:border-bronze/60 transition-all duration-300">
            <CardHeader className="flex flex-row items-start justify-between gap-4">
              <div>
                <Badge variant={statusVariant(wedding.status)} className="mb-2">
                  {wedding.status}
                </Badge>
                <CardTitle className="text-2xl font-serif">{wedding.couple}</CardTitle>
                <div className="flex items-center gap-1.5 text-xs text-ink-muted mt-1.5">
                  <MapPin className="w-3.5 h-3.5 text-bronze shrink-0" aria-hidden="true" />
                  <span>{wedding.venue}</span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[11px] font-semibold text-ink-muted block uppercase tracking-wider">
                  Palace Circuit
                </span>
                <span className="font-serif font-bold text-lg text-ink">
                  {wedding.city}
                </span>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 py-3 border-y border-warm-stone/60 text-xs">
                <div>
                  <div className="flex items-center gap-1 text-ink-muted mb-1">
                    <Calendar className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                    <span className="font-medium">Dates</span>
                  </div>
                  <span className="font-medium text-ink block">{wedding.dates}</span>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-ink-muted mb-1">
                    <Users className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                    <span className="font-medium">Delegation</span>
                  </div>
                  <span className="font-medium text-ink block">{wedding.guestCount} Royal Guests</span>
                </div>
              </div>

              <div className="bg-ivory-warm p-3.5 rounded-md border border-warm-stone/70">
                <span className="text-[11px] font-semibold text-bronze uppercase tracking-wider block">
                  Next Critical Milestone
                </span>
                <p className="text-xs font-medium text-ink mt-0.5">
                  {wedding.nextMilestone}
                </p>
                <div className="flex items-center justify-between text-[11px] text-ink-muted mt-2 pt-2 border-t border-warm-stone/60">
                  <span>Lead Producer: <strong className="text-ink">{wedding.leadProducer}</strong></span>
                  <span className="font-medium">{wedding.ceremoniesCount} Ceremonies Scheduled</span>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              <span className="text-xs font-medium text-ink-muted">
                {wedding.budgetSummary}
              </span>
              <div className="flex items-center gap-2">
                {wedding.id === activeWeddingId && (
                  <span className="text-[10px] uppercase tracking-wider text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded-full">
                    Active Desk
                  </span>
                )}
                <Button
                  variant={wedding.id === activeWeddingId ? "bronze" : "outline"}
                  size="sm"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                  onClick={() => {
                    setActiveWeddingId(wedding.id)
                    navigate('/quotes')
                  }}
                >
                  {wedding.id === activeWeddingId ? 'Active Desk' : 'Switch Workspace'}
                </Button>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>

      {filteredWeddings.length === 0 && (
        <div className="text-center py-16 px-4 bg-ivory-card border border-warm-stone rounded-lg shadow-2xs">
          <p className="font-serif text-xl font-bold text-ink">No weddings found in {selectedCity}</p>
          <p className="text-xs text-ink-muted mt-1">Adjust filters or create a new wedding dossier.</p>
          <Button
            variant="secondary"
            size="md"
            className="mt-4"
            onClick={() => setSelectedCity('All')}
          >
            Reset Filters
          </Button>
        </div>
      )}
    </div>
  )
}
