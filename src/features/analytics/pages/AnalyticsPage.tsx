import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { RefreshCw } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatINR } from '@/lib/formatters'
import { getOverview } from '@/services/api'

const PROFITABILITY_DATA = [
  { wedding: 'Singhania (Udaivilas)', revenue: 48, cost: 37, margin: 11 },
  { wedding: 'Kothari (Rambagh)', revenue: 62, cost: 48, margin: 14 },
  { wedding: 'Chordia (Jagmandir)', revenue: 39, cost: 30, margin: 9 },
  { wedding: 'Mittal (City Palace)', revenue: 54, cost: 41, margin: 13 },
]

export function AnalyticsPage() {
  const { data: overview, isLoading, refetch } = useQuery({
    queryKey: ['overview'],
    queryFn: getOverview,
  })

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Executive Operations Desk
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Agency Profitability & Margins
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Revenue realizations, production costs, and net agency commissions across Jaipur and
            Udaipur royal wedding seasons.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>

          <Button
            variant="outline"
            size="md"
            onClick={() => alert('Exporting season P&L ledger to PDF.')}
          >
            Export Financial Ledger
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Active Celebrations
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">
            {overview?.active_weddings_count || 4} Palace Weddings
          </p>
          <span className="text-[11px] text-garden font-medium block mt-0.5">
            Jaipur & Udaipur Desk
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Season Gross Billings
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">
            {overview?.total_contracted_revenue ? formatINR(overview.total_contracted_revenue) : '₹20.3 Cr'}
          </p>
          <span className="text-[11px] text-garden font-medium block mt-0.5">
            +18% versus previous season
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Pending Milestones
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">
            {overview?.pending_tasks_count || 19} Critical Cues
          </p>
          <span className="text-[11px] text-ink-muted font-medium block mt-0.5">
            Statutory & Rigging Checkpoints
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Verified Artisan Network
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">
            {overview?.verified_vendors_count || 24} Guild Masters
          </p>
          <span className="text-[11px] text-bronze font-medium block mt-0.5">
            Quality Vetted Rating &gt; 4.90
          </span>
        </Card>
      </div>

      <Card variant="elevated" className="p-6">
        <CardHeader className="px-0 pt-0 pb-4">
          <CardTitle className="text-xl font-serif">Portfolio Margin Distribution (Lakhs INR)</CardTitle>
          <p className="text-xs text-ink-muted">Gross contracted billings versus direct technical and artisanal production expenses.</p>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={PROFITABILITY_DATA} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2DBD0" vertical={false} />
                <XAxis dataKey="wedding" tick={{ fill: '#71717A', fontSize: 11 }} />
                <YAxis tick={{ fill: '#71717A', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E8E2D9', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#541424" name="Revenue (Lakhs)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="cost" fill="#B8860B" name="Cost (Lakhs)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
