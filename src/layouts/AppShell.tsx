import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/navigation/Sidebar'
import { Header } from '@/components/navigation/Header'
import { MobileDrawer } from '@/components/navigation/MobileDrawer'

export function AppShell() {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false)

  return (
    <div className="min-h-screen bg-ivory text-ink flex">
      {/* Desktop Persistent Sidebar */}
      <Sidebar />

      {/* Responsive Slide-out Drawer */}
      <MobileDrawer
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onOpenMobileNav={() => setIsMobileNavOpen(true)} />

        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
