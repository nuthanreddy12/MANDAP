import React, { createContext, useContext, useState, useEffect, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getWeddings, type ApiWedding } from '@/services/api'
import { MOCK_WEDDINGS, PalaceWedding } from '@/mocks/data/weddings'

export interface WeddingContextType {
  activeWeddingId: string
  setActiveWeddingId: (id: string) => void
  activeWedding: PalaceWedding | undefined
  weddings: PalaceWedding[]
  isLoading: boolean
  refetchWeddings: () => void
}

const WeddingContext = createContext<WeddingContextType | undefined>(undefined)

const STORAGE_KEY = 'mandap_active_wedding_id'

export const WeddingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient()

  // 1. Fetch real active weddings from API
  const { data: apiWeddings = [], isLoading, refetch } = useQuery({
    queryKey: ['weddings'],
    queryFn: getWeddings,
    staleTime: 1000 * 60 * 5,
  })

  // 2. Normalize weddings list with fallback to MOCK_WEDDINGS
  const weddings: PalaceWedding[] = useMemo(() => {
    if (apiWeddings && apiWeddings.length > 0) {
      return apiWeddings.map((w: ApiWedding, idx: number) => ({
        id: w.id,
        couple: w.couple_names,
        venue: w.venue || 'Palace Heritage Estate',
        city: (w.destination?.includes('Udaipur') ? 'Udaipur' : w.destination?.includes('Jaisalmer') ? 'Jaisalmer' : 'Jaipur') as any,
        dates: w.dates || 'Winter 2026',
        guestCount: w.guest_count || 400,
        status: w.health_status === 'attention_needed' ? 'Final Review' : 'In Production',
        nextMilestone: w.health_status === 'attention_needed' ? 'Catering Tasting and Surcharge Audit' : 'Ceremony Schedule Coordination',
        leadProducer: w.assigned_planner || 'Nisha Sharma',
        ceremoniesCount: idx === 0 ? 5 : 4,
        budgetSummary: w.client_budget ? `Production allocation: ₹${(w.client_budget / 10000000).toFixed(2)} Cr` : 'Production allocation: ₹4.8 Cr',
      }))
    }
    return MOCK_WEDDINGS
  }, [apiWeddings])

  // 3. Active wedding ID state, persisted in local storage
  const [activeWeddingId, setActiveWeddingIdState] = useState<string>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && (saved === 'w1' || saved === 'w2' || saved === 'w3' || saved === 'w4' || saved.startsWith('w'))) {
      return saved
    }
    return 'w1'
  })

  // Ensure activeWeddingId is valid in the loaded weddings list
  useEffect(() => {
    if (weddings.length > 0 && !weddings.some((w) => w.id === activeWeddingId)) {
      setActiveWeddingIdState(weddings[0].id)
      localStorage.setItem(STORAGE_KEY, weddings[0].id)
    }
  }, [weddings, activeWeddingId])

  const setActiveWeddingId = (id: string) => {
    setActiveWeddingIdState(id)
    localStorage.setItem(STORAGE_KEY, id)
    // Invalidate dependent query caches so all modules re-render for the new wedding immediately
    queryClient.invalidateQueries({ queryKey: ['quotes', id] })
    queryClient.invalidateQueries({ queryKey: ['quote-comparison', id] })
    queryClient.invalidateQueries({ queryKey: ['tasks', id] })
    queryClient.invalidateQueries({ queryKey: ['timeline', id] })
    queryClient.invalidateQueries({ queryKey: ['invoices', id] })
    queryClient.invalidateQueries({ queryKey: ['finance-overview', id] })
    queryClient.invalidateQueries({ queryKey: ['documents', id] })
  }

  const activeWedding = useMemo(() => {
    return weddings.find((w) => w.id === activeWeddingId) || weddings[0]
  }, [weddings, activeWeddingId])

  return (
    <WeddingContext.Provider
      value={{
        activeWeddingId,
        setActiveWeddingId,
        activeWedding,
        weddings,
        isLoading,
        refetchWeddings: refetch,
      }}
    >
      {children}
    </WeddingContext.Provider>
  )
}

export function useWedding(): WeddingContextType {
  const context = useContext(WeddingContext)
  if (!context) {
    throw new Error('useWedding must be used within a WeddingProvider')
  }
  return context
}

