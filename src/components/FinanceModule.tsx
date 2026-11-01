import { FinancePage } from '@/features/finance/pages/FinancePage'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

export function FinanceModule() {
  return (
    <ErrorBoundary
      fallbackTitle="Finance & Invoices Ledger Error"
      fallbackMessage="An unexpected issue occurred in the financial reconciliation ledger. Click below to retry or return to your wedding portfolio."
    >
      <FinancePage />
    </ErrorBoundary>
  )
}

export default FinanceModule
