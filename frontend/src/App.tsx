import React from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AuthProvider } from "@/lib/authContext"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { LoginPage } from "@/pages/LoginPage"
import { AppLayout } from "@/components/layout/AppLayout"
import { OverviewPage } from "@/pages/OverviewPage"
import { WeddingsListPage } from "@/pages/WeddingsListPage"
import { WeddingOverviewPage } from "@/pages/WeddingOverviewPage"
import { WeddingQuotesPage } from "@/pages/WeddingQuotesPage"
import { WeddingPlanPage } from "@/pages/WeddingPlanPage"
import { WeddingRunOfShowPage } from "@/pages/WeddingRunOfShowPage"
import { WeddingFinancePage } from "@/pages/WeddingFinancePage"
import { WeddingDocumentsPage } from "@/pages/WeddingDocumentsPage"
import { EnquiriesPage } from "@/pages/EnquiriesPage"
import { VendorsDirectoryPage } from "@/pages/VendorsDirectoryPage"
import { FinancePage } from "@/pages/FinancePage"
import { SettingsPage } from "@/pages/SettingsPage"
import { CustomerProtectedRoute } from "@/components/auth/CustomerProtectedRoute"
import { CustomerLoginPage } from "@/pages/customer/CustomerLoginPage"
import { CustomerSignupPage } from "@/pages/customer/CustomerSignupPage"
import { CustomerDashboardPage } from "@/pages/customer/CustomerDashboardPage"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 60 * 1000,
    },
  },
})

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="login" element={<LoginPage />} />
            <Route path="customer/login" element={<CustomerLoginPage />} />
            <Route path="customer/signup" element={<CustomerSignupPage />} />

            {/* Protected Customer Portal */}
            <Route element={<CustomerProtectedRoute />}>
              <Route path="customer/dashboard" element={<CustomerDashboardPage />} />
              <Route path="customer" element={<Navigate to="/customer/dashboard" replace />} />
            </Route>

            {/* Protected Agency Workspaces */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route index element={<Navigate to="/overview" replace />} />
                <Route path="overview" element={<OverviewPage />} />
                
                {/* Wedding Portfolio & Dedicated Workspaces */}
                <Route path="weddings" element={<WeddingsListPage />} />
                <Route path="weddings/:id" element={<Navigate to="overview" replace />} />
                <Route path="weddings/:id/overview" element={<WeddingOverviewPage />} />
                <Route path="weddings/:id/quotes" element={<WeddingQuotesPage />} />
                <Route path="weddings/:id/plan" element={<WeddingPlanPage />} />
                <Route path="weddings/:id/run-of-show" element={<WeddingRunOfShowPage />} />
                <Route path="weddings/:id/finance" element={<WeddingFinancePage />} />
                <Route path="weddings/:id/documents" element={<WeddingDocumentsPage />} />
                
                {/* Agency Operations & Business Workspaces */}
                <Route path="enquiries" element={<EnquiriesPage />} />
                <Route path="vendors" element={<VendorsDirectoryPage />} />
                <Route path="finance" element={<FinancePage />} />
                <Route path="settings" element={<SettingsPage />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/overview" replace />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App

