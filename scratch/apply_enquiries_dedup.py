import sqlite3

# 1. Clean duplicate enquiries and test weddings in SQLite database
conn = sqlite3.connect("mandap.db")
c = conn.cursor()

c.execute("SELECT id FROM enquiries WHERE email = 'sethi.chawla@example.com' ORDER BY created_at ASC")
sethi_ids = [r[0] for r in c.fetchall()]
print(f"Total sethi.chawla@example.com enquiries found: {len(sethi_ids)}")

if len(sethi_ids) > 1:
    keep_enq = sethi_ids[0]
    delete_enqs = sethi_ids[1:]
    print(f"Keeping {keep_enq}, deleting {len(delete_enqs)} duplicate enquiries")
    
    placeholders = ",".join(f"'{i}'" for i in delete_enqs)
    
    # Find and delete associated duplicate weddings
    c.execute(f"SELECT id FROM weddings WHERE source_enquiry_id IN ({placeholders})")
    dup_wedding_ids = [r[0] for r in c.fetchall()]
    if dup_wedding_ids:
        w_placeholders = ",".join(f"'{w}'" for w in dup_wedding_ids)
        c.execute(f"DELETE FROM tasks WHERE wedding_id IN ({w_placeholders})")
        c.execute(f"DELETE FROM wedding_vendors WHERE wedding_id IN ({w_placeholders})")
        c.execute(f"DELETE FROM weddings WHERE id IN ({w_placeholders})")
        print(f"Deleted {len(dup_wedding_ids)} duplicate weddings and tasks")
    
    c.execute(f"DELETE FROM enquiries WHERE id IN ({placeholders})")
    conn.commit()
    print("Database enquiries deduplication completed!")
else:
    print("Enquiries already clean in database.")

# Verify remaining enquiries
c.execute("SELECT id, couple_names, email, status FROM enquiries ORDER BY created_at ASC")
remaining = c.fetchall()
print(f"\nRemaining enquiries in DB ({len(remaining)}):")
for r in remaining:
    print(r)

conn.close()

# 2. Update backend/api/enquiries.py get_enquiries() with deduplication safety
with open("backend/api/enquiries.py", "r", encoding="utf-8") as f:
    enq_api_code = f.read()

old_get_enquiries = '''    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Enquiry.couple_names.ilike(search_term)) |
            (Enquiry.destination.ilike(search_term)) |
            (Enquiry.notes.ilike(search_term))
        )
    return query.order_by(Enquiry.created_at.desc()).all()'''

new_get_enquiries = '''    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Enquiry.couple_names.ilike(search_term)) |
            (Enquiry.destination.ilike(search_term)) |
            (Enquiry.notes.ilike(search_term))
        )
    raw_enquiries = query.order_by(Enquiry.created_at.desc()).all()

    # Deduplicate enquiries by email and normalized couple names, preserving latest
    seen_keys = set()
    deduped_enquiries = []
    for enq in raw_enquiries:
        clean_key = (enq.email or enq.couple_names or enq.id).strip().lower()
        if clean_key not in seen_keys:
            seen_keys.add(clean_key)
            deduped_enquiries.append(enq)
    return deduped_enquiries'''

assert old_get_enquiries in enq_api_code, "old_get_enquiries not found in backend/api/enquiries.py"
enq_api_code = enq_api_code.replace(old_get_enquiries, new_get_enquiries, 1)

assert "—" not in enq_api_code, "Em dash detected in backend/api/enquiries.py"
with open("backend/api/enquiries.py", "w", encoding="utf-8") as f:
    f.write(enq_api_code)
print("Updated backend/api/enquiries.py successfully!")

# 3. Update backend/tests/test_milestone2.py to clean up test records at end of test_milestone2_enquiry_lifecycle
with open("backend/tests/test_milestone2.py", "r", encoding="utf-8") as f:
    m2_test_code = f.read()

old_m2_end = '''    # Re-fetch task to verify persistence
    task_get = client.get(f"/api/v1/tasks/{task_id}")
    assert task_get.status_code == 200
    assert task_get.json()["status"] == "done"

def test_vendor_directory_crud(client):'''

new_m2_end = '''    # Re-fetch task to verify persistence
    task_get = client.get(f"/api/v1/tasks/{task_id}")
    assert task_get.status_code == 200
    assert task_get.json()["status"] == "done"

    # 10. Clean up test records so test does not pollute production enquiry/wedding lists
    clean_db = SessionLocal()
    try:
        clean_db.query(Task).filter(Task.wedding_id == wedding_id).delete()
        clean_db.query(WeddingVendor).filter(WeddingVendor.wedding_id == wedding_id).delete()
        clean_db.query(Wedding).filter(Wedding.id == wedding_id).delete()
        clean_db.query(Enquiry).filter(Enquiry.id == enquiry_id).delete()
        clean_db.commit()
    finally:
        clean_db.close()

def test_vendor_directory_crud(client):'''

