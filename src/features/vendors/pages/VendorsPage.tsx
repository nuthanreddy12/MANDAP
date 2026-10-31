import { useState } from 'react'
import { Plus, Star, ShieldCheck, MapPin } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface Vendor {
  id: string
  name: string
  category: 'Floral & Decor' | 'Royal Hospitality' | 'Folk & Ensemble' | 'Photography'
  city: 'Jaipur' | 'Udaipur' | 'Both'
  rating: string
  tier: 'Heritage Master' | 'Verified Partner'
  activeWeddingsCount: number
}

const MOCK_VENDORS: Vendor[] = [
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
    name: 'Jaipur Royal Brass & Shehnai Collective',
    category: 'Folk & Ensemble',
    city: 'Jaipur',
    rating: '4.95',
    tier: 'Heritage Master',
    activeWeddingsCount: 2,
  },
  {
    id: 'v-3',
    name: 'Rajputana Safa & Turban Guild',
    category: 'Royal Hospitality',
    city: 'Both',
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
  const [vendors] = useState<Vendor[]>(MOCK_VENDORS)

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Partner Network
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Curated Artisans & Vendors
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Direct coordination with heritage floral decorators, safa masters, royal catering
            connoisseurs, and traditional musical troupes across Rajasthan.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('Onboarding new vendor partner dossier.')}
        >
          Add Vendor Partner
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {vendors.map((vendor) => (
          <Card key={vendor.id} variant="default" className="hover:border-bronze/60 transition-all duration-300">
            <CardHeader className="flex flex-row items-start justify-between">
              <div>
                <Badge variant={vendor.tier === 'Heritage Master' ? 'bronze' : 'neutral'} className="mb-2">
                  {vendor.tier}
                </Badge>
                <CardTitle className="text-xl font-serif">{vendor.name}</CardTitle>
                <span className="text-xs text-ink-muted block mt-1">{vendor.category}</span>
              </div>
              <div className="flex items-center gap-1 text-xs font-semibold text-ink bg-warm-stone-light/70 px-2.5 py-1 border border-warm-stone rounded-md">
                <Star className="w-3.5 h-3.5 fill-antique-brass text-antique-brass" aria-hidden="true" />
                <span>{vendor.rating}</span>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-xs py-2 border-y border-warm-stone/60">
                <div className="flex items-center gap-1.5 text-ink-muted">
                  <MapPin className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                  <span>Base: {vendor.city}</span>
                </div>
                <span className="font-medium text-ink">
                  {vendor.activeWeddingsCount} Active Productions
                </span>
              </div>

              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-1.5 text-xs text-garden font-medium">
                  <ShieldCheck className="w-4 h-4" aria-hidden="true" />
                  <span>GST & Palace Verified</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => alert(`Reviewing rate card for ${vendor.name}`)}
                >
                  Rate Cards & Quotes
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
