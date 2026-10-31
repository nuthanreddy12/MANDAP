import { Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { ROUTES } from '@/routes/routePaths'

import { LandingPage } from '@/features/landing/pages/LandingPage'
import { WeddingsPage } from '@/features/weddings/pages/WeddingsPage'
import { EnquiriesPage } from '@/features/enquiries/pages/EnquiriesPage'
import { VendorsPage } from '@/features/vendors/pages/VendorsPage'
import { QuotesPage } from '@/features/quotes/pages/QuotesPage'
import { TasksPage } from '@/features/tasks/pages/TasksPage'
import { RunOfShowPage } from '@/features/run-of-show/pages/RunOfShowPage'
import { FinancePage } from '@/features/finance/pages/FinancePage'
import { DocumentsPage } from '@/features/documents/pages/DocumentsPage'
import { AnalyticsPage } from '@/features/analytics/pages/AnalyticsPage'

export function AppRoutes() {
  return (
    <Routes>
      {/* Public Landing Experience */}
      <Route path={ROUTES.HOME} element={<LandingPage />} />

      {/* Management Dashboard Gateway */}
      <Route path={ROUTES.DASHBOARD} element={<Navigate to={ROUTES.WEDDINGS} replace />} />

      {/* Preserved Management Dashboard Modules */}
      <Route element={<AppShell />}>
        <Route path={ROUTES.WEDDINGS} element={<WeddingsPage />} />
        <Route path={ROUTES.ENQUIRIES} element={<EnquiriesPage />} />
        <Route path={ROUTES.VENDORS} element={<VendorsPage />} />
        <Route path={ROUTES.QUOTES} element={<QuotesPage />} />
        <Route path={ROUTES.TASKS} element={<TasksPage />} />
        <Route path={ROUTES.RUN_OF_SHOW} element={<RunOfShowPage />} />
        <Route path={ROUTES.FINANCE} element={<FinancePage />} />
        <Route path={ROUTES.DOCUMENTS} element={<DocumentsPage />} />
        <Route path={ROUTES.ANALYTICS} element={<AnalyticsPage />} />
      </Route>

      {/* Fallback to Home */}
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  )
}