assert old_m2_end in m2_test_code, "old_m2_end not found in backend/tests/test_milestone2.py"
m2_test_code = m2_test_code.replace(old_m2_end, new_m2_end, 1)

assert "—" not in m2_test_code, "Em dash detected in backend/tests/test_milestone2.py"
with open("backend/tests/test_milestone2.py", "w", encoding="utf-8") as f:
    f.write(m2_test_code)
print("Updated backend/tests/test_milestone2.py successfully!")

# 4. Update src/features/enquiries/pages/EnquiriesPage.tsx
enquiries_page_code = '''import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  Calendar,
  MapPin,
  Users,
  RefreshCw,
  CheckCircle2,
  Mail,
  Phone,
  UserCheck,
  Search,
  Filter,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { formatINR } from '@/lib/formatters'
import { getEnquiries, createEnquiry, type ApiEnquiry } from '@/services/api'

type StatusFilter = 'all' | 'new' | 'meeting_booked' | 'proposal_sent' | 'qualified' | 'converted'

export function EnquiriesPage() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedEnquiry, setSelectedEnquiry] = useState<ApiEnquiry | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')

  const [clientNames, setClientNames] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [destination, setDestination] = useState('Udaipur')
  const [datesInterested, setDatesInterested] = useState('December 2026')
  const [estimatedGuestCount, setEstimatedGuestCount] = useState(350)
  const [estimatedBudget, setEstimatedBudget] = useState(50000000)
  const [actionMessage, setActionMessage] = useState<string | null>(null)

  const { data: rawEnquiries = [], isLoading, refetch } = useQuery({
    queryKey: ['enquiries'],
    queryFn: getEnquiries,
  })

  // Deduplicate enquiries by email and couple names so duplicate entries never appear
  const uniqueEnquiries = useMemo(() => {
    const seen = new Set<string>()
    const list: ApiEnquiry[] = []
    for (const enq of rawEnquiries) {
      const key = (enq.email || enq.couple_names || enq.client_names || enq.id).toLowerCase().trim()
      if (!seen.has(key)) {
        seen.add(key)
        list.push(enq)
      }
    }
    return list
  }, [rawEnquiries])

  // Filter by search query and status tab
  const filteredEnquiries = useMemo(() => {
    return uniqueEnquiries.filter((enq) => {
      const matchesStatus = statusFilter === 'all' || enq.status?.toLowerCase() === statusFilter
      const text = `${enq.couple_names || ''} ${enq.client_names || ''} ${enq.email || ''} ${enq.destination || ''}`.toLowerCase()
      const matchesSearch = !searchQuery.trim() || text.includes(searchQuery.toLowerCase().trim())
      return matchesStatus && matchesSearch
    })
  }, [uniqueEnquiries, statusFilter, searchQuery])

  // Status counts for filter tabs
  const counts = useMemo(() => {
    const res = { all: uniqueEnquiries.length, new: 0, meeting_booked: 0, proposal_sent: 0, qualified: 0, converted: 0 }
    for (const enq of uniqueEnquiries) {
      const s = enq.status?.toLowerCase() as keyof typeof res
      if (s && s in res) {
        res[s]++
      }
    }
    return res
  }, [uniqueEnquiries])

  const createMutation = useMutation({
    mutationFn: () =>
      createEnquiry({
        client_names: clientNames.trim(),
        couple_names: clientNames.trim(),
        email: email.trim(),
        phone: phone.trim(),
        destination,
        dates_interested: datesInterested,
        rough_date: datesInterested,
        estimated_guest_count: estimatedGuestCount,
        guest_count: estimatedGuestCount,
        estimated_budget: estimatedBudget,
        budget_max: estimatedBudget,
        status: 'new',
      }),
    onSuccess: () => {
      setActionMessage('New bespoke celebration inquiry logged successfully!')
      setIsModalOpen(false)
      setClientNames('')
      setEmail('')
      setPhone('')
      queryClient.invalidateQueries({ queryKey: ['enquiries'] })
    },
  })

  const stageVariant = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'new':
        return 'danger'
      case 'contacted':
      case 'consultation_scheduled':
      case 'meeting_booked':
        return 'bronze'
      case 'proposal_sent':
      case 'contract_pending':
        return 'warning'
      case 'converted':
      case 'qualified':
        return 'success'
      default:
        return 'neutral'
    }
  }

  const formatStatus = (s?: string) => {
    if (!s) return 'New'
    return s.replace(/_/g, ' ').replace(/\\b\\w/g, (c) => c.toUpperCase())
  }

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Prospecting Pipeline
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Client Inquiries & Palace Bookings ({uniqueEnquiries.length})
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Intake funnel for high-net-worth client families, royal venue inquiries, and bespoke proposal requests.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>

          <Button
            variant="bronze"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsModalOpen(true)}
          >
            Log New Inquiry
          </Button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Status Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-warm-stone overflow-x-auto pb-px">
          {[
            { id: 'all' as const, label: `All (${counts.all})` },
            { id: 'new' as const, label: `New (${counts.new})` },
            { id: 'meeting_booked' as const, label: `Meeting Booked (${counts.meeting_booked})` },
            { id: 'proposal_sent' as const, label: `Proposal Sent (${counts.proposal_sent})` },
            { id: 'qualified' as const, label: `Qualified (${counts.qualified})` },
            { id: 'converted' as const, label: `Converted (${counts.converted})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`pb-2.5 px-3.5 text-xs font-medium uppercase tracking-wider transition-all border-b-2 whitespace-nowrap cursor-pointer ${
                statusFilter === tab.id
                  ? 'border-[#541424] text-[#541424] font-semibold'
                  : 'border-transparent text-[#71717A] hover:text-[#1A1A1A]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[240px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
          <input
            type="text"
            placeholder="Search inquiries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
          />
        </div>
      </div>

      {/* Inquiry Pipeline List */}
      <div className="space-y-4">
        {filteredEnquiries.length === 0 && !isLoading && (
          <div className="p-12 text-center bg-white border border-warm-stone rounded-2xl space-y-2">
            <Filter className="w-8 h-8 text-ink-muted mx-auto opacity-50" />
            <p className="font-serif text-lg font-bold text-ink">No inquiries match your criteria</p>
            <p className="text-xs text-ink-muted">Try selecting a different status filter or clear the search query.</p>
          </div>
        )}

        {filteredEnquiries.map((enq: ApiEnquiry) => {
          const rawNames = enq.client_names || enq.couple_names || 'Confidential Client'
          const coupleDisplay = rawNames.replace(/[×]/g, 'x').replace(/\\s+/g, ' ')
          const dateDisplay = enq.dates_interested || enq.rough_date || 'Winter 2026'
          const guestCountDisplay = enq.estimated_guest_count || enq.guest_count || 400
          const budgetDisplay = enq.estimated_budget || enq.budget_max || 0
          const cardKey = enq.id || enq.email || `${coupleDisplay}-${enq.created_at}`

          return (
            <Card key={cardKey} variant="elevated" className="hover:border-bronze/60 transition-all shadow-sm">
              <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Badge variant={stageVariant(enq.status)}>
                      {formatStatus(enq.status)}
                    </Badge>
                    <span className="text-xs text-ink-muted font-mono">{enq.email}</span>
                  </div>
                  <h3 className="text-xl font-serif font-bold text-ink">{coupleDisplay}</h3>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                    <span className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-bronze shrink-0" />
                      {enq.destination || 'Rajasthan'}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-bronze shrink-0" />
                      {dateDisplay}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-bronze shrink-0" />
                      {guestCountDisplay} Guests
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-6 self-end md:self-center">
                  <div className="text-right">
                    <span className="text-[11px] font-semibold text-ink-muted uppercase tracking-wider block">
                      Estimated Budget
                    </span>
                    <span className="font-serif font-bold text-lg text-ink">
                      {formatINR(budgetDisplay)}
                    </span>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedEnquiry(enq)}
                  >
                    Open Dossier
                  </Button>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Slide-over / Modal Dossier View */}
      <Modal
        isOpen={Boolean(selectedEnquiry)}
        onClose={() => setSelectedEnquiry(null)}
        title="Royal Wedding Proposal Dossier"
      >
        {selectedEnquiry && (
          <div className="space-y-5 text-xs text-ink">
            {/* Header Lockup */}
            <div className="p-4 bg-warm-stone/20 border border-warm-stone rounded-xl">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-bronze">
                  Ref: {selectedEnquiry.id}
                </span>
                <Badge variant={stageVariant(selectedEnquiry.status)}>
                  {formatStatus(selectedEnquiry.status)}
                </Badge>
              </div>
              <h2 className="text-xl font-serif font-bold text-ink">
                {(selectedEnquiry.client_names || selectedEnquiry.couple_names || 'Client').replace(/[×]/g, 'x')}
              </h2>
              <div className="flex flex-wrap gap-4 mt-2 text-xs text-ink-muted">
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-bronze" />
                  {selectedEnquiry.email}
                </span>
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-bronze" />
                  {selectedEnquiry.phone}
                </span>
              </div>
            </div>

            {/* Metrics Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-white border border-warm-stone rounded-lg text-center">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block">Circuit</span>
                <span className="font-serif font-semibold text-ink text-sm">
                  {selectedEnquiry.destination || 'Rajasthan'}
                </span>
              </div>
              <div className="p-3 bg-white border border-warm-stone rounded-lg text-center">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block">Season Window</span>
                <span className="font-serif font-semibold text-ink text-sm">
                  {selectedEnquiry.dates_interested || selectedEnquiry.rough_date || 'Winter 2026'}
                </span>
              </div>
              <div className="p-3 bg-white border border-warm-stone rounded-lg text-center">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block">Delegation</span>
                <span className="font-serif font-semibold text-ink text-sm">
                  {selectedEnquiry.estimated_guest_count || selectedEnquiry.guest_count || 400} Guests
                </span>
              </div>
              <div className="p-3 bg-white border border-warm-stone rounded-lg text-center">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block">Budget Capacity</span>
                <span className="font-serif font-semibold text-ink text-sm">
                  {formatINR(selectedEnquiry.estimated_budget || selectedEnquiry.budget_max || 0)}
                </span>
              </div>
            </div>

            {/* Assigned Producer & Theme */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3.5 bg-white border border-warm-stone rounded-lg space-y-1">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block flex items-center gap-1">
                  <UserCheck className="w-3.5 h-3.5 text-bronze" />
                  Assigned Producer
                </span>
                <span className="font-medium text-ink block">
                  {selectedEnquiry.assigned_owner || 'Aarav Mehta'}
                </span>
              </div>
              <div className="p-3.5 bg-white border border-warm-stone rounded-lg space-y-1">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block">Theme Vision</span>
                <span className="font-medium text-ink block">
                  {selectedEnquiry.theme || 'Heritage Palace Splendor'}
                </span>
              </div>
            </div>

            {/* Notes Section */}
            {selectedEnquiry.notes && (
              <div className="p-3.5 bg-white border border-warm-stone rounded-lg space-y-1">
                <span className="text-[10px] uppercase tracking-wider text-ink-muted block font-semibold">
                  Intake Notes & Preferences
                </span>
                <p className="text-ink leading-relaxed">
                  {selectedEnquiry.notes}
                </p>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Log New Inquiry Modal Form */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Log Bespoke Celebration Inquiry"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault()
            createMutation.mutate()
          }}
          className="space-y-4 text-xs"
        >
          <div>
            <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
              Couple / Family Names
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Singhania x Agrawal"
              value={clientNames}
              onChange={(e) => setClientNames(e.target.value)}
              className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Client Email
              </label>
              <input
                type="email"
                required
                placeholder="client@luxury.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              />
            </div>
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Phone Number
              </label>
              <input
                type="tel"
                required
                placeholder="+91 98290 12345"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Destination Circuit
              </label>
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              >
                <option value="Udaipur">Udaipur</option>
                <option value="Jaipur">Jaipur</option>
                <option value="Jodhpur">Jodhpur</option>
                <option value="Jaisalmer">Jaisalmer</option>
              </select>
            </div>
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Target Date / Season
              </label>
              <input
                type="text"
                required
                placeholder="e.g. November 2026"
                value={datesInterested}
                onChange={(e) => setDatesInterested(e.target.value)}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Estimated Guest Count
              </label>
              <input
                type="number"
                min="50"
                value={estimatedGuestCount}
                onChange={(e) => setEstimatedGuestCount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              />
            </div>
            <div>
              <label className="block text-ink-muted uppercase tracking-wider mb-1 font-semibold">
                Budget Capacity (INR)
              </label>
              <input
                type="number"
                step="1000000"
                value={estimatedBudget}
                onChange={(e) => setEstimatedBudget(Number(e.target.value))}
                className="w-full px-3 py-2 border border-warm-stone rounded-xl text-ink bg-white focus:outline-none focus:border-bronze"
              />
            </div>
          </div>

          <div className="pt-3 flex justify-end gap-3 border-t border-warm-stone">
            <Button variant="outline" size="md" type="button" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="bronze" size="md" type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Logging Inquiry...' : 'Register Inquiry'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
'''

assert "—" not in enquiries_page_code, "Em dash detected in enquiries_page_code!"
with open("src/features/enquiries/pages/EnquiriesPage.tsx", "w", encoding="utf-8") as f:
    f.write(enquiries_page_code)
print("Updated src/features/enquiries/pages/EnquiriesPage.tsx successfully!")

# 5. Create src/components/EnquiriesModule.tsx alias
module_code = '''// Alias export for canonical EnquiriesPage component
export { EnquiriesPage as default, EnquiriesPage as EnquiriesModule } from '@/features/enquiries/pages/EnquiriesPage'
'''

assert "—" not in module_code, "Em dash detected in module_code!"
with open("src/components/EnquiriesModule.tsx", "w", encoding="utf-8") as f:
    f.write(module_code)
print("Created src/components/EnquiriesModule.tsx successfully!")

