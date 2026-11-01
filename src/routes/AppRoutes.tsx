import { Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { ROUTES } from '@/routes/routePaths'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { CustomerProtectedRoute } from '@/components/auth/CustomerProtectedRoute'

import { LandingPage } from '@/features/landing/pages/LandingPage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { CustomerLoginPage } from '@/features/customer/pages/CustomerLoginPage'
import { CustomerSignupPage } from '@/features/customer/pages/CustomerSignupPage'
import { CustomerDashboardPage } from '@/features/customer/pages/CustomerDashboardPage'

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

      {/* Public Authentication Portals */}
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />
      <Route path={ROUTES.CUSTOMER_LOGIN} element={<CustomerLoginPage />} />
      <Route path={ROUTES.CUSTOMER_SIGNUP} element={<CustomerSignupPage />} />

      {/* Client Couple Sanctuary (Customer Protected) */}
      <Route element={<CustomerProtectedRoute />}>
        <Route path={ROUTES.CUSTOMER_DASHBOARD} element={<CustomerDashboardPage />} />
      </Route>

      {/* Agency Operations Desk (Staff Protected) */}
      <Route element={<ProtectedRoute />}>
        <Route path={ROUTES.DASHBOARD} element={<Navigate to={ROUTES.WEDDINGS} replace />} />
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
      </Route>

      {/* Fallback to Home */}
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  )
}
