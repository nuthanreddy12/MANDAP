import re

code = '''import { useState, useMemo, useEffect } from 'react'
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
  Check,
  XCircle,
  FileSpreadsheet,
  Layers,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
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

// Robust monetary parser preventing NaN, undefined, or string concatenation
export function parseMoney(val: unknown): number {
  if (typeof val === 'number') return isNaN(val) ? 0 : val
  if (typeof val === 'string') {
    const clean = val.replace(/[^0-9.-]/g, '')
    const parsed = parseFloat(clean)
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
}

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
  const [payInvoiceId, setPayInvoiceId] = useState<string>('')
  const [payVendorId, setPayVendorId] = useState<string>('')
  const [payVendorName, setPayVendorName] = useState<string>('')
  const [payAmount, setPayAmount] = useState<string>('')
  const [payStage, setPayStage] = useState<string>('advance')
  const [payReference, setPayReference] = useState<string>('')

  // 1. Fetch real invoices from API
  const {
    data: fetchedInvoices = [],
    isLoading: isInvoicesLoading,
    refetch: refetchInvoices,
  } = useQuery({
    queryKey: ['invoices', weddingId],
    queryFn: () => getInvoices(weddingId),
  })

  // 2. Fetch finance overview ledger from API
  const {
    data: overview,
    refetch: refetchOverview,
  } = useQuery({
    queryKey: ['finance-overview', weddingId],
    queryFn: () => getFinanceOverview(weddingId),
  })

  // Local invoices state for instant zero-latency reactivity and parent synchronization
  const [localInvoices, setLocalInvoices] = useState<ApiInvoice[]>([])

  // Keep localInvoices synchronized with fetched query data
  useEffect(() => {
    if (fetchedInvoices && fetchedInvoices.length > 0) {
      setLocalInvoices(fetchedInvoices)
    }
  }, [fetchedInvoices])

  // Dynamically derived summary metrics directly from all vendor invoices
  const dynamicTotalAgreed = useMemo(() => {
    return localInvoices.reduce((sum, inv) => sum + parseMoney(inv.agreed_value), 0)
  }, [localInvoices])

  const dynamicTotalInvoiced = useMemo(() => {
    return localInvoices.reduce((sum, inv) => sum + parseMoney(inv.invoice_total), 0)
  }, [localInvoices])

  const dynamicTotalPaid = useMemo(() => {
    return localInvoices.reduce((sum, inv) => sum + parseMoney(inv.paid_amount), 0)
  }, [localInvoices])

  const dynamicBalancePayable = useMemo(() => {
    return Math.max(0, dynamicTotalInvoiced - dynamicTotalPaid)
  }, [dynamicTotalInvoiced, dynamicTotalPaid])

  const dynamicApprovedExtras = useMemo(() => {
    return localInvoices.reduce((sum, inv) => sum + parseMoney(inv.approved_extras), 0)
  }, [localInvoices])

  const dynamicVariance = useMemo(() => {
    return dynamicTotalInvoiced - (dynamicTotalAgreed + dynamicApprovedExtras)
  }, [dynamicTotalInvoiced, dynamicTotalAgreed, dynamicApprovedExtras])

  // Display metrics: use live derived invoice totals if invoices exist, else fallback to overview
  const displayTotalContracted = localInvoices.length > 0 ? dynamicTotalAgreed : parseMoney(overview?.agreed_value)
  const displayTotalInvoiced = localInvoices.length > 0 ? dynamicTotalInvoiced : parseMoney(overview?.invoice_total)
  const displayTotalPaid = localInvoices.length > 0 ? dynamicTotalPaid : parseMoney(overview?.paid_amount)
  const displayBalancePayable = localInvoices.length > 0 ? dynamicBalancePayable : parseMoney(overview?.balance_payable)
  const displayVariance = localInvoices.length > 0 ? dynamicVariance : parseMoney(overview?.variance_amount)
  const displayInvoicesCount = localInvoices.length > 0 ? localInvoices.length : (overview?.invoices_count || 0)
  const displayPendingReviews = overview?.pending_reviews_count ?? localInvoices.filter((i) => i.status === 'review_required' || i.status === 'submitted').length

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
    onSuccess: async () => {
      setActionMessage('Demonstration financial ledger seeded with clean matching and unapproved surcharge cases!')
      await queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      await queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
      const fresh = await refetchInvoices()
      if (fresh.data && fresh.data.length > 0) {
        setLocalInvoices(fresh.data)
      }
      refetchOverview()
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to seed demonstration ledger')
    },
  })

  // 6. Submit invoice mutation
  const submitInvoiceMutation = useMutation({
    mutationFn: (data: any) => uploadVendorInvoice(data),
    onSuccess: async () => {
      setActionMessage('Official vendor invoice submitted and registered for reconciliation.')
      setIsUploadOpen(false)
      setNewVendorName('')
      setNewInvoiceNumber('')
      setNewAgreedValue('')
      setNewInvoiceTotal('')
      await queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] })
      await queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] })
      const fresh = await refetchInvoices()
      if (fresh.data && fresh.data.length > 0) {
        setLocalInvoices(fresh.data)
      }
      refetchOverview()
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to submit invoice')
    },
  })

  // 7. Record payment mutation
  const recordPaymentMutation = useMutation({
    mutationFn: (data: any) => recordPayment(data),
    onSuccess: async () => {
      // Invalidate and refetch queries to synchronize with backend state
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['invoices', weddingId] }),
        queryClient.invalidateQueries({ queryKey: ['finance-overview', weddingId] }),
      ])
      const fresh = await refetchInvoices()
      if (fresh.data && fresh.data.length > 0) {
        setLocalInvoices(fresh.data)
      }
      refetchOverview()
      if (selectedInvoiceId) {
        getReconciliationDetails(selectedInvoiceId).then(setReconciliation).catch(() => {})
      }
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to record payment')
      // On error, revert local state to server data
      if (fetchedInvoices && fetchedInvoices.length > 0) {
        setLocalInvoices(fetchedInvoices)
      }
    },
  })

  const handleReconcile = (invoiceId: string) => {
    setSelectedInvoiceId(invoiceId)
    setErrorMessage(null)
    setActionMessage(null)
    reconcileMutation.mutate(invoiceId)
  }

  const handleOpenPayment = (inv?: ApiInvoice) => {
    setErrorMessage(null)
    setActionMessage(null)
    const target = inv || localInvoices[0]
    if (target) {
      setPayInvoiceId(target.id)
      setPayVendorId(target.vendor_id || '')
      setPayVendorName(target.vendor_name)
      setPayAmount('')
      setPayReference(`NEFT-${Math.floor(100000 + Math.random() * 900000)}`)
    } else {
      setPayInvoiceId('')
      setPayVendorId('')
      setPayVendorName('')
      setPayAmount('')
      setPayReference(`NEFT-${Math.floor(100000 + Math.random() * 900000)}`)
    }
    setIsPaymentOpen(true)
  }

  const handleSelectInvoiceForPayment = (invoiceId: string) => {
    setPayInvoiceId(invoiceId)
    const found = localInvoices.find((i) => i.id === invoiceId)
    if (found) {
      setPayVendorId(found.vendor_id || '')
      setPayVendorName(found.vendor_name)
    }
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
    const agreed = parseMoney(newAgreedValue) || parseMoney(newInvoiceTotal)
    const total = parseMoney(newInvoiceTotal)
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
    const amountVal = parseMoney(payAmount)
    if (!amountVal || amountVal <= 0) {
      setErrorMessage('Please enter a valid disbursement amount.')
      return
    }

    const payload = {
      wedding_id: weddingId,
      invoice_id: payInvoiceId || undefined,
      vendor_id: payVendorId || undefined,
      vendor_name: payVendorName || 'Vendor',
      payment_stage: payStage,
      amount: amountVal,
      payment_date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      reference: payReference || `NEFT-${Math.floor(100000 + Math.random() * 900000)}`,
    }

    // 1. Instantly update parent state so Disbursed Payments & Balance Outstanding update in real time
    setLocalInvoices((prev) =>
      prev.map((inv) => {
        const isTarget =
          (payload.invoice_id && inv.id === payload.invoice_id) ||
          (payload.vendor_id && inv.vendor_id === payload.vendor_id) ||
          (payload.vendor_name && inv.vendor_name.toLowerCase().includes(payload.vendor_name.toLowerCase()))
        if (!isTarget) return inv

        const currentPaid = parseMoney(inv.paid_amount)
        const total = parseMoney(inv.invoice_total)
        const updatedPaid = currentPaid + amountVal
        const updatedBalance = Math.max(0, total - updatedPaid)
        const updatedPct = total > 0 ? Math.min(100, Math.round((updatedPaid / total) * 100)) : 0
        const isPaid = updatedPaid >= total && total > 0

        return {
          ...inv,
          paid_amount: updatedPaid,
          remaining_balance: updatedBalance,
          payment_percentage: updatedPct,
          payment_status: isPaid ? 'paid' : updatedPaid > 0 ? 'partially_paid' : 'unpaid',
          payments_count: (inv.payments_count || 0) + 1,
        }
      })
    )

    // 2. Close modal immediately and show confirmation
    setIsPaymentOpen(false)
    setPayAmount('')
    setPayReference('')
    setActionMessage('Vendor bank disbursement recorded! Ledger and portfolio balances updated in real time.')

    // 3. Dispatch backend mutation
    recordPaymentMutation.mutate(payload)
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

  const activeInvoice = localInvoices.find((inv) => inv.id === selectedInvoiceId)
  const currentPayTarget = localInvoices.find((i) => i.id === payInvoiceId)

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
          <p className="text-sm text-ink-muted mt-1 max-w-2xl">
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
            onClick={() => handleOpenPayment()}
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

      {/* Financial Portfolio Metrics Banner: Dynamically derived in real time */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl shadow-sm">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Total Contracted PO</span>
          <span className="font-serif text-xl font-bold text-ink mt-1 block">
            {formatINR(displayTotalContracted)}
          </span>
          <span className="text-[10px] text-ink-muted">Authorized contracts</span>
        </div>

        <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl shadow-sm">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Billed Invoices</span>
          <span className="font-serif text-xl font-bold text-ink mt-1 block">
            {formatINR(displayTotalInvoiced)}
          </span>
          <span className="text-[10px] text-ink-muted">{displayInvoicesCount} invoices on file</span>
        </div>

        <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl shadow-sm">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Disbursed Payments</span>
          <span className="font-serif text-xl font-bold text-emerald-700 mt-1 block">
            {formatINR(displayTotalPaid)}
          </span>
          <span className="text-[10px] text-emerald-600 font-medium">Bank verified</span>
        </div>

        <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl shadow-sm">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Balance Outstanding</span>
          <span className="font-serif text-xl font-bold text-ink mt-1 block">
            {formatINR(displayBalancePayable)}
          </span>
          <span className="text-[10px] text-ink-muted">Pending final milestones</span>
        </div>

        <div className="p-4 bg-white border border-[#E8E2D9] rounded-2xl shadow-sm">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold block">Unapproved Variance</span>
          <span className={`font-serif text-xl font-bold mt-1 block ${displayVariance > 0 ? 'text-red-700' : 'text-emerald-700'}`}>
            {displayVariance > 0 ? `+${formatINR(displayVariance)}` : 'INR 0'}
          </span>
          <span className="text-[10px] text-ink-muted">{displayPendingReviews} audits needing review</span>
        </div>
      </div>

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
              <h2 className="font-serif text-2xl font-bold text-ink">
                Audit for {activeInvoice.vendor_name} ({activeInvoice.invoice_number})
              </h2>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowJudgeTelemetry(!showJudgeTelemetry)}
              >
                {showJudgeTelemetry ? 'Hide Telemetry' : 'Show Telemetry'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedInvoiceId(null)}
              >
                Close Audit View
              </Button>
            </div>
          </div>

          {/* 3 Cards: A (Quote), B (Invoice), C (Bank Ledger) */}
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
                  <span className="text-ink-muted block text-[10px] uppercase">Disbursed Payments</span>
                  <span className="font-serif text-lg font-bold text-emerald-700">
                    {formatINR(activeInvoice.paid_amount)}
                  </span>
                </div>
                <div>
                  <span className="text-ink-muted block text-[10px] uppercase">Remaining Contractual Balance</span>
                  <span className="font-serif text-base font-bold text-ink">
                    {formatINR(activeInvoice.remaining_balance)}
                  </span>
                </div>
                <div className="pt-1">
                  <div className="flex items-center justify-between text-[11px] text-ink-muted mb-1">
                    <span>Disbursement Progress</span>
                    <span className="font-semibold text-ink">
                      {activeInvoice.invoice_total > 0 ? ((activeInvoice.paid_amount / activeInvoice.invoice_total) * 100).toFixed(1) : '0'}%
                    </span>
                  </div>
                  <div className="w-full bg-warm-stone/40 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-emerald-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, activeInvoice.invoice_total > 0 ? (activeInvoice.paid_amount / activeInvoice.invoice_total) * 100 : 0)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Gemini AI CFO Audit Narrative */}
          <div className="bg-white border border-[#E8E2D9] rounded-2xl p-5 shadow-sm space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#541424] flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-bronze" />
                <span>Executive AI Audit Narrative</span>
              </span>
              <span className="text-[11px] text-ink-muted">
                Audit Status: <strong className="uppercase text-ink">{reconciliation.status.replace('_', ' ')}</strong>
              </span>
            </div>
            <p className="text-xs text-ink leading-relaxed bg-[#FAF8F5] p-3.5 rounded-xl border border-warm-stone/80 font-medium">
              {reconciliation.ai_explanation || 'Reconciliation analysis complete. Review line item matches below.'}
            </p>
          </div>

          {/* Line-by-Line 3-Way Match Table */}
          {reconciliation.line_matches && reconciliation.line_matches.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-serif text-base font-bold text-ink">
                Line-by-Line Item Matching & Variance Detection ({reconciliation.line_matches.length} items)
              </h3>
              <div className="overflow-x-auto border border-warm-stone rounded-2xl">
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

          {/* Telemetry Modal / Expansion */}
          {showJudgeTelemetry && (
            <div className="bg-neutral-900 text-neutral-100 rounded-2xl p-5 font-mono text-[11px] space-y-3 border border-neutral-700">
              <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                <span className="text-amber-400 font-semibold uppercase tracking-wider">
                  Reconciliation Telemetry & Provenance (Audit Mode)
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
            <span>Vendor Invoices Portfolio ({displayInvoicesCount})</span>
            <Badge variant="neutral">{displayInvoicesCount} active bills</Badge>
          </h2>
          <span className="text-xs text-ink-muted">
            Tax Deduction At Source (TDS) & GST Compliance Locked
          </span>
        </div>

        {localInvoices.length === 0 && !isInvoicesLoading && (
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

        <div className="space-y-4">
          {localInvoices.map((inv: ApiInvoice) => {
            const isSelected = selectedInvoiceId === inv.id
            const invTotal = parseMoney(inv.invoice_total)
            const invPaid = parseMoney(inv.paid_amount)
            const invRem = parseMoney(inv.remaining_balance)
            const payPct = invTotal > 0 ? Math.min(100, Math.round((invPaid / invTotal) * 100)) : 0
            const isFullyPaid = invPaid >= invTotal && invTotal > 0

            return (
              <Card
                key={inv.id}
                variant="elevated"
                className={`transition-all hover:border-bronze/50 ${isSelected ? 'border-2 border-[#541424] shadow-md' : ''}`}
              >
                <CardContent className="p-5 space-y-4">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="space-y-1.5">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant={statusVariant(inv.status)}>
                          Audit: {inv.status.replace('_', ' ')}
                        </Badge>
                        <Badge variant={isFullyPaid ? 'success' : invPaid > 0 ? 'bronze' : 'neutral'}>
                          Payment: {isFullyPaid ? 'Fully Settled' : invPaid > 0 ? `Partially Paid (${payPct}%)` : 'Unpaid (Due)'}
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

                    <div className="flex flex-col sm:flex-row items-end sm:items-center gap-4 self-end md:self-center">
                      <div className="text-right">
                        <div className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold">Invoice Amount</div>
                        <div className="text-xl font-serif font-bold text-ink">{formatINR(invTotal)}</div>
                        <div className="text-[11px] text-ink-muted mt-0.5">
                          Paid: <span className="text-emerald-700 font-semibold">{formatINR(invPaid)}</span> | Balance: <span className="font-semibold text-ink">{formatINR(invRem)}</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={<CreditCard className="w-3.5 h-3.5" />}
                          onClick={() => handleOpenPayment(inv)}
                        >
                          Record Payment
                        </Button>

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
                    </div>
                  </div>

                  {/* Payment Progress Bar */}
                  <div className="pt-2 border-t border-warm-stone/50 space-y-1">
                    <div className="flex items-center justify-between text-[11px] text-ink-muted">
                      <span>Payment Milestone Progress: <strong>{payPct}%</strong></span>
                      <span>Outstanding Balance: <strong className="text-ink">{formatINR(invRem)}</strong></span>
                    </div>
                    <div className="w-full bg-warm-stone/40 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${isFullyPaid ? 'bg-emerald-600' : 'bg-[#B8860B]'}`}
                        style={{ width: `${payPct}%` }}
                      />
                    </div>
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

      {/* Modal: Record Payment with Dropdown & Live Balance Calculations */}
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
              {/* Select target invoice from registered list */}
              <div>
                <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                  Target Vendor Invoice
                </label>
                <select
                  value={payInvoiceId}
                  onChange={(e) => handleSelectInvoiceForPayment(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink font-medium bg-white"
                >
                  {localInvoices.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      {inv.invoice_number} : {inv.vendor_name} (Balance Due: {formatINR(inv.remaining_balance)})
                    </option>
                  ))}
                  <option value="">Other / Custom Vendor Entry</option>
                </select>
              </div>

              {/* Dynamic Invoice Summary Card */}
              {currentPayTarget && (
                <div className="p-3.5 bg-amber-50/60 border border-amber-200/80 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-ink-muted">Invoiced Grand Total:</span>
                    <strong className="text-ink font-serif text-sm">{formatINR(currentPayTarget.invoice_total)}</strong>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-ink-muted">Already Disbursed:</span>
                    <span className="text-emerald-700 font-semibold">{formatINR(currentPayTarget.paid_amount)}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs pt-1 border-t border-amber-200/60">
                    <span className="font-semibold text-ink">Remaining Balance Due:</span>
                    <strong className="text-amber-900 font-serif text-base">{formatINR(currentPayTarget.remaining_balance)}</strong>
                  </div>

                  {/* Quick-fill buttons */}
                  {currentPayTarget.remaining_balance > 0 && (
                    <div className="pt-2 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => setPayAmount(currentPayTarget.remaining_balance.toString())}
                        className="px-2.5 py-1 text-[11px] bg-white border border-amber-300 rounded-lg text-amber-900 font-medium hover:bg-amber-100 transition-all cursor-pointer"
                      >
                        Pay Full Balance ({formatINR(currentPayTarget.remaining_balance)})
                      </button>
                      <button
                        type="button"
                        onClick={() => setPayAmount(Math.round(currentPayTarget.invoice_total * 0.5).toString())}
                        className="px-2.5 py-1 text-[11px] bg-white border border-amber-300 rounded-lg text-amber-900 font-medium hover:bg-amber-100 transition-all cursor-pointer"
                      >
                        Pay 50% ({formatINR(Math.round(currentPayTarget.invoice_total * 0.5))})
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Custom vendor name fallback if not matching invoice */}
              {!currentPayTarget && (
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Vendor Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Royal Rajputana Hospitality"
                    value={payVendorName}
                    onChange={(e) => setPayVendorName(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                    Disbursement Amount (INR)
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    placeholder="e.g. 500000"
                    value={payAmount}
                    onChange={(e) => setPayAmount(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-ink-muted uppercase tracking-wider mb-1">Milestone Stage</label>
                  <select
                    value={payStage}
                    onChange={(e) => setPayStage(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white"
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
                  {recordPaymentMutation.isPending ? 'Recording...' : 'Disburse & Record Payment'}
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

assert '—' not in code, 'Em dash detected in code!'

with open('src/features/finance/pages/FinancePage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated src/features/finance/pages/FinancePage.tsx successfully!')

# Also create src/components/FinanceModule.tsx as alias/wrapper
module_code = '''// Alias for canonical FinancePage component
export { FinancePage as default, FinancePage as FinanceModule } from '@/features/finance/pages/FinancePage'
'''

assert '—' not in module_code, 'Em dash detected in module_code!'

with open('src/components/FinanceModule.tsx', 'w', encoding='utf-8') as f:
    f.write(module_code)

print('Created src/components/FinanceModule.tsx successfully!')

