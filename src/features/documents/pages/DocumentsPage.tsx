import { useState } from 'react'
import { Plus, Download } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface PalaceDocument {
  id: string
  title: string
  category: 'Palace Agreement' | 'ASI Permit' | 'Police & Sound NOC' | 'Vendor SLA'
  wedding: string
  issuedBy: string
  status: 'Approved & Stamped' | 'In Processing' | 'Renewal Required'
  expiryOrDate: string
}

const MOCK_DOCS: PalaceDocument[] = [
  {
    id: 'doc-1',
    title: 'Jagmandir Island Palace Private Mooring & Jetty Transit License',
    category: 'Palace Agreement',
    wedding: 'Meera & Kabir (Jagmandir)',
    issuedBy: 'HRH Group of Hotels Legal Cell',
    status: 'Approved & Stamped',
    expiryOrDate: 'Valid through 28 Jan 2027',
  },
  {
    id: 'doc-2',
    title: 'Aerial Drone Filming Permission (Heritage Buffer Zone)',
    category: 'ASI Permit',
    wedding: 'Rhea & Arjun (Rambagh)',
    issuedBy: 'Archaeological Survey of India, Jaipur Circle',
    status: 'Approved & Stamped',
    expiryOrDate: 'Valid 04 Jan to 07 Jan 2027',
  },
  {
    id: 'doc-3',
    title: 'Outdoor Amplified Acoustic Clearance & Decibel Limit Undertaking',
    category: 'Police & Sound NOC',
    wedding: 'Ananya & Devendra (Udaivilas)',
    issuedBy: 'Superintendent of Police Office, Udaipur',
    status: 'In Processing',
    expiryOrDate: 'Expected 08 Nov 2026',
  },
]

export function DocumentsPage() {
  const [docs] = useState<PalaceDocument[]>(MOCK_DOCS)

  const statusVariant = (s: PalaceDocument['status']) => {
    switch (s) {
      case 'Approved & Stamped':
        return 'success'
      case 'In Processing':
        return 'warning'
      case 'Renewal Required':
        return 'danger'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Regulatory & Contracts
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Palace Permissions & Documents
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Statutory clearances, ASI heritage guidelines, sound curfew approvals, and signed
            client master services agreements.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('Document upload modal will open in Stage 2.')}
        >
          Upload Clearance File
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {docs.map((doc) => (
          <Card key={doc.id} variant="default" className="hover:border-bronze/60 transition-all duration-300">
            <CardHeader className="flex flex-row items-start justify-between">
              <div>
                <Badge variant={statusVariant(doc.status)} className="mb-2">
                  {doc.status}
                </Badge>
                <CardTitle className="text-lg font-serif">{doc.title}</CardTitle>
                <span className="text-xs text-bronze font-medium block mt-1">
                  {doc.wedding}
                </span>
              </div>
            </CardHeader>

            <CardContent className="space-y-3">
              <div className="text-xs text-ink-muted space-y-1 py-2 border-y border-warm-stone/60">
                <p>Issuing Authority: <strong className="text-ink">{doc.issuedBy}</strong></p>
                <p>Validity: <strong className="text-ink">{doc.expiryOrDate}</strong></p>
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-ink-faint font-medium">
                  Signed PDF with Digital Verification
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Download className="w-3.5 h-3.5" />}
                  onClick={() => alert(`Downloading signed copy of ${doc.title}`)}
                >
                  Download Dossier
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
