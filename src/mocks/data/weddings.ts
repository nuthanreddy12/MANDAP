export interface PalaceWedding {
  id: string
  couple: string
  venue: string
  city: 'Jaipur' | 'Udaipur' | 'Jaisalmer'
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
    id: 'w1',
    couple: 'Mehra x Kapoor',
    venue: 'The Oberoi Rajvilas, Heritage Pavilions',
    city: 'Jaipur',
    dates: '14 Nov 2026 to 16 Nov 2026',
    guestCount: 420,
    status: 'In Production',
    leadProducer: 'Nisha Sharma',
    nextMilestone: 'Catering Tasting and Surcharge Audit',
    ceremoniesCount: 5,
    budgetSummary: 'Production allocation: ₹1.85 Cr',
  },
  {
    id: 'w2',
    couple: 'Singhania x Rathore',
    venue: 'The Oberoi Udaivilas, Lake Pichola',
    city: 'Udaipur',
    dates: '12 Dec 2026 to 15 Dec 2026',
    guestCount: 380,
    status: 'In Production',
    leadProducer: 'Gayatri Rathore',
    nextMilestone: 'Sangeet Stage Technical Rigging Inspection',
    ceremoniesCount: 5,
    budgetSummary: 'Production allocation: ₹4.80 Cr',
  },
  {
    id: 'w3',
    couple: 'Kothari x Mehta',
    venue: 'Rambagh Palace, Heritage Courtyards',
    city: 'Jaipur',
    dates: '04 Jan 2027 to 07 Jan 2027',
    guestCount: 450,
    status: 'Contract Signed',
    leadProducer: 'Aarav Mehta',
    nextMilestone: 'Royal Shehnai & Folk Ensemble Procurement',
    ceremoniesCount: 6,
    budgetSummary: 'Production allocation: ₹6.20 Cr',
  },
  {
    id: 'w4',
    couple: 'Sethi x Chawla',
    venue: 'Suryagarh Heritage Citadel, Desert Dunes',
    city: 'Jaisalmer',
    dates: '20 Feb 2027 to 22 Feb 2027',
    guestCount: 350,
    status: 'Final Review',
    leadProducer: 'Kabir Verma',
    nextMilestone: 'ASI Heritage Clearance & Camel Safari Logistical Gate',
    ceremoniesCount: 4,
    budgetSummary: 'Production allocation: ₹3.90 Cr',
  },
]
