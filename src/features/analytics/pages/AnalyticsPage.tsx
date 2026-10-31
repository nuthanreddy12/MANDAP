import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

const PROFITABILITY_DATA = [
  { wedding: 'Singhania (Udaivilas)', revenue: 48, cost: 37, margin: 11 },
  { wedding: 'Kothari (Rambagh)', revenue: 62, cost: 48, margin: 14 },
  { wedding: 'Chordia (Jagmandir)', revenue: 39, cost: 30, margin: 9 },
  { wedding: 'Mittal (City Palace)', revenue: 54, cost: 41, margin: 13 },
]

export function AnalyticsPage() {
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

        <Button
          variant="outline"
          size="md"
          onClick={() => alert('Exporting season P&L ledger to PDF.')}
        >
          Export Financial Ledger
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Season Gross Billings
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">₹20.3 Cr</p>
          <span className="text-[11px] text-garden font-medium block mt-0.5">
            +18% versus previous season
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Net Agency Retainer & Margin
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">₹4.7 Cr</p>
          <span className="text-[11px] text-bronze font-medium block mt-0.5">
            23.1% average net commission
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Vendor Payout Reconciliation
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">94.2%</p>
          <span className="text-[11px] text-garden font-medium block mt-0.5">
            Zero disputed line items
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Avg Production Turnaround
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">4.2 Months</p>
          <span className="text-[11px] text-ink-muted font-medium block mt-0.5">
            From inquiry to first Phera
          </span>
        </Card>
      </div>

      {/* Production Chart */}
      <Card variant="default">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <CardTitle className="text-xl font-serif">
                Wedding Financial Breakdown (in ₹ Lakhs)
              </CardTitle>
              <p className="text-xs text-ink-muted mt-0.5">
                Comparing Gross Production Revenue against Direct Artisan & Vendor Outlays
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 bg-bronze rounded-xs inline-block" />
                Gross Revenue
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 bg-garden rounded-xs inline-block" />
                Agency Net Margin
              </span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={PROFITABILITY_DATA}
              margin={{ top: 20, right: 30, left: 10, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E8DFD8" vertical={false} />
              <XAxis
                dataKey="wedding"
                tick={{ fill: '#70645D', fontSize: 11, fontFamily: 'Work Sans' }}
                axisLine={{ stroke: '#E8DFD8' }}
              />
              <YAxis
                tick={{ fill: '#70645D', fontSize: 11, fontFamily: 'Work Sans' }}
                axisLine={{ stroke: '#E8DFD8' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#E8DFD8',
                  borderRadius: '6px',
                  fontFamily: 'Work Sans',
                  fontSize: '12px',
                  color: '#2C2523',
                  boxShadow: '0 4px 12px rgba(44,37,35,0.06)',
                }}
              />
              <Bar dataKey="revenue" name="Gross Revenue (₹L)" fill="#8D674E" radius={[4, 4, 0, 0]} />
              <Bar dataKey="margin" name="Net Agency Margin (₹L)" fill="#5A7356" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
