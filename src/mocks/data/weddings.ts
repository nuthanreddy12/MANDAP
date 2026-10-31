export interface PalaceWedding {
  id: string
  couple: string
  venue: string
  city: 'Jaipur' | 'Udaipur'
  dates: string
  guestCount: number
  status: 'In Production' | 'Contract Signed' | 'Final Review'
  leadProducer: string
  nextMilestone: string
  ceremoniesCount: number
  budgetSummary: string
}

export const MOCK_WEDDINGS: PalaceWedding[] = [
  {
    id: 'w-001',
    couple: 'Ananya Singhania & Devendra Rathore',
    venue: 'The Oberoi Udaivilas, Lake Pichola',
    city: 'Udaipur',
    dates: '12 Dec 2026 to 15 Dec 2026',
    guestCount: 380,
    status: 'In Production',
    leadProducer: 'Gayatri Rathore',
    nextMilestone: 'Sangeet Stage Technical Rigging Inspection',
    ceremoniesCount: 5,
    budgetSummary: 'Production allocation: ₹4.8 Cr',
  },
  {
    id: 'w-002',
    couple: 'Rhea Kothari & Arjun Mehta',
    venue: 'Rambagh Palace, Heritage Courtyards',
    city: 'Jaipur',
    dates: '04 Jan 2027 to 07 Jan 2027',
    guestCount: 450,
    status: 'Contract Signed',
    leadProducer: 'Vikramaditya Solanki',
    nextMilestone: 'Royal Shehnai & Folk Ensemble Procurement',
    ceremoniesCount: 6,
    budgetSummary: 'Production allocation: ₹6.2 Cr',
  },
  {
    id: 'w-003',
    couple: 'Meera Chordia & Kabir Varma',
    venue: 'Jagmandir Island Palace, Lake Pichola',
    city: 'Udaipur',
    dates: '22 Jan 2027 to 25 Jan 2027',
    guestCount: 290,
    status: 'Final Review',
    leadProducer: 'Gayatri Rathore',
    nextMilestone: 'ASI Heritage Clearance & Jetty Transit Run-Sheet',
    ceremoniesCount: 4,
    budgetSummary: 'Production allocation: ₹3.9 Cr',
  },
]

