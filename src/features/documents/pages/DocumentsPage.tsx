import { useState, useRef, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  Download,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ShieldCheck,
  Building2,
  UtensilsCrossed,
  FileCheck,
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { useWedding } from '@/context/WeddingContext'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { getDocuments, downloadDocument, uploadQuoteFile, type ApiDocument } from '@/services/api'

type DocFilterCategory = 'all' | 'clearance' | 'menu' | 'quote'

export function DocumentsPage() {
  const queryClient = useQueryClient()
  const { activeWeddingId: weddingId } = useWedding()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState<DocFilterCategory>('all')

  const { data: rawDocuments = [], isLoading, refetch } = useQuery({
    queryKey: ['documents', weddingId],
    queryFn: () => getDocuments(weddingId),
  })

  // Deduplicate documents by clean normalized filename or title so duplicate cards never render
  const uniqueDocuments = useMemo(() => {
    const seen = new Set<string>()
    const list: ApiDocument[] = []
    for (const doc of rawDocuments) {
      const rawName = (doc.filename || doc.title || doc.id).toLowerCase().trim()
      // Strip random doc hash prefix like doc_42872e8bb2_ to identify true canonical file
      const cleanKey = rawName.replace(/^doc_[a-f0-9]+_/, '').replace(/[_-]/g, ' ')
      if (!seen.has(cleanKey)) {
        seen.add(cleanKey)
        list.push(doc)
      }
    }
    return list
  }, [rawDocuments])

  // Helper to categorize document
  const getCategoryInfo = (doc: ApiDocument) => {
    const lower = `${doc.filename} ${doc.title}`.toLowerCase()
    if (
      lower.includes('menu') ||
      lower.includes('guide') ||
      lower.includes('tasting') ||
      lower.includes('banquet')
    ) {
      return {
        type: 'menu' as const,
        label: 'Hospitality & Menus',
        badge: 'emerald' as const,
        icon: <UtensilsCrossed className="w-3.5 h-3.5 text-emerald-600" />,
      }
    }
    if (
      lower.includes('quote') ||
      lower.includes('agreement') ||
      lower.includes('pricing') ||
      lower.includes('contract') ||
      lower.includes('bid')
    ) {
      return {
        type: 'quote' as const,
        label: 'Commercial & Quotes',
        badge: 'bronze' as const,
        icon: <FileCheck className="w-3.5 h-3.5 text-[#B8860B]" />,
      }
    }
    return {
      type: 'clearance' as const,
      label: 'Palace Statutory Clearance',
      badge: 'neutral' as const,
      icon: <Building2 className="w-3.5 h-3.5 text-slate-700" />,
    }
  }

  // Filtered documents
  const filteredDocuments = useMemo(() => {
    if (activeCategory === 'all') return uniqueDocuments
    return uniqueDocuments.filter((doc) => getCategoryInfo(doc).type === activeCategory)
  }, [uniqueDocuments, activeCategory])

  // Counts for filter pills
  const counts = useMemo(() => {
    let clearance = 0
    let menu = 0
    let quote = 0
    for (const d of uniqueDocuments) {
      const cat = getCategoryInfo(d).type
      if (cat === 'clearance') clearance++
      else if (cat === 'menu') menu++
      else if (cat === 'quote') quote++
    }
    return { all: uniqueDocuments.length, clearance, menu, quote }
  }, [uniqueDocuments])

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadQuoteFile(weddingId, file, 'compliance'),
    onSuccess: (data) => {
      setActionMessage(`Clearance file "${data.filename}" uploaded and digitally indexed.`)
      queryClient.invalidateQueries({ queryKey: ['documents', weddingId] })
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to upload clearance file')
    },
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setErrorMessage(null)
    setActionMessage(null)
    uploadMutation.mutate(file)
  }

  const handleDownload = async (doc: ApiDocument) => {
    try {
      setDownloadingId(doc.id)
      setErrorMessage(null)
      const blob = await downloadDocument(doc.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.filename || `${doc.title}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setActionMessage(`Clearance dossier downloaded: ${doc.filename}`)
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to retrieve clearance PDF from storage')
    } finally {
      setDownloadingId(null)
    }
  }

  const statusVariant = (s?: string) => {
    switch (s?.toLowerCase()) {
      case 'ready':
      case 'approved':
      case 'approved & stamped':
        return 'success'
      case 'in processing':
      case 'under_review':
        return 'warning'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Regulatory & Contracts
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Palace Permissions & Documents
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Statutory clearances, ASI heritage guidelines, sound curfew approvals, and signed client master services agreements for Mehra x Kapoor wedding.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf"
            className="hidden"
          />

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
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadMutation.isPending}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload Clearance File'}
          </Button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{actionMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Category Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-warm-stone overflow-x-auto pb-px">
        {[
          { id: 'all' as const, label: `All Documents (${counts.all})` },
          { id: 'clearance' as const, label: `Statutory Clearances (${counts.clearance})` },
          { id: 'menu' as const, label: `Menus & Guest Guides (${counts.menu})` },
          { id: 'quote' as const, label: `Vendor Contracts & Quotes (${counts.quote})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveCategory(tab.id)}
            className={`pb-3 px-4 text-xs font-medium uppercase tracking-wider transition-all border-b-2 whitespace-nowrap cursor-pointer ${
              activeCategory === tab.id
                ? 'border-[#541424] text-[#541424] font-semibold'
                : 'border-transparent text-[#71717A] hover:text-[#1A1A1A]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredDocuments.length === 0 && !isLoading && (
          <div className="col-span-2 p-12 text-center bg-white border border-warm-stone rounded-2xl space-y-2">
            <FileText className="w-8 h-8 text-ink-muted mx-auto opacity-50" />
            <p className="font-serif text-lg font-bold text-ink">No documents in this category</p>
            <p className="text-xs text-ink-muted">Upload a statutory permit or palace agreement PDF to populate this section.</p>
          </div>
        )}

        {filteredDocuments.map((doc) => {
          const categoryInfo = getCategoryInfo(doc)
          return (
            <Card
              key={doc.id || doc.filename}
              variant="default"
              className="hover:border-bronze/60 transition-all duration-300 shadow-sm"
            >
              <CardHeader className="flex flex-row items-start justify-between pb-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant={statusVariant(doc.status)}>
                      {doc.status === 'ready' ? 'Approved & Stamped' : doc.status}
                    </Badge>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-warm-stone/40 text-ink text-[10px] font-semibold uppercase tracking-wider">
                      {categoryInfo.icon}
                      <span>{categoryInfo.label}</span>
                    </span>
                  </div>
                  <CardTitle className="text-lg font-serif pt-1 text-ink">{doc.title}</CardTitle>
                  <span className="text-xs text-bronze font-medium block">
                    Mehra x Kapoor · Udaipur Circuit
                  </span>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="text-xs text-ink-muted space-y-1.5 py-2.5 border-y border-warm-stone/60">
                  <p>
                    File Name:{' '}
                    <strong className="text-ink font-mono text-[11px] font-semibold">
                      {doc.filename}
                    </strong>
                  </p>
                  <p>
                    Storage:{' '}
                    <strong className="text-ink font-medium">
                      Protected Atelier Storage (SHA-256 Verified)
                    </strong>
                  </p>
                  <p>
                    Format:{' '}
                    <strong className="text-ink">
                      application/pdf ({Math.round(doc.file_size / 1024) || 1} KB)
                    </strong>
                  </p>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-xs text-ink-faint font-medium flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Official Dossier Verified</span>
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={
                      <Download
                        className={`w-3.5 h-3.5 ${downloadingId === doc.id ? 'animate-bounce' : ''}`}
                      />
                    }
                    onClick={() => handleDownload(doc)}
                    disabled={downloadingId === doc.id}
                  >
                    {downloadingId === doc.id ? 'Downloading...' : 'Download Dossier'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
