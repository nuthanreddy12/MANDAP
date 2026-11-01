import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Star, ShieldCheck, MapPin, Phone, RefreshCw } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { getVendors } from '@/services/api'

interface VendorCardItem {
  id: string
  name: string
  category: string
  city: string
  contactPerson?: string
  phone?: string
  rating: string
  tier: 'Heritage Master' | 'Verified Partner'
  activeWeddingsCount: number
}

const MOCK_VENDORS: VendorCardItem[] = [
  {
    id: 'v-1',
    name: 'Mewar Floral Artisans',
    category: 'Floral & Decor',
    city: 'Udaipur',
    rating: '4.98',
    tier: 'Heritage Master',
    activeWeddingsCount: 3,
  },
  {
    id: 'v-2',
    name: 'Royal Rajputana Hospitality & Banquets Pvt. Ltd.',
    category: 'Catering & Banquets',
    city: 'Jaipur',
    rating: '4.95',
    tier: 'Heritage Master',
    activeWeddingsCount: 2,
  },
  {
    id: 'v-3',
    name: 'Rajputana Safa & Turban Guild',
    category: 'Royal Hospitality',
    city: 'Jaipur / Udaipur',
    rating: '5.0',
    tier: 'Heritage Master',
    activeWeddingsCount: 4,
  },
  {
    id: 'v-4',
    name: 'Stories by the Lake Cinecraft',
    category: 'Photography',
    city: 'Udaipur',
    rating: '4.92',
    tier: 'Verified Partner',
    activeWeddingsCount: 1,
  },
]

export function VendorsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All')

  const { data: apiVendors = [], isLoading, refetch } = useQuery({
    queryKey: ['vendors'],
    queryFn: getVendors,
  })

  const vendors: VendorCardItem[] = apiVendors.length > 0
    ? apiVendors.map((v) => ({
        id: v.id,
        name: v.name,
        category: v.category,
        city: v.city,
        contactPerson: v.contact_person,
        phone: v.phone,
        rating: v.rating ? String(v.rating) : '4.95',
        tier: 'Heritage Master' as const,
        activeWeddingsCount: 2,
      }))
    : MOCK_VENDORS

  const filteredVendors = vendors.filter(
    (v) => selectedCategory === 'All' || v.category.toLowerCase().includes(selectedCategory.toLowerCase())
  )

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Curated Artisan Network
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Vetted Heritage Guild & Vendors
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Strictly vetted royal caterers, floral architects, ceremonial musicians, and production specialists across Rajasthan.
          </p>
        </div>

        <div className="flex items-center gap-3">
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
            onClick={() => alert('Opening artisan vetting assessment.')}
          >
            Vet New Artisan
          </Button>
        </div>
      </div>

      {/* Categories Bar */}
      <div className="flex flex-wrap items-center gap-2">
        {['All', 'Catering', 'Floral', 'Hospitality', 'Photography'].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer ${
              selectedCategory === cat
                ? 'bg-[#541424] text-white shadow-xs'
                : 'bg-ivory-card border border-warm-stone text-ink-muted hover:text-ink'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Vendors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredVendors.map((vendor) => (
          <Card key={vendor.id} variant="elevated" className="hover:border-bronze/60 transition-all">
            <CardHeader className="flex flex-row items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <Badge variant={vendor.tier === 'Heritage Master' ? 'bronze' : 'neutral'}>
                    <ShieldCheck className="w-3 h-3 mr-1 inline" />
                    {vendor.tier}
                  </Badge>
                  <span className="text-xs text-ink-muted font-medium uppercase tracking-wider">
                    {vendor.category}
                  </span>
                </div>
                <CardTitle className="text-xl font-serif">{vendor.name}</CardTitle>
                <div className="flex items-center gap-1.5 text-xs text-ink-muted mt-1">
                  <MapPin className="w-3.5 h-3.5 text-bronze shrink-0" />
                  <span>{vendor.city} Operations Hub</span>
                </div>
              </div>

              <div className="flex items-center gap-1 bg-ivory-warm px-2 py-1 rounded-md border border-warm-stone">
                <Star className="w-3.5 h-3.5 fill-bronze text-bronze" />
                <span className="font-serif font-bold text-xs text-ink">{vendor.rating}</span>
              </div>
            </CardHeader>

            <CardContent className="space-y-3">
              {vendor.contactPerson && (
                <div className="text-xs text-ink-muted flex items-center justify-between border-t border-warm-stone/50 pt-2">
                  <span>Lead Contact: <strong className="text-ink">{vendor.contactPerson}</strong></span>
                  {vendor.phone && (
                    <span className="flex items-center gap-1 text-bronze">
                      <Phone className="w-3 h-3" />
                      {vendor.phone}
                    </span>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
