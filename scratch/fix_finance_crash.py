# 1. Update FinancePage.tsx
with open("src/features/finance/pages/FinancePage.tsx", "r", encoding="utf-8") as f:
    fin_content = f.read()

# Add imports
old_imports = """import {
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
} from '@/services/api'"""

new_imports = """import {
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
import { useWedding } from '@/context/WeddingContext'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'"""

assert old_imports in fin_content, "old_imports not found in FinancePage.tsx"
fin_content = fin_content.replace(old_imports, new_imports, 1)

# Safe wedding context lookup and rename to FinancePageContent
old_header = """export function FinancePage() {
  const queryClient = useQueryClient()
  const { activeWeddingId: weddingId } = useWedding()"""

new_header = """function FinancePageContent() {
  const queryClient = useQueryClient()
  
  // Safe wedding context resolution with graceful fallback
  let weddingId = 'w1'
  try {
    const weddingCtx = useWedding()
    if (weddingCtx && weddingCtx.activeWeddingId) {
      weddingId = weddingCtx.activeWeddingId
    }
  } catch {
    weddingId = 'w1'
  }"""

assert old_header in fin_content, "old_header not found in FinancePage.tsx"
fin_content = fin_content.replace(old_header, new_header, 1)

# Fix Button variant 'default' -> 'primary'
old_btn = "variant={isSelected ? 'default' : 'bronze'}"
new_btn = "variant={isSelected ? 'primary' : 'bronze'}"
assert old_btn in fin_content, "old_btn not found in FinancePage.tsx"
fin_content = fin_content.replace(old_btn, new_btn, 1)

# Append wrapped export at the bottom
fin_content += """

export function FinancePage() {
  return (
    <ErrorBoundary
      fallbackTitle="Finance & Invoices Ledger Error"
      fallbackMessage="An unexpected runtime issue occurred in the financial reconciliation ledger. Click below to retry or return to your wedding portfolio."
    >
      <FinancePageContent />
    </ErrorBoundary>
  )
}

export default FinancePage
"""

assert "\u2014" not in fin_content, "Em dash detected in FinancePage.tsx"

with open("src/features/finance/pages/FinancePage.tsx", "w", encoding="utf-8") as f:
    f.write(fin_content)
print("FinancePage.tsx updated successfully with safe context and ErrorBoundary!")

# 2. Update RunOfShowPage.tsx
with open("src/features/run-of-show/pages/RunOfShowPage.tsx", "r", encoding="utf-8") as f:
    ros_content = f.read()

# Remove unused ApiTimelineEvent
old_ros_import = """  calculateScheduleRecovery,
  approveRecoverySchedule,
  type ApiTimelineEvent,
} from '@/services/api'"""

new_ros_import = """  calculateScheduleRecovery,
  approveRecoverySchedule,
} from '@/services/api'"""

assert old_ros_import in ros_content, "old_ros_import not found in RunOfShowPage.tsx"
ros_content = ros_content.replace(old_ros_import, new_ros_import, 1)

# Add isLocked to first branch of syncedRunSheet
old_first_branch = """      return events.map((cue) => ({
        ...cue,
        activeStartTime: cue.start_time,
        activeEndTime: cue.end_time,
        delayOffsetMinutes: cue.delay_minutes || 0,
        isCascaded: false,
        isDelayed: (cue.delay_minutes || 0) > 0,
        originalStart: cue.start_time,
        originalEnd: cue.end_time,
        changeReason: undefined as string | undefined,
        hasConflict: false,
        conflictMessage: undefined as string | undefined,
      }))"""

new_first_branch = """      return events.map((cue) => ({
        ...cue,
        activeStartTime: cue.start_time,
        activeEndTime: cue.end_time,
        delayOffsetMinutes: cue.delay_minutes || 0,
        isCascaded: false,
        isDelayed: (cue.delay_minutes || 0) > 0,
        originalStart: cue.start_time,
        originalEnd: cue.end_time,
        changeReason: undefined as string | undefined,
        isLocked: Boolean(cue.is_locked),
        hasConflict: false,
        conflictMessage: undefined as string | undefined,
      }))"""

assert old_first_branch in ros_content, "old_first_branch not found in RunOfShowPage.tsx"
ros_content = ros_content.replace(old_first_branch, new_first_branch, 1)

assert "\u2014" not in ros_content, "Em dash detected in RunOfShowPage.tsx"

with open("src/features/run-of-show/pages/RunOfShowPage.tsx", "w", encoding="utf-8") as f:
    f.write(ros_content)
print("RunOfShowPage.tsx updated successfully!")

# 3. Update FinanceModule.tsx
fin_module_code = """import { FinancePage } from '@/features/finance/pages/FinancePage'
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
"""
with open("src/components/FinanceModule.tsx", "w", encoding="utf-8") as f:
    f.write(fin_module_code)
print("FinanceModule.tsx updated successfully!")

