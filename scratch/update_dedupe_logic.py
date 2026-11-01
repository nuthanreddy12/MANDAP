# 1. Update DocumentsPage.tsx dedupe key
with open("src/features/documents/pages/DocumentsPage.tsx", "r", encoding="utf-8") as f:
    doc_content = f.read()

old_doc_dedupe = """  // Deduplicate documents by clean normalized filename or title so duplicates never render
  const uniqueDocuments = useMemo(() => {
    const seen = new Set<string>()
    const list: ApiDocument[] = []
    for (const doc of rawDocuments) {
      const key = (doc.filename || doc.title || doc.id).toLowerCase().trim()
      if (!seen.has(key)) {
        seen.add(key)
        list.push(doc)
      }
    }
    return list
  }, [rawDocuments])"""

new_doc_dedupe = """  // Deduplicate documents by clean normalized filename or title so duplicate cards never render
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
  }, [rawDocuments])"""

assert old_doc_dedupe in doc_content, "old_doc_dedupe not found"
doc_content = doc_content.replace(old_doc_dedupe, new_doc_dedupe, 1)
assert "\u2014" not in doc_content, "Em dash detected in DocumentsPage.tsx"

with open("src/features/documents/pages/DocumentsPage.tsx", "w", encoding="utf-8") as f:
    f.write(doc_content)
print("DocumentsPage.tsx dedupe enhanced!")

# 2. Update EnquiriesPage.tsx dedupe key
with open("src/features/enquiries/pages/EnquiriesPage.tsx", "r", encoding="utf-8") as f:
    enq_content = f.read()

old_enq_dedupe = """  // Deduplicate enquiries by email and couple names so duplicate entries never appear
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
  }, [rawEnquiries])"""

new_enq_dedupe = """  // Deduplicate enquiries by email and normalized couple names so duplicate cards never appear
  const uniqueEnquiries = useMemo(() => {
    const seen = new Set<string>()
    const list: ApiEnquiry[] = []
    for (const enq of rawEnquiries) {
      // Normalize couple names (e.g., 'Sethi x Chawla', 'Sethi \u00d7 Chawla') to prevent encoding duplicates
      const normCouple = (enq.couple_names || enq.client_names || '')
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '')
      const key = (enq.email ? enq.email.toLowerCase().trim() : normCouple) || enq.id
      if (key && !seen.has(key)) {
        seen.add(key)
        list.push(enq)
      }
    }
    return list
  }, [rawEnquiries])"""

assert old_enq_dedupe in enq_content, "old_enq_dedupe not found"
enq_content = enq_content.replace(old_enq_dedupe, new_enq_dedupe, 1)
assert "\u2014" not in enq_content, "Em dash detected in EnquiriesPage.tsx"

with open("src/features/enquiries/pages/EnquiriesPage.tsx", "w", encoding="utf-8") as f:
    f.write(enq_content)
print("EnquiriesPage.tsx dedupe enhanced!")

