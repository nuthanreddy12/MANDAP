with open("src/features/finance/pages/FinancePage.tsx", "r", encoding="utf-8") as f:
    content = f.read()

target_block = """    // 1. Instantly update parent state so Disbursed Payments & Balance Outstanding update in real time
    setOverrideInvoices((current) => {
      const base = current || fetchedInvoices
      return base.map((inv) => {
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
    })"""

replacement_block = """    // 1. Instantly update both parent React state and React Query cache for zero-latency UI reactivity
    const updateInvoiceList = (baseList: ApiInvoice[]) => {
      return baseList.map((inv) => {
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
    }

    setOverrideInvoices((current) => updateInvoiceList(current || fetchedInvoices))

    // Direct React Query cache synchronization so top summary cards update immediately
    queryClient.setQueryData(['invoices', weddingId], (old: ApiInvoice[] | undefined) => {
      return updateInvoiceList(old || fetchedInvoices)
    })

    queryClient.setQueryData(['finance-overview', weddingId], (old: any) => {
      if (!old) return old
      const newPaid = parseMoney(old.paid_amount) + amountVal
      const totalInv = parseMoney(old.invoice_total)
      return {
        ...old,
        paid_amount: newPaid,
        balance_payable: Math.max(0, totalInv - newPaid),
      }
    })"""

assert target_block in content, "target_block not found in FinancePage.tsx"
content = content.replace(target_block, replacement_block, 1)

assert "\u2014" not in content, "Em dash detected"

with open("src/features/finance/pages/FinancePage.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("FinancePage.tsx updated successfully with dual-state synchronization!")

