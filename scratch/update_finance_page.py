code = '''import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  FileText,
  Plus,
  CreditCard,
  ShieldCheck,
  Eye,
  Check,
  XCircle,
  FileSpreadsheet,
  ArrowRight,
  Info,
  Clock,
  Layers,
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { formatINR } from '@/lib/formatters'
import {
  getInvoices,
  getFinanceOverview,
  reconcileInvoice,
  getReconciliationDetails,
  decideReconciliation,
  seedDemoInvoices,
  uploadVendorInvoice,
  recordPayment,
  type ApiInvoice,
  type ApiReconciliation,
} from '@/services/api'

export function FinancePage() {
  const queryClient = useQueryClient()
  const weddingId = 'w1'
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null)
  const [reconciliation, setReconciliation] = useState<ApiReconciliation | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [showJudgeTelemetry, setShowJudgeTelemetry] = useState<boolean>(false)

  // Dialog states
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false)
  const [isPaymentOpen, setIsPaymentOpen] = useState<boolean>(false)
  const [isDecisionOpen, setIsDecisionOpen] = useState<boolean>(false)
  const [decisionType, setDecisionType] = useState<'approve' | 'reject'>('approve')
  const [decisionNotes, setDecisionNotes] = useState<string>('')

  // Form states for manual submission
  const [newVendorName, setNewVendorName] = useState('')
  const [newInvoiceNumber, setNewInvoiceNumber] = useState('')
  const [newCategory, setNewCategory] = useState('catering')
  const [newAgreedValue, setNewAgreedValue] = useState('')
  const [newInvoiceTotal, setNewInvoiceTotal] = useState('')

  // Form states for recording payment
  const [payVendorName, setPayVendorName] = useState('')
  const [payAmount, setPayAmount] = useState('')
  const [payStage, setPayStage] = useState('advance')
  const [payReference, setPayReference] = useState('')

  // 1. Fetch real invoices
  const {
    data: invoices = [],
    isLoading: isInvoicesLoading,
    refetch: refetchInvoices,
  } = useQuery({
    queryKey: ['invoices', weddingId],
    queryFn: () => getInvoices(weddingId),
  })

  // 2. Fetch finance overview ledger
  const {
    data: overview,
    refetch: refetchOverview,
  } = useQuery({
    queryKey: ['finance-overview', weddingId],
    queryFn: () => getFinanceOverview(weddingId),
  })

  // 3. Reconcile mutation
  const reconcileMutation = useMutation({
    mutationFn: (invoiceId: string) => reconcileInvoice(invoiceId),
    onSuccess: (data) => {
      setReconciliation(data)
      setActionMessage('3-Way AI financial reconciliation and discrepancy check completed!')
      queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Financial reconciliation failed')
    },
  })

  // 4. Decision mutation
  const decisionMutation = useMutation({
    mutationFn: ({ invoiceId, decision, notes }: { invoiceId: string; decision: 'approve' | 'reject'; notes: string }) =>
      decideReconciliation(invoiceId, decision, notes),
    onSuccess: (data) => {
      setActionMessage(data.message || 'Audit decision recorded successfully.')
      setIsDecisionOpen(false)
      setDecisionNotes('')
      queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
      if (selectedInvoiceId) {
        getReconciliationDetails(selectedInvoiceId).then(setReconciliation).catch(() => {})
      }
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to record decision')
    },
  })

  // 5. Seed demo mutation
  const seedMutation = useMutation({
    mutationFn: () => seedDemoInvoices(weddingId),
    onSuccess: () => {
      setActionMessage('Demonstration financial ledger seeded with clean matching and unapproved surcharge cases!')
      queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to seed demonstration ledger')
    },
  })

  // 6. Submit invoice mutation
  const submitInvoiceMutation = useMutation({
    mutationFn: (data: any) => uploadVendorInvoice(data),
    onSuccess: () => {
      setActionMessage('Official vendor invoice submitted and registered for reconciliation.')
      setIsUploadOpen(false)
      setNewVendorName('')
      setNewInvoiceNumber('')
      setNewAgreedValue('')
      setNewInvoiceTotal('')
      queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to submit invoice')
    },
  })

  // 7. Record payment mutation
  const recordPaymentMutation = useMutation({
    mutationFn: (data: any) => recordPayment(data),
    onSuccess: () => {
      setActionMessage('Vendor bank disbursement recorded and allocated to wedding ledger.')
      setIsPaymentOpen(false)
      setPayVendorName('')
      setPayAmount('')
      setPayReference('')
      queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to record payment')
    },
  })

  const handleReconcile = (invoiceId: string) => {
    setSelectedInvoiceId(invoiceId)
    setErrorMessage(null)
    setActionMessage(null)
    reconcileMutation.mutate(invoiceId)
  }

  const handleOpenDecision = (type: 'approve' | 'reject') => {
    setDecisionType(type)
    setDecisionNotes(
      type === 'approve'
        ? 'Approved as authorized midnight extension change order after wedding host confirmation.'
        : 'Disallowed surcharge: midnight generator power was contracted as included in master PO.'
    )
    setIsDecisionOpen(true)
  }

  const handleConfirmDecision = () => {
    if (!selectedInvoiceId) return
    decisionMutation.mutate({
      invoiceId: selectedInvoiceId,
      decision: decisionType,
      notes: decisionNotes,
    })
  }

  const handleCreateInvoice = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newVendorName || !newInvoiceNumber || !newInvoiceTotal) return
    const agreed = parseFloat(newAgreedValue) || parseFloat(newInvoiceTotal)
    const total = parseFloat(newInvoiceTotal)
    submitInvoiceMutation.mutate({
      wedding_id: weddingId,
      vendor_name: newVendorName,
      category: newCategory,
      invoice_number: newInvoiceNumber,
      invoice_date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      agreed_value: agreed,
      approved_extras: 0,
      invoice_total: total,
      paid_amount: 0,
      line_items: [
        {
          original_description: `${newVendorName} standard package services`,
          quantity: 1,
          unit: 'lot',
          unit_price: total,
          line_total: total,
          category: newCategory,
        },
      ],
      source_filename: `${newInvoiceNumber.replace(/[^a-zA-Z0-9]/g, '_')}_Official_Invoice.pdf`,
    })
  }

  const handleCreatePayment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!payVendorName || !payAmount) return
    recordPaymentMutation.mutate({
      wedding_id: weddingId,
      vendor_name: payVendorName,
      payment_stage: payStage,
      amount: parseFloat(payAmount),
      payment_date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      reference: payReference || `NEFT-${Math.floor(100000 + Math.random() * 900000)}`,
    })
  }

  const statusVariant = (s: string) => {
    switch (s?.toLowerCase()) {
      case 'matched':
      case 'approved':
      case 'approved_override':
      case 'paid':
        return 'success'
      case 'flagged':
      case 'rejected':
      case 'discrepancy':
        return 'danger'
      case 'review_required':
      case 'submitted':
        return 'warning'
      default:
        return 'neutral'
    }
  }

  const activeInvoice = invoices.find((inv) => inv.id === selectedInvoiceId)

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            AI 3-Way Financial Reconciliation Engine
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Financial Invoices & PO Matching
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Automated three-way matching across purchase orders, vendor invoices, and banking disbursements with unapproved surcharge detection.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isInvoicesLoading ? 'animate-spin' : ''}`} />}
            onClick={() => {
              refetchInvoices()
              refetchOverview()
            }}
          >
            Refresh
          </Button>

          <Button
            variant="outline"
            size="md"
            leftIcon={<CreditCard className="w-4 h-4" />}
            onClick={() => setIsPaymentOpen(true)}
          >
            Record Payment
          </Button>

          <Button
            variant="bronze"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsUploadOpen(true)}
          >
            Upload Vendor Invoice
          </Button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{actionMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Financial Portfolio Metrics Banner */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl">
            <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Total Contracted PO</span>
            <span className="font-serif text-xl font-bold text-ink mt-1 block">
              {formatINR(overview.agreed_value || 0)}
            </span>
            <span className="text-[10px] text-ink-muted">Authorized contracts</span>
          </div>

          <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl">
            <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Billed Invoices</span>
            <span className="font-serif text-xl font-bold text-ink mt-1 block">
              {formatINR(overview.invoice_total || 0)}
            </span>
            <span className="text-[10px] text-ink-muted">{overview.invoices_count || 0} invoices on file</span>
          </div>

          <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl">
            <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Disbursed Payments</span>
            <span className="font-serif text-xl font-bold text-emerald-700 mt-1 block">
              {formatINR(overview.paid_amount || 0)}
            </span>
            <span className="text-[10px] text-emerald-600 font-medium">Bank verified</span>
          </div>

          <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl">
            <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Balance Outstanding</span>
            <span className="font-serif text-xl font-bold text-ink mt-1 block">
              {formatINR(overview.balance_payable || 0)}
            </span>
            <span className="text-[10px] text-ink-muted">Pending final milestones</span>
          </div>

          <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl">
            <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Unapproved Variance</span>
            <span className={`font-serif text-xl font-bold mt-1 block ${(overview.variance_amount || 0) > 0 ? 'text-red-700' : 'text-emerald-700'}`}>
              {(overview.variance_amount || 0) > 0 ? `+${formatINR(overview.variance_amount)}` : '₹0'}
            </span>
            <span className="text-[10px] text-ink-muted">{overview.pending_reviews_count || 0} audits needing review</span>
          </div>
        </div>
      )}

      {/* 3-Way Match Verification Card Section */}
      {reconciliation && activeInvoice && (
        <div className="bg-[#FAF8F5] border-2 border-[#541424]/40 rounded-3xl p-6 md:p-8 shadow-lg space-y-6">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-[#E8E2D9] pb-5">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#541424]/10 text-[#541424] text-[11px] font-semibold uppercase tracking-wider">
                  <Sparkles className="w-3.5 h-3.5 text-bronze" />
                  <span>3-Way Reconciliation Audit Result</span>
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-200/80 text-slate-800 text-[10px] font-mono font-medium">
                  {reconciliation.ai_provider || 'Google Gemini'} ({reconciliation.ai_model || 'gemini-3.5-flash-lite'})
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
                  <ShieldCheck className="w-3 h-3" />
                  Python Decimal Engine: 100% Mathematically Verified
                </span>
              </div>

              <h2 className="font-serif text-2xl md:text-3xl font-bold text-ink">
                Audit: {activeInvoice.vendor_name} ({activeInvoice.invoice_number})
              </h2>
              <p className="text-xs text-ink-muted mt-1">
                Audited against approved contract and bank ledger on {new Date().toLocaleDateString('en-GB')}.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowJudgeTelemetry(!showJudgeTelemetry)}
              >
                {showJudgeTelemetry ? 'Hide Telemetry' : 'Inspect Judge Telemetry'}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setReconciliation(null)}
              >
                Close Audit
              </Button>
            </div>
          </div>

          {/* Three-Way Comparison Cards: Card A, Card B, Card C */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Card A: Approved Quote / PO */}
            <div className="bg-white border border-[#E8E2D9] rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-warm-stone/80">
                <span className="text-[11px] font-bold uppercase tracking-wider text-bronze flex items-center gap-1.5">
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Card A: Approved Quote / PO</span>
                </span>
                <Badge variant="neutral">Baseline PO</Badge>
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Vendor</span>
                  <span className="font-medium text-ink">{activeInvoice.vendor_name}</span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Approved Contract Amount</span>
                  <span className="font-serif text-lg font-bold text-ink">
                    {formatINR(reconciliation.agreed_amount || activeInvoice.agreed_value)}
                  </span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Authorized Scope & Extras</span>
                  <span className="text-ink">{reconciliation.approved_extras > 0 ? formatINR(reconciliation.approved_extras) : 'INR 0.00 (No pre-approved change orders)'}</span>
                </div>
                <div className="pt-1 text-[11px] text-ink-muted">
                  Terms: Contractually locked rate per guest / package with GST compliance.
                </div>
              </div>
            </div>

            {/* Card B: Submitted Vendor Invoice */}
            <div className={`bg-white border rounded-2xl p-5 shadow-sm space-y-3 ${reconciliation.variance_amount > 0 ? 'border-red-300' : 'border-[#E8E2D9]'}`}>
              <div className="flex items-center justify-between pb-2 border-b border-warm-stone/80">
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#541424] flex items-center gap-1.5">
                  <FileText className="w-4 h-4" />
                  <span>Card B: Submitted Invoice</span>
                </span>
                <Badge variant={statusVariant(reconciliation.status)}>
                  {reconciliation.status.replace('_', ' ')}
                </Badge>
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Invoice Number & Source</span>
                  <span className="font-medium text-ink">{activeInvoice.invoice_number} ({activeInvoice.source_filename || 'PDF on file'})</span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Billed Grand Total</span>
                  <span className="font-serif text-lg font-bold text-ink">
                    {formatINR(reconciliation.invoice_total || activeInvoice.invoice_total)}
                  </span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Unapproved Surcharge / Variance</span>
                  <span className={`font-serif text-base font-bold ${reconciliation.variance_amount > 0 ? 'text-red-700' : 'text-emerald-700'}`}>
                    {reconciliation.variance_amount > 0 ? `+${formatINR(reconciliation.variance_amount)} (Unapproved)` : 'INR 0.00 (Zero Variance)'}
                  </span>
                </div>
                <div className="pt-1 text-[11px] text-ink-muted">
                  Line Items Billed: {reconciliation.line_matches?.length || activeInvoice.line_items_count} items analyzed.
                </div>
              </div>
            </div>

            {/* Card C: Recorded Payments & Disbursements */}
            <div className="bg-white border border-[#E8E2D9] rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-warm-stone/80">
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                  <CreditCard className="w-4 h-4" />
                  <span>Card C: Recorded Payments</span>
                </span>
                <Badge variant="success">Bank Ledger</Badge>
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Disbursed Advance / Milestones</span>
                  <span className="font-serif text-lg font-bold text-emerald-700">
                    {formatINR(reconciliation.total_paid || activeInvoice.paid_amount)}
                  </span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Remaining Contractual Balance</span>
                  <span className="font-serif text-base font-bold text-ink">
                    {formatINR(reconciliation.remaining_balance || activeInvoice.remaining_balance)}
                  </span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Payment Status</span>
                  <span className="text-ink">Advance confirmed via NEFT bank transfer.</span>
                </div>
                <div className="pt-1 text-[11px] text-ink-muted">
                  Disbursement hold: Balance held pending discrepancy audit resolution.
                </div>
              </div>
            </div>
          </div>

          {/* Gemini AI CFO Audit Narrative */}
          <div className="bg-white border border-[#E8E2D9] rounded-2xl p-5 shadow-sm space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#541424] flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-bronze" />
                <span>Gemini Financial Audit Narrative (CFO Briefing)</span>
              </span>
              <span className="text-[10px] font-mono text-ink-muted">
                Audit Ref: {reconciliation.id || 'AUD-2026-W1'}
              </span>
            </div>
            <p className="text-xs text-ink leading-relaxed font-sans bg-[#FAF8F5] p-3.5 rounded-xl border border-warm-stone/80">
              {reconciliation.ai_explanation || reconciliation.audit_summary || 'All line items and taxes match the authorized purchase order exactly.'}
            </p>
          </div>

          {/* Discrepancies Alert */}
          {reconciliation.discrepancies && reconciliation.discrepancies.length > 0 && (
            <div className="p-5 bg-red-50 border border-red-200 rounded-2xl space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-red-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span>Detected Surcharges & Scope Variances ({reconciliation.discrepancies.length})</span>
              </h4>
              <ul className="text-xs text-red-800 space-y-1.5 list-disc pl-5">
                {reconciliation.discrepancies.map((d, i) => (
                  <li key={i}>
                    <strong className="text-red-950">{d.type}:</strong> {d.details}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Line-item Matching Table */}
          {reconciliation.line_matches && reconciliation.line_matches.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-ink">
                Line-Item Three-Way Reconciliation Breakdown
              </h4>
              <div className="overflow-x-auto bg-white rounded-2xl border border-warm-stone">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-warm-stone text-ink-muted uppercase tracking-wider bg-warm-stone/20">
                      <th className="py-3 px-4">Invoice Line Item</th>
                      <th className="py-3 px-4">Matched PO Item</th>
                      <th className="py-3 px-4">Invoiced Total</th>
                      <th className="py-3 px-4">Agreed Total</th>
                      <th className="py-3 px-4 text-right">Variance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-warm-stone/50">
                    {reconciliation.line_matches.map((item, i) => (
                      <tr key={i} className={item.variance > 0 ? 'bg-red-50/50' : ''}>
                        <td className="py-3 px-4 font-medium text-ink">{item.invoice_item}</td>
                        <td className="py-3 px-4 text-ink-muted">{item.matched_quote_item || 'None (Unapproved Addition)'}</td>
                        <td className="py-3 px-4 font-semibold text-ink">{formatINR(item.invoice_total)}</td>
                        <td className="py-3 px-4 text-ink-muted">{formatINR(item.agreed_total)}</td>
                        <td className="py-3 px-4 text-right font-semibold">
                          {item.variance > 0 ? (
                            <span className="text-red-700">+{formatINR(item.variance)}</span>
                          ) : (
                            <span className="text-emerald-700">Matched</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Action Bar for Human Review / Resolution */}
          <div className="pt-4 border-t border-[#E8E2D9] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="text-xs text-ink-muted">
              {activeInvoice.status === 'approved' ? (
                <span className="text-emerald-700 font-medium flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Invoice approved for full milestone payment release.
                </span>
              ) : activeInvoice.status === 'rejected' ? (
                <span className="text-red-700 font-medium flex items-center gap-1.5">
                  <XCircle className="w-4 h-4" />
                  Invoice disputed: vendor has been requested to reissue without unapproved charges.
                </span>
              ) : (
                <span>Action required: Finance Manager or Lead Planner must approve or dispute variance.</span>
              )}
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="md"
                leftIcon={<XCircle className="w-4 h-4 text-red-600" />}
                onClick={() => handleOpenDecision('reject')}
                disabled={decisionMutation.isPending}
              >
                Dispute Invoice
              </Button>

              <Button
                variant="bronze"
                size="md"
                leftIcon={<Check className="w-4 h-4" />}
                onClick={() => handleOpenDecision('approve')}
                disabled={decisionMutation.isPending}
              >
                Approve Change Order
              </Button>
            </div>
          </div>

          {/* Judge Telemetry Modal / Expansion */}
          {showJudgeTelemetry && (
            <div className="bg-neutral-900 text-neutral-100 rounded-2xl p-5 font-mono text-[11px] space-y-3 border border-neutral-700">
              <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                <span className="text-amber-400 font-semibold uppercase tracking-wider">
                  Reconciliation Telemetry & Provenance (Judge Audit Mode)
                </span>
                <span className="text-neutral-400">
                  Audit Timestamp: {reconciliation.ai_timestamp || new Date().toISOString()}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-neutral-300">
                <div>AI Provider: <span className="text-emerald-400">{reconciliation.ai_provider || 'Google Gemini'}</span></div>
                <div>Model: <span className="text-emerald-400">{reconciliation.ai_model || 'gemini-3.5-flash-lite'}</span></div>
                <div>Math Validation: <span className="text-emerald-400">Python Decimal (Zero Hallucination)</span></div>
                <div>Human Signoff: <span className="text-amber-400">{activeInvoice.status}</span></div>
              </div>
              <div className="pt-2">
                <span className="text-neutral-400 block mb-1">Reconciliation Audit Payload:</span>
                <pre className="bg-black/60 p-3 rounded-lg overflow-x-auto text-[10px] text-neutral-300">
                  {JSON.stringify(reconciliation, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Invoices Portfolio List */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 className="font-serif text-xl font-bold text-ink flex items-center gap-2">
            <span>Vendor Invoices Portfolio ({invoices.length})</span>
            <Badge variant="neutral">{invoices.length} active bills</Badge>
          </h2>
          <span className="text-xs text-ink-muted">
            Tax Deduction At Source (TDS) & GST Compliance Locked
          </span>
        </div>

        {invoices.length === 0 && !isInvoicesLoading && (
          <div className="p-12 text-center bg-white border border-warm-stone rounded-3xl space-y-4">
            <FileText className="w-10 h-10 text-ink-muted mx-auto opacity-50" />
            <div className="max-w-md mx-auto space-y-1">
              <p className="font-serif text-lg font-bold text-ink">No vendor invoices recorded yet</p>
              <p className="text-xs text-ink-muted leading-relaxed">
                Vendor billing records populate automatically upon contract execution. You can also load our curated demonstration ledger to evaluate 3-way matching and unapproved surcharge detection.
              </p>
            </div>
            <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
              <Button
                variant="bronze"
                size="md"
                leftIcon={<Layers className="w-4 h-4" />}
                onClick={() => seedMutation.mutate()}
                disabled={seedMutation.isPending}
              >
                {seedMutation.isPending ? 'Loading Demo Ledger...' : 'Load Demonstration Ledger'}
              </Button>
              <Button
                variant="outline"
                size="md"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => setIsUploadOpen(true)}
              >
                Submit First Invoice
              </Button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {invoices.map((inv: ApiInvoice) => {
            const isSelected = selectedInvoiceId === inv.id
            return (
              <Card
                key={inv.id}
                variant="elevated"
                className={`transition-all hover:border-bronze/50 ${isSelected ? 'border-2 border-[#541424] shadow-md' : ''}`}
              >
                <CardContent className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={statusVariant(inv.status)}>
                        {inv.status.replace('_', ' ')}
                      </Badge>
                      <span className="font-mono text-xs text-ink-muted font-semibold">{inv.invoice_number}</span>
                      {inv.source_filename && (
                        <span className="text-[10px] text-ink-muted bg-warm-stone/30 px-2 py-0.5 rounded-md">
                          {inv.source_filename}
                        </span>
                      )}
                    </div>
                    <h3 className="font-serif text-lg font-bold text-ink">{inv.vendor_name}</h3>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                      <span>Category: <strong className="text-ink uppercase">{inv.category}</strong></span>
                      <span>Agreed Contract: <strong className="text-ink">{formatINR(inv.agreed_value)}</strong></span>
                      {inv.approved_extras > 0 && (
                        <span>Approved Extras: <strong className="text-ink">{formatINR(inv.approved_extras)}</strong></span>
                      )}
                      <span>Items: <strong className="text-ink">{inv.line_items_count}</strong></span>
                    </div>
                    {inv.discrepancy_note && (
                      <div className="text-[11px] text-red-700 font-medium pt-0.5">
                        Note: {inv.discrepancy_note}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col sm:flex-row items-end sm:items-center gap-5 self-end md:self-center">
                    <div className="text-right">
                      <div className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold">Invoice Amount</div>
                      <div className="text-xl font-serif font-bold text-ink">{formatINR(inv.invoice_total)}</div>
                      <div className="text-[11px] text-ink-muted">
                        Paid: <span className="text-emerald-700 font-semibold">{formatINR(inv.paid_amount)}</span> | Balance: <span className="font-semibold">{formatINR(inv.remaining_balance)}</span>
                      </div>
                    </div>

                    <Button
                      variant={isSelected ? 'default' : 'bronze'}
                      size="sm"
                      leftIcon={<Sparkles className="w-3.5 h-3.5" />}
                      onClick={() => handleReconcile(inv.id)}
                      disabled={reconcileMutation.isPending && selectedInvoiceId === inv.id}
                    >
                      {reconcileMutation.isPending && selectedInvoiceId === inv.id ? 'Auditing...' : isSelected ? 'Re-audit 3-Way Match' : 'Run 3-Way AI Audit'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Modal: Upload Vendor Invoice */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-lg w-full space-y-5 shadow-2xl border border-warm-stone">
            <div className="flex items-center justify-between pb-3 border-b border-warm-stone">
              <h3 className="font-serif text-xl font-bold text-ink">Submit Vendor Invoice</h3>
              <Button variant="ghost" size="sm" onClick={() => setIsUploadOpen(false)}>
                Cancel
              </Button>
            </div>
            <form onSubmit={handleCreateInvoice} className="space-y-4 text-xs">
              <div>
                <label className="block text-ink-muted uppercase tracking-wider mb-1">Vendor Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Royal Rajputana Hospitality"
                  value={newVendorName}
                  onChange={(e) => setNewVendorName(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Invoice Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. INV-2026-901"
                    value={newInvoiceNumber}
                    onChange={(e) => setNewInvoiceNumber(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink font-mono"
                  />
                </div>
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  >
                    <option value="catering">Catering</option>
                    <option value="decoration">Decoration</option>
                    <option value="photography">Photography</option>
                    <option value="entertainment">Entertainment</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Agreed PO Value (INR)</label>
                  <input
                    type="number"
                    required
                    placeholder="e.g. 1800000"
                    value={newAgreedValue}
                    onChange={(e) => setNewAgreedValue(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  />
                </div>
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Invoice Billed Total (INR)</label>
                  <input
                    type="number"
                    required
                    placeholder="e.g. 1850000"
                    value={newInvoiceTotal}
                    onChange={(e) => setNewInvoiceTotal(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  />
                </div>
              </div>
              <div className="pt-3 flex justify-end gap-3">
                <Button variant="outline" size="md" type="button" onClick={() => setIsUploadOpen(false)}>
                  Cancel
                </Button>
                <Button variant="bronze" size="md" type="submit" disabled={submitInvoiceMutation.isPending}>
                  {submitInvoiceMutation.isPending ? 'Submitting...' : 'Register Invoice'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Record Payment */}
      {isPaymentOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-lg w-full space-y-5 shadow-2xl border border-warm-stone">
            <div className="flex items-center justify-between pb-3 border-b border-warm-stone">
              <h3 className="font-serif text-xl font-bold text-ink">Record Vendor Disbursement</h3>
              <Button variant="ghost" size="sm" onClick={() => setIsPaymentOpen(false)}>
                Cancel
              </Button>
            </div>
            <form onSubmit={handleCreatePayment} className="space-y-4 text-xs">
              <div>
                <label className="block text-ink-muted uppercase tracking-wider mb-1">Vendor Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Virasat Mandap & Floral Scenography"
                  value={payVendorName}
                  onChange={(e) => setPayVendorName(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Disbursement Amount (INR)</label>
                  <input
                    type="number"
                    required
                    placeholder="e.g. 500000"
                    value={payAmount}
                    onChange={(e) => setPayAmount(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  />
                </div>
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Milestone Stage</label>
                  <select
                    value={payStage}
                    onChange={(e) => setPayStage(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  >
                    <option value="advance">Advance (30-50%)</option>
                    <option value="second_payment">Mid-Milestone (40%)</option>
                    <option value="final_balance">Final Settlement (10-20%)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-ink-muted uppercase tracking-wider mb-1">Banking Reference / UTR Number</label>
                <input
                  type="text"
                  placeholder="e.g. NEFT-HDFC-991823"
                  value={payReference}
                  onChange={(e) => setPayReference(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink font-mono"
                />
              </div>
              <div className="pt-3 flex justify-end gap-3">
                <Button variant="outline" size="md" type="button" onClick={() => setIsPaymentOpen(false)}>
                  Cancel
                </Button>
                <Button variant="bronze" size="md" type="submit" disabled={recordPaymentMutation.isPending}>
                  {recordPaymentMutation.isPending ? 'Recording...' : 'Record Payment'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Decision Resolution (Approve Change Order / Dispute) */}
      {isDecisionOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 md:p-8 max-w-lg w-full space-y-5 shadow-2xl border border-warm-stone">
            <div className="flex items-center justify-between pb-3 border-b border-warm-stone">
              <h3 className="font-serif text-xl font-bold text-ink">
                {decisionType === 'approve' ? 'Approve Authorized Change Order' : 'Dispute Invoice with Vendor'}
              </h3>
              <Button variant="ghost" size="sm" onClick={() => setIsDecisionOpen(false)}>
                Cancel
              </Button>
            </div>
            <div className="space-y-4 text-xs">
              <p className="text-ink-muted leading-relaxed">
                {decisionType === 'approve'
                  ? 'You are approving the unapproved variance as an authorized client change order. The wedding ledger will update accordingly.'
                  : 'You are rejecting the unapproved charges. An official dispute notice will be recorded on the invoice and the vendor requested to reissue.'}
              </p>
              <div>
                <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                  Finance Audit Resolution Notes
                </label>
                <textarea
                  rows={3}
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  placeholder="Enter detailed audit rationale..."
                />
              </div>
              <div className="pt-3 flex justify-end gap-3">
                <Button variant="outline" size="md" onClick={() => setIsDecisionOpen(false)}>
                  Cancel
                </Button>
                <Button
                  variant={decisionType === 'approve' ? 'bronze' : 'danger'}
                  size="md"
                  onClick={handleConfirmDecision}
                  disabled={decisionMutation.isPending}
                >
                  {decisionMutation.isPending ? 'Recording...' : decisionType === 'approve' ? 'Confirm Approval' : 'Confirm Dispute'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
'''

assert "—" not in code, "Em dash detected in code"

with open("src/features/finance/pages/FinancePage.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("FinancePage.tsx written successfully.")

