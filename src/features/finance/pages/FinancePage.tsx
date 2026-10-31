import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface InvoiceReconciliation {
  id: string
  invoiceNumber: string
  vendorName: string
  wedding: string
  amount: string
  tdsDeduction: string
  netPayable: string
  status: 'Reconciled & Paid' | 'Pending Audit' | 'Overdue Advance'
  dueDate: string
}

const MOCK_INVOICES: InvoiceReconciliation[] = [
  {
    id: 'inv-1',
    invoiceNumber: 'INV/MFA/2026/089',
    vendorName: 'Mewar Floral Artisans',
    wedding: 'Ananya & Devendra (Udaivilas)',
    amount: '₹13,80,000',
    tdsDeduction: '₹27,600 (2% 194C)',
    netPayable: '₹13,52,400',
    status: 'Reconciled & Paid',
    dueDate: 'Paid 28 Oct 2026',
  },
  {
    id: 'inv-2',
    invoiceNumber: 'INV/JRB/2026/042',
    vendorName: 'Jaipur Royal Brass & Shehnai',
    wedding: 'Rhea & Arjun (Rambagh)',
    amount: '₹2,55,000',
    tdsDeduction: '₹5,100 (2% 194C)',
    netPayable: '₹2,49,900',
    status: 'Pending Audit',
    dueDate: 'Due 04 Nov 2026',
  },
  {
    id: 'inv-3',
    invoiceNumber: 'INV/RSG/2026/117',
    vendorName: 'Rajputana Safa & Turban Guild',
    wedding: 'Meera & Kabir (Jagmandir)',
    amount: '₹4,20,000',
    tdsDeduction: '₹8,400 (2% 194C)',
    netPayable: '₹4,11,600',
    status: 'Overdue Advance',
    dueDate: 'Overdue by 2 days',
  },
]

export function FinancePage() {
  const [invoices] = useState<InvoiceReconciliation[]>(MOCK_INVOICES)

  const statusVariant = (s: InvoiceReconciliation['status']) => {
    switch (s) {
      case 'Reconciled & Paid':
        return 'success'
      case 'Pending Audit':
        return 'warning'
      case 'Overdue Advance':
        return 'danger'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Treasury & Accounting
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Finance & Invoice Reconciliation
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Tracking artisan advance disbursements, GST tax invoices, TDS deductions under Section 194C,
            and milestone payouts.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('Log vendor tax invoice modal will open in Stage 2.')}
        >
          Record Vendor Invoice
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Total Disbursed This Season
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">₹3.42 Cr</p>
          <span className="text-[11px] text-garden font-medium block mt-0.5">
            100% Tax Compliant
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            Pending Vendor Audit
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">₹68.4 Lakhs</p>
          <span className="text-[11px] text-bronze font-medium block mt-0.5">
            8 Invoices In Verification
          </span>
        </Card>

        <Card variant="muted" className="p-5">
          <span className="text-xs uppercase tracking-wider text-ink-muted font-medium">
            TDS Remitted (194C)
          </span>
          <p className="font-serif text-2xl font-bold text-ink mt-1">₹6.84 Lakhs</p>
          <span className="text-[11px] text-ink-muted font-medium block mt-0.5">
            Quarterly Challans Filed
          </span>
        </Card>
      </div>

      <Card variant="default" className="p-0 overflow-hidden shadow-xs">
        <CardHeader>
          <CardTitle className="text-lg font-serif">Recent Vendor Invoices & Milestone Releases</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-warm-stone/60">
            {invoices.map((inv) => (
              <div
                key={inv.id}
                className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-ivory-warm/30 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-ink text-sm">
                      {inv.vendorName}
                    </span>
                    <Badge variant={statusVariant(inv.status)}>{inv.status}</Badge>
                  </div>
                  <p className="text-xs text-ink-muted">
                    {inv.invoiceNumber} • {inv.wedding}
                  </p>
                  <span className="text-[11px] text-ink-faint block">
                    Tax Deduction: {inv.tdsDeduction} • {inv.dueDate}
                  </span>
                </div>

                <div className="flex items-center gap-5">
                  <div className="text-left md:text-right">
                    <span className="text-xs text-ink-muted block uppercase tracking-wider font-medium">
                      Net Payable
                    </span>
                    <span className="font-serif text-lg font-bold text-ink">
                      {inv.netPayable}
                    </span>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      alert(`Initiating invoice audit check for ${inv.invoiceNumber}`)
                    }
                  >
                    Inspect Audit Dossier
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
